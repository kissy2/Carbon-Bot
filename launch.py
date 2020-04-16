from time import localtime,strftime
from utils import fight,get_current_node,click,sleep,uniform,sample,pathfinder,shortest,collection,app
from random import randint
from start import sniff,Raw,on_receive,on_msg,useful
from threading import Thread
from win10toast import ToastNotifier
notify,first_fight=ToastNotifier(),True

def get_closest(edge, pos , direction):
	ret,length=[],len(edge)
	for j in range(min(5,length)):
		m=600
		for i in range(length):
			if (dist:=abs(edge[i]%14-pos%14 if direction in ('n','s') else edge[i]//14-pos//14)) < m:
				if j and prev-dist>5:
					continue
				index,m=i,dist
		ret.append(edge[index])
		edge.pop(index)
		length-=1
		if not j:
			prev=m
	return ret[randint(0,len(ret)-1)]

def wrapper(func, *args, **kwargs):
	def wrapped():
		return func(*args, **kwargs)
	return wrapped

def teleport(text):
	print("teleport",text)
	try:
		call,prev=wrapper(teleport,text),useful['mapid']
		app.send_keystrokes('h')
		if cond_wait(1.5,2.5,('mapid',prev,5,call)):
			return
		print("enter haven bag",useful['mapid'])
		click(173, offx=-10, offy=-10)
		sleep(uniform(2.5,3.5))
		click(134,offy=-10)
		sleep(uniform(2,2.5))
		app.send_keystrokes(text+'{ENTER}', with_spaces=True)
		if cond_wait(3,5,('mapid',162793472,5,call)):
			return
	except RuntimeError:
		sleep(uniform(3,5))
		teleport(text)
	print("done teleport")

def order(l):
	length,ret,pos=len(l),[],useful['mypos']
	while length:
		m=600
		for c in range(length):
			if (dist:=abs(l[c]%14-pos%14) + abs(l[c]//14-pos//14))<m:
				m,i=dist,c 
		length,pos=length-1,l[i]
		ret.append(l[i])
		l.pop(i)
	return ret

def wait_check_fight(tmin,tmax,cond=0):
	global first_fight
	sleep(uniform(tmin,tmax))
	if useful['infight'] and cond!=-1:
		fight(first_fight)
		first_fight=False
		print("out")

def cond_wait(tmin,tmax,cond):
	tries=0
	while useful[cond[0]] == cond[1]:
		if tries == cond[2]:
			print("forced break after timeout",useful['mapid'],cond[1],useful[cond[0]] == cond[1])
			app.send_keystrokes('{VK_SHIFT}')
			cond[3]()
			sleep(2)
			if useful[cond[0]] == cond[1]:
				cond_wait(tmin,tmax,cond)
			return True
		tries+=1
		wait_check_fight(tmin,tmax,cond[2])

def check_arch(l):
	while 1:
		prev=useful['mapid']
		cond_wait(2,3,('mapid',prev,-1))
		for m in useful["map_mobs"].items():
			if 'info' in m[1].keys():
				for i in m[1]['info']:
					if i[0] in l.keys():
						with open('ArchMonsters.txt','r+') as f:
							c,r=collection.nodes.find_one({'mapid':useful['mapid']},{'coord':1})['coord'],f.read()
							f.seek(0)
							f.write('%s : Name : %s , Level : %s , Coord : %s\n'%(strftime("%A, %d %B %Y %H:%M:%S", localtime()),l[i[0]],i[1],c)+r)
							notify.show_toast(title='ArchMonster Found !',msg='%s\n%s\n%s'%(l[i[0]],i[1],c),duration=600,threaded=True)

def collect(rsc,farmer_exception,e=None,out=False):
	count,lc=7,useful['mypos']
	if out:
		e=get_current_node(2)
	app.send_keystrokes('{VK_SHIFT DOWN}')
	for c in order([x['elementCellId'] if x['enabledSkill'] not in farmer_exception else x['elementCellId']-28 for x in useful['resources'].values() if (str(x['elementCellId']) in e and x['enabledSkill'] in rsc )]):
		s=str(c)
		click(c ,offx=e[s]['xoffset'],offy=e[s]['yoffset'],alt=e[s]['altitude'])
		count,lc=count+3,c
	return count,lc


def execute(paths_names, rsc=[], check_archi=True, rotation=1):
	Thread(target=sniff, kwargs={'filter':'tcp port 5555', 'lfilter':lambda p: p.haslayer(Raw),'prn':lambda p: on_receive(p, on_msg)}).start()
	# cond_wait(5,10,('lifepoints',1,20,wrapper(notify.show_toast,title='Script Eroor',msg='Could Not Hook Game Process',duration=1000)))
	paths,rsc,farmer_exception=list(collection.paths.find({'$or':[{'_id':{'$regex':f'.*{x}.*','$options':'i'}} for x in paths_names]},{'zaap':1,'nodes':1})),{s for r in rsc for x in collection.skills.find({'_id':{'$regex': '^%s.*'%(r),'$options':'i'}}) for s in x['skill_id']},{45,296,58,308,57,341,159,52,54,191,50,46,53,307}
	if (l:=len(paths)) and check_archi:
		Thread(target=check_arch,args=[{x['raceid']:x['_id'] for x in collection.archmonsters.find({})}]).start()
	while rotation:
		for p in sample(paths,l):
			teleport(collection.zaaps.find_one({'_id':p['zaap']},{'name':1,'_id':0})['name'])
			p=[get_current_node(1)]+p['nodes']
			for s in range(len(p)-1):
				for e in pathfinder(p[s],p[s+1]):
					prev,(count,lc)=useful['mapid'],collect(rsc,farmer_exception,e[2])
					click(cell:=get_closest(e[0],lc,e[1]),direction=e[1])
					app.send_keystrokes('{VK_SHIFT}')
					cond_wait(1.5,3,('mapid',prev,count,wrapper(click,cell,direction=e[1])))	
					print("mapchanged",prev,useful['mapid'])
			collect(rsc,farmer_exception,out=True)
			app.send_keystrokes('{VK_SHIFT}')
			wait_check_fight(6,7)
			if useful['inventory_weight'] / useful['inventory_max']>.9:
				teleport('koalak')
				for e in pathfinder(get_current_node(1),collection.nodes.find_one({'mapid':84935175},{'_id':1})['_id']):
					click(cell:=get_closest(e[0],useful['mypos'],e[1]),direction=e[1])
					cond_wait(1.5,3,('mapid',useful['mapid'],count,wrapper(click,cell,direction=e[1])))
				click(330,offy=-20)
				wait_check_fight(2,3)
				app.send_keystrokes('{DOWN}')
				wait_check_fight(2,3)
				app.send_keystrokes('{ENTER}')
				wait_check_fight(3,5)
				click(80,offx=40,offy=-7)
				wait_check_fight(1,1.5)
				click(80,offx=-15,offy=-7)
				wait_check_fight(1,1.5)
				click(80,offy=16)
				wait_check_fight(1,1.5)
				app.send_keystrokes('{VK_ESCAPE}')
		rotation-=1
	print("out bot")


# Thread(target=sniff, kwargs={'filter':'tcp port 5555 ', 'lfilter':lambda p: p.haslayer(Raw),'prn':lambda p: on_receive(p, on_msg)}).start()

# print(pathfinder('8857','8143'))
execute(paths_names=['elm','icefish','aspen','holy'],rsc=['silicate','sage','freyesque','lard','sickle','elm','aspen','hornbeam','icefish','tench','cod','holy','swordfish','monkfish','perch','Edelweiss','kaliptus','cherry'])
# Thread(target=sniff, kwargs={'filter':'tcp port 5555 ', 'lfilter':lambda p: p.haslayer(Raw),'prn':lambda p: on_receive(p, on_msg)}).start()
# sleep(3)
# while 1:
	# print(useful['resources'])
	# sleep(3)
	# if useful['infight']:
# 		fight(app,first_fight)
# 	sleep(3)
