import requests
from winsound import PlaySound
from time import sleep,strftime
servers=input('Enter servers to check ( seperated by , )\n>>').split(',')
print('seller is running ...')
while 1:
	page = requests.post('https://vente.tryandjudge.com/ScriptPHP/verification.php',{'devise':'EUR','tester':'serveurcontentprices'}).text.split('<td>')[1:]
	for x in range(0,69,3):
		server = page[x][:page[x].find('<')].lower()
		price = page[x+1][:page[x+1].find('<')]
		status = True if '<' in page[x+2][page[x+2].find('>')+1:page[x+2].find('</center>')-1] else False
		if server in servers and status:
			print('server :',server,'price :',price,strftime("%A, %d %B %Y %I:%M %p"))
			PlaySound(f'./sell_kamas',True)
	sleep(5)

