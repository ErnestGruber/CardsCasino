PROJECT_NAME = cardcasino
TEST_PATH = ./tests

HARBOR_USERNAME ?=
HARBOR_PASSWORD ?=
HARBOR_REGISTRY ?=
IMAGE_NAME ?= backend/cardcasino
TAG = $(shell git rev-parse --short=8 HEAD)

ifeq ($(OS),Windows_NT)
    DEL = del /s /q
    RMDIR = rmdir /s /q
    FIND_PYCACHE = for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
    VENV_BIN = .venv\Scripts\
    PYTHON = python
else
    DEL = rm -f
    RMDIR = rm -rf
    FIND_PYCACHE = find . -type d -name __pycache__ -exec rm -r {} \+
    VENV_BIN = .venv/bin/
    PYTHON = python3.12
endif

lint:  ## Lint project code.
	$(VENV_BIN)poetry run ruff check --fix .

develop: clean_dev  ##@Develop Create project venv
	$(PYTHON) -m venv .venv
	$(VENV_BIN)pip install -U pip poetry
	$(VENV_BIN)poetry config virtualenvs.create false
	$(VENV_BIN)poetry install
	$(VENV_BIN)pre-commit install

local:
	docker compose -f docker-compose.dev.yaml up --build --force-recreate --remove-orphans --renew-anon-volumes

local_down: ##@Develop Stop dev containers with delete volumes
	docker compose -f docker-compose.dev.yaml down -v

docker-apply-migrations:
	docker compose exec back $(VENV_BIN)python -m $(PROJECT_NAME).infrastructure.database upgrade head

test: ##@Tests Run tests
	$(VENV_BIN)pytest -vx $(TEST_PATH)

test-ci: ##@Test Run tests with pytest and coverage in CI
	$(VENV_BIN)coverage run -m pytest $(TEST_PATH) --junitxml=junit.xml
	$(VENV_BIN)coverage report
	$(VENV_BIN)coverage xml

lint-ci: ruff mypy  ##@Linting Run all linters in CI

ruff: ##@Linting Run ruff
	$(VENV_BIN)ruff check ./$(PROJECT_NAME)

mypy: ##@Linting Run mypy
	$(VENV_BIN)mypy ./$(PROJECT_NAME) --config-file ./pyproject.toml --enable-incomplete-feature=NewGenericSyntax

clean_dev:
	$(RMDIR) .venv

clean_pycache:
	$(FIND_PYCACHE)

build:
	@echo -n "$(HARBOR_PASSWORD)" | docker login --username $(HARBOR_USERNAME) --password-stdin $(HARBOR_REGISTRY)
	@docker build -t $(HARBOR_REGISTRY)/$(IMAGE_NAME):$(TAG) -f Dockerfile .
	@docker push $(HARBOR_REGISTRY)/$(IMAGE_NAME):$(TAG)
	@echo "Pushing Docker image: $(HARBOR_REGISTRY)/$(IMAGE_NAME):$(TAG)"
	@docker logout $(HARBOR_REGISTRY)
	@echo "Build and push process completed."
