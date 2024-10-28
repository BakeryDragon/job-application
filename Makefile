# Define the directories to format
SRC_FILES = app.py prompt.py

# Target to run black
black:
	black $(SRC_FILES)

# Target to run isort
isort:
	isort $(SRC_FILES)

# Target to run both black and isort
format: black isort

.PHONY: black isort format
