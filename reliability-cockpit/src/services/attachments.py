"""Private application attachment boundary. No public storage or source clients."""
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from uuid import uuid4
import os,re
from datetime import datetime,timezone
from typing import Protocol
from pydantic import Field
from sqlalchemy import Column,String,Integer,JSON,select
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError
from src.domain.condition_evidence import EvidenceModel
from src.domain.engineering import EngineeringError,Role
class ScanStatus(StrEnum):
 CLEAN='CLEAN'
 QUARANTINED='QUARANTINED'
class AttachmentMetadata(EvidenceModel):
 attachment_id:str
 canonical_asset_id:str
 owner_ref:str
 filename:str
 content_type:str
 size:int=Field(gt=0)
 checksum:str=Field(pattern='^[a-f0-9]{64}$')
 scan_status:ScanStatus
 created_at:datetime
 provenance:str='HUMAN_ATTACHMENT'
class AttachmentBase(DeclarativeBase):pass
class AttachmentRow(AttachmentBase):
 __tablename__='nadi_attachment'
 attachment_id=Column(String(100),primary_key=True)
 document=Column(JSON,nullable=False)
class AttachmentAudit(AttachmentBase):
 __tablename__='nadi_attachment_event'
 event_id=Column(String(100),primary_key=True)
 attachment_id=Column(String(100),nullable=False)
 actor=Column(String(160),nullable=False)
 action=Column(String(40),nullable=False)
 occurred_at=Column(String(40),nullable=False)
class PrivateStorage(Protocol):
 def put(self,key:str,data:bytes):...
 def get(self,key:str)->bytes:...
 def discard(self,key:str):...
class DisposableFileStorage:
 """Development fixture implementation; production storage requires separate review."""
 def __init__(self,root):
  self.root=Path(root).resolve();self.root.mkdir(mode=0o700,parents=True,exist_ok=True)
  if self.root.stat().st_mode & 0o077:raise ValueError('private storage permissions required')
 def path(self,key):
  if not re.fullmatch(r'[a-f0-9]{32}',key):raise EngineeringError('ATTACHMENT_KEY_INVALID',422)
  return self.root/key
 def put(self,key,data):
  fd=os.open(self.path(key),os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'wb') as f:f.write(data)
 def get(self,key):
  fd=os.open(self.path(key),os.O_RDONLY|os.O_NOFOLLOW)
  with os.fdopen(fd,'rb') as f:return f.read()
 def discard(self,key):self.path(key).unlink(missing_ok=True)
class AttachmentService:
 TYPES={'application/pdf':b'%PDF-','image/png':b'\x89PNG\r\n\x1a\n','image/jpeg':b'\xff\xd8\xff'}
 def __init__(self,store,storage,assets,*,max_bytes,scanner=None,clock=None):
  if type(max_bytes)!=int or not 1<=max_bytes<=20*1024*1024:raise ValueError('explicit bounded size required')
  self.engine,self.storage,self.assets=store.engine,storage,assets
  self.limit,self.scanner=max_bytes,scanner;self.clock=clock or (lambda:datetime.now(timezone.utc))
 def authorize(self,actor,asset,*,write=False):
  if asset not in actor.asset_ids or not actor.roles:raise EngineeringError('NOT_FOUND',404)
  if write and Role.AUTHOR not in actor.roles:raise EngineeringError('FORBIDDEN',403)
  if not self.assets(asset):raise EngineeringError('ASSET_UNAVAILABLE',503)
 def audit(self,c,actor,key,action):
  c.execute(AttachmentAudit.__table__.insert().values(event_id=str(uuid4()),attachment_id=key,actor=actor.principal_id,action=action,occurred_at=self.clock().isoformat()))
 def upload(self,actor,asset,filename,content_type,data):
  self.authorize(actor,asset,write=True)
  if not isinstance(filename,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_. -]{0,119}',filename) or '..' in filename:
   raise EngineeringError('ATTACHMENT_FILENAME_INVALID',422)
  if content_type not in self.TYPES or not isinstance(data,bytes) or not 0<len(data)<=self.limit or not data.startswith(self.TYPES[content_type]):
   raise EngineeringError('ATTACHMENT_CONTENT_INVALID',422)
  key=uuid4().hex
  try:
   status=ScanStatus.CLEAN if self.scanner and self.scanner(data,content_type) is True else ScanStatus.QUARANTINED
   metadata=AttachmentMetadata(attachment_id=key,canonical_asset_id=asset,owner_ref=actor.principal_id,filename=filename,content_type=content_type,size=len(data),checksum=sha256(data).hexdigest(),scan_status=status,created_at=self.clock())
   self.storage.put(key,data)
   try:
    with self.engine.begin() as c:
     c.execute(AttachmentRow.__table__.insert().values(attachment_id=key,document=metadata.model_dump(mode='json')));self.audit(c,actor,key,'UPLOAD')
   except Exception:
    self.storage.discard(key);raise
   return metadata
  except EngineeringError:raise
  except Exception:raise EngineeringError('ATTACHMENT_UNAVAILABLE',503) from None
 def retrieve(self,actor,key):
  try:
   with self.engine.begin() as c:
    raw=c.scalar(select(AttachmentRow.document).where(AttachmentRow.attachment_id==key))
    if raw is None:raise EngineeringError('NOT_FOUND',404)
    metadata=AttachmentMetadata.model_validate(raw);self.authorize(actor,metadata.canonical_asset_id)
    if actor.principal_id!=metadata.owner_ref and not ({Role.REVIEWER,Role.ADMIN}&actor.roles):raise EngineeringError('FORBIDDEN',403)
    if metadata.scan_status!=ScanStatus.CLEAN:raise EngineeringError('ATTACHMENT_QUARANTINED',409)
    data=self.storage.get(key)
    if len(data)!=metadata.size or sha256(data).hexdigest()!=metadata.checksum:raise EngineeringError('ATTACHMENT_INTEGRITY_FAILED',409)
    self.audit(c,actor,key,'RETRIEVE');return metadata,data
  except EngineeringError:raise
  except Exception:raise EngineeringError('ATTACHMENT_UNAVAILABLE',503) from None
