# Pentagi — Setup & Deployment

Pentagi is installed at `~/.local/bin/pentagi` (81MB Go binary).
Docker compose is at `/home/craig/arsenal/pentagi/docker-compose.yml`.

## Current State (as of 2026-07-15)

- ✅ Binary installed (elf x86-64)
- ✅ Docker-compose full stack running
- ✅ PostgreSQL running (system + pgvector container)
- ✅ Pentagi web UI at https://127.0.0.1:8443
- ✅ LLM provider: OpenRouter (OpenAI-compatible)
- ✅ All 32 DB migrations applied

## Running Containers

| Container | Status | Port | Purpose |
|-----------|--------|------|---------|
| `pentagi` | Up | 8443 | Web UI + API |
| `pgvector` | Healthy | 5433* | Vector database |
| `scraper` | Up | 9444* | Browser sandbox |
| `pgexporter` | Up | 9187 | DB metrics |

*Ports remapped due to conflicts: 5432 (system postgres), 9443 (already in use)

## Port Conflict Resolution

The compose file defaults to ports already occupied by the host system. Override in `.env`:

```bash
echo "PGVECTOR_LISTEN_PORT=5433" >> /home/craig/arsenal/pentagi/.env
echo "SCRAPER_LISTEN_PORT=9444" >> /home/craig/arsenal/pentagi/.env
```

The `DATABASE_URL` in the compose file uses the internal Docker network (`pgvector:5432`),
so the host port remap doesn't affect internal connectivity.

## LLM Provider Configuration

```bash
# Add to /home/craig/arsenal/pentagi/.env
echo "OPEN_AI_KEY=sk-or-..." >> .env                    # OpenRouter API key
echo "OPEN_AI_SERVER_URL=https://openrouter.ai/api/v1" >> .env
```

## Docker Access

The user must have docker group membership and the compose GID must match:

```bash
sudo usermod -aG docker $USER
DOCKER_GID=$(getent group docker | cut -d: -f3)
sed -i "s/DOCKER_GID=998/DOCKER_GID=$DOCKER_GID/" .env
```

Use `sg docker -c "docker compose ..."` from scripts that don't inherit the group.

## Quick Start

```bash
cd /home/craig/arsenal/pentagi
sg docker -c "docker compose up -d"
# Verify: curl -sk https://127.0.0.1:8443/ | head -5
```

## Architecture

Pentagi uses a multi-agent system:
- **Primary Agent** — orchestrator
- **Generator Agent** — decomposes tasks into subtasks
- **Refiner Agent** — reviews/updates subtask list
- **Reporter Agent** — creates final reports
- **Coder Agent** — writes code
- **Pentester Agent** — executes pentesting tools (nmap, metasploit, sqlmap, etc.)
- **Installer Agent** — manages tool installation
- **Assistant Agent** — interactive assistance with dual modes (delegation or direct tools)

Supports 44+ tools across categories with automatic memory storage, observability
(Grafana, VictoriaMetrics, Jaeger, Loki), and LLM analytics (Langfuse).

