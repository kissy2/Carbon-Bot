from time import localtime,strftime
from utils import fight,get_current_node,click,sleep,switch_coord,get_path,uniform,sample,pathfinder,shortest,collection,app,window,arg,logging
from random import randint
from start import sniff,Raw,on_receive,on_msg,useful
from threading import Thread
from win10toast import ToastNotifier
notify,first_fight=ToastNotifier(),True

def get_closest(edge,mat,direction):
	try:
		if direction=='d':
			return edge[randint(0,len(edge)-1)]
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
		logging.critical(f'out empty in get_closest current pos {useful["mypos"]}')
	except:
		print('Error in check_spells')
		logging.error(f'Error in get_closest direction : {direction}\nedge : {edge}\nmat : {mat}',exc_info=1)

def wrapper(func, *args, **kwargs):
	def wrapped():
		return func(*args, **kwargs)
	return wrapped

def teleport(text):
	app.send_keystrokes('{VK_SHIFT}')
	click(0,-1000)
	logging.info(f'Teleporting to {text}')
	try:
		call,prev=wrapper(teleport,text),useful['mapid']
		app.send_keystrokes('h')
		if cond_wait(1.5,2.5,['mapid',prev,5,call]):
			return
		logging.info(f'Enter Havenbag ,{useful["mapid"]} is it though ?')
		click(173, offx=-10, offy=-10)
		sleep(uniform(2.5,3.5))
		click(134,offy=-10)
		sleep(.25)
		app.send_keystrokes(text+'~', with_spaces=True)
		if cond_wait(3,5,['mapid',162793472,5,call]):
			return
	except RuntimeError:
		logging.error('RuntimeError in teleport')
		sleep(uniform(3,5))
		teleport(text)
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
		logging.error(f'Eroor in check_adjc pos : {pos}\nlist : {l}\nmat : {mat}',exc_info=1)

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
		logging.error(f'Eroor in sub_order pos : {pos}\nlist : {li}\nmat : {mat}',exc_info=1)

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
		logging.error(f'Eroor in order list : {li}\npriority : {priority}\nmat : {mat}',exc_info=1)

def wait_check_fight(tmin,tmax,cond=0):
	try:
		global first_fight
		sleep(uniform(tmin,tmax))
		if useful['infight'] and cond!=-1:
			app.send_keystrokes('{VK_SHIFT}')
			pos=fight(first_fight)
			app.send_keystrokes('{VK_SHIFT DOWN}')
			first_fight=False
			if not useful['fight']['alive']:
				logging.critical('Fight Lost')
				sleep(30)
				return -1
			elif useful['mypos']==pos:
				logging.info('Forced break after fight : character did not move')
				return 100
			logging.info('simple fight ended')
		return 1
	except:
		print('Error in wait_check_fight')
		logging.error(f'Eroor in wait_check_fight {tmin} {tmax} {cond}',exc_info=1)

def cond_wait(tmin,tmax,cond):
	try:
		tries=0
		while useful[cond[0]] == cond[1]:
			if cond[2]!=-1 and tries >= cond[2]:
				logging.info(f'Forced break after timeout , {useful["mapid"]}')
				app.send_keystrokes('{VK_SHIFT}')
				cond[3]()
				sleep(2)
				if useful[cond[0]] == cond[1]:
					cond[2]-=1
					if not cond[2]:
						logging.critical(f'Break from path : something bad happened here {useful["mapid"]}')
						return -1
					return cond_wait(tmin,tmax,cond)
				return True	
			if window.name and window.name[0:5]=='Dofus':
				logging.critical('Disconnected : Trying to reconnect every 2 minutes')
				sleep(120)
				app.send_keystrokes('~')
				sleep(120)
				app.send_keystrokes('~')
				sleep(120)
				return -1
			elif (t:=wait_check_fight(tmin,tmax,cond[2]))==-1:
				return t
			tries+=t
	except:
		print('Error in cond_wait')
		logging.error(f'Eroor in cond_wait {tmin} {tmax} {cond}',exc_info=1)

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
							f.write('%s : Name : %s , Level : %s , Coord : %s\n'%(strftime("%A, %d %B %Y %H:%M:%S", localtime()),l[i[0]],i[1],c)+r)
							notify.show_toast(title='ArchMonster Found !',msg='Name : %s\nLevel : %s\nCoord : %s'%(l[i[0]],i[1],c),duration=600,threaded=True)

def set_mat(key):
	try:
		if not key:
			t=get_current_node(2)
		else:
			t=collection.nodes.find_one({'_id':key},{'interactives':1,'walkable':1,'_id':0})
		return t['interactives'],[2 if x in t['walkable'] else 0 for x in range(560)]
	except:
		print('Error in set_mat')
		logging.error(f'Eroor in set_mat the key was : {key}',exc_info=1)

def collect(rsc,priority,exceptions,key=None):
	try:
		e,mat=set_mat(key)
		app.send_keystrokes('{VK_SHIFT DOWN}')
		for c,k in order([(x['enabledSkill'] ,x['elementCellId'],k) for k,x in useful['resources'].items() if (str(x['elementCellId']) in e and x['enabledSkill'] in rsc )],mat,priority):
			if k in useful['resources']:
				maxi,offx,offy=10,e[(s:=str(c))]['xoffset'],e[s]['yoffset']
				if (t:=useful['resources'][k]['enabledSkill']) in exceptions:
					offx,offy=offx+exceptions[t][0],offy+exceptions[t][1]
				click(c, offx, offy, e[s]['altitude'])
				while k in useful['resources'] and maxi:
					if (t:=wait_check_fight(.5,1))==100:
						break
					elif t==-1:
						return t
					maxi-=t
		return mat
	except:
		print('Error in collect')
		logging.error(f'Eroor in collect rsc : {rsc}\nkey : {key}\npriority : {priority}\nexceptions : {exceptions}\nuseful : {useful}',exc_info=1)

def get_closest_zaap(mapid):
	n,m=collection.nodes.find_one({'mapid':mapid},{'coord':1}),1000
	for x in collection.zaaps.find({}):
		c=x['_id'].split(',')
		if (calc:=abs(int(c[0])-n['coord'][0])+abs(int(c[1])-n['coord'][1]))<m:
			name,m=x['name'],calc 	
	teleport(name)
	return n['_id']

def move(nid,zaap=False,sneaky=None):
	if zaap:
		nid=get_closest_zaap(nid)
	for e in pathfinder(get_current_node(1),nid):
		click(cell:=get_closest(e[0],set_mat(e[2])[1],e[1]),direction=e[1])
		cond_wait(2,2.5,['mapid',useful['mapid'],4,wrapper(click,cell,direction=e[1])])
		if sneaky in useful['map_npc']:
			print("sneaky bro ?")
			break
	return nid

def treasure_hunt():
	g=lambda x,y,d,ofs: [x+ofs,y] if d==0 else [x-ofs,y] if d==4 else [x,y+ofs] if d==2 else [x,y-ofs]
	last=move(useful['hunt']['startMapId'],True)
	for _ in range(useful['hunt']['checkPointTotal']):
		for j in range(useful['hunt']['totalStepCount']):
			current_node,sneaky=collection.nodes.find_one({'_id':last},{'coord':1,'_id':0})['coord'],None
			if 'poiLabelId' in useful['hunt']['currentstep']:
				for x in collection.treasure.find_one({'_id':f'{current_node[0]},{current_node[1]}'},{(s:=str(useful['hunt']['currentstep']['direction'])):1,'_id':0})[s]:
					if x[0]==useful['hunt']['currentstep']['poiLabelId']:
						new_coord=g(current_node[0] ,current_node[1],useful['hunt']['currentstep']['direction'],x[1])
						break
				else:
					notify.show_toast('tnikna')
			else:
				new_coord,sneaky=g(current_node[0] ,current_node[1],useful['hunt']['currentstep']['direction'],10),useful['hunt']['currentstep']['npcId']
			move(collection.nodes.find_one({'worldmap':1,'coord':new_coord},{'_id':1})['_id'],sneaky=sneaky)


def check_inventory():
	if useful['inventory_weight'] / useful['inventory_max']>.9:
		logging.info(f'Inventory is full {useful["inventory_weight"]}')
		move(84935175,True)
		click(330,offy=-20)
		sleep(2)
		app.send_keystrokes('{DOWN}')
		sleep(2)
		app.send_keystrokes('~')
		sleep(3)
		click(80,offx=40,offy=-7)
		sleep(1)
		click(80,offx=-15,offy=-7)
		sleep(1)
		app.send_keystrokes('{DOWN}')
		sleep(1)
		app.send_keystrokes('~')
		sleep(1)
		app.send_keystrokes('{VK_ESCAPE}')
		logging.info(f'Done emptying inventory {useful["inventory_weight"]}')

def execute(paths_names, rsc=[], priority=[] ,check_archi=True, rotation=-1):
	try:
		logging.info('CARBON BOT IS LAUNCHED')
		Thread(target=sniff, kwargs={'filter':f'ip host {collection.servers.find_one({"_id":arg["server"]},{"_id":0})["ip"]} and tcp port {arg["port"]}', 'lfilter':lambda p: p.haslayer(Raw),'prn':lambda p: on_receive(p, on_msg)}).start()
		# cond_wait(5,10,('lifepoints',1,20,wrapper(notify.show_toast,title='Script Eroor',msg='Could Not Hook Game Process',duration=1000)))
		g=lambda rsc:[s for r in rsc for x in collection.skills.find({'_id':{'$regex': '^%s.*'%(r),'$options':'i'}}) for s in x['skill_id']]
		paths,rsc,priority,exceptions=list(collection.paths.find({'$or':[{'_id':{'$regex':f'.*{x}.*','$options':'i'}} for x in paths_names]},{'zaap':1,'nodes':1})),set(g(rsc)),g(priority),{x['_id']:[x['offx'],x['offy']] for x in collection.exceptions.find({},{'offx':1,'offy':1})}
		if (l:=len(paths)) and check_archi:
			Thread(target=check_arch,args=[{x['raceid']:x['_id'] for x in collection.archmonsters.find({})}]).start()
		while rotation:
			for p in sample(paths,l):
				teleport(collection.zaaps.find_one({'_id':p['zaap']},{'name':1,'_id':0})['name'])
				p,path=[get_current_node(1)]+p['nodes'],[]
				for s in range(len(p)-1):
						path+=pathfinder(p[s],p[s+1])
				for e in path:
					prev=useful['mapid']
					if (mat:=collect(rsc,priority,exceptions,e[2]))==-1:
						break
					logging.info(f'preclick get_closest args current node : {e[2]} edges : {e[0]}\nmat : {mat}\ndirection : {e[1]}')
					cell=get_closest(e[0],mat,e[1])
					click(cell,direction=e[1])
					logging.info(f'get_closest return is {cell}')
					if (mat:=cond_wait(2,2.5,['mapid',prev,4,wrapper(click,cell,direction=e[1])]))==-1:
						break
					logging.info(f'map changed from {prev} to {useful["mapid"]}')
				if mat !=-1:
					collect(rsc,priority,exceptions)
					wait_check_fight(4,5)
				check_inventory()
			rotation-=1
		print("Done all rotations with success")
	except:
		print("An Error Occured in Excecute Check log file!!!!")
		logging.error(f'Error in execute but why',exc_info=1)


execute(paths_names=['icefish','aspen','elm','holy','rice','rye'],
		rsc=['nettle','ginseng','belladonna','rice','ray','sage','flax','rye','pandkin','silicate','lard','sickle','elm','aspen','hornbeam','icefish','tench','cod','holy','swordfish','monkfish','perch','Edelweiss','kaliptus','cherry'],
		priority=['elm','aspen,','holy','kaliptus','cherry','tench','swordfish','icefish'])

# h=pathfinder('9334','9346')
# print([x[1] for x in h])
# for x in h:
# 	print(x[0])
# Thread(target=sniff, kwargs={'filter':f'ip host {collection.servers.find_one({"_id":arg["server"]},{"_id":0})["ip"]} and tcp port {arg["port"]}', 'lfilter':lambda p: p.haslayer(Raw),'prn':lambda p: on_receive(p, on_msg)}).start()
# input('press')
# edge =[11, 12, 25]
# mat = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2]
# mat=set_mat(None)[1]
# direction ='n'
# print(get_closest(edge,mat,direction))
# import utils2
# click(173,-2,-20)