#!/bin/bash

if [[ -z "$1" ]]; then
  echo "Missing argument: mysqldump file"
  exit 1
fi

output_file=$1

container_name="mysql:8.0"
container_id=$(docker container ps |grep "$container_name" | awk '{ print $1 }')

if [[ -z "$container_id" ]]; then
  echo "Couldn't find id of running container!"
  exit 1
fi

docker exec $container_id sh -c 'exec mysqldump --no-data BookPrices -uroot -p"$MYSQL_ROOT_PASSWORD"' > $output_file
