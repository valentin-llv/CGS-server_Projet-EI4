import queue, socket

# Trick to add queue to select.select
class PollableQueue(queue.Queue):
    def __init__(self):
        super().__init__()

        # Compatibility on non-POSIX systems
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 0))
        server.listen(1)

        self.putsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.putsocket.connect(server.getsockname())
        self.getsocket, _ = server.accept()

        server.close()

    def fileno(self):
        return self.getsocket.fileno()

    def put(self, item):
        super().put(item)
        self.putsocket.send(b'x')

    def get(self):
        self.getsocket.recv(1)
        return super().get()