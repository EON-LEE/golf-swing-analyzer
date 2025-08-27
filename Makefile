.PHONY: install install-dev test lint format type-check clean run

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt -r requirements-dev.txt
	pre-commit install

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=. --cov-report=html

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

format:
	black .
	isort .

type-check:
	mypy .

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

run:
	streamlit run app.py
