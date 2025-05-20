import os
from http.server import CGIHTTPRequestHandler, HTTPServer

ip = os.getenv("SERVER_IP", "10.9.76.8")
port = int(os.getenv("SERVER_PORT", 8888))

# Run http server to enable download RAC zip file into the vm nodes
# will run from hypervisor
dir = f"{os.getcwd()}/"
os.chdir(dir)

# Create server object
server_object = HTTPServer(server_address=(ip, port), RequestHandlerClass=CGIHTTPRequestHandler)
# Start the web server
server_object.serve_forever()
