import argparse
import requests
import Queue
import threading
import pprint
import time
import base64
import cProfile





class QueryWorker(threading.Thread):
    #variable for format: name,timestamp,usersid
    xml_checkfile = '''
    <CheckFileRequest>
      <Args action="11" sourceID="2" sourceIP="192.168.142.151" name="{}" protocol="0">
        <Cluster id="000c29b7c6273590c4563e21d8421c2ebcdb" name="aQBzAGkAMQA1ADAA"/>
        <Zone id="1" name="UwB5AHMAdABlAG0A"/>
      </Args>
      <EventArgs eventType="8192" serverName="aQBzAGkAMQA1ADAALQBhAHUAZABpAHQA" userId="1000000" timeStampMicroSeconds="266451" desiredAccess="0x100081" ntStatus="0x0" timeStamp="{}" userSid="{}" clientIP="192.168.142.20" createDispo="0x1">
      </EventArgs>
    </CheckFileRequest>
    '''

    xml_heartbeat = '''
    <CheckFileRequest>
      <Args action="9" sourceID="2" sourceIP="192.168.142.151" name="aQBzAGkAMQA1ADAALQBhAHUAZABpAHQA">
        <Cluster id="000c29b7c6273590c4563e21d8421c2ebcdb" name="aQBzAGkAMQA1ADAA"/>
      </Args>
    </CheckFileRequest>
    '''


    """Threaded Folder Discovery and Copy"""
    def __init__(self,queue,stats,args,heartbeat=False):
        threading.Thread.__init__(self)
        self.queue = queue
        self.stats = stats
        self.args = args
        self.heartbeat = heartbeat

    def add_stat(self,key,value=1):
        self.stats[key] = self.stats.get(key,0) + value


    def run(self):
        while True:
            work_item = self.queue.get()

            if self.heartbeat:
                data = self.xml_heartbeat
            else:
                name = work_item['name']
                data = self.xml_checkfile.format(name,work_item['timestamp'],work_item['usersid'])

            try:
                start_time = time.time()
                response = requests.put('http://{}:{}/isilon-audit'.format(self.args.ip,self.args.port),data=data,timeout=5)
                response.content
                self.add_stat("data",time.time() - start_time)
                self.add_stat("headers",response.elapsed.total_seconds())
                self.add_stat("success")
            except Exception as ex:
                self.add_stat(type(ex).__name__)

            self.queue.task_done()


def print_stats(stats):
    total = {}
    for thread_stats in stats:
        for item in thread_stats:
            if item in total:
                total[item]+=thread_stats[item]
            else:
                total[item]=thread_stats[item]

    pprint.pprint(total)



def encode_name(name):
    return base64.b64encode(name.encode('utf-16-le'))


def main(args):


    work_queue = Queue.Queue(args.threads*10)
    work_queue_hb = Queue.Queue(args.threads*2)
    stats = []
    stats_hb = []


    #Start up worker threads
    for i in range(args.threads):
        stats.append({})
        t = QueryWorker(work_queue,stats[i],args)
        t.setDaemon(True)
        t.start()

        stats_hb.append({})
        t = QueryWorker(work_queue_hb,stats_hb[i],args,heartbeat=True)
        t.setDaemon(True)
        t.start()
        work_queue_hb.put('')




    start_time = time.time()
    #Generate Workitmes
    base_name = encode_name("/ifs/asdkfj/asdfkadsf/adsfa/asdf/asdf/")
    for i in range(args.count):

        name = base_name + encode_name(str(i))
        sid = "asdfkj23lk-asdfk234-sfasdfkj3-" + str(i)
        work_queue.put({'name':name,'timestamp':3234234,'usersid':sid})
        if i % 100 == 0:
            work_queue_hb.put("")



    work_queue.join()
    work_queue_hb.join()
    total_time = time.time() - start_time

    print('HeartBeat:')
    print_stats(stats_hb)

    print('CheckFile')
    print_stats(stats)

    print("Total time: {}".format(total_time))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip',default='127.0.0.1',help='audit processor endpoint')
    parser.add_argument('--port',default='12228',type=int,help='http listening port')
    parser.add_argument('--threads',default=8,type=int,help='number of threads')
    parser.add_argument('--count',default=5000,type=int,help='number of requests')
    parser.add_argument('--profile',action='store_true',help='profile the bench app')
    args = parser.parse_args()

    if args.profile:
        cProfile.run(main(args))
    else:
        main(args)