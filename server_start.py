def launch_in_process(conn,client,name,server,parameters):
	from zlib import decompress	
	from data import Data
	from json import load,dump
	from server_protocol import read, msg_from_id, types, write, logging,useful
	from random import sample,uniform,randint,choice,random
	from pymongo import MongoClient
	from math import ceil,floor
	from time import sleep,time
	from threading import Thread
	from urllib.request import urlopen,Request
	global collection,wait,func,waitp,buf,connected,archmonsters
	#'mongodb+srv://carbon:bot@carbon-9bthr.gcp.mongodb.net/test?retryWrites=true&w=majority').carbon_db
	collection,wait,useful['name'],useful['server'],useful['mod'],connected=MongoClient('localhost:27017').admin,lambda x,y:agro(uniform(x,y)),name,server,False,True
	func,waitp,archmonsters=lambda x:collection.nodes.find_one({'mapid':x}, {'coord'}),b'',{x['raceid']:x['_id'] for x in collection.archmonsters.find({})}
	logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename=f'logs/log-{name} - {server}.txt', level=logging.INFO)
	logging.raiseExceptions = False
	try:
		conn.sendto(collection.servers.find_one({'_id':server})['ip'].encode(),client)
	except:
		logging.error('connection closed by client')
		return
	try:
		useful['tbd']=time()+60*(randint(int((tmp:=parameters[6][:parameters[6].find('|')].split('-'))[0]),int(tmp[1]))+5)
		logging.info(f'time before Disconnecting {useful["tbd"]}')
	except:
		logging.error('error in Pausing function')	
	def click(cellid,offx=0,offy=0,alt=0,direction=None,c=1,s=0,so=.5):
		try:
			if hasattr(cellid,'__next__'):	cellid=cellid.__next__()
			limit,x,y,line,row={'s':lambda x,odd:(x[0],x[1]+5) if odd else (x[0],x[1]+20) ,'n':lambda x,odd:(x[0],x[1]-27) if odd else (x[0],x[1]-14),'w':lambda x,odd:(x[0]-50,x[1]) if odd else (x[0]-23,x[1]),'e':lambda x,odd:(x[0]+23,x[1]) if odd else (x[0]+50,x[1])},269,16,cellid//14,cellid % 14
			if odd:=line%2:	x+=31
			if direction not in (None,'d'):
				if useful['mapid']==95420418 and direction in ('e','w'):
					alt=12
				elif useful['mapid']==90702849 and direction=='e':
					alt=-16
				elif useful['mapid']==70778880 and direction=='s':
					alt=-14 if odd else -10
				x,y=limit[direction]((x,y),odd)
			elif direction=='d' and useful['mapid'] in (128453121,128452097,128451073):	offx,offy=10,15 
			logging.info(f'Click : {cellid}, {offx}, {offy}, {alt}, {direction} , {x+ceil(row*62.4)+floor(offx*.687)} , {y+floor(15.58*line)+ceil(offy*.55)-9*alt+38}')
			send(b'c\n'+(x+ceil(row*62.4)+floor(offx*.687)).to_bytes(2,'big',signed=True)+b'\n'+(y+floor(15.58*line)+ceil(offy*.55)-9*alt).to_bytes(2,'big',signed=True)+b'\n'+c.to_bytes(2,'big'))
			if s : wait(s,s+so)
		except:
			logging.error(f'Error in click cellid : {cellid} , offx : {offx} , offy : {offy} , altitude : {alt} , direction : {direction}',exc_info=1)

	def send(t,s=.1):
		global connected
		try:
			conn.sendto(t+b'$$$',client)
			sleep(s)
		except:
			connected=False

	def press(k,s=.1,so=.5):
		logging.info('press : '+k)
		send(bytes('p\n'+k,'utf-8'))
		wait(s,s+so)

	def notify(t,s=.5):
		send(b'n\n'+t,s)

	def get_mod_state():
		try:
			return urlopen(Request("https://panel.snowbot.eu/api/moderatorCheckerPC/checkModerator.php?gameServer="+useful["server"]),timeout=1).read()!=b'false'
		except:
			logging.error('Error in get mod state',exc_info=1)
			return False
			
	def check_admin():
		global connected,waitp
		try:
			if parameters[5]!='1':	useful["mod"]=get_mod_state()
			logging.info(f'admin check {useful["threat"]} {useful["mod"]}')
			if useful['reset']:
				logging.warning('reset buffer required Disconnecting')
				send(bytes('o\n'+parameters[1],'utf-8'))
				connected=False
				assert 0
			if useful['threat']:
				send(bytes('a\n'+useful['threat'],'utf-8'),s=7 if useful['threat']=='medium' else 1)
				if useful['threat']=='high':
					logging.warning('disconnected high threat')
					connected=False
					return
				sleep(5)
				useful['threat']=None
			if useful['mod']:
				logging.warning(f"moderator {useful['mod']} in {useful['server']}")
				print('Moderator in ',useful['server'])
				if parameters[5]=='1':	
					useful['mod']=False
					return
				else:
					if parameters[5]=='2':
						send(bytes('a\nmedium','utf-8'),1)
						while useful['mod']:
							useful['mod']=False
							for i in range(150):
								agro(2)
								if useful['threat']:
									check_admin()
									break
							useful["mod"]=f()
					else:
						logging.info('Disconnected')
						send(bytes('d','utf-8'),1)
						connected=False
		except:
			logging.error("Failed checking mods",exc_info=1)

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
		f,g,get=lambda s,t:4*(abs(t[0]-s[0] if t[0]>0 and s[0]>0 or t[0]<0 and s[0]<0 else abs(t[0])+abs(s[0]))+abs(t[1]-s[1] if t[1]>0 and s[1]>0 or t[1]<0 and s[1]<0 else abs(t[1])+abs(s[1]))),lambda x:sample(('n','s','w','e','d'),5) if x else ('n','s','w','e','d'),lambda x:collection.nodes.find_one({'_id':x},{'coord':1,'mapid':1,'n':1,'s':1,'w':1,'e':1,'d':1})
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
								sp.append([d[1],y,p[n]['_id'],p[n+1]['mapid']])
								break
					ret.append(sp)
				logging.info(f'Path directions : {[x[1] for x in ret[0]]}')
				return ret if multipath else ret[0]
			for node in nodes:
				for d in g(shuffle):
					if d=='d':	node[0][-1][d] = {x:y for x,y in node[0][-1][d].items() if y!=-1}#remove unlinked doors
					for k in node[0][-1][d]:
						if node[0][-2 if node[0][-1]['_id']!=start['_id'] else -1]['_id']!=k:
							if k in done:
								wait.insert(0,node[0]+[k])
							else:
								done.add(k)
								heap.insert(0,[node[0]+[neighbor:=get(k)],len(node[0])+f(neighbor['coord'],target['coord'])])
		logging.info('no path found')
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

	def get_current_node(cond=0,mapid=None,pos=None,nested=False):
		global connected
		try:
			# logging.info(f'get current node called {useful["mapid"]} {useful["mypos"]}')
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
			logging.error(f'Error in get_current_node cond : {cond} mapid : {mapid} pos: :{pos} , current mapId {useful["mapid"]} nested {nested}')
			if connected:
				if nested:
					logging.warning('nested get_current_node disconnection')
					connected=False
					send(bytes('o\n'+parameters[1],'utf-8'))
					assert 0
				else:
					press('~',s=.5)
					click(557,offy=150,offx=89,s=1,so=1)
					press('{ENTER 3}',s=1,so=2) 
					if useful['mapid'] in (None,162793472):	
						# useful['mapid']=choice((88085773,128452097,128453121,128451073)) #random maps to avoid no teleporting allowed maps
						logging.warning('no mapid detected reconnecting')
						click(554,offy=120,s=.5)
						press('{VK_ESCAPE}',s=1,so=1)
						click(244,offy=36,s=1,so=1,c=5)
						press('{ENTER 3}',s=10,so=10)
						send(b'r',s=60)
					return get_current_node(cond,mapid,None,True)
			else:
				logging.info('not connected')
				assert 0
			# return notify(bytes(useful['name']+' - '+useful['server']+' : Stack\n'+'get node error','utf8')) if nested else get_current_node(cond,mapid,pos,True)
	
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
			t=[[x,[(y[-1] if insight(y[0][0],y[0][1],x[1],x[2],mat) else y[-1]*-1,y[0][0],y[0][1]) for y in heap]] for x in temp[:hm]]
			#remove loop if you want to avoid going as closer as you can to the enemy
			for x in range(len(t)):
				temp=t[x][1][1:]
				temp.sort(key=lambda e:abs(t[x][0][1]-e[1])+abs(t[x][0][2]-e[2]))
				temp.insert(0,t[x][1][0])
				t[x][1]=temp
			return t
		except:
			logging.error(f'Error in get_closest x0 : {x0} , y0 : {y0}\nuseful : {useful}',exc_info=1)

	def move_fight(c):
		counter=3
		logging.info(f'in move from {useful["mypos"]} to  {c} , mp : {useful["fight"]["mp"]}')
		while counter and c!=useful['mypos'] and useful['fight']['mp']:
			click(c,c=2,s=.8,so=1.5)
			counter-=1
		logging.info(f'move return {useful["mypos"]}')
		return useful['mypos']

	def check_spells(spells,buffs,mat,treasure,hpc,lvl_cond):
		try:
			enter,heal,cast_cooldown=True,False,{k:v['cpt'] for k,v in spells.items()}
			logging.info(f"Turn ({useful['fight']['round']}) : {useful['fight']['enemyteamMembers']} , Ap : {useful['fight']['ap']} , Mp : {useful['fight']['mp']} {useful['lifepoints']} {useful['maxLifePoints']}")
			while useful['infight'] and useful['fight']['ap']>2 and enter and not heal:
				(x0,y0),ok1=switch_coord(p:=useful['mypos']),False
				for y,x,k,v in ((y,x,k,v) for y in get_closest_enemy(x0,y0,[p],mat,useful['fight']['mp']) for k,v in spells.items() for x in y[1]):
					if useful['infight'] and useful['fight']['ap']>2:
						if y[0][0] in useful['fight']['enemyteamMembers'] and (v['range'][1] + (useful['fight']['range'] if v['range'][2] else 0) >= (calc:=abs(x[1]-y[0][1])+abs(x[2]-y[0][2])) and calc >=v['range'][0] and not v['fc'] and (not v['inline'] or x[1]==y[0][1] or x[2]==y[0][2]) and (not v['sight'] or x[0]>-1) and v['ap']<=useful['fight']['ap']):
							if treasure and 'hunt' in useful and useful['fight']['enemyteamMembers'][-1]['lifepoints'] <= hpc:
								logging.info('enemy low health')
								if useful['lifepoints']/useful['maxLifePoints']<.8:
									move_fight(abs(x[0]))
									heal=True
									break
								else:
									if lvl_cond:
										if not buffs['2']['fc']: 
											press('{VK_CONTROL DOWN}')
											press('2')
											buffs['2']['fc']=3
											click(useful['mypos'],offy=-4,s=.4,so=.7)
											press('{VK_CONTROL}')
									elif useful['my_level']>79:
										press('1' if useful['my_level']<174 else '4')
										click(useful['mypos'],offy=-4,s=.5,so=.7)
							if (p:=move_fight(t:=abs(x[0])))!=t:	break
							counter=3
							while useful['infight'] and y[0][0] in useful['fight']['enemyteamMembers'] and counter and v['ap']<=useful['fight']['ap']:
								logging.info(f"enemies {useful['fight']['enemyteamMembers']}")
								logging.info(f'my health {useful["lifepoints"]} {useful["maxLifePoints"]}')
								if treasure and 'hunt' in useful and useful['fight']['enemyteamMembers'][-1]['lifepoints'] <= hpc and useful['lifepoints']/useful['maxLifePoints']<.8:		
									logging.info(f'waiting treasure regen')
									break
								if treasure and 'hunt' in useful and useful['lifepoints']/useful['maxLifePoints']<.25:
									logging.info(f'casting shield')
									if lvl_cond:
										press('{VK_CONTROL DOWN}')
										press('2',s=.8,so=.5)
										click(useful['mypos'],offy=-4,s=.8,so=.5)
										press('{VK_CONTROL}')
										buffs['2']['fc']=3
									else:	
										for _ in range(2):
											press('4' if useful['my_level']>174 else '1',s=.8,so=.9)
											click(useful['mypos'],offy=-4,s=.8,so=.5)
										enter=False
										break
								press(k,s=1)
								ap,counter=useful['fight']['ap'],counter-1
								click(useful['fight']['enemyteamMembers'][y[0][0]]['cellid'],offy=-4,s=1,so=1)
								logging.info(f" Ap : {useful['fight']['ap']} , Mp : {useful['fight']['mp']} {useful['lifepoints']} {useful['maxLifePoints']}")
								if useful['infight'] and ap != useful['fight']['ap']: 
									cast_cooldown[k]-=1
									if not cast_cooldown[k]:
										v['fc']=max(v['recast'],1)
										if k=='1' and y[0][0] in useful['fight']['enemyteamMembers']:
											logging.info('position changed break to redetect')
											ok1=True
										break
							if ok1:	break
					else:	break
				if useful['infight'] and not ok1:
					if (jump_cond:=not buffs['1']['fc'] and buffs['1']['ap']<=useful['fight']['ap']) or heal:
						m=600
						logging.info('enter jump check')
						for y,x,v in ((y,x,v) for y in get_closest_enemy(x0,y0,[p],mat,50,1) for x in y[1] for v in spells.values()) :
							calc=abs(x[1]-y[0][1])+abs(x[2]-y[0][2])
							if mat[abs(x[0])]==2 and x[0]>-1 and v['range'][1] + (useful['fight']['range'] if v['range'][2] else 0)>=calc and (not v['inline'] or x[1]==y[0][1] or x[2]==y[0][2]) and x[0]!=useful['fight']['enemyteamMembers'][y[0][0]]['cellid'] and calc<m:
								m,x1,y1=calc,x[1],x[2]
								if heal and jump_cond or move_fight((t:=get_path(x0,y0,x1,y1,mat))[min(useful['fight']['mp'],len(t)-1)])!=t[-1] and jump_cond:				
									press('{VK_CONTROL DOWN}')
									press('1',s=0.8,so=1)
									press('{VK_CONTROL}')
									(x0,y0)=switch_coord(p:=useful['mypos'])
									temp=get_path(x0,y0,y[0][1],y[0][2],mat)
									t=temp[min(6 if useful['my_level']>132 else 5,len(temp)-2)]
									if t!=useful['mypos']:	
										click(t,offy=-4,s=.8,so=1)
										if useful['mypos']!=t:	click(556,offx=-18,offy=67,c=7,s=.2)
								break
						buffs['1']['fc']=buffs['1']['recast']#force boost
					elif useful['fight']['ap']>1 and not heal and not ok1:
						logging.info('checking available buffs')
						for k,v in buffs.items():
							if k!='1':
								c=v['cpt']
								while not v['fc'] and c and v['ap']<=useful['fight']['ap']:
									press('{VK_CONTROL DOWN}')
									press(k,s=0.8,so=1)
									press('{VK_CONTROL}')
									click(useful['mypos'],offy=-4,s=.8,so=.4)
									v['fc'],c=v['recast'],c-1
						enter=False
			logging.info('passing turn ')
			for xx in (spells,buffs):
				for x in xx.values():
					if x['fc']:
						x['fc']-=1
		except:
			logging.error(f'Error in check_spells\nuseful : {useful}\nspells : {spells}\nbuffs : {buffs}\nmat : {mat}',exc_info=1)
		finally:
			# return {x:spells[x] for x in ['1']+sample([*spells][1:],len(spells)-1)},buffs
			return {x:spells[x] for x in sample([*spells],len(spells))},buffs
	def fight(treasure=False):
		try:
			global connected
			logging.info(f'Fight Started')
			press('{VK_SHIFT}')
			try:
				if not useful['fight']['lock']:
					click(557,offy=20,offx=15,s=1)
					press('{VK_NUMPAD8}')
				# if not useful['fight']['spectator']:	
				# 	click(557,offy=150,offx=14)
					# press('{VK_NUMPAD8}')
				logging.info(f'infight mount {useful["mount"]}')
				if useful['mount'] and not useful['mount']['riding']:	press('{VK_NUMPAD6}')
			except:
				logging.error('lock spec mount error',exc_info=1)
			mat,prev,mapid,hpc=get_current_node(),useful['mypos'],useful['mapid'],useful['fight']['enemyteamMembers'][-1]['lifepoints']*.12
			logging.info(f'Fight mat {mat}')
			try:
				m=600
				for c in useful['fight']['positionsForDefenders'] if useful['fight']['defenderId'] == useful['contextualId'] else useful['fight']['positionsForChallengers']:
					(x0,y0),(x1,y1)=switch_coord(useful['fight']['enemyteamMembers'][-1]['cellid']),switch_coord(c)
					if (calc:=abs(x0-x1)+abs(y0-y1))<m:
						index,m=c,calc
				if prev!= index:	click(index)
			except:
				logging.warning('too late for positioning',exc_info=1)
			lvl_cond=useful['my_level']>164
			spells,buffs= (
							#spells
							{'1': {'range': (1, 5, False),'ap':4, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': True},
							 '2': {'range': (1, 3, False),'ap':3, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': False}}
							 if useful['fight']['ap']<10 else
								{'1': {'range': (1, 5, False),'ap':4, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': True},
								'2': {'range': (1, 4, False),'ap':5, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': False},
								'3': {'range': (1, 3, False),'ap':3, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': False}}
								if useful['my_level']<135 else
								{'1': {'range': (1, 5, False),'ap':4, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': True},
								'2': {'range': (1, 4, False),'ap':5, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': False},
								'3': {'range': (1, 3, False),'ap':3, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': False},
								'4': {'range': (1, 6, False),'ap':4, 'cpt' : 1 , 'recast': 0, 'fc': 0, 'sight': False, 'inline': False}}
								if useful['my_level']<175 else
								{'1': {'range': (1, 5, False),'ap':4, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': True},
								'2': {'range': (1, 4, False),'ap':5, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': False},
								'3': {'range': (1, 3, False),'ap':3, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': False},
								'4': {'range': (1, 1, False),'ap':3, 'cpt' : 2 , 'recast': 0, 'fc': 0, 'sight': True, 'inline': False},
								'5': {'range': (1, 6, False),'ap':4, 'cpt' : 1 , 'recast': 0, 'fc': 0, 'sight': False, 'inline': False}}	 		
						 ,
							#buffs
							{'1' : {'ap':5, 'recast':1,'fc':0,'cpt':1},
							 '2' : {'ap':3, 'recast':3 if lvl_cond else 4,'fc':0,'cpt':1},
							 '3' : {'ap':3, 'recast':0,'fc':0,'cpt':2}
							})
			prev,pc=None,0
			try:
				ap,mp=useful['fight']['ap'],useful['fight']['mp']
			except:
				ap,mp=6,3
				logging.error("wrong stats")
			click(556,offx=-18,offy=67,c=7,s=.2)
			while useful['infight'] and connected:
				press('{F1}')
				counter=5
				while not wait(1,2) and 'turn' in useful['fight'].keys() and not useful['fight']['turn'] and connected and useful['infight'] and (counter:=counter-1):
					if useful['fight']['turn'] is None:	break 
					logging.info('Waiting for turn')
				if useful['fight']['round'] == prev:	
					buf.reset()
					pc+=1
					logging.warning(f'same turn {pc}')
				# if pc > 9 :	useful['infight']=False
				if pc > 3 :
					logging.warning("*** Suicide ***")
					buf.reset()
					press('~',s=1)
					click(557,offy=150,offx=89,s=1,so=1)
					press('{ENTER 3}',s=3,so=3)
					revive()
					send(bytes('o\n'+parameters[1],'utf-8'))
					connected=False
					assert 0
				prev,mpl,decal=useful['fight']['round'],0,0
				if useful['fight']['mplost']:
					for i in range(len(useful['fight']['mplost'])):
						if not useful['fight']['mplost'][i-decal]:
							useful['fight']['mplost'].pop(i-decal)
							decal+=1
						else:
							useful['fight']['mplost'][i-decal]-=1
							mpl+=1
				useful['fight']['mp']=mp-mpl
				useful['fight']['ap']=ap
				spells,buffs=check_spells(spells,buffs,mat,treasure,hpc,lvl_cond)
		except:
			logging.error(f'Error in fight\nuseful : {useful}',exc_info=1)
		finally:
			prev=useful['mypos']
			wait(1,4)
			for _ in range(3):
				click(554,offy=120,s=.5)
				press('~')
			logging.info(f'fight result : {useful["w_l_f"]}')
			return prev

	def move(nid,zaap=False,exit=None,nested=False,harvest=False,passed=False,hint_sleeping=False):
		global connected
		logging.info(f'move to : {nid} , zaap : {zaap} ,exit node : {exit} ,energy : {useful["energy"]}')
		if not connected or not passed and revive()==-1:	assert 0
		if zaap:
			logging.info('checking closest zaap')
			n,m=func(nid),1000
			for x in collection.zaaps.find({}):
				if (calc:=abs(int((c:=x['_id'].split(','))[0])-n['coord'][0])+abs(int(c[1])-n['coord'][1]))<m:
					name,m=x['name'],calc
			while teleport(name,exit):	
				click(80,-21,-10,s=2,so=5)
				# notify(bytes(useful['name']+' - '+useful['server']+' : Stack\n'+'Failed Teleporting','utf8'))
			nid=n['_id']
		for e in (p:=pathfinder((c:=get_current_node(1)),nid,shuffle=False)):
			prev=useful['mapid']
			check_admin()
			if harvest and not nested:
				if (mat:=collect(*harvest[1:]))==-1:
					logging.info('return -1 in collect move')
					return move(collection.nodes.find_one({"_id":nid},{"mapid":1})["mapid"],True)
			if hint_sleeping and useful['mapid'] not in [x['mapId'] for x in useful['hunt']['flags']]:
				logging.info('hint sleeping')
				wait(int((txy:=parameters[4].split('-'))[0]),int(txy[1]))
				hint_sleeping=False
			elif 'hunt' in useful.keys() and random()<0.07 and not useful['map_players'] and not useful['zaap']:
				logging.info('random click')
				click(choice(clean_cells(*all_cells())),s=5,so=5)
			if (cond:= harvest and useful['Harvesting'] and not nested):	press('{VK_SHIFT DOWN}')
			click(cell:=get_closest(e[0],set_mat(e[2])[1],e[1]),direction=e[1])
			if cond:	press('{VK_SHIFT}')
			if cond_wait(['mapid',prev,4,wrapper(click,cell,direction=e[1]),e[2],e[3]])==-1:
				logging.info('Recall move from nested func move')
				if nested:
					logging.info('nested call failed reconnecting ...')
					# notify(bytes(useful['name']+' - '+useful['server']+' : Stack\n'+'nested move error','utf8'))
					send(bytes('o\n'+parameters[1],'utf-8'))
					connected=False
					assert 0
				return move(nid,nested=True)
			if hasattr(exit,'__call__') and not exit():	
				return
		return nid

	def randomteleport():
		try:
			logging.info('random teleport')
			temp=[68552706,88213271,88212759,88212758,88212246,88212247,88080662,73400320,73531904,73400321,73400322,73400323,84935175,147768,147766,145203,146741,146748,144419,144931]
			move(choice(temp),True)
			if useful['map_merchant']:
				logging.info('checking merchant')
				map_clean_cells=clean_cells(*all_cells(),True)
				merchants_cells=[c['cellId'] for c in useful['map_merchant'].values()]
				for _ in range(len(merchants_cells)):
					if (s:=choice(merchants_cells)) in map_clean_cells:
						click(s,s=4,so=8)
						for _ in range(randint(2,6)):	click(74,s=4,so=8)
						counter=5
						while useful['dialog'] and counter:
							click(60,offx=11,offy=-21,s=1,so=2)
							counter-=1
						if not counter and useful['dialog']:
							logging.warning('Disconnecting failed to close merchant dialog')
							send(bytes('o\n'+parameters[1],'utf-8'))
							connected=False
							assert 0
						break
			elif useful['marketplace']:
				logging.info('checking marketplace')
				static_interactives=collection.nodes.find_one({'_id':get_current_node(1)},{'o'})['o']
				for x in static_interactives:
					if x==useful['marketplace']:	
						click(static_interactives[x]-56,s=30,so=60)
						counter=5
						while useful['dialog'] and counter:
							click(23,offy=32,s=2,so=2)
							counter-=1
						if not counter and useful['dialog']:
							logging.warning('Disconnecting failed to close marketplace dialog')
							send(bytes('o\n'+parameters[1],'utf-8'))
							connected=False
							assert 0
						break
			if 'wait' in useful:	agro(randint(50,65)*useful['wait'])
			else:	wait(200,500)
		except:
			logging.error(f'Error in random teleport',exc_info=1)

	def treasure_hunt(supervised=False,harvest=False):
		global connected
		from json import loads,load,dump
		from subprocess import Popen,PIPE,DEVNULL
		def check_hint(j=None,last=True):
			logging.info(f'check hint : offset : {j} last : {last}')
			if j != None:
				flags,i=useful['hunt']['flags'],4
				while (t:=flags==useful['hunt']['flags']) and i:
					if i != 4:	wait((tst:=useful['client_render_time']/2)-2,tst+7) 
					click(70,-118,-12+j*35,s=1.2,so=1)
					i-=1
				if t:
					logging.info(f"failed flag {flags,useful['hunt']['flags']}")
					return
			if last:	click(70,-132,useful['hunt']['totalStepCount']*35-4,c=3,s=2,so=1)
			return True

		def wait_fix():
			logging.info('Wait for hunt fix -> sleeping')
			while (t:=Popen(args='REG QUERY HKCU\Environment /v fix',stdout=PIPE,stderr=DEVNULL).communicate()[0].split(b' ')[-1].decode())[:t.index('\r')]!=name+'-'+server:	agro(10)
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
				if supervised:
					notify(b'TREASER HUNT\nSET CLUE MANUALLY')
					logging.info('SET CLUE MANUALLY')
					wait_fix()
					update_treasure(last:=get_current_node(1),prev,current_coord)
				else:
					logging.info('Trying random fix')
					while useful['hunt']['availableRetryCount']:
						#todo add testing to all nodes in given direction
						last=l[0] if (l:=[*collection.nodes.find_one({'_id':last},{directions[useful['hunt']['currentstep']['direction']][0],'coord'})[directions[useful['hunt']['currentstep']['direction']][0]]]) else [*nwmd][randint(0,len(nwmd)-1)] if (nwmd:=collection.nodes.find_one({'_id':last},{"d",'coord'})["d"]) else -1#temp solution randint to avoid cycle in multi doors node
						if last == -1 :
							logging.critical(f"Force retake in {useful['mapid']} hunt {useful['hunt']}")
							notify(bytes(f"TREASER HUNT\nRETAKE {useful['server'],useful['name'],useful['mapid'],useful['hunt']['currentstep']}",'utf-8'))
							useful["retake"]=True
							del useful["hunt"]
							return
						else:	move(last)
						logging.info(f"Fix {last} {directions[useful['hunt']['currentstep']['direction']][0]} {useful['hunt']}")
						check_hint(j)
						if j!=len(useful['hunt']['flags']):
							logging.info('update called from random fix')
							update_treasure(last,prev,current_coord)
							break
						with open("fix.json","r") as fix_list:
							fix_list,ckey=load(fix_list),str(useful['hunt']['currentstep']['poiLabelId'])
							if (cond:=ckey in fix_list.keys()) and useful['mapid'] in fix_list[ckey]:
								continue
						if useful['hunt']['availableRetryCount']:
							logging.info('adding new map to avoid while fixing')
							fix_list[ckey]=fix_list[ckey]+[useful['mapid']] if cond else [useful['mapid']]
							with open("fix.json","w") as temp:	
								dump(fix_list,temp)
					logging.info(f'currentstep after loop iter {useful["hunt"]["currentstep"]}')
					logging.info(f'return after for loop fix {useful["hunt"]["result"]} {last}')
				logging.info(f'fix return {last} , {useful["hunt"]}')
				return None if 'result' in useful and useful['hunt']['result']==4 else last
			except:
				logging.error('Failed fixing missing clue probably hunt failed',exc_info=True)

		def f(coord,last,d,nested=False):
			logging.info(f"f called with {coord} {last} {d}")
			cur,ret,cont=collection.nodes.find_one({'_id':last},t:={d,'d','coord','mapid','walkable'}),[],0
			if cur['coord']==coord:	return [*cur[d]][randint(0,len(cur[d])-1)]
			def g(snode,nnode):
				if d =='n':	return snode['coord'][1]-nnode['coord'][1]
				if d =='s':	return nnode['coord'][1]-snode['coord'][1]
				if d =='e':	return nnode['coord'][0]-snode['coord'][0]
				if d =='w':	return snode['coord'][0]-nnode['coord'][0]
			while (cur['coord']!=coord and not ret) or cont:
				calc,cont=0,False
				for x in [*cur[d]]:
					tn=collection.nodes.find_one({'_id':x},t)
					if ((l:=len(tn['walkable']))>calc and (tn[d] or tn['d'])) or tn['coord']==coord:
						if tn['coord']==coord:	
							ret.append(tn['_id'])
							cont=True
						cur,calc=tn,l
				if not calc:
					best=-1
					for x,v in cur['d'].items():
						if v!=-1:				
							tn=collection.nodes.find_one({'_id':x},t)
							if (temp:=g(cur,tn)>best) or tn['coord']==coord:
								if tn['coord']==coord:	
									ret.append(tn['_id'])
								cur,best=tn,temp
					if not ret and best==-1:
						if not nested:
							for x in collection.nodes.find({'mapid':collection.nodes.find_one({'_id':last},{'mapid'})['mapid']},{'_id'}):
								if x['_id']!=last:	return f(coord,x['_id'],d,True)
						for x in collection.nodes.find({'coord':coord,'worldmap':1},{'_id':1}):
							if pathfinder(last,x['_id']):
								logging.warning('Doors/Caves possible problem')
								print('Doors/Caves possible problem')
								notify(bytes(f"TREASER HUNT\nSET DOORS/CAVES {useful['server'],useful['name'],last,x['_id']}",'utf-8'))
								ret=[x['_id']]
								break
						# wait_fix()
						# cur=collection.nodes.find_one({'_id':get_current_node(1)},t)
			return [cur['_id']] if not ret else ret	
		e,e1,e2,prev=get_current_node(1,142089230,357),get_current_node(1,128452097,489),get_current_node(1,142088718,356),None
		useful['th_counter']=int(parameters[1])
		if 'hunt' not in useful:
			for j in range(6):	
				click(70,-118,-12+j*35,s=1.2,so=1)
				if 'hunt' in useful:
					if useful['hunt']['flags']:	click(70,-132,useful['hunt']['totalStepCount']*35-4,s=2,so=1)
					break	
			else:
				click(70,-118,-87,s=1,so=1.5)
				press('~',s=1,so=1.2)
		while connected and useful['th_counter']:
			try:
				logging.info(f'Treasure Hunt has began')
				if time()>useful['tbd']:
					logging.info('Pausing function triggred')
					send(bytes('o\n'+parameters[1]+'\n1','utf-8'))
					connected=False
					break
				if (t:=Popen(args='REG QUERY HKCU\Environment /v dofus_stop',stdout=PIPE,stderr=DEVNULL).communicate()[0].split(b' ')[-1].decode())[:t.index('\r')]=='1':	return
				if 'hunt' in useful and  prev==useful['hunt']:	del useful['hunt']
				if 'hunt' not in useful:
					# if not randint(0,1):
						# move(128453121,zaap=True,exit=e)
						# move(e1)
					# else:	move(128452097,zaap=True,exit=e)
					move(128452097,zaap=True,exit=e)
					counter=5
					while 'hunt' not in useful and connected and counter:
						click(554,offy=120)
						click(288,s=.5)
						press('{DOWN}')
						if len(useful['map_players']):
							press('~',s=4,so=3)
						else:
							press('~',s=1,so=3)
							count=10
							while useful['mypos']==304 and 'hunt' not in useful and (count:=count-1):	sleep(.5)
						if 'retake' in useful and useful['retake']:
							click(70,-118,-87,s=1,so=1.5)
							press('~',s=1,so=1.2)
							del useful['retake']
						if 'wait' in useful:
							sleep(randint(55,70)*useful['wait'])
							del useful['wait']
						if not (counter:=counter-1):
							move(e,False,exit=e)
							connected=False
							send(bytes('o\n'+parameters[1],'utf-8'))
							assert 0
					move(e if randint(0,1) else e2,False,exit=e)
					# move(e,False,exit=e)
					wait(4,8)
					prev=useful['hunt']
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
							wait(2,5)
							temp,t,tt,ten=last,{directions[useful['hunt']['currentstep']['direction']][0]:1,"d":1},{directions[useful['hunt']['currentstep']['direction']][0]:1,"d":1,"walkable":1},10
							try:
								while ten:
									calc=0
									for y in t:
										for x in (li:=[*collection.nodes.find_one({'_id':temp},t)[y]]):
											tn,temp=collection.nodes.find_one({'_id':x},tt),x
											if ((l:=len(tn['walkable']))>calc and tn[y] or tn['d']) or len(li)==1:
												temp,calc=x,l
										if 	calc:	break
										elif li:
											temp=li[randint(0,len(li)-1)]
											logging.info(f"guessing {temp} of {li}")
											break
									else: 
										for x in collection.nodes.find({'mapid':useful['mapid']},t):
											if x['_id'] != temp and (x[directions[useful['hunt']['currentstep']['direction']][0]] or x['d']):#vulnerable to 3 + nodes map	
												temp,ten=x['_id'],ten+1
												break
									move(temp,harvest=harvest)
									if useful['hunt']['currentstep']['npcId'] in useful['map_npc']:	break
									ten-=1
								next_node=[temp]
							except:
								logging.info(f'sneaky error abandon hunt {useful["hunt"]}',exc_info=1)
								useful['retake']=True
								del useful['hunt']
								buf.reset()
								assert 0
						logging.info(f'move to {next_node} and flag it')
						if (length:=len(next_node)==1) and next_node[0]==last:
							logging.info('move called on same map call fix')
							check_hint(None,True)
							if 'npcId' in useful['hunt']['currentstep']:
								useful['retake']=True
								del useful['hunt']
							# check_hint(None,True)
							break
						else:
							hint_sleeping=True
							for x in next_node:
								last,prev=move(x,harvest=harvest,hint_sleeping=hint_sleeping),len(useful['hunt']['flags'])
								hint_sleeping=False
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
					click(70,-263,-10)
					wait_check_fight(50,60,Treasure=True)
					if useful['w_l_f']:
						useful['th_counter']-=1
						parameters[1]=str(useful['th_counter'])
					logging.info(f'Treasure hunt remaining before disconnecting : {parameters[1]}')
					wait(int((txy:=parameters[2].split('-'))[0]),int(txy[1]))
					if useful['mount'] and useful['mount']['riding']:	press('{VK_NUMPAD6}')
				else:
					randomteleport()

			except:
				logging.info('Error in Treasure Hunt',exc_info=True)
				randomteleport()

	def generate(cells,direction):
		tres,res=[],[]
		cells=tmp if (tmp:=[x for x in cells if x not in (0,14,532,546,545,559,13,27)]) else cells
		length=len(cells)
		for y in range(10):
			tres.append(cells[y if y < length else randint(0,length-1)])
		for x in tres :
			if direction=='n' and x>3 and x<10 or x>16 and x<24:
				res.append(x)
			elif direction=='s'and x>535 and x<542 or x>548 and x<556:
				res.append(x)
			elif direction=='w' and x>111 and x<421:
				res.append(x)
			elif direction=='e' and x>138 and x<448 :
				res.append(x)
		res= res if res else tres
		return choice(res)

	def get_closest(edge,mat,direction):
		try:
			# generate=lambda cells,length:(x for x in [cells[y if y < length else randint(0,length-1)] for y in range(5)])
			check=lambda cell,index : not (cell%14==13 and index in (5,6) or not ooe and not cell%14 and index in (4,7) or not cell%14 and index==3 or cell%14==13 and index==2)
			calc = lambda cell,index: temp if (temp:=(base[index]+1 if ooe and index in (4,5) else base[index] -1 if not ooe and index>5 else base[index])+cell)>-1 and temp<560 else False
			if direction=='d':
				return generate(edge,direction)
			elif useful['mypos'] in edge:
				return (y if (y:=useful['mypos'] + (x if x <3 else -x+2)*(28 if direction in ('w','e') else 1)) else useful['mypos'] for x in range(5))#check new pos in node edges
			l,base,done,ret=[useful['mypos']],(28,-28,1,-1,13,14,-13,-14),set(),[]
			while l:
				ooe=l[0]//14%2
				for i in range(8): 
					if not check(l[0],i):
						continue
					if not i and not ((t:=calc(l[0],4)) and mat[t]==2 and check(l[0],4) or (t:=calc(l[0],5)) and mat[t]==2 and check(l[0],5)):
						continue
					if i==1 and not ( (t:=calc(l[0],7)) and mat[t]==2 and check(l[0],7) or (t:=calc(l[0],6)) and mat[t]==2 and check(l[0],6)):
						continue
					if i==2 and not ((t:=calc(l[0],6)) and mat[t]==2 and check(l[0],6) or (t:=calc(l[0],5)) and mat[t]==2 and check(l[0],5)):
						continue
					if i==3 and not ((t:=calc(l[0],7)) and mat[t]==2 and check(l[0],7) or (t:=calc(l[0],4)) and mat[t]==2 and check(l[0],4)):
						continue
					next_cell=calc(l[0],i)
					if next_cell  and next_cell not in l and next_cell not in done and mat[next_cell]==2:
						if next_cell in edge:
							ret.append(next_cell)
							if (ll:=len(ret))>=min(10,len(edge)):
								return generate(ret,direction)
						l.append(next_cell)
				done.add(l[0])
				l.pop(0)
			logging.warning(f'out empty in get_closest (cells) current pos {useful["mypos"]} edges : {edge}\nmat : {mat}\ndirection : {direction}')
			return generate(edge,direction)
		except:
			logging.error(f'Error in get_closest (cells) direction : {direction}\nedge : {edge}\nmat : {mat}',exc_info=True)

	def wrapper(fun, *args, **kwargs):
		def wrapped():
			return fun(*args, **kwargs)
		return wrapped

	def teleport(text,exit=None):
		global connected
		logging.info(f'Teleporting to {text}')
		count=randint(2,3)
		while useful['mapid']!=162793472 and connected: 
			click(554,offy=120,s=.5,so=1)
			press('h')
			wait(2,5)
			check_admin()
			if not (count:=count-1):
				buf.reset()
				logging.info('waiting 15-25s before reteleporting')
				wait(15,25)
				if useful['mapid']!=162793472:
					logging.warning(f'Could Not Teleport To HavenBag From This Map {useful["mapid"]} exit node {exit}')
					# notify(bytes(useful['name']+' - '+useful['server']+' : Stack\n'+'Teleport Error','utf8'))
					if revive()==-1:	assert 0
					if exit:	move(exit,exit=wrapper(teleport,text))
					elif useful['disconnect']:
						logging.info(f'attempt before disconnection {useful["disconnect"]}')
						useful['disconnect']-=1
					else:
						logging.warning('Disconnected')
						send(bytes('o\n'+parameters[1],'utf-8'))
						connected=False
						assert 0
					return True
		logging.info(f'Enter Havenbag ,{useful["mapid"]}')
		counter=-1
		while not useful['dialog'] and connected:
			click(173, -10, -10,s=2,so=3)
			if (counter:=counter+1)>=randint(3,5):
				logging.warning(f'teleport counter surpassed {useful["mapid"]}')
				buf.reset()
				if useful['mapid']==162793472:	click(300,s=1,so=3)
				if useful['disconnect']:
					logging.critical(f'attempt before disconnection {useful["disconnect"]}')
					useful['disconnect']-=1
					if useful['disconnect']==1:
						notify(bytes(useful['name']+' - '+useful['server']+' : Stack\n'+'Dialog error','utf8'))
				else:
					logging.warning('Disconnected')
					send(bytes('o\n'+parameters[1],'utf-8'))
					connected=False
					assert 0
				return teleport(text,exit)
		count=randint(2,3)
		logging.info(f'dialog open : {useful["dialog"]}')
		while useful['mapid']==162793472 and connected:
			# click(173, -10, -10,s=2.5,so=3)
			click(135,offy=-10,c=3,s=.8,so=.7)
			for x in text:	press(x,s=.15,so=.25)
			wait(4,7)
			click(175,offy=-5,c=2,s=5,so=.7)
			check_admin()
			if not (count:=count-1):
				logging.warning(f"map is {useful['mapid']} out of Havenbag error")	
				# notify(bytes(useful['name']+' - '+useful['server']+' : Stack\n'+'Out of havenbag error','utf8'))
				buf.reset()
				press('h',s=10)
				buf.reset()
				if useful['disconnect']:
					logging.info(f'attempt before disconnection {useful["disconnect"]}')
					useful['disconnect']-=1
				else:
					send(bytes('o\n'+parameters[1],'utf-8'))
					connected=False
					assert 0
				return useful['mapid']==162793472
		if useful['dialog'] :
			click(80,s=1.2,so=1.3)
		logging.info(f'Done teleporting to {text} current mapid is {useful["mapid"]} poss {useful["mypos"]}')

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
			global connected
			boo=uniform(tmin,tmax)
			while boo>0:
				sleep(1)
				boo-=1
				check_admin()
				if useful['infight'] and cond!=-1:
					pos=fight(treasure=Treasure)
					if revive()==-1:	assert 0
					elif useful['mypos']==pos:
						logging.info('Forced break after fight : character didn\'t do anything')
						return 100
					# press('{VK_SHIFT DOWN}')
					logging.info('fight ended no action needed')
					return 1
		except:
			logging.error(f'Eroor in wait_check_fight {tmin} {tmax} {cond}',exc_info=True)

	def revive():
		try:
			global connected
			if not useful['energy']:
				logging.info('Player became a ghost trying to revive')
				click(554,offy=120,s=.5,so=.8)
				click(370,offx=20,offy=10,s=4,so=4)
				counter=5
				while not useful['phenix'] and counter:
					click(554,offy=120,s=.5)
					click(370,offx=20,offy=10,s=4,so=4)
					for x in ' /release~':	press(x,s=.2,so=.1)
					sleep(5)
					counter-=1
				if not counter:
					logging.warning("failed reviving player no phenix")
					connected=False
					return -1
				logging.info(f"phenix : {useful['phenix']},energy : {useful['energy']}")
				counter=5
				while not useful['energy'] and counter:
					logging.info('no energy reviving')
					click(collection.nodes.find_one({'_id':move(collection.nodes.find_one({'mapid':useful['phenix']},{'_id'})['_id'],passed=True)},{'o'})['o'][useful['phenix_id']],offx=7,offy=-4,s=20)
					counter-=1
				if not counter:
					logging.warning("failed reviving player couldnt rich the phenix")
					connected=False
					send(bytes('d','utf-8'))
					return -1
				click(554,offy=120,s=.5)
				for x in ' /sit~':	press(x,s=.2,so=.15)
				wait(520,700)
		except:
			logging.error(f'failed reviving',exc_info=True)

	def cond_wait(cond):
		global archmonsters
		try:
			tries=0
			tmin,tmax=float((temp:=parameters[3].split('-'))[0]),float(temp[1])
			# if useful['my_level']>160:
			# 	for m in useful["map_mobs"].items():
			# 		if 'info' in m[1].keys():
			# 			for i in m[1]['info']:
			# 				if i[0] in archmonsters.keys():		
			# 					notify(('ArchMonster Found !\nID : %s , Name : %s , Level : %s , Coord : %s'%(name+' - '+server,archmonsters[i[0]],i[1],collection.nodes.find_one({'mapid':useful['mapid']},{'coord':1})['coord'])).encode())
			# 					break
			if (crt:=max(useful['client_render_time'],len(useful['map_players'])))>10:	
				logging.info(f'overloaded map sleeping {crt/2.5} s')
				sleep(crt/2.5)#avoid runtime error on overloaded maps
			while useful[cond[0]] == cond[1] and connected:
				if cond[2]!=-1:
					if tries >= cond[2]:
						logging.info(f'Forced break after timeout , {useful["mapid"]}')
						buf.reset()
						if useful['dialog']:	click(80,s=1,so=1.5)
						# press('{VK_SHIFT}',s=.5)
						# if useful['dialog']:	press('{VK_ESCAPE}',s=1)
						click(554,offy=120,s=.5)
						cond[3]()
						wait_check_fight(tmin,tmax,cond[2])
						if useful[cond[0]] == cond[1]:
							cond[2]-=1
							if not cond[2]:
								logging.critical(f'Breaking from path : something bad happened here {useful["mapid"]} {len(buf)} {len(waitp)}')
								buf.reset()
								return -1
							return cond_wait(cond)	
				if (t:=wait_check_fight(tmin,tmax,cond[2]))==-1:
					return -1
				tries+=t if t else 1
			if useful[cond[0]] != cond[5]:
				if useful["mapid"]==121766912:
					click(269,s=4,so=4)
					click(242,s=4,so=4)
					notify(bytes(useful['name']+' - '+useful['server']+' : Stack\n'+'Weird map','utf8'))
					return -1
				if not useful['w_l_f']:
					logging.info('lost prev fight')
					useful['w_l_f']=True
					return -1
				pcoord=collection.nodes.find_one({'_id':cond[4]},{'coord'})['coord']
				ncoord=collection.nodes.find_one({'mapid':useful[cond[0]]},{'coord'})
				logging.warning(f'Weird teleport {pcoord,ncoord}')
				if ncoord and abs(pcoord[0]-ncoord['coord'][0]) + abs(pcoord[1]-ncoord['coord'][1])<3: 
				# if useful[cond[0]] in [collection.nodes.find_one({'_id':v},{'mapid'})['mapid'] for x in collection.nodes.find_one({'_id':cond[4]},{'n':1,'s':1,'w':1,'e':1,'d':1,'_id':0}).values() for v in x]:
					logging.info('Something went wrong while changing map')
					buf.reset()
					return -1
				elif useful['mapid']!=162793472:
					logging.critical('Moderator teleport check !')
					press(' .~')
					useful['threat']='high'
					check_admin()
		except:
			logging.error(f'Eroor in cond_wait {parameters[3]} {cond}',exc_info=True)

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
		while not useful['mapid'] and connected:	sleep(2)
		logging.info("map changed start leveling up")
		p=[x for x in collection.paths.find_one({'_id':zone},{'nodes'})['nodes']]
		while connected:
			try:
				for n in p:
					if time()>useful['tbd']:
						logging.info('Pausing function triggred')
						send(bytes('o\n'+parameters[1]+'\n1','utf-8'))
						connected=False
						break
					if n!=move(n):	break	
					loop=True
					while loop:
						check_admin()
						temp=deepcopy(useful['map_mobs']).items()
						if useful['lifepoints']/useful['maxLifePoints']<.8:
							st=(useful['maxLifePoints']-useful['lifepoints'])/2
							logging.info(f'☺ sleeping {st}')
							wait(st-5,st+5)
							useful["lifepoints"] = useful["maxLifePoints"]
							logging.info('done sleeping')
						for x,y in temp:
							logging.info(f'{x} {y}')
							if 'alllevel' in y and y['alllevel']<useful['my_level']*threshold and y['cellId'] not in [c['cellId']-28*r for c in useful['map_players'].values() for r in range(2)] and y['cellId'] not in [(c['cellId'] if not mlr else c['cellId']-(14 if (ooe:=c['cellId']//14%2) else 15) if mlr==1 else c['cellId']-(13 if ooe else 14))-28*r for c in useful['map_npc'].values() for mlr in range(3) for r in range(4)]:
								counter,state=4,None
								# press('{VK_SHIFT}',s=.5)
								click(y['cellId'],s=.8,so=.8)
								while not state and counter and x in useful['map_mobs']:
									state=wait_check_fight(1,3)
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
			logging.info(f' collect : {useful["mapid"]} : {useful["resources"]}')
			if not connected:	return
			e,mat=set_mat(key)
			for x in useful['resources'].values():
				if x['enabledSkill'] == 102 and str(x['elementCellId']) not in e:
					e[str(x['elementCellId'])]={"xoffset":0,"yoffset":-5,"altitude":0}
					collection.nodes.update_one({"_id":get_current_node(1)},{'$set':{'interactives':e}})
					logging.info(f'added a well to this map {useful["mapid"]}')
			for c,k in order([(x['enabledSkill'] ,x['elementCellId'],k) for k,x in useful['resources'].items() if (str(x['elementCellId']) in e and 'enabledSkill' in x and x['enabledSkill'] in rsc )],mat,priority):
				if safe_mode and len(useful['map_players']):	break
				if k in useful['resources'] and useful['resources'][k]['elementCellId'] not in [c['cellId']-28*r for c in useful['map_mobs'].values() for r in range(2)] and useful['resources'][k]['elementCellId'] not in [(c['cellId'] if not mlr else c['cellId']-(14 if (ooe:=c['cellId']//14%2) else 15) if mlr==1 else c['cellId']-(13 if ooe else 14))-28*r for c in useful['map_mobs'].values() for mlr in range(3) for r in range(4)]:
					maxi,offx,offy,prev=5,e[(s:=str(c))]['xoffset'],e[s]['yoffset'],useful['mypos']
					if (t:=useful['resources'][k]['enabledSkill']) in exceptions:	offx,offy=offx+exceptions[t][0],offy+exceptions[t][1]				
					click(c, offx, offy, e[s]['altitude'],s=.5)
					while k in useful['resources'] and maxi:
						if safe_mode and len(useful['map_players']) and not useful['infight']:	return mat
						elif (t:=wait_check_fight(1,2.2))==100 or not useful['Harvesting'] and prev==useful['mypos']:
							break
						elif check_inventory() or t==-1:
							logging.info('return -1 in collect')
							return -1
						elif useful['mypos']==c and not useful['Harvesting']:
							notify((f'MISS CLICK WHILE HARVESTING\n{name+"-"+server} fix offset {useful["mapid"]} : {c}').encode())
							break
						maxi-=1
			return mat
		except:
			logging.error(f'Eroor in collect rsc : {rsc}\nkey : {key}\npriority : {priority}\nexceptions : {exceptions}\nuseful : {useful}',exc_info=True)

	def check_inventory():
		try:
			if not connected:	return True
			if useful["full_inventory"] or useful['inventory_weight'] / useful['inventory_max']>.97:
				logging.info(f'Inventory is full {useful["inventory_weight"]}')
				n,m,counter=func(useful['mapid'])['coord'],1000,5
				for x in sample((84935175,99095051,192415750,8914959,8913935,8912911,2885641,2884617,2883593,8129542,91753985,54534165),12):
					if (calc:=abs((c:=func(x)['coord'])[0]-n[0])+abs(c[1]-n[1]))<m:
						name,m=x,calc 	 
				if not move(name,True):
					logging.info(f'Failed emptying inventory from this map{useful["mapid"]}')
					return
				while not useful['dialog']:
					press('{VK_SHIFT}')
					click([*useful['map_npc'].values()][randint(0,len(useful['map_npc'])-1)]['cellId'],offy=-50,s=4,so=3)
				press('{DOWN}',s=.5,so=.8)
				press('~',s=4,so=3)
				for i in range(2):
					click(82,i*20,-7,s=3,so=2)
					click(80,-15,-7,s=.5,so=.8)
					press('{DOWN}{DOWN}~',s=.8,so=.8)
				click(83,8,-50,s=2,so=3)
				useful["full_inventory"]=False
				logging.info(f'Done emptying inventory {useful["inventory_weight"]}')
				return True
		except:
			logging.error(f'Error in check inventory',exc_info=True)

	def harvest(paths,rsc,priority,exceptions,safe_mode):
		try:
			global connected
			logging.info(f'Harvest called with {paths,rsc,priority,exceptions,safe_mode}')
			while not useful['mapid']:	sleep(5)#remove on sub
			while connected:
				for p in sample(paths,len(paths)):
					if not connected:	break
					teleport(collection.zaaps.find_one({'_id':p['zaap']})['name'])
					p,path=[get_current_node(1)]+p['nodes'],[]
					for s in range(len(p)-1):
						path+=pathfinder(p[s],p[s+1])
					for e in path:
						if not connected:	break
						if time()>useful['tbd']:
							logging.info('Pausing function triggred')
							send(bytes('o\n'+parameters[1]+'\n1','utf-8'))
							connected=False
							break
						prev=useful['mapid']
						if (mat:=collect(rsc,priority,exceptions,safe_mode,e[2]))==-1:	break
						if useful['Harvesting']:	press('{VK_SHIFT DOWN}')
						click(cell:=get_closest(e[0],mat,e[1]),direction=e[1])
						if useful['Harvesting']:	press('{VK_SHIFT}')
						if not connected or cond_wait(['mapid',prev,4,wrapper(click,cell,direction=e[1]),e[2],e[3]])==-1:	break
					else:
						collect(rsc,priority,exceptions,safe_mode=safe_mode)
					press('{VK_SHIFT}')
					wait_check_fight(4,4.5)
			logging.info('Done Harvesting')
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
				# logging.info(f'from raw packet {id} {lenData} {len(buf)}')
				if lenData > len(buf) - total:
					raise IndexError
				if id in (6668,6207,7104):
					buf.read(lenData)
					return
				data = Data(buf.read(lenData))
			except IndexError:
				buf.pos = 0
				if useful['reset']:
					logging.warning('reset buffer')
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
			global waitp,connected
			if self.id in msg_from_id:	return msg_from_id[self.id]
			else:	logging.critical(f'Error in start key error {self.id} {useful}')

				

		def json(self):
			if not hasattr(self, "parsed"):
				self.parsed = read(self.msgType, self.data)
			return self.parsed

		@staticmethod
		def from_json(json, count=None, random_hash=True):
			global connected
			try:
				if not json or "__type__" not in json:	return
				type_name: str = json["__type__"]
				type_id: int = types[type_name]["protocolId"]
				data = write(type_name, json, random_hash=random_hash)
				return Msg(type_id, data, count)
			except AttributeError:
				logging.info(f'AttributeError {json}')
				buf.reset()
				waitp=b''
			except:
				logging.critical(f'critical error in from_json hard reset {json} {len(buf)}',exc_info=1)
				# buf.reset()
				# waitp=b''
				if connected:
					send(bytes('o\n'+parameters[1],'utf-8'))
					connected=False

	def on_receive(pa):
		global buf, waitp
		try:
			waitp += pa
			length=int.from_bytes(waitp[:2], 'big')
			# buf += decompress(waitp[2:2+length])
			buf+=waitp[2:2+length]
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
			logging.error("on_receive",exc_info=1)

	def on_msg(msg):
		global buf,waitp,connected
		try:
			Msg.from_json(msg.json())
		except:
			# buf.reset()
			# waitp=b''
			logging.error(f'Error in Start',exc_info=1)
			if connected:
				send(bytes('o\n'+parameters[1],'utf-8'))
				connected=False

			
	def explore():
		try:
			logging.info('exploring zaaps')
			teleport('astrub')
			# while not useful['mapid']:	sleep(5) #remove on money >1000k
			for x in collection.paths.find_one({'_id':"zaaps"},{'nodes'})['nodes']:	
				if x!=(t:=move(x)):
					logging.error(f'couldn\'t finish exploring stop in this node {t}')
					return
		except:
			logging.error('Error in explore',exc_info=1)

	def all_cells():
		try:
			cmap=collection.nodes.find_one({'_id':get_current_node(1)})
			logging.info(f'Agro {cmap["coord"]} {cmap["_id"]}')
			clean=[]
			merchants_cells=[c['cellId'] for c in useful['map_merchant'].values()]
			static_interactives=[c-28*r for c in cmap['o'].values() for r in range(2)]+[(c if not mlr else c-(14 if (ooe:=c//14%2) else 15) if mlr==1 else c-(13 if ooe else 14))-28*r for c in cmap['o'].values() for mlr in range(3) for r in range(4)]
			for c in cmap['walkable']:
				t=False
				for i in ('n','s','w','e','d'):
					for n in cmap[i].values():
						if n !=-1 and c not in n and c not in static_interactives and c not in clean and c not in cmap['interactives'] and c not in merchants_cells:
							clean.append(c)
						else:
							t=True
							break
					if t:	break
			return cmap,clean if useful['mapid']!=88083210 else [90]
		except:
			logging.error('Error in all cells',exc_info=1)

	def clean_cells(cmap,clean,cond=False):
		try:
			tup=('map_mobs','map_npc')
			useful[tup[1]]={k :v if type(v) is dict else {'cellId':v} for k,v in useful[tup[1]].items()}
			all_clean_cells =[c for c in clean if c not in [c['cellId']-28*r for i in tup for c in useful[i].values() for r in range(2)]+[(c['cellId'] if not mlr else c['cellId']-(14 if (ooe:=c['cellId']//14%2) else 15) if mlr==1 else c['cellId']-(13 if ooe else 14))-28*r for i in tup for c in useful[i].values() for mlr in range(3) for r in range(5)]+[c['cellId'] if 'cellId' in c else c['cellid'] for c in useful['map_players'].values()]]
			filtred_cells = [c for c in all_clean_cells if c>154 and c <392 and (tres:=c%14)>3 and tres <10]
			return all_clean_cells if cond or useful['threat'] or len(filtred_cells)<50 else filtred_cells
		except:
			logging.error(f'Error in clean cells {cmap} , {clean}  , {useful["map_players"]}, {useful[tup[0]]} , {useful[tup[1]]}',exc_info=1)
	
	def agro(time):
		try:
			if not connected:	return
			if useful['mapid']==162793472 or not useful['mapid']:
				sleep(time)
				return
			cmap,clean=all_cells()
			logging.info(f'Agro {time} {cmap["coord"]} {cmap["_id"]}')
			while time>0:
				tst=uniform(.2,.45)
				sleep(tst)
				time-=tst
				while useful['agro'] or useful['threat']=='high':
					logging.info(f'agro threat {useful["agro"]}')
					rest=clean_cells(cmap,clean)
					useful['agro'].clear()
					click(choice(rest),s=1.5,so=1)
					time-=1.5
					check_admin()
		except:
			logging.error(f'Error in agro avoider {time}',exc_info=1)

	def seller():
		logging.info('Seller launched')
		def checker(cell,arg):
			while not useful['dialog']:	click(cell,s=5)
			click(47,30,25,s=3)
			for i in range(10):
				prev=useful['inventory'].copy()
				for j in range(5):	click(108,j*62-6,i*78-13,s=.25,so=.75)
				if useful['inventory'] == prev:	break
			press('{VK_ESCAPE}',s=3)
			print(f'  Done checking {arg} marketplace')	
		print('Reloging to detect shortcuts')
		click(554,offy=120,s=.5)
		press('{VK_ESCAPE}',s=1,so=1)
		click(244,offy=36,s=1,so=1,c=5)
		press('{ENTER 3}',s=10,so=10)
		send(b'r',s=60)
		print('Opening chests')
		while useful['shortcuts']:
			for x in useful['shortcuts']:	press(str(x),s=.25,so=.75)
		print('Done opening chests\nChecking marketplace prices')
		# move(73400321,True)
		# checker(261,'consumables')
		# move(get_current_node(1,73400322,17))
		# checker(389,'resource')
		# estimated_prices=[]
		# for x in useful['ready_to_sell']:
		# 	if x['type']=='r':
		# 		price=x['minimalPrices'][0]*.95 if x['quantity']<10 else x['minimalPrices'][1]*.97/10 if x['quantity']<100 else x['minimalPrices'][2]*.99/100
		# 		for y in (1000,100,10,1):
		# 			if (rate:=price/y)>=1:
		# 				rate=round(rate)*y
		# 				break
		# 		else:
		# 			rate=x['minimalPrices'][0]
		# 		estimated_prices.append(str(rate))
		# logging.info(estimated_prices)
		# #move to uncrowded map
		# print('Selling in merchant mode')
		# press('{VK_NUMPAD4}',s=5)
		# click(82,20,-7,s=1)
		# for x in estimated_prices:
		# 	click(108,-6,41,s=.5,so=1)
		# 	press('{BACKSPACE}')
		# 	for y in str(x):	press(y,s=.5)
		# 	press('~')

	def sniffer():
		global connected
		try:
			while connected:	on_receive(conn.recv(8192))
		except Exception as e:
			logging.error(f'Error in sniffer : {e}')
			connected=False
			send(bytes('o\n'+parameters[1],'utf-8'))
	buf,thread=Buffer(),Thread(target=sniffer)	
	thread.start()

	wait(15,45)
	for _ in range(3):	press('~',s=.5,so=1)
	press('{VK_NUMPAD6}',s=1,so=2)
	if useful['mount'] and useful['mount']['riding']:	press('{VK_NUMPAD6}',s=1,so=1)
	for x in ' /solo~':	press(x,s=.2,so=.15)
	if (cond:=parameters[0] =='1' and parameters[7]!='3') or parameters[0]=='2':
		g,param=lambda rsc:[s for r in rsc for x in collection.skills.find({'_id':{'$regex': '^%s.*'%(r),'$options':'i'}}) for s in x['skill_id']],[[y.replace(' ','') for y in x[x.find(':')+1:].split(',')]for x in parameters[7:]]
		param_list=[list(collection.paths.find_one({'$or':[{'_id':{'$regex':f'.*{x}.*','$options':'i'}} for x in param[0]]},{'zaap':1,'nodes':1})),set(g(param[1])),g(param[2]),{x['_id']:[x['offx'],x['offy']] for x in collection.exceptions.find({},{'offx':1,'offy':1})},parameters[7]=='1']
	treasure_hunt(0,param_list if cond else False) if parameters[0]=='1' else harvest(*param_list) if parameters[0]=='2' else level_up(parameters[1]) if parameters[0]=='3' else explore() if parameters[0]=='4' else  seller() if parameters[0]=='5' else logging.error('Wrong algorithm option')
	if thread:	
		connected=False
		thread.join()
	if useful['threat']!='high':	send(bytes('d','utf-8'))
	conn.close()
	logging.info('\n\n\nProcess Terminated\n\n\n')