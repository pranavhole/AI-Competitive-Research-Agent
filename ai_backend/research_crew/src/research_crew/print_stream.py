import sys
import asyncio

class PrintInterceptor:
    def __init__(self, queue):
        self.queue = queue
        self.original_write = sys.stdout.write

    def write(self, msg):
        if msg.strip():
            try:
                self.queue.put_nowait(msg)
            except:
                pass
        self.original_write(msg)

    def flush(self):
        pass

    def start(self):
        sys.stdout.write = self.write

    def stop(self):
        sys.stdout.write = self.original_write
