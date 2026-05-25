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
	docker exec duck-contest-app-1 uv run alembic -c database/alembic.ini upgrade head

migrate:
	docker exec duck-contest-app-1 uv run alembic -c database/alembic.ini revision --autogenerate -m "initial models"

seed:
	docker-compose exec app uv run python ./scripts/seed.py


format:
	uv run ruff format .
	uv run ruff check . --fix

check:
	uv run ruff check .
