# -*- coding: utf-8 -*-

import socket

from threading import Thread, Lock
from time import sleep

from module.plugins.Hook import Hook, threaded


def forward(source, destination):
    try:
        size = 1024
        data = source.recv(size)
        while data:
            destination.sendall(data)
            data = source.recv(size)
    finally:
        destination.shutdown(socket.SHUT_WR)


#: socket.create_connection wrapper for python 2.5
def create_connection(address, timeout=object(), source_address=None):
    if hasattr(socket, 'create_connection'):
        if type(timeout) == object:
            timeout = socket._GLOBAL_DEFAULT_TIMEOUT

        return socket.create_connection(address, timeout, source_address)

    else:
        host, port = address
        err = None
        for res in getaddrinfo(host, port, 0, SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            sock = None
            try:
                sock = socket(af, socktype, proto)
                if type(timeout) != object:
                    sock.settimeout(timeout)
                if source_address:
                    sock.bind(source_address)
                sock.connect(sa)
                return sock

            except socket.error, _:
                err = _
                if sock is not None:
                    sock.close()

        if err is not None:
            raise err
        else:
            raise socket.error("getaddrinfo returns an empty list")


class ClickAndLoad(Hook):
    __name__    = "ClickAndLoad"
    __type__    = "hook"
    __version__ = "0.33"

    __config__ = [("activated", "bool", "Activated"                                     , True ),
                  ("port"     , "int" , "Port"                                          , 9666 ),
                  ("extern"   , "bool", "Listen for requests coming from WAN (internet)", False)]

    __description__ = """Click'N'Load hook plugin"""
    __license__     = "GPLv3"
    __authors__     = [("RaNaN", "RaNaN@pyload.de"),
                       ("Walter Purcaro", "vuolter@gmail.com")]


    def coreReady(self):
        if not self.config['webinterface']['activated']:
            return

        ip      = "0.0.0.0" if self.getConfig("extern") else "127.0.0.1"
        webport = int(self.config['webinterface']['port'])
        cnlport = self.getConfig('port')

        self.proxy(ip, webport, cnlport)


    @threaded
    def proxy(self, ip, webport, cnlport):
        self.manager.startThread(self.server, ip, webport, cnlport)
        lock = Lock()
        lock.acquire()
        lock.acquire()


    def server(self, ip, webport, cnlport):
        try:
            dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dock_socket.bind((ip, cnlport))
            dock_socket.listen(5)

            while True:
                client_socket = dock_socket.accept()[0]
                server_socket = create_connection(("127.0.0.1", webport))

                self.manager.startThread(forward, client_socket, server_socket)
                self.manager.startThread(forward, server_socket, client_socket)

        except socket.error, e:
            self.logDebug(e)
            self.server(ip, webport, cnlport)

        finally:
            client_socket.close()
            server_socket.close()
            dock_socket.close()
