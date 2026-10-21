"""Bounded qualification writer for disposable PostgreSQL copies ONLY.

All imported rows go through InspectionService.command, including receipts,
author attribution, schema validation and immutable CREATE history. No live-mode
adapter or migration is supplied by this candidate.
"""
from copy import copy
from hashlib import sha256
from pathlib import Path
import json,os,stat,tempfile
from sqlalchemy import select,text
from src.domain.engineering import Role,EngineeringError
from src.domain.manual_inspection import InspectionDraft
from src.repositories.human_records import RecordRow,RevisionRow,HumanReceiptRow,HumanRecordRepository
from src.services.pdm_history_staging import verified_events,capture_event_key,verify_manifest

MAX_PILOT_RECORDS=25
DOCUMENT_BUDGET=9500
BYTE_BUDGET=120*1024*1024
DOCUMENTS=(('nadi_human_record','document'),('nadi_human_record_revision','snapshot'),('nadi_human_record_receipt','result'),('engineering_case','document'),('engineering_case_event','snapshot'),('engineering_case_receipt','result'))
def budget(connection):
    count=size=0
    for table,column in DOCUMENTS:
        n,b=connection.execute(text('SELECT count(*),coalesce(sum(octet_length('+column+'::text)),0) FROM '+table)).one();count+=n;size+=b
    if count>DOCUMENT_BUDGET or size>BYTE_BUDGET:raise EngineeringError('HISTORY_QUALIFICATION_BUDGET_EXCEEDED',409)
    return {'documents':count,'bytes':size}

class BoundRepository(HumanRecordRepository):
    def __init__(self,engine,connection):self.engine,self.connection=engine,connection
    def transact(self,operation):return operation(self.connection)

def validate_disposable_target(engine,database):
    # Shared by qualification setup before any migrations/test account writes.
    if engine.dialect.name!='postgresql' or not database.startswith('pdm_history_pilot_') or not database.endswith('_test'):
        raise ValueError('DISPOSABLE_HISTORY_COPY_ONLY')
    if engine.url.host!='127.0.0.1' or engine.url.port in {None,5432,15443}:raise ValueError('DISPOSABLE_LOOPBACK_PORT_REQUIRED')
    with engine.connect() as c:
        if c.scalar(text('SELECT current_database()'))!=database:raise ValueError('DISPOSABLE_DATABASE_IDENTITY_MISMATCH')

class HistoryPilot:
    def __init__(self,inspections,provider,*,database):
        self.service,self.provider,self.engine,self.database=inspections,provider,inspections.repo.engine,database
        validate_disposable_target(self.engine,database)
        # Caller must provision the isolated copy explicitly; no init/migrate here.

    def run(self,plan_dir,subject,journal,*,limit=MAX_PILOT_RECORDS,after_commit=None):
        if type(limit) is not int or not 1<=limit<=MAX_PILOT_RECORDS:raise ValueError('BOUNDED_PILOT_LIMIT_REQUIRED')
        plan_dir=Path(plan_dir);meta=verify_manifest(plan_dir);events=verified_events(plan_dir)
        grant=self.provider.current_grant(subject)
        if not grant or Role.AUTHOR not in grant.principal.roles or 'NADI-ASSET-001' not in grant.principal.asset_ids:raise EngineeringError('FORBIDDEN',403)
        actor=grant.principal;journal=Path(journal).absolute()
        journal.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
        info=journal.parent.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid() or info.st_mode&0o077 or journal.parent.resolve()!=journal.parent:raise ValueError('PRIVATE_JOURNAL_REQUIRED')
        if journal.is_symlink():raise ValueError('PRIVATE_JOURNAL_REQUIRED')
        if journal.exists():
            prior=json.loads(journal.read_text())
            if (prior.get('plan_id'),prior.get('subject'),prior.get('database'))!=(meta['plan_id'],subject,self.database):raise ValueError('JOURNAL_IDENTITY_CHANGED')
        chosen=[];skipped={};replayed=0
        # Journal is a convenience, never authorization or duplicate authority.
        with self.engine.connect() as c:
            for event in events:
                if event['status']!='ACCEPTED':skipped[event['status']]=skipped.get(event['status'],0)+1;continue
                payload=InspectionDraft.model_validate(dict(event['draft'],inspector_ref=subject)).model_dump(mode='json')
                # Same CREATE fingerprint contract as ReviewedRecordService.command;
                # omitted optional fields must never become a subset comparison.
                fingerprint=sha256(json.dumps([self.service.kind,'CREATE',payload,None,0],sort_keys=True,separators=(',',':')).encode()).hexdigest()
                receipt=self.service.repo.receipt(c,subject,event['request_id'],fingerprint)
                if receipt is not None:
                    replayed+=1;continue
                chosen.append(event)
                if len(chosen)==limit:break
        if verify_manifest(plan_dir)['plan_id']!=meta['plan_id']:raise ValueError('PLAN_CHANGED_DURING_SELECTION')
        committed=[]
        if chosen:
            with self.provider.guard(subject,grant.version):
                with self.engine.begin() as c:
                    c.execute(text("SET LOCAL lock_timeout='5s'"));c.execute(text("SET LOCAL statement_timeout='30s'"))
                    c.execute(text('LOCK TABLE nadi_human_record,nadi_human_record_revision,nadi_human_record_receipt IN SHARE ROW EXCLUSIVE MODE'))
                    before=budget(c)
                    if before['documents']+3*len(chosen)>DOCUMENT_BUDGET:raise EngineeringError('HISTORY_QUALIFICATION_BUDGET_EXCEEDED',409)
                    bound=copy(self.service);bound.repo=BoundRepository(self.engine,c)
                    # Only inspect owning-store metadata for duplicate prevention.
                    # Refuse rather than expose another author's hidden record.
                    existing=set()
                    documents=select(RecordRow.document).where(RecordRow.kind=='INSPECTION').union_all(select(RevisionRow.snapshot).where(RevisionRow.kind=='INSPECTION'))
                    for document in c.scalars(documents):
                        capture=document.get('input_capture')
                        if not capture:continue
                        try:existing.add(capture_event_key(capture))
                        except ValueError:
                            # Single-cell partials: match against candidate coordinates
                            # using candidate axis; missing metadata never permits overwrite.
                            for event in chosen:
                                if capture.get('source_sha256')==event['source']['sha256'] and capture.get('sheet_index')==event['source']['sheet_index'] and capture.get('profile_id')==event['source']['profile']:
                                    try:existing.add(capture_event_key(dict(capture,source_event_axis=event['source']['axis'])))
                                    except ValueError:raise EngineeringError('EXISTING_EVENT_IDENTITY_UNRESOLVED',409)
                    for event in chosen:
                        if event['event_key'] in existing:raise EngineeringError('EXISTING_SOURCE_EVENT_PRESERVED',409)
                        draft=InspectionDraft.model_validate(dict(event['draft'],inspector_ref=subject))
                        if draft.input_capture is None or draft.inspected_at is not None or draft.measurements or draft.case_refs or draft.sr_references or draft.engineering_analysis or draft.attachments:
                            raise EngineeringError('PROVISIONAL_HISTORY_ONLY',422)
                        if 'DEMO/HISTORIS' not in (draft.operating_context or ''):raise EngineeringError('HISTORY_DEMO_LABEL_REQUIRED',422)
                        capture=draft.input_capture.model_dump(mode='json')
                        if capture_event_key(dict(capture,source_event_axis=event['source']['axis']))!=event['event_key']:raise EngineeringError('SOURCE_EVENT_IDENTITY_MISMATCH',422)
                        if event['request_id']!='history:'+event['event_key'][:56]:raise EngineeringError('SOURCE_EVENT_REQUEST_ID_MISMATCH',422)
                        row=bound.command(actor,'CREATE',draft.model_dump(mode='json'),event['request_id'])
                        if row.status!='DRAFT' or row.review is not None or row.measurements:raise RuntimeError('PILOT_INVARIANT_FAILED')
                        committed.append({'event_key':event['event_key'],'record_id':row.record_id,'revision':row.revision});existing.add(event['event_key'])
                    after=budget(c)  # Over-budget writes rollback the entire chunk.
            if after_commit:after_commit()  # Failure here simulates lost ACK; receipts recover it.
        result={'schema':'NADI_HISTORY_PILOT_V1','plan_id':meta['plan_id'],'subject':subject,'database':self.database,'created':len(committed),'replayed':replayed,'records':committed,'skipped':skipped,'maximum_new_records':limit,'provisional_only':True}
        fd,name=tempfile.mkstemp(prefix='.'+journal.name+'-',dir=journal.parent)
        with os.fdopen(fd,'w') as stream:stream.write(json.dumps(result,sort_keys=True)+'\n')
        os.replace(name,journal)
        return result
