# Arambh — Makefile shortcuts

.PHONY: up down build logs shell-backend shell-ai test clean seed

## Start all services
up:
	docker compose up --build

## Start in background
up-bg:
	docker compose up --build -d

## Stop all services
down:
	docker compose down

## Stop and remove all volumes (DELETES DATA)
clean:
	docker compose down -v --remove-orphans

## Rebuild specific service
build-backend:
	docker compose up --build backend

build-ai:
	docker compose up --build ai-services

build-frontend:
	docker compose up --build frontend

## View logs
logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-ai:
	docker compose logs -f ai-services

logs-crawler:
	docker compose logs -f crawler

## Shell access
shell-backend:
	docker compose exec backend bash

shell-ai:
	docker compose exec ai-services bash

shell-mongo:
	docker compose exec mongodb mongosh -u admin -p arambh_secret arambh

## Run tests
test:
	docker compose exec backend pytest tests/ -v
	docker compose exec ai-services pytest tests/ -v
	docker compose exec crawler pytest tests/ -v

test-backend:
	docker compose exec backend pytest tests/ -v

test-ai:
	docker compose exec ai-services pytest tests/ -v

## RAG evaluation
eval:
	docker compose exec ai-services python -m app.utils.evaluation

## With monitoring stack
up-monitoring:
	docker compose -f docker-compose.yml -f devops/monitoring/docker-compose.monitoring.yml up -d

## Help
help:
	@echo "Available commands:"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make clean       - Stop + delete all data"
	@echo "  make test        - Run all tests"
	@echo "  make eval        - Run RAG evaluation"
	@echo "  make logs        - View all logs"
	@echo "  make shell-backend - Shell into backend"
	@echo "  make up-monitoring - Start with Prometheus/Grafana"
