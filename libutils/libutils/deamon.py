#!/usr/bin/python3
import atexit
import os
import signal
import sys


def deamon(pid_file: str, log_file: str, prog_name: str):
    """
    pid_file: full path of pid file, it is suggested in /tmp
    log_file: full path of log file.
    """
    # This is a daemon programe, which will start after
    # system booted.
    #
    # It is defined to start by rc.local.
    #
    # fork a sub process from father
    if os.path.exists(pid_file):
        raise RuntimeError(f"{prog_name} is already running")
    # the first fork.
    if os.fork() > 0:
        raise SystemExit(0)

    os.chdir('/')
    os.umask(0)
    os.setsid()
    # Second fork
    if os.fork() > 0:
        raise SystemExit(0)
    # Flush I/O buffers
    sys.stdout.flush()
    sys.stderr.flush()

    # with open(log_file, 'rb', 0) as read_null:
    # os.dup2(read_null.fileno(), sys.stdin.fileno())
    with open(log_file, 'a') as write_null:
        # Redirect to 1 which means stdout
        os.dup2(write_null.fileno(), 1)
    with open(log_file, 'a') as error_null:
        # Redirect to 2 which means stderr
        os.dup2(error_null.fileno(), 2)
    # write parent process pid into pid file.
    if pid_file:
        with open(pid_file, 'w+') as f:
            f.write(str(os.getpid()))
        atexit.register(os.remove, pid_file)

    def sigterm_handler(signo, frame):
        raise SystemExit(1)
    signal.signal(signal.SIGTERM, sigterm_handler)
