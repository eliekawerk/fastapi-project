lint-and-fix:
	python -m black storeapi
	python -m  isort storeapi
	python -m ruff storeapi --fix