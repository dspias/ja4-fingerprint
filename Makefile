#-----------------------------------------------------------
# Docker
#-----------------------------------------------------------

# Wake up docker containers
up:
	docker-compose up -d

# Shut down docker containers
down:
	docker-compose down

# Build and up docker containers
build:
	docker-compose up -d --build

# Build containers with no cache option
build-no-cache:
	docker-compose build --no-cache

# Build and up docker containers
rebuild: down build

# Build and up docker containers
restart: down up

# Run terminal of the python container
python:
	docker exec -it ja4_container bash

# Run terminal of the python container
tls:
	docker exec -it ja4_container python3 ja4.py pcap/tls-handshake.pcapng -J