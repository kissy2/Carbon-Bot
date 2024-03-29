if __name__ == '__main__':
    from server_start import launch_in_process as f
    from multiprocessing import Process
    from threading import Thread
    from socket import *
    from functools import reduce

    global connected


    def launch_in_thread(conn):
        global connected
        try:
            conn.settimeout(30)
            conn.setblocking(1)
            client_name, server_name, client_key, parameters = (cts := conn.recv(1024).decode().split('\n'))[0], cts[1], \
                                                               cts[2], cts[3:]
        except:
            conn.close()
            print('Invaled session arguments or took more than 30 seconds to send api key')
            return
        conn.settimeout(700)
        conn.setblocking(1)
        if client_key in keys:
            if client_key in connected:
                if connected[client_key] >= keys[client_key]:
                    conn.close()
                    print('Maximum connection limit reached with this key : ', client_key)
                    return
            else:
                connected[client_key] = 0
            connected[client_key] += 1
            print('Connected clients : ', reduce(lambda x, y: x + y, connected.values(), 0), '\n', connected)
            p = Process(target=f, args=(conn, client, client_name, server_name, parameters))
            p.start()
            p.join()
            connected[client_key] -= 1
            if not connected[client_key]:    del connected[client_key]
            print('Connected clients : ', reduce(lambda x, y: x + y, connected.values(), 0), '\n', connected, '\n')
        else:
            conn.close()


    print('Initiating new session')
    s, connected, keys = socket(AF_INET, SOCK_STREAM), {}, {'kissy': 1000}
    s.bind((gethostbyname(gethostname()), 16969))
    print(gethostbyname(gethostname()))
    s.listen(1000)  # maximum number of simultaneous connections
    while 1:
        print('Waiting for connection from carbon bot client')
        conn, client = s.accept()
        print('Connected by', client[0])
        Thread(target=launch_in_thread, args=(conn,)).start()
    s.close()
