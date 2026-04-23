up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build 

rebuild:
	docker-compose down
	docker-compose build 
	docker-compose up -d

migration: 
	uv run alembic -c src/database/alembic.ini revision --autogenerate -m "initial models"

migrate: 
	uv run alembic -c src/database/alembic.ini upgrade head

format:
	uv run ruff format .
	uv run ruff check . --fix

check:
	uv run ruff check .