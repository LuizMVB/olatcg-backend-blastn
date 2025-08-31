
# Homology BLASTN

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/container-Docker-blue.svg)](https://www.docker.com/)
[![Postgres](https://img.shields.io/badge/PostgreSQL-psycopg2-green.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

**Homology BLASTN** is an open-source, **dockerized** project that runs BLASTN homology analysis with a clean, modular architecture (Clean Architecture + SOLID).  
It separates concerns into **domain**, **application (use cases)**, **infrastructure (adapters)**, and **presentation** layers. Dependencies are injected via ports (protocols).

---

## 🚀 TL;DR — Run with Docker

```bash
# 1) Build images and prepare volumes
docker compose build

# 2) Start the consumer (detached)
docker compose up -d

# 3) Tail logs
docker compose logs -f consumer
```

> On the **first run**, the container will **seed** `/blast` (taxonomy, sequences, BLAST DB) into the persistent volume.
> Subsequent runs are fast because the seed is **idempotent**.

To stop:
```bash
docker compose down
```

To reset everything (including volumes and seed):
```bash
docker compose down -v  # CAUTION: removes volumes (blast DB and storage)
```

---

## 🧱 Project is Containerized

This repository ships with:
- **Dockerfile (multi-stage)** — builds a slim runtime image with BLAST+ installed and a pre-built seed at `/blast_seed`.
- **docker-compose.yml** — orchestrates the `consumer` service, volumes, healthcheck and env-files.
- **Entrypoint** — `/usr/local/bin/entrypoint.sh` seeds `/blast` from `/blast_seed` **only if empty** (idempotent). Then it execs the main command (`python -u /app/main.py`).

### Why seed?
Building the BLAST DB (downloading sequences, taxdump, creating taxid map, `makeblastdb`) is expensive. We do it during image build and store the result in `/blast_seed`.  
At runtime, the entrypoint copies `/blast_seed` → `/blast` **iff** the `/blast` volume is empty or missing `combined_sequences.fna`.

---

## 🧰 Requirements

- Docker + Docker Compose
- Network access during build (to fetch NCBI files) — only needed when building the image.

---

## ⚙️ Environment Files

Create two files under `env/` (or reuse the provided examples):

`env/app.env`:
```dotenv
# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest
RABBITMQ_BLASTN_QUEUE_NAME=blastn-jobs
RABBITMQ_PREFETCH=1
RABBITMQ_HEARTBEAT=60
RABBITMQ_BLOCKED_TIMEOUT=300
RABBITMQ_CONN_ATTEMPTS=12

# Logging
LOG_LEVEL=INFO

# Storage
STORAGE_FILE=/mnt/data/blastn_storage

# Taxonomy (seeded inside the container; you can override)
TAXID_MAP_FILE=/blast/taxonomy/taxid_map.txt
NODES_FILE=/blast/taxonomy/nodes.dmp
NAMES_FILE=/blast/taxonomy/names.dmp
```

`env/db.env`:
```dotenv
DB_NAME=homology
DB_USER=postgres
DB_PASS=postgres
DB_HOST=postgres
```

> If you use an external Postgres or RabbitMQ, just update the host/user/pass.

---

## 🐳 docker-compose.yml — What it does

Key bits of the provided compose file:
```yaml
services:
  consumer:
    build:
      context: .
      dockerfile: Dockerfile
    image: homology-blastn:latest
    command: ["python", "-u", "/app/main.py"]   # main process
    env_file:
      - ./env/app.env
      - ./env/db.env
    restart: unless-stopped
    volumes:
      - blast_data:/blast                       # persists BLAST taxonomy + DB
      - blastn_storage:/mnt/data/blastn_storage # persists compressed inputs/outputs
      # - ./app:/app                            # uncomment for live-reload in dev
    healthcheck:
      test: ["CMD-SHELL", "blastn -version >/dev/null 2>&1"]
      interval: 30s
      timeout: 5s
      retries: 5

volumes:
  blast_data:
  blastn_storage:
```

- **Volumes**: 
  - `blast_data` keeps `/blast` across restarts/rebuilds (taxonomy dump, sequences, BLAST DB).
  - `blastn_storage` keeps `/mnt/data/blastn_storage` (compressed query/output files).
- **Healthcheck** confirms `blastn` is available.
- Comment/uncomment the bind mount `./app:/app` for **development** without rebuilding.

---

## 🔑 Entrypoint: how it works

`/usr/local/bin/entrypoint.sh` runs **before** your main command:

1. Checks if `/blast` exists and has `combined_sequences.fna`.
2. If **empty** (first run), it copies everything from **`/blast_seed` to `/blast`** (taxonomy, sequences, DB).
3. Executes the container command (e.g., `python -u /app/main.py`).

This is safe to run repeatedly and keeps startup quick after the first seeding.

---

## 🧪 Local Development

- Enable live-reload by mounting your code:
  ```yaml
  # docker-compose.yml
  volumes:
    - blast_data:/blast
    - blastn_storage:/mnt/data/blastn_storage
    - ./app:/app         # <— mount your working tree
  ```
- Use `LOG_LEVEL=DEBUG` in `env/app.env` to see detailed logs.
- If you change the set of sequences or taxonomy sources, **rebuild** the image to refresh `/blast_seed`:
  ```bash
  docker compose build --no-cache
  docker compose up -d --force-recreate
  ```

---

## 📨 Message Format (RabbitMQ)

**Queue**: `RABBITMQ_BLASTN_QUEUE_NAME` (default: `blastn-jobs`)  
**Payload** (`application/json`):
```json
{
  "analysis_id": 123,
  "parameters": {
    "sequences": ["ACTG...", "TTGAC..."],
    "database": "/blast/db/environmental_bacteria_db",
    "evalue": 1e-5,
    "gap_open": null,
    "gap_extend": null,
    "penalty": null
  }
}
```

---

## 🧩 Project Structure

```text
homology_clean/
  domain/
    models.py        # Entities/DTOs
    ports.py         # Protocols (DIP)
    exceptions.py    # Domain-level exceptions
  application/
    use_cases.py     # PerformHomologyAnalysis orchestrator
  infrastructure/
    config.py        # Env configuration
    logging_setup.py # Structured logging
    storage.py       # File/GZip storage service
    blast.py         # BLAST executor adapter (subprocess)
    taxonomy.py      # Taxonomy repositories (filesystem-backed)
    db.py            # Connection factory
    repositories.py  # Analysis repository (psycopg2)
  presentation/
    handler.py       # RabbitMQ-friendly entrypoint (blastn_callback)
consumer.py          # RabbitMQ resilient consumer
main.py              # Entry point (wires everything together)
```

---

## ❓ Troubleshooting

- **First run takes long**: seeding `/blast` downloads/builds DBs. Later runs reuse the volume.
- **Change in sequences/taxonomy not reflected**: rebuild the image (`--no-cache`) and recreate the service.
- **Reset to factory**: `docker compose down -v` (removes `blast_data` and `blastn_storage` volumes).
- **Healthcheck failing**: ensure BLAST+ is present in the image and `blastn -version` returns 0.

---

## 🤝 Contributing

Contributions welcome! Open issues and PRs.  
We follow [PEP 8](https://peps.python.org/pep-0008/) and recommend `black` + `isort`.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
