from json import load
from random import randint,sample
from pymongo import MongoClient
collection=MongoClient('mongodb://localhost:27017/')['admin']['nodes']

def get_neighbors(cell,shape):
	done,heap,to_add=set(),[cell],(13,14,-13,-14)
	while heap:
		cell=heap[0]
		even=cell//14%2==0
		for i in range(4):
			if even and cell%14==0 and i in (0,3) or not even and cell%14==13 and i in (1,2):
				continue
			next_cell=(to_add[i]+1 if not even and i<2 else to_add[i] -1 if even and i>1 else to_add[i])+cell
			if next_cell not in heap and -1<next_cell<560 and shape[next_cell] not in (1,2) and next_cell not in done:
				heap.append(next_cell)
		heap.pop(0)
		done.add(cell)
	return list(done) 

def func(cells,flat):
	ret={'n':[],'s':[],'w':[],'e':[]}
	for c in cells:
		if flat[c] in (3,4,10):
			ret['n'].append(c)		
		elif flat[c] in (7,8,6):
			ret['s'].append(c)
		elif flat[c] in (9,8,10):
			ret['w'].append(c)
		elif flat[c] in (5,4,6):
			ret['e'].append(c)
	return ret

def check_adjc(i,neighbors):
	for x in ((i-13,i-14,i+14,i+15) if i//14%2 else (i-14,i-15,i+13,i+14)):
		if x in neighbors:
			return True

def create_nodes():
	collection.delete_many({})
	from jsonassets import map_info 
	with open('./jsonassets/MapScrollActions.json', 'r', encoding='utf8') as g:
		nid,t,f=0,{'rightMapId':'e','bottomMapId':'s','leftMapId':'w','topMapId':'n'},lambda s,p:(int(s[:p]),int(s[p+1:]))
		search={x['id']:{t[y[0]]:y[1] if x[y[0][:y[0].find('M')]+'Exists'] else -1 for y in x.items() if y[0] in t.keys()} for x in load(g)}
	for m in map_info.maps:
		while m['walkable']:
			neighbors=get_neighbors(m['walkable'][0],m['cells'])
			node={'_id':str(nid),'mapid':m['id'],'coord':f(m['coord'],m['coord'].find(';')),'subarea':m['subAreaid'],'worldmap':m['worldMap'],'priority':1 if m['hasPriorityOnWorldMap'] else 0,'mapshape':m['cells'],'walkable':neighbors,'fightcells':m['fightcells'],'interactives':None,'neighbors':{x[0]: m['neighbours'][x[0]] if x[1]==-1 else x[1] for x in search[m['id']].items()} if m['id'] in search.keys() else m['neighbours']}
			node.update(func(neighbors,m['cells']))
			node['interactives'],m['walkable']=({str(i):j for i,j in m['interactives'].items()},[]) if neighbors == m['walkable'] else ({str(i):j for i,j in m['interactives'].items() if i in neighbors or check_adjc(i,neighbors)},[x for x in m['walkable'] if x not in neighbors])			
			if (node['n'] or node['s'] or node['w'] or node['e']) and len(neighbors)>1:
				nid+=1
				collection.insert_one(node)

def link_nodes():
	f=lambda c,d:int(c+13 if d=='w' else c-13 if d=='e' else (40 if c//14 else 39)*14-(14-c%14) if d=='n' else c%14+(14 if c//14%2 else 0))
	for n in collection.find({},{'n','s','w','e','neighbors','worldmap','mapid','coord'}):
		for k,v in n['neighbors'].items():
			temp,all_nodes={},list(collection.find({'mapid':v,'worldmap':n['worldmap']},{'walkable','neighbors','n','s','w','e'})) 
			if len(all_nodes)==1 and n[k]:
				temp[all_nodes[0]['_id']]=n[k]
				for x in all_nodes[0]['neighbors'].items():
					if n['mapid'] == x[1]:
						if not all_nodes[0][x[0]]:					
							collection.update_one({'_id':all_nodes[0]['_id']},{'$set':{x[0]:{n['_id']:[f(xx,k) for xx in n[k]]}}})
						break
			else:
				for c in n[k]:
					for j in all_nodes:
						if f(c,k) in j['walkable']:
							temp[j['_id']] = temp[j['_id']]+[c] if j['_id'] in temp.keys() else [c]
							break	
			collection.update_one({'_id':n['_id']},{'$set':{k:temp}})

def shortest(heap,target):
	m,ret,i,index,decal=10000,[],0,set(),0
	for x in heap:
		if x[0][-1]['coord']==target:
			return None,None,[j['coord'] for j in x[0]]
		if x[1]==m:
			ret.append(x)
			index.add(i)
		elif x[1]<m:
			m,ret,index=x[1],[x],set({i})
		i+=1
	for j in index:
		del heap[j-decal]
		decal+=1
	return ret,heap,None

def pathfinder(start,target):
	f=lambda s,t:4*(abs(t[0]-s[0] if t[0]>0 and s[0]>0 or t[0]<0 and s[0]<0 else abs(t[0])+abs(s[0]))+abs(t[1]-s[1] if t[1]>0 and s[1]>0 or t[1]<0 and s[1]<0 else abs(t[1])+abs(s[1])))
	heap,done=[[[start,],f(start['coord'],target)]],set()
	while heap:
		nodes,heap,path=shortest(heap,target)
		if path:
			print(path)
			return path
		for node in nodes:
			for d in sample(('n','s','w','e'),4):
				for k in node[0][-1][d].keys():
					if k not in done:
						done.add(k)
						neighbor=collection.find_one({'_id':k},{'coord':1,'n':1,'s':1,'w':1,'e':1})
						heap.insert(0,[node[0]+[neighbor],f(neighbor['coord'],target)])			

# create_nodes()
# link_nodes()
import timeit
def wrapper(func, *args, **kwargs):
	def wrapped():
		return func(*args, **kwargs)
	return wrapped
x,y=collection.find_one({'_id':'849'},{'coord':1,'n':1,'s':1,'w':1,'e':1}),[-32,-56]
# a=pathfinder(x,y)
# for i in a:
# 	print(i)
wrapped = wrapper(pathfinder, x,y)
for i in range(1):
	print(timeit.timeit(stmt=wrapped, number=1))
