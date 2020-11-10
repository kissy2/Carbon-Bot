from zlib import compress
from sqlite3 import connect
from socket import *
from urllib.request import Request,urlopen
from pywinauto.application import Application
from pywinauto.findwindows import find_elements
from winsound import PlaySound,SND_FILENAME,SND_ALIAS
from subprocess import Popen,DEVNULL,PIPE
from multiprocessing import Process
from time import sleep,strftime
from platform import release
from scapy.all import AsyncSniffer
from scapy.all import Raw, IP, TCP
if win10:=release()=='10':
	from win10toast import ToastNotifier
	notify=ToastNotifier()
global parameters
get_hwnd,get_window,bti,conn,nl,server,parameters=lambda hwnd:Application().connect(handle=hwnd.handle).top_window(),lambda text:find_elements(title_re=f'^{text}'),lambda b:int.from_bytes(b,'big',signed=True),connect('cbd',isolation_level=None),'\n\n',(gethostbyname(gethostname()), 16969),None
conn.cursor().execute('create table if not exists accounts(login not null,password not null,name not null,server not null,primary key (login, name , server))')
# temp=[x for x in conn.cursor().execute('select * from accounts order by login')]
# conn.cursor().execute('drop table accounts')
# conn.cursor().execute('create table if not exists accounts(login not null,password not null,name not null,server not null,primary key (login, name , server))')
# for x in temp:	conn.cursor().execute('insert into accounts values(?,?,?,?)',(x[0],x[1],x[2],x[3]))
def click(app,x,y,c=1,s=0):
	try:
		for _ in range(c):	app.click(coords=(x,y))
		if s:	sleep(s)
	except RuntimeError:
		sleep(8)
		print(f'RuntimeError in Click',app.print_control_identifiers())

def press(app,k,s=0):
	try:
		app.send_keystrokes(k)
		if s:	sleep(s)
	except RuntimeError:
		sleep(8)
		print(f'RuntimeError in Press',app.print_control_identifiers())
	
def alert(app,severity):
	app.set_focus()
	if severity=='high':
		print("MODERATOR NOTIFICATION RESPOND QUICKLY!!!!")
		PlaySound(f'./threat_{severity}', SND_FILENAME)
		return -1
	elif severity=='medium':
		for _ in range(5):	PlaySound(f'./threat_{severity}', SND_FILENAME)
	elif severity=='low':
		PlaySound("SystemHand", SND_ALIAS)
	sleep(10)
	app.minimize()

def hook(name,app=None):
	try:
		while Popen(args='REG QUERY HKCU\Environment /v eca',stdout=PIPE,stderr=DEVNULL).communicate()[0][:-1][-2]=='1':	sleep(2)
		Popen('setx eca 1',stdout=DEVNULL)
		if app:
			app.close()
			sleep(2)
		for x in get_window('Dofus 2'):	get_hwnd(x).close()
		while 1:
			try:
				urlopen(Request('https://www.google.tn/'),timeout=10)
				break
			except:
				sleep(120)
		while not (window:=get_window('Ankama Launcher$')):
			Popen('call "Ankama Launcher"',stdout=DEVNULL,shell=True)
			sleep(30)
		app = Application('uia').connect(handle=window[0].handle).windows()[0]
		# app.set_focus()#force repaint
		# sleep(1)
		for x in app.children()[0].children():
			if x.get_properties()['texts'][0]=='PLAY':	break
		tries=4
		while not (window:=get_window('Dofus 2')) and not (window:=get_window(name)) and tries:
			x.click()
			tries-=1
			sleep(25)
		app.minimize()
		app=get_hwnd(window[0])
		app.move_window(x=-10, y=0, width=1400, height=768, repaint=True)
		app.minimize()
		# prev=False
		# while not get_window(hook_args[-1]):
		# 	if prev : press(app,'~',s=2)
		# 	click(app,650,230,c=3,s=2)
		# 	press(app,hook_args[0],s=2)
		# 	press(app,'{TAB}',s=2)
		# 	press(app,hook_args[1],s=2)
		# 	press(app,'~',s=20)
		# 	prev=True
		return window[0]
	except Exception as e:
		print('Hooking dofus client failed ',e)
	finally:
		Popen('setx eca 0',stdout=DEVNULL)
# import logging
# logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename=f'logs/client.txt', level=logging.DEBUG)
# logging.raiseExceptions = False

def sniffer(p,conn,name):
	try:
		global next_seq,wait,last20
		data=p[Raw].load
		seq,lendata=p[TCP].seq,len(data)
		# logging.info(f'{name} , {seq} , {next_seq} , {lendata} , {seq in last20} , {len(wait)}')
		if seq in last20:	
			if last20[seq] < lendata:
				next_seq=seq+lendata
				while next_seq in last20:	next_seq+=last20[next_seq]
				# logging.info(f'reset seq {next_seq}')
			else:	return
		last20={x:last20[x] for x in [*last20][-19:]}
		last20[seq]=lendata
		if next_seq and  seq != next_seq:	
			wait.append((seq,data))
		elif wait:
			wait.append((seq,data))
			wait.sort(key=lambda w: w[0])    
			for i in wait:		conn.sendto(len((compressed:=compress(i[1]))).to_bytes(2,'big')+compressed,server)
			next_seq,wait=i[0]+len(i[1]),[]
		else:
			next_seq=seq+lendata
			conn.sendto(len(compressed:=compress(data)).to_bytes(2,'big')+compressed,server)
	except Exception as e:
		print(f'error in sniffer {e}')

def execute(s,addr,window,name):
	def post_hook():
		app,pid=get_hwnd(window),str(window.process_id).encode()
		for x in Popen("netstat -no",stdout=PIPE,stderr=DEVNULL).communicate()[0][:-1].split(b'\r\n')[4:]:
			if pid in x and addr in x and (b'5555' in x or b'443' in x):
				client_port=(x[(t:=x.find(b':')+1):x.find(b' ',t)]).decode()
				break
		sniff=AsyncSniffer(filter=f'tcp and dst port {client_port} and host {addr.decode()}', lfilter=lambda p: p.haslayer(Raw),prn=lambda p: sniffer(p,s,name))
		sniff.start()
		# print(client_port,pid,sniff)
		return sniff,app,pid
	try:
		global next_seq,wait,last20
		next_seq,wait,last20=None,[],{}
		sniff,app,pid=post_hook()
		while (data:=s.recv(1024)):
			for p in data[:-3].split(b'$$$'):
				if (args:=p.split(b'\n'))[0]==b'c':
					click(app,bti(args[1]),bti(args[2]),bti(args[3]))
				elif args[0]==b'p':
					press(app,args[1].decode())
				elif args[0]==b'a':
					if alert(app,args[1].decode())==-1:
						s.close()
						return
				elif args[0]==b'n' and win10:
					notify.show_toast((x:=args[1].decode()),(y:=args[2].decode()),duration=30,threaded=True)
					r=open("notifications.txt","a+")
					r.seek(0,0)
					r=r.read()
					with open('notifications.txt','w') as f:
						f.seek(0,0)
						f.write('%s : %s , %s\n'%(x,strftime("%A, %d %B %Y %I:%M %p"),y)+r)
				# elif args[0]==b'r':
				# 	sniff.stop(join=True)
				# 	sleep(20)
				# 	next_seq,wait,last20=None,[],{}
				# 	sniff,app,pid=post_hook()
				# 	press(app,'{ENTER 3}',s=10)
	except Exception as e:
		# logging.critical('exec error',e)
		print('exec error',e)
		s.close()
		# app.close()
		# if not get_window(name):
		# 		sniff.stop(join=True)
		# 		window=hook(name,app)
		# 		next_seq,wait,last20=None,[],{}
		# 		sniff,app,pid=post_hook()

def new_session(session_args):
	def safe_mode():
		with open('harvest.opt','r') as f:	temp=f.read().encode()
		while 1:
			if (inp:=input('\nActivate safe mode (you\'re character will collect resources only if there is no other player on same map) ?\n1 - Yes\n2 - No\n>>')) in ('1','2'):	return temp+b'\n'+inp.encode()
			else:	print('Wrong option')
	global parameters
	try:
		app=hook(session_args[-2])
		s=socket(AF_INET,SOCK_STREAM)
		s.connect(server)
		print('Connected')
		s.settimeout(300)
		s.setblocking(1)
		if not parameters:
			# key=input('Enter Api Key :\n>> ').encode()
			key=b"kissy"
			algo=input('\nChoose An Algorithm :\n1 - Treasure Hunt\n2 - Harvest\n3 - Level Up (change map to start leveling)\n4 - Explore Zaaps (you need to have access to havenbag && already have astrub zaap)\n5 - Sell resources\n>> ').encode()
			parameters=key+b'\n'+algo+b'\n'
			if algo == b'1':
				while 1:
					if (inp:=input('\nDo you want to harvest resources while doing Treasure Hunt ?\n1 - Yes\n2 - No\n>>'))=='1':
						parameters+=safe_mode()
						break
					elif inp=='2':	break
					else:	print('Wrong option')
			elif algo == b'2':
				parameters+=safe_mode()
			elif algo == b'3':
				while 1:
					if (inp:=input('\nChoose A Leveling Area :\n1 - Incarnam(1-10)\n2 - Astrub City(10-20)\n3 - Astrub Fields(20-30)\n4 - Tainela(30-40)\n5 - Goball Corner(30-40)\n>> ')) in ('1','2','3','4','5'):
						parameters+=inp.encode()
						break
					else:	print('Wrong option')
		s.sendto((session_args[-2]+'\n'+session_args[-1]+'\n').encode()+parameters,server)
		if not (addr:=s.recv(64)):
			print('Invalid Key or maximum connection attempt reached')
			return
		print('Key accepted')
		s.settimeout(600)
		s.setblocking(1)
		p=Process(target=execute,args=(s,addr,app,session_args[-2]))
		p.start()
		return p.pid
	except Exception as e:
		print('session error',e)
		s.close()

if __name__=="__main__":
	execution_pool={}
	def prn_accounts():
		print(f'{nl[0]}Existing accounts :{nl}')
		for raw in db.execute('select rowid,name,server,login from accounts order by rowid'):
			print(f'Id : {raw[0]}\tCharacter name : {raw[1]}\tServer name : {raw[2]}\tAccount name : {raw[3]}{nl}')
	while 1:
		db=conn.cursor()
		try:
			if (i:=input(f'{nl[0]}Welcome to carbon bot choose one of the options below :{nl}1 - Launch all accounts in the database{nl}2 - Launch specific accounts from the database{nl}3 - Add new accounts to the database{nl}4 - Delete accounts from the database{nl}5 - Show existing accounts{nl}>> '))=='1':
				for row in db.execute('select * from accounts'):
					execution_pool[f'{row[2]}-{row[3]}']=new_session(row)
				break
			elif i=='2':
				prn_accounts()
				for row in db.execute("select * from accounts where rowid in {}".format( tuple(t) if len(t:=input(f"Enter the Ids (seperated by a comma ',' ) of the accounts you want to run{nl}>> ").split(','))>1 else f'({t[0]})')):
					execution_pool[f'{row[2]}-{row[3]}']=new_session(row)
				break
			elif i=='3':
				first=True
				while 1:
					if first or (i:=input(f'{nl}Add another account ? : y/n{nl}>> ').lower())=='y':
						db.execute('insert into accounts values(?,?,?,?)',(input(f"{nl[0]}Enter account name : "),input(f"{nl[0]}Enter account password : "),input(f"{nl[0]}Enter character name : "),input(f"{nl[0]}Enter server name : "))) 
						first=False
					elif i=='n':
						break
			elif i=='4':
				prn_accounts()
				db.execute('delete from accounts where rowid='+input(f'Enter the id of the account you want to delete from the database{nl}>> '))
				print('\nAccount deleted succesfully')
			elif i=='5':
				prn_accounts()
			else:
				print('\nWrong option try again')
		except Exception as e:
			print('\n-------------------------------------------\nOperation failed : ',e,'\n-------------------------------------------\n')
	conn.close()
	print(execution_pool)
	# while execution_pool:
	# 	print(f'Running instances :{nl}')
	# 	for k,v in execution_pool.items():
	# 		print(k,':',v)
	# 	operation=input(f'Execute an operation over running instances:{nl}1 - Suspend Process{nl}2 - Resume Process{nl}3 - Kill Process{nl}>>')
	# 	input('Enter ID of chosen process')