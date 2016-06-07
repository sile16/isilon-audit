import asyncio
import argparse
from aiohttp import ClientSession
import signal
import pprint
import cProfile
import sys
import base64
import time
import traceback

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

def encode_name(name):
    return base64.b64encode(name.encode('utf-16-le')).decode('utf-8')

base_name = "/ifs/asdkfj/asdfkadsf/adsfa/asdf/asdf/"
base_name_encoded = encode_name(base_name)


class AsyncBench(object):

    def __init__(self):
        self.stats = {}
        self.static_data = xml_checkfile.format(base_name_encoded,str(2342342),"asdfasdfa")


    def add_stat(self,key,value=1):
        self.stats[key] = self.stats.get(key,0) + value


    async def check_file(self,sem, url, i):
        # getter function with semaphore
        async with sem:
            #name = encode_name(base_name + str(i))
            ##name = base_name_encoded + encode_name(str(i))
            #sid = "asdfkj23lk-asdfk234-sfasdfkj3-" # + str(i)
            #timestamp = str(2342342)
            #data = xml_checkfile.format(name,timestamp,sid)
            data = self.static_data

            try:
                start_time = time.time()
                async with ClientSession() as session:
                    async with session.put(url,data=data) as response:
                        await response.read()
                        self.add_stat("data",time.time() - start_time)
                        #self.add_stat("headers",response.elapsed.total_seconds())
                        self.add_stat("success")
                        #self.add_stat(response)
                        return

            except Exception as ex:
                self.add_stat(type(ex).__name__)
                print(traceback.print_exc())


    async def send_heartbeat(self,url):
        async with ClientSession() as session:
            async with session.put(url,data=xml_heartbeat) as response:
                delay = response.headers.get("DELAY")
                date = response.headers.get("DATE")
                print("{}:{} with delay {}".format(date, response.url, delay))
                return await response.read()


    async def run_queries(self, loop, args):
        url = "http://{}:{}/{}".format(args.ip,args.port,args.path)
        tasks = []
        # create instance of Semaphore
        sem = asyncio.Semaphore(args.threads)

        for i in range(args.count):
            # pass Semaphore to every PUT request
            task = asyncio.ensure_future(self.check_file(sem, url, i))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        await responses


    async def run_heartbeat(self,loop,args,heartbeat_stats):
        return


def main(args):
    bench = AsyncBench()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(bench.run_queries(loop, args))
    loop.run_until_complete(future)
    pprint.pprint(bench.stats)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip',default='127.0.0.1',help='audit processor endpoint')
    parser.add_argument('--port',default='12228',type=int,help='http listening port')
    parser.add_argument('--path',default='/isilon-audit',help='url path')
    parser.add_argument('--threads',default=8,type=int,help='number of concurrent requests')
    parser.add_argument('--count',default=5000,type=int,help='number of requests')
    parser.add_argument('--profile',action='store_true',help='profile the bench app')
    parser.add_argument('--heartbeat-interval',default=10,type=int,help='interval in seconds in between heartbeats')
    parser.add_argument('--nodes',default=10,type=int,help='number of nodes that generate heartbeats')

    args = parser.parse_args()

    if args.profile:
        cProfile.runctx("main(args)",globals(),locals())
    else:
        main(args)

