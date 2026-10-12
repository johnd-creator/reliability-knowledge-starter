// EXPERIMENTAL CAUSAL CONTROL ONLY. Not installed by the official launcher.
// Weak ancestry links test whether Flight debug metadata causes measured retention.
// This changes private React diagnostics; it is not approved application remediation.
const prepared=new WeakSet();
function isDebugNode(value) {
  return value&&typeof value==='object'&&Number.isInteger(value.tag)&&value.tag>=0&&value.tag<=4&&
    ['owner','stack','start','end','promise','awaited','previous'].every(key=>Object.hasOwn(value,key));
}
function descriptor(value) {
  let reference=value&&typeof value==='object'?new WeakRef(value):null;
  return {enumerable:true,configurable:true,get(){return reference?.deref()??null;},set(next){
    prepare(next);reference=next&&typeof next==='object'?new WeakRef(next):null;
  }};
}
function prepare(node) {
  if(!node||prepared.has(node))return;
  if(!isDebugNode(node))throw Error('Unexpected private Flight metadata shape');
  prepared.add(node);
  for(const key of ['previous','awaited']) {
    const value=node[key];prepare(value);Object.defineProperty(node,key,descriptor(value));
  }
}
module.exports=class ExperimentalWeakFlightMap extends Map {
  set(key,value){prepare(value);return super.set(key,value);}
  get(key){const value=super.get(key);prepare(value);return value;}
};
