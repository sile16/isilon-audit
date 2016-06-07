'''
Isilon Example Auditing Script
'''

import sys
import logging
import traceback
import xml.etree.ElementTree as ET
import defusedxml.ElementTree as defusedET
import pylru
import base64

import falcon
from wsgiref import simple_server
from wsgiref.simple_server import WSGIRequestHandler

class UserEventCount(object):
    """
    This is a sliding window that keeps track of how many events are
    triggers over a number of buckets.
    """

    def __init__(self,file_cache_count = 200,threshold=1000,buckets=60):
        self.file_cache = pylru.lrucache(file_cache_count)
        self.buckets = buckets
        self.threshold = threshold
        self.event_index = 0
        self.event_counts = {}
        self.event_total = 0

    def increment_event_count(self):
        #increment key with a default value of 0, and increment our running total
        self.event_counts[self.event_index] = self.event_counts.get(self.event_index,0) + 1
        self.event_total+=1

    def new_event_over_threadhold(self,event):
        #returns None if not in list, doesn't not genearate key error
        last_seen = self.file_cache.get(event)

        #if not in cache or hasn't been seen since greater than our window we increment
        if last_seen is None or (self.event_index - last_seen) > self.buckets:
            self.increment_event_count()

        #Always update the file cache with the current_index
        self.file_cache[event] = self.event_index

        #check if over threshold.
        if self.event_total > self.threshold:
            return True
        return False

    def next_bucket(self):
        self.event_index+=1
        old_event_index = self.event_index - self.buckets
        if old_event_index >= 0 :
            #pop old bucket off stack and decrement our running Total
            #default value of 0 as this key may not exist
            self.event_total = self.event_counts.pop(old_event_index,0)


class CryptoLockerDetect(object):
    def __init__(self,email="sile16@gmail.com",user_count=1000):
        """
        email alert email
        users number of users to track
        files number of recent file to track_sid
        threshold for generating an alert
        bucket = for each time frame to track file writes
        windows = number of buckets to track, window in seconds = window * bucket
        """

        self.user_cache = pylru.lrucache(user_count)
        self.logger = logging.getLogger()



    def parse_check_event(self,check_event_xml):
        #Check Event can have mulitple events
        args = check_event_xml[0]
        eventargs = check_event_xml[1]


        #print(ET.dump(check_event_xml))
        path = base64.b64decode(args.attrib['name']).decode('utf-16-le')

        if 'bytesWritten' in eventargs.attrib and int(eventargs.attrib['bytesWritten']) > 0:
            self.logger.debug(path)
            self.logger.debug(eventargs.attrib)
            self.logger.debug(eventargs.text)
            self.logger.debug(eventargs.tail)


        if eventargs.attrib['eventType'] == '2':
            timeStamp = eventargs.attrib['timeStamp']
            path = eventargs.text
            sid = eventargs.attrib['userSid']

            user = self.user_cache.get(sid)
            if user is None:
                #User not in cache, create a new user
                user = UserEventCount()

            if user.new_event_over_threadhold(path):
                #toodo
                #Send Alert!!!
                self.logger.warning("User over threashold!!")

            self.user_cache[sid] = user








class AuditResource(object):
    xml_response_text = '<CheckFileResponse status="0x0" />'

    def __init__(self):
        #logging
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        self.logger = logging.getLogger()

        self.cld = CryptoLockerDetect()
        self.logger.info("Starting")


    def on_get(self, req, resp):
        """Handles GET requests"""
        resp.content_type = 'text/html'
        resp.body = "<p>Isilon-Audit Server</p>"

    def on_put(self, req, resp):
        """ Format coming from Isilon:
        xml_doc = '<CheckFileRequest><Args %s><Cluster %s/><Zone %s/></Args><%s %s>%s%s</%s></CheckFileRequest>' % (args_str,
         cluster_str,
         zone_str,
         eventArgs_tag,
         eventArgs_str,
         partialPath_str,
         newPartialPath_str,
         eventArgs_tag)"""


        raw_content = req.stream.read()
        try:
            content = defusedET.fromstring(raw_content)
        except Exception as ex:
            raise falcon.HTTPBadRequest('Bad request: {}'.format(raw_content), str(ex))

        try:
            resp.content_type = 'text/xml; charset=utf-8'
            args = content.find('Args')

            if args.attrib['action'] == '11':
                resp.status = falcon.HTTP_200
                logging.debug("checkevent")
                self.cld.parse_check_event(content)
                resp.body = self.xml_response_text

            elif args.attrib['action'] == '9':
                logging.debug('Registration Request Received')
                #filter='<Filter protocol="0">'
                resp.body = self.xml_response_text

            else:
               logging.error("Request unknown action: {0}".format(args.attrib['action']))

        except Exception as ex:
            self.logger.error(traceback.print_exc())
            self.logger.error('Request: {}'.format(raw_content))



app = falcon.API()
app.add_route('/isilon-audit', AuditResource())

if __name__ == '__main__':

    class NoLoggingWSGIRequestHandler(WSGIRequestHandler):
        def log_message(self, format, *args):
            pass

    httpd = simple_server.make_server('', 12228, app,handler_class=NoLoggingWSGIRequestHandler)
    httpd.serve_forever()
