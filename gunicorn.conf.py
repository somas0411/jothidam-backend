# Read automatically by `gunicorn app:app`.
# One worker keeps memory low on small instances; the longer timeout allows
# for report generation on a slow or just-woken server.
# The request limits in app.py are counted in the worker's memory, so they are
# exact only with one worker.
workers = 1
threads = 2
timeout = 120
