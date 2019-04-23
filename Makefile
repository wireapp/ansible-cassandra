.PHONY: default
default: watch

.PHONY: watch
watch:
	find . | grep -v git | entr molecule converge
