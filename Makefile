deps:
	uv sync  

db-up:
	docker compose up -d db

migration: 
	uv run alembic -c src/database/alembic.ini revision --autogenerate -m "initial models"

migrate: 
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
