"""Export numeric evidence figures; raw profiles and records are never plotted."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def rows(path):return [json.loads(x) for x in path.read_text().splitlines()]

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--output',required=True);args=p.parse_args();root=Path(args.root);out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(2,1,figsize=(11,7),layout='constrained')
    for name,label,color in [('nav-poll-v2','Navigation + polling','#15803d'),('poll-only-v2','Polling-dominated','#2563eb'),('nav-no-poll','Navigation without polling [graph probe]','#9333ea'),('nav-hmr-corrected','Navigation + HMR [graph probe]','#b45309')]:
        path=root/name
        if not (path/'progress.json').exists():continue
        pid=json.loads((path/'progress.json').read_text())['expected_worker'];heap=rows(path/f'heap-{pid}.jsonl');gc=[r for r in rows(path/f'gc-{pid}.jsonl') if r['kind']==4];origin=heap[0]['at']
        axes[0].plot([(r['at']-origin)/60000 for r in heap],[r['heapUsed']/1048576 for r in heap],color=color,alpha=.75,linewidth=1,label=label)
        axes[1].plot([(r['at']-origin)/60000 for r in gc],[r['heapUsed']/1048576 for r in gc],color=color,linewidth=1,label=label)
        result=json.loads((path/'result.json').read_text()) if (path/'result.json').exists() else {}
        if result.get('failure')=='UNEXPECTED_WORKER_GENERATION':
            # Plot the original generation only. A replacement worker's lower
            # heap is a failed gate, not a successful memory improvement.
            end=(heap[-1]['at']-origin)/60000
            for ax in axes:ax.axvline(end,color='#dc2626',linestyle=':',linewidth=1.2,label='Worker replacement (~65 min)')
    for ax in axes:
        ax.set_ylabel('V8 heap (MiB)');ax.grid(alpha=.18);ax.set_xlim(left=0);ax.set_ylim(0,1800);ax.legend(fontsize=9,loc='upper left')
    axes[0].axhline(1676.8,linestyle='--',color='#dc2626',linewidth=1,label='Next threshold')
    axes[0].legend(fontsize=9,loc='upper left')
    axes[0].set_title('PR77 isolated fixture workload — unchanged resource limits');axes[1].set_title('Observer-time heap following major GC (approximation)');axes[1].set_xlabel('Elapsed minutes since process startup')
    fig.savefig(out/'heap-timeline.png',dpi=150);plt.close(fig)
    path=root/'nav-hmr-corrected';progress=json.loads((path/'progress.json').read_text());events=rows(path/f"flight-{progress['expected_worker']}.jsonl")
    fig,ax=plt.subplots(figsize=(11,4),layout='constrained');origin=events[0]['at']
    ax.plot([(r['at']-origin)/60000 for r in events],[r['mapSize'] for r in events],label='Live Map entries',color='#2563eb')
    ax.plot([(r['at']-origin)/60000 for r in events],[r['ancestryNodes'] for r in events],label='Reachable ancestry (500k cap)',color='#b45309')
    truncated=[r for r in events if r['truncated']];ax.scatter([(r['at']-origin)/60000 for r in truncated],[r['ancestryNodes'] for r in truncated],marker='^',color='#dc2626',label='Truncated: lower bound')
    ax.set_title('Flight debug Map versus retained previous/awaited ancestry');ax.set_xlabel('Minutes since first graph sample');ax.set_ylabel('Count');ax.grid(alpha=.18);ax.legend(fontsize=9);fig.savefig(out/'flight-ancestry.png',dpi=150)

if __name__=='__main__':main()
