# library
import logging
from google.appengine.ext import ndb
from datetime import datetime
from datetime import timedelta

DB_MAX_ROWS = 100
LOG_LENGTH = 20

# set up class for looking up url mapping entry from the Datatstore


class InboundRequest(ndb.Model):
    time_stamp = ndb.DateTimeProperty(indexed=True)
    request_body = ndb.StringProperty(indexed=False)
    request_query_params = ndb.StringProperty(indexed=False)
    request_host_url = ndb.StringProperty(indexed=False)
    request_headers = ndb.StringProperty(indexed=False)
    request_path = ndb.StringProperty(indexed=True)

    @staticmethod
    def add_record(time_stamp, host_url, path, headers, qparams, body):
        rc = InboundRequest(
            time_stamp=time_stamp,
            request_host_url=host_url,
            request_path=path,
            request_headers=headers,
            request_query_params=qparams,
            request_body=body)
        rc.put()

    @staticmethod
    def wipe():
        ndb.delete_multi(InboundRequest.query().fetch(keys_only=True))

    @staticmethod
    def get_latest():
        return InboundRequest.query().order(-InboundRequest.time_stamp).fetch(LOG_LENGTH)

    @staticmethod
    def wipe_if_big():

        # get is descending order
        rows = InboundRequest.query().order(-InboundRequest.time_stamp).fetch(keys_only=True)
        # delete all records after DB_MAX_ROWS
        if(len(rows) > DB_MAX_ROWS):
            row_to_delete = rows[DB_MAX_ROWS:]
            logging.info(
                'wiping %d oldest records as DB has exceeded limit of %d' %
                (len(row_to_delete), DB_MAX_ROWS))
            ndb.delete_multi(row_to_delete)
