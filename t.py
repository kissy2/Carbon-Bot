from zlib import compress
from sqlite3 import connect
from socket import *
from pywinauto.application import Application
from pywinauto.findwindows import find_elements
from winsound import PlaySound,SND_LOOP,SND_ASYNC,SND_FILENAME,SND_ALIAS
from subprocess import Popen,DEVNULL,PIPE
from multiprocessing import Process
from threading import Thread
from time import sleep,strftime
from platform import release
if win10:=release()=='10':
	from win10toast import ToastNotifier
	notify=ToastNotifier()
global api_args
get_hwnd,get_window,bti,conn,nl,server,api_args=lambda hwnd:Application().connect(handle=hwnd.handle).top_window(),lambda text:find_elements(title_re=f'^{text}'),lambda b:int.from_bytes(b,'big',signed=True),connect('cbd',isolation_level=None),'\n\n',("51.103.139.195", 16969),None
conn.cursor().execute('create table if not exists accounts(login not null,password not null,name not null,server not null,primary key (login, name , server))')


def click(app,x,y,c=1,s=0):
	try:
		for _ in range(c):	app.click(coords=(x,y))
		if s:	sleep(s)
	except RuntimeError as rte:
		print(f'RuntimeError in Click',rte)
		sleep(8)

def press(app,k,s=0):
	try:
		app.send_keystrokes(k)
		if s:	sleep(s)
	except RuntimeError as rte:
		print(f'RuntimeError in Press',rte)
		sleep(8)
	
def alert(app,severity):
	app.set_focus()
	if severity=='high':
		PlaySound(f'./threat_{severity}', SND_LOOP+SND_ASYNC)
		input("MODERATOR NOTIFICATION RESPOND QUICKLY!!!!")
		PlaySound(None,0)
	elif severity=='medium':
		for _ in range(5):
			PlaySound(f'./threat_{severity}', SND_FILENAME)
	elif severity=='low':
		PlaySound("SystemHand", SND_ALIAS)
	app.minimize()

def hook(hook_args,app=None):
	try:
		while Popen(args='REG QUERY HKCU\Environment /v eca',stdout=PIPE,stderr=DEVNULL).communicate()[0][:-1][-2]=='1':
			sleep(2)
			Popen('setx eca 1',stdout=DEVNULL)
		if app:
			app.close()
			sleep(5)
		while not (window:=get_window('Ankama Launcher$')):
			Popen('call "Ankama Launcher"',stdout=DEVNULL,shell=True)
			sleep(30)
		app = Application('uia').connect(handle=window[0].handle).windows()[0]
		app.set_focus()#force repaint
		sleep(1)
		for x in app.children()[0].children():
			if x.get_properties()['texts'][0]=='PLAY':
				break
		while not (window:=get_window('Dofus 2')) and not (window:=get_window(hook_args[-1])):
			x.click()
			sleep(20)
		app.minimize()
		app=get_hwnd(window[0])
		app.move_window(x=-10, y=0, width=1365, height=768, repaint=True)
		app.minimize()
		prev=False
		while not get_window(hook_args[-1]):
			if prev : press(app,'~',s=2)
			click(app,650,230,c=3,s=2)
			press(app,hook_args[0],s=2)
			press(app,'{TAB}',s=2)
			press(app,hook_args[1],s=2)
			press(app,'~',s=20)
			prev=True
		return window[0]
	except Exception as e:
		print('Hooking dofus client failed ',e)
	finally:
		Popen('setx eca 0',stdout=DEVNULL)

def sniffer(conn,gsa,pid):
	try:
		s,next_seq,wait,last10=socket(AF_INET,SOCK_RAW),None,[],[]
		for x in Popen("netstat -no",stdout=PIPE,stderr=DEVNULL).communicate()[0][:-1].split(b'\r\n')[4:]:
			if (b'5555' in x or b'443' in x) and pid in x:
				client_port=int.to_bytes(int(x[(t:=x.find(b':')+1):x.find(b' ',t)]),2,'big')
		s.bind((gethostbyname(gethostname()),0))
		s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
		s.ioctl(SIO_RCVALL, RCVALL_ON)
		while 1:
			idata,addr=s.recvfrom(65565)
			if addr[0]==gsa:
				rdata=idata[20:]
				if rdata[2:4]!= client_port:	continue
				data=rdata[(rdata[12]>>4)*4:]
				seq=int.from_bytes(rdata[4:8],'big')
				if seq in last10:	continue
				if data:
					last10=last10[-9:]+[seq]
					if next_seq and  seq != next_seq:	
						wait.append((seq,data))
					elif wait:
						wait.append((seq,data))
						wait.sort(key=lambda w: w[0])    
						for i in wait:	
							conn.sendto(len((compressed:=compress(i[1]))).to_bytes(2,'big')+compressed,server)
						next_seq,wait=i[0]+len(i[1]),[]
					else:
						next_seq=seq+len(data)
						if data:	
							conn.sendto(len(compressed:=compress(data)).to_bytes(2,'big')+compressed,server)
	except Exception as e:
		print('sniffer error',e)
	finally:
		s.close()

def execute(s,addr,window):
	app=get_hwnd(window)
	thread=Thread(target=sniffer,args=(s,addr,str(window.process_id).encode()))
	thread.start()
	try:
		while (data:=s.recv(1024)):
			#check app
			for p in data[:-3].split(b'$$$'):
				if (args:=p.split(b'\n'))[0]==b'c':
					click(app,bti(args[1]),bti(args[2]),bti(args[3]))
				elif args[0]==b'p':
					press(app,args[1].decode())
				elif args[0]==b'a':
					alert(app,args[1].decode())
				elif args[0]==b'n' and win10:
					notify.show_toast((x:=args[1].decode()),(y:=args[2].decode()),duration=30,threaded=True)
					r=open("notifications.txt","a+")
					r.seek(0,0)
					r=r.read()
					with open('notifications.txt','w') as f:
						f.seek(0,0)
						f.write('%s : %s , %s\n'%(x,strftime("%A, %d %B %Y %I:%M %p"),y)+r)
	except Exception as e:
		print('exec error',e)
		s.close()
		#close app & sniffer thread

def new_session(session_args):
	global api_args
	try:
		app=hook(session_args[:-1])
		s=socket(AF_INET,SOCK_STREAM)
		s.connect(server)
		print('Connected')
		s.settimeout(900)
		s.setblocking(1)
		if not api_args:	api_args=(input('Enter Api Key :\n>> ')+'\n'+(pi:=input('Choose An Algorithm :\n1 - Treasure Hunt\n2 - Level Up (change map to start leveling)\n3 - Explore Zaaps (you need to have access to havenbag && already have astrub zaap)\n>> '))+'\n'+(input('Choose A Leveling Area :\n1 - Incarnam(1-10)\n2 - Astrub City(10-20)\n3 - Astrub Fields(20-30)\n4 - Tainela(30-40)\n5 - Goball Corner(30-40)\n>> ') if pi=='2' else '0')).encode()
		s.sendto((session_args[-2]+'\n'+session_args[-1]+'\n').encode()+api_args,server)
		if not (addr:=s.recv(64).decode()):
			print('Invalid Key or maximum connection attempt reached')
			return
		print('Key accepted')
		Process(target=execute,args=(s,addr,app)).start()
	except timeout:
		print('Server not responding')
		s.close()
	except Exception as e:
		print('session error',e)
		s.close()

if __name__=="__main__":
	while 1:
		db=conn.cursor()
		def prn_accounts():
			print(f'{nl[0]}Existing accounts :{nl}')
			for raw in db.execute('select rowid,name,server,login from accounts'):
				print(f'Id : {raw[0]}\tCharacter name : {raw[1]}\tServer name : {raw[2]}\tAccount name : {raw[3]}{nl}')
		try:
			if (i:=input(f'{nl[0]}Welcome to carbon bot choose one of options below :{nl}1 - Launch all accounts in the database{nl}2 - Launch specific accounts from the database{nl}3 - Add new accounts to the database{nl}4 - Delete accounts from the database{nl}5 - Show existing accounts{nl}>> '))=='1':
				for row in db.execute('select * from accounts'):
					new_session(row)
				break
			elif i=='2':
				prn_accounts()
				for row in db.execute("select * from accounts where rowid in {}".format( tuple(t) if len(t:=input(f"Enter the Ids (seperated by a comma ',' ) of the accounts you want to run{nl}>> ").split(','))>1 else f'({t[0]})')):
					new_session(row)
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
			db.close()
		except Exception as e:
			print('\n-------------------------------------------\nOperation failed : ',e,'\n-------------------------------------------\n')
		finally:
			db.close()