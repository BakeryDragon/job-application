# Run black on all Python files in the current directory
black:
	black .

# Run isort on all Python files in the current directory
isort:
	isort .

# Run both black and isort
format: black isort

.PHONY: black isort format

start:
	python run.py