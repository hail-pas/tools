DIRS = gui/ parser/ translate/

deps:
	@poetry install --no-root

up:
	@poetry update

style:
	@isort --length-sort -src $(DIRS)
	@black $(DIRS)
