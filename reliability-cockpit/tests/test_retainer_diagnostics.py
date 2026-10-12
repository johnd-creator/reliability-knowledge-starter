"""Known-answer graph, privacy and output tests; no application/service access."""
import importlib.util,json,random,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('retainer_probe',ROOT/'deploy/development/retainers/run.py')
PROBE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(PROBE)
META={'node_types':[['hidden', 'array', 'string', 'object', 'code', 'closure', 'regexp', 'number', 'native', 'synthetic', 'concatenated string', 'sliced string', 'symbol', 'bigint', 'object shape']],'node_fields':['type','name','id','self_size','edge_count','trace_node_id','detachedness'],'edge_fields':['type','name_or_index','to_node'],'edge_types':[['context','element','property','internal','hidden','shortcut','weak']]}
class RetainerSafetyTest(unittest.TestCase):
    def test_output_refuses_live_old_evidence_and_escape(self):
        for p in ['/tmp/nadi-fix04-private/new','/tmp/nadi-fix05-private/../escape',str(ROOT/'.nadi-dev/new'),'relative']:
            with self.subTest(p=p),self.assertRaises(ValueError):PROBE.private_output(p)
    def test_new_leaf_only(self):
        with tempfile.TemporaryDirectory() as p:
            with self.assertRaises(ValueError):PROBE.private_output(p)
        self.assertEqual(PROBE.private_output('/tmp/nadi-fix05-private/never-created-test-leaf'),Path('/tmp/nadi-fix05-private/never-created-test-leaf'))
    def test_provenance_only_accepts_exact_declared_hmr(self):
        with tempfile.TemporaryDirectory() as value:
            root=Path(value);target=root/'reliability-cockpit/web/components/DevelopmentStatus.tsx';target.parent.mkdir(parents=True);target.write_text('<span>DEV</span>');sha=PROBE.helper.git_fixture(root)
            PROBE.verify_source(root,sha)
            target.write_text('<span>DEV MATCH 3</span>');PROBE.verify_source(root,sha)
            target.write_text('<span>DEV MATCH 99</span>')
            with self.assertRaises(RuntimeError):PROBE.verify_source(root,sha)
            target.write_text('<span>DEV</span>');(root/'unrelated').write_text('unrelated')
            with self.assertRaises(RuntimeError):PROBE.verify_source(root,sha)
    def test_provenance_refuses_staged_change_env_and_wrong_sha(self):
        with tempfile.TemporaryDirectory() as value:
            root=Path(value);(root/'unrelated').write_text('original');sha=PROBE.helper.git_fixture(root)
            with self.assertRaises(RuntimeError):PROBE.verify_source(root,'0'*40)
            (root/'unrelated').write_text('changed');PROBE.helper.command(['git','add','.'],root)
            with self.assertRaises(RuntimeError):PROBE.verify_source(root,sha)

    def test_provenance_refuses_ignored_environment_file(self):
        with tempfile.TemporaryDirectory() as value:
            root=Path(value);(root/'.gitignore').write_text('.env\n');sha=PROBE.helper.git_fixture(root);(root/'.env').write_text('SYNTHETIC_ONLY=1')
            with self.assertRaises(RuntimeError):PROBE.verify_source(root,sha)

class SnapshotGraphTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='retainer-tests-');cls.bin=Path(cls.tmp.name)/'analyze'
        subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror',str(ROOT/'deploy/development/retainers/analyze.cpp'),'-o',str(cls.bin)],check=True,capture_output=True)
        cls.private=Path('/tmp/nadi-fix05-private');cls.private.mkdir(mode=0o700,exist_ok=True)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def graph(self,edges):
        strings=['','Map','SourceMap','system / Script','"use strict"; SYNTHETIC_PRIVACY_MARKER /home/private-owner','pendingOperations','generatedSourceMapCache','source','child']
        nn=[];ee=[]
        for i,(t,name,size) in enumerate([(9,0,0),(3,1,40),(3,2,40),(4,3,40),(2,4,100000)]):
            e=edges.get(i,[]);nn.extend([t,name,2*i+1,size,len(e),0,0]);ee.extend(v for edge in e for v in [edge[0],edge[1],edge[2]*7])
        return {'snapshot':{'meta':json.loads(json.dumps(META)),'node_count':5,'edge_count':len(ee)//3},'nodes':nn,'edges':ee,'strings':strings}
    def analyze(self,data):
        with tempfile.NamedTemporaryFile(mode='w',dir=self.private,suffix='.heapsnapshot') as f:
            json.dump(data,f);f.flush();return subprocess.run([str(self.bin),f.name],text=True,capture_output=True)
    def test_exclusive_flight_dominance(self):
        r=self.analyze(self.graph({0:[(0,5,1)],1:[(2,8,3)],3:[(3,7,4)]}));self.assertEqual(r.returncode,0,r.stderr);x=json.loads(r.stdout)
        m=next(m for m in x['mechanisms'] if m['name']=='Flight.pendingOperations');self.assertEqual(m['dominated_source_bytes'],100000);self.assertEqual(m['dominated_all_bytes'],100080)
        self.assertNotIn('PRIVACY_MARKER',r.stdout);self.assertNotIn('private-owner',r.stdout)
    def test_shared_reachability_is_not_exclusive_retention(self):
        r=self.analyze(self.graph({0:[(0,5,1),(0,6,2)],1:[(2,8,3)],2:[(2,8,3)],3:[(3,7,4)]}));self.assertEqual(r.returncode,0,r.stderr);x=json.loads(r.stdout)
        for m in x['mechanisms']:
            if m['name'] in ['Flight.pendingOperations','Node.sourceMapCache']:
                self.assertEqual(m['reachable_source_bytes'],100000);self.assertEqual(m['dominated_source_bytes'],0)
    def test_weak_edges_do_not_create_a_strong_alternative(self):
        r=self.analyze(self.graph({0:[(0,5,1),(0,6,2)],1:[(2,8,3)],2:[(6,8,3)],3:[(3,7,4)]}));self.assertEqual(r.returncode,0,r.stderr);x=json.loads(r.stdout)
        m=next(m for m in x['mechanisms'] if m['name']=='Flight.pendingOperations');self.assertEqual(m['dominated_source_bytes'],100000)
    def test_cycle_and_strong_shared_dominators(self):
        # A cycle does not turn a shared source into an exclusive Map-owned source.
        x=self.graph({0:[(0,5,1),(0,6,2)],1:[(2,8,3)],2:[(2,8,3)],3:[(2,8,1),(3,7,4)]})
        r=self.analyze(x);self.assertEqual(r.returncode,0,r.stderr)
        m=next(m for m in json.loads(r.stdout)['mechanisms'] if m['name']=='Flight.pendingOperations')
        self.assertEqual(m['dominated_source_bytes'],0)
    def test_graph_budget_and_bad_edge_refused(self):
        for mutate in [lambda x:x['snapshot'].update(node_count=4000001),lambda x:x['edges'].__setitem__(2,8),lambda x:x['edges'].__setitem__(0,99)]:
            x=self.graph({0:[(0,5,1)],1:[(2,8,3)],3:[(3,7,4)]});mutate(x)
            self.assertNotEqual(self.analyze(x).returncode,0)
    def test_random_small_graph_dominators_against_set_oracle(self):
        rng=random.Random(20261013)
        for trial in range(40):
            edges={0:[(0,5,1)],1:[(2,8,3)],3:[(3,7,4)]}
            for u in range(4):
                for v in range(1,4):
                    if rng.random()<0.35:edges.setdefault(u,[]).append((2,8,v))
            reachable={0}
            while True:
                new=reachable|{v for u in reachable for _,_,v in edges.get(u,[])}
                if new==reachable:break
                reachable=new
            dom={u:({0} if u==0 else set(reachable)) for u in reachable}
            while True:
                changed=False
                for u in sorted(reachable-{0}):
                    incoming=[dom[v] for v in reachable if any(to==u for _,_,to in edges.get(v,[]))]
                    new={u}|set.intersection(*incoming)
                    if new!=dom[u]:dom[u]=new;changed=True
                if not changed:break
            r=self.analyze(self.graph(edges));self.assertEqual(r.returncode,0,r.stderr)
            measured=next(m for m in json.loads(r.stdout)['mechanisms'] if m['name']=='Flight.pendingOperations')
            with self.subTest(trial=trial):
                self.assertEqual(measured['dominated_source_bytes'],100000 if 1 in dom[4] else 0)
                self.assertEqual(measured['dominated_all_bytes'],sum([0,40,40,40,100000][u] for u in reachable if 1 in dom[u]))
    def test_inline_map_marker_beyond_prefix_is_counted_without_content(self):
        x=self.graph({0:[(0,5,1)],1:[(2,8,3)],3:[(3,7,4)]});x['strings'][4]='"use strict";'+('x'*1024)+'//# sourceMappingURL=data:application/json;base64,SYNTHETIC_PRIVATE_MAP'
        r=self.analyze(x);self.assertEqual(r.returncode,0,r.stderr);measured=json.loads(r.stdout)
        self.assertEqual(measured['source_strings_with_inline_map_count'],1);self.assertEqual(measured['source_strings_with_inline_map_self_bytes'],100000)
        self.assertNotIn('SYNTHETIC_PRIVATE_MAP',r.stdout)
    def test_large_map_url_is_not_module_source_and_is_private(self):
        x=self.graph({0:[(0,5,1)],1:[(2,8,3)],3:[(3,9,4)]});x['strings'].append('source_map_url');x['strings'][4]='data:application/json;base64,SYNTHETIC_PRIVATE_MAP_URL'
        r=self.analyze(x);self.assertEqual(r.returncode,0,r.stderr);measured=json.loads(r.stdout)
        self.assertEqual(measured['large_source_map_url_self_bytes'],100000);self.assertEqual(measured['large_source_bytes'],0)
        m=next(m for m in measured['mechanisms'] if m['name']=='Flight.pendingOperations');self.assertEqual(m['dominated_map_url_bytes'],100000)
        self.assertNotIn('SYNTHETIC_PRIVATE_MAP_URL',r.stdout)
    def test_operation_ancestry_uses_own_properties_and_handles_cycles(self):
        strings=['','Map','Array','Object','system / Script','"use strict"; SYNTHETIC_SOURCE','pendingOperations','table','previous','awaited','owner','source']
        entries={0:[(0,6,1)],1:[(3,7,2)],2:[(3,7,3)],3:[(2,8,4)],4:[(2,9,3),(2,10,5)],5:[(3,11,6)]}
        nn=[];ee=[]
        for i,(t,name,size) in enumerate([(9,0,0),(3,1,40),(1,2,40),(3,3,40),(3,3,40),(4,4,40),(2,5,100000)]):
            edges=entries.get(i,[]);nn.extend([t,name,2*i+1,size,len(edges),0,0]);ee.extend(v for edge in edges for v in [edge[0],edge[1],edge[2]*7])
        x={'snapshot':{'meta':json.loads(json.dumps(META)),'node_count':7,'edge_count':len(ee)//3},'nodes':nn,'edges':ee,'strings':strings}
        r=self.analyze(x);self.assertEqual(r.returncode,0,r.stderr);a=json.loads(r.stdout)['flight_ancestry'];self.assertEqual(a['map_entry_candidates'],1);self.assertEqual(a['previous_awaited_nodes'],2);self.assertEqual(a['restricted_reachable_source_bytes'],100000)
    def test_schema_drift_refused(self):
        x=self.graph({0:[(0,5,1)],1:[(2,8,3)],3:[(3,7,4)]});x['snapshot']['meta']['node_fields'][0:2]=['name','type'];self.assertNotEqual(self.analyze(x).returncode,0)
    def test_nonprivate_path_refused(self):
        r=subprocess.run([str(self.bin),str(ROOT/'README.md')],capture_output=True,text=True);self.assertNotEqual(r.returncode,0);self.assertNotIn(str(ROOT),r.stderr)
if __name__=='__main__':unittest.main()
