.PHONY: up down build logs migrate test

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

migrate:
	docker-compose run --rm web alembic upgrade head

migration:
	docker-compose run --rm web alembic revision --autogenerate -m "$(msg)"

test:
	docker-compose run --rm web pytest
