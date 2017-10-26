#!/usr/bin/env bash

if [ -d ./script/ ]; then
    touch ./script/local.env
fi

source ./load_env.sh

docker-compose down
echo -e "\e[0;32mService will be visible at https://${FQDN}:${HTTPS_PORT_HOST}/\e[m"
docker-compose up --build $1
echo -e "\e[0;32mService will be visible at https://${FQDN}:${HTTPS_PORT_HOST}/\e[m"

if [ "$1" == "-d" ]; then
    echo -e "\e[0;32mYou are following logs, pressing CTRL+C will NOT stop the containers\e[m"
    docker-compose logs -f
else
    docker-compose ps
fi