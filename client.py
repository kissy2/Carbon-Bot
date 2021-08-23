# from zlib import compress
from sqlite3 import connect
from socket import *
from urllib.request import Request,urlopen
from pywinauto.application import Application
from pywinauto.findwindows import find_elements
from winsound import PlaySound,SND_FILENAME,SND_ALIAS
from subprocess import Popen,DEVNULL,PIPE
from multiprocessing import Process
from time import sleep,strftime
from random import uniform,randint
from platform import release
from scapy.all import AsyncSniffer
from scapy.all import Raw, IP, TCP
if win10:=release()=='10':
	from win10toast import ToastNotifier
	notify=ToastNotifier()
prev,get_hwnd,get_window,bti,conn,nl,server=None,lambda hwnd:Application().connect(handle=hwnd.handle).top_window(),lambda text:find_elements(title_re=f'^{text}'),lambda b:int.from_bytes(b,'big',signed=True),connect('cbd',isolation_level=None),'\n\n',(gethostbyname(gethostname()), 16969)
conn.cursor().execute('create table if not exists accounts(login primary key,password not null,name not null,server not null)')
# temp=[x for x in conn.cursor().execute('select * from accounts order by login')]
# conn.cursor().execute('drop table accounts')
# conn.cursor().execute('create table if not exists accounts(login primary key,password not null,name not null,server not null)')
# print(temp)
# for x in temp:	conn.cursor().execute('insert into accounts values(?,?,?,?)',(x[0],x[1],x[2],x[3]))
def click(app,x,y,c=1,s=0):
	try:
		for _ in range(c):	app.click(coords=(x,y))
		if s:	sleep(s)
	except RuntimeError:
		sleep(8)
		print(f'RuntimeError in Click',app.print_control_identifiers())
	except Exception as e:
		print(f'Click error',e)

def press(app,k,s=0):
	try:
		app.send_keystrokes(k)
		if s:	sleep(s)
	except RuntimeError:
		sleep(8)
		print(f'RuntimeError in Press',app.print_control_identifiers())
	except Exception as e:
		print(f'Press error',e)
	
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


def dofus_closer():
	for x in get_window('Dofus 2'):	get_hwnd(x).close()


def hook(login,password,name):
	try:
		print('Hooking to dofus client',name)
		while Popen(args='REG QUERY HKCU\Environment /v eca',stdout=PIPE,stderr=DEVNULL).communicate()[0][:-1][-2]=='1':	sleep(2)
		Popen('setx eca 1',stdout=DEVNULL)
		dofus_closer()
		while 1:
			try:
				urlopen(Request('https://www.google.tn/'),timeout=10)
				break
			except:
				print("No internet connection was detected retrying after 2 minutes .....")
				sleep(120)

		if not (window:=get_window(name)):
			while not (window:=get_window('Dofus 2.')):
				try:
					Popen('call "D:/Games/Ankama/dofus/Dofus.exe"',stdout=DEVNULL,shell=True)
					sleep(10)
				except Exception as e:
					print("Couldnt start dofus client",e)
					return -1
			app=get_hwnd(window[0])
			app.move_window(x=-10, y=0, width=1400, height=768, repaint=True)
			app.minimize()
			click(app,700,430,s=1)
			click(app,675,225,c=5,s=1)
			press(app,login)
			press(app,'{TAB}',s=1)
			press(app,password)
			press(app,'{ENTER 3}',s=10)
			if not (window:=get_window(name)):	click(app,675,185,c=3,s=20)
		else:
			app=get_hwnd(window[0])

		assert name in window[0].name
		return window[0]
	except Exception as e:
		print('Hooking dofus client failed ',e)
		Popen('setx eca 0',stdout=DEVNULL)
		sleep(300)
		return hook(login,password,name) #bad if max depth reccursion reached .....
	finally:
		Popen('setx eca 0',stdout=DEVNULL)

def sniffer(p,conn):
	try:
		global next_seq,wait,last20
		data=p[Raw].load
		seq,lendata=p[TCP].seq,len(data)
		if seq in last20:	
			if last20[seq] < lendata:
				next_seq=seq+lendata
				while next_seq in last20:	next_seq+=last20[next_seq]
			else:	return
		last20={x:last20[x] for x in [*last20][-19:]}
		last20[seq]=lendata
		if next_seq and  seq != next_seq:	
			wait.append((seq,data))
		elif wait:
			wait.append((seq,data))
			wait.sort(key=lambda w: w[0])    
			# for i in wait:		conn.sendto(len((compressed:=compress(i[1]))).to_bytes(2,'big')+compressed,server)
			for i in wait :	conn.sendto(len(i[1]).to_bytes(2,'big')+i[1],server)
			next_seq,wait=i[0]+len(i[1]),[]
		else:
			next_seq=seq+lendata
			# conn.sendto(len(compressed:=compress(data)).to_bytes(2,'big')+compressed,server)
			conn.sendto(len(data).to_bytes(2,'big')+data,server)
	except Exception as e:
		print(f'error in sniffer {e}')

def post_hook(window,s,addr,check=True):
		try:
			print('Post_hook called',window.name)
			app,pid,counter=get_hwnd(window),str(window.process_id).encode(),24
			if check:
				while '-' not in window.name and counter:
					counter-=1	
					sleep(.5)
				if not counter:	
					print('Name undetected')
					return None,app,None
			for x in Popen("netstat -no",stdout=PIPE,stderr=DEVNULL).communicate()[0][:-1].split(b'\r\n')[4:]:
				if pid in x and addr in x and (b'5555' in x or b'443' in x):
					client_port=(x[(t:=x.find(b':')+1):x.find(b' ',t)]).decode()
					break
			else:
				print('Failed detecting client port',window.name)
				return None,app,None
			sniff=AsyncSniffer(filter=f'tcp and dst port {client_port} and host {addr.decode()}', lfilter=lambda p: p.haslayer(Raw),prn=lambda p: sniffer(p,s))
			sniff.start()
			return sniff,app,pid
		except Exception as e:
			print('Post_hook problem',e)
			return None,app,None

def close_app_sock(app,s):
	try:
		app.close()
		s.close()
		print('App and socket closed')
	except Exception as e:
		print('Already closed socket or app',e)

def close_sniffer(sniff):
	try:
		sniff.stop(join=True)
		while sniff.running:	sleep(1)
		print("Sniffer closed")
	except Exception as e:
		print('Failed closing sniffer',e)

def execute(s,addr,window,session_args,prev_parameters):
	try:
		global next_seq,wait,last20
		next_seq,wait,last20=None,[],{}
		sniff,app,pid=post_hook(window,s,addr)
		if not pid:
			print('Failed post hooking',window.name)	
			close_app_sock(app,s)
			return new_session(session_args,prev_parameters)
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

				elif args[0]==b'd':
					print('Disconnect')
					close_app_sock(app,s)
					close_sniffer(sniff)
					return

				elif args[0]==b'r':
					print('Reconnect')
					close_sniffer(sniff)
					sleep(15)
					next_seq,wait,last20=None,[],{}
					sniff,app,pid=post_hook(window,s,addr,False)
					if not pid:
						print('Failed post hook after reconnection',window.name)
						close_app_sock(app,s)
						print('Initilising a new session') 
						return new_session(session_args,prev_parameters)
					try:
						press(app,'{ENTER 3}',s=25)
						press(app,'{ENTER 3}',s=1)
					except Exception as e:
						print('Window error',e)

				elif args[0]==b'o':
					print('Disconnect then reconnect')
					close_app_sock(app,s)
					temp=prev_parameters.split(b'\n')
					temp[2]=args[1]
					close_sniffer(sniff)
					if len(args)==3:
						sep=temp[7].find(b'|')
						t=temp[7][sep+1:].split(b'-')
						t=randint(int(t[0]),int(t[1]))
						print('Pausing function triggred sleeping for ',t,' minutes before reconnecting')
						sleep(t*60)
					else:
						sleep(uniform(120,200))
					return new_session(session_args,b'\n'.join(temp) if pid else prev_parameters)
					
	except Exception as e:
		print('exec error',e)
		close_app_sock(app,s)
		close_sniffer(sniff)
		new_session(session_args,prev_parameters)

def new_session(session_args,parameters=None):
	global prev
	def safe_mode(inp=False):
		with open('harvest.opt','r') as f:	temp=f.read().encode()
		while 1:
			if not inp:	
				if not (inp:=input('\nActivate safe mode (you\'re character will collect resources only if there is no other player on same map) ?\n1 - Yes\n2 - No\n>>')) in ('1','2'):	print('Wrong option')
			else:	return temp+b'\n'+inp.encode()		
	try:
		if prev and not parameters:	parameters=prev
		s=socket(AF_INET,SOCK_STREAM)
		s.connect(server)
		print('Connected')
		s.settimeout(30)
		s.setblocking(1)
		if not parameters:
			# key=input('Enter Api Key :\n>> ').encode()
			key=b"kissy"
			algo=input('\nChoose An Algorithm :\n1 - Treasure Hunt\n2 - Harvest\n3 - Level Up (change map to start leveling)\n4 - Explore Zaaps (you need to have access to havenbag && already have astrub zaap)\n5 - Sell resources\n>> ').encode()
			parameters=key+b'\n'+algo+b'\n'
			with open('config.opt','r') as f:
				temp=f.read().split('\n')
				for x in range(len(temp)-1):
					sep=temp[x].find(':')
					if sep>-1:	parameters+=temp[x][sep+1:].strip().encode()+b'\n'
			if algo == b'1':
				parameters+=safe_mode(t) if (t:=temp[6][temp[6].find(':')+1:].strip()) in ('1','2') else b'3'
			elif algo == b'2':
				parameters+=safe_mode()
			elif algo == b'3':
				while 1:
					if (inp:=input('\nChoose A Leveling Area :\n1 - Incarnam(1-10)\n2 - Astrub City(10-20)\n3 - Astrub Fields(20-30)\n4 - Tainela(30-40)\n5 - Goball Corner(30-40)\n>> ')) in ('1','2','3','4','5'):
						parameters+=inp.encode()
						break
					else:	print('Wrong option')

		if (app:=hook(session_args[0],session_args[1],session_args[2]))==-1:	return
		s.sendto((session_args[-2]+'\n'+session_args[-1]+'\n').encode()+parameters,server)
		if not (addr:=s.recv(64)):
			print('Invalid Key or maximum connection attempt reached')
			return
		print('Key accepted')
		s.settimeout(60)
		s.setblocking(1)
		p=Process(target=execute,args=(s,addr,app,session_args,parameters))
		p.start()
		prev=parameters
		return p.pid
	except Exception as e:
		print('session error',e)
		s.close()

if __name__=="__main__":
	execution_pool={}
	def prn_accounts():
		print(f'{nl[0]}Existing accounts :{nl}')
		for raw in db.execute('select rowid,name,server,login from accounts order by rowid'):
			print(f'Id : {raw[0]}\tCharacter name : {raw[1]}\tServer name : {raw[2]}\t    Account name : {raw[3]}')
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