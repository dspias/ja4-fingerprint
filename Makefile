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
ja4-http1:
	docker exec -it ja4_container python3 ja4.py pcap/http1.pcapng -J

ja4-http1-cookies:
	docker exec -it ja4_container python3 ja4.py pcap/http1-with-cookies.pcapng -J

ja4-http2-cookies:
	docker exec -it ja4_container python3 ja4.py pcap/http2-with-cookies.pcapng -J

ja4-ipv6:
	docker exec -it ja4_container python3 ja4.py pcap/ipv6.pcapng -J

ja4-latest:
	docker exec -it ja4_container python3 ja4.py pcap/latest.pcapng -J

# Run terminal of the python container
ja4h-http1:
	docker exec -it ja4_container python3 ja4h.py pcap/http1.pcapng -J

ja4h-http1-cookies:
	docker exec -it ja4_container python3 ja4h.py pcap/http1-with-cookies.pcapng -J

ja4h-http2-cookies:
	docker exec -it ja4_container python3 ja4h.py pcap/http2-with-cookies.pcapng -J

ja4h-ipv6:
	docker exec -it ja4_container python3 ja4h.py pcap/ipv6.pcapng -J

ja4h-latest:
	docker exec -it ja4_container python3 ja4h.py pcap/latest.pcapng -J

script ?= ja4.py
pcap ?= http1.pcapng

query:
	docker exec -it ja4_container python3 ${script} pcap/${pcap} -J