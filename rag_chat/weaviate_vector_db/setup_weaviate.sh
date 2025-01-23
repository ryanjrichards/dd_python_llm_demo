#!/bin/bash

# Start the Docker containers using docker-compose with the specified compose file
docker compose -f "$(dirname "$0")/compose.yaml" up