#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gevent import monkey
monkey.patch_all()

import sys
import struct
import logging
import logging.handlers
import _socket
import gevent
from gevent.server import DatagramServer, StreamServer
from gevent.socket import EWOULDBLOCK
from gevent.queue import Queue
try:
    from urllib.request import urlopen
    from urllib.parse import quote
    import pickle
except ImportError:
    from urllib2 import urlopen, quote
    import cPickle as pickle
try:
    import simplejson as json
except ImportError:
    import json

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

    def __init__(self, loggly_token, bind_ip='127.0.0.1', tcp_port=DEFAULT_TCP, udp_port=DEFAULT_UDP, fqdn=True, hostname=None, tags=None):
        self.loggly_token = loggly_token
        self.formatter = formatter.JSONFormatter(tags, hostname, fqdn)
        self.udp_server = DatagramServer('%s:%s' % (bind_ip, udp_port), self.udp_handle)
        self.tcp_server = StreamServer('%s:%s' % (bind_ip, tcp_port), self.tcp_handle)

        self.queue = Queue()

        [gevent.spawn(self.sender) for i in range(100)]

        logging.info('Listening on %s (udp=%s tcp=%s).', bind_ip, udp_port, tcp_port)

    def sender(self):
        while True:
            obj = self.queue.get()
            qsize = self.queue.qsize()
            if qsize > 100 and qsize % 100 == 0:
                logger.error("Queue has over %d messages", qsize)
            record = logging.makeLogRecord(obj)
            data = self.formatter.format(record, serialize=False)
            tags = data.pop('tags', [])

            if sys.version_info < (3, 0):
                payload = json.dumps(data)
            else:
                payload = bytes(json.dumps(data), 'utf-8')

            log_data = "PLAINTEXT=" + quote(payload)
            url = "http://logs-01.loggly.com/inputs/%s/tag/%s/" % (self.loggly_token, ','.join(tags))

            while True:
                try:
                    urlopen(url, log_data)
                    break
                except Exception as exc:
                    logging.error('Can\'t send message to %s: %s', url, exc)
                    gevent.sleep(5)
                    continue

    def udp_handle(self, data, address):
        slen = struct.unpack('>L', data[:4])[0]
        chunk = data[4:slen+4]
        try:
            obj = pickle.loads(chunk)
        except EOFError:
            logging.error('UDP: invalid data to pickle %s', chunk)
            return
        self.queue.put_nowait(obj)

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
                obj = pickle.loads(chunk)
            except EOFError:
                logging.error('TCP: invalid data to pickle %s', chunk)
                break
            self.queue.put_nowait(obj)

    def start(self):
        self.udp_server.start()
        self.tcp_server.start()
        gevent.wait()
