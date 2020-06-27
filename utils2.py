from re import search,findall,sub
from json import load,loads
from urllib.request import Request,urlopen,build_opener,HTTPCookieProcessor
from os import listdir
from pymongo import MongoClient
from json import dump
# from utils import get_current_node,useful,click
collection,reg,base,req,opener=MongoClient('mongodb://localhost:27017/').admin,'[0-9]+-[a-zA-Z-]+">[a-zA-Z -]+','https://www.dofus.com/en/mmorpg/encyclopedia/',lambda l:Request(l, headers={'User-Agent': 'Mozilla/5.0'}),build_opener(HTTPCookieProcessor())

def get_neighbors(cell,shape,floor):
	done,heap,to_add=set(),[cell],(13,14,-13,-14)
	while heap:
		cell,ooe=heap[0],heap[0]//14%2
		for i in range(4):
			if ooe and cell%14==13 and i in (1,2) or not ooe and not cell%14 and i in (0,3):
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
			node={'_id':str(nid),'mapid':m['id'],'coord':f(m['coord'],m['coord'].find(';')),'subarea':m['subAreaid'],'worldmap':m['worldMap'],'priority':1 if m['hasPriorityOnWorldMap'] else 0,'walkable':neighbors,'fightcells':m['fightcells'],'interactives':None,'neighbors':{x[0]: m['neighbours'][x[0]] if x[1]==-1 else x[1] for x in search[m['id']].items()} if m['id'] in search.keys() else m['neighbours'],'n':delta(m['n'],neighbors),'s':delta(m['s'],neighbors),'w':delta(m['w'],neighbors),'e':delta(m['e'],neighbors),'d':delta(m['d'],neighbors,False),'o':m['o']}
			node['interactives'],m['walkable']=({i:j for i,j in m['interactives'].items()},[]) if len(m['walkable'])-(l:=len(neighbors))<5 else ({i:j for i,j in m['interactives'].items() if check_adjc(int(i),neighbors)},[x for x in m['walkable'] if x not in neighbors])
			#add fix to fish in multi nodes map and remove length filter hardcode (the line above)
			m['interactives']={x[0]:x[1] for x in m['interactives'].items() if x[0] not in node['interactives']}
			if l>4 and (node['n'] or node['s'] or node['w'] or node['e'] or node['d'] or node['interactives']):
				collection.nodes.insert_one(node)
				nid+=1


def link_nodes():
	fix,f={},lambda c,d:int(c+13 if d=='w' else c-13 if d=='e' else (40 if c//14 else 39)*14-(14-c%14) if d=='n' else c%14+(14 if c//14%2 else 0))
	for n in collection.nodes.find({},{'n','s','w','e','neighbors','worldmap','mapid','coord'}):
		for k,v in n['neighbors'].items():
			temp,all_nodes={},list(collection.nodes.find({'mapid':v},{'walkable','neighbors','n','s','w','e','d'})) 
			if len(all_nodes)==1:
				if n[k]:
					temp[all_nodes[0]['_id']]=n[k]
					for x in all_nodes[0]['neighbors'].items():
						if n['mapid'] == x[1]:
							if not all_nodes[0][x[0]] and not all_nodes[0]['d']:	
								collection.nodes.update_one({'_id':all_nodes[0]['_id']},{'$set':{x[0]:{n['_id']:[f(xx,k) for xx in n[k]]}}})
								fix[all_nodes[0]['_id']]=(x[0],n['_id'],[f(xx,k) for xx in n[k]])
							break
				elif n['_id'] in fix and k==fix[n['_id']][0]:
					temp[fix[n['_id']][1]]=fix[n['_id']][2]
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
	with open('./assets/skills.json', 'r', encoding='utf8') as g: 
		skills={} 
		for x in load(g): 
			if 'gatheredRessourceItem' in x.keys() and x['gatheredRessourceItem']>0:
				skills[x['gatheredRessourceItem']]=[x['id'],] if x['gatheredRessourceItem'] not in skills.keys() else skills[x['gatheredRessourceItem']]+[x['id']]
	for i in range(1,4):
		for x in opener.open(req(base+"resources?text=&EFFECTMAIN_and_or=AND&object_level_min=1&object_level_max=200&type_id[0]=34&type_id[1]=41&type_id[2]=35&type_id[3]=39&type_id[4]=36&type_id[5]=38&type_id[6]=58&EFFECT_and_or=AND&size=96&page="+str(i))).read().decode('utf8', errors='ignore').split("<td>")[1:]:
			if f:=search(reg,x):
				f=f.group(0)
				if (gid:=int(f[:f.index('-')])) in skills.keys():
					collection.skills.insert_one({'_id':f[f.index('>')+1:],'skill_id':skills[gid],'gid':gid})

def set_archmonsters():
	collection.archmonsters.delete_many({})
	for p in range(1,4):
		for x in opener.open(req(base+"monsters?text=&monster_level_min=1&monster_level_max=1600&monster_superrace_id[0]=20&size=96&page=%s"%(p))).read().decode('utf8', errors='ignore').split("<td>")[1:]:
			if f:=search(reg,x):
				f=f.group(0)
				collection.archmonsters.insert_one({'_id':f[f.index('>')+1:],'raceid':int(f[:f.index('-')])})

def set_monsters():
	collection.monsters.delete_many({})
	for p in range(1,18):#increase range if new monsters were added
		for x in opener.open(req(base+"monsters?text=&monster_level_min=1&monster_level_max=1600&monster_type[0]=boss&monster_type[1]=other&size=96&page=%s"%(p))).read().decode('utf8', errors='ignore').split("<td>")[1:]:
			if f:=search(reg,x):
				f=f.group(0)
				collection.monsters.insert_one({'_id':int(f[:f.index('-')]),'name':f[f.index('>')+1:]})


def set_runes():
	collection.runes.delete_many({})
	for x in opener.open(req(base+"resources?text=&EFFECTMAIN_and_or=AND&object_level_min=1&object_level_max=200&type_id[0]=78&EFFECT_and_or=AND&size=96")).read().decode('utf8', errors='ignore').split("<td>")[1:]:
		if f:=search(reg,x):
			f=f.group(0)
			collection.runes.insert_one({'_id':f[:f.index('-')],'name':f[f.index('>')+1:]})

def set_interactives():
	fullpath,rd,ri,interactives,doors='./PyDofus_mod/output/','"FX_Particules_Spark", "FX_Mort_Lumiere"',['"AnimState0_to_AnimState1_0", "AnimState1_0", "AnimState2_0", "AnimState1_to_AnimState0_0", "AnimState0_0"', '"AnimState2_to_AnimState1_0", "AnimState1_0", "AnimState2_0", "AnimState1_to_AnimState0_0", "AnimState0_0"', '"AnimState0_0", "AnimState1_0", "AnimState1_to_AnimState0_0", "AnimState2_0", "AnimState0_to_AnimState1_0"', '"AnimState0_0", "AnimState1_0", "AnimState2_to_AnimState1_0", "AnimState1_to_AnimState0_0", "AnimState2_0"',' "AnimState1_to_AnimState2_0", "AnimState2_to_AnimState1_0", "AnimState1_0", "AnimState2_0", "AnimState0_0"'],set(),set()
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
	with open('./raw_transformer/pipelines/rsc.py','w') as f:
		f.write(f'resources={interactives}\ndoors={doors}')

def set_paths():
	# collection.paths.delete_many({})
	fullpath,f='./paths/',lambda x,c=True,s=0:x.index('"' if c else ",",s)
	for p in listdir(fullpath):
		if '.' in p:
			with open(fullpath+p) as g:
				print('Path name : ',p)
				t=findall('map =.*gather = true',g.read())
				path={'_id':p[:p.index('.')],'zaap':'%s,%s'%(t[0][f(t[0])+1:(sep:=f(t[0],False))], t[0][sep+1:f(t[0],s=sep)]) ,'nodes':[]}
				for x in t[1:]:
					lis={'coord':(c:=([int(x[f(x)+1:(sep:=f(x,False))]), int(x[sep+1:f(x,s=sep)])]))}
					if ('xp' or 'zaaps') not in p:
						lis['interactives']={'$ne':{}}
					if len(l:=list(collection.nodes.find(lis,{'worldmap'})))>1:
						if worldmap:=input(f'multi nodes found on this map {c}\n{l}\nwrite worldmap index if you want to filter by worldmap else hit enter : '):
							if len(l:=[x for x in l if x['worldmap']== int(worldmap)])==1:
								path['nodes'].append(l[0]['_id'])
								continue
						if len(l):
							print(f'choose a node in this map :\n{l}\n')
							while node_input:=input('Enter node id to add it to the path or hit enter to continue : '):
								path['nodes'].append(node_input)
					elif l:
						path['nodes'].append(l[0]['_id'])
				collection.paths.insert_one(path)

def set_paths_2():
	with open('./paths/ignore/underground.json', 'r', encoding='utf8') as f:
		for x in (out:=load(f)):
			nodes=[]
			for y in x['nodes']:
				nodes.append(get_current_node(1,y[0],y[1]))
			try:
				collection.paths.insert_one({'_id':x['_id'],'zaap':x['zaap'],'nodes':nodes})
			except:
				pass
	if input('DO YOU WANT SET A NEW PATH ? Y/N').lower()=='y':
		while 1:
			input("GO TO STARTING ZAAP AND HIT ENTER")
			t=collection.nodes.find_one({'mapid':useful['mapid']},{'coord':1})
			new_path,temp={'_id':input('WRITE THE PATH NAME'),'zaap':f'{t["coord"][0]},{t["coord"][1]}','nodes':[]},[[useful['mapid'],useful['mypos']]]
			while 1:
				if (i:=input("GO TO THE NEXT MAP AND HIT ENTER _OR_ S TO SAVE THE PATH\n"))=='':
					new_path['nodes'].append(nid:=get_current_node(1))
					temp.append([useful['mapid'],useful['mypos']])
				elif i=='s':
					try:
						collection.paths.insert_one(new_path)
						print(out)
						with open('./paths/ignore/underground.json', 'w', encoding='utf8') as f:
							out.append({'_id':new_path['_id'],'zaap':new_path['zaap'],'nodes':temp})
							dump(out,f)
					except:
						print('AN ERROR OCCURED WHILE INSERTING TRY AGAIN WITH A DIFFERENT NAME')
					break
				else:
					print('NO SUCH OPTION TRY AGAIN')

def set_doors_hardcode():
	from win32api import GetCursorPos as gp
	with open('./assets/Doors.json', 'r', encoding='utf8') as f:
		for x in (out:=load(f)):
			s=get_current_node(3,x['mapid'],x['pos'])
			temp={x:y for x,y in s[1].items()}
			for k,v in x['d'].items():
				k=int(k)
				if (t:=get_current_node(1,v[0],v[1])) in temp:
					if k not in temp[t]:
						temp[t].append(k)
				else:
					temp[t]=[k]
			collection.nodes.update_one({'_id':s[0]},{'$set':{'d':temp}})
	if input('DO YOU WANT SET NEW DOORS ? Y/N : ').lower()=='y':
		while 1:
			if (i:=input('1 - LINK DOORS\n2 - LINK CAVES\n'))=='1':
				temp,temp1,node,pos,mapid={},{},get_current_node(3),useful['mypos'],useful['mapid']
				for x,v in node[1].items():
					if v==-1:
						input(f'Move to the next map that link the Door at cell {x} HIT ENTER WHEN DONE')
						temp[tid]= temp[tid]+[int(x)] if (tid:=get_current_node(1)) in temp else [int(x)]
						temp1[x]=(useful['mapid'],useful['mypos'])
					else:
						temp[x]=v
				with open('./assets/Doors.json', 'w', encoding='utf8') as f:
					out.append({'mapid':mapid,'pos':pos,'d':temp1})
					dump(out,f)
				collection.nodes.update_one({'_id':node[0]},{'$set':{'d':temp}})
			elif i=='2':
				input('*****MOVE THE CURSOR TO THE CAVE ENTRANCE AND HIT ENTER*****')
				nid,mapid,pos=get_current_node(3),useful['mapid'],useful['mypos']
				l,r,(cpx,cpy)=0,0,gp()
				while (c:=cpx-62)>252:
					r,cpx=r+1,c
				while (c:=cpy-16)>54:
					l,cpy=l+1,c
				click(cell:=l*14+r)
				if input(f'CLICKING ON THE ESTIMATED CELL {cell} WHEN THE MAP IS CHANGED HIT SPACE THEN ENTER TO SAVE IT ELSE HIT ENTER TO TRY AGAIN')==' ':
					nid[1][get_current_node(1)]=[cell]
					with open('./assets/Doors.json', 'w', encoding='utf8') as f:
						out.append({'mapid':mapid,'pos':pos,'d':{str(cell):(useful['mapid'],useful['mypos'])}})
						dump(out,f)
					collection.nodes.update_one({'_id':nid[0]},{'$set':{'d':nid[1]}})
				else:
					print("ABORT")
			else:
				print('not yet implemented maybe this option will add missing resources')

def set_exceptions():
	while 1:
		i,x,y=input('Enter Resource Name : '),int(input('ENTER X_OFFSET : ')),int(input('ENTER Y_OFFSET : '))
		for x in (r:=collection.skills.find_one({'_id':{'$regex':i,'$options':'i'}},{'skill_id':1}))['skill_id']:
			collection.exceptions.insert_one({'_id':x,'name':r['_id'],'offx':x,'offy':y})
		print('DONE\n')

def set_treasure_ids():
	import concurrent.futures
	hints,id_dofus_sama,id_dofus_map,named_ids,directions=loads((t:=urlopen(Request('https://dofus-map.com/en/hunt')).read().decode('utf-8'))[(tt:=t.index('var text = {')+11):t.index('}',tt)+1]),{},{},[],{'0':'right','4':'left','2':'bottom','6':'top'}
	for x in urlopen(req('https://www.dofusama.fr/treasurehunt/en/search-clue.html')).read().decode('utf-8').split('<option value="')[1:]:
		id_dofus_sama[t[t.index('>')+1:t.index('<')]]=(t:=sub("&#(\d+);", lambda m: chr(int(m.group(1))), x.lower()))[:t.index('"')]
	collection.dofus_sama.delete_many({})
	collection.named_ids.delete_many({})
	collection.treasure.delete_many({})
	with open('./raw_transformer/output/PointOfInterest.json', 'r', encoding='utf8') as f:
		with open('./raw_transformer/output/i18n_en.json', 'r', encoding='utf8') as g:
			texts=load(g)['texts']
		for x in load(f):
			key,test=texts[str(x['nameId'])].lower(),True
			try:
				collection.dofus_sama.insert_one({'_id':x['id'],'ds_id':id_dofus_sama[key]})
			except:
				print(f'Missing clue on dofus sama server : {key}')
			for y in hints.items():
				if y[1].lower()==key:
					id_dofus_map[i],test=id_dofus_map[i]+[x['id']] if (i:=int(y[0])) in id_dofus_map else [x['id']],False
			if test:
				print(f'Missing clue on dofus map server : {key}')
			named_ids.append({'_id':x['id'],'name':key})
	collection.named_ids.insert_many(named_ids)
	if input('PRESS Y TO GENERATE A NEW TREASURE COLLECTION OR N TO UPDATE ID\'S IN CURRENT COLLECTION : ').lower()=='y':
		def dofus_map(args):
			hints=loads(urlopen(Request(f'https://dofus-map.com/huntTool/getData.php?x={args[0]}&y={args[1]}&direction={args[2][1]}&world=0&language=en')).read().decode('utf-8'))['hints']
			print(args)
			if hints:
				if collection.treasure.find_one({'_id':(id:=f'{args[0]},{args[1]}')},{'_id'}):
					collection.treasure.update_one({'_id':id},{'$set':{args[2][0]:hints}})
				else:
					collection.treasure.insert_one({'_id':id,args[2][0]:hints})
		with concurrent.futures.ThreadPoolExecutor(max_workers=2) as e:
		    e.map(dofus_map,((x,y,d) for x in range(-88,50) for y in range(-88,50) for d in directions.items()))
	else:
		with open('./assets/treasure.json', 'r', encoding='utf8') as f:
			collection.treasure.insert_many(load(f))
		for x in collection.treasure.find({}):
			for d in directions:
				if d in x:
					collection.treasure.update_one({'_id':x['_id']},{'$set':{d:[{'id':y,'x':x['x'],'y':x['y']} for x in x[d] for y in (id_dofus_map[x['n']] if x['n'] in id_dofus_map else [])]}})
		with open('./assets/hints.json', 'r', encoding='utf8') as f:
			directions={0:('e','right','4'),4:('w','left','0'),2:('s','bottom','6'),6:('n','top','2')}
			for x in load(f):
				if len(l:=list(collection.nodes.find({'coord':[int((t:=x['coord'].split(','))[0]),int(t[1])],'worldmap':1},{'_id','worldmap'})))>1:
					last=input(f'{l}\nChoose a node to update')
				else:
					last=l[0]['_id']
				hint=collection.named_ids.find_one({'name':x['name']},{'_id'})['_id']
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
						if temp2:=collection.treasure.find_one({'_id':(id:=f'{cur["coord"][0]},{cur["coord"][1]}')}):
							if directions[d[0]][2] in temp2:
								for t in temp2[directions[d[0]][2]]:
									if t['id']==hint:
										t['x'],t['y']=x,y
										break
								else:
									temp2[directions[d[0]][2]].append({'id':hint,'x':x,'y':y})
							else:
								temp2[directions[d[0]][2]]=[{'id':hint,'x':x,'y':y}]
							collection.treasure.update_one({'_id':id},{'$set':{directions[d[0]][2]:temp2[directions[d[0]][2]]}})
						else:
							collection.treasure.insert_one({'_id':id},{'$set':{directions[d[0]][2]:[{'id':hint,'x':x,'y':y}]}})
						i-=1
# create_nodes()
# link_nodes()
# set_doors_hardcode()
# set_paths()
# set_paths_2()
# set_interactives()
# set_skills()
# set_archmonsters()
# set_monsters()
# set_runes()
# set_exceptions()
set_treasure_ids()#takes 3-4 hours... how to optimize this maybe multiprocessing + asyncio ?
print('done')
