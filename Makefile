.PHONY: setup
setup:
	[ -f requirements.txt ] && pip install -r requirements.txt; \
	pip install .

.PHONY: setup-dev
setup-dev:
	[ -f requirements.txt ] && pip install -r requirements.txt; \
	[ -f dev-requirements.txt ] && pip install -r dev-requirements.txt; \
	pip install -e ".[dev]"; \
	pre-commit install

.PHONY: pin
pin:
	pip-compile --output-file=requirements.txt pyproject.toml
	pip-compile --extra=dev --output-file=dev-requirements.txt pyproject.toml
	
.PHONY: pin-upgrade
pin-upgrade:
	pip-compile --upgrade --output-file=requirements.txt pyproject.toml
	pip-compile --upgrade --extra=dev --output-file=dev-requirements.txt pyproject.toml

.PHONY: sync
sync:
	pip-sync dev-requirements.txt requirements.txt
	pip install -e ".[dev]"

.PHONY: all
all: format lint type-check

.PHONY: format
format:
	isort .
	yapf --recursive -i -p .

.PHONY: lint
lint:
	flake8 .
	pylint $$(git ls-files "*.py")

.PHONY: lint-cached
lint-cached:
	git_files=$$(git --no-pager diff --cached --name-only | grep \.py$$); \
	[ -z "$$git_files" ] || (flake8 $$git_files && pylint $$git_files)

.PHONY: format-cached
format-cached:
	git_files=$$(git --no-pager diff --cached --name-only | grep \.py$$); \
	[ -z "$$git_files" ] || (isort $$git_files && yapf -i -p $$git_files)

.PHONY: test
test:
	pytest

.PHONY: type-check
type-check:
	mypy -p jira_access

.PHONY: type-check-cached
type-check-cached:
	git_files=$$(git --no-pager diff --cached --name-only | grep \.py$$); \
	[ -z "$$git_files" ] || mypy $$git_files

.PHONY: tox
tox:
	@echo "Be sure not to be in a virtual environment and be sure that python 3.7, 3.8, 3.9, 3.10 and 3.11 are installed."
	rm -rf .tox
	tox -p auto
