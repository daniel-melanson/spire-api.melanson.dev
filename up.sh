#!/bin/bash
docker-compose down
docker image prune --force
docker compose up --remove-orphans --wait --detach --build
