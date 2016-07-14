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

import logging


class _EndpointDiscoveryRetryPolicy(object):
    """The endpoint discovery retry policy class used for geo-replicated database accounts
       to handle the write forbidden exceptions due to writable/readable location changes
       (say, after a failover).
    """

    Max_retry_attempt_count = 120
    Retry_after_in_milliseconds = 1000
    FORBIDDEN_STATUS_CODE = 403
    WRITE_FORBIDDEN_SUB_STATUS_CODE = 3

    def __init__(self, global_endpoint_manager):
        self.global_endpoint_manager = global_endpoint_manager
        self._max_retry_attempt_count = _EndpointDiscoveryRetryPolicy.Max_retry_attempt_count
        self.current_retry_attempt_count = 0
        self.retry_after_in_milliseconds = _EndpointDiscoveryRetryPolicy.Retry_after_in_milliseconds
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    def ShouldRetry(self, exception):
        """Returns true if should retry based on the passed-in exception.

        :Parameters:
            - `exception`: errors.HTTPFailure instance

        :Returns:
            boolean

        """
        if self.current_retry_attempt_count < self._max_retry_attempt_count and self.global_endpoint_manager.EnableEndpointDiscovery:
            self.current_retry_attempt_count += 1
            logging.info('Write location was changed, refreshing the locations list from database account and will retry the request.')

            # Refresh the endpoint list to refresh the new writable and readable locations
            self.global_endpoint_manager.RefreshEndpointList()
            return True
        else:
            return False
