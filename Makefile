.PHONY: default
default: watch

.PHONY: watch
watch:
	find . | grep -v git | entr molecule converge

.PHONY: changelog
changelog:
	docker run -it --rm -v "$(pwd)":/usr/local/src/your-app ferrarimarco/github-changelog-generator:1.14.3 -u wireapp -p ansible-cassandra -t "$$GITHUB_TOKEN"
