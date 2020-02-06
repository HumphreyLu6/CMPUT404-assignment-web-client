#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
import urllib.parse

# https://stackoverflow.com/questions/21628852/changing-hostname-in-a-url
def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


UserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"


class HTTPClient(object):
    def parse_url(self, url):
        parse_result = urllib.parse.urlparse(url)
        if parse_result.hostname == None:
            raise Exception("No hostname found")

        port = 80
        if parse_result.port != None:
            port = int(parse_result.port)

        path = parse_result.path
        if path == "":
            path = "/"

        self.url_pr = parse_result._replace(
            netloc="{}:{}".format(parse_result.hostname, port), path=path
        )

        return None

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        lines = data.splitlines()
        code = int(lines[0].split(" ")[1])
        return code

    def get_headers(self, data):
        headers = data.split("\r\n\r\n")[0]
        return headers

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body

    def sendall(self, data):
        self.socket.sendall(data.encode("utf-8"))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if part:
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode("utf-8")

    def GET(self, url, args=None):
        self.parse_url(url)
        request = "GET {0} HTTP/1.1\r\nUser-Agent:{2}\r\nHost:{1}\r\nConnection:close\r\n\r\n".format(
            self.url_pr.path, self.url_pr.hostname, UserAgent
        )

        self.connect(self.url_pr.hostname, self.url_pr.port)

        self.sendall(request)
        data = self.recvall(self.socket)
        self.close()

        self.headers = self.get_headers(data)
        code = self.get_code(self.headers)
        body = self.get_body(data)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        self.parse_url(url)
        if args == None:
            args = ""
        encoded_string = urllib.parse.urlencode(args)
        request = (
            "POST {0} HTTP/1.1\r\n"
            "Host: {1}\r\n"
            "Content-Type: application/x-www-form-urlencoded\r\n"
            "Content-Length: {2}\r\n"
            "Connection: close\r\n\r\n{3}".format(
                self.url_pr.path,
                self.url_pr.hostname,
                len(encoded_string),
                encoded_string,
            )
        )

        self.connect(self.url_pr.hostname, self.url_pr.port)
        self.sendall(request)
        data = self.recvall(self.socket)
        self.close()

        self.headers = self.get_headers(data)
        code = self.get_code(self.headers)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if command == "POST":
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if len(sys.argv) <= 1:
        help()
        sys.exit(1)
    elif len(sys.argv) == 3:
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
