from time import sleep,localtime,strftime
from math import ceil,floor
from utils import pathfinder,shortest,collection
from random import randint,uniform
from start import sniff,Raw,on_receive,on_msg,useful
from threading import Thread
from pywinauto.application import Application
from win10toast import ToastNotifier
notify,app=ToastNotifier(),None

def click(cellid,offx=0,offy=0,alt=0,direction=None,press=False):
	limit,x,y,line,row={'s':lambda x,odd:(x[0],x[1]+8) if odd else (x[0],x[1]+25) ,'n':lambda x,odd:(x[0],x[1]-25) if odd else (x[0],x[1]-10),'w':lambda x,odd:(x[0]-50,x[1]) if odd else (x[0]-25,x[1]),'e':lambda x,odd:(x[0]+25,x[1]) if odd else (x[0]+50,x[1])},258,51,cellid//14,cellid % 14
	odd=line%2
	if odd:
		x+=30
	if direction:
		x,y=limit[direction]((x,y),odd)
	elif offx:
		offx=ceil(offx*2/3)	
	app.send_keystrokes('{VK_SHIFT DOWN}' if press else '')
	app.click_input(coords=(x+row*63+offx, y+floor(15.75*line)+offy))
	app.send_keystrokes('{VK_SHIFT}')

def get_closest(edge, pos, direction):
	ret,length=[],len(edge)
	for j in range(3):
		minim=600
		for i in range(length):
			dist=abs(edge[i]%14-pos%14 if direction in ('n','s') else edge[i]//14-pos//14)
			if dist < minim:
				if j and dist-prev>2:
					continue
				index,minim=i,dist
		if minim !=600:
			ret.append(edge[index])
			edge.pop(index)
			length,prev=length-1,minim
	return ret[randint(0,min(2,len(ret)-1))]

def get_current_node(mapid, pos):
	for n in collection.nodes.find({'mapid':mapid},{'walkable':1}):
		if pos in n['walkable']:
			return n['_id']

def wrapper(func, *args, **kwargs):
	def wrapped():
		return func(*args, **kwargs)
	return wrapped

def teleport(text):
	call=wrapper(teleport,text)
	try:
		prev=useful['mapid']
		app.send_keystrokes('h')
		if wait(1.5,2.5,('mapid',prev,5,call)):
			return
		click(173, offx=-10, offy=-10)
		wait(2.5,3.5)
		click(134,offy=-10)
		wait(2,2.5)
		app.send_keystrokes(text+'{ENTER}', with_spaces=True)
		if wait(3,5,('mapid',162793472,5,call)):
			return
	except RuntimeError:
		wait(3,5)
		teleport(text)

def order(l):
	pos,length,ret=useful['mypos'],len(l),[]
	while length:
		m=600
		for c in range(length):
			calc=abs(pos-l[c])
			if calc<m:
				m=calc
				i=c  
		length,pos=length-1,l[i]
		ret.append(pos)
		l.pop(i)
	return ret

# def fight(capture=False):
	

def wait(tmin,tmax,cond=False):
	if cond:
		tries=0
		while useful[cond[0]] == cond[1]:
			if tries == cond[2]:
				print("break",useful['mapid'])
				# if useful['fight']:
					# fight()
				cond[3]()
				if useful[cond[0]] == cond[1]:
					wait(tmin,tmax,cond)
				return True
			tries+=1
			sleep(uniform(tmin,tmax))
	else:
		sleep(uniform(tmin,tmax))

def forbiden_cells():
	ret=set()
	for m in useful['map_mobs'].values():
		right,left=(m['cellId']-13,m['cellId']-14) if m['cellId']//14%2 else (m['cellId']-14,m['cellId']-15)
		offset=0
		for c in range(3):
			ret.add(m['cellId']-offset)
			ret.add(right)
			ret.add(left)
			right,left,offset=right-offset,left-offset,offset+28
		ret.add(m['cellId']-offset)	
	return ret

def check_arch(l):
	while 1:
		prev=useful['mapid']
		wait(2,3,('mapid',prev,-1))
		# print(useful['resources'])
		# print(useful['map_mobs'])
		for m in useful["map_mobs"].items():
			if 'info' in m[1].keys():
				for i in m[1]['info']:
					if i[0] in l.keys():
						with open('ArchMonsters.txt','w+') as f:
							c=collection.nodes.find_one({'mapid':useful['mapid']},{'coord':1})['coord']
							f.write('%s : Name : %s , Level : %s , Coord : %s\n'%(strftime("%A, %d %B %Y %H:%M:%S", localtime()),l[i[0]],i[1],c)+f.read())
							notify.show_toast(title='ArchMonster Found !',msg='%s\n%s\n%s'%(l[i[0]],i[1],c),duration=60,threaded=True)

def run(paths=[], rsc=[], check_archi=True, rotation=1):
	global app
	Thread(target=sniff, kwargs={'filter':'tcp port 5555', 'lfilter':lambda p: p.haslayer(Raw),'prn':lambda p: on_receive(p, on_msg)}).start()
	app = Application().connect(path='D:/Ankama/dofus').top_window()
	app.move_window(x=-10, y=0, width=1365, height=768, repaint=True)
	# app.minimize()
	# wait(5,10,('lifepoints',1,20,alarm))
	rsc,farmer_exception=set({s for r in rsc for x in collection.skills.find({'_id':{'$regex': '^%s.*'%(r), '$options': 'i'}}) for s in x['skill_id']}),set({45,296,58,308,57,341,159,52,54,191,50,46,53,307})
	if check_archi:
		Thread(target=check_arch,args=[{x['raceid']:x['_id'] for x in collection.archmonsters.find({})}]).start()
	while rotation:
		for p in paths:
			teleport(collection.zaaps.find_one({'_id':p['zaap']},{'name':1,'_id':0})['name'])
			p=[get_current_node(useful['mapid'],useful['mypos'])]+p['nodes']
			for s in range(len(p)-1):
				for e in pathfinder(p[s],p[s+1]):
					prev=useful['mapid']
					shift,count=False,2
					for c in order([x[0] if x[1]['enabledSkill'] not in farmer_exception else x[0]-28 for x in useful['resources'].items() if x[1]['enabledSkill'] in rsc]):
						if c not in forbiden_cells():
							s=str(c)
							print('recolt',c)
							click(c ,offx=e[2][s]['xoffset']-1,offy=e[2][s]['yoffset']-1,alt=e[2][s]['altitude'],press=shift)
							wait(.25,.5)
							shift,count=True,count+1
					cell=get_closest(e[0],int(s) if shift else useful['mypos'],e[1])
					print(cell,e[1])
					click(cell,direction=e[1],press=shift)
					wait(3,4.5,('mapid',prev,count,wrapper(click,cell,direction=e[1])))
					print("mapchanged",prev,useful['mapid'])
		rotation-=1

p=[{'zaap':'-2,0','nodes':['899','902']},]
run(paths=p,rsc=['ash','nettle','sage','hornbeam','five'])
# app = Application().connect(path='D:/Ankama/dofus').top_window()
# app.move_window(x=-10, y=0, width=1365, height=768, repaint=True)
