#!/bin/bash

if [[ -z "$1"  ]]; then
  echo "Missing argument: name of container"
  exit 1
fi

container_name="$1"
container_id="$(docker container ps |grep $container_name | awk '{ print $1 }')"

if [[ -z "$container_id"  ]]; then
  echo "Couldn't find id of running container!"
  exit 1
fi

docker exec -it "$container_id" sh