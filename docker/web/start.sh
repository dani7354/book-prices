#!/bin/bash

# start uwsgi application
newrelic-admin run-program /usr/local/bin/uwsgi /usr/local/bookprices_web/bookprices/web/bookprices_web.ini
