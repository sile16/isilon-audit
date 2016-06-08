import asyncio
import argparse
import aiohttp
import cProfile
import base64
import time
import traceback
from stats import Stats


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
    def __init__(self,args):
        self.stats = Stats()
        self.url = "http://{}:{}/{}".format(args.ip,args.port,args.path)

        # create instance of Semaphore
        self.sem = asyncio.Semaphore(args.threads)
        self.loop = loop = asyncio.get_event_loop()
        self.stats = Stats()
        self.heartbeat_stats = Stats


    async def send_command(self, data, stats):
        # getter function with semaphore
        async with self.sem:
            try:
                start_time = time.time()
                with aiohttp.Timeout(5):
                    async with aiohttp.put(url,data=data) as response:
                        await response.read()
                        stats.add("data",time.time() - start_time)
                        stats.add("success")
                        return

            except Exception as ex:
                stats.add(type(ex).__name__)
                print(traceback.print_exc())

    async def queue_requests(self):
        for i in range(args.count):
            async with self.sem:
                name = encode_name(base_name + str(i))
                sid = "asdfkj23lk-asdfk234-sfasdfkj3-" + str(i)
                timestamp = str(2342342)
                data = xml_checkfile.format(name,timestamp,sid)
                asyncio.ensure_future(self.send_command(data,self.stats))


        self.loop.stop()





    async def run_heartbeats(self,):


        await asyncio.sleep(10):
            async def queue_heartbeats(self):

        return


    def run(self):
        asyncio.ensure_future(self.run_heartbeats())
        asyncio.ensure_future(self.run_queries())
        self.loop.run_forever()
        print()


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
        cProfile.runctx("AsyncBench(args).run()",globals(),locals())
    else:
        AsyncBench(args).start()

