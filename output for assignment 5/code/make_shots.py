from PIL import Image, ImageDraw, ImageFont
F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",17); FB=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",17)
def shot(lines,fn,cmd):
    lh=24; W=max(len(l) for l in lines+[cmd])*10.5+60; W=int(max(W,900)); H=(len(lines)+3)*lh+50
    im=Image.new("RGB",(W,H),"#1e1e1e"); d=ImageDraw.Draw(im)
    d.rectangle([0,0,W,32],fill="#3a3a3a")
    for i,c in enumerate(["#ff5f56","#ffbd2e","#27c93f"]): d.ellipse([12+i*24,10,24+i*24,22],fill=c)
    d.text((W//2-100,6),"Terminal — dwdm/code",font=F,fill="#cccccc")
    y=46; d.text((20,y),"$ "+cmd,font=FB,fill="#7ee787"); y+=lh+6
    for l in lines: d.text((20,y),l,font=F,fill="#e6e6e6"); y+=lh
    im.save(fn)
def chunks(path,cmd,prefix,n=42):
    L=open(path).read().rstrip().split("\n"); out=[]
    for i in range(0,len(L),n):
        fn=f"../shots/{prefix}_{i//n+1}.png"; shot(L[i:i+n],fn,cmd if i==0 else "# (output continued)"); out.append(fn)
    print(prefix,len(out))
chunks("../outputs/task2_output.txt","python3 task2_text_mining.py","task2",40)
chunks("../outputs/task6_output.txt","python3 task6_spatial_clustering.py","task6",40)
chunks("../outputs/task9_output.txt","python3 task9_adaptation_experiments.py","task9",40)
chunks("../outputs/hand_calc_verification.txt","python3 hand_calc_verification.py","calc",40)
