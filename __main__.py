import threading
from . import server, client

def server():
    server.main()
def client():
    client.main()
 
t1 = threading.Thread(server)
t1.daemon = True

t2 = threading.Thread(client)

t1.start()
t2.start()