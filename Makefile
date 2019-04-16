
default: watch

watch:
	find . | grep -v git | entr molecule converge
