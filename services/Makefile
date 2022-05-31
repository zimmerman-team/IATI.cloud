up:
	sudo ifconfig lo0 alias 127.0.3.1 up
	docker image prune -f
	docker-compose up -d

down:
	docker-compose down

build:
	docker image prune -f
	docker-compose build
	docker image prune -f

status:
	docker-compose ps
