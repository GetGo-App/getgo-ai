# read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

FROM python:3.10

RUN useradd -m -u 1000 user

WORKDIR /app

COPY --chown=user ./requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user . /app

RUN pip install -e .

CMD ["uvicorn", "agents.main:app", "--host", "0.0.0.0", "--port", "7860"]
