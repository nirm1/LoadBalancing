from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import hashlib
import datetime
import sys


def hash_cash(salt, target, max_duration=datetime.timedelta(0,3,0), algo=hashlib.sha256):
    """
    :param salt: bytes
    :param target: number of leading zeros
    :param algo: hash algorithm to use, default sha256
    :return: the hashdigest
    """
    start_time = datetime.datetime.now()
    c = 0
    while True:
        td = datetime.datetime.now() - start_time
        data = salt + str(c).encode('utf-8')
        hd = algo(data).hexdigest()
        if hd[:target] == '0' * target or td > max_duration:
            return hd, c, (hd[:target] == '0' * target)
        c += 1


class LoadHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super(LoadHandler, self).__init__(request, client_address, server)

    def do_GET(self):
        print("cpu_load.py got a request")
        
        start_time = datetime.datetime.now()
        salt = str(start_time).encode('utf-8')
        target = 5
        hexdigest, clear_text, success = hash_cash(salt, target)
        end_time = datetime.datetime.now()

        message_parts = [
                '<!doctype html public>',
                '<html><head><title>Welcome to {0}!</title></head><body>'.format(sys.argv[1]),
                '<h1>Server: {0}</h1>'.format(sys.argv[1]),
                'clear text: {0}<br />'.format(clear_text),
                'salt: {0}<br />'.format(salt.decode('utf-8')),
                'target: {0}<br />'.format(target),
                'hashdigest: {0}<br />'.format(hexdigest),
                'time needed: {s}s{m}<br />'.format(s=(end_time - start_time).seconds, m=(end_time - start_time).microseconds),
                'successful? {0}'.format('Yes' if success else 'No'),
                '</body></html>'
                ]
        #for name, value in sorted(self.headers.items()):
        #    message_parts.append('%s=%s' % (name, value.rstrip()))
        message_parts.append('')
        message = '\r\n'.join(message_parts)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
        return

if __name__ == '__main__':
    port = int(sys.argv[1])
    httpd = HTTPServer(('0.0.0.0', port), LoadHandler)
    httpd.serve_forever()
