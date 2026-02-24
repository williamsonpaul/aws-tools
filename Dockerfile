FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY pyproject.toml setup.py ./

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["aws-asg"]
