#!/usr/bin/env python3
"""Simple HTTPS server for development."""
import http.server
import ssl
import socketserver
from pathlib import Path


class HTTPSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTPS request handler that performs SSL negotiation."""
    
    def setup(self):
        """Wrap socket with SSL before processing."""
        self.connection = self.request
        # Don't call super().setup() as it tries to read from unencrypted socket
        self.rfile = self.connection.makefile('rb', self.rbufsize)
        self.wfile = self.connection.makefile('wb', self.wbufsize)


class HTTPSServer(socketserver.TCPServer):
    """HTTPS server implementation."""
    
    def __init__(self, server_address, RequestHandlerClass, certfile, keyfile):
        self.certfile = certfile
        self.keyfile = keyfile
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)
        super().__init__(server_address, RequestHandlerClass, bind_and_activate=True)
    
    def get_request(self):
        """Accept connection and immediately wrap with SSL."""
        sock, addr = super().get_request()
        try:
            ssl_sock = self.ssl_context.wrap_socket(sock, server_side=True)
            return ssl_sock, addr
        except Exception as e:
            print(f"SSL wrapping error: {e}")
            sock.close()
            raise


if __name__ == "__main__":
    port = 5000
    server_dir = Path(__file__).parent
    cert_file = str(server_dir.parent / "cert.pem")
    key_file = str(server_dir.parent / "key.pem")
    
    class MyHTTPRequestHandler(HTTPSRequestHandler):
        def __init__(self, *args, **kwargs):
            self.directory = str(server_dir)
            super().__init__(*args, **kwargs)
    
    server = HTTPSServer(("127.0.0.1", port), MyHTTPRequestHandler, cert_file, key_file)
    
    print(f"✓ Starting HTTPS server on https://127.0.0.1:{port}/")
    print(f"✓ Serving from: {server_dir}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Server stopped")

