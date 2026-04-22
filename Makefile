deps:
	uv sync  

db-up:
	docker compose up -d db

migrate: 
	uv run alembic -c src/database/alembic.ini revision --autogenerate -m "initial models"

migrate-up: 
	uv run alembic -c src/database/alembic.ini upgrade head

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
