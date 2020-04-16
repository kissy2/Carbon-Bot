from re import search,findall
from json import load
from urllib.request import Request,urlopen,build_opener,HTTPCookieProcessor
from os import listdir
from utils import collection
reg,base,req,opener='[0-9]+-[a-zA-Z-]+">[a-zA-Z -]+','https://www.dofus.com/en/mmorpg/encyclopedia/',lambda l:Request(l, headers={'User-Agent': 'Mozilla/5.0'}),build_opener(HTTPCookieProcessor())

def get_neighbors(cell,shape,floor):
	done,heap,to_add=set(),[cell],(13,14,-13,-14)
	while heap:
		cell,ooe=heap[0],heap[0]//14%2
		for i in range(4):
			if ooe and cell%14==13 and i in (1,2) or not ooe and cell%14==0 and i in (0,3):
				continue
			next_cell=(to_add[i]+1 if ooe and i<2 else to_add[i] -1 if not ooe and i>1 else to_add[i])+cell
			if -1<next_cell<560 and shape[next_cell] not in (1,2) and abs(abs(floor[cell])-abs(floor[next_cell]))<51 and next_cell not in heap and next_cell not in done:
				heap.append(next_cell)
		heap.pop(0)
		done.add(cell)
	return list(done) 

def check_adjc(i,neighbors):
	for x in ((i,i-13,i-14,i+14,i+15) if i//14%2 else (i,i-14,i-15,i+13,i+14)):
		if x in neighbors:
			return True

def create_nodes():
	collection.nodes.delete_many({})
	with open('./assets/map_info.json', 'r', encoding='utf8') as g: 
		maps,delta=load(g),lambda a,b,co=True:[c for c in a if int(c) in b] if co else {c:-1 for c in a if int(c) in b}
	with open('./assets/MapScrollActions.json', 'r', encoding='utf8') as g:
		nid,t,f=0,{'rightMapId':'e','bottomMapId':'s','leftMapId':'w','topMapId':'n'},lambda s,p:(int(s[:p]),int(s[p+1:]))
		search={x['id']:{t[y[0]]:y[1] if x[y[0][:y[0].find('M')]+'Exists'] else -1 for y in x.items() if y[0] in t.keys()} for x in load(g)}
	for m in maps:
		while m['walkable']:
			neighbors=get_neighbors(m['walkable'][0],m['cells'],m['floor'])
			node={'_id':str(nid),'mapid':m['id'],'coord':f(m['coord'],m['coord'].find(';')),'subarea':m['subAreaid'],'worldmap':m['worldMap'],'priority':1 if m['hasPriorityOnWorldMap'] else 0,'walkable':neighbors,'fightcells':m['fightcells'],'interactives':None,'neighbors':{x[0]: m['neighbours'][x[0]] if x[1]==-1 else x[1] for x in search[m['id']].items()} if m['id'] in search.keys() else m['neighbours'],'n':delta(m['n'],neighbors),'s':delta(m['s'],neighbors),'w':delta(m['w'],neighbors),'e':delta(m['e'],neighbors),'d':delta(m['d'],neighbors,False)}
			node['interactives'],m['walkable']=({i:j for i,j in m['interactives'].items()},[]) if len(m['walkable'])-(l:=len(neighbors))<5 else ({i:j for i,j in m['interactives'].items() if check_adjc(int(i),neighbors)},[x for x in m['walkable'] if x not in neighbors])
			m['interactives']={x[0]:x[1] for x in m['interactives'].items() if x[0] not in node['interactives']}
			#add fix to fish in multi nodes map and remove length filter hardcode (2 lines above)
			if l>4 and (node['n'] or node['s'] or node['w'] or node['e'] or node['d']):
				collection.nodes.insert_one(node)
				nid+=1

def link_nodes():
	f=lambda c,d:int(c+13 if d=='w' else c-13 if d=='e' else (40 if c//14 else 39)*14-(14-c%14) if d=='n' else c%14+(14 if c//14%2 else 0))
	for n in collection.nodes.find({},{'n','s','w','e','neighbors','worldmap','mapid','coord'}):
		for k,v in n['neighbors'].items():
			temp,all_nodes={},list(collection.nodes.find({'mapid':v},{'walkable','neighbors','n','s','w','e'})) 
			if len(all_nodes)==1 and n[k]:
				temp[all_nodes[0]['_id']]=n[k]
				for x in all_nodes[0]['neighbors'].items():
					if n['mapid'] == x[1]:
						if not all_nodes[0][x[0]]:					
							collection.nodes.update_one({'_id':all_nodes[0]['_id']},{'$set':{x[0]:{n['_id']:[f(xx,k) for xx in n[k]]}}})
						break
			else:
				for c in n[k]:
					for j in all_nodes:
						if f(c,k) in j['walkable']:
							temp[j['_id']] = temp[j['_id']]+[c] if j['_id'] in temp.keys() else [c]
							break	
			collection.nodes.update_one({'_id':n['_id']},{'$set':{k:temp}})
	collection.nodes.update_many({},{'$unset':{'neighbors':1}})

def set_skills():
	collection.skills.delete_many({})
	links=["resources?text=&EFFECTMAIN_and_or=AND&object_level_min=1&object_level_max=200&type_id[0]=38&EFFECT_and_or=AND&size=96","resources?text=&EFFECTMAIN_and_or=AND&object_level_min=1&object_level_max=200&type_id%5B%5D=34&EFFECT_and_or=AND#jt_list","resources?text=&EFFECTMAIN_and_or=AND&object_level_min=1&object_level_max=200&type_id%5B%5D=41&EFFECT_and_or=AND#jt_list","resources?text=&EFFECTMAIN_and_or=AND&object_level_min=1&object_level_max=200&type_id%5B%5D=36&EFFECT_and_or=AND#jt_list","resources?text=&EFFECTMAIN_and_or=AND&object_level_min=1&object_level_max=200&type_id%5B%5D=35&EFFECT_and_or=AND#jt_list"]
	with open('./assets/skills.json', 'r', encoding='utf8') as g: 
		skills={} 
		for x in load(g): 
			if 'gatheredRessourceItem' in x.keys() and x['gatheredRessourceItem']>0:
				skills[x['gatheredRessourceItem']]=[x['id'],] if x['gatheredRessourceItem'] not in skills.keys() else skills[x['gatheredRessourceItem']]+[x['id']]
	for l in links:
		for x in opener.open(req(base+l)).read().decode('utf8', errors='ignore').split("<td>")[1:]:
			if f:=search(reg,x):
				f=f.group(0)
				gid=int(f[:f.index('-')])
				if gid in skills.keys():
					collection.skills.insert_one({'_id':f[f.index('>')+1:],'skill_id':skills[gid],'gid':gid})

def set_archmonsters():
	collection.archmonsters.delete_many({})
	for p in range(1,4):
		for x in opener.open(req(base+"monsters?text=&monster_level_min=1&monster_level_max=1600&monster_superrace_id[0]=20&size=96&page=%s"%(p))).read().decode('utf8', errors='ignore').split("<td>")[1:]:
			if f:=search(reg,x):
				f=f.group(0)
				collection.archmonsters.insert_one({'_id':f[f.index('>')+1:],'raceid':int(f[:f.index('-')])})

def set_runes():
	collection.runes.delete_many({})
	for x in opener.open(req(base+"resources?text=&EFFECTMAIN_and_or=AND&object_level_min=1&object_level_max=200&type_id[0]=78&EFFECT_and_or=AND&size=96")).read().decode('utf8', errors='ignore').split("<td>")[1:]:
		if f:=search(reg,x):
			f=f.group(0)
			collection.runes.insert_one({'_id':f[:f.index('-')],'name':f[f.index('>')+1:]})

def set_interactives():
	fullpath,rd,ri,interactives,doors='D:/AssetsManager-master/PyDofus_mod/output/','"FX_Particules_Spark", "FX_Mort_Lumiere"',['"AnimState0_to_AnimState1_0", "AnimState1_0", "AnimState2_0", "AnimState1_to_AnimState0_0", "AnimState0_0"', '"AnimState2_to_AnimState1_0", "AnimState1_0", "AnimState2_0", "AnimState1_to_AnimState0_0", "AnimState0_0"', '"AnimState0_0", "AnimState1_0", "AnimState1_to_AnimState0_0", "AnimState2_0", "AnimState0_to_AnimState1_0"', '"AnimState0_0", "AnimState1_0", "AnimState2_to_AnimState1_0", "AnimState1_to_AnimState0_0", "AnimState2_0"',' "AnimState1_to_AnimState2_0", "AnimState2_to_AnimState1_0", "AnimState1_0", "AnimState2_0", "AnimState0_0"'],set(),set()
	with open(fullpath+'elements.json') as g:
		for e in load(g)['elements_map'].values():
			if 'entity_look' in e.keys():			
				for p in listdir(fullpath):
					if '.d2p' in p:
						for sp in listdir(fullpath+p):
							if f'{e["entity_look"][1:-1]}.json' == sp:
								with open (fullpath+p+'/'+sp,'r') as f:
									f=' '.join(f.read().split())
									if rd in f:
										doors.add(e['id'])
									else:
										for r in ri:
											if r in f:
												interactives.add(e['id'])
												break
	with open('D:/AssetsManager-master/raw_transformer/pipelines/rsc.py','w') as f:
		f.write(f'resources={interactives}\ndoors={doors}')

def set_paths(worldmap=1):
	collection.paths.delete_many({})
	fullpath,f='D:/sniffbot2.0-light/paths/',lambda x,c=True,s=0:x.index('"' if c else ",",s)
	for p in listdir(fullpath):
		if '.' in p:
			with open(fullpath+p) as g:
				t=findall('map =.*gather = true',g.read())
				path={'_id':p[:p.index('.')],'zaap':'%s,%s'%(t[0][f(t[0])+1:(sep:=f(t[0],False))], t[0][sep+1:f(t[0],s=sep)]) ,'nodes':[]}
				for x in t[1:]:
					if len(l:=list(collection.nodes.find({'coord':[ int(x[f(x)+1:(sep:=f(x,False))]), int(x[sep+1:f(x,s=sep)])],'interactives':{'$ne':{}} ,'worldmap':worldmap,'$or':[{'n':{'$ne':[]}}, {'s': {'$ne':[]}}, {'e': {'$ne':[]}}, {'w': {'$ne':[]}}  ]},{})))>1:
						print(f'choose a node:\n{l}\n')
						path['nodes'].append(input('->'))
					else:
						path['nodes'].append(l[0]['_id'])
				collection.paths.insert_one(path)

def set_doors_hardcode():
	from launch import get_current_node,sniff,Raw,on_receive,on_msg,useful,Thread
	Thread(target=sniff, kwargs={'filter':'tcp port 5555', 'lfilter':lambda p: p.haslayer(Raw),'prn':lambda p: on_receive(p, on_msg)}).start()
	while 1:
		input('Hit ENTER To Start')
		temp={}
		for x in collection.nodes.find_one({'_id':(nid:=get_current_node(1)),'d':{'$exists':True}},{'d'})['d']:
			input(f'Move to the next map that link the Door {x} and hit ENTER')
			temp[collection.nodes.find_one({'_id':get_current_node(1)},{'_id':1})['_id']]=int(x)
		collection.nodes.update_one({'_id':nid},{'$set':{'d':temp}})

# set_doors_hardcode()
# create_nodes()
# link_nodes()
# set_paths()
# set_interactives()
# set_skills()
# set_archmonsters()
# set_runes()