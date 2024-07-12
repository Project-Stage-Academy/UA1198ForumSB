include .env
export

run:
	cd forum && ./manage.py runserver

run_smtp:
	./scripts/run_smtp_server.sh

migrations:
	cd forum && ./manage.py makemigrations

migrate:
	cd forum && ./manage.py migrate

show_urls:
	./scripts/list_urls.sh
