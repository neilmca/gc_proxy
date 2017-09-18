#!/usr/bin/python
#


import logging
from cgi import parse_qs
from datetime import datetime
import re
import random
import os
import string
import urllib2
from urlparse import urlparse
import json
import webapp2
from basehandler.basehandler import BaseHandler
from model.forward_mappings import ForwardMappings
import StringIO
import http_access

class EchoHandler(BaseHandler):
    """Handles search requests for comments."""

    def get(self):
        """Handles a get request with a query."""
        try:
            try:
                sio = StringIO.StringIO()
                sio.write('====BEGIN REQUEST=====\n')
                sio.write(self.request.method)
                sio.write(' ')
                sio.write(self.request.path)
                sio.write(' ')
                sio.write('\n')
                for key, value in self.request.headers.items():
                    sio.write(key + ':' + value +'\n')
                sio.write('\n')
                sio.write('\n')
                sio.write('====END REQUEST=======\n')
                logging.info(sio.getvalue())                
                self.response.headers['Content-Type'] = 'text/plain'
                self.response.headers['Content-Length']  = str(len(sio.getvalue()))
                self.response.write(sio.getvalue())
                return
            finally:
                sio.close()
        except IOError:
            self.response.set_status(404)

    def post(self):
        """Handles a get request with a query."""

        self.response.write('post response')

class ReverseProxyHandler(BaseHandler):
    """Handles search requests for comments."""

    @staticmethod
    def log_method(title, end, from_url, to_url, method, url, headers, content):
        sio = StringIO.StringIO()
        try:
            sio.write('\n')            
            sio.write(title)
            sio.write('\n')
            sio.write('from: ')
            sio.write(from_url)
            sio.write('\n')
            sio.write('to: ')
            sio.write(to_url)
            sio.write('\n\n')
            sio.write(method) 
            sio.write(' ')
            sio.write(url)
            sio.write('\n\n')                
            for key, value in headers.items():
                sio.write(key + ':' + value +'\n')
            sio.write('\n\n')
            if content != None and content != '':
                sio.write('body truncated (128):\n')
                sio.write(content[:128])
            sio.write('\n')
            sio.write(end)
            sio.write('\n\n')
            logging.info(sio.getvalue())
        finally:
            sio.close()

    def get(self):
        """Handles a get request with a query."""
        sent = False
        try:
            forwarding_url = ForwardMappings.get_forward_to_url(self.request.path)
            if forwarding_url == None:
                #no mapping found so quite
                self.response.write('could not find forwarding mapping for : {}'.format(str(self.request.path)))
                self.response.set_status(404)
                return


            url = '{}{}'.format(forwarding_url, self.request.path)
            ReverseProxyHandler.log_method('====REVERSE PROXY REQUEST=======\n', '====END PROXY REQUEST=======\n', self.request.host, forwarding_url, self.request.method, url, self.request.headers, self.request.body)               
            
            #pass onto to destination url
            resp_code, resp_content, resp_headers = http_access.fetch_get(url, self.request.headers, None)
            self.response.set_status(resp_code)
            for key, value in resp_headers.items():
                self.response.headers[key] = value
            sent = True
            ReverseProxyHandler.log_method('====REVERSE PROXY RESPONSE=======\n', '====END PROXY RESPONSE=======\n', forwarding_url, self.request.host, self.request.method, self.request.path, self.response.headers, resp_content)               
            self.response.write(resp_content)
            return
            
        except IOError as e:
            if not sent:
                self.response.write('error trying to proxy: {}'.format(str(e)))
                self.response.set_status(404)

    def put(self):
        """Handles a put request with a query."""
        self.handle_postput(as_post = False)

    def post(self):
        """Handles a post request with a query."""
        self.handle_postput()
        
    def handle_postput(self, as_post = True):
        sent = False
        try:
            forwarding_url = ForwardMappings.get_forward_to_url(self.request.path)
            if forwarding_url == None:
                #no mapping found so quite
                self.response.write('could not find forwarding mapping for : {}'.format(str(self.request.path)))
                self.response.set_status(404)
                return

            url = '{}{}'.format(forwarding_url, self.request.path)
            ReverseProxyHandler.log_method('====REVERSE PROXY REQUEST=======\n', '====END PROXY REQUEST=======\n', self.request.method, url, self.request.headers, self.request.body)               
            #pass onto to destination url
            if as_post == True:
                resp_code, resp_content, resp_headers = http_access.fetch_post(url, self.request.headers, self.request.body, None)
            else:
                resp_code, resp_content, resp_headers = http_access.fetch_put(url, self.request.headers, self.request.body, None)
            self.response.set_status(resp_code)
            for key, value in resp_headers.items():
                self.response.headers[key] = value
            sent = True
            ReverseProxyHandler.log_method('====REVERSE PROXY RESPONSE=======\n', '====END PROXY RESPONSE=======\n', self.request.method, url, self.response.headers, resp_content)               
            self.response.write(resp_content)
            return
            
        except IOError as e:
            if not sent:
                self.response.write('error trying to proxy: {}'.format(str(e)))
                self.response.set_status(404)



logging.getLogger().setLevel(logging.DEBUG)

ForwardMappings.init()

application = webapp2.WSGIApplication([
    ('/.*', ReverseProxyHandler)

],
    debug=True)
