import os
import sqlite3
from prettytable import from_db_cursor
from prettytable import PrettyTable



class SqliteHandler:


    # creates database where connected client info will be stored
    def create_db(self, client_db, db_table_name):
        try:
            database_conn_object = sqlite3.connect(client_db, check_same_thread=False)
            cursor = database_conn_object.cursor()
            # creates table if it does not exist
            cursor.execute("""CREATE TABLE IF NOT EXISTS {}(
                                Client_ID INTEGER PRIMARY KEY NOT NULL,
                                Date_Joined DATETIME DEFAULT CURRENT_TIMESTAMP,
                                IP_Address TEXT NULL,
                                Mac_Address TEXT NULL,
                                Node_Name TEXT NULL,
                                Platform TEXT NULL,
                                Release TEXT NULL,
                                Processor TEXT NULL,
                                File_Name TEXT NULL
                                );
                                """.format(db_table_name))
            database_conn_object.commit()  # commits changes to database
            print("[+]Database Created!!!")
            return database_conn_object  # socket connection object
        except:
            print("[-]Unable To create database!!!")



    # store client information in database when a new connection is made
    def store_node_data(self, db_conn, conn, fileName, client_sysinfo_list, db_table_name):
        cursor = db_conn.cursor()
       
        # insert client info into sqlite database
        cursor.execute(
            f"INSERT INTO {db_table_name}(IP_Address, Mac_Address, Node_Name, Platform, Release, Processor, File_Name) VALUES(?, ?, ?, ?, ?, ?, ?)",
            (str(client_sysinfo_list[0]), str(client_sysinfo_list[1]),
             str(client_sysinfo_list[2]), str(client_sysinfo_list[3]),
             str(client_sysinfo_list[4]), str(client_sysinfo_list[5]),
             str(fileName)
             ))
        db_conn.commit()  # commit changes

        client_id = cursor.lastrowid
        return client_id



    def update_client_info(self, db_conn, mac_address, new_client_info, db_table_name):
        cursor = db_conn.cursor()
        try:
            # Retrieve the client ID based on the MAC address
            cursor.execute(f"SELECT Client_ID FROM {db_table_name} WHERE Mac_Address=?", (mac_address,))
            result = cursor.fetchone()

            if result:
                client_id = result[0]
                update_columns = ', '.join([f"{column}=? " for column in ["IP_Address", "Mac_Address", "Node_Name", "Platform", "Release", "Processor", "File_Name"]])
                update_values = tuple(new_client_info) + (client_id,)
                cursor.execute(f"UPDATE {db_table_name} SET {update_columns} WHERE Client_ID=?", update_values)
                db_conn.commit()
                print("[+]Client information updated successfully!")
                return client_id
            else:
                print("[-]Client with the specified MAC address not found!")

        except sqlite3.Error as e:
            print(f"[-]Error updating client information: {e}")

        finally:
            cursor.close()




    def check_mac_address_exists(self, mac_address, db_conn, db_table_name):
        cursor = db_conn.cursor()
        cursor.execute(f"SELECT * FROM {db_table_name} WHERE Mac_Address=?", (mac_address,))
        result = cursor.fetchone()  # Fetch a single row

        if result:
            return True
        else:
            return False



    def get_nodes_info(self, db_conn, client_conn_object, db_table_name):
        cursor = db_conn.cursor()
        clients_to_remove = [] # Create a list of client IDs to remove
        
        for client_id, connections in client_conn_object.items():
            try:
                connections[0].send("conn check".encode()) # Check if connection is still active
            except Exception as e:
                clients_to_remove.append(client_id) # If not connected mark for removal
        
        # Remove disconnected clients from dictionary
        for client_id in clients_to_remove:
            client_conn_object.pop(client_id)

        # Retrieve all client information from the database
        cursor.execute(f"SELECT * FROM {db_table_name}")
        connected_clients = from_db_cursor(cursor)  # Insert retrieved client information into a table
        print(connected_clients)




    def fetch_all_data(self, client_db, db_conn, db_table_name):
        try:
            cursor = db_conn.cursor()
            cursor.execute(f"SELECT * FROM {db_table_name}")
            rows = cursor.fetchall() # Fetch all rows from the result set

            table = PrettyTable() # Create a PrettyTable object
            table.field_names = [description[0] for description in cursor.description] # Add column names to the table
            for row in rows:
                table.add_row(row)
            
=
            print(table)
        except sqlite3.Error as error:
            print("[-]Error occurred while fetching data:", error)



    def remove_client_from_db(self, db_conn, client_id, db_table_name, client_conn_object):
        cursor = db_conn.cursor()
        try:
            # check if client_id exists in the database
            check_sql = f"SELECT EXISTS(SELECT 1 FROM {db_table_name} WHERE Client_ID = ?)"
            cursor.execute(check_sql, (client_id,))
            exists = cursor.fetchone()[0]

            if exists:
                # Delete a row with client ID from the table
                delete_sql = f"DELETE FROM {db_table_name} WHERE Client_ID = ?" 
                cursor.execute(delete_sql, (client_id,))
                db_conn.commit()

                if client_id in client_conn_object:
                    client_conn_object.pop(client_id)

                print(f"[+]Client with ID {client_id} has been successfully removed from the database!")
            else:
                print(f"[-]Client with ID {client_id} does not exist in the database!")

        except Exception as e:
            print(f"[-]An error occurred while trying to remove client with ID {client_id}: {e}")
        finally:
            cursor.close()




    def remove_all_clients_from_db(self, db_conn, db_table_name, client_conn_object):
        cursor = db_conn.cursor()
        try:
            
            sql = f"DELETE FROM {db_table_name}" # delete all rows from the table
            cursor.execute(sql)
            db_conn.commit()
            client_conn_object.clear()
            print(f"[+]All clients have been successfully removed from the {db_table_name} table!")

        except Exception as e:
            print(f"[-]An error occurred while trying to remove all clients: {e}")

        finally:
            cursor.close()



    # print out the contents of text file
    def get_log_content(self, client_id, client_folder, db_conn, db_table_name):
        cursor = db_conn.cursor()
        cursor.execute(f"SELECT File_Name FROM {db_table_name} WHERE Client_ID=?", (client_id,))
        result = cursor.fetchall()

        if result:
            fileName = result[0][0] 
            filePath = os.path.join(client_folder, fileName)

            if os.path.exists(filePath):
                with open(filePath, "r") as logFile:
                    for log in logFile.readlines():
                        print(log, end='')
            else:
                print("[-]Client log file does not exists!")

        else:
            print("[-]Client does not exists!")

