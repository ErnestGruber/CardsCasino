PROJECT_NAME = cardcasino
TEST_PATH = ./tests

HARBOR_USERNAME ?=
HARBOR_PASSWORD ?=
HARBOR_REGISTRY ?=
IMAGE_NAME ?= backend/cardcasino
TAG = $(shell git rev-parse --short=8 HEAD)

lint:  ## Lint project code.
	poetry run ruff check --fix .

develop: clean_dev  ##@Develop Create project venv
	python3.12 -m venv .venv
	.venv/bin/pip install -U pip poetry
	.venv/bin/poetry config virtualenvs.create false
	.venv/bin/poetry install
	.venv/bin/pre-commit install

local:
	docker compose -f docker-compose.dev.yaml up --build --force-recreate --remove-orphans --renew-anon-volumes

local_down: ##@Develop Stop dev containers with delete volumes
	docker compose -f docker-compose.dev.yaml down -v

docker-apply-migrations:
	docker compose exec back python -m $(PROJECT_NAME).infrastructure.database upgrade head

test: ##@Tests Run tests
	.venv/bin/pytest -vx $(TEST_PATH)

test-ci: ##@Test Run tests with pytest and coverage in CI
	.venv/bin/coverage run -m pytest $(TEST_PATH) --junitxml=junit.xml
	.venv/bin/coverage report
	.venv/bin/coverage xml

lint-ci: ruff mypy  ##@Linting Run all linters in CI

ruff: ##@Linting Run ruff
	.venv/bin/ruff check ./$(PROJECT_NAME)

mypy: ##@Linting Run mypy
	.venv/bin/mypy ./$(PROJECT_NAME) --config-file ./pyproject.toml --enable-incomplete-feature=NewGenericSyntax

clean_dev:
	rm -rf .venv/

clean_pycache:
	find . -type d -name __pycache__ -exec rm -r {} \+

build:
	@echo -n "$(HARBOR_PASSWORD)" | docker login --username $(HARBOR_USERNAME) --password-stdin $(HARBOR_REGISTRY)
	@docker build -t $(HARBOR_REGISTRY)/$(IMAGE_NAME):$(TAG) -f Dockerfile .
	@docker push $(HARBOR_REGISTRY)/$(IMAGE_NAME):$(TAG)
	@echo "Pushing Docker image: $(HARBOR_REGISTRY)/$(IMAGE_NAME):$(TAG)"
	@docker logout $(HARBOR_REGISTRY)
	@echo "Build and push process completed."