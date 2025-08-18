#!/usr/bin/env bash
set -euo pipefail

SEED_DIR="/blast_seed"
TARGET_DIR="/blast"

# Se o volume estiver vazio (ou faltar um artefato chave), semeia a partir do seed
if [ ! -d "$TARGET_DIR" ] || [ -z "$(ls -A "$TARGET_DIR" 2>/dev/null)" ] || [ ! -f "$TARGET_DIR/combined_sequences.fna" ]; then
  echo "[entrypoint] Seeding $TARGET_DIR from $SEED_DIR..."
  mkdir -p "$TARGET_DIR"
  # -a preserva atributos; o ponto é essencial para copiar o conteúdo
  cp -a "$SEED_DIR/." "$TARGET_DIR/"
else
  echo "[entrypoint] $TARGET_DIR already initialized. Skipping seed."
fi

# Executa o processo principal
exec "$@"