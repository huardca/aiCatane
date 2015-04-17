import urllib
import urllib2
from multiprocessing import Pipe, Lock
from Queue import Queue
import multiprocessing as mp
import os

# Wannabe factory to create the sender and start it synchronously
def init_sender(pipe, collection):
    sender = Sender(pipe, collection)
    sender.sender_proc()

class Sender:

    def __init__(self, pipe, collection):
        self.pipe = pipe
        self.collection = collection

    # Save to database
    def send_data(self, resourceValues, info):
        for i in info:
            if i[1]:
                # Save to database
                url = 'http://step.polymtl.ca/~alexrose/catane/catane.php?b='
                url += str(resourceValues[0])
                url += '&a='
                url += str(resourceValues[1])
                url += '&w='
                url += str(resourceValues[2])
                url += '&m='
                url += str(resourceValues[3])
                url += '&l='
                url += str(resourceValues[4])
                url += '&s='
                url += str(i[2])
                url += '&col='
                url += self.collection
                url += '&results='
                url += urllib.quote(str(info))

                response = urllib2.urlopen(url=url, timeout=120)
                html = response.read()
                response.close()

                # f = file('out.txt', 'a')
                # f.write("HTTP SENT " + url + os.linesep)
                # f.close()

    # Main function for sending process
    # With this method, we wont crash on http timeout
    # We'll reduce load on the server with only one process sending requests per machine
    # We won't slow the game execution down by waiting on HTTP requests to complete
    def sender_proc(self):
        # Create message queue
        q = mp.Manager().Queue()

        # f = file('out.txt', 'a')
        # f.write("Running sender_proc" + os.linesep)
        # f.close()

        proc = mp.Process(target=self.sender_loop, args=(q,))
        proc.start()

        # This loops reads from the pipe and immediately push data in the queue
        while(True):
            val, info = self.pipe.recv()
            q.put((val, info))

    def sender_loop(self, q):

        # This loop waits for data to be pushed in the queue
        # and send it to the server
        while(True):
            val, info = q.get()
            try:
                self.send_data(val, info)
                f = file('out.txt', 'a')
                f.write("read from queue" + str(val) + os.linesep)
                f.close()
            except Exception as e:
                print "Error : ", e
