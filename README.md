Py2Loggly
=========

Py2Loggly is a proxy server listening on UDP and TCP for messages coming from python's UDP/TCP logging handler, it will forward all these messages to `loggly.com`.

Installation
------------

### Install dependencies

py2loggly only depends on `gevent`


### Install py2loggly

    $ python setup.py install

Usage
-----

### Starting the server

The only required parameter is `--loggly-token` to provide your loggly TOKEN.

    $ py2loggly --loggly-token $LOGGLY_TOKEN

The default TCP port is 9020 and the default UDP port is 9021.

##### Parameters

    usage: py2loggly [-h] [-v] [--bind-ip IP] [--tcp-port PORT] [--udp-port PORT]
                     [--fqdn] [--hostname HOSTNAME] --loggly-token TOKEN
                     [--tags TAG1 TAG2 [TAG1 TAG2 ...]]

    Proxy for python UDP/TCP logging to loggly

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      --bind-ip IP          IP address to listen on
      --tcp-port PORT       TCP port to listen on
      --udp-port PORT       UDP port to listen on
      --fqdn                Use the fully qualified domain name
      --hostname HOSTNAME   Use the provided hostname instead of guessing it.
      --loggly-token TOKEN  the loggly TOKEN.
      --tags TAG1 TAG2 [TAG1 TAG2 ...]
                            Tags for the event message

### Sending messages to py2loggly

You can either use `SockerHandler` or `DatagramHandler` from python's `logging.handlers`

The biggest advantage to use `DatagramHandler` is that logging won't slow down your application and if py2loggly is not running, it won't impact your application.

So the recommended setup is to run py2loggly locally on each server and use the `DatadgramHandler`.

#### Example

    import logging, logging.handlers

    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.DEBUG)
    socketHandler = logging.handlers.SocketHandler('localhost',
                        logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    # don't bother with a formatter, since a socket handler sends the event as
    # an unformatted pickle
    rootLogger.addHandler(socketHandler)

    # Now, we can log to the root logger, or any other logger. First the root...
    logging.info('Jackdaws love my big sphinx of quartz.')

License
-------

MIT
