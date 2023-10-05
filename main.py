import http.server
import socketserver

PORT = 1000
DIRECTORY = '/soal'

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving on port {PORT}...")
    httpd.serve_forever()
