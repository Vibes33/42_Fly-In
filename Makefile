ifeq (run,$(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # Ignore les arguments supplémentaires s'ils ressemblent à des targets
  $(eval $(RUN_ARGS):;@:)
endif

.PHONY: install run debug clean lint

install:
	python3 -m pip install -r requirements.txt || true

run:
	@python3 -m src.main $(if $(RUN_ARGS),$(RUN_ARGS),maps/example.map) $(ARGS) --capacity-info

debug:
	@python3 -m pdb -m src.main $(if $(RUN_ARGS),$(RUN_ARGS),maps/example.map) $(ARGS)
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache

lint:
	flake8 src/
	mypy src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
