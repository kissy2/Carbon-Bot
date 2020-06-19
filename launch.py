from utils import fight,get_current_node,click,sleep,switch_coord,get_path,uniform,sample,pathfinder,shortest,collection,app,window,arg,logging,check_admin,check_connection,accounts,thread,Thread,useful
from random import randint
from platform import release
from time import strftime
if release()=='10':
	from win10toast import ToastNotifier
	notify=ToastNotifier()
func=lambda x:collection.nodes.find_one({'mapid':x},{'coord'})

def move(nid,zaap=False,sneaky=None,treasure=False):
	if zaap:
		n,m=func(nid),1000
		for x in collection.zaaps.find({}):
			if (calc:=abs(int((c:=x['_id'].split(','))[0])-n['coord'][0])+abs(int(c[1])-n['coord'][1]))<m:
				name,m=x['name'],calc	
		if teleport(name):
			return
		nid=n['_id']
	for e in (p:=pathfinder((c:=get_current_node(1)),nid,shuffle=False)):
		prev=useful['mapid']
		click(cell:=get_closest(e[0],set_mat(e[2])[1],e[1]),direction=e[1])
		cond_wait(2,2.5,['mapid',prev,4,wrapper(click,cell,direction=e[1]) if e[0]!='d' else wrapper(click,cell,direction=e[1],offx=7,offy=7)])
		if sneaky in useful['map_npc']:
			logging.info(f'Treasure Hunt : sneaky is here {(s:=get_current_node(1))}')
			return s
	if treasure and not p and nid !=c:#remove hunt
		move(128452097,True)
		logging.info('dump hunt')
		while 'hunt' in useful:
			if 'wait' in useful:
				logging.info(f'sleeping in move {useful["wait"]}')
				sleep(60*useful['wait'])
			click(125,offy=-2*35)
			sleep(1)
			app.send_keystrokes('~')
		del useful['wait']
	return nid

def treasure_hunt(lvl=20,supervised=False):
	from urllib.request import urlopen,Request
	from json import loads,load,dump
	def check_hint(j=None,last=True):
		logging.info(f'check hint : offset : {j} last : {last}')
		if j != None:
			flags,i=useful['hunt']['flags'],4
			while (t:=flags==useful['hunt']['flags']) and i:
				click(125,offy=j*35)
				sleep(2)
				i-=1
			if t:
				return
		if last:
			click(125,-14,useful['hunt']['totalStepCount']*35+8)
			sleep(2)
		return True
	def update_treasure(last,hint):
		try:
			logging.info(f'update_treasure called {last} {hint}')
			for d in directions.items():
				start,i=last,10	
				while i and (cur:=collection.nodes.find_one({'_id':start}))[d[1][0]]:
					if last==start:
						x,y=cur['coord'][0],cur['coord'][1]
					for start in cur[d[1][0]]:
						#not ideal check exact path not first node with map change option
						if (cur:=collection.nodes.find_one({'_id':start},{d[1][0],'coord'}))[d[1][0]]:
							break
					else:
						i=1
						logging.info(f'Failed updating out empty after direction {d} last node is {start}')
					logging.info(f'updating {cur["coord"]}')
					if temp2:=collection.treasure.find_one({'_id':(id:=f'{cur["coord"][0]},{cur["coord"][1]}')}):
						if directions[d[0]][2] in temp2:
							for t in temp2[directions[d[0]][2]]:
								if t['id']==hint['poiLabelId']:
									t['x'],t['y']=x,y
									break
							else:
								temp2[directions[d[0]][2]].append({'id':hint['poiLabelId'],'x':x,'y':y})
						else:
							temp2[directions[d[0]][2]]=[{'id':hint['poiLabelId'],'x':x,'y':y}]
						collection.treasure.update_one({'_id':id},{'$set':{directions[d[0]][2]:temp2[directions[d[0]][2]]}})
					else:
						collection.treasure.insert_one({'_id':id},{'$set':{directions[d[0]][2]:[{'id':hint['poiLabelId'],'x':x,'y':y}]}})
					i-=1
			with open('./assets/hints.json', 'r', encoding='utf8') as f:
				a=load(f)+[{'coord':f'{x},{y}','name':collection.named_ids.find_one({'_id':hint['poiLabelId']})['name']}]
			with open('./assets/hints.json', 'w', encoding='utf8') as f:
				dump(a,f)
		except:
			logging.error('Failed updating missing clue',exc_info=True)
	def fix(last):
		try:
			logging.warning(f'Fix : Trying to find the clue in adjacent maps {useful["hunt"]}')
			check_hint()
			last,current_coord,prev,j=(t:=collection.nodes.find_one({'mapid':useful['hunt']['flags'][-1]['mapId'] if useful['hunt']['flags'] else useful['hunt']['startMapId']},{'mapid','coord'}))['_id'],t['coord'],useful['hunt']['currentstep'],len(useful['hunt']['flags'])
			logging.info(f'start node : {last} currentstep : {prev}')
			try:
				logging.info('Try Fix in dofus sama')
				last=move(f([int((t:=(r:=urlopen(Request('https://www.dofusama.fr/treasurehunt/en/search-clue.html', f'direction={useful["hunt"]["currentstep"]["direction"]}&map_pos_x={current_coord[0]}&map_pos_y={current_coord[1]}&map_indice={collection.dofus_sama.find_one({"_id":useful["hunt"]["currentstep"]["poiLabelId"]})["ds_id"]}'.encode('ascii'),headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8'))[(s:=r.index('>[')+2):r.index(']',s)].split(','))[0]),int(t[1])],last,directions[useful['hunt']['currentstep']['direction']][0]))
				check_hint(j)
				logging.info(f'Dofus sama clue in node {last}')
			except:
				if release()=='10':
					notify.show_toast('TREASER HUNT','404 clue')
				logging.warning('Treasure Hunt : Couldn\'t find this clue on dofus sama')
			logging.info(f'currentstep after try {useful["hunt"]["currentstep"]}')
			if  prev!=useful['hunt']['currentstep']:
				logging.info('enter first update')
				update_treasure(last,prev)
				#save id to future update
			elif supervised:
				input('Move to the map that contain the clue ***verify it before*** then press enter')
				update_treasure(last:=get_current_node(1),prev)
			else:
				logging.info('enter for loop fix')
				for _ in range(useful['hunt']['availableRetryCount']):
					#add testing to all nodes in given direction
					last=move([*collection.nodes.find_one({'_id':last},{directions[useful['hunt']['currentstep']['direction']][0],'coord'})[directions[useful['hunt']['currentstep']['direction']][0]]][0])
					logging.info(f"Fix {last} {directions[useful['hunt']['currentstep']['direction']][0]}")
					check_hint(j)
					if prev!=useful['hunt']['currentstep']:
						logging.info('enter second update')
						update_treasure(last,prev)
						break
					logging.info(f'currentstep after for loop iter {useful["hunt"]["currentstep"]}')
				logging.info(f'return after for loop fix {useful["hunt"]["result"]} {last}')
			logging.info(f'fix return {last} , {useful["hunt"]}')
			return None if useful['hunt']['result']==4 else last
		except:
			logging.error('Failed fixing missing clue',exc_info=True)
	def f(coord,last,d):
		cur=collection.nodes.find_one({'_id':last},t:={d,'d','coord'})
		while cur['coord']!=coord:
			for x in [*cur[d]]:
				#not ideal didn't check exact path
				if (cur:=collection.nodes.find_one({'_id':x},t))[d] or cur['coord']==coord:
					break
			else:
				for x in [*cur['d']]:
					if (cur:=collection.nodes.find_one({'_id':x},t))[d] or cur['coord']==coord:##not ideal didn't check 2 straight doors
						break
				else:
					if release()=='10':
						notify.show_toast('TREASER HUNT','SET DOORS/CAVES')
					input(f'Set doors/caves in this map {x} before continuing the hunt : hit enter to continue')
					cur=collection.nodes.find_one({'_id':x},t)##not ideal didn't check 2 straight doors
		return cur['_id']
	while 1:
		try:
			logging.info(f'Treasure Hunt has began')
			if 'hunt' not in useful:
				move(128452097,True)
				while 'hunt' not in useful:
					click(0,-1000)
					click(288)
					sleep(3)
					for _ in range((lvl//20)+1):
						app.send_keystrokes('{UP}')
						sleep(.2)
					app.send_keystrokes('~')
					sleep(7)
					if 'wait' in useful:
						sleep(60*useful['wait'])
			move(get_current_node(1,142089230,357),False)
			directions,last={0:('e','right','4'),4:('w','left','0'),2:('s','bottom','6'),6:('n','top','2')},move(useful['hunt']['flags'][-1]['mapId'] if useful['hunt']['flags'] else useful['hunt']['startMapId'],True,treasure=True)
			while useful['hunt']['checkPointTotal']-useful['hunt']['checkPointCurrent']-1:
				for j in range(len(useful['hunt']['flags']),useful['hunt']['totalStepCount']):
					current_coord,sneaky=collection.nodes.find_one({'_id':last},{'coord':1,'_id':0})['coord'],None
					logging.info(f'current step {useful["hunt"]["currentstep"]}\ncurrent coord {current_coord}')
					if 'poiLabelId' in useful['hunt']['currentstep']:
						logging.info(f'Looking for clue {useful["hunt"]["currentstep"]["poiLabelId"]} on Dofus Map')
						if res:=collection.treasure.find_one({'_id':f'{current_coord[0]},{current_coord[1]}',f'{(d:=str(useful["hunt"]["currentstep"]["direction"]))}.id':useful['hunt']['currentstep']['poiLabelId']},{d}):
							for x in res[d]:
								if x['id']==useful['hunt']['currentstep']['poiLabelId']:
									next_node=f([x['x'],x['y']],last,directions[useful['hunt']['currentstep']['direction']][0])
									logging.info(f'Dofus map clue in this node {next_node}')
									break
						else:
							logging.warning('Treasure Hunt : Couldn\'t find this clue on dofus map')
							if not (last:=fix(last)):
								break
							else:
								continue
					else:
						sneaky,t=useful['hunt']['currentstep']['npcId'],{directions[useful['hunt']['currentstep']['direction']][0]}
						try:
							for _ in range(10):
								for y,x in ((y,x) for y in t for x in [*collection.nodes.find_one({'_id':last},t)[y]]):
									if collection.nodes.find_one({'_id':x},t)[directions[useful['hunt']['currentstep']['direction']][0]]:#not accurate didn't check exact path if multinode or 2 straight doors
										break
								last=x
							next_node=last
						except:
							logging.info('sneaky error')
							break
					logging.info(f'move {next_node} ╔to and flag hint')
					last=move(next_node,sneaky=sneaky)
					if not check_hint(j,False):
						break
				if 'result' in useful['hunt'] and useful['hunt']['result']==4:
					break
				check_hint()
				if useful['hunt']['result']==3:
					logging.warning(f'Wrong clue after for loop\n')
					last=fix(last)
			if useful['hunt']['result']!=4:
				click(125,-145)
				wait_check_fight(3,4,Treasure=True,lvl=lvl)
		except:
			print('Error in Treasure Hunt')
			logging.info('Error in Treasure Hunt',exc_info=True)

def get_closest(edge,mat,direction):
	try:
		if direction=='d':
			return edge[randint(0,len(edge)-1)]
		elif useful['mypos'] in edge:
			return useful['mypos']
		l,base,done,ret=[useful['mypos']],(28,-28,1,-1,13,14,-13,-14),set(),[]
		while l:
			for i in range(8): 
				if (ooe:=l[0]//14%2) and l[0]%14==13 and i in (5,6) or not ooe and not l[0]%14 and i in (4,7) or not l[0]%14 and i==3 or l[0]%14==13 and i==2:
					continue  
				next_cell=(base[i]+1 if ooe and i in (4,5) else base[i] -1 if not ooe and i>5 else base[i])+l[0]
				if next_cell>-1 and next_cell<560  and next_cell not in l and next_cell not in done and mat[next_cell]==2:
					if next_cell in edge:
						ret.append(next_cell)
						if len(ret)>=min(3,len(edge)):
							return ret[randint(0,len(ret)-1)]						
					l.append(next_cell)
			done.add(l[0])
			l.pop(0)
		print('Critical in get_closest (cells) out empty')
		logging.critical(f'out empty in get_closest (cells) current pos {useful["mypos"]} edges : {edge}\nmat : {mat}\ndirection : {direction}')
	except:
		print('Error in get_closest (cells)')
		logging.error(f'Error in get_closest (cells) direction : {direction}\nedge : {edge}\nmat : {mat}',exc_info=True)

def wrapper(fun, *args, **kwargs):
	def wrapped():
		return fun(*args, **kwargs)
	return wrapped

def teleport(text):
	logging.info(f'Teleporting to {text}')
	app.send_keystrokes('{VK_SHIFT}')
	app.send_message(257,16)
	app.send_keystrokes('^{ }')
	sleep(1)
	app.send_keystrokes('^{a}')
	sleep(1)
	app.send_keystrokes('{BACKSPACE}')
	while useful['dialog']:
		app.send_keystrokes('{VK_ESCAPE}')
		sleep(5)
	count=5
	while useful['mapid']!=162793472 and not check_connection():
		click(0,-1000)
		sleep(1)
		app.send_keystrokes('h')
		wait_check_fight(4,5)
		check_admin()
		if not (count:=count-1):
			logging.warning(f'Could Not Teleport To HavenBag From This Map{useful["mapid"]}')
			return True
	logging.info(f'Enter Havenbag ,{useful["mapid"]}')
	counter=0
	while not useful['dialog'] and not check_connection():
		click(173, -10, -10)
		sleep(uniform(2.5,3.5))
		if counter>5:
			logging.warning('teleport counter surpassed')
			app.send_keystrokes('{VK_SHIFT}')
			app.send_message(257,16)
			click(300)
		counter+=1
	while useful['mapid']==162793472 and not check_connection():
		click(134,offy=-10)
		sleep(1)
		app.send_keystrokes('^{a}{BACKSPACE}')
		sleep(1)
		app.send_keystrokes(text)
		sleep(3)
		app.send_keystrokes('~')
		sleep(5)
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
		print('Error in check_adjc')
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
		print('Error in order')
		logging.error(f'Eroor in order list : {li}\npriority : {priority}\nmat : {mat}',exc_info=True)

def wait_check_fight(tmin,tmax,cond=0,Treasure=False,lvl=20):
	try:
		sleep(uniform(tmin,tmax))
		check_admin()
		if useful['infight'] and cond!=-1:
			pos=fight(treasure=Treasure,lvl=lvl)
			if not useful['fight']['alive']:
				logging.info('Fight Lost')
				sleep(uniform(7,15))
				while useful['energy'] == 0:
					logging.info('Player became a ghost trying to revive')
					app.send_keystrokes('{VK_ESCAPE}{ENTER 3}')
					sleep(2)
					while not useful['phenix']:
						app.send_keystrokes('^{ }')
						sleep(1)
						app.send_keystrokes('^{a}')
						sleep(1)
						app.send_keystrokes('/release~')
						sleep(5)
					click(collection.nodes.find_one({'_id':move(collection.nodes.find_one({'mapid':useful['phenix']},{'_id'})['_id'])},{'o'})['o'][useful['phenix_id']])
					sleep(uniform(5,10))
					app.send_keystrokes('{VK_NUMPAD6}')
				return -1
			elif useful['mypos']==pos:
				logging.info('Forced break after fight : character didn\'t do anything')
				return 100
			app.send_keystrokes('{VK_SHIFT DOWN}')
			logging.info('fight ended no action needed')
			return 1
	except:
		print('Error in wait_check_fight')
		logging.error(f'Eroor in wait_check_fight {tmin} {tmax} {cond}',exc_info=True)

def cond_wait(tmin,tmax,cond):
	try:
		tries=0
		while useful[cond[0]] == cond[1]:
			if cond[2]!=-1 :
				if check_connection():
					return -1
				if tries >= cond[2]:
					logging.info(f'Forced break after timeout , {useful["mapid"]}')
					app.send_message(257,16)
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
		print('Error in cond_wait')
		logging.error(f'Eroor in cond_wait {tmin} {tmax} {cond}',exc_info=True)

def check_arch(l):
	while 1:
		cond_wait(2,3,['mapid',useful['mapid'],-1])
		for m in useful["map_mobs"].items():
			if 'info' in m[1].keys():
				for i in m[1]['info']:
					if i[0] in l.keys():
						with open('ArchMonsters.txt','r+') as f:
							c,r=collection.nodes.find_one({'mapid':useful['mapid']},{'coord':1})['coord'],f.read()
							f.seek(0)
							f.write('%s , Server : %s , Name : %s , Level : %s , Coord : %s\n'%(strftime("%A, %d %B %Y %I:%M %p"),arg['server'],l[i[0]],i[1],c)+r)
							if release()=='10':
								notify.show_toast(title='ArchMonster Found !',msg='Server : %s\nName : %s\nLevel : %s\nCoord : %s'%(arg['server'],l[i[0]],i[1],c),duration=50,threaded=True)

def set_mat(key):
	try:
		if not key:
			t=get_current_node(2)
		else:
			t=collection.nodes.find_one({'_id':key},{'interactives':1,'walkable':1,'_id':0})
		return t['interactives'],[2 if x in t['walkable'] else 0 for x in range(560)]
	except:
		print('Error in set_mat')
		logging.error(f'Eroor in set_mat the key was : {key}',exc_info=True)

def collect(rsc,priority,exceptions,key=None):
	try:
		e,mat=set_mat(key)
		app.send_keystrokes('{VK_SHIFT DOWN}')
		for c,k in order([(x['enabledSkill'] ,x['elementCellId'],k) for k,x in useful['resources'].items() if (str(x['elementCellId']) in e and 'enabledSkill' in x and x['enabledSkill'] in rsc )],mat,priority):
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
						# notify.show_toast('miss_click',arg['server'])
						# app.set_focus()
						break
					maxi-=1
		return mat
	except:
		print('Error in collect')
		logging.error(f'Eroor in collect rsc : {rsc}\nkey : {key}\npriority : {priority}\nexceptions : {exceptions}\nuseful : {useful}',exc_info=True)


def check_inventory():
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
			app.send_keystrokes('{VK_SHIFT}')
			app.send_message(257,16)
			click([*useful['map_npc'].values()][randint(0,len(useful['map_npc'])-1)]['cellId'],offy=-50)
			sleep(5)
		app.send_keystrokes('{DOWN}')
		sleep(1)
		app.send_keystrokes('~')
		sleep(5)
		for i in range(2):
			click(82,i*20,-7)
			sleep(5)
			click(80,-15,-7)
			sleep(1)
			app.send_keystrokes('{DOWN}{DOWN}~')
			sleep(5)
		click(0,-1000)
		sleep(.5)
		app.send_keystrokes('{VK_ESCAPE}')
		sleep(5)
		useful["full_inventory"]=False
		logging.info(f'Done emptying inventory {useful["inventory_weight"]}')
		return True

def execute(paths_names, rsc=[], priority=[] ,check_archi=True):
	try:
		print('CARBON BOT IS RUNNING ...')
		logging.info('\n\n*****CARBON BOT IS LAUNCHED*****\n\n')
		g=lambda rsc:[s for r in rsc for x in collection.skills.find({'_id':{'$regex': '^%s.*'%(r),'$options':'i'}}) for s in x['skill_id']]
		paths,rsc,priority,exceptions=list(collection.paths.find({'$or':[{'_id':{'$regex':f'.*{x}.*','$options':'i'}} for x in paths_names]},{'zaap':1,'nodes':1})),set(g(rsc)),g(priority),{x['_id']:[x['offx'],x['offy']] for x in collection.exceptions.find({},{'offx':1,'offy':1})}
		if (l:=len(paths)) and check_archi:
			Thread(target=check_arch,args=[{x['raceid']:x['_id'] for x in collection.archmonsters.find({})}]).start()
		while 1:
			logging.info('Start rotation')
			for p in sample(paths,l):
				teleport(collection.zaaps.find_one({'_id':p['zaap']},{'name':1,'_id':0})['name'])
				p,path=[get_current_node(1)]+p['nodes'],[]
				for s in range(len(p)-1):
					path+=pathfinder(p[s],p[s+1])
				for e in path:
					prev=useful['mapid']
					if (mat:=collect(rsc,priority,exceptions,e[2]))==-1:
						break
					click(cell:=get_closest(e[0],mat,e[1]),direction=e[1])
					if cond_wait(2,2.5,['mapid',prev,4,wrapper(click,cell,direction=e[1])])==-1:
						break
					logging.info(f'map changed from {prev} to {useful["mapid"]}')
				else:
					collect(rsc,priority,exceptions)
				wait_check_fight(4,4.5)
			logging.info('Done rotation')
		logging.info('CARBON BOT HAS STOPPED ')
	except:
		print("An Error Occured in Excecute Check log file!!!!")
		logging.error(f'Error in execute but why',exc_info=True)

def xp(zone='xp_incarnam',threshold=1):
	from copy import deepcopy
	useful['my_level']=int(input('change map then enter your level : '))
	p=[x for x in collection.paths.find_one({'_id':{'$regex':f'.*{zone}.*','$options':'i'}})['nodes']]
	while 1:
		for n in p:
			for e in pathfinder(get_current_node(1),n):
				prev=useful['mapid']
				click(cell:=get_closest(e[0],set_mat(None)[1],e[1]),direction=e[1])
				if cond_wait(2,2.5,['mapid',prev,4,wrapper(click,cell,direction=e[1])])==-1:
					print('something went wrong')
					break
				loop=True
				while loop:
					temp=deepcopy(useful['map_mobs']).items()
					if useful['lifepoints']/useful['maxLifePoints']<.8:
						app.send_keystrokes('^{ }')
						wait_check_fight(.75,1)
						app.send_keystrokes('^{a}{BACKSPACE}')
						wait_check_fight(.75,1)
						app.send_keystrokes('/sit~')
						logging.info('sleeping')
						sleep((useful['maxLifePoints']-useful['lifepoints'])/2.5)
						logging.info('done sleeping')
						useful['lifepoints']=useful['maxLifePoints']
					for x,y in temp:
						if 'alllevel' in y and y['alllevel']<useful['my_level']*threshold:
							counter,state=4,None
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


# execute(arg['path'].split(','),arg['resource'].split(','),arg['priority'].split(','))
treasure_hunt(200 if arg['name']=='Unfriendly' else 140,False)
# xp('astrub_fields')

# useful={'hunt':{'currentstep':{'__type__': 'TreasureHuntStepFollowDirectionToHint', 'direction': 0, 'npcId': 2669}}}
# directions={0:('e','right','4'),4:('w','left','0'),2:('s','bottom','6'),6:('n','top','2')}
# sneaky,t=useful['hunt']['currentstep']['npcId'],{directions[useful['hunt']['currentstep']['direction']][0],'d'}
# last="6127"
# for _ in range(10):
# 	for y,x in ((y,x) for y in t for x in [*collection.nodes.find_one({'_id':last},t)[y]]):
# 		if collection.nodes.find_one({'_id':x},t)[directions[useful['hunt']['currentstep']['direction']][0]]:#not accurate didn't check exact path if multinode or 2 straight doors
# 			break
# 	last=x
# next_node=last
# print(next_node)

# from urllib.request import urlopen,Request
# useful={'hunt':{'currentstep':{'__type__': 'TreasureHuntStepFollowDirectionToHint', 'direction': 0, 'npcId': 2669}}}
# directions={0:('e','right','4'),4:('w','left','0'),2:('s','bottom','6'),6:('n','top','2')}
# # sneaky,t=useful['hunt']['currentstep']['npcId'],{directions[useful['hunt']['currentstep']['direction']][0]}
# last="6127"
# def f(coord,last,d):
# 	cur=collection.nodes.find_one({'_id':last},t:={d,'d','coord'})
# 	while cur['coord']!=coord:
# 		print(cur['coord'])
# 		for x in [*cur[d]]:
# 			#not ideal didn't check exact path
# 			if (cur:=collection.nodes.find_one({'_id':x},t))[d] or cur['coord']==coord:
# 				break
# 		else:
# 			for x in [*cur['d']]:
# 				if (cur:=collection.nodes.find_one({'_id':x},t))[d] or cur['coord']==coord:##not ideal didn't check 2 straight doors
# 					break
# 			else:
# 				if release()=='10':
# 					notify.show_toast('TREASER HUNT','SET DOORS/CAVES')
# 				input(f'Set doors/caves in this map {x} before continuing the hunt : hit enter to continue')
# 				cur=collection.nodes.find_one({'_id':x},t)##not ideal didn't check 2 straight doors
# 	return cur['_id']
# current_coord=[4, 13]
# print([int((t:=(r:=urlopen(Request('https://www.dofusama.fr/treasurehunt/en/search-clue.html', f'direction={useful["hunt"]["currentstep"]["direction"]}&map_pos_x={current_coord[0]}&map_pos_y={current_coord[1]}&map_indice={collection.dofus_sama.find_one({"_id":useful["hunt"]["currentstep"]["poiLabelId"]})["ds_id"]}'.encode('ascii'),headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8'))[(s:=r.index('>[')+2):r.index(']',s)].split(','))[0]),int(t[1])])
# last=f([int((t:=(r:=urlopen(Request('https://www.dofusama.fr/treasurehunt/en/search-clue.html', f'direction={useful["hunt"]["currentstep"]["direction"]}&map_pos_x={current_coord[0]}&map_pos_y={current_coord[1]}&map_indice={collection.dofus_sama.find_one({"_id":useful["hunt"]["currentstep"]["poiLabelId"]})["ds_id"]}'.encode('ascii'),headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8'))[(s:=r.index('>[')+2):r.index(']',s)].split(','))[0]),int(t[1])],last,directions[useful['hunt']['currentstep']['direction']][0])
# print(last)
# click(496)
# import utils2
# while 1 :
# 	input('wait')
# 	print(useful['fight']['range'])
# 	wait_check_fight(1,2)
# 	print(useful['hunt'])

# directions={0:('e','right','4'),4:('w','left','0'),2:('s','bottom','6'),6:('n','top','2')}
# useful['hunt']={'currentstep':{'__type__': 'TreasureHuntStepFollowDirectionToPOI', 'direction': 0, 'poiLabelId': 48}}
# last="5231"
# current_coord=[-22,34]


# from urllib.request import urlopen,Request,build_opener,HTTPCookieProcessor

# b=build_opener(HTTPCookieProcessor())

# r=b.open(Request('https://vente.tryandjudge.com/dofuskamas.php',headers={'User-Agent': 'Mozilla/5.0'}))
# print(r.headers)
# h=""
# for x in .items():
# 	h+=x[0]+'='+x[1]+"&"
# print(h)
# import requests
# page = requests.get('https://vente.tryandjudge.com/dofuskamas.php')
# print(page.headers)
# print(page.text)
# print(r.read().decode('utf-8'))
