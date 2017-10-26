#!/bin/bash

# Collect static files
#pip install -r /code/requirements.txt

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate


# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput


mkdir -p $(python manage.py shell -c "from django.conf import settings; print settings.MEDIA_ROOT")
chmod 777 $(python manage.py shell -c "from django.conf import settings; print settings.MEDIA_ROOT")

#Setting up cron tasks
echo "Cron tasks"
#python manage.py crontab remove
python manage.py crontab add
#python manage.py crontab show
service cron start

if [ "$1" == "loaddata" ]; then
    echo "Load initial data"
    #./misc/tool_shed.py find-in-json "$(./manage.py dumpdata auth.group 2>/dev/null)" 'name' --recursive --return-all --print-values --separator '\n'
    python manage.py loaddata */fixtures/*.json
elif [ "$1" == "do_not_start" ]; then
    echo "Entrypoint have been run with success, we have been ASKED to NOT START the web server, probably for a good reason"
else
    rm -f /var/run/apache2/apache2.pid
    rm -rf /run/httpd/* /tmp/httpd*
    chmod -R 777 /tmp/*
    exec "$@"
fi

# Start server
#echo "Starting server"
#python manage.py runserver 0.0.0.0:8001
