from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler, HTTPStatus
import traceback
from urllib.parse import urlparse
from pcc.logger import Logger
from pcc.directoryutils import DirectoryUtils

class PccControllerServerRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        self.__root_dir = DirectoryUtils().root_dir + "/app/build"
        self.__logger = Logger().set_namespace(self.__class__.__name__)
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        try:
            return self.__serve_static_asset()
        except Exception:
            self.log_error('Exception: {}'.format(traceback.format_exc()))

    def __do_404(self):
        self.send_response(404)
        self.end_headers()

    def __serve_static_asset(self):
        self.path = urlparse(self.path).path # get rid of query parameters e.g. `?foo=bar&baz=1`
        if self.path == '/':
            self.path = '/index.html'

        try:
            file_to_open = open(self.path, 'rb').read()
            self.send_response(200)
        except Exception as e:
            self.__logger.error(str(e))
            self.log_error('Exception: {}'.format(traceback.format_exc()))
            file_to_open = "File not found"
            self.__do_404()
            return

        if self.path.endswith('.js'):
            self.send_header("Content-Type", "text/javascript")
        elif self.path.endswith('.css'):
            self.send_header("Content-Type", "text/css")
        elif self.path.endswith('.svg') or self.path.endswith('.svgz'):
            self.send_header("Content-Type", "image/svg+xml")
        self.end_headers()

        if type(file_to_open) is bytes:
            self.wfile.write(file_to_open)
        else:
            self.wfile.write(bytes(file_to_open, 'utf-8'))
        return

    def log_request(self, code='-', size='-'):
        if isinstance(code, HTTPStatus):
            code = code.value
        self.log_message('[REQUEST] "%s" %s %s', self.requestline, str(code), str(size))

    def log_error(self, format, *args):
        self.__logger.error("%s - - %s" % (self.client_address[0], format % args))

    def log_message(self, format, *args):
        self.__logger.info("%s - - %s" % (self.client_address[0], format % args))

class PccControllerThreadingHTTPServer(ThreadingHTTPServer):

    # Override: https://github.com/python/cpython/blob/18cb2ef46c9998480f7182048435bc58265c88f2/Lib/socketserver.py#L421-L443
    # See: https://docs.python.org/3/library/socketserver.html#socketserver.BaseServer.request_queue_size
    # This prevents messages we might see in `dmesg` like:
    #   [Sat Jan 29 00:44:36 2022] TCP: request_sock_TCP: Possible SYN flooding on port 80. Sending cookies.  Check SNMP counters.
    request_queue_size = 128

class ControllerServer:

    def __init__(self):
        self.__server = PccControllerThreadingHTTPServer(('0.0.0.0', 80), PccControllerServerRequestHandler)

    def serve_forever(self):
        self.__server.serve_forever()
