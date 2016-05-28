import argparse
import requests
import Queue
import threading
import pprint



class QueryWorker(threading.Thread):
    """Threaded Folder Discovery and Copy"""
    def __init__(self,queue,stats,args):
        threading.Thread.__init__(self)
        self.queue = queue
        self.stats = stats
        self.args = args

    def run(self):


        while True:
            work_item = self.queue.get()

            try:
                response = requests.put('http://{}:{}'.format(args.ip,args.port),data=work_item)







def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip',default='127.0.0.1',help='audit processor endpoint')
    parser.add_argument('--port',default='12228',type=int,help='http listening port')
    parser.add_argument('--threads',default=8,type=int,help='number of threads')
    parser.add_argument('--count',default=50000,type=int,help='number of requests')

    args = parser.parse_args()

    work_queue = Queue.Queue()
    stats = []

    for i in range(args.threads):
        stats.append({})
        stats_burst.append({})
        t = QueryWorker(work_queue,stats[i])
        t.setDaemon(True)
        t.start()

    for i in range(20000):
        work_queue.put("")

    work_queue.join()

    total = {}
    for thread_stats in stats:
        for item in thread_stats:
            if item in total:
                total[item]+=thread_stats[item]
            else:
                total[item]=thread_stats[item]

    print('total:')
    pprint(total)




if __name__ == '__main__':
    main()