
default: watch

watch:
	find . | grep -v git | entr pipenv run molecule converge
