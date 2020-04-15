import ast
import os
import json
import time
from multiprocessing import Pool, cpu_count
from . import rsc
import dlm_unpack
from math import ceil

def format_cells(cells):
	# 0 Walkable
	# 1 Void
	# 2 Obstacle
	# 3 change map north
	# 4 change map north east
	# 5 change map east
	# 6 change map south east
	# 7 change map south
	# 8 change map south west
	# 9 change map west
	# 10 change map north west

	output=[]
	walkable=[]
	cell_id = 0
	ret={'n':[],'s':[],'w':[],'e':[]}

	for cell_pack_id in range(len(cells) // 14):
		for cell in cells[14 * cell_pack_id: 14 * (cell_pack_id + 1)]:
			try:
				if cell['mov']:
					value = 0
				else:
					value = 1
				if not cell['los']:
					value = 2

				n, s, w, e = False, False, False, False
				if cell['mapChangeData'] and (cell['mapChangeData'] & 1 or (cell_id + 1) % 28 == 0 and cell['mapChangeData'] & 2 or (cell_id + 1) % 28 == 0 and cell['mapChangeData'] & 128):
					e = True
				if cell['mapChangeData'] and (cell_id == 0 and cell['mapChangeData'] & 8 or cell['mapChangeData'] & 16 or cell_id == 0 and cell['mapChangeData'] & 32):
					w = True
				if cell['mapChangeData'] and (cell_id < 14 and cell['mapChangeData'] & 32 or cell['mapChangeData'] & 64 or cell_id < 14 and cell['mapChangeData'] & 128):
					n = True
				if cell['mapChangeData'] and (cell_id >= 546 and cell['mapChangeData'] & 2 or cell['mapChangeData'] & 4 or cell_id >= 546 and cell['mapChangeData'] & 8):
					s = True

				if n and e:
					value = 4
					ret['n'].append(cell_id)
					ret['e'].append(cell_id)
				elif n and w:
					value = 10
					ret['n'].append(cell_id)
					ret['w'].append(cell_id)
				elif s and e:
					value = 6
					ret['s'].append(cell_id)
					ret['e'].append(cell_id)
				elif s and w:
					value = 8
					ret['s'].append(cell_id)
					ret['w'].append(cell_id)
				elif n:
					value = 3
					ret['n'].append(cell_id)
				elif s:
					value = 7
					ret['s'].append(cell_id)
				elif w:
					value = 9
					ret['w'].append(cell_id)
				elif e:
					value = 5
					ret['e'].append(cell_id)
				if value not in (1,2):
					walkable.append(cell_id)
				output.append(value)
				cell_id += 1
			except Exception as e:
				print("tnikna",e,cell)
	return output,walkable,ret


def format_cell_for_dofus_pf(cells):
	output = []
	for cell in cells:
		output.append(cell['mov']+cell['nonWalkableDuringFight']+cell['los'])
	return output

def get_interactives(layers):
	interactives = {}
	doors={}
	for layer in layers:
		for cell in layer['cells']:
			for element in cell['elements']:
				if 'identifier' in element.keys() and element['identifier'] and 'elementId' in element.keys():
					if element['elementId'] in rsc.doors:
						doors[int(cell['cellId'])]=-1

					elif element['elementId'] in rsc.resources:
						if cell['cellId']%14 in (0,13) and (element['offsetX'] !=0 or element['offsetY'] !=0):
							continue	
						interactives[int(cell['cellId'])] = {'xoffset':element['offsetX'],'yoffset':element['offsetY'],'altitude':element['altitude']}
	return interactives,doors


# def is_using_new_movement_system(cells):
#	 using = False
#	 for cell in cells:
#		 if cell['moveZone']:
#			 using = True
#			 break
#	 return using
	

def generate_single_map_data(map_path, map_positions_with_key):
	data = dlm_unpack.unpack_dlm(map_path)
	map_id, cells, layers = str(int(data['mapId'])), data['cells'], data['layers']
	neighbours = {
		'n': data['topNeighbourId'],
		's': data['bottomNeighbourId'],
		'w': data['leftNeighbourId'],
		'e': data['rightNeighbourId'],
	}
	c='{};{}'.format(map_positions_with_key[map_id]['posX'], map_positions_with_key[map_id]['posY'])
	x,y,z=format_cells(cells)
	a,b=get_interactives(layers)
	map_data = {
		'id': int(map_id),
		'coord': c,
		'subAreaid': map_positions_with_key[map_id]['subAreaId'],
		'worldMap': map_positions_with_key[map_id]['worldMap'],
		'hasPriorityOnWorldMap': map_positions_with_key[map_id]['hasPriorityOnWorldmap'],
		'fightcells':format_cell_for_dofus_pf(cells),
		'cells': x,
		'floor':[x['floor'] for x in cells],
		'walkable':y,
		# 'isUsingNewMovementSystem': is_using_new_movement_system(cells),
		'neighbours': neighbours,
		'interactives':a,
		'n':z['n'],
		's':z['s'],
		'w':z['w'],
		'e':z['e'],
		'd':b
	}
	return map_data


def generate_map_info():
	"""
	Outputs a list of maps characteristics. As this list is too big to fit in mongo, we split it into multiple map_info_n.json

	The map characteristics are:
	{
		'id': map_id,
		'coord': 'x;y',
		'subAreaid': I'm not sure we even use this,
		'worldMap': As an int. 1 is the normal world, the others I don't remember right now,
		'hasPriorityOnWorldMap': The maps you want usually have this set to 'True',
		'cells': a 40 lines by 14 columns matrix of int representing the map. 0 is walkable, 1 is void, 2 is a los blocking obstacle, 3 are invalid squares for changing maps,
		'interactives': {elementId: {cell: 0}, }
	}

	:return:
	"""
	print('Generating map info')
	start = time.time()
	maps = []
	with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/MapPositions.json')), 'r') as f:
		map_positions = json.load(f)
	map_positions_with_key = {}
	for map in map_positions:
		map_positions_with_key[str(int(map['id']))] = map

	
	for root, dir, files in os.walk(os.path.abspath(os.path.join(os.path.dirname(__file__), '../partially_unpacked_maps'))):
		for file in files:
			if file.endswith('.dlm') and 'maps' in root and os.path.basename(file).replace('.dlm', '') in map_positions_with_key.keys():
				maps.append(root + '/' + file)

	map_info = []
	elements_info = {}
	with Pool(cpu_count() - 2) as p:
		results_list = p.starmap(generate_single_map_data, [(map, map_positions_with_key) for map in maps])
	
	with open('D:/sniffbot2.0-light/assets/map_info.json','w') as f:
		json.dump(results_list,f)
	
	print('Mapinfo generation done in {}s'.format(round(time.time() - start)))


if __name__ == '__main__':
	start = time.time()
	generate_map_info()
	print('Done in ', time.time() - start)
