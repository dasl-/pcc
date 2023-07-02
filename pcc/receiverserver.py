from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler, HTTPStatus
from io import BytesIO
import json
import traceback
import urllib
from pcc.logger import Logger
from pifi.volumecontroller import VolumeController

class ReceiverAPI():

    def __init__(self):
        self.__vol_controller = VolumeController()
        self.__logger = Logger().set_namespace(self.__class__.__name__)

    def get_receiver_data(self):
        response_details = {}
        response_details['vol_pct'] = self.__vol_controller.get_vol_pct()
        response_details['success'] = True
        return response_details

    def set_vol_pct(self, post_data):
        vol_pct = int(post_data['vol_pct'])
        self.__vol_controller.set_vol_pct(vol_pct)
        return {
            'vol_pct': vol_pct,
            'success': True
        }

class PccReceiverServerRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        self.__api = ReceiverAPI()
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
            parsed_path = urllib.parse.urlparse(self.path)
            get_data = urllib.parse.unquote(parsed_path.query)
            if get_data:
                get_data = json.loads(get_data)

            if parsed_path.path == '/receiver_data':
                response = self.__api.get_receiver_data()
            else:
                self.__do_404()
                return

            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            resp = BytesIO()
            resp.write(bytes(json.dumps(response), 'utf-8'))
            self.wfile.write(resp.getvalue())
        except Exception:
            self.log_error('Exception: {}'.format(traceback.format_exc()))

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])

            post_data = None
            if content_length > 0:
                body = self.rfile.read(content_length)
                post_data = json.loads(body.decode("utf-8"))

            if self.path == '/vol_pct':
                response = self.__api.set_vol_pct(post_data)
            else:
                self.__do_404()
                return

            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            resp = BytesIO()
            resp.write(bytes(json.dumps(response), 'utf-8'))
            self.wfile.write(resp.getvalue())
        except Exception:
            self.log_error('Exception: {}'.format(traceback.format_exc()))

    def __do_404(self):
        self.send_response(404)
        self.end_headers()

    def log_request(self, code='-', size='-'):
        if isinstance(code, HTTPStatus):
            code = code.value
        self.log_message('[REQUEST] "%s" %s %s', self.requestline, str(code), str(size))

    def log_error(self, format, *args):
        self.__logger.error("%s - - %s" % (self.client_address[0], format % args))

    def log_message(self, format, *args):
        self.__logger.info("%s - - %s" % (self.client_address[0], format % args))

class PccReceiverThreadingHTTPServer(ThreadingHTTPServer):

    # Override: https://github.com/python/cpython/blob/18cb2ef46c9998480f7182048435bc58265c88f2/Lib/socketserver.py#L421-L443
    # See: https://docs.python.org/3/library/socketserver.html#socketserver.BaseServer.request_queue_size
    # This prevents messages we might see in `dmesg` like:
    #   [Sat Jan 29 00:44:36 2022] TCP: request_sock_TCP: Possible SYN flooding on port 80. Sending cookies.  Check SNMP counters.
    request_queue_size = 128

class ReceiverServer:

    def __init__(self):
        self.__server = PccReceiverThreadingHTTPServer(('0.0.0.0', 8080), PccReceiverServerRequestHandler)

    def serve_forever(self):
        self.__server.serve_forever()
