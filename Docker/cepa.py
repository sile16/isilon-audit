'''
Isilon Example Auditing Script
'''

import sys
import logging
import traceback
import urllib
import xml.dom.minidom
import xml.sax.saxutils
from twisted.web import server, resource
from twisted.internet import reactor

#set up logging
logging.basicConfig(filename='/audit.log', level=logging.INFO)

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
                put_body = request.content.read()
                put_body_decoded = urllib.unquote(put_body).decode("utf-16")

                if '<RegisterRequest />' in put_body_decoded:
                    logging.info('Registration Requst Received')
                    response_content = '<RegisterResponse><EndPoint guid="8bff877d-39bd-4b56-80ce-8b7884711d3f" friendlyName="Splunk" version="1.0" desc="Detect CryptoLocker" /><Filter protocol="0"><EventTypeFilter value="0xFFFFFFFFFFFFFFFFFFFFFFFF" adminEvents="0x80000000" /></Filter></RegisterResponse>'
                    self._response(response_content,request)

                elif '<HeartBeatRequest />' in put_body_decoded:
                    logging.debug("CEPA:HeartBeatRequest")
                    response_content = 'hbStatus=0&xml=<HeartBeatResponse />'
                    self._response(response_content,request)

                elif '<CheckEventRequest>' in put_body_decoded:
                    logging.info("CEPA:checkevent")
                    logging.info(put_body_decoded)
                    response_content = 'ntStatus=0&xml=<CheckEventResponse />'
                    self._response(response_content,request)

                else:
                   logging.error("PUT request unknown: {0}".format(put_body_decoded))

            except:
                    e = sys.exc_info()[1]
                    logging.error("Error : {0}".format(put_body_decoded))
                    logging.error(traceback.format_exc())
        else:
            logging.error("Path {} is not recognized".format(self.path))


def main():
    logging.info("Starting")
    try :
        reactor.listenTCP(12229, server.Site(CepaResource()),interface="127.0.0.1")
        reactor.run()

    except: # catch *all* exceptions
        e = sys.exc_info()[1]
        logging.error("Error: %s" % str(e))


if __name__ == '__main__':
    main()
