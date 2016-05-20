'''
Isilon Example Auditing Script
'''

import sys
import logging
import traceback
import urllib
import xml.etree.ElementTree as etree
from twisted.web import server, resource
from twisted.internet import reactor

#logging
logging.basicConfig(filename='/audit.log', level=logging.INFO)

def track_sid(sid):


def parse_check_event(check_event_xml):
    #Check Event can have mulitple events
    check_event = etree.fromstring(check_event_xml)
    events = check_event.findall('EventList/Event')

    for event in events:
        logging.info("{}: {}".format(event.tag,event.attrib))
        for detail in event.getchildren():
            #sub events are Cluster and Zone
            logging.info("{}: {}".format(detail.tag,detail.attrib))

        if 'event' in event.attrib:
            eventid = event.attrib['event']
            #File Write event
            if eventid == '0x1':
                timestamp = int(event.attrib['timestamp'][0:-8],16)





        cluster = event.find('Cluster')
        zone = event.find('Zone')





class CepaResource(resource.Resource):

    isLeaf = True

    def _response(self,message,request):
        bytebuf = message.encode("utf-16")
        request.setResponseCode(200)
        request.setHeader('Content-Length', len(bytebuf))
        request.setHeader('Content-Type', 'text/xml; charset=utf-16')
        request.write(bytebuf)


    def render_PUT(self,request):
        if request.path == '/':
            try:
                content = request.content.read()
                content_decoded = urllib.unquote(content).decode("utf-16")

                if '<CheckEventRequest>' in content_decoded:
                    logging.info("checkevent")
                    logging.debug(content_decoded)
                    response_content = 'ntStatus=0&xml=<CheckEventResponse />'
                    parse_check_event(content_decoded)
                    self._response(response_content,request)

                elif '<HeartBeatRequest />' in content_decoded:
                    logging.debug("HeartBeatRequest")
                    response_content = 'hbStatus=0&xml=<HeartBeatResponse />'
                    self._response(response_content,request)

                elif '<RegisterRequest />' in content_decoded:
                    logging.info('Registration Request Received')
                    #filter='<Filter protocol="0">'
                    response_content = '<RegisterResponse><EndPoint guid="8bff877d-39bd-4b56-80ce-8b7884711d3f" friendlyName="Splunk" version="1.0" desc="Detect CryptoLocker" /><EventTypeFilter value="0xFFFFFFFFFFFFFFFFFFFFFFFF" adminEvents="0x80000000" /></Filter></RegisterResponse>'
                    self._response(response_content,request)

                else:
                   logging.error("Request unknown: {0}".format(content_decoded))

            except:
                    e = sys.exc_info()[1]
                    logging.error("Error : {0}".format(content_decoded))
                    logging.error(traceback.format_exc())
        else:
            logging.error("Path {} is not recognized".format(self.path))


def main():
    logging.info("Starting")
    try :
        reactor.listenTCP(12229, server.Site(CepaResource()),interface="127.0.0.1")
        reactor.run()
    except:
        e = sys.exc_info()[1]
        logging.error("Error: {}".format(str(e)))


if __name__ == '__main__':
    main()
