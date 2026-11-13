import json,os,sys,urllib.request as u
U=os.getenv("MAKEFUN_ENV_URL") or sys.exit(1)
F="abcdefgh"
T=[[ord(c)-80 for c in s] for s in ["PPPPUZZ<UKFPPPPdUUZiZZdnxxxxPPPP","dnZPddPPF<<<<22(2((#2((#2((#2((#"]]
N=[33,31,18,14,-14,-18,-31,-33]
D=[15,17,-15,-17]
R=[1,-1,16,-16]
K=R+D
SQ=[i for i in range(128)if not i&0x88]
CK=[15]*128
CK[0],CK[7],CK[4],CK[112],CK[116],CK[119]=13,14,12,7,3,11
M=10**5
TT={}
KL={}
nd=[0]
def uci(m):
 f,t,p=m
 return F[f&7]+str(f//16+1)+F[t&7]+str(t//16+1)+("nbrq"[p-2] if p else "")
def parse(f):
 b=[0]*128
 p=f.split()
 i=112
 for ch in p[0]:
  if ch=="/":i-=24
  elif ch.isdigit():i+=int(ch)
  else:b[i]=" pnbrqk".find(ch.lower())*(1-2*ch.islower());i+=1
 w=2*(p[1]=="w")-1
 c=sum(1<<i for i,ch in enumerate("KQkq")if ch in p[2])
 e=-1 if p[3]=="-" else (int(p[3][1])-1)*16+F.find(p[3][0])
 return b,w,c,e
def atk(b,s,q):
 for d in (-17*q,-15*q):
  t=s+d
  if not t&0x88 and b[t]==q:return 1
 for o,v in ((N,2),(K,6)):
  for d in o:
   t=s+d
   if not t&0x88 and b[t]==v*q:return 1
 for d in D+R:
  t=s+d
  while not t&0x88 and not b[t]:t+=d
  if not t&0x88 and b[t] in (5*q,3*q if d in D else 4*q):return 1
 return 0
def gen(b,w,c,e,cap):
 ms=[]
 d=16*w
 for f in SQ:
  p=b[f]
  if p*w<=0:continue
  a=abs(p)
  if a==1:
   tg=[t for t in (f+d-1,f+d+1) if not t&0x88 and (b[t]*w<0 or t==e)]
   if not b[f+d]:tg.append(f+d)
   if not cap and f+d in tg and f//16==1+5*(w<0) and not b[f+2*d]:ms.append((f,f+2*d,0))
   ms+=[(f,t,q) for t in tg for q in ((5,4,3,2) if t//16==7-7*(w<0) else (0,)) if q or not cap or t!=f+d]
  elif a==2 or a==6:
   for o in N if a==2 else K:
    t=f+o
    if not t&0x88 and (b[t]*w<0 or not cap and not b[t]):ms.append((f,t,0))
   if a==6 and not cap:
    for bit,rs,tg in ((1,7,6),(2,0,2)) if w>0 else ((4,119,118),(8,112,114)):
     if c&bit and b[rs]==4*w:
      lo,hi=(f,rs) if f<rs else (rs,f)
      if not any(b[lo+1:hi]) and not any(atk(b,s,-w) for s in (f,(f+tg)//2,tg)):ms.append((f,tg,0))
  else:
   for o in (D if a==3 else R if a==4 else D+R):
    t=f+o
    while not t&0x88:
     v=b[t]
     if v*w<0 or not v and not cap:ms.append((f,t,0))
     if v:break
     t+=o
 k=b.index(6*w)
 return [m for m in ms if abs(b[m[1]])!=6 and not atk(make(b,c,e,m,w)[0],m[1] if abs(b[m[0]])==6 else k,-w)]
def make(b,c,e,m,w):
 f,t,p=m
 n=b[:]
 v=n[f];n[f]=0
 if abs(v)==1 and t==e and not n[t]:n[t-16*w]=0
 n[t]=p*w if p else v
 if abs(v)==6 and abs(t-f)==2:
  if t>f:n[t-1]=n[t+1];n[t+1]=0
  else:n[t+1]=n[t-2];n[t-2]=0
 return n,-w,c&CK[f]&CK[t],f+16*w if abs(v)==1 and abs(t-f)==32 else -1
def ev(b,w):
 s=0
 for i in SQ:
  p=b[i]
  if not p:continue
  a=abs(p)
  f=i&7;r=i//16^7*(p<0)
  k=r*4+min(f,7-f)
  x=T[0][k] if a==1 else T[1][k] if a==6 else 7-abs(f-3.5)-abs(r-3.5)
  s+=((0,100,320,330,500,900,0)[a]+x)*p//a
 return s*w
def sr(b,w,c,e,d,al,be,pl):
 nd[0]+=1
 if nd[0]>80000:raise EOFError
 if d<=0:
  s=ev(b,w)
  if s>=be:return be
  if s>al:al=s
  if pl>90:return al
 tm=0
 if d>0:h=(tuple(b),w,c,e);tm=TT.get(h,0)
 k=b.index(6*w)
 chk=atk(b,k,-w)
 # Null-move pruning (v9): lewati giliran; kalau lawan tetap tidak bisa
 # menembus beta di kedalaman kurang, pangkas. Hanya bila eval statis
 # sudah >= beta (menghindari zugzwang + menghemat node).
 if d>=3 and not chk and ev(b,w)>=be:
  s=-sr(b,-w,c,-1,d-3,-be,-be+1,pl+1)
  if s>=be:return be
 ms=gen(b,w,c,e,d<=0 and not chk)
 if not ms:return -M+pl if chk else (al if d<=0 else 0)
 ms.sort(key=lambda m:(m==tm,m==KL.get(pl),abs(b[m[1]])),reverse=True)
 bs=al if d<=0 else -M
 bm=0
 for m in ms:
  s=-sr(*make(b,c,e,m,w),d-1,-be,-al,pl+1)
  if s>bs:bs=s;bm=m
  al=max(al,s)
  if al>=be:
   if not b[m[1]]:KL[pl]=m
   break
 if d>0:TT[h]=bm
 return bs
def best(b,w,c,e,lg):
 ms=[m for m in gen(b,w,c,e,0)if uci(m) in lg]
 if len(ms)<=1:return (ms[0] if ms else None),0
 bm=ms[0];bs=-M;d=1
 while 1:
  try:
   bs,bm=max((-sr(*make(b,c,e,m,w),d-1,-M,M,1),m) for m in ms);d+=1
   if abs(bs)>M-1000:break
  except EOFError:break
 return bm,bs
def post(p,y):
 r=u.Request(U+p,data=json.dumps(y).encode())
 try:
  with u.urlopen(r) as s:return json.load(s)
 except Exception:sys.exit(1)
g=post("/game",{})
while g["status"]!="done":
 if g["status"]=="over":g=post("/game",{});continue
 b,w,c,e=parse(g["fen"]);nd[0]=0;TT.clear()
 L=g["legal_moves"]
 m,s=best(b,w,c,e,L)
 z=uci(m) if m else L[0]
 g=post("/resign" if s<=-M+200 else "/move",{"game":g["game"],"move":z})
