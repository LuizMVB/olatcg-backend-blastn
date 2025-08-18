# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9-slim-bookworm

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /requirements.txt
COPY ./app /app
COPY ./build /build

WORKDIR /app

RUN bash /build/setup.sh

RUN mkdir -p /blast_seed && cp -a /blast/. /blast_seed/

ENV PATH="/scripts:/py/bin:$PATH"
ENV BLASTDB="/blast/db"

COPY build/docker-entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["python", "-u", "/app/main.py"]