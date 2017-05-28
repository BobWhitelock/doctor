
.PHONY: test
# Run tests this way so imports work (see
# http://stackoverflow.com/a/34140498/2620402).
test:
	. venv/bin/activate && python -m pytest src/ --verbose

.PHONY: ipython
ipython:
	. venv/bin/activate && ipython

.PHONY: freeze
freeze:
	. venv/bin/activate && pip freeze > requirements.txt
