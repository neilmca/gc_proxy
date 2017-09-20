# library
import logging
from google.appengine.ext import ndb
from datetime import datetime
from datetime import timedelta


# set up class for looking up url mapping entry from the Datatstore


class ForwardMappings(ndb.Model):
    inbound_path_predicate = ndb.StringProperty(indexed=False)
    forward_to_url = ndb.StringProperty(indexed=False)
    channel = ndb.StringProperty(indexed=True)
    
    
    @staticmethod
    def init():
        #logging.info('ForwardMappings.init')
        records = ForwardMappings.query().fetch(keys_only=True)
        #logging.info(records)
        if len(records) == 0:
            rc = ForwardMappings(inbound_path_predicate = "*", forward_to_url = "localhost:8888", channel = '0')
            rc.put()

    @staticmethod
    def get_forward_to_url(channel = '0', path = None):

        mappings = ForwardMappings.query(ForwardMappings.channel == channel).fetch()
        #logging.info(str(mappings))
        #logging.info('path = %s' % path)
        forward_to_url = None
        for map in mappings:
            if map.inbound_path_predicate == '*':
                #wildcard predicate so map - only if there is not already a mapping that is closer match
                if forward_to_url == None:
                    forward_to_url = map.forward_to_url
            else:
                #is path predicate in path request
                if map.inbound_path_predicate in path:
                    forward_to_url = map.forward_to_url

        if forward_to_url != None:        
            logging.info('found mapping for %s to channel=%s, url=%s' % (path, channel, forward_to_url))
        return forward_to_url

       