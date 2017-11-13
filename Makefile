#
# Utility tasks
#

build:
	docker-compose build

migrate: build
	docker-compose run oipa python manage.py migrate

runserver: migrate
	docker-compose up

test: build
	docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm oipa python manage.py test
