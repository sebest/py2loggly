#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gevent import monkey; monkey.patch_all()

import cPickle
import struct
import logging
import logging.handlers
import _socket
import gevent
from gevent.server import DatagramServer, StreamServer
from gevent.socket import EWOULDBLOCK

from . import formatter

DEFAULT_UDP = logging.handlers.DEFAULT_UDP_LOGGING_PORT
DEFAULT_TCP = logging.handlers.DEFAULT_TCP_LOGGING_PORT

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DatagramServer(DatagramServer):

    def do_read(self):
        try:
            data, address = self._socket.recvfrom(65536)
        except _socket.error, err:
            if err[0] == EWOULDBLOCK:
                return
            raise
        return data, address

class Server(object):

    def __init__(self, bind_ip='127.0.0.1', tcp_port=DEFAULT_TCP, udp_port=DEFAULT_UDP, fqdn=True, hostname=None, tags=None):
        self.formatter = formatter.JSONFormatter(tags, hostname, fqdn)
        self.udp_server = DatagramServer('%s:%s' % (bind_ip, udp_port), self.udp_handle)
        self.tcp_server = StreamServer('%s:%s' % (bind_ip, tcp_port), self.tcp_handle)
        logging.info('Listening on %s (udp=%s tcp=%s) sending to %s.', bind_ip, udp_port, tcp_port, '')

    def send_obj(self, obj):
        record = logging.makeLogRecord(obj)
        payload = self.formatter.format(record)
        logger.debug('message %s', payload)

    def udp_handle(self, data, address):
        slen = struct.unpack('>L', data[:4])[0]
        chunk = data[4:slen+4]
        try:
            obj = cPickle.loads(chunk)
        except EOFError:
            logging.error('UDP: invalid data to pickle %s', chunk)
            return
        self.send_obj(obj)

    def tcp_handle(self, socket, address):
        fileobj = socket.makefile()
        while True:
            chunk = fileobj.read(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack(">L", chunk)[0]
            chunk = fileobj.read(slen)
            while len(chunk) < slen:
                chunk = chunk + fileobj.read(slen - len(chunk))
            fileobj.flush()
            try:
                obj = cPickle.loads(chunk)
            except EOFError:
                logging.error('TCP: invalid data to pickle %s', chunk)
                break
            self.send_obj(obj)

    def start(self):
        self.udp_server.start()
        self.tcp_server.start()
        gevent.wait()
