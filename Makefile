SHELL := /bin/bash

.PHONY: fmt lint test up down

fmt:
	python -m ruff format services shared scripts
	terraform -chdir=infra/terraform fmt -recursive || true

lint:
	python -m ruff check services shared scripts

test:
	pytest -q

up:
	docker compose up --build

down:
	docker compose down
