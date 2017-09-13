import logging
from google.appengine.api import urlfetch
import urllib


def fetch_put(url, headers_dict=None, payload='', query_params_dict=None):
    return fetch_it(url, headers_dict=headers_dict, payload=payload, query_params_dict=query_params_dict, sendAsPut=True)


def fetch_post(url, headers_dict=None, payload='', query_params_dict=None):
    return fetch_it(url, headers_dict=headers_dict, payload=payload, query_params_dict=query_params_dict, sendAsPut=False)


def fetch_it(url, headers_dict=None, payload='', query_params_dict=None, sendAsPut=False):
    try:
        headers = {}
        for key, value in headers_dict.items():
            headers[key] = value

        method = urlfetch.POST
        if sendAsPut:
            method = urlfetch.PUT

        if query_params_dict:
            encoded_params = urllib.urlencode(query_params_dict)
            url = url + '?' + encoded_params

        logging.info('fetch_it = %s' % url)
        result = urlfetch.fetch(url=url, payload=payload,
                                method=method, headers=headers_dict)

    except urlfetch.Error:
        logging.exception('Caught exception fetching url')

    return result.status_code,  result.content, result.headers


def fetch_get(url, headers_dict=None, query_params_dict=None):
    try:
        headers = {}
        for key, value in headers_dict.items():
            headers[key] = value

        if query_params_dict:
            encoded_params = urllib.urlencode(query_params_dict)
            url = url + '?' + encoded_params

        logging.info('fetch_get = %s' % url)
        result = urlfetch.fetch(url=url, headers=headers, method=urlfetch.GET)
    except urlfetch.Error:
        logging.exception('Caught exception fetching url')

    return result.status_code,  result.content, result.headers
