#!/bin/bash
declare -r docker_compose_filepath=$1

if [[ -z "$docker_compose_filepath" ]]; then
  echo "Missing argument: docker-compose filepath"
  exit 1
fi

case $2 in
all | default)
  docker compose -f "$docker_compose_filepath" --profile default up --build
  ;;
db)
  docker compose -f "$docker_compose_filepath" --profile db_only up --build
  ;;
*)
  echo "Invalid or missing argument for mode (all, db)"
  exit 1
  ;;
esac
