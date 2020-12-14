from time import sleep,strftime
from subprocess import Popen
stop_time=int(input('enter stoppage hour (24h format) :\n>>'))
print('closer is running ...')
while 1:
	if int(strftime('%H'))==stop_time:
		sleep(25*60)
		Popen('setx dofus_stop 1')
		sleep(20*60)
		Popen('setx dofus_stop 0')
		Popen(f'shutdown -s')
	sleep(15*60)