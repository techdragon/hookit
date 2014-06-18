# Bind GitHub WebHooks to actions

    Usage:
      hookit [--scripts=<dir>] [--listen=<address>] [--port=<port>]

    Options:
      -v --version        Show version
      --scripts=<dir>     Where to look for hook scripts [default: .]
      --listen=<address>  Server address to listen on [default: 0.0.0.0]
      --port=<port>       Server port to listen on [default: 8000]

## Execute scripts in any language

On webhook the server will try to execute a script located at `<scripts>/<repository>/<branch>`.
Note that the script `<branch>` should not have a suffix.
If you want to execute a webhook for the branch `master`, your script must be named `master` not `master.sh`, or `master.py`, or `master.rb`, etc.
On POSIX operating systems, set the executable permission on the script. ( `chmod +x <filename>` )
The script will run with arguments containing repository, branch and commit hash. An example script may look like:

    #!/usr/bin/env python

    import sys
    from subprocess import call

    branch = sys.argv[1]
    repo = sys.argv[2]

    message = 'You have changes in the %s branch of %s' % (branch, repo)
    call(['/usr/bin/say', message])

## Installation

This package is availiable on Python Package Index

    pip install hookit

## Security

The server will only accept requests from GitHub's trusted servers and run scripts from an jailed directory.

Whitelisted networks:
* 192.30.252.0/22
* 204.232.175.64/27
