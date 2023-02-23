#!/usr/bin/env bash
touch /app/config/uwsgi.sock
chmod 777 -R /app/config/uwsgi.sock
uwsgi --ini /app/config/uwsgi.ini --enable-threads