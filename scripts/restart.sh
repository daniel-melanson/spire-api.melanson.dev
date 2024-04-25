#!/bin/bash
docker-compose down --remove-orphans
docker-compose up --build --remove-orphans --detach
