#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# Copyright 2015 Nhu Bui
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [URL] [GET/POST]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_path_port(self,url):
	#Default to port 80, port 80 is the port 
	#that the server "listens to" or expects to receive from a Web client
	port = 80
	host =url.replace('http://', "")
	path = "/"

	#parsing the path from host if any
	index = host.find('/')
	if index != -1:
		path = host[index:]
		host = host[:index]
	
	#parsing the port from host if any
	index = host.find(':')
	if index != -1:
		port = int(host[index+1:])
		host = host[:index]
        return host, path, port

    def connect(self, host, port):
	#create a new socket
	try:
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except soccket.error as msg:
		print('Failed to create socket!')
		print('Error code: ' + str(msg[0]) + ', error message: ' + msg[1])
		sys.exit()

	#get rid of leading / in url. 
	#ie. want google.ca not google.ca/
	if host.endswith('/'):
		host = host[:-1]

	#connect to website
	self.s.connect((host, port))
        return self.s

    def get_code(self, data):
	code= data.split()[1]
        return int(code)

    def get_headers(self,data):
        return data.split('\r\n\r\n')[0]

    def get_body(self, data):
	#if there is a body, then it would be after \r\n\r\n
	#else body would be ''
	index = data.find('\r\n\r\n')
	body = data[index:]
        return body

    def get_code_data(self,host, port, clientMsg):
	#connect client socket to server socket
	self.clientSocket = self.connect(host,port)
	
	#send server the HTTP call
	try:
		self.clientSocket.sendall(clientMsg)
	except self.clientSocket as msg:
		print('Error code: ' + str(msg[0]) + ', error message: ' + msg[1])
		sys.exit()

	#receive data from server
	data = self.recvall(self.clientSocket)

	code =self.get_code(data)
	body= self.get_body(data)
	return code, body

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(24)
            if (part):
                buffer.extend(part)
            else:
                done = not part          
        return str(buffer)

    def GET(self, url, args=None):
	host, path, port = self.get_host_path_port(url)

	#message to send to server
	message ="GET %s HTTP/1.1 \r\n" %path
	message +="Host: %s\r\n" %host
	message +="Accept: */*\r\nConnection:close\r\n\r\n"

	#send client's message out to server and receive server's response
	code, body = self.get_code_data(host, port, message)

        return HTTPRequest(code, body)

    def POST(self, url, args=''):
	host, path, port = self.get_host_path_port(url)
	if args!='':
		args=urllib.urlencode(args)

	#message to send to server
	message ="POST %s HTTP/1.1 \r\n" %path
	message +="Host: %s\r\n" %host
	message +="Content-Length: %d\r\n" % len(args)
        message +="Content-Type: application/x-www-form-urlencoded\r\n"
	message +="Accept: */*\r\nConnection:close\r\n\r\n"
	message +=args

	#send client's message out to server and receive server's response
	code, body = self.get_code_data(host,port, message)

        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:         
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[1], sys.argv[2] )
    else:
        print client.command( command, sys.argv[1] )    
