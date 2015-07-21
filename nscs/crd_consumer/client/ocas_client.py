# Copyright 2013 Freescale Semiconductor, Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import httplib
import logging
import time
import urllib
import urlparse
import httplib2
from common import serializer
from common import constants
from common import utils

from common import rm_exceptions as exceptions

_logger = logging.getLogger(__name__)

def exception_handler_v20(status_code, error_content):
    """ Exception handler for UCM API client

        :param status_code: HTTP error status code
        :param error_content: deserialized body of error response
    """

    msg = "%s-%s" % (status_code, error_content)
    raise exceptions.UCMClientException(status_code=status_code,
                                            message=msg)

class Client(object):
    """Client for the UCM WSGI API.

    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    :param insecure: ssl certificate validation. (optional)

    """
    
    url = 'http://localhost:20202/v1'
    
    # API has no way to report plurals, so we have to hard code them
    EXTED_PLURALS = {}

    def get_attr_metadata(self):
        if self.format == 'json':
            return {}
        old_request_format = self.format
        #self.format = 'json'
        #exts = self.list_extensions()['extensions']
        self.format = ''
        exts = []
        self.format = old_request_format
        ns = dict([(ext['alias'], ext['namespace']) for ext in exts])
        self.EXTED_PLURALS.update(constants.PLURALS)
        return {'plurals': self.EXTED_PLURALS,
                'xmlns': constants.XML_NS_V20,
                constants.EXT_NS: ns}
            
    def __init__(self, **kwargs):
        """ Initialize a new client for the Quantum v2.0 API. """
        super(Client, self).__init__()
        self.httpclient = HTTPClient(**kwargs)
        self.version = '2.0'
        self.format = 'json'
        #self.action_prefix = "/v%s" % (self.version)
        #self.format = ''
        self.action_prefix = ""
        self.retries = 0
        self.retry_interval = 1

    def _handle_fault_response(self, status_code, response_body):
        # Create exception with HTTP status code and message
        _logger.debug("Error message: %s", response_body)
        # Add deserialized error message to exception arguments
        try:
            des_error_body = self.deserialize(response_body, status_code)
        except:
            # If unable to deserialized body it is probably not a
            # Quantum error
            des_error_body = {'message': response_body}
        # Raise the appropriate exception
        exception_handler_v20(status_code, des_error_body)

    def do_request(self, method, action, body=None, headers=None, params=None):
        # Add format and tenant_id
        #action += ".%s" % self.format
        action = self.action_prefix + action
        if type(params) is dict and params:
            action += '?' + urllib.urlencode(params, doseq=1)
        if body:
            body = self.serialize(body)
        self.httpclient.content_type = self.content_type()
        resp, replybody = self.httpclient.do_request(action, method, body=body)
        status_code = self.get_status_code(resp)
        if status_code in (httplib.OK,
                           httplib.CREATED,
                           httplib.ACCEPTED,
                           httplib.NO_CONTENT):
            return self.deserialize(replybody, status_code)
        else:
            self._handle_fault_response(status_code, replybody)

    def get_status_code(self, response):
        """
        Returns the integer status code from the response, which
        can be either a Webob.Response (used in testing) or httplib.Response
        """
        if hasattr(response, 'status_int'):
            return response.status_int
        else:
            return response.status

    def serialize(self, data):
        """
        Serializes a dictionary with a single key (which can contain any
        structure) into either xml or json
        """
        if data is None:
            return None
        elif type(data) is dict:
            return serializer.Serializer(
                self.get_attr_metadata()).serialize(data, self.content_type())
        else:
            raise Exception("unable to serialize object of type = '%s'" %
                            type(data))

    def deserialize(self, data, status_code):
        """
        Deserializes an xml or json string into a dictionary
        """
        if status_code == 204:
            return data
        return serializer.Serializer(self.get_attr_metadata()).deserialize(
            data, self.content_type())['body']

    def content_type(self, _format=None):
        """
        Returns the mime-type for either 'xml' or 'json'.  Defaults to the
        currently set format
        """
        _format = _format or self.format
        return "application/%s" % (_format)

    def retry_request(self, method, action, body=None,
                      headers=None, params=None):
        """
        Call do_request with the default retry configuration. Only
        idempotent requests should retry failed connection attempts.

        :raises: ConnectionFailed if the maximum # of retries is exceeded
        """
        max_attempts = self.retries + 1
        for i in xrange(max_attempts):
            try:
                return self.do_request(method, action, body=body,
                                       headers=headers, params=params)
            except exceptions.ConnectionFailed:
                # Exception has already been logged by do_request()
                if i < self.retries:
                    _logger.debug(_('Retrying connection to UCM service'))
                    time.sleep(self.retry_interval)

        raise exceptions.ConnectionFailed(reason=_("Maximum attempts reached"))

    def delete(self, action, body=None, headers=None, params=None):
        return self.retry_request("DELETE", action, body=body,
                                  headers=headers, params=params)

    def get(self, action, body=None, headers=None, params=None):
        return self.retry_request("GET", action, body=body,
                                  headers=headers, params=params)

    def post(self, action, body=None, headers=None, params=None):
        # Do not retry POST requests to avoid the orphan objects problem.
        return self.do_request("POST", action, body=body,
                               headers=headers, params=params)

    def put(self, action, body=None, headers=None, params=None):
        return self.retry_request("PUT", action, body=body,
                                  headers=headers, params=params)

    def list(self, collection, path, retrieve_all=True, **params):
        if retrieve_all:
            res = []
            for r in self._pagination(collection, path, **params):
                res.extend(r[collection])
            return {collection: res}
        else:
            return self._pagination(collection, path, **params)

    def _pagination(self, collection, path, **params):
        if params.get('page_reverse', False):
            linkrel = 'previous'
        else:
            linkrel = 'next'
        next = True
        while next:
            res = self.get(path, params=params)
            yield res
            next = False
            try:
                for link in res['%s_links' % collection]:
                    if link['rel'] == linkrel:
                        query_str = urlparse.urlparse(link['href']).query
                        params = urlparse.parse_qs(query_str)
                        next = True
                        break
            except KeyError:
                break
            

class HTTPClient(httplib2.Http):
    """Handles the REST calls and responses, include authn"""

    USER_AGENT = 'python-ucmclient'
    def __init__(self, timeout=None,
                 insecure=False, **kwargs):
        super(HTTPClient, self).__init__(timeout=timeout)
        self.content_type = 'application/json'
        # httplib2 overrides
        self.force_exception_to_status_code = True
        self.disable_ssl_certificate_validation = insecure

    def _cs_request(self, *args, **kwargs):
        kargs = {}
        kargs.setdefault('headers', kwargs.get('headers', {}))
        kargs['headers']['User-Agent'] = self.USER_AGENT

        if 'content_type' in kwargs:
            kargs['headers']['Content-Type'] = kwargs['content_type']
            kargs['headers']['Accept'] = kwargs['content_type']
        else:
            kargs['headers']['Content-Type'] = self.content_type
            kargs['headers']['Accept'] = self.content_type

        if 'body' in kwargs:
            kargs['body'] = kwargs['body']
        utils.http_log_req(_logger, args, kargs)
        resp, body = self.request(*args, **kargs)
        utils.http_log_resp(_logger, resp, body)
        status_code = self.get_status_code(resp)
        if status_code == 401:
            raise exceptions.Unauthorized(message=body)
        elif status_code == 403:
            raise exceptions.Forbidden(message=body)
        return resp, body

    def do_request(self, url, method, **kwargs):
        # Perform the request once. If we get a 401 back then it
        # might be because the auth token expired, so try to
        # re-authenticate and try again. If it still fails, bail.
        try:
            kwargs.setdefault('headers', {})
            print "Method - %s" % str(method)
            print "URL - %s" % str(url)
            print "ARGS - %s" % str(kwargs)
            resp, body = self._cs_request(url, method,
                                          **kwargs)
            return resp, body
        except exceptions.Unauthorized as ex:
            raise ex

    def get_status_code(self, response):
        """
        Returns the integer status code from the response, which
        can be either a Webob.Response (used in testing) or httplib.Response
        """
        if hasattr(response, 'status_int'):
            return response.status_int
        else:
            return response.status
