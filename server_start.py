def launch_in_process(conn,client,name,server,parameters,fix_list,lock):
	from zlib import decompress	
	from data import Data
	from server_protocol import read, msg_from_id, types, write, logging,useful
	from random import sample,uniform,randint
	from pymongo import MongoClient
	from math import ceil,floor
	from time import sleep,strftime
	from threading import Thread
	global collection,wait,func,prevd,waitp,buf,connected,archmonsters
	#'mongodb+srv://carbon:bot@carbon-9bthr.gcp.mongodb.net/test?retryWrites=true&w=majority').carbon_db
	collection,wait,useful['name'],connected=MongoClient('localhost:27017').admin, lambda x,y:sleep(uniform(x,y)),name,True
	func,prevd,waitp,archmonsters=lambda x:collection.nodes.find_one({'mapid':x}, {'coord'}),None,b'',{x['raceid']:x['_id'] for x in collection.archmonsters.find({})}
	logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename=f'logs/log-{name} - {server}.txt', level=logging.DEBUG)
	logging.raiseExceptions = False
	try:
		conn.sendto(collection.servers.find_one({'_id':server})['ip'].encode(),client)
	except:
		logging.error('connection closed by client')
		return
	def click(cellid,offx=0,offy=0,alt=0,direction=None,c=1,s=.5,so=.5):
		# global prevd
		try:
			if hasattr(cellid,'__next__'):
				cellid=cellid.__next__()
			limit,x,y,line,row={'s':lambda x,odd:(x[0],x[1]+5) if odd else (x[0],x[1]+20) ,'n':lambda x,odd:(x[0],x[1]-27) if odd else (x[0],x[1]-14),'w':lambda x,odd:(x[0]-50,x[1]) if odd else (x[0]-23,x[1]),'e':lambda x,odd:(x[0]+23,x[1]) if odd else (x[0]+50,x[1])},269,16,cellid//14,cellid % 14
			if odd:=line%2:	x+=31
			# if prevd=='d':
			# 	prevd=None
			# 	press('{VK_SHIFT DOWN}')
			# 	press('{VK_SHIFT DOWN}')
			# 	click(useful['mypos'],s=.2)
			# 	press('{VK_SHIFT}')
			if direction not in (None,'d'):
				if useful['mapid']==95420418 and direction in ('e','w'):
					alt=12
				elif useful['mapid']==90702849 and direction=='e':
					alt=-16
				x,y=limit[direction]((x,y),odd)
			# prevd=direction
			logging.info(f'Click : {cellid}, {offx}, {offy}, {alt}, {direction} , {x+ceil(row*62.4)+floor(offx*.687)} , {y+floor(15.58*line)+ceil(offy*.6)-8*alt+38}')
			send(b'c\n'+(x+ceil(row*62.4)+floor(offx*.687)).to_bytes(2,'big',signed=True)+b'\n'+(y+floor(15.58*line)+ceil(offy*.6)-8*alt).to_bytes(2,'big',signed=True)+b'\n'+c.to_bytes(2,'big'))
			if s : wait(s,s+so)
		except:
			logging.error(f'Error in click cellid : {cellid} , offx : {offx} , offy : {offy} , altitude : {alt} , direction : {direction}',exc_info=1)

	def send(t,s=.5):
		global connected
		try:
			conn.sendto(t+b'$$$',client)
			sleep(s)	
		except:
			connected=False

	def press(k,s=.1):
		logging.info(k)
		send(bytes('p\n'+k,'utf-8'))
		wait(s,s+.5)

	def notify(t,s=.5):
		send(b'n\n'+t)
		sleep(s)

	def check_admin():
		global connected
		if useful['threat']:
			send(bytes('a\n'+useful['threat'],'utf-8'),s=7 if useful['threat']=='medium' else 1)
			if useful['threat']=='high':
				connected=False
				assert 0
			elif useful['threat']=='low':
				while useful['dialog'] and connected:
					press('{VK_ESCAPE}',s=1)
					if useful['dialog'] == 2:	useful['dialog']=False
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
								heap.insert(0,[node[0]+[neighbor:=get(k)],len(node[0])+f(neighbor['coord'],target['coord'])])
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
			logging.error(f'Error in get_path x0:{x0}, y0:{y0}, x1:{x1}, y1:{y1}, revert:{revert}\nmat : {mat}',exc_info=1)

	def get_closest_enemy(x0,y0,heap,mat,area,hm=None):
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
			logging.error(f'Error in get_closest x0 : {x0} , y0 : {y0}\nuseful : {useful}',exc_info=1)

	def move_fight(c):
		counter=5
		logging.info(f'in move {useful["mypos"]} , {c}')
		while counter and c!=useful['mypos'] and useful['fight']['mp']:
			click(c,c=2,s=1)
			counter-=1
		logging.info(f'move return {useful["mypos"]}')
		return useful['mypos']

	def check_spells(spells,buffs,mat,treasure):
		try:
			enter=True
			press('~')
			while useful['infight'] and useful['fight']['ap']>2 and enter:
				(x0,y0),ok1=switch_coord(p:=useful['mypos']),False
				logging.info(f'health {useful["lifepoints"]} {useful["maxLifePoints"]}')
				if treasure and useful['lifepoints']/useful['maxLifePoints']<.2:
					logging.info(f'out no hit {useful["lifepoints"]}')
					press('{VK_CONTROL DOWN}')
					press('4')
					press('{VK_CONTROL}')
					click(useful['mypos'],offy=-4)
					break
				else:
					for y,x,k,v in ((y,x,k,v) for y in get_closest_enemy(x0,y0,[p],mat,useful['fight']['mp']) for k,v in spells.items() for x in y[1]):
						if useful['infight'] and useful['fight']['ap']>2:
							if y[0][0] in useful['fight']['enemyteamMembers'] and (v['range'][1] + (useful['fight']['range'] if v['range'][2] else 0) >= (calc:=abs(x[1]-y[0][1])+abs(x[2]-y[0][2])) and calc >=v['range'][0] and not v['fc'] and (not v['inline'] or x[1]==y[0][1] or x[2]==y[0][2]) and (not v['sight'] or x[0]>-1)):
								logging.info(f'call move 1 {p},{x[0]}')
								if (p:=move_fight(t:=abs(x[0])))!=t:	break
								c,counter=v['cpt'],3
								logging.info(f"{ok1},{useful['infight']},{y[0][0] in useful['fight']['enemyteamMembers']},{counter},{v['ap']<=useful['fight']['ap']}")
								while useful['infight'] and y[0][0] in useful['fight']['enemyteamMembers'] and counter and v['ap']<=useful['fight']['ap']:
									press(k)
									ap,counter=useful['fight']['ap'],counter-1
									click(useful['fight']['enemyteamMembers'][y[0][0]]['cellid'],offy=-4,s=1)
									if useful['infight'] and ap != useful['fight']['ap']: 
										if not (c:=c-1):
											v['fc']=max(v['recast'],1)
											if k=='1' and y[0][0] in useful['fight']['enemyteamMembers']:
												ok1=True
											break
								if ok1:	break
						else:	break
				if useful['infight'] and not ok1:
					if useful['fight']['mp']:
						m=600
						for y,x,v in ((y,x,v) for y in get_closest_enemy(x0,y0,[p],mat,50,1) for x in y[1] for v in spells.values()) :
							calc=abs(x[1]-y[0][1])+abs(x[2]-y[0][2])
							if mat[abs(x[0])]==2 and x[0]>-1 and v['range'][1] + (useful['fight']['range'] if v['range'][2] else 0)>=calc and (not v['inline'] or x[1]==y[0][1] or x[2]==y[0][2]) and x[0]!=useful['fight']['enemyteamMembers'][y[0][0]]['cellid'] and calc<m:
								m,x1,y1=calc,x[1],x[2]
								logging.info(f'call move 2 {useful["mypos"]} {p}')
								if move_fight((t:=get_path(x0,y0,x1,y1,mat))[min(useful['fight']['mp'],len(t)-1)])!=t[-1] and not buffs['1']['fc'] and buffs['1']['ap']<=useful['fight']['ap']:
									press('{VK_CONTROL DOWN}')
									press('1')
									press('{VK_CONTROL}')
									(x0,y0)=switch_coord(p:=useful['mypos'])
									click((t:=get_path(x0,y0,y[0][1],y[0][2],mat))[min(6 if useful['my_level']>132 else 5,len(t)-2)],offy=-4,s=1)
									buffs['1']['fc']=buffs['1']['recast']
								break
						useful['fight']['mp']=0#force boost
					elif useful['fight']['ap']>1:
						for k,v in buffs.items():
							if k!='1' and not v['fc'] and not v['cpt'] and v['ap']<=useful['fight']['ap']:
								press('{VK_CONTROL DOWN}')
								press(k)
								press('{VK_CONTROL}')
								click(useful['mypos'],offy=-4,s=1)
								v['fc'],v['cpt']=v['recast'],v['cpt']-1
						enter=False
			for xx in (spells,buffs):
				for x in xx.values():
					if x['fc']:
						x['fc']-=1
			wait(1,4)
		except:
			logging.error(f'Error in check_spells\nuseful : {useful}\nspells : {spells}\nbuffs : {buffs}\nmat : {mat}',exc_info=1)
		finally:
			return spells,buffs
	def fight(treasure=False):
		try:
			logging.info(f'Enter fight')
			# press('{VK_SHIFT}')
			try:
				if not useful['fight']['lock']:
					click(557,offy=20,offx=15,s=1)
					press('{VK_NUMPAD8}')
				if not useful['fight']['spectator']:	
					click(557,offy=150,offx=14)
				if useful['mount'] and useful['mount']['energy'] and not useful['mount']['riding']:	
					press('{VK_NUMPAD6}')
			except:
				logging.error('lock spec mount error',exc_info=1)
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
					click(index,s=.5)
			except:
				logging.critical('too late for positioning',exc_info=1)
			spells,buffs= (
							#spells
							{'1': {'range': (1, 5, False),'ap':4, 'cpt' : 1 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': True},
							 '2': {'range': (1, 3, False),'ap':3, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': False}}
							 if useful['my_level']<194 else
						 		{'1': {'range': (1, 5, False),'ap':4, 'cpt' : 1 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': True},
								'2': {'range': (1, 1, False),'ap':3, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': False},
						 		'3': {'range': (1, 3, False),'ap':3, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': False},
						 		'4': {'range': (1, 4, False),'ap':5, 'cpt' : 1 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': False},
						 		'5': {'range': (1, 6, False),'ap':4, 'cpt' : 1 , 'recast': 0, 'fc': 0, 'sight': False, 'inline': False}}
						 ,
							#buffs/debuffs
							{'1' : {'ap':5, 'recast':1,'fc':0,'cpt':1},
							 '2' : {'ap':3, 'recast':0,'fc':0,'cpt':2},
							 '3' : {'ap':3, 'recast':4,'fc':0,'cpt':1},
							})
			while useful['infight'] and connected:
				press('{F1}')
				counter=5
				while not wait(1,2) and 'turn' in useful['fight'].keys() and not useful['fight']['turn'] and connected and useful['infight'] and (counter:=counter-1):
					check_admin()
					logging.info('Waiting for turn')
				spells,buffs=check_spells(spells,buffs,mat,treasure)
		except:
			logging.error(f'Error in fight\nuseful : {useful}',exc_info=1)
		finally:
			prev=useful['mypos']
			wait(2,3)
			for _ in range(3):
				click(554,offy=120,s=.5)
				press('~')
			if useful['mount'] and useful['mount']['riding']:
				press('{VK_NUMPAD6}')
			return prev

	def move(nid,zaap=False,exit=None,nested=False,harvest=False):
		global connected
		logging.info(f'move to : {nid} , zaap : {zaap} ,exit node : {exit}')
		if zaap:
			n,m=func(nid),1000
			for x in collection.zaaps.find({}):
				if (calc:=abs(int((c:=x['_id'].split(','))[0])-n['coord'][0])+abs(int(c[1])-n['coord'][1]))<m:
					name,m=x['name'],calc	
			teleport(name,exit)
			nid=n['_id']
		for e in (p:=pathfinder((c:=get_current_node(1)),nid,shuffle=False)):
			prev=useful['mapid']
			check_admin()
			if harvest:
				press('{VK_SHIFT DOWN}')
				if (mat:=collect(*harvest[1:]))==-1:
					press('{VK_SHIFT}')	
					return move(nid,True,harvest=harvest)
				press('{VK_SHIFT}')
			click(cell:=get_closest(e[0],set_mat(e[2])[1],e[1]),direction=e[1])
			if not connected:	assert 0
			if cond_wait(2,2.5,['mapid',prev,4,wrapper(click,cell,direction=e[1])])==-1:
				logging.info('Recall move from nested func move')
				if nested:
					logging.critical('closing connection client sniffer error')
					connected=False
					assert 0
				return move(nid,nested=True)
			if hasattr(exit,'__call__') and not exit():	
				return
		return nid

	def treasure_hunt(supervised=False,harvest=False):
		from urllib.request import urlopen,Request
		from json import loads,load,dump
		def check_hint(j=None,last=True):
			logging.info(f'check hint : offset : {j} last : {last}')
			if j != None:
				flags,i=useful['hunt']['flags'],4
				while (t:=flags==useful['hunt']['flags']) and i:
					click(70,-118,-12+j*35,s=2)
					i-=1
				if t:
					return
			if last:
				click(70,-132,useful['hunt']['totalStepCount']*35-4,s=2)
			return True
		def wait_fix():
			logging.info('Wait for hunt fix -> sleeping')
			from subprocess import Popen,PIPE,DEVNULL
			while (t:=Popen(args='REG QUERY HKCU\Environment /v fix',stdout=PIPE,stderr=DEVNULL).communicate()[0].split(b' ')[-1].decode())[:t.index('\r')]!=name+'-'+server:
				sleep(10)
			logging.info("break from wait_fix")
			Popen('setx fix 0',stdout=DEVNULL)
		def update_treasure(last,hint,start_coord):
			try:
				logging.info(f'update_treasure called {last} {hint}')
				direction,test_coord=str(hint['direction']),lambda x,y,x1,y1,d:x>=x1 if d=='4' else x<=x1 if d=='0' else y<=y1 if d=='2' else y>=y1
				for d in directions.items():
					logging.info(f'updating direction : {d}')
					cur,i,tlist={'_id':last},11,[d[1][0],"d"]
					while i and (cur:=collection.nodes.find_one({'_id':cur['_id']}))[d[1][0]]:
						if last==cur['_id']:	x,y=cur['coord'][0],cur['coord'][1]
						calc=0
						for ty in tlist:
							for tx in cur[ty]:
								tn=collection.nodes.find_one({'_id':tx})
								if ((l:=len(tn['walkable']))>calc and tn[ty] or tn['d']) or len(cur[ty])==1:
									cur,calc=tn,l
							if 	calc:	break
						if not calc:
							i=1
							logging.info(f"Stop updating on direction {d} last node is {cur['coord']}")
						else:
							logging.info(f'updating {cur["coord"]}')
						x1,y1=cur["coord"][0],cur["coord"][1]
						if x!=x1 or y!=y1:
							if temp2:=collection.treasure.find_one({'_id':(id:=f'{x1},{y1}')}):
								if directions[d[0]][-1] in temp2:
									for t in temp2[directions[d[0]][-1]]:
										if t['id']==hint['poiLabelId']:
											if direction==directions[d[0]][-1] and test_coord(start_coord[0],start_coord[-1],x1,y1,direction):
												t['x'],t['y']=x,y
											elif test_coord(x,y,t['x'],t['y'],directions[d[0]][-1]):
												t['x'],t['y']=x,y
											else:
												i=1
											break
									else:
										temp2[directions[d[0]][-1]].append({'id':hint['poiLabelId'],'x':x,'y':y})
								else:
									temp2[directions[d[0]][-1]]=[{'id':hint['poiLabelId'],'x':x,'y':y}]
								collection.treasure.update_one({'_id':id},{'$set':{directions[d[0]][-1]:temp2[directions[d[0]][-1]]}})
							else:
								collection.treasure.insert_one({'_id':id},{'$set':{directions[d[0]][-1]:[{'id':hint['poiLabelId'],'x':x,'y':y}]}})
						i-=1
				with open('./hints.json', 'r', encoding='utf8') as f:
					a=load(f)+[{'coord':f'{x},{y}','name':collection.named_ids.find_one({'_id':hint['poiLabelId']})['name'],'direction':direction,'start':start_coord}]
				with open('./hints.json', 'w', encoding='utf8') as f:
					dump(a,f)
			except:
				logging.error('Failed updating missing clue',exc_info=True)
		def fix():
			try:
				logging.warning(f'Treasure Fix Called :\n{useful["hunt"]}')
				check_hint()
				last,current_coord,prev,j=(t:=collection.nodes.find_one({'mapid':useful['hunt']['flags'][-1]['mapId'] if useful['hunt']['flags'] else useful['hunt']['startMapId']},{'mapid','coord'}))['_id'],t['coord'],useful['hunt']['currentstep'],len(useful['hunt']['flags'])
				if 'npcId' in useful['hunt']['currentstep']:
					logging.critical('encountered sneaky in fix')
					return last
				logging.info(f'start node : {last} start_coord : {current_coord} currentstep : {prev}')
				try:
					logging.info('Try Fix in dofus sama')
					for x in f([int((t:=(r:=urlopen(Request('https://www.dofusama.fr/treasurehunt/en/search-clue.html', f'direction={useful["hunt"]["currentstep"]["direction"]}&map_pos_x={current_coord[0]}&map_pos_y={current_coord[1]}&map_indice={collection.dofus_sama.find_one({"_id":useful["hunt"]["currentstep"]["poiLabelId"]})["ds_id"]}'.encode('ascii'),headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8'))[(s:=r.index('>[')+2):r.index(']',s)].split(','))[0]),int(t[1])],last,directions[useful['hunt']['currentstep']['direction']][0]):
						last=move(x)
						logging.info(f'Dofus sama clue in node {last}')
						check_hint(j)
						logging.info(f'currentstep after try {useful["hunt"]["currentstep"]}')
						if  j!=len(useful['hunt']['flags']) or useful["hunt"]["currentstep"]['__type__']=='TreasureHuntStepFight':
							update_treasure(last,prev,current_coord)
							return last
				except:
					logging.warning('Treasure Hunt : Couldn\'t find this clue on dofus sama')
				if supervised:
					notify(b'TREASER HUNT\nSET CLUE MANUALLY')
					logging.info('SET CLUE MANUALLY')
					wait_fix()
					update_treasure(last:=get_current_node(1),prev,current_coord)
				else:
					logging.info('Trying random fix')
					while useful['hunt']['availableRetryCount']:
						#add testing to all nodes in given direction
						last=move(l[0] if (l:=[*collection.nodes.find_one({'_id':last},{directions[useful['hunt']['currentstep']['direction']][0],'coord'})[directions[useful['hunt']['currentstep']['direction']][0]]]) else [*collection.nodes.find_one({'_id':last},{"d",'coord'})["d"]][0])
						logging.info(f"Fix {last} {directions[useful['hunt']['currentstep']['direction']][0]}")
						check_hint(j)
						if j!=len(useful['hunt']['flags']):
							logging.info('update called from random fix')
							update_treasure(last,prev,current_coord)
							break
						if (cond:=useful['hunt']['currentstep']['poiLabelId'] in fix_list.get().keys()) and useful['mapid'] in fix_list.get()[useful['hunt']['currentstep']['poiLabelId']]:
							continue
						if useful['hunt']['availableRetryCount']:
							lock.acquire()
							temp=fix_list.get()
							logging.info(f'adding new map to avoid while fixing {temp}')
							temp[useful['hunt']['currentstep']['poiLabelId']]=temp[useful['hunt']['currentstep']['poiLabelId']]+[useful['mapid']] if cond else [useful['mapid']]
							fix_list.set(temp)
							lock.release()
							logging.info(f'state after update {temp}')
					logging.info(f'currentstep after loop iter {useful["hunt"]["currentstep"]}')
					logging.info(f'return after for loop fix {useful["hunt"]["result"]} {last}')
				logging.info(f'fix return {last} , {useful["hunt"]}')
				return None if 'result' in useful and useful['hunt']['result']==4 else last
			except:
				logging.error('Failed fixing missing clue probably hunt failed',exc_info=True)
		def f(coord,last,d,nested=False):
			logging.info(f"f called with {coord} {last} {d}")
			cur,ret=collection.nodes.find_one({'_id':last},t:={d,'d','coord','mapid','walkable'}),[]
			while cur['coord']!=coord and not ret or cont:
				calc,cont=0,False
				for x in [*cur[d]]:
					#not ideal didn't check exact path or smaller node have access to doors
					tn=collection.nodes.find_one({'_id':x},t)
					if ((l:=len(tn['walkable']))>calc and tn[d] or tn['d']) or tn['coord']==coord:
						if tn['coord']==coord:
							ret.insert(0,tn['_id'])
							cont=True
						cur,calc=tn,l
				if not calc:
					for x in [*cur['d']]:
						if (cur:=collection.nodes.find_one({'_id':x},t))[d] or cur['coord']==coord:##not ideal didn't check 2 straight doors
							break
					else:
						if not ret:
							if not nested:
								for x in collection.nodes.find({'mapid':collection.nodes.find_one({'_id':last},{'mapid'})['mapid']},{'_id'}):
									if x['_id']!=last:	return f(coord,x['_id'],d,True)
							notify(b'TREASER HUNT\nSET DOORS/CAVES')
							logging.info('SET DOORS/CAVES')
							wait_fix()
							cur=collection.nodes.find_one({'_id':get_current_node(1)},t)##not ideal didn't check 2 straight doors
			return [cur['_id']] if not ret else ret	
		e=get_current_node(1,142089230,357)
		while connected:
			try:
				logging.info(f'Treasure Hunt has began')
				if 'hunt' not in useful:
					move(128452097,zaap=True,exit=e)
					while 'hunt' not in useful and connected:
						click(554,offy=120)
						click(288,s=.5)
						press('{DOWN}')
						press('~',s=5)
						if 'retake' in useful and useful['retake']:
							click(70,-118,-87,s=1)
							press('~',s=1)
							del useful['retake']
						if 'wait' in useful:
							sleep(60*useful['wait'])
							del useful['wait']
					move(e,False,exit=e)
				directions,last={0:('e','right','4'),4:('w','left','0'),2:('s','bottom','6'),6:('n','top','2')},move(useful['hunt']['flags'][-1]['mapId'] if useful['hunt']['flags'] else useful['hunt']['startMapId'],True,exit=e)
				while useful['hunt']['checkPointTotal']-useful['hunt']['checkPointCurrent']-1:
					for j in range(len(useful['hunt']['flags']),useful['hunt']['totalStepCount']):
						current_coord,skip,fail=collection.nodes.find_one({'_id':last},{'coord':1,'_id':0})['coord'],False,False
						logging.info(f'current step {useful["hunt"]["currentstep"]}\ncurrent coord {current_coord}')
						if 'poiLabelId' in useful['hunt']['currentstep']:
							logging.info(f'Looking for clue {useful["hunt"]["currentstep"]["poiLabelId"]} on Dofus Map')
							strcell=str(current_coord[0])+","+str(current_coord[1])
							if res:=collection.treasure.find_one({'_id':f'{strcell+"*"+str(int(useful["mapid"])) if current_coord[0]==-15 and current_coord[1]== 39 else strcell}',f'{(d:=str(useful["hunt"]["currentstep"]["direction"]))}.id':useful['hunt']['currentstep']['poiLabelId']},{d}):
								for x in res[d]:
									if x['id']==useful['hunt']['currentstep']['poiLabelId']:
										next_node=f([x['x'],x['y']],last,directions[useful['hunt']['currentstep']['direction']][0])
										logging.info(f'Dofus map clue in this node {next_node}')
										break
							else:
								logging.warning('Treasure Hunt : Couldn\'t find this clue on dofus map')
								last,skip=fix(),True
								break
						else:
							temp,t,tt=last,{directions[useful['hunt']['currentstep']['direction']][0]:1,"d":1},{directions[useful['hunt']['currentstep']['direction']][0]:1,"d":1,"walkable":1}
							try:
								for _ in range(10):
									calc=0
									for y in t:
										for x in (li:=[*collection.nodes.find_one({'_id':temp},t)[y]]):
											tn,temp=collection.nodes.find_one({'_id':x},tt),x
											if ((l:=len(tn['walkable']))>calc and tn[y] or tn['d']) or len(li)==1:
												temp,calc=x,l
										if 	calc:	break
									else: break
									move(temp,harvest=harvest)
									if useful['hunt']['currentstep']['npcId'] in useful['map_npc']:	break
								next_node=[temp]
							except Exception as e:
								logging.info(f'sneaky error {e}')
								break
						logging.info(f'move to {next_node} and flag it')
						if (length:=len(next_node)==1) and next_node[0]==last:
							logging.info('move called on same map call fix')
							break
						else:
							for x in next_node:
								last,prev=move(x,harvest=harvest),len(useful['hunt']['flags'])
								if useful['mapid'] in {y['mapId'] for y in useful['hunt']['flags']}:
									logging.info(f"skip current map {x} {useful['mapid']} {useful['hunt']['flags']}")
									if x==next_node[-1]:	skip=True
								elif not check_hint(j,False if length else True):
									logging.info(f'Failed flagging the clue on this map {x}')
									if x==next_node[-1]:	fail=True#try fix
								elif prev!=len(useful['hunt']['flags']):
									break
							if skip or fail: break
					if not skip:
						if 'result' in useful['hunt'] and useful['hunt']['result']==4:
							break
						check_hint()
						if 'result' in useful['hunt'] and useful['hunt']['result']==3:
							logging.warning(f'Wrong clue after for loop')
							last=fix()
				if useful['hunt']['result']!=4:
					click(70,-263,-87)
					wait_check_fight(3,4,Treasure=True)
			except:
				print('Error in Treasure Hunt')
				logging.info('Error in Treasure Hunt',exc_info=True)

	def get_closest(edge,mat,direction):
		try:
			generate=lambda cells,length:(x for x in [cells[y if y < length else randint(0,length-1)] for y in range(5)])
			if direction=='d':
				return generate(edge,len(edge))
			elif useful['mypos'] in edge:
				return (y if (y:=useful['mypos'] + (x if x <3 else -x+2)*(28 if direction in ('w','e') else 1)) else useful['mypos'] for x in range(5))#check new pos in node edges
			l,base,done,ret=[useful['mypos']],(28,-28,1,-1,13,14,-13,-14),set(),[]
			while l:
				for i in range(8): 
					if (ooe:=l[0]//14%2) and l[0]%14==13 and i in (5,6) or not ooe and not l[0]%14 and i in (4,7) or not l[0]%14 and i==3 or l[0]%14==13 and i==2:
						continue  
					next_cell=(base[i]+1 if ooe and i in (4,5) else base[i] -1 if not ooe and i>5 else base[i])+l[0]
					if next_cell>-1 and next_cell<560  and next_cell not in l and next_cell not in done and mat[next_cell]==2:
						if next_cell in edge:
							ret.append(next_cell)
							if (ll:=len(ret))>=min(5,len(edge)):
								return generate(ret,ll)
						l.append(next_cell)
				done.add(l[0])
				l.pop(0)
			print('Critical in get_closest (cells) out empty')
			logging.critical(f'out empty in get_closest (cells) current pos {useful["mypos"]} edges : {edge}\nmat : {mat}\ndirection : {direction}')
			return generate(edge,len(edge))
		except:
			print('Error in get_closest (cells)')
			logging.error(f'Error in get_closest (cells) direction : {direction}\nedge : {edge}\nmat : {mat}',exc_info=True)

	def wrapper(fun, *args, **kwargs):
		def wrapped():
			return fun(*args, **kwargs)
		return wrapped

	def teleport(text,exit=None):
		logging.info(f'Teleporting to {text}')
		while useful['dialog']:
			press('{VK_ESCAPE}',s=5)
		count=3
		while useful['mapid']!=162793472 and connected: 
			click(554,offy=120,s=.5)
			press('h')
			wait_check_fight(4,5)
			check_admin()
			if not (count:=count-1):
				logging.warning(f'Could Not Teleport To HavenBag From This Map {useful["mapid"]} exit node {exit}')
				if exit:	move(exit,exit=wrapper(teleport,text))
				return True
		logging.info(f'Enter Havenbag ,{useful["mapid"]}')
		counter=-1
		while not useful['dialog'] and connected:
			click(173, -10, -10,s=2.5,so=3.5)
			if (counter:=counter+1)>=5:
				logging.warning(f'teleport counter surpassed {useful["mapid"]}')
				click(300,s=1)
		while useful['mapid']==162793472 and connected:
			click(134,offy=-10,c=3,s=1)
			press(text,s=1)
			click(175,offy=-5,c=2,s=5)
			check_admin()
		logging.info(f'Done teleporting to {text} current mapid is {useful["mapid"]}')

	def check_adjc(l,mat,pos):
		try:
			base,temp=(13,14,-13,-14,0),[]
			while l:
				for i in range(5): 
					if (ooe:=l[0]//14%2) and l[0]%14==13 and i in (1,2) or not ooe and not l[0]%14 and i in (0,3):
						continue
					next_cell=(base[i]+1 if ooe and i<2 else base[i] -1 if not ooe and (i>1 and i<4) else base[i])+l[0]
					if next_cell>-1 and next_cell<560:
						if mat[next_cell]==2:
							temp.append(next_cell)
						elif next_cell not in l:
							l.append(next_cell)
				if temp:
					(x0,y0),m=switch_coord(pos),600
					for x in temp:
						(x1,y1)=switch_coord(x)
						if (dist:=abs(x0-x1)+abs(y0-y1))<m:
							c=x
					return c
				l.pop(0)
		except:
			logging.error(f'Eroor in check_adjc pos : {pos}\nlist : {l}\nmat : {mat}',exc_info=True)

	def sub_order(li,mat,pos):
		try:
			if (l:=len(li))<2:
				return li,(li[0][0] if l else pos)
			ref,l,ret,length={},[],[],0
			for x in li:
				if (a:=check_adjc([x[0]],mat,pos)):
					if a not in l:
						l.append(a)
						length+=1
					ref[a]=ref[a]+[x] if a in ref else [x]
			while length:
				m=600
				for i in range(length):
					(x0,y0),(x1,y1)=switch_coord(pos),switch_coord(l[i])
					calc=get_path(x0,y0,x1,y1,mat,revert=False)
					if calc<m:
						index,m=i,calc
				length,pos,ret=length-1,l[index],ret+[x for x in ref[l[index]]]
				l.pop(index)
			return ret,pos
		except:
			logging.error(f'Eroor in sub_order pos : {pos}\nlist : {li}\nmat : {mat}',exc_info=True)

	def order(li,mat,priority):
		try:
			ret,pos=[],useful['mypos']
			for x in priority:
				if top:=[(y[1],y[2]) for y in li if y[0]==x]:
					t=sub_order(top,mat,pos)
					ret,pos=ret+t[0],t[1]
			return ret+sub_order([(x[1],x[2]) for x in li if (x[1],x[2]) not in ret],mat,pos)[0]
		except:
			logging.error(f'Eroor in order list : {li}\npriority : {priority}\nmat : {mat}',exc_info=True)

	def wait_check_fight(tmin,tmax,cond=0,Treasure=False):
		try:
			wait(tmin,tmax)
			check_admin()
			if useful['infight'] and cond!=-1:
				pos=fight(treasure=Treasure)
				if not useful['fight']['alive']:
					logging.info('Fight Lost')
					wait(7,15)
					while not useful['energy']:
						logging.info('Player became a ghost trying to revive')
						press('{VK_ESCAPE}{ENTER 3}',s=2)
						while not useful['phenix']:
							click(532,-100,180,c=3,s=1)
							press('/release~',s=5)
						click(collection.nodes.find_one({'_id':move(collection.nodes.find_one({'mapid':useful['phenix']},{'_id'})['_id'])},{'o'})['o'][useful['phenix_id']])
						wait(5,10)
						press('{VK_NUMPAD6}')
					return -1
				elif useful['mypos']==pos:
					logging.info('Forced break after fight : character didn\'t do anything')
					return 100
				# press('{VK_SHIFT DOWN}')
				logging.info('fight ended no action needed')
				return 1
		except:
			logging.error(f'Eroor in wait_check_fight {tmin} {tmax} {cond}',exc_info=True)

	def cond_wait(tmin,tmax,cond):
		global archmonsters
		try:
			tries=0
			if useful['my_level']>160:
				for m in useful["map_mobs"].items():
					if 'info' in m[1].keys():
						for i in m[1]['info']:
							if i[0] in archmonsters.keys():		
								notify(('ArchMonster Found !\nID : %s , Name : %s , Level : %s , Coord : %s'%(name+' - '+server,archmonsters[i[0]],i[1],collection.nodes.find_one({'mapid':useful['mapid']},{'coord':1})['coord'])).encode())
								sleep(30)#to change based on hunt mode supervied or not
								break
			# if useful['client_render_time']>7:	sleep(useful['client_render_time']/2)#avoid runtime error on overloaded maps
			while useful[cond[0]] == cond[1] and connected:
				if cond[2]!=-1:
					if tries >= cond[2]:
						logging.info(f'Forced break after timeout , {useful["mapid"]}')
						# press('{VK_SHIFT}',s=.5)
						cond[3]()
						wait_check_fight(tmin,tmax,cond[2])
						if useful[cond[0]] == cond[1]:
							cond[2]-=1
							if not cond[2]:
								logging.critical(f'Breaking from path : something bad happened here {useful["mapid"]}')
								return -1
							return cond_wait(tmin,tmax,cond)	
				if (t:=wait_check_fight(tmin,tmax,cond[2]))==-1:
					return -1
				tries+=t if t else 1
		except:
			logging.error(f'Eroor in cond_wait {tmin} {tmax} {cond}',exc_info=True)

	def set_mat(key):
		try:
			if not key:
				t=get_current_node(2)
			else:
				t=collection.nodes.find_one({'_id':key},{'interactives':1,'walkable':1,'_id':0})
			return t['interactives'],[2 if x in t['walkable'] else 0 for x in range(560)]
		except:
			logging.error(f'Eroor in set_mat the key was : {key}',exc_info=True)


	def level_up(zone):
		from copy import deepcopy
		useful['my_level'],threshold=(4,1.5) if '1' == zone else (17,1.2) if zone in ('2','3') else (25,1.2)
		logging.info(f'wait for map change : Zone {zone} , Start Level : {useful["my_level"]}')
		while not useful['mapid'] and connected:	wait(1,2)
		logging.info("map changed start leveling up")
		p=[x for x in collection.paths.find_one({'_id':zone},{'nodes'})['nodes']]
		while connected:
			try:
				for n in p:
					if n!=move(n):	break	
					loop=True
					while loop:
						check_admin()
						temp=deepcopy(useful['map_mobs']).items()
						if useful['lifepoints']/useful['maxLifePoints']<.8:
							logging.info('sleeping')
							sleep((useful['maxLifePoints']-useful['lifepoints'])/2)
							logging.info('done sleeping')
							useful['lifepoints']=useful['maxLifePoints']
						for x,y in temp:
							logging.info(f'{x} {y}')
							if 'alllevel' in y and y['alllevel']<useful['my_level']*threshold and y['cellId'] not in [c['cellId']-28*r for c in useful['map_players'].values() for r in range(2)] and y['cellId'] not in [(c['cellId'] if not mlr else c['cellId']-(14 if (ooe:=c['cellId']//14%2) else 15) if mlr==1 else c['cellId']-(13 if ooe else 14))-28*r for c in useful['map_npc'].values() for mlr in range(3) for r in range(4)]:
								counter,state=4,None
								# press('{VK_SHIFT}',s=.5)
								click(y['cellId'])
								while not state and counter and x in useful['map_mobs']:
									state=wait_check_fight(2,3)
									counter-=1
								if state==-1:
									loop=False
								if state:
									break
						else:
							loop=False
			except:
				logging.error(f'Error in level_up zone : {zone}\ntemp {temp}',exc_info=1)

	def collect(rsc,priority,exceptions,safe_mode,key=None):
		try:
			e,mat=set_mat(key)
			for x in useful['resources'].values():
				if x['enabledSkill'] == 102 and str(x['elementCellId']) not in e:
					e[str(x['elementCellId'])]={"xoffset":0,"yoffset":-5,"altitude":0}
					collection.nodes.update_one({"_id":get_current_node(1)},{'$set':{'interactives':e}})
					logging.info(f'added a well to this map {useful["mapid"]}')
			for c,k in order([(x['enabledSkill'] ,x['elementCellId'],k) for k,x in useful['resources'].items() if (str(x['elementCellId']) in e and 'enabledSkill' in x and x['enabledSkill'] in rsc )],mat,priority):
				if safe_mode and len(useful['map_players']):	break
				if k in useful['resources']:
					maxi,offx,offy,prev=5,e[(s:=str(c))]['xoffset'],e[s]['yoffset'],useful['mypos']
					if (t:=useful['resources'][k]['enabledSkill']) in exceptions:
						offx,offy=offx+exceptions[t][0],offy+exceptions[t][1]				
					click(c, offx, offy, e[s]['altitude'])
					while k in useful['resources'] and maxi:
						if (t:=wait_check_fight(1.5,2))==100 or not useful['Harvesting'] and not sleep(1) and prev==useful['mypos']:
							break
						elif check_inventory() or t==-1:
							return -1
						elif useful['mypos']==c and not useful['Harvesting']:
							notify((f'MISS CLICK WHILE HARVESTING\n{name+"-"+server}').encode())
							# sleep(30)
							break
						maxi-=1
			return mat
		except:
			logging.error(f'Eroor in collect rsc : {rsc}\nkey : {key}\npriority : {priority}\nexceptions : {exceptions}\nuseful : {useful}',exc_info=True)

	def check_inventory():
		if useful["full_inventory"] or useful['inventory_weight'] / useful['inventory_max']>.97:
			logging.info(f'Inventory is full {useful["inventory_weight"]}')
			n,m,counter=func(useful['mapid'])['coord'],1000,5
			for x in sample((84935175,99095051,192415750,8914959,8913935,8912911,2885641,2884617,2883593,8129542,91753985,54534165),12):
				if (calc:=abs((c:=func(x)['coord'])[0]-n[0])+abs(c[1]-n[1]))<m:
					name,m=x,calc 	
			# if not move(name,True):
				# logging.info(f'Failed emptying inventory from this map{useful["mapid"]}')
				# return
			move("61")

			while not useful['dialog']:
				press('{VK_SHIFT}')
				click([*useful['map_npc'].values()][randint(0,len(useful['map_npc'])-1)]['cellId'],offy=-50,s=4,so=3)
			press('{DOWN}',s=1)
			press('~',s=5)
			for i in range(2):
				click(82,i*20,-7,s=3,so=2)
				click(80,-15,-7,s=1)
				press('{DOWN}{DOWN}~',s=1)
			click(83,8,-50,s=2,so=3)
			useful["full_inventory"]=False
			logging.info(f'Done emptying inventory {useful["inventory_weight"]}')
			return True

	def harvest(paths,rsc,priority,exceptions,safe_mode):
		try:
			while not useful['mapid']:	sleep(5)
			while connected:
				for p in sample(paths,len(paths)):
					# teleport(collection.zaaps.find_one({'_id':p['zaap']})['name'])
					p,path=[get_current_node(1)]+p['nodes'],[]
					for s in range(len(p)-1):
						path+=pathfinder(p[s],p[s+1])
					for e in path:
						prev=useful['mapid']
						press('{VK_SHIFT DOWN}')
						if (mat:=collect(rsc,priority,exceptions,safe_mode,e[2]))==-1:
							break
						click(cell:=get_closest(e[0],mat,e[1]),direction=e[1])
						press('{VK_SHIFT}')
						if cond_wait(2,2.5,['mapid',prev,4,wrapper(click,cell,direction=e[1])])==-1 or not connected:
							break
					else:
						collect(rsc,priority,exceptions,safe_mode=safe_mode)
					press('{VK_SHIFT}')
					wait_check_fight(4,4.5)

		except:
			logging.error(f'Error in harvest',exc_info=True)

	class Buffer(Data):
		def end(self):
			del self.data[: self.pos]
			self.pos = 0

		def reset(self):
			self.__init__()

	class Msg:
		def __init__(self, m_id, data, count=None):
			self.id = m_id
			if isinstance(data, bytearray):
				data = Data(data)
			self.data = data
			self.count = count

		def __str__(self):
			ans = str.format(
				"{}(m_id={}, data={}, count={})",
				self.__class__.__name__,
				self.id,
				self.data.data,
				self.count,
			)
			return ans

		def __repr__(self):
			ans = str.format(
				"{}(m_id={}, data={!r}, count={})",
				self.__class__.__name__,
				self.id,
				self.data.data,
				self.count,
			)
			return ans

		@staticmethod
		def fromRaw(buf: Buffer, from_client):
			global waitp
			if not buf:
				return
			try:
				header = buf.readUnsignedShort()
				total = 2
				if from_client:
					count = buf.readUnsignedInt()
					total += 4
				else:
					count = None
				id = header >> 2
				ld = header & 3
				total += ld
				lenData = int.from_bytes(buf.read(ld), "big")
				logging.info(f'from raw packet {id} {lenData} {len(buf)}')
				if lenData > len(buf) - total:
					raise IndexError
				if id not in [6103,6268,6130,6791,6828,3009,226,5618,5740,6830,5502,5787,951,5921,5528,5864,5696,5525,700,143,5927,6239,6312,5522,5910,5731,5523,5586,5552,6643,5787,500,6322,209,1030,5686,46,29,719,714,712,713,1099,703,5658,6465,6132,720,8,153,5670,178,5967,5708,881,6134,6135,76,5996,6486,6484,6483,780,156,471,251,160,159,36,141,566,6622]:
					buf.read(lenData)
					return
				data = Data(buf.read(lenData))
			except IndexError:
				buf.pos = 0
				if useful['reset']:
					useful['reset']=False
					buf.reset()
					waitp=b''
				return "next"
			else:
				if id == 2:
					newbuffer = Buffer(data.readByteArray())
					newbuffer.uncompress()
					msg = Msg.fromRaw(newbuffer, from_client)
					assert msg is not None and not newbuffer.remaining()
					return msg
				buf.end()
				return Msg(id, data, count)

		def lenlenData(self):
			if len(self.data) > 65535:
				return 3
			if len(self.data) > 255:
				return 2
			if len(self.data) > 0:
				return 1
			return 0

		def bytes(self):
			header = 4 * self.id + self.lenlenData()
			ans = Data()
			ans.writeShort(header)
			if self.count is not None:
				ans.writeUnsignedInt(self.count)
			ans += len(self.data).to_bytes(self.lenlenData(), "big")
			ans += self.data
			return ans.data

		@property
		def msgType(self):
			global waitp
			try:
				return msg_from_id[self.id]
			except:
				buf.reset()
				waitp=b''
				logging.critical(f'Error in start key error hard reset {useful["mapid"]}')

		def json(self):
			if not hasattr(self, "parsed"):
				self.parsed = read(self.msgType, self.data)
			return self.parsed

		@staticmethod
		def from_json(json, count=None, random_hash=True):
			try:
				type_name: str = json["__type__"]
				type_id: int = types[type_name]["protocolId"]
				data = write(type_name, json, random_hash=random_hash)
				return Msg(type_id, data, count)
			except:
				logging.critical(json)

	def on_receive(pa):
		global buf, waitp
		logging.info(f'recev {len(pa)}')
		if len(waitp)>1500:	logging.info(f'buff len {len(waitp)}')
		try:
			waitp += pa
			length=int.from_bytes(waitp[:2], 'big')
			buf += decompress(waitp[2:2+length])
			waitp=waitp[2+length:]
			msg = None
			while len(buf) > 0 and msg != "next":
				msg = Msg.fromRaw(buf, None)
				while msg and msg != "next":
					on_msg(msg)
					msg = Msg.fromRaw(buf, None)
			if waitp and int.from_bytes(waitp[:2], 'big') <= len(waitp[2:]):
				on_receive(b'')
		except Exception as e:
			logging.error(e)

	def on_msg(msg):
		global buf,waitp
		try:
			Msg.from_json(msg.json())
		except:
			buf.reset()
			waitp=b''
			logging.error(f'Error in Start',exc_info=1)
			
	def explore():
		try:
			logging.info('exploring zaaps')
			teleport('astrub')
			for x in collection.paths.find_one({'_id':"zaaps"},{'nodes'})['nodes']:	
				if x!=(t:=move(x)):
					logging.error(f'couldn\'t finish exploring stop in this node {t}')
					return
		except:
			logging.error('Error in explore',exc_info=1)

	def sniffer():
		global connected
		try:
			while connected:	on_receive(conn.recv(8192))
		except Exception as e:
			logging.error(f'Error in sniffer : {e}')
			connected=False
	buf=Buffer()
	thread=Thread(target=sniffer)
	thread.start()
	for _ in range(3):	press('~',s=1)
	press('{VK_NUMPAD6}',s=1)
	if useful['mount'] and useful['mount']['riding']:	press('{VK_NUMPAD6}')
	logging.info(str(useful['mount']))
	if (cond:=parameters[0] =='1' and parameters[1]) or parameters[0]=='2':
		g,param=lambda rsc:[s for r in rsc for x in collection.skills.find({'_id':{'$regex': '^%s.*'%(r),'$options':'i'}}) for s in x['skill_id']],[[y.replace(' ','') for y in x[x.find(':')+1:].split(',')]for x in parameters[1:]]
		param_list=[list(collection.paths.find({'$or':[{'_id':{'$regex':f'.*{x}.*','$options':'i'}} for x in param[0]]},{'zaap':1,'nodes':1})),set(g(param[1])),g(param[2]),{x['_id']:[x['offx'],x['offy']] for x in collection.exceptions.find({},{'offx':1,'offy':1})},param[-1][0]=='1']
	treasure_hunt(1,param_list if cond else False) if parameters[0]=='1' else harvest(*param_list) if parameters[0]=='2' else level_up(parameters[1]) if parameters[0]=='3' else explore() if parameters[0]=='4' else logging.error('Wrong algorithm option')
	if thread:	thread.join()
	conn.close()
	logging.info('\n\n\nProcess Terminated\n\n\n')