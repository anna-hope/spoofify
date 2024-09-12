FROM ghcr.io/astral-sh/uv:0.4.9-python3.12-bookworm-slim
RUN --mount=source=dist,target=/dist uv pip install --system --no-cache /dist/*.whl
CMD ["python", "-m", "hypercorn", "-b", "0.0.0.0:8000", "spoofify:app"]

