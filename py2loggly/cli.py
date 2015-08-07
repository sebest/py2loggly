import argparse

from . import __version__
from .server import Server


def main():
    parser = argparse.ArgumentParser(description='Proxy for python UDP/TCP logging to loggly', version=__version__)
    parser.add_argument('--bind-ip', metavar='IP', help='IP address to listen on', default='127.0.0.1')
    parser.add_argument('--tcp-port', metavar='PORT', help='TCP port to listen on', default=9020, type=int)
    parser.add_argument('--udp-port', metavar='PORT', help='UDP port to listen on', default=9021, type=int)
    parser.add_argument('--fqdn', action='store_true', help='Use the fully qualified domain name')
    parser.add_argument('--hostname', metavar='HOSTNAME', help='Use the provided hostname instead of guessing it.')
    parser.add_argument('--loggly-token', metavar='TOKEN', help='the loggly TOKEN.', required=True)
    parser.add_argument('--tags', metavar='TAG1 TAG2', help='Tags for the event message', nargs='+')
    args = parser.parse_args()
    Server(loggly_token=args.loggly_token, bind_ip=args.bind_ip, tcp_port=args.tcp_port, udp_port=args.udp_port,
           fqdn=args.fqdn, hostname=args.hostname, tags=args.tags).start()
