.PHONY: run test lint datos

run:
	streamlit run app.py

test:
	pytest

lint:
	ruff check .

datos:
	python scripts/preparar_datos.py
