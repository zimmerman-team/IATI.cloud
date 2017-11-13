#
# Utility tasks
#

build:
	docker-compose build

migrate: build
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml run oipa /app/src/bin/wait-for-postgres.sh python manage.py migrate

runserver: migrate
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

test: build
	docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm oipa python manage.py test

test-coverage: build
	docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm oipa coverage run --source=. --omit=*__init__*,*data_backup* manage.py test --nomigrations

coveralls: build
	docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm oipa coveralls

