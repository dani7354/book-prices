#!/bin/bash

# start nginx service
service nginx start &

# start uwsgi application
/usr/local/bin/uwsgi /usr/local/bookprices_web/web/bookprices_web.ini

# wait for any process to exit
wait -n

# exit with status of process that exited first
exit $?
