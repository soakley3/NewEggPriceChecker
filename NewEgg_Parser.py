#
# NewEgg price checking script.
# Edit the URLs 

__author__="lucas"
__date__ ="$Nov 24, 2010 11:52:39 PM$"  #updated in 2023 for python 3 

import os
import urllib.request
import threading
import time
import queue
import subprocess
import sys


urls = ['https://www.newegg.com/intel-core-i7-12700k-core-i7-12th-gen/p/N82E16819118343?Item=N82E16819118343&cm_sp=gift-idea-trending-item',
            'https://www.newegg.com/msi-geforce-rtx-4070-rtx-4070-ventus-3x-12g-oc/p/N82E16814137789?Item=N82E16814137789&cm_sp=Dailydeal_SS-_-14-137-789-_-06162023']
    
time_between = 1 # amount in seconds to wait before checking the site again.


shutdown_event = threading.Event()

class NeweggCheck(threading.Thread):
    def __init__(self, url, timecheck=30):
        threading.Thread.__init__(self)
        self.url, self.timecheck = url, timecheck

    def sleep(self, sleep_time):
        '''
        Sleeps the thread, but also checks for the shutdown signal. sleep_time is in
        seconds.
        '''
        wait_time = time.time() + (sleep_time)
        while time.time() < wait_time and not shutdown_event.is_set():
            time.sleep(0.016)
   

    def run(self):
        '''
        Main loop of the thread - parses the NewEgg page and determines
        the price of the item. It will then wait the specified amount of seconds
        and then check the price again. If it differs from the previous check
        then add the announcement to the speech thread, this way if multiple
        prices change simultaneously, then the speech wont be garbled.
        '''
        print('thread started', self.url)
        price = 0
        while not shutdown_event.is_set():
            # read the page into a list of bytes
            try:
               #print("getting page")
                lines = urllib.request.urlopen(self.url).readlines()
                #print("lines: ", lines)
            except (KeyboardInterrupt, SystemExit):
                #print("exception 1 getting page.")
                pass
            except Exception as e:
                #print("exception 2 getting page.")
                #print("Exception e: ", e)
                self.sleep(self.timecheck)
                continue

            # Check each line for that line above
            found = False

            for line in lines:
                # We have to see if the byte pattern matches, since `lines` is a list of bytes
                if (b'price-current-label' in line):
                    parseable = line.decode("utf-8") # newegg site is encoded with UTF 8 // <meta charSet="utf-8"/>
                    # The price can be found in the page in the "price-current-label" html. 
                    price_string = parseable[parseable.find("price-current-label")+37: parseable.find('</strong><sup>') ]
                    price_float = float(price_string)

                    if price != price_float:
                        # add the speech into the speech queue
                        speechThread.add_speech("'the. prices. have. updated. . . It. is. now. %s'" % price_string)

                        print('Price of', self.url, 'has changed')
                        price = price_float
                        # write out the price and the URL for logging purposes to newegg.txt
                        # This appends so that the file is not overwritten from a previous run. 
                        f = open('newegg.txt', 'a')
                        f.write(price_string+' '+self.url+'\n')
                        f.close()
                    found = True
                    break
            if not found:
                print('POSSIBLE PRICE CHANGE, CANNOT FIND PRICE', self.url)
                speechThread.add_speech("espeak 'possible price. change'")
            self.sleep(self.timecheck)


class SpeechQueue(threading.Thread):
    '''
    Thread to make speech un-garbled.
    This way multiple NewEggCheck threads won't try speaking 
    at the same time, causing garbled speech. This is queue 
    so that the speech is FIFO.
    '''

    def __init__(self,min_wait=0.016):
        threading.Thread.__init__(self)
   
        self.queue = queue.Queue()
        if min_wait < 0.016:
            self.min_wait = 0.016
        else:
            self.min_wait = min_wait

    def add_speech(self, speech):
        '''
        Adds the speech into the queue to be spoken later.
        '''
        self.queue.put(speech)

    def run(self):
        print('started speech thread ..')
        subprocess.call(['espeak-ng', 'Starting speech thread'])
        while not shutdown_event.is_set():
            if not self.queue.empty():
                words = self.queue.get()
                # create subprocess to speak.
                subprocess.call(['espeak-ng', "'%s'"%words])
            time.sleep(self.min_wait)


if __name__ == "__main__":

    thread_list = []

    # start the speech thread
    speechThread = SpeechQueue()
    speechThread.start()

    #start the price check threads
    for url in urls:
        thread_list.append(NeweggCheck(url, timecheck=time_between))
        thread_list[len(thread_list)-1].start()

    try:
        while True:
            time.sleep(0.016)
    except (KeyboardInterrupt, SystemExit):
        shutdown_event.set()

    while speechThread.is_alive():
        time.sleep(0.016)
    print("speech thread killed.")

    for th in thread_list:
        while th.is_alive():
            time.sleep(0.016)
    print("killed all price threads.")

    print("Terminated successfully")

    sys.exit(0)