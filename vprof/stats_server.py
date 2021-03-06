"""Program stats server."""
import functools
import json
import os
import SimpleHTTPServer
import SocketServer
import subprocess
import sys

_STATIC_DIR = 'frontend'
_PROFILE_HTML = '%s/profile.html' % _STATIC_DIR


class _StatsServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """Declares Multithreaded HTTP server."""
    allow_reuse_address = True


class StatsHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """Program stats request handler."""
    ROOT_URI = '/'
    PROFILE_URI = '/profile'

    def __init__(self, profile_json, *args, **kwargs):
        self._profile_json = profile_json
        # Since this class is old-style - call parent method directly.
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(
            self, *args, **kwargs)

    def do_GET(self):   #pylint: disable=C0103
        """Handles HTTP GET requests."""
        if self.path == self.ROOT_URI:
            res_filename = os.path.dirname(__file__) + '/' + _PROFILE_HTML
            with open(res_filename) as res_file:
                output = res_file.read()
            content_type = 'text/html'
        elif self.path == self.PROFILE_URI:
            output = json.dumps(self._profile_json)
            content_type = 'text/json'
        else:
            res_filename = (
                os.path.dirname(__file__) + '/' + _STATIC_DIR + self.path)
            with open(res_filename) as res_file:
                output = res_file.read()
            _, extension = os.path.splitext(self.path)
            content_type = 'text/%s' % extension

        self._send_response(
            200, headers=(('Content-type', '%s; charset=utf-8' % content_type),
                          ('Content-Length', len(output))))
        self.wfile.write(output)

    def _send_response(self, http_code, message=None, headers=None):
        """Sends HTTP response code, message and headers."""
        self.send_response(http_code, message)
        if headers:
            for header in headers:
                self.send_header(*header)
            self.end_headers()


def start(host, port, profile_stats):
    """Starts HTTP server with specified parameters.

    Args:
        host: Server hostname.
        port: Server port.
        profile_stats: Dict with collected progran stats.
    """
    stats_handler = functools.partial(
        StatsHandler, profile_stats)
    subprocess.call(['open', 'http://%s:%s' % (host, port)])
    try:
        _StatsServer((host, port), stats_handler).serve_forever()
    except KeyboardInterrupt:
        print('Stopping...')
        sys.exit(0)
