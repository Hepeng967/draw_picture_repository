from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,base64,io,html,qrcode,fitz,shutil
from bs4 import BeautifulSoup
ROOT=Path(__file__).parent; DAT=Path('/mnt/data/16例科研散点图_原图来源索引.json')
meta=json.load(open(DAT,encoding='utf-8'))
font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
fontbold='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
f=lambda pt,bold=False: ImageFont.truetype(fontbold if bold else font,pt)
W,H=1680,1010
pdf=fitz.open()

def fit(im,w,h):
 im=im.copy().convert('RGB');im.thumbnail((w,h),Image.Resampling.LANCZOS);return im

def put_text(draw,text,xy,ft,maxw,fill='#263143'):
 x,y=xy
 parts=[];seg=''
 for t in str(text):
  if draw.textlength(seg+t,font=ft)>maxw and seg:parts.append(seg);seg=t
  else:seg+=t
 if seg:parts.append(seg)
 for part in parts[:3]:
  draw.text((x,y),part,font=ft,fill=fill);y+=ft.size+12
 return y

def make_pdfpage(image,links=()):
 pp=pdf.new_page(width=W,height=H)
 buf=io.BytesIO();image.save(buf,format='PNG',optimize=True)
 pp.insert_image(pp.rect,stream=buf.getvalue())
 for rect,url in links:
  if url and url.startswith('http'):
   try:pp.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(*rect),'uri':url})
   except Exception:pass

bg='#f7f9fc';blue='#184c77';dark='#192738'
cover=Image.new('RGB',(W,H),'#ffffff');d=ImageDraw.Draw(cover)
d.rectangle([0,0,W,19],fill=blue)
d.text((80,77),'科研散点图 · 16 例重新绘制',font=f(58,True),fill=dark)
d.text((80,156),'原论文视觉结构核对 / Python 合成数据绘图 / 用户审阅版',font=f(32),fill=blue)
d.rounded_rectangle((70,232,1610,372),radius=18,fill='#fff3e6',outline='#e5b96d',width=2)
d.text((100,251),'文件属性及可核查范围',font=f(28,True),fill='#9d6113')
d.text((100,303),'16 张新版图片均由 Python 实际渲染；原论文图在 PDF 中提供可点击网址与二维码。',font=f(24),fill=dark)
d.text((80,406),'图像本体无法从远程论文网站下载至本地，因此此版 PDF 尚不含离线原图。',font=f(26),fill='#b34c38')
d.text((80,451),'随附 HTML 通过原始公开网址加载原图，可左右并排直接对照。',font=f(25),fill=blue)
for i,row in enumerate(meta):
 x=72+(i%8)*199; y=540+(i//8)*210
 im=fit(Image.open(ROOT/f'case_{i+1:02d}'/'picture.png'),181,165)
 d.rounded_rectangle((x,y,x+186,y+195),radius=12,fill='#edf2f8')
 cover.paste(im,(x+(181-im.width)//2,y+6+(165-im.height)//2))
 d.text((x+8,y+171),f'Case {i+1:02d}',font=f(19,True),fill=blue)
d.text((80,957),'仅复现图形结构，不代表论文的真实实验数据；请通过原始论文确认具体含义。',font=f(21),fill='#65748a')
make_pdfpage(cover)
# strict difference records based on source visual inspected through web
notes={
1:'L-shaped alignment-uniformity distribution; marker families, accuracy colorbar.',
2:'Two dense calibration panels, blue performance strata, nonuniform point clouds.',
3:'Bubble area encodes model scale; increasing alignment, dense text annotation.',
4:'Three panels, distinct marker bands, black references, shared color scale.',
5:'Four method panels; axes concentrated at 0/1, translucent points, MAE labels.',
6:'2-by-2 log-scale compute vs performance; before/after groups and fits.',
7:'Per-model multi-shape scatter, trajectory arrows and percentage callouts.',
8:'Yellow Pareto region computed from the outermost non-dominated scatter points; logarithmic FLOPs, pink OLMo stars.',
9:'2-by-2 RL scaling panels, graded point colors, distinct axes, grey trend bands.',
10:'Fig. 3(d)-style PCA trajectory map: radial blue time trajectories, red x points, colored square endpoints, and PCA/time insets.',
11:'Three correction states, steep negative clean regression and displaced outliers.',
12:'Overlapping large transparent uncertainty ellipses with Deception Elo labels.',
13:'Diagonal decision boundary, pastel outcome regions and 2-axis error bars.',
14:'Four small joint plots; marginal histograms and zero reference lines.',
15:'2-by-2 joint KDE, triangular multimodal density, marginal density curves.',
16:'Dense colored embedding clusters, 100 perimeter labels and leader lines.'}
for i,row in enumerate(meta,1):
 img=Image.new('RGB',(W,H),bg);d=ImageDraw.Draw(img)
 d.rectangle((0,0,W,14),fill=blue)
 d.text((70,37),f'CASE {i:02d}',font=f(29,True),fill=blue)
 name=row['paper'];yend=put_text(d,name,(280,36),f(27,True),1310)
 d.text((75,132),f"{row['venue']}  ·  {row['figure']}  ·  arXiv:{row['arxiv']}",font=f(23),fill='#627489')
 # actual plot large LEFT
 d.rounded_rectangle([56,196,1076,855],radius=21,fill='white',outline='#d7e0ec',width=3)
 d.text((80,211),'新版 Python 复现图（合成数据）',font=f(25,True),fill=blue)
 plot=fit(Image.open(ROOT/f'case_{i:02d}'/'picture.png'),970,565)
 img.paste(plot,(64+(1008-plot.width)//2,266+(570-plot.height)//2))
 # source QR panel RIGHT
 d.rounded_rectangle([1100,196,1628,855],radius=21,fill='white',outline='#d7e0ec',width=3)
 d.text((1121,218),'论文原图入口',font=f(29,True),fill=blue)
 d.text((1121,270),'点击本区或扫码打开',font=f(22),fill=dark)
 source=row['sources'][0]
 qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=6,border=1);qr.add_data(source);qr.make(fit=True)
 q=qr.make_image(fill_color='#163e62',back_color='white').convert('RGB');q.thumbnail((308,308))
 img.paste(q,(1209,321))
 d.text((1123,644),'对照结构：',font=f(25,True),fill=dark)
 yy=680
 for line in [notes[i][:54],notes[i][54:]]:
  if line:yy=put_text(d,line,(1123,yy),f(18),478,fill='#637285')+1
 d.text((1123,790),'原图本体未离线嵌入',font=f(21),fill='#ac543a')
 d.text((72,889),'原论文 URL：',font=f(20,True),fill=blue)
 url=source
 if len(url)>125:url=url[:120]+'...'
 d.text((245,889),url,font=f(17),fill='#476485')
 d.text((72,929),'绘制修订说明：保留主要空间分布、配色、点形、分面及统计装饰；布局与数据允许变化。',font=f(20),fill=dark)
 d.text((72,971),f'{i:02d} / 16      点击右侧卡片可进入原论文原图；更多子图和 PDF 页面请查看 HTML。',font=f(18),fill='#637285')
 links=[((1100,196,1628,854),source),((244,886,1590,926),source),((60,126,990,167),f'https://arxiv.org/abs/{row["arxiv"]}')]
 make_pdfpage(img,links)

out=Path('/mnt/data/16例科研散点图_逐张重绘审阅版.pdf');pdf.save(out,garbage=4,deflate=True);pdf.close()
# generate browsable side-by-side link gallery: ORIGINAL online image at left, NEW picture offline base64 at right
style='''body{margin:0;background:#f3f6fb;color:#1d2737;font-family:Arial,sans-serif}header{padding:22px 35px;background:#183c5d;color:white;position:sticky;top:0;z-index:2}main{max-width:1550px;margin:auto;padding:25px}article{padding:20px 25px;margin:0 0 22px;background:white;border-radius:13px;box-shadow:0 2px 10px #dbe3ec}h2{font-size:21px;margin:5px 0 11px}p{font-size:13px;color:#567}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}.panel{border:1px solid #dae2ec;border-radius:8px;padding:12px;text-align:center;min-width:0}.panel img{display:block;max-width:100%;max-height:550px;object-fit:contain;margin:auto}.label{display:block;text-align:left;color:#205077;font-weight:bold;margin-bottom:12px}.links{display:flex;gap:22px;margin-top:14px}.links a{color:#195b93;font-weight:bold}@media(max-width:850px){.pair{grid-template-columns:1fr}header{position:relative}}'''
sections=[]
for i,row in enumerate(meta,1):
 pic=(ROOT/f'case_{i:02d}'/'picture.png').read_bytes();src='data:image/png;base64,'+base64.b64encode(pic).decode()
 source=row['sources'][0]; multi=''.join(f'<a href="{html.escape(u,quote=True)}" target="_blank">原图子图 {j+1}</a>' for j,u in enumerate(row['sources']))
 if source.split('#')[0].lower().endswith('.pdf'):
  original=f'<p style="padding:80px 10px">该论文仅有已核对的官方 PDF 图页入口，请点击下方链接。</p>'
 elif source.lower().endswith('.svg'):
  original=f'<img src="{html.escape(source,quote=True)}" loading="lazy" alt="source from paper"/>'
 else:
  original=f'<img src="{html.escape(source,quote=True)}" loading="lazy" alt="source from paper"/>'
 sections.append(f'<article id="case{i}"><h2>{i:02d}. {html.escape(row["paper"])}</h2><p>{row["venue"]} · {row["figure"]} · {row["arxiv"]}。仅右图使用模拟数据。</p><div class="pair"><div class="panel"><span class="label">论文原图（在线直链）</span>{original}</div><div class="panel"><span class="label">Python 新版绘制图</span><img src="{src}"></div></div><div class="links">{multi}<a href="https://arxiv.org/abs/{row["arxiv"]}" target="_blank">arXiv</a></div></article>')
htmlfile=Path('/mnt/data/16例科研散点图_在线原图并排对照_v2.html');htmlfile.write_text('<!doctype html><html lang="zh-CN"><meta charset="UTF-8"><title>16 例论文原图与 Python 新版对照</title><style>'+style+'</style><header><b>16 例论文原图 vs Python 新版复现</b><div style="font-size:13px">左侧原图联网加载；右侧模拟数据复现图已离线嵌入。原图属于论文作者。</div></header><main>'+''.join(sections)+'</main></html>',encoding='utf-8')
for i in range(1,17):
 code=(ROOT/f'case_{i:02d}'/'code.py')
 code.write_text(f'"""Case {i:02d} reproduction. Data inputs live in render_all.py:case{i:02d}()."""\nfrom pathlib import Path\nimport sys\nsys.path.insert(0,str(Path(__file__).resolve().parent.parent))\nfrom render_all import case{i:02d}\ncase{i:02d}()\n',encoding='utf-8')
(ROOT/'README.md').write_text('16-paper-style rebuild (synthetic data)\n\npython render_all.py => all 16 output plots.\npython case_01/code.py => plot case 01.\n\nSource metadata: /mnt/data/16例科研散点图_原图来源索引.json\nPlots can be modified through explicit x/y arrays in caseXX functions.\nOriginal images are NOT downloaded and are NOT embedded in the PDF. HTML shows originals online side by side.\n',encoding='utf-8')
pack=Path('/mnt/data/scatter_rebuild_v2.zip');shutil.make_archive(str(pack)[:-4],'zip',root_dir=ROOT)
print(out, out.stat().st_size,htmlfile,pack)
