import asyncore, socket

class Server(asyncore.dispatcher_with_send):

    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind(("localhost", 11452))
        self.buffer = ''
        self.recvData = ''


    def handle_close(self):
        self.close()

    def handle_read(self):
        print(self.recvfrom(8192))
        self.buffer ='a'

    def handle_write(self):
        pass
        # if self.buffer != '':
        #     sent = self.sendto(self.buffer,("localhost",11452))
        #     self.buffer = self.buffer[sent:]


if __name__ == '__main__':

    The_Server = Server()
    asyncore.loop()
