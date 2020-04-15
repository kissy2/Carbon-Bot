with open('map_info.json','a',encoding='utf8') as f:
	for i in range(1000):
		with open('map_info_%d.json'%(i),'r',encoding='utf8') as g:
			f.write(g.read())
