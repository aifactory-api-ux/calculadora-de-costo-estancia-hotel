# La librería no tiene servidor: la imagen ejecuta la suite de pruebas.
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pytest

COPY src/ ./src/
COPY tests/ ./tests/
COPY pyproject.toml ./
COPY README.md ./

CMD ["python", "-m", "pytest", "tests"]
