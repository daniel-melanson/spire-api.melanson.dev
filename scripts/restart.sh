#!/bin/bash
docker compose down --remove-orphans
docker system prune --all --force
docker compose up --build --remove-orphans --detach --wait
