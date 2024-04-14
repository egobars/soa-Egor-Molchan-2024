#!/bin/bash
docker run --rm --network="snet-network" -v "$(pwd)/migrations":/snet liquibase/liquibase:4.19.0 --defaultsFile=/snet/dev.properties update
uvicorn main:server --host=0.0.0.0 --port=8000 --reload
