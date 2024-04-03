# Remote Keylogger

<img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" alt="Python"><img src="https://img.shields.io/badge/Sqlite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="sqlite">

Remote Keylogger developed in Python 3, captures keystrokes on multiple client systems. It supports remote start and stop of the keylogging process. The server component utilizes SQLite to manage client data, with individual keylogs stored in a designated 'clientfolder' directory for easy retrieval.


## Features

* Multi-Client Support: Simultaneously monitor keystrokes on various client machines from a single server.
* Remote Control: Start and stop the keylogging process on any connected client machine.
* Cross-Platform Compatibility: Designed to run on different operating systems, ensuring wide usability.



## Installation

Ensure Python 3.x is installed on your system before proceeding with the setup. Follow these steps to install and configure the MultiClient Remote Keylogger:

Run the following command to install the necessary Python packages.

`
  pip install -r requirements.txt
`


## Usage 

* Start the Server: Run the server program to start the interactive shell and send commands to the client.
* Access the Client: Run the client program to connect to the server.


```

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

```



## Disclaimer

This code is intended for educational and informational purposes only. Use it responsibly and ensure compliance with applicable laws and regulations. Respect the privacy and security of others.  
The author of this code assume no liability and is not responsible for misuses or damages caused by any code contained in this repository in any event that, accidentally or otherwise, it comes to be utilized by a threat agent or unauthorized entity as a means to compromise the security, privacy, confidentiality, integrity, and/or availability of systems and their associated resources. In this context the term "compromise" is henceforth understood as the leverage of exploitation of known or unknown vulnerabilities present in said systems, including, but not limited to, the implementation of security controls, human or electronically-enabled.

