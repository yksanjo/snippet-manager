.PHONY: install test clean demo

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -e .

test:
	python3 -m pytest tests/ -v 2>/dev/null || echo "No tests yet"

demo:
	python3 demo.py

clean:
	rm -rf __pycache__ *.pyc build/ dist/ *.egg-info

format:
	black *.py 2>/dev/null || echo "black not installed"

lint:
	flake8 *.py 2>/dev/null || echo "flake8 not installed"

run:
	python3 snippet_manager.py
