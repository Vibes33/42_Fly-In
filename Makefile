# Permet de capturer les arguments passés après make run ou make debug
ifeq (run,$(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(RUN_ARGS):;@:)
endif
ifeq (debug,$(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(RUN_ARGS):;@:)
endif

.PHONY: install run debug clean lint

install:
	pip install -r requirements.txt || true

run:
	@python3 -m src.main $(if $(RUN_ARGS),$(RUN_ARGS),maps/example.map)

debug:
	@python3 -m pdb -m src.main $(if $(RUN_ARGS),$(RUN_ARGS),maps/example.map)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache

lint:
	flake8 src/
	mypy src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
