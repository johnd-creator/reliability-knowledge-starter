"""Plot sanitized FIX06 summaries only; no source content or raw profiles."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=argparse.ArgumentParser();p.add_argument('baseline');p.add_argument('candidate');p.add_argument('output');a=p.parse_args()
fig,axes=plt.subplots(3,1,figsize=(10,9),sharex=True)
for file,color in [(a.baseline,'#334155'),(a.candidate,'#118C45')]:
 d=json.loads(Path(file).read_text());name=d['mode']
 rows=d['timeline'];x=[r['seconds']/60 for r in rows]
 axes[0].plot(x,[r['heap_mib'] for r in rows],color=color,label=name)
 gc=d['major_gc_timeline'];axes[0].scatter([r['seconds']/60 for r in gc],[r['heap_mib'] for r in gc],s=7,color=color,alpha=.4,label=name+' natural major GC')
 axes[1].plot(x,[r['rss_mib'] for r in rows],color=color,label=name)
 axes[2].plot(x,[r['external_mib'] for r in rows],color=color,label=name)
 if d['result'].get('failure'):
  for ax in axes:ax.axvline(d['elapsed']/60,color=color,linestyle=':',alpha=.5)
axes[0].annotate('Candidate guard stop: extra PID\ncause UNKNOWN; no retry',xy=(39.58,560),xytext=(44,610),fontsize=9,arrowprops={'arrowstyle':'->','color':'#118C45'})
axes[0].annotate('Baseline threshold restart',xy=(79.85,1648.9),xytext=(59,1550),fontsize=9,arrowprops={'arrowstyle':'->','color':'#334155'})
axes[0].axhline(1676.8,color='#DC2626',linestyle='--',label='Next used-heap threshold (~80%)')
for ax,label in zip(axes,['Heap used (MiB)','Worker RSS (MiB)','External memory (MiB)']):
 ax.set_ylabel(label);ax.grid(alpha=.2);ax.legend(loc='upper left')
axes[-1].set_xlabel('Elapsed minutes (original worker only)')
fig.suptitle('NADI FIX-06 — isolated synthetic workload; no live acceptance',fontsize=13)
fig.tight_layout();fig.savefig(a.output,dpi=160);plt.close(fig)
