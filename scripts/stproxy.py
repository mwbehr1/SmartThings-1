#!/usr/bin/env python3
__doc__ = "SmartThings Generic HTTP Proxy"
__author__ = "Aaron Turner"

import argparse
import json
import logging
import socket
from http.server import (
    BaseHTTPRequestHandler,
    HTTPServer,
)
from urllib.parse import (
    urlparse,
    parse_qs,
)

logger = logging.getLogger('stproxy')

class SmartThingsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parser = urlparse(self.path)
        query_args = parse_qs(parser.query)
        (host, port) = parser.path.split(':')
        path = self.path
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        try:
            s.connect((host, int(port)))
        except socket.timeout:
            self.send_error(401, "unable to connect to %s" % (path))
            return

        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type','text/json')
        self.end_headers()

        # Send message back to client
        message = "Hello world!"
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return

    def do_POST(self):
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-p', '--port', type=int, default=8000,
                        help='Webserver port (%(default)s)')
    parser.add_argument('-l', '--log-level', type=str, default='INFO',
                        choices=['ERROR', 'WARNING', 'INFO', 'DEBUG'],
                        help='Log level (%(default)s)')

    args = parser.parse_args()

    httpd = HTTPServer(('0.0.0.0', args.port), SmartThingsHandler)
    httpd.serve_forever()
