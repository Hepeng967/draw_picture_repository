import os, math, sys, json, warnings
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse, Polygon
from matplotlib.ticker import PercentFormatter, ScalarFormatter
from scipy.stats import gaussian_kde
from mpl_toolkits.axes_grid1 import make_axes_locatable

ROOT=Path(__file__).parent
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':11,'axes.labelsize':10,'axes.spines.top':True,'axes.spines.right':True,'savefig.facecolor':'white'})

# All values generated below are synthetic, chosen to approximately reproduce
# the geometric patterns of the referenced paper figures. To use real data,
# replace the named numpy arrays or tables in each case function.

def rng(i):return np.random.default_rng(400+i)
def save(fig,i):
    p=ROOT/f'case_{i:02d}';p.mkdir(exist_ok=True)
    fig.savefig(p/'picture.png',dpi=170,bbox_inches='tight',facecolor='white')
    plt.close(fig)

def case01():
    r=rng(1);fig,ax=plt.subplots(figsize=(6.2,4.9))
    # x: uniformity, y: alignment, c: linear-probe accuracy, group: objective.
    xv=np.concatenate([r.normal(-3.88,.13,88), r.uniform(-3.5,-.02,60)])
    yv=np.concatenate([.19+1.5*np.exp(-np.abs(xv[:88]+4)*11)+r.normal(0,.14,88), .04+.27*np.exp(-.6*(xv[88:]+3.5))+r.normal(0,.03,60)])
    # Upper-left largely poor performance; lower elbow better performance.
    cv=np.clip(84-18*yv+r.normal(0,2,len(yv)),50,85)
    cv[xv>-.7]=r.uniform(51,62,np.sum(xv>-.7))
    sc=ax.scatter(xv,yv,c=cv,cmap='coolwarm_r',vmin=50,vmax=85,s=35,alpha=.87,edgecolors='none',marker='o')
    xplus=r.uniform(-3.0,-.7,17); yp=.36-.095*(xplus+3)+r.normal(0,.045,len(xplus))
    ax.scatter(xplus,yp,c=r.uniform(53,72,len(xplus)),cmap='coolwarm_r',vmin=50,vmax=85,marker='P',s=75,alpha=.55)
    xtri=r.uniform(-3.75,-1.0,12);yt=.36-.07*(xtri+3)+r.normal(0,.06,len(xtri))
    ax.scatter(xtri,yt,c=r.uniform(66,84,len(xtri)),cmap='coolwarm_r',vmin=50,vmax=85,marker='^',s=48,alpha=.52)
    ax.set(xlim=(-4.22,.25),ylim=(-.05,2.1),xlabel=r'$\mathcal{L}_{uniform}(t=2)$',ylabel=r'$\mathcal{L}_{align}(\alpha=2)$',title='Linear Classification on Outputs')
    ax.legend(handles=[Line2D([0],[0],marker='P',color='gray',ls='',label='Contrastive only'),Line2D([0],[0],marker='o',color='gray',ls='',label='Align / Uniform only'),Line2D([0],[0],marker='^',color='gray',ls='',label='All three mixed')],loc='upper right',framealpha=.9,fontsize=8)
    fig.colorbar(sc,ax=ax,label='Val Accuracy',fraction=.045,pad=.04)
    save(fig,1)

def case02():
    r=rng(2);fig,axs=plt.subplots(1,2,figsize=(10.5,4.4));fig.patch.set_facecolor('white')
    colors=['#b9d8ef','#82bce0','#4896cb','#237dbb','#075199'];cmap=LinearSegmentedColormap.from_list('blue',colors)
    # Panel 1: dense negatively sloped, panel 2: inverted arc with downward tail.
    n=2900;x=r.uniform(4.0,6.65,n);y=97.7-1.18*x+r.normal(0,.40,n);z=r.choice(5,n,p=[.15,.18,.23,.23,.21]);
    ax=axs[0];ax.set_facecolor('#EAEAF1');ax.scatter(x,y,c=np.array(colors)[z],s=8,alpha=.86,lw=0)
    ax.set(xlim=(3.7,6.85),ylim=(89.8,94.25),xlabel='ECE(%)',ylabel='Accuracy(%)');ax.yaxis.set_major_formatter(PercentFormatter(xmax=100,decimals=0))
    handles=[Line2D([0],[0],ls='',marker='o',color=colors[i],markersize=5,label=str([.5,.6,.7,.8,.9][i])) for i in range(5)]
    ax.legend(handles=handles,title='CIFAR-10-C AUC',fontsize=7,title_fontsize=8,loc='upper right',framealpha=.7)
    m=1800;x2=r.normal(5.5,1.5,m).clip(1.5,11);z2=r.choice(4,m,p=[.22,.24,.25,.29]);y2=92-1.32*(x2-5.1)-.18*(x2-5)**2+r.normal(0,1.6,m)-np.maximum(0,(3-z2))*r.exponential(4,m)
    ax=axs[1];ax.set_facecolor('#EAEAF1');ax.scatter(x2,y2,c=np.array(colors)[z2+1],s=11,alpha=.85,lw=0)
    ax.set(xlim=(-.5,12),ylim=(40,94),xlabel='ECE(%)',ylabel='Accuracy(%)');ax.yaxis.set_major_formatter(PercentFormatter(xmax=100,decimals=0))
    ax.legend(handles=[Line2D([0],[0],ls='',marker='o',color=colors[i+1],markersize=5,label=str([.45,.6,.75,.9][i])) for i in range(4)],title='CIFAR-10-C AUC',loc='lower left',fontsize=8,title_fontsize=8)
    for a in axs:a.grid(True,color='white',lw=1);a.set_axisbelow(True)
    fig.tight_layout();save(fig,2)

def case03():
    # Blue, increasing-radius circles; many model text labels with light gray grid.
    rows=[('bloom-560m',.153,.33,1),('bloom-1.1b',.163,.36,1.5),('bloom-1.7b',.160,.39,2),('bloom-3b',.175,.43,2.5),('bloom-7.1b',.18,.465,3.6),('olmo-1b',.18,.49,1.8),('openllama-3b',.193,.47,2.1),('openllama-7b',.21,.55,4),('gemma-2b',.193,.56,2.2),('gemma-7b',.205,.59,4.4),('olmo-7b',.19,.55,3),('llama-7b',.213,.59,4.5),('llama-13b',.218,.62,6),('llama-33b',.231,.65,9),('llama-65b',.237,.66,13),('mistral-7b',.213,.61,4),('llama3-8b',.223,.64,5),('llama3-70b',.239,.70,15),('mixtral-8x7b',.233,.675,11)]
    fig,ax=plt.subplots(figsize=(6.2,5.4));ax.set_facecolor('#f8f8f8')
    x=np.array([z[1] for z in rows]);y=np.array([z[2] for z in rows]);sz=np.array([z[3] for z in rows]);norm=(y-y.min())/(y.max()-y.min())
    ax.scatter(x,y,s=25+sz**1.95*8,c=norm,cmap='Blues',edgecolors='white',lw=.7,alpha=.94)
    for j,(name,xx,yy,s) in enumerate(rows):
        ax.text(xx+.0005,yy+(.005 if j%2==0 else -.008),name,fontsize=6.5,color='#555',alpha=.9)
    ax.set(xlim=(.135,.26),ylim=(.3,.72),xlabel='Alignment to VISION (DINOv2)',ylabel='Performance on Hellaswag')
    ax.grid(color='#e4e4e4',linewidth=.7);ax.set_axisbelow(True);fig.tight_layout();save(fig,3)

def case04():
    r=rng(4);fig,axs=plt.subplots(1,3,figsize=(12.8,3.65),sharey=True)
    cm='cool';norm=Normalize(vmin=-.5,vmax=.68)
    for j,a in enumerate(axs):
        # Distinct bands: squares near low region, diamonds, triangles and high stars.
        for k,(mk,scale,base) in enumerate([('s',.20,.33),('D',.26,.58),('^',.27,1.05),('*',.20,1.85)]):
            x=np.array([.12,.145,.17,.19,.235,.35,.50,.65]) if j==0 else np.array([.1,.13,.16,.2,.26,.4,.52,.65])
            if k==0:y=base+2.1*(x-.10)**.80
            elif k==1:y=base+1.6*(x-.1)**.75
            elif k==2:y=base+1.2*(x-.1)**.58
            else:y=base+.16*(x-.1)**.5
            v=(.57 if k in [2,3] else -.42) +.15*np.sin(3*x)+r.normal(0,.085,len(x))
            a.scatter(x,y,c=v,cmap=cm,norm=norm,marker=mk,s=42 if mk!='*' else 67,edgecolors='#9a87b9',lw=.25,alpha=.80)
        xx=np.linspace(.1,.7,150)
        for off in [.21,.43,.61]:a.plot(xx,.28+off+1.7*(xx-.1)**.8,color='#5b5b5b',lw=.8)
        a.set(xlim=(.085,.72),ylim=(.25,2.20),xlabel='Test error (train on real data only)',title=fr'synthetic dataset size $n_2={ [50,200,400][j]}$')
        a.set_yscale('log',base=3)
        a.grid(alpha=.08)
    axs[0].set_ylabel='Test error (train on real + synth.)'
    fig.subplots_adjust(left=.09,right=.91,bottom=.19,top=.86,wspace=.16)
    import matplotlib.cm as cmplt
    m=cmplt.ScalarMappable(norm=norm,cmap=cm)
    cb=fig.colorbar(m,ax=axs,location='right',fraction=.018,pad=.016);cb.ax.set_title(r'$\log_e(\psi)$',fontsize=9)
    save(fig,4)

def case05():
    r=rng(5);titles=['VinePPO','PPO','RLOO','GRPO'];cols=['#6b3187','#e2a00f','#4da6c0','#3bac80'];fig,axs=plt.subplots(2,2,figsize=(7.5,7.5),sharex=True,sharey=True)
    for k,(a,t,col) in enumerate(zip(axs.ravel(),titles,cols)):
        n=150
        if k==0:
            x=np.r_[r.beta(1.6,8,65),r.beta(3,2,35),r.normal(1,.035,50)].clip(0,1)
            y=np.r_[np.round(r.beta(1.2,3,65)*5)/5,r.beta(2,1.7,35),r.normal(1,.05,50)].clip(0,1)
        elif k==1:
            x=np.r_[r.normal(0,.018,100),r.normal(1,.016,65),r.uniform(0,1,45)].clip(0,1)
            y=np.r_[r.beta(1,7,100),r.beta(.85,.8,65),r.uniform(0,1,45)].clip(0,1)
        else:
            x=np.r_[r.normal(0,.024,50),r.uniform(0,1,70),r.normal(1,.021,50)].clip(0,1)
            y=np.round(r.uniform(0,1,len(x))*8)/8+r.normal(0,.01,len(x));y=y.clip(0,1)
        a.scatter(x,y,s=r.uniform(45,125,len(x)),c=col,alpha=.18,edgecolor='white',lw=.4)
        a.set(xlim=(-.18,1.18),ylim=(-.20,1.20),title=t)
        a.text(.06,.93,'MAE: '+['0.03','0.11','0.18','0.15'][k],transform=a.transAxes,fontsize=12,va='top')
        a.grid(color='#c1c1c1',lw=.85)
    fig.supxlabel('Ground Truth Value',fontsize=15);fig.supylabel('Predicted Value',fontsize=15)
    fig.subplots_adjust(left=.13,bottom=.11,right=.99,top=.94,hspace=.28,wspace=.25);save(fig,5)

def case06():
    r=rng(6);fig,axs=plt.subplots(2,2,figsize=(8.5,6.4),sharex=True)
    for j,a in enumerate(axs.flat):
        xx=np.power(10,r.uniform(20,24.0,62));t=np.log10(xx)-20
        for c,(col,shift) in enumerate([('#2588bc',0.0),('#e7a42d',1.0)]):
            y=np.clip((t-1.9)*(.13 if j%2==0 else .2)+(.25 if j%2==0 else .02)+shift*(.07 if j<2 else .002)+r.normal(0,.055,len(t)),.02,.75)
            a.scatter(xx,y,s=19,color=col,alpha=.75,lw=0)
            fitx=np.geomspace(1e20,1e24,100);tfit=np.log10(fitx)-20
            line=np.clip((tfit-1.9)*(.13 if j%2==0 else .2)+(.25 if j%2==0 else .02)+shift*(.07 if j<2 else .002),.02,.77)
            a.plot(fitx,line,color=col,lw=2.1)
        a.set_xscale('log');a.set_ylim(0,.80);a.set_title(['MMLU: before adjustment','GSM8K: before adjustment','MMLU: after adjustment','GSM8K: after adjustment'][j],fontsize=9.5)
        a.text(.04,.92,['Difference = 0.073','Difference = 0.191','Difference = 0.005','Difference = 0.005'][j],transform=a.transAxes,va='top',fontsize=8,bbox={'facecolor':'white','edgecolor':'#ddd','alpha':.8})
        a.grid(alpha=.18);a.set_ylabel('Accuracy' if j%2==0 else '')
        if j>1:a.set_xlabel('Pretraining compute (FLOPs)')
    fig.legend([Line2D([0],[0],marker='o',lw=0,color='#2588bc'),Line2D([0],[0],marker='o',lw=0,color='#e7a42d')],['Before Nov 2023','After Nov 2023'],loc='lower center',bbox_to_anchor=(.5,-.02),ncol=2)
    fig.tight_layout(rect=[0,.06,1,1]);save(fig,6)

def case07():
    fig,ax=plt.subplots(figsize=(8.2,6.2))
    # x: MBPP pass@1; y: HumanEval pass@1, labeled models with variable shape+area
    rec=[('Llama2-7B',26,14,85,'o','#ffa08a'),('Llama2-Chat-70B',52,32,450,'o','#992b12'),('CodeLlama-7B',57.5,38,90,'p','#a9efec'),('CodeLlama-34B',68,52,320,'p','#0bb6b6'),('CodeLlama-70B',72,57,500,'p','#007a7e'),('WizardCoder-CL',56.5,48,100,'v','#e498d5'),('DeepSeekCoder-Base',60.5,49,95,'^','#f2df7d'),('DeepSeekCoder-Instruct-6.7B',73,74,120,'^','#ffcf38'),('DeepSeekCoder-33B',79,78,210,'^','#e89612'),('Magicoder-7B',64,61,80,'d','#91b8f0'),('Magicoder-13B',68,71,75,'d','#5688e4'),('Magicoder-DS',76,77,95,'d','#235ecf'),('DirectlyMix',39,33,95,'X','#a8a8a8')]
    for n,x,y,s,m,c in rec:ax.scatter(x,y,s=s,marker=m,color=c,edgecolor='black',lw=1.0,zorder=3)
    for (start,end,c,txt) in [((26,14),(54.5,58),'#efa87a','176.6% improvement'),((57.5,38),(68.5,74),'#368fc4','49.9% improvement'),((60.5,49),(77,81),'#8cad52','33.3% improvement')]:
        ax.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'->','color':c,'lw':1.8,'linestyle':(0,(6,4)),'connectionstyle':'arc3,rad=.16'})
        ax.text((start[0]+end[0])/2,(start[1]+end[1])/2+7,txt,color=c,fontsize=10,fontweight='bold')
    ax.text(35,37,'Inferior performance from\ndirect multi-source mixing',color='gray',fontstyle='italic',fontsize=9)
    ax.set(xlim=(25,81),ylim=(10,83),xlabel='MBPP Score (Pass@1)',ylabel='HumanEval Score (Pass@1)');ax.grid(color='#a9a9a9',lw=.8)
    ax.legend([Line2D([0],[0],marker=m,lw=0,color=c,markeredgecolor='black',markersize=7) for _,_,_,_,m,c in rec[:10]], [e[0] for e in rec[:10]],fontsize=7,loc='upper left',ncol=1)
    fig.tight_layout();save(fig,7)

def case08():
    fig,ax=plt.subplots(figsize=(8.5,5.1))
    x=np.array([.60,.70,.82,1.05,1.25,1.38,1.63,1.84,2.4,2.8,3.7,4.1,4.55,5.4,6.7,8.0])
    y=np.array([35,39,51,57,62.5,54,60,66,63,67.5,72,74,70.5,75.5,73.5,75.])
    names=['Amber-7B','OLMo-7B','OLMo-0424-7B','DCLM-7B','OLMo-2-7B','Llama-2-13B','StableLM-2-12B','OLMo-2-13B','Llama-3.1-8B','Qwen-2.5-7B','OLMo-2-32B','Qwen-2.5-14B','Gemma-2-27B','Gemma-3-27B','Qwen-2.5-32B','Gemma-3-27B']
    ax.set(xlim=(.5,9),ylim=(30,80),xlabel='Approximate FLOPs',ylabel='Avg. Performance (10 Benchmarks)')
    ax.set_xscale('log')
    # Compute frontier directly from the outermost non-dominated scatter points.
    pts=sorted(zip(x,y), key=lambda t:t[0])
    frontier=[]; best=-1e9
    for xx,yy in pts:
        if yy>best:
            frontier.append((xx,yy)); best=yy
    fx=np.array([p[0] for p in frontier]); fy=np.array([p[1] for p in frontier])
    ymax=ax.get_ylim()[1]
    # light yellow Pareto region above the frontier, now derived from actual outer points
    ax.fill_between(fx, fy, ymax, step='post', color='#fff7bf', alpha=.82, zorder=0)
    ax.plot(fx, fy, color='#f0a9b6', ls='--', lw=1.3, zorder=1)
    for i,(xx,yy,n) in enumerate(zip(x,y,names)):
        if i in [4,7,10]: marker='*'; color='#ef4aa5'; ss=255; ec='white'; lw=.55
        elif i in [0,1,2,3]: marker='s'; color='#61d8b0'; ss=64; ec='white'; lw=.45
        elif i in [6,8]: marker='D'; color='#688b91'; ss=63; ec='white'; lw=.45
        else: marker='o'; color='#0d363a'; ss=53; ec='white'; lw=.45
        ax.scatter(xx,yy,marker=marker,color=color,s=ss,edgecolors=ec,lw=lw,zorder=3)
        ax.text(xx*1.02,yy+1.3,n,fontsize=7,color='#0d3438' if marker!='*' else '#b20a6a')
    ax.grid(color='#bad3d1',ls=':',alpha=.60); ax.set_axisbelow(True)
    ax.legend([Line2D([0],[0],marker=m,color='w',markerfacecolor=c,markersize=10 if m=='*' else 7) for m,c in [('*','#ef4aa5'),('s','#61d8b0'),('D','#688b91'),('o','#0d363a')]],['Ours','Other fully open','Partially open','Open weights'],loc='upper center',bbox_to_anchor=(.5,1.11),ncol=4,fontsize=8,frameon=False)
    fig.tight_layout(); save(fig,8)

def case09():
    r=rng(9);fig,axs=plt.subplots(2,2,figsize=(8.5,6.7),sharex='col')
    cols=['#bccb19','#6faad7'];cm=LinearSegmentedColormap.from_list('perf',cols)
    for j,a in enumerate(axs.flat):
        n=24;xc=r.uniform(0,1,n)
        if j%2==0:xx=235+230*xc;yy=(2.4-.15*xc+.36*r.normal(size=n)) if j==0 else 205-85*xc+37*r.normal(size=n)
        else:xx=13+21*xc;yy=(5.7-4*xc+.27*r.normal(size=n)) if j==1 else 5+7.5*xc+.35*r.normal(size=n)
        col=300+400*xc;mm=xc>.75
        xxg=np.linspace(min(xx),max(xx),100);coeff=np.polyfit(xx,yy,1);fit=np.polyval(coeff,xxg)
        a.fill_between(xxg,fit-.3*(1+j/2),fit+.3*(1+j/2),color='#b7b7b7',alpha=.2,zorder=0)
        a.plot(xxg,fit,color='#999999',ls='--',lw=2.5)
        sc=a.scatter(xx[~mm],yy[~mm],c=col[~mm],cmap=cm,vmin=300,vmax=700,s=58,edgecolors='none')
        a.scatter(xx[mm],yy[mm],c=col[mm],cmap=cm,vmin=300,vmax=700,s=52,marker='X')
        a.text(.38,.92,r'$R^2=$'+['-0.06','0.94','0.32','0.94'][j],transform=a.transAxes,fontsize=10)
        a.grid(color='#eeeeee',alpha=.6);a.set_axisbelow(True)
        cb=fig.colorbar(sc,ax=a,fraction=.05,pad=.035)
        if j%2:cb.set_label('Performance level',rotation=90)
    axs[0,0].set_title('h1-pole-v0');axs[0,1].set_title('humanoid-stand')
    axs[0,0].set_ylabel('Optimal UTD');axs[1,0].set_ylabel('Optimal model size')
    axs[1,0].set_xlabel('Optimal budget');axs[1,1].set_xlabel('Optimal budget')
    fig.tight_layout();save(fig,9)

def case10():
    from matplotlib.collections import LineCollection
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    r=rng(10); fig,ax=plt.subplots(figsize=(8.0,5.3))
    ax.set_facecolor('#ececec')
    center=np.array([0.05,-0.02])
    # radial / slightly curved trajectories, approximating Fig. 3(d)
    n_traj=34
    angles=np.linspace(-2.45,2.35,n_traj)+r.normal(0,.06,n_traj)
    lens=0.55+1.45*r.random(n_traj)
    time_colors=plt.cm.Blues(np.linspace(.35,.95,12))
    endpoint_colors=['#f1d400','#3dc35d','#f79aa2','#81c9ff']
    for k,(ang,L) in enumerate(zip(angles,lens)):
        t=np.linspace(0,1,12)
        bend=.14*np.sin(2*ang)
        rr=L*(0.1+0.9*t)
        x=center[0]+rr*np.cos(ang)+bend*(t**1.4)
        y=center[1]+rr*np.sin(ang)+0.08*np.sin(np.pi*t)*(0.7*np.sign(np.sin(ang))+0.3)
        pts=np.c_[x,y]
        segs=np.stack([pts[:-1],pts[1:]],axis=1)
        lc=LineCollection(segs, colors=time_colors[:-1], linewidths=1.3, alpha=.95, zorder=2)
        ax.add_collection(lc)
        ax.plot(x,y,color='#3650b3',lw=.35,alpha=.35,zorder=1)
        ax.scatter(x,y,s=6,c=time_colors,zorder=3,linewidths=0)
        if k%5==0:
            ax.scatter(x[-1],y[-1],s=30,marker='s',c=endpoint_colors[(k//5)%len(endpoint_colors)],edgecolors='none',zorder=4)
    # red x points spread across the manifold
    redx=np.vstack([
        r.normal([0.0,0.0],[.42,.32],(78,2)),
        np.c_[r.uniform(-1.6,1.5,38), r.uniform(-1.1,1.1,38)]
    ])
    ax.scatter(redx[:,0],redx[:,1],marker='x',s=18,c='#cf3d3b',lw=.9,zorder=2)
    # central cluster and small green cloud
    green=np.c_[r.normal(-.25,.16,45),r.normal(-.55,.07,45)]
    ax.scatter(green[:,0],green[:,1],s=9,c='#28b621',alpha=.9,zorder=3,linewidths=0)
    # axes arrows resembling x1/x2 and side indicators
    ax.annotate('',xy=(1.95,-1.05),xytext=(1.55,-1.05),arrowprops=dict(arrowstyle='-|>',color='black',lw=1.2))
    ax.annotate('',xy=(1.55,-0.58),xytext=(1.55,-1.05),arrowprops=dict(arrowstyle='-|>',color='black',lw=1.2))
    ax.text(2.0,-1.07,r'$x_1$',fontsize=12); ax.text(1.51,-0.52,r'$x_2$',fontsize=12)
    ax.annotate('',xy=(-1.2,0.78),xytext=(-1.55,0.42),arrowprops=dict(arrowstyle='-|>',color='black',lw=1.2))
    ax.annotate('',xy=(-1.28,-0.68),xytext=(-1.55,-0.32),arrowprops=dict(arrowstyle='-|>',color='black',lw=1.2))
    ax.text(-1.57,0.44,r'$x_2$',fontsize=12,rotation=36); ax.text(-1.59,-0.71,r'$x_1$',fontsize=12,rotation=-35)
    # time gradient inset
    iax=inset_axes(ax,width='18%',height='6%',loc='upper right',borderpad=1.3)
    iax.imshow(np.linspace(0,1,256)[None,:],aspect='auto',cmap='Blues',origin='lower')
    iax.set_xticks([]); iax.set_yticks([]); iax.set_title('Time',fontsize=10,pad=2)
    for s in iax.spines.values(): s.set_visible(False)
    # PCA inset
    pax=inset_axes(ax,width='14%',height='18%',loc='upper right',bbox_to_anchor=(0.17,0.02,1,1),bbox_transform=ax.transAxes,borderpad=0)
    vals=np.array([43,18,6,1.8,1.2,.8,.7,.5,.45,.4])
    pax.plot(range(1,11),vals,color='#4a86c5',lw=1.3)
    pax.set_title('PCA',fontsize=9,pad=2); pax.set_ylabel('Variance %',fontsize=7); pax.set_xlabel('Component #',fontsize=7)
    pax.tick_params(labelsize=7,length=2)
    pax.spines[['top','right']].set_visible(False)
    # small categorical block inset
    cax=inset_axes(ax,width='9%',height='9%',loc='center right',borderpad=.9)
    block=np.array([[[0.95,0.85,0.0],[0.53,0.80,1.0]],[[0.24,0.76,0.29],[0.97,0.62,0.72]]])
    cax.imshow(block,interpolation='nearest'); cax.set_xticks([]); cax.set_yticks([])
    for s in cax.spines.values(): s.set_visible(False)
    ax.text(-1.95,1.28,'d',fontsize=16,fontweight='bold')
    ax.set_xlim(-2.0,2.1); ax.set_ylim(-1.3,1.35)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    fig.tight_layout(); save(fig,10)

def case11():
    r=rng(11);fig,axs=plt.subplots(1,3,figsize=(13,4.0),sharex=True,sharey=True)
    x=r.normal(0,.94,350);y=-.63*x+.12+r.normal(0,.22,len(x))
    xo=r.normal(3.9,.22,200);yo=r.normal(6.5,.24,200)
    for i,delta in enumerate([0,.9,1.5]):
        a=axs[i];a.scatter(x,y,s=17,color='#4596ce',alpha=.52,label='Clean Data')
        if i<2:
            a.scatter(xo,yo,s=16,color='#ff9130',alpha=.54,label='Outlier Data')
            if i==1:a.scatter(r.normal(3.8,.18,170),r.normal(.15,.025,170),s=12,color='#d9cb48',alpha=.7,label='Rectified')
        else:
            a.scatter(r.normal(0,.9,150),-.63*r.normal(0,.9,150)+r.normal(0,.12,150),s=10,color='#d9cb48',alpha=.70,label='Rectified')
        xx=np.array([-3,5]);a.plot(xx,-.64*xx+.30,color='black',lw=1.5,label='Ground Truth')
        if i==0:ry=1.35*xx+1.0
        elif i==1:ry=-.03*xx+.20
        else:ry=-.67*xx+.28
        a.plot(xx,ry,color='red',lw=1.3,label='Concave Rectifier')
        a.set(xlim=(-3.5,5.5),ylim=(-5,9),xlabel='x',title=rf'Rectified Distribution, $\delta={delta}$')
        a.grid(alpha=.12)
    axs[0].set_ylabel('y');axs[0].legend(loc='upper left',fontsize=7);fig.tight_layout();save(fig,11)

def case12():
    r=rng(12);fig,ax=plt.subplots(figsize=(8.6,5.3));ax.set_facecolor('#fbfaf7')
    names=['qwen-2.5-7b-instruct','llama-4-maverick','mistral-small','claude-3-opus','phi-4','deepseek-chat-v3','gemma-3-4b','deepseek-r1-distill','llama-3.3-70b','gemini-2.0','qwen3-235b','gemini-2.5-pro','grok-3-beta','claude-3.7-sonnet','claude-3.7-thinking']
    x=np.array([37.5,43,43.8,43,47,47.1,46.6,49,50,49.6,51,52.1,54.6,56.2,58.8]);y=np.array([1612,1634,1630,1612,1690,1688,1708,1721,1719,1701,1750,1723,1776,1818,1820]);
    palette=['#ef8c1a','#6e358d','#6d7b86','#cbad93','#29954e','#048f95','#5488d2','#7fc8c6','#8c59aa','#2f8dde','#e36c15','#1261bb','#15bd78','#a87951','#a87951']
    for i,(name,xx,yy,c) in enumerate(zip(names,x,y,palette)):
        # Large translucent ellipses whose centers coincide with colored dots.
        e=Ellipse((xx,yy),width=3.3 if i<5 else 5.2,height=r.uniform(145,320),facecolor=c,alpha=.065,edgecolor='none',zorder=1)
        ax.add_patch(e);ax.scatter(xx,yy,s=190,color=c,edgecolor='black',lw=1.2,zorder=3)
        ax.text(xx-3 if i%3==0 else xx+.3,yy+19 if i%2 else yy-28,name,fontsize=8.4,color=c if i%3==0 else '#303745',zorder=4)
    ax.set(xlim=(34,63),ylim=(1500,1900),xlabel='Win Rate (%)',ylabel='Deception Elo');ax.grid(color='#d5d5d5',lw=.85)
    fig.tight_layout();save(fig,12)

def case13():
    fig,ax=plt.subplots(figsize=(8.0,5.5));ax.set(xlim=(0,.32),ylim=(1.0,1.5),xlabel='Sensitivity (x-axis)',ylabel='Environment Tuned Performance (y-axis)')
    xx=np.linspace(0,.32,200);line=1.165+.94*xx
    ax.fill_between(xx,1,line,color='#fae4e4',zorder=0)
    ax.fill_between(xx,line,1.265,where=(line<1.265),color='#d8bbd5',zorder=0)
    ax.fill_between(xx,np.maximum(line,1.265),1.5,color='#fffde3',zorder=0)
    ax.axvspan(0,.105,ymin=(1.265-1)/.5,ymax=1,color='#e0eddf',alpha=.8)
    ax.fill_between(xx,1.265,np.minimum(line,1.5),where=line>1.265,color='#f8c4c4',alpha=.85,zorder=0)
    ax.plot(xx,line,color='#ed92bf',lw=.75)
    pts=[('PPO',.103,1.268,'#1d96cc'),('Observation zero-mean\nnormalization',.076,1.26,'#42a55c'),('Observation symlog',.109,1.26,'#f68424'),('Advantage per-minibatch\nzero-mean normalization',.138,1.36,'#9d4bab'),('Advantage lower-bounded\npercentile scaling',.145,1.29,'#c66536'),('Advantage percentile scaling',.254,1.315,'#e97dcb'),('Value target symlog',.119,1.11,'#a5a5a5')]
    for name,x,y,c in pts:
        ax.errorbar(x,y,xerr=.013,yerr=.009,fmt='o',markersize=5,capsize=4,lw=1.3,color=c)
        dx=.014 if x<.2 else -.05;dy=.045 if y<1.27 else .02
        ax.text(x+dx,y+dy,name,fontsize=8,color=c,va='center')
    ax.text(.025,1.4,'Observation\nzero-mean\nnormalization',color='#43a260',fontsize=8)
    ax.set_xticks([0,.15,.3]);ax.set_yticks([1,1.2,1.5]);ax.grid(alpha=.12)
    ax.set_title('Environment Tuned Performance (y-axis)');fig.tight_layout();save(fig,13)

def case14():
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    r=rng(14);fig=plt.figure(figsize=(10.4,8.4));outer=fig.add_gridspec(2,2,wspace=.35,hspace=.42)
    for j in range(4):
        sub=outer[j//2,j%2].subgridspec(5,5,hspace=.035,wspace=.025)
        ax=fig.add_subplot(sub[1:,:4]);tx=fig.add_subplot(sub[0,:4],sharex=ax);ry=fig.add_subplot(sub[1:,4],sharey=ax)
        x1=r.normal(88,6,160);y1=r.normal(2.2,.9,160)
        x2=r.uniform(30,96,80);y2=r.normal(.8,2.6,80)
        x3=r.uniform(30,98,70);y3=r.normal(-.4,1.3,70)
        if j>0:x2=x2*.3+66; x1=x1*.2+78
        if j>1:y1=y1*.35; y2=y2*.55;y3=y3*.35
        for xx,yy,c,n in [(x1,y1,'#55b4e9','KW'),(x2,y2,'#b8c5c8','KWC'),(x3,y3,'#b57cc2','Diff')]:
            ax.scatter(xx,yy,s=18,c=c,alpha=.52,lw=0,label=n)
            tx.hist(xx,bins=18,histtype='step',color='#aaa',lw=.75)
            ry.hist(yy,bins=18,histtype='step',color='#aaa',lw=.75,orientation='horizontal')
        ax.axhline(0,color='#ed618c',ls='--',lw=1.2)
        ax.set(xlim=(30,102),ylim=(-9,8),xlabel='Accuracy (%) of ERM',ylabel='Improvement of SD (%)' if j%2==0 else '')
        ax.grid(alpha=.2);ax.legend(fontsize=6,loc='lower right',framealpha=.65)
        tx.axis('off');ry.axis('off')
        ax.set_title(['One source','Two sources','Three sources','Four sources'][j],y=-.40,fontsize=10)
    fig.tight_layout();save(fig,14)

def case15():
    from scipy.stats import gaussian_kde
    r=rng(15);fig=plt.figure(figsize=(9.8,9.8));outer=fig.add_gridspec(2,2,wspace=.29,hspace=.22)
    specs=[('Original','#25a5a0',(-1.2,.5)),('Ours','#8a9ccb',(-.8,.8)),('DiffPure','#57bda9',(-1,1)),('REAP','#f78b6e',(-.95,.55))]
    for i,(name,c,sh) in enumerate(specs):
        # three-point triangular mixture reproduces original density geometry
        centers=[(-1.25,-.5),(1.1,-.4),(-.1,1.65)]
        if i==2:centers=[(-1.2,-.7),(1.,-.25),(-.2,1.)]
        if i==3:centers=[(-1.0,-.8),(1.2,-.7),(.2,.8)]
        points=np.vstack([r.multivariate_normal(cc,[[.25,.06],[.06,.22]],210) for cc in centers]);x,y=points.T
        gs=outer[i//2,i%2].subgridspec(5,5,hspace=.015,wspace=.03)
        ax=fig.add_subplot(gs[1:,:4]);ta=fig.add_subplot(gs[0,:4],sharex=ax);ra=fig.add_subplot(gs[1:,4],sharey=ax)
        gx=np.linspace(-3,3,90);gy=np.linspace(-2.2,3,90);xx,yy=np.meshgrid(gx,gy)
        kde=gaussian_kde(np.vstack([x,y]),bw_method=.19);z=kde(np.vstack([xx.ravel(),yy.ravel()])).reshape(xx.shape)
        # custom semi-transparent contour levels with color derived from base
        import matplotlib.colors as mc
        col=mc.to_rgb(c);cmap=LinearSegmentedColormap.from_list('custom'+str(i),[(1,1,1),col])
        levels=np.linspace(np.percentile(z,68),z.max(),10)
        ax.contourf(xx,yy,z,levels=levels,cmap=cmap,alpha=.70,extend='min')
        ax.scatter(x,y,s=11,c=c,alpha=.80,edgecolors='white',lw=.24)
        ta.plot(gx,gaussian_kde(x)(gx),c=c,lw=.85);ta.fill_between(gx,gaussian_kde(x)(gx),color=c,alpha=.24)
        ra.plot(gaussian_kde(y)(gy),gy,color=c,lw=.9);ra.fill_betweenx(gy,0,gaussian_kde(y)(gy),color=c,alpha=.22)
        ta.axis('off');ra.axis('off');ax.set(xlim=(-3,3),ylim=(-2.2,3));ax.set_xticklabels([]);ax.set_yticklabels([]);ax.grid(color='#bfbfbf',alpha=.5)
        ax.set_xlabel(name,fontsize=12)
    fig.tight_layout();save(fig,15)

def case16():
    r=rng(16);fig,ax=plt.subplots(figsize=(9.0,9.0))
    # replace x,y,cls and label names to use a real embedding dataset
    labels=['apple','aquarium','baby','bear','beaver','bee','beetle','bicycle','bottle','bowl','bridge','bus','butterfly','camel','can','castle','caterpillar','cattle','chair','chimpanzee','clock','cloud','cockroach','couch','crab','crocodile','cup','dinosaur','dolphin','elephant','flatfish','forest','fox','girl','hamster','house','kangaroo','keyboard','lamp','lawnmower','leopard','lion','lizard','lobster','man','maple','motorcycle','mountain','mouse','mushroom','oak','orange','orchid','otter','palm','pear','pickup','pine','plain','plate','poppy','porcupine','possum','rabbit','raccoon','ray','road','rocket','rose','sea','seal','shark','shrew','skunk','skyscraper','snail','snake','spider','squirrel','streetcar','sunflower','sweetpepper','table','tank','telephone','television','tiger','tractor','train','trout','tulip','turtle','wardrobe','whale','willow','wolf','woman','worm','bee2','lion2']
    n=len(labels);ang=np.linspace(-np.pi,np.pi,n,endpoint=False);rad=.25+3.05*r.beta(2.0,1.55,n)
    centers=np.c_[rad*np.cos(ang),rad*np.sin(ang)]
    colors=plt.cm.tab20(np.linspace(0,1,20))
    for i,(name,center) in enumerate(zip(labels,centers)):
        npts=30
        angle=ang[i];orient=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
        cloud=r.normal(0,1,(npts,2))@np.diag([.12+.04*r.random(),.21+.07*r.random()])@orient.T+center
        ax.scatter(cloud[:,0],cloud[:,1],s=3.7,color=colors[i%20],alpha=.7,lw=0)
        # radial label + leader line; labels follow perimeter, rotated tangentially.
        labelrad=5.4;lx=labelrad*np.cos(angle);ly=labelrad*np.sin(angle)
        ax.plot([center[0],lx*.92],[center[1],ly*.92],color='#bbb',lw=.35,alpha=.7)
        rot=np.degrees(angle)+90
        if 90<rot<270:rot-=180
        ax.text(lx,ly,name,fontsize=5.7,rotation=rot,color=colors[i%20],ha='center',va='center',rotation_mode='anchor')
    ax.set_aspect('equal');ax.axis('off');ax.set(xlim=(-6.4,6.4),ylim=(-6.4,6.4));fig.subplots_adjust(left=.01,right=.99,bottom=.01,top=.99)
    save(fig,16)

CASES=[case01,case02,case03,case04,case05,case06,case07,case08,case09,case10,case11,case12,case13,case14,case15,case16]
if __name__=='__main__':
    if len(sys.argv)>1:CASES[int(sys.argv[1])-1]()
    else:
        for i,fun in enumerate(CASES,1):
            try:fun();print(f'OK case {i:02d}',flush=True)
            except Exception as e:print('FAIL',i,e,flush=True);raise
