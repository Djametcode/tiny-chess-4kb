import json,os
from urllib.request import urlopen as U,Request as Q
E=os.environ["MAKEFUN_ENV_URL"]
V=0,100,320,330,500,900,0
NN=33,31,18,14,-33,-31,-18,-14
KG=1,17,16,15,-1,-17,-16,-15
BD=17,15,-17,-15
RD=16,1,-16,-1
SQ=[i for i in range(128)if not i&136]
FL="abcdefgh"
MA=30000
def p(f):
	a=f.split();b=[0]*128;r=7;q=0
	for x in a[0]:
		if x=="/":r-=1;q=0
		elif x.isdigit():q+=int(x)
		else:
			c="pnbrqk".index(x.lower())+1;b[r*16+q]=c if x.isupper()else-c;q+=1
	w=1 if a[1]=="w"else-1;c=0
	for x,v in(("K",1),("Q",2),("k",4),("q",8)):
		if x in a[2]:c|=v
	e=-1
	if a[3]!="-":e=(int(a[3][1])-1)*16+FL.index(a[3][0])
	return b,w,e,c
def A(b,s,y):
	for o in-15,-17:
		u=s+o*y
		if not u&136 and b[u]==y:return 1
	for o in NN:
		u=s+o
		if not u&136 and b[u]==2*y:return 1
	for o in KG:
		u=s+o
		if not u&136 and b[u]==6*y:return 1
	for ds,c1,c2 in((BD,3,5),(RD,4,5)):
		for o in ds:
			u=s
			while 1:
				u+=o
				if u&136:break
				x=b[u]
				if x:
					if x==c1*y or x==c2*y:return 1
					break
	return 0
def G(b,w,e,c):
	m=[]
	for s in SQ:
		x=b[s]
		if not x or(x>0)!=(w>0):continue
		a=abs(x);o=x>0
		if a==1:
			d=16 if o else-16;t=s+d
			if not t&136 and not b[t]:
				if t>>4 in(0,7):
					for z in 5,4,3,2:m.append((s,t,z))
				else:
					m.append((s,t,0));u=s+2*d
					if s>>4==(1 if o else 6)and not b[u]:m.append((s,u,0))
			for y in d-1,d+1:
				t=s+y
				if t&136:continue
				z=b[t]
				if z and(z>0)!=o:
					if t>>4 in(0,7):
						for v in 5,4,3,2:m.append((s,t,v))
					else:m.append((s,t,0))
				elif t==e:m.append((s,t,0))
		elif a<3 or a==6:
			for y in(NN if a==2 else KG):
				t=s+y
				if not t&136 and(not b[t]or(b[t]>0)!=o):m.append((s,t,0))
			if a==6:
				if o and s==4:kc,qc,p1,p2=1,2,7,0
				elif not o and s==116:kc,qc,p1,p2=4,8,119,112
				else:kc=0
				if kc:
					if c&kc and b[p1]==4*w and not b[5|p2]and not b[6|p2]and A(b,s,-w)+A(b,s+1,-w)+A(b,s+2,-w)<1:m.append((s,s+2,0))
					if c&qc and b[p2]==4*w and not b[3|p2]and not b[2|p2]and not b[1|p2]and A(b,s,-w)+A(b,s-1,-w)+A(b,s-2,-w)<1:m.append((s,s-2,0))
		else:
			for y in((BD if a==3 else RD)if a<5 else BD+RD):
				t=s
				while 1:
					t+=y
					if t&136:break
					z=b[t]
					if not z:m.append((s,t,0))
					else:
						if(z>0)!=o:m.append((s,t,0))
						break
	return m
def K(b,w,e,c,m):
	s,t,z=m;n=b[:];x=n[s];y=n[t]
	n[t]=z*w if z else x
	n[s]=0;a=abs(x)
	if a==1 and(s&7)!=(t&7)and not y:n[t-16*w]=0
	if a==6:
		if abs(t-s)==2:
			if t&7>3:n[t+1]=0;n[t-1]=4*w
			else:n[t-2]=0;n[t+1]=4*w
		c&=12 if w>0 else 3
	if s==0 or t==0:c&=13
	if s==7 or t==7:c&=14
	if s==112 or t==112:c&=7
	if s==119 or t==119:c&=11
	e2=-1
	if a==1 and abs(t-s)==32:e2=(s+t)//2
	return n,e2,c
T=[[0]*128 for i in range(13)]
for a in range(1,7):
	for s in SQ:T[a][s]=V[a];T[-a][s]=-V[a]
def W(b,w):
	t=0
	for s in SQ:
		x=b[s]
		if x:t+=T[x][s]
	return t*w
def SR(b,w,e,c,d,al,be):
	if d<1:return W(b,w)
	k=b.index(6*w);bs=-MA-1;ok=0
	for m in G(b,w,e,c):
		nb,e2,c2=K(b,w,e,c,m)
		if A(nb,m[1]if abs(b[m[0]])==6 else k,-w):continue
		ok=1
		s2=-SR(nb,-w,e2,c2,d-1,-be,-al)
		if s2>bs:
			bs=s2
			if s2>al:
				al=s2
				if al>=be:break
	if not ok:return-MA if A(b,k,-w)else 0
	return bs
def B(f):
	b,w,e,c=p(f);al=-MA;cu=None;k=b.index(6*w)
	for m in G(b,w,e,c):
		nb,e2,c2=K(b,w,e,c,m)
		if A(nb,m[1]if abs(b[m[0]])==6 else k,-w):continue
		s2=-SR(nb,-w,e2,c2,1,-MA,-al)
		if s2>al:al=s2;cu=m
	s,t,z=cu
	return FL[s&7]+str((s>>4)+1)+FL[t&7]+str((t>>4)+1)+("pnbrq"[z-1]if z else"")
def H(t,d):return json.load(U(Q(E+t,json.dumps(d).encode(),{"Content-Type":"application/json"})))
while 1:
	r=H("/game",{})
	if r["status"]=="done":break
	while r["status"]=="your_move":r=H("/move",{"game":r["game"],"move":B(r["fen"])})
