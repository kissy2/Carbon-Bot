from random import sample,uniform
from pymongo import MongoClient
from start import useful
from math import ceil,floor
from time import sleep
from subprocess import Popen,DEVNULL,PIPE
from pywinauto.application import Application
from pywinauto.findwindows import find_elements
from winsound import PlaySound,SND_LOOP,SND_ASYNC,SND_FILENAME,SND_ALIAS
from start import sniff,Raw,on_receive,on_msg,useful
from threading import Thread,Event
import argparse,logging
global thread,prevd
# import utils2
(arg:=argparse.ArgumentParser()).add_argument("-name", "--name", required=True, help="ENTER YOUR CHARACTER NAME")
arg.add_argument("-server", "--server", required=True, help="ENTER YOUR SERVER NAME")
arg.add_argument("-port", "--port", required=True, help="ENTER DOFUS CLIENT PORT NUMBER")
arg.add_argument("-paths", "--path", required=True, help="ENTER NAMES OF PATHS")
arg.add_argument("-resources", "--resource", required=False, help="ENTER NAMES OF RESOURCES TO COLLECT (NOT REQUIRED)")
arg.add_argument("-priority", "--priority", required=False, help="ENTER RESOURCES HARVEST ORDER (NOT REQUIRED)")
arg,wait,e,prevd,accounts=vars(arg.parse_args()),lambda x,y:sleep(uniform(x,y)),Event(),None,{'furye':'','ilyzael':'1','jahash':'9','brumen':'3','meriana':'5','echo':'4','agride':'8'}
thread,connect,get_window,sniffer,collection=None,lambda hwnd:Application().connect(handle=hwnd.handle).top_window(),lambda text:find_elements(title_re=f'^{text}'),lambda :Thread(target=sniff, kwargs={'stop_filter':lambda p: e.is_set(),'filter':f'ip host {collection.servers.find_one({"_id":arg["server"]},{"_id":0})["ip"]} and tcp port {arg["port"]}', 'lfilter':lambda p: p.haslayer(Raw),'prn':lambda p: on_receive(p, on_msg)}),MongoClient('mongodb://localhost:27017/').admin
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename=f'log-{arg["server"]}.txt', level=logging.DEBUG)

def click(cellid,offx=0,offy=0,alt=0,direction=None):
	global prevd
	try:
		limit,x,y,line,row={'s':lambda x,odd:(x[0],x[1]+11) if odd else (x[0],x[1]+24) ,'n':lambda x,odd:(x[0],x[1]-21) if odd else (x[0],x[1]-8),'w':lambda x,odd:(x[0]-45,x[1]) if odd else (x[0]-18,x[1]),'e':lambda x,odd:(x[0]+18,x[1]) if odd else (x[0]+45,x[1])},251,15,cellid//14,cellid % 14
		if odd:=line%2:
			x+=31
		if prevd=='d':
			prevd=None
			app.send_keystrokes('{VK_SHIFT DOWN}')
			sleep(.1)
			click(useful['mypos'])
			sleep(.1)
			click(0,-1000)
			sleep(.1)
		if direction not in (None,'d'):
			if useful['mapid']==95420418:
				alt=12
			x,y=limit[direction]((x,y),odd)
		prevd=direction
		logging.info(f'Click : {cellid} , {offx} ,{offy}, {alt}, {direction}, {(x+ceil(row*62.4)+floor(offx*.687), y+floor(15.5*line)+ceil(offy*.6)-8*alt+38)}')
		app.click(coords=(x+ceil(row*62.4)+floor(offx*.687), y+floor(15.5*line)+ceil(offy*.6)-8*alt))
	except RuntimeError:
		logging.error(f'RuntimeError in Click',exc_info=1)
		sleep(5)
		click(cellid,offx,offy,alt,direction)
	except:
		print('Error in click')
		logging.error(f'Error in click cellid : {cellid} , offx : {offx} , offy : {offy} , altitude : {alt} , direction : {direction}',exc_info=1)
def check_connection():
	global thread
	try:
		if window.name and window.name[0:5]=='Dofus':
			while window.name and window.name[0:5]=='Dofus':
				logging.critical('Disconnected : Trying to reconnect every 5 minutes')
				if thread:
					sleep(240)
					app.send_keystrokes('~')
				sleep(2)
				click(202,40)
				sleep(2)
				app.send_keystrokes('^{a}{BACKSPACE}')
				sleep(2)
				app.send_keystrokes('thepurgeanarchy'+accounts[arg["server"]])
				sleep(2)
				click(230,40,13)
				sleep(2)
				app.send_keystrokes('^{a}{BACKSPACE}')
				sleep(2)
				app.send_keystrokes('vikings4life~')
				sleep(52)
				app.send_keystrokes('~~~')
			if thread:
				e.set()
				thread.join()
				e.clear()
			thread=sniffer()
			thread.start()
			logging.info('Connected Successfully')
			return True
		elif not thread:
			thread=sniffer()
			thread.start()
			app.send_keystrokes('~~~')
	except:
		print('Error in check_connection')
		logging.error('Error in check_connection')


def check_admin():
	if useful['threat']:
		app.set_focus()
		if useful['threat']=='high':
			PlaySound(f'./assets/threat_{useful["threat"]}', SND_LOOP+SND_ASYNC)
			input("MODERATOR NOTIFICATION RESPOND QUICKLY!!!!")
			PlaySound(None,0)
		elif useful['threat']=='medium':
			for j in range(10):
				PlaySound(f'./assets/threat_{useful["threat"]}', SND_FILENAME)
		elif useful['threat']=='low':
			while useful['dialog']:
				app.send_keystrokes('{VK_ESCAPE}')
				sleep(.5)
			for j in range(5):
				PlaySound("SystemHand", SND_ALIAS)
		app.minimize()
		useful['threat']=None

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
	logging.info(f'Finding a path from {start} to {target}')
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
				sp=[]
				for n in range(len(p)-1):
					for y,d in ((y,d) for y in g(False) for d in p[n][y].items()):
						if d[0]==p[n+1]['_id']:
							sp.append([d[1],y,p[n]['_id']])
							break
				ret.append(sp)
			logging.info(f'Path directions : {[x[1] for x in ret[0]]}')
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
	try:
		projec={'walkable':1}
		if pos is None:
			pos,mapid=useful['mypos'],useful['mapid']
		if not cond:
			projec['fightcells']=1
		elif cond==2:
			projec['interactives']=1
		elif cond==3:
			projec['d']=1
		for n in collection.nodes.find({'mapid':mapid},projec):
			if not cond or pos in n['walkable']:
				break
		return n['_id'] if cond==1 else {'interactives':n['interactives'],'walkable':n['walkable']} if cond==2 else (n['_id'],n['d']) if cond==3 else n['fightcells']
	except:
		print('Error in get_current_node')
		logging.error(f'Error in get_current_node cond : {cond} mapid : {mapid} pos: :{pos}')

def get_path(x0,y0,x1,y1,mat,revert=True):
	try:
		f,done,offset=lambda x0,y0:abs(x0-x1)+abs(y0-y1),{revert_coord(x0,y0)},((0, 1), (0, -1), (-1, 0), (1, 0))
		heap=[[[(x0,y0)],f(x0,y0)]]
		while heap:
			best,heap,path=shortest(heap,(x1,y1),False)
			if path:
				return [revert_coord(c[0],c[1]) for c in path] if revert else len(path)
			temp=set()
			for i in best:
				c=(i[0][-1][0],i[0][-1][1])
				reverted=revert_coord(c[0],c[1])
				for j in range(4):
					if not (ooe:=reverted//14%2) and not reverted%14 and j in (1,2) or ooe and reverted%14==13 and j in (0,3) or reverted//14==39 and j in (1,3):
						continue
					d = (i[0][-1][0] + offset[j][0], i[0][-1][1] + offset[j][1])
					if (cellid:=revert_coord(d[0],d[1]))>-1 and cellid<560  and mat[cellid] == 2 and d not in i[0] and c not in temp and c not in done:
						heap.append([i[0]+[d],f(d[0],d[1])])
						temp.add(cellid)
				done.add(c)
		return [] if revert else 599
	except:
		print('Error in get_path')
		logging.error(f'Error in get_path x0:{x0}, y0:{y0}, x1:{x1}, y1:{y1}, revert:{revert}\nmat : {mat}',exc_info=1)

def get_closest(x0,y0,heap,mat,area,hm=None):
	try:
		to_add,start=(13,14,-13,-14),0
		temp=[[x,(t:=switch_coord(y['cellid']))[0],t[1]] for x,y in useful['fight']['enemyteamMembers'].items()]
		temp.sort(key=lambda x:abs(x0-x[1])+abs(y0-x[2]))
		for _ in range(area):
			for cell in heap[start:]:
				for i in range(4):
					if not((ooe:=cell//14%2) and cell%14==13 and i in (1,2) or not ooe and not cell%14 and i in (0,3)) and (next_cell:=(to_add[i]+1 if ooe and i<2 else to_add[i] -1 if not ooe and i>1 else to_add[i])+cell)<560 and next_cell>-1 and mat[next_cell]==2 and next_cell not in heap:
						heap.append(next_cell)
				start+=1
		heap=[(switch_coord(x),x) for x in heap]
		return [[x,[(y[-1] if insight(y[0][0],y[0][1],x[1],x[2],mat) else y[-1]*-1,y[0][0],y[0][1]) for y in heap]] for x in temp[:hm]]
	except:
		print('Error in get_closest (fight)')
		logging.error(f'Error in get_closest x0 : {x0} , y0 : {y0}\nuseful : {useful}',exc_info=1)

def move(p,c):
	if useful['fight']['mp'] and p!=c: 
		counter=5
		while counter and p==useful['mypos']:
			click(c)
			click(c)
			wait(1,2)
			counter-=1
	return useful['mypos']

def check_spells(spells,buffs,mat,treasure):
	try:
		# logging.info(f'New turn {useful["fight"]["round"]} :  called check_spells ap : {useful["fight"]["ap"]} mp : {useful["fight"]["mp"]} health : {useful["lifepoints"]} enemies : { useful["fight"]["enemyteamMembers"]}')
		enter,used=True,[]
		app.send_keystrokes('~')
		while useful['infight'] and useful['fight']['ap']>2 and enter:
			logging.info(f'enter while {useful["fight"]["ap"]}')
			(x0,y0)=switch_coord(p:=useful['mypos'])
			if treasure and useful['lifepoints']/useful['maxLifePoints']<.2:
				print('out no hit')
				break
			for y,x,k,v in ((y,x,k,v) for y in get_closest(x0,y0,[p],mat,useful['fight']['mp']) for k,v in spells.items() for x in y[1]):
				if useful['infight'] and useful['fight']['ap']>2:
					if y[0][0] in useful['fight']['enemyteamMembers'] and v['range'][1] + (useful['fight']['range'] if v['range'][2] else 0) >= (calc:=abs(x[1]-y[0][1])+abs(x[2]-y[0][2])) and calc >=v['range'][0] and not v['fc'] and (not v['inline'] or x[1]==y[0][1] or x[2]==y[0][2]) and (not v['sight'] or x[0]>-1):
						move(p,t:=abs(x[0]))
						if useful['mypos']!=t:
							break
						c,counter=v['cpt'],2
						while useful['infight'] and y[0][0] in useful['fight']['enemyteamMembers'] and k not in used and v['ap']<=useful['fight']['ap']:
							app.send_keystrokes(k)
							wait(.5,1)
							v['fc'],ap=v['recast'],useful['fight']['ap']
							click(useful['fight']['enemyteamMembers'][y[0][0]]['cellid'],offy=-4)
							wait(1,1.5)
							if ap != useful['fight']['ap']: 
								if not (c:=c-1):
									used.append(k)
							else:
								 if not (counter:=counter-1):
								 	break
				else:
					break
			if useful['infight'] and useful['fight']['mp']:
				logging.info(f"mp {useful['fight']['mp']} \n{get_closest(x0,y0,[p],mat,useful['fight']['mp'],50)}")
				m=600
				for y,x,v in ((y,x,v) for y in get_closest(x0,y0,[p],mat,50,1) for x in y[1] for v in spells.values()) :
					calc=abs(x[1]-y[0][1])+abs(x[2]-y[0][2])
					if mat[abs(x[0])]==2 and x[0]>-1 and v['range'][1] + (useful['fight']['range'] if v['range'][2] else 0)>=calc and (not v['inline'] or x[1]==y[0][1] or x[2]==y[0][2]) and x[0]!=useful['fight']['enemyteamMembers'][y[0][0]]['cellid'] and calc<m:
						m,x1,y1=calc,x[1],x[2]
						move(p,(t:=get_path(x0,y0,x1,y1,mat))[(tm:=min(useful['fight']['mp'],(length:=len(t)-1)))])
						if length>useful['fight']['mp'] and not buffs['1']['fc'] and buffs['1']['ap']<=useful['fight']['ap']:
							# print('in',t,useful['mypos'],useful['fight'])
							app.send_keystrokes('{VK_CONTROL DOWN}')
							app.send_keystrokes('1')
							app.send_keystrokes('{VK_CONTROL}')
							wait(.5,1.5)
							t=t[tm:]
							print(t)
							click(t[min(6 if useful['my_level']>132 else 5,len(t)-1)],offy=-4)
							wait(.5,1.5)
							buffs['1']['fc']=buffs['1']['recast']
						break
				useful['fight']['mp']=0
			elif useful['infight'] and useful['fight']['ap']>1:
				for k,v in buffs.items():
					if k!='1' and not v['fc'] and not v['cpt'] and v['ap']<=useful['fight']['ap']:
						app.send_keystrokes('{VK_CONTROL DOWN}')
						app.send_keystrokes(k)
						app.send_keystrokes('{VK_CONTROL}')
						wait(.5,1.5)
						click(useful['mypos'],offy=-4)
						wait(.5,1.5)
						v['fc'],v['cpt']=v['recast'],v['cpt']-1
				enter=False
		for xx in (spells,buffs):
			for x in xx.values():
				if x['fc']:
					x['fc']-=1
		wait(1.5,2)
		return spells,buffs
	except:
		print('Error in check_spells')
		logging.error(f'Error in check_spells\nuseful : {useful}\nspells : {spells}\nbuffs : {buffs}\nmat : {mat}',exc_info=1)

def fight(treasure=False):
	try:
		logging.info(f'Enter fight\nuseful : {useful}')
		app.send_message(257,16)
		try:
			if not useful['fight']['lock']:
				click(557,offy=20,offx=15)
				wait(.25,.75)
			if not useful['fight']['spectator']:
				app.send_keystrokes('^{ }')
				wait(.75,1)
				app.send_keystrokes('^{a}{BACKSPACE}')
				wait(1,1.5)
				app.send_keystrokes('/s~')
				click(0,-1000)
				app.send_keystrokes('{VK_NUMPAD8}')
				wait(.75,1)
		except:
			logging.error('lock spec error')
		wait(1.5,2)
		mat,prev,mapid=get_current_node(),useful['mypos'],useful['mapid']
		logging.info(f'Fight mat {mat}')
		try:
			m=600
			for c in useful['fight']['positionsForDefenders'] if useful['fight']['defenderId'] == useful['contextualId'] else useful['fight']['positionsForChallengers']:
				(x0,y0),(x1,y1)=switch_coord(useful['fight']['enemyteamMembers'][-1]['cellid']),switch_coord(c)
				if (calc:=abs(x0-x1)+abs(y0-y1))<m:
					index,m=c,calc
			if prev!= index:
				click(index)
				wait(.5,.75)
		except:
			logging.critical('too late for positioning',exc_info=1)
		spells,buffs= (#spells
						{'1': {'range': (6, 8, True),'ap':4 ,'cpt' : 2 ,'recast': 0, 'fc': 0, 'sight': True,'inline': False},
						 '2': {'range': (1, 8, False),'ap':3, 'cpt' : 1 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': True},
			 			 '3': {'range': (1, 12, True),'ap':3 ,'cpt' : 2 ,'recast': 0, 'fc': 0, 'sight': True,'inline': False},
						 '4': {'range': (1, 7, True),'ap':3 ,'cpt' : 2 ,'recast': 0, 'fc': 0, 'sight': False,'inline': False}
						 },
					  # {'1': {'range': (6, 10, True),'ap':4 ,'cpt' : 1 ,'recast': 3, 'fc': 0, 'sight': True,'inline': False},
					  #  '2': {'range': (1, 8, True),'ap':4, 'cpt' : 1 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': True}, 
					  #  '3': {'range': (2, 6, True),'ap':4, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': False}, 
					  #  '4': {'range': (5, 10, True),'ap':3, 'cpt' : 1 , 'recast': 3, 'fc': 1, 'sight': True, 'inline': False}, 
					  #  '5': {'range': (1, 12, True),'ap':3, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': False}},
					   #buffs
					   {'1' : {'ap':3, 'recast':5,'fc':0},
						'2' : {'ap':3, 'recast':6,'fc':0},
						'3' : {'ap':2, 'recast':5,'fc':0}}) if arg['name']=='Unfriendly' else(
						#spells
						{'1': {'range': (1, 3, False),'ap':3, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': False},
						 '2': {'range': (1, 5, False),'ap':4, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': True}},
						#buffs/debuffs
						{'1' : {'ap':5, 'recast':2,'fc':0,'cpt':1},
						 '2' : {'ap':3, 'recast':0,'fc':0,'cpt':2},
						})
		while useful['infight']:
			app.send_keystrokes('{F1}')
			while not wait(1.5,3) and 'turn' in useful['fight'].keys() and not useful['fight']['turn']:
				check_connection()
				check_admin()
				logging.info('Waiting for turn')
			spells,buffs=check_spells(spells,buffs,mat,treasure)
		prev=useful['mypos']
		wait(2,3)
		for _ in range(3):
			click(0,-1000)
			app.send_keystrokes('~')
		return prev
	except:
		print('Error in fight')
		logging.error(f'Error in fight\nuseful : {useful}',exc_info=1)

while Popen(args='REG QUERY HKCU\Environment /v eca',stdout=PIPE,stderr=DEVNULL).communicate()[0][:-1][-2]=='1':
	wait(1,2)
Popen('setx eca 1',stdout=DEVNULL)
if not (window:=get_window(arg['name'])):
	while not (window:=get_window('Ankama Launcher$')):
		Popen('call Launcher.lnk',stdout=DEVNULL,shell=True)
		sleep(30)
	app=connect(window[0])
	app.set_focus()
	while not (window:=get_window('Dofus 2')) and not (window:=get_window(arg['name'])):
		click(642,300)
		sleep(45)
	app.minimize()
window=window[0]
app=connect(window)
app.move_window(x=-10, y=0, width=1365, height=768, repaint=True)
# app.minimize()
check_connection()
Popen('setx eca 0',stdout=DEVNULL)