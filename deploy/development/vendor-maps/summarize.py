"""Sanitized aggregate metrics. Never publish raw heap profiles or payloads."""
import argparse,collections,json,statistics
from pathlib import Path

MIB=1048576
def rows(path):return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []

def public_function_name(value):
    # Webpack module IDs may be embedded in functionName, not only callFrame.url.
    # Suppress the whole ID rather than publishing clipped absolute paths.
    if '/' in value or '\\' in value:return '(compiled module)'
    return (value or '(anonymous)')[:80]

def slope(values):
    if len(values)<2:return None
    xs=[x['at']/60000 for x in values];ys=[x['heapUsed']/MIB for x in values]
    mx=statistics.mean(xs);my=statistics.mean(ys);den=sum((x-mx)**2 for x in xs)
    return round(sum((x-mx)*(y-my) for x,y in zip(xs,ys))/den,3) if den else None

def summarize(root):
    definition=json.loads((root/'definition.json').read_text());progress=json.loads((root/'progress.json').read_text());worker=progress['expected']
    heap=rows(root/f'heap-{worker}.jsonl');gc=rows(root/f'gc-{worker}.jsonl');metrics=rows(root/'metrics.jsonl');compilers=[x for x in rows(root/'compilers.jsonl') if x['pid']==worker];major=[x for x in gc if x['kind']==4]
    warm_start=heap[0]['at']+15*60000;warm=[x for x in heap if x['at']>=warm_start];warm_major=[x for x in major if x['at']>=warm_start]
    profiles=sorted(root.glob(f'alloc-{worker}-*.heapprofile'));allocation=[]
    for file in profiles:
        profile=json.loads(file.read_text());sizes=collections.Counter();mechanisms=collections.Counter()
        def visit(node,parents):
            frame=node['callFrame'];url=frame['url'];stack=parents+[frame]
            if url=='node:fs':
                owner=next((f for f in reversed(parents) if f['url']!='node:fs'),frame)
            else:owner=frame
            # Strip filesystem paths, compiled source, line text, usernames and IDs.
            category='node-internal' if owner['url'].startswith('node:') else 'webpack' if 'webpack' in owner['url'] else 'next-runtime' if 'next/' in owner['url'] else 'app-compiled' if '.next-primary-dev' in owner['url'] else 'other'
            name=public_function_name(owner['functionName'])
            sizes[(category,name)]+=node['selfSize']
            if any(f['functionName'] in ['defaultLoadImpl','readFileSync','wrapSafe','loadSource'] for f in stack): mechanisms['module_source_read_stack']+=node['selfSize']
            if any('app-page.runtime.dev' in f['url'] for f in stack): mechanisms['flight_runtime_stack']+=node['selfSize']
            for child in node.get('children',[]):visit(child,stack)
        visit(profile['head'],[])
        allocation.append(dict(at=int(file.stem.rsplit('-',1)[1]),sampled_mib=round(sum(sizes.values())/MIB,1),mechanisms_mib={k:round(v/MIB,1) for k,v in mechanisms.items()},top=[dict(category=k[0],function=k[1],mib=round(v/MIB,1)) for k,v in sizes.most_common(12)]))
    parent=int(metrics[0]['MainPID']);parent_heap=rows(root/f'heap-{parent}.jsonl')
    events={}
    for sample in metrics:
        for line in (sample.get('events') or '').splitlines():
            name,value=line.split();events[name]=max(events.get(name,0),int(value))
    gc_durations=[x['duration'] for x in gc]
    return dict(mode=definition['mode'],baseline_sha=definition['base_sha'],test_copy_sha=definition['copy_sha'],node=definition['node'],limits={k:definition[k] for k in ['heap_mib','cgroup_mib','cpu_percent']},flight_graph_instrumented=False,sampling=definition['sampling'],elapsed=progress['elapsed'],worker_unchanged=all(r['workers']==[worker] for r in metrics),parent_unchanged=all(int(r['MainPID'])==parent for r in metrics),heap_limit_mib=round(heap[-1]['heapLimit']/MIB,1),next_threshold_mib=round(heap[-1]['heapLimit']*.8/MIB,1),minimum_sampled_threshold_distance_mib=round((heap[-1]['heapLimit']*.8-max(x['heapUsed'] for x in heap))/MIB,1),native_maps_enabled=all(x.get('nativeSourceMaps') is True for x in heap if x['reason']!='startup'),parent_heap_peak_mib=round(max(x['heapUsed'] for x in parent_heap)/MIB,1) if parent_heap else None,cpu_seconds=round(int(metrics[-1]['CPUUsageNSec'])/1e9,1),memory_events_peak=events,samples=len(heap),gc_count=len(gc),gc_duration_total_ms=round(sum(gc_durations),1),gc_duration_peak_ms=round(max(gc_durations),1) if gc_durations else None,major_gc_count=len(major),warm_major_gc_count=len(warm_major),heap_peak_mib=round(max(x['heapUsed'] for x in heap)/MIB,1),heap_final_mib=round(heap[-1]['heapUsed']/MIB,1),external_peak_mib=round(max(x['external'] for x in heap)/MIB,1),array_buffers_peak_mib=round(max(x['arrayBuffers'] for x in heap)/MIB,1),rss_peak_mib=round(max(x['rss'] for x in heap)/MIB,1),cgroup_sampled_peak_mib=round(max(int(x['MemoryCurrent']) for x in metrics)/MIB,1),cgroup_kernel_peak_mib=round(max(int(x['MemoryPeak']) for x in metrics)/MIB,1),warm_heap_slope_mib_per_min=slope(warm),warm_post_major_gc_slope_mib_per_min=slope(warm_major),major_gc_latest_mib=round(major[-1]['heapUsed']/MIB,1) if major else None,compiler_completions=len(compilers),compiler_module_peak={name:max(x['modules'] for x in compilers if x['name']==name) for name in {x['name'] for x in compilers}},resource_counts_final=dict(collections.Counter(heap[-1]['resources'])),heap_spaces_final={x['space_name']:round(x['space_used_size']/MIB,1) for x in heap[-1]['spaces']},major_gc_timeline=[dict(seconds=round((x['at']-heap[0]['at'])/1000,1),heap_mib=round(x['heapUsed']/MIB,1)) for x in major],timeline=[dict(seconds=round((x['at']-heap[0]['at'])/1000),heap_mib=round(x['heapUsed']/MIB,1),rss_mib=round(x['rss']/MIB,1),external_mib=round(x['external']/MIB,1)) for x in heap[::12]],allocation_profiles=allocation,browser=json.loads((root/'browser-result.json').read_text()) if (root/'browser-result.json').exists() else json.loads((root/'browser-progress.json').read_text()),result=json.loads((root/'result.json').read_text()) if (root/'result.json').exists() else {'state':'RUNNING'})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root');p.add_argument('--output');args=p.parse_args();result=summarize(Path(args.root))
    if args.output:Path(args.output).write_text(json.dumps(result,indent=2))
    else:print(json.dumps(result,indent=2))
