import requests
from winsound import PlaySound
from time import sleep,strftime
servers=input('Enter servers to check ( seperated by , ) :\n>>').split(',')
threshold=float(input('threshold :\n>>'))
print('seller is running ...')
while 1:
	page = requests.get('https://www.leskamas.com/en-gb/sell-kamas.html').text.split(' onmouseover="this.style.backgroundColor=\'#ffff66\';">')[1:13]
	for x in page:
		temp=x.split('<td>')[1:]
		server=temp[0].replace('</td>','').lower()
		price=temp[3].replace('</td>','')
		status=True if 'Sourcing' in temp[-1] else False
		if server in servers and status and float(price[0:4])>threshold:
			print('server :',server,'price :',price,' (',strftime("%A, %d %B %Y %I:%M %p"),')')
			PlaySound(f'./sell_kamas',True)
	sleep(30)

