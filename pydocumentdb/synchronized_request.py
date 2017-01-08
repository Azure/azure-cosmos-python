#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""Synchronized request in the Azure DocumentDB database service.
"""

import json

from six.moves.urllib.parse import urlparse, urlencode    
import six

import pydocumentdb.documents as documents
import pydocumentdb.errors as errors
import pydocumentdb.http_constants as http_constants
import pydocumentdb.retry_utility as retry_utility

def _IsReadableStream(obj):
    """Checks whether obj is a file-like readable stream.

    :Returns:
        boolean

    """
    if (hasattr(obj, 'read') and callable(getattr(obj, 'read'))):
        return True
    return False


def _RequestBodyFromData(data):
    """Gets request body from data.

    When `data` is dict and list into unicode string; otherwise return `data`
    without making any change.

    :Parameters:
        - `data`: str, unicode, file-like stream object, dict, list or None

    :Returns:
        str, unicode, file-like stream object, or None

    """
    if isinstance(data, six.string_types) or _IsReadableStream(data):
        return data
    elif isinstance(data, (dict, list, tuple)):
        
        json_dumped = json.dumps(data, separators=(',',':'))

        if six.PY2:
            return json_dumped.decode('utf-8')
        else:
            return json_dumped
    return None


def _Request(connection_policy, requests_session, resource_url, request_options, request_body):
    """Makes one http request using the requests module.

    :Parameters:
        - `connection_policy`: documents.ConnectionPolicy
        - `requests_session`: requests.Session, Session object in requests module
        - `resource_url`: str, the url for the resource
        - `request_options`: dict
        - `request_body`: str, unicode or None

    :Returns:
        tuple of (result, headers), where both result and headers
        are dicts.

    """
    is_media = request_options['path'].find('media') > -1
    is_media_stream = is_media and connection_policy.MediaReadMode == documents.MediaReadMode.Streamed

    connection_timeout = (connection_policy.MediaRequestTimeout
                          if is_media
                          else connection_policy.RequestTimeout)

    parse_result = urlparse(resource_url)

    # We are disabling the SSL verification for local emulator(localhost) because in order to enable it we need to provide a path
    # for the emulator certificate and assign it to REQUESTS_CA_BUNDLE environment variable, so for security reasons we wanted to avoid
    # checking in that certificate on the file system. 
    is_ssl_enabled = (parse_result.hostname != 'localhost')

    # The requests library expects header values to be strings only, and will raise an error on validation if they are not. Because
    # these values can come from a few different places, go ahead and cast them before passing them along.
    request_options['headers'] = { header: str(value) for header, value in request_options['headers'].items() }

    if connection_policy.SSLConfiguration:
        ca_certs = connection_policy.SSLConfiguration.SSLCaCerts
        cert_files = (connection_policy.SSLConfiguration.SSLCertFile, connection_policy.SSLConfiguration.SSLKeyFile)

        response = requests_session.request(request_options['method'], 
                                resource_url, 
                                data = request_body, 
                                headers = request_options['headers'],
                                timeout = connection_timeout / 1000.0,
                                stream = is_media_stream,
                                verify = ca_certs,
                                cert = cert_files)
    else:
        response = requests_session.request(request_options['method'], 
                                    resource_url, 
                                    data = request_body, 
                                    headers = request_options['headers'],
                                    timeout = connection_timeout / 1000.0,
                                    stream = is_media_stream,
                                    verify = is_ssl_enabled)

    headers = dict(response.headers)

    # In case of media stream response, return the response to the user and the user
    # will need to handle reading the response.
    if is_media_stream:
        return (response.raw, headers)

    data = response.content
    if not six.PY2:
        # python 3 compatible: convert data from byte to unicode string
        data = data.decode('utf-8')

    if response.status_code >= 400:
        raise errors.HTTPFailure(response.status_code, data, headers)

    result = None
    if is_media:
        result = data
    else:
        if len(data) > 0:
            try:
                result = json.loads(data)
            except:
                raise errors.JSONParseFailure(data)

    return (result, headers)

def SynchronizedRequest(client,
                        global_endpoint_manager,
                        connection_policy,
                        requests_session,
                        method,
                        base_url,
                        path,
                        request_data,
                        query_params,
                        headers):
    """Performs one synchronized http request according to the parameters.

    :Parameters:
        - `client`: object, document client instance
        - `global_endpoint_manager`: _GlobalEndpointManager
        - `connection_policy`: documents.ConnectionPolicy
        - `requests_session`: requests.Session, Session object in requests module
        - `method`: str
        - `base_url`: str
        - `path`: str
        - `request_data`: str, unicode, file-like stream object, dict, list
          or None
        - `query_params`: dict
        - `headers`: dict

    :Returns:
        tuple of (result, headers), where both result and headers
        are dicts.

    """
    request_body = None
    if request_data:
        request_body = _RequestBodyFromData(request_data)
        if not request_body:
           raise errors.UnexpectedDataType(
               'parameter data must be a JSON object, string or' +
               ' readable stream.')

    request_options = {}
    request_options['path'] = path
    request_options['method'] = method
    if query_params:
        request_options['path'] += '?' + urlencode(query_params)

    request_options['headers'] = headers
    if request_body and (type(request_body) is str or
                         type(request_body) is six.text_type):
        request_options['headers'][http_constants.HttpHeaders.ContentLength] = (
            len(request_body))
    elif request_body is None:
        request_options['headers'][http_constants.HttpHeaders.ContentLength] = 0
    
    if request_options['path'] is not None:
        resource_url = base_url + request_options['path']
    # Pass _Request function with it's parameters to retry_utility's Execute method that wraps the call with retries
    return retry_utility._Execute(client, global_endpoint_manager, _Request, connection_policy, requests_session, resource_url, request_options, request_body)

