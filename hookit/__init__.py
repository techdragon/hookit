# -*- coding: utf8 -*-

"""
Usage:
  hookit [--scripts=<dir>] [--listen=<address>] [--port=<port>]

args:
  -v --version        Show version
  --scripts=<dir>     Where to look for hook scripts [default: .]
  --listen=<address>  Server address to listen on [default: 0.0.0.0]
  --port=<port>       Server port to listen on [default: 8000]
"""

import sys
import json
import struct
import socket
import logging
import os.path
import urlparse
from cgi import parse_qs
from subprocess import call

from docopt import docopt
from github3 import GitHub
from netaddr import IPNetwork
from netaddr import IPAddress

from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

args = docopt(__doc__, version=0.1)
gh = GitHub()


def webhook_from_github(client):
    """Call the github api to check what the valid IP addresses are.
     This is inside the function to ensure we check against the valid
     IP addresses at the time the webhook was recieved."""
    github_info = gh.meta()
    for address in github_info['hooks']:
        if IPAddress(client) in IPNetwork(str(address)):
            return True
    return False



class HookHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_forbidden()

    def do_POST(self):
        # Reject all requests from non-Github IPs
        # if not in_whitelist(self.client_address[0]):
        if not webhook_from_github(self.client_address[0]):
            logging.error("Webhook came from untrusted IP!")
            self.send_forbidden()
            return

        # Read POST data
        length = int(self.headers.getheader('Content-Length'))
        data = self.rfile.read(length)
        payload = json.loads(str(data))

        if not payload:
            self.send_forbidden()
            return

        hook_trigger(payload)

        self.send_ok()

    def send_ok(self):
        self.send_response(200)
        self.end_headers()

    def send_forbidden(self):
        self.send_response(403)
        self.end_headers()


def hook_trigger(payload):
    # Check if the webhook contains a reference to a repository
    if not payload['ref']:
        logging.error(
            "Payload did not contain a refference to a repository. " +
            "This is normal for the first webhook payload sent from " +
            "GitHub after setting up your webhook."
        )
        logging.error("Payload : " + str(payload))
        return

    ref = payload['ref']
    after = payload['after']
    repo = payload['repository']['name']
    branch = ref.split('/')[-1]

    jail = os.path.abspath(args['--scripts'])
    trigger = os.path.abspath('%s/%s/%s' % (jail, repo, branch))

    # Check if absolute trigger path resides in jail directory
    if not os.path.commonprefix([trigger, jail]).startswith(jail):
        logging.warning('%s: Tried to execute outside jail' % trigger)
        return

    # No action
    if not os.path.isfile(trigger):
        logging.info('%s: No such trigger' % trigger)
        return

    logging.info('%s: Executing trigger' % trigger)
    call([trigger, branch, repo, after])


def run():
    host = args['--listen']

    try:
        port = int(args['--port'])
    except ValueError:
        logging.error('Binding port must be integer')
        sys.exit(1)

    try:
        http = HTTPServer((host, port), HookHandler)
        http.serve_forever()
    except (socket.gaierror, socket.error) as e:
        startup_error(e.strerror.capitalize())
    except OverflowError as e:
        startup_error('Port must be in interval 0-65535')
    except KeyboardInterrupt:
        print('')
        sys.exit(0)


def startup_error(message):
    logging.error('Could not start server: %s' % message)
    sys.exit(1)


if __name__ == '__main__':
    run()
