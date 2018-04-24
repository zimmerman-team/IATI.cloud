#
# Utility tasks
#

build:
	docker-compose build

migrate: build
	docker-compose -f docker-compose.dev.yml run oipa /app/src/bin/wait-for-postgres.sh python manage.py migrate

runserver: migrate
	docker-compose -f docker-compose.dev.yml up

test: build
	docker-compose -f docker-compose.test.yml build
	docker-compose -f docker-compose.test.yml run --rm oipa python manage.py test --nomigrations

test-coverage: build
	docker-compose -f docker-compose.test.yml run --rm oipa coverage run --source=. --omit=*__init__*,*data_backup* manage.py test --nomigrations

test-docker-cloud: build
	@# run 'sut' service
	docker-compose -f docker-compose.test.yml build
	docker-compose -f docker-compose.test.yml run --rm sut


coveralls: build
	docker-compose -f docker-compose.test.yml run --rm oipa coveralls

lint:
	flake8 OIPA --statistics

format-code:
	autopep8 -i -r -a OIPA --max-line-length 99

