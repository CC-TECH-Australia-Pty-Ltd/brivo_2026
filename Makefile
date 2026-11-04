# Common tasks. Run `make help` for the list.
.DEFAULT_GOAL := help
BACKEND := cd backend &&

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-14s %s\n", $$1, $$2}'

setup: ## Install backend and frontend dependencies, create backend/.env
	$(BACKEND) uv sync
	cd frontend && npm install
	@test -f backend/.env || cp backend/.env.example backend/.env

db-up: ## Start local PostgreSQL (Docker)
	docker compose up -d --wait db

db-down: ## Stop local PostgreSQL (keeps data)
	docker compose down

db-reset: ## Delete local database data, start fresh and migrate
	docker compose down -v && docker compose up -d --wait db
	$(MAKE) migrate

migrate: ## Apply pending Alembic migrations (backend/migrations/versions)
	$(BACKEND) uv run alembic upgrade head

migrate-status: ## Show the database's current migration and the latest one
	$(BACKEND) uv run alembic current && uv run alembic heads

migration: ## Create the next numbered migration: make migration name="add participant"
	@test -n "$(name)" || (echo 'usage: make migration name="what it changes"' && exit 1)
	$(BACKEND) uv run alembic revision -m "$(name)" --rev-id "$$(uv run python -c 'from alembic.config import Config; from alembic.script import ScriptDirectory; h = ScriptDirectory.from_config(Config("alembic.ini")).get_current_head(); print(f"{int(h or 0) + 1:04d}")')"

api: ## Run the API with auto-reload on http://localhost:8000
	$(BACKEND) uv run uvicorn brivo.main:app --reload

web: ## Run the React app on http://localhost:5173
	cd frontend && npm run dev

check: ## Lint, type-check, boundary-check and test everything
	$(BACKEND) uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run lint-imports && uv run pytest
	cd frontend && npm run lint && npm run build

.PHONY: help setup db-up db-down db-reset migrate migrate-status migration api web check
