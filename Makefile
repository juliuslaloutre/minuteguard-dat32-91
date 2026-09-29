.PHONY: install test lint demo evaluate

install:
	python3 -m venv .venv
	.venv/bin/python -m pip install -e ".[dev]"

test:
	.venv/bin/python -m pytest --cov=minuteguard --cov-report=term-missing

lint:
	.venv/bin/python -m ruff check .
	.venv/bin/python -m mypy src

demo:
	.venv/bin/minuteguard audit data/sample_meeting.txt --provider fixture --output outputs/runs/demo.json --report outputs/runs/demo.md

evaluate:
	.venv/bin/minuteguard evaluate --predictions data/fixture_predictions.json --output outputs/runs/evaluation.json

