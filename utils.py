from random import sample,uniform
from pymongo import MongoClient
from start import useful
from math import ceil,floor
from time import sleep
from pywinauto.application import Application
from pywinauto.findwindows import find_window
wait,collection,app=lambda x,y:sleep(uniform(x,y)),MongoClient('mongodb://localhost:27017/').admin,Application().connect(handle=find_window(title_re='Unfriendly')).top_window()
app.move_window(x=-10, y=0, width=1365, height=768, repaint=True)
# app.minimize()


def shortest(heap,target,c=True):
	m,ret,i,index,decal=10000,[],0,[],0
	for x in heap:
		if x[0][-1]['_id']==target['_id'] if c else x[0][-1]==target:
			return None,None,([x[0]] if c else x[0])
		if x[1]==m:
			ret.append(x)
			index.append(i)
		elif x[1]<m:
			m,ret,index=x[1],[x],[i]
		i+=1
	for j in index:
		del heap[j-decal]
		decal+=1
	return ret,heap,None 

def pathfinder(start,target,shuffle=True,multipath=False):
	print("find path from ",start,target)
	f,g,get=lambda s,t:4*(abs(t[0]-s[0] if t[0]>0 and s[0]>0 or t[0]<0 and s[0]<0 else abs(t[0])+abs(s[0]))+abs(t[1]-s[1] if t[1]>0 and s[1]>0 or t[1]<0 and s[1]<0 else abs(t[1])+abs(s[1]))),lambda x:sample(('n','s','w','e','d'),5) if x else ('n','s','w','e','d'),lambda x:collection.nodes.find_one({'_id':x},{'coord':1,'n':1,'s':1,'w':1,'e':1,'d':1})
	start,target=get(start),get(target)
	heap,done,wait=[[[start,],f(start['coord'],target['coord'])]],set(),[]
	while heap:
		nodes,heap,path=shortest(heap,target)
		if path:
			if multipath:
				for k in wait:
					length=len(k)-1
					for p in range(len(path)):
						if k[-1]==path[p][length]['_id']:
							path.append(k[:-1]+path[p][length:])
			ret=[]
			for p in path:
				ret.append([[d[1],y,p[n]['_id']] for n in range(len(p)-1) for y in g(False) for d in p[n][y].items() if d[0]==p[n+1]['_id']])
			return ret if multipath else ret[0]
		for node in nodes:
			for d in g(shuffle):
				for k in node[0][-1][d]:
					if node[0][-2 if node[0][-1]['_id']!=start['_id'] else -1]['_id']!=k:
						if k in done:
							wait.insert(0,node[0]+[k])
						else:
							done.add(k)
							heap.insert(0,[node[0]+[neighbor:=get(k)],f(neighbor['coord'],target['coord'])])
	return []

def click(cellid,offx=0,offy=0,alt=0,direction=None):
	limit,x,y,line,row={'s':lambda x,odd:(x[0],x[1]+7) if odd else (x[0],x[1]+20) ,'n':lambda x,odd:(x[0],x[1]-20) if odd else (x[0],x[1]-7),'w':lambda x,odd:(x[0]-45,x[1]) if odd else (x[0]-18,x[1]),'e':lambda x,odd:(x[0]+18,x[1]) if odd else (x[0]+45,x[1]),'d': lambda x,odd:(x[0],x[1])},257,16,cellid//14,cellid % 14
	if odd:=line%2:
		x+=30
	if direction:
		x,y=limit[direction]((x,y),odd)
	print("click",cellid,offx,offy,alt,(x+floor(row*61.8)+ceil(offx*2/3), y+floor(15.6*line)+offy-8*alt+38),direction)
	app.click(coords=(x+floor(row*61.8)+ceil(offx*2/3), y+floor(15.6*line)+offy-8*alt))
	sleep(0.25)

def switch_coord(c):
	i=0
	while c%14 and c < 546:
		c,i=c+(14 if c//14%2 else 13),i+1 
	if c > 545:
		return c%14+20,c%14+i
	if c//14%2:
		return (c+14)//28,19-(c+14)//28+i+1
	return c//28,19-c//28+i

def revert_coord(x,y):
	x=x*28 if x<20 else 546+x%20
	for c in range(y-(19-x//28 if x<546 else x%14)):
		x-= 13 if x//14%2 else 14
	return x

def insight(x0,y0,x1,y1,mat):
	dx,dy = abs(x1 - x0),abs(y1 - y0)
	x_inc,y_inc = 1 if x1 > x0 else -1,1 if y1 > y0 else -1
	error,n,x,y,dx,dy = dx-dy,dx+dy,x0,y0,dx*2,dy*2
	while n > 0 :
		if not mat[revert_coord(x,y)]:
			return False
		elif error > 0:
			x += x_inc
			error -= dy
		elif error < 0:
			y += y_inc
			error += dx
		else:
			x += x_inc
			y += y_inc
			error = dx - dy
			n -= 1
		n -= 1
	return True

def get_current_node(cond=0,mapid=None,pos=None):
	projec,(pos,mapid)={'walkable':1},(pos,mapid)if pos else (useful['mypos'],useful['mapid'])
	if not cond:
		projec['fightcells']=1
	elif cond==2:
		projec['interactives']=1
	elif cond==3:
		projec['d']=1
	for n in collection.nodes.find({'mapid':mapid},projec):
		if not cond or pos in n['walkable']:
			return n['_id'] if cond==1 else {'interactives':n['interactives'],'walkable':n['walkable']} if cond==2 else (n['_id'],n['d']) if cond==3 else n['fightcells']

def get_path(x0,y0,x1,y1,mat,revert=True):
	f,done=lambda x0,y0:abs(x0-x1)+abs(y0-y1),{revert_coord(x0,y0)}
	heap=[[[(x0,y0)],f(x0,y0)]]
	while heap:
		best,heap,path=shortest(heap,(x1,y1),False)
		if path:
			return [revert_coord(c[0],c[1]) for c in path] if revert else len(path)
		temp=set()
		for i in best:
			for j in ((0, 1), (0, -1), (-1, 0), (1, 0)):
				d = (i[0][-1][0] + j[0], i[0][-1][1] + j[1])
				if (cellid:=revert_coord(d[0],d[1]))>-1 and cellid<560  and mat[cellid] == 2 and d not in i[0] and cellid not in temp and cellid not in done:
					heap.append([i[0]+[d],f(d[0],d[1])])
					temp.add(cellid)
			done.add(revert_coord(i[0][-1][0],i[0][-1][1]))
	return [] if revert else 599

def check_spells(spells,buffs,mat):
	enter,g=True,lambda:useful['fight']['enemyteamMembers'][[*useful['fight']['enemyteamMembers']][0]]['cellid']
	while useful['infight'] and useful['fight']['ap']>2 and enter:
		(x0,y0),(x1,y1)=switch_coord(p:=useful['mypos']),switch_coord(g())
		for k,v in spells.items():
			if v['range'][1] + (useful['fight']['range'] if v['range'][2] else 0) >= (calc:=abs(x0-x1)+abs(y0-y1)) and calc >=v['range'][0] and not v['fc'] and (not v['inline'] or y0==y1 or x0==x1) and (not v['sight'] or insight(x0,y0,x1,y1,mat)):
				c=v['cpt']
				while c and useful['infight'] and v['ap']<=useful['fight']['ap']:
					app.send_keystrokes(k)
					wait(1,1.5)
					click(g())
					v['fc'],c=v['recast'],c-1
					wait(1.5,3)
		if useful['infight'] and useful['fight']['ap']>2:
			if useful['fight']['mp']:
				if (path:=get_path(x0,y0,x1,y1,mat)[1:-1]):
					while p==useful['mypos']:
						click(path[min(useful['fight']['mp'],len(path))-1])
						wait(2,3)
				useful['fight']['mp']=0
			else:
				for k,v in buffs.items():
					if not v['fc'] and v['ap']<=useful['fight']['ap']:
						app.send_keystrokes('{VK_CONTROL DOWN}')
						app.send_keystrokes(k)
						app.send_keystrokes('{VK_CONTROL}')
						wait(1,1.5)
						click(useful['mypos'])
						wait(1.5,2)
						v['fc']=v['recast']
						if k=='1':
							break
				else:
					enter=False
	for xx in (spells,buffs):
		for x in xx.values():
			if x['fc']:
				x['fc']-=1
	wait(1.5,2)
	return spells,buffs

def fight(first_fight=False):
	app.send_keystrokes('{VK_SHIFT}')
	if first_fight:
		click(557,offy=20,offx=15)
		wait(.5,.75)
		click(557,offy=90)
		wait(.5,.75)
		click(557,offy=90,offx=15)
	wait(1.5,2)
	m,mat=600,get_current_node()
	for c in useful['fight']['positionsForDefenders'] if useful['fight']['defenderId'] == useful['contextualId'] else useful['fight']['positionsForChallengers']:
		(x0,y0),(x1,y1)=switch_coord(useful['fight']['enemyteamMembers'][-1]['cellid']),switch_coord(c)
		if (calc:=abs(x0-x1)+abs(y0-y1))<m:
			index,m=c,calc
	click(index)
	wait(.5,.75)
	spells,buffs = {'1': {'range': (6, 10, True),'ap':4 ,'cpt' : 1 ,'recast': 3, 'fc': 0, 'sight': True,'inline': False}, '2': {'range': (1, 8, True),'ap':4, 'cpt' : 1 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': True}, '3': {'range': (5, 10, True),'ap':3, 'cpt' : 1 , 'recast': 3, 'fc': 1, 'sight': True, 'inline': False}, '4': {'range': (1, 10, True),'ap':2, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': False}, '5': {'range': (1, 12, True),'ap':3, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': False}, '6': {'range': (1, 7, True),'ap':3, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': False, 'inline': False}},{'1' : {'ap':3, 'recast':5,'fc':0},'2' : {'ap':3, 'recast':6,'fc':0},'3' : {'ap':2, 'recast':5,'fc':0}}
	while useful['infight']:
		click(557,offy=45)
		while not useful['fight']['turn']:
			wait(1.5,3)
		spells,buffs=check_spells(spells,buffs,mat)
	prev=useful['mypos']
	wait(2.5,4)
	app.send_keystrokes('{ENTER}')
	return prev
