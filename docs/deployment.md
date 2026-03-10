# Deployment Guide (Docker, AWS, DigitalOcean)

## 1. Prerequisites
- Docker + Docker Compose
- A VM (AWS EC2 or DigitalOcean Droplet)
- Open ports:
  - `22` SSH
  - `80` frontend
  - `8000` backend API (optional public)
  - `5432` only if DB access is needed externally (otherwise keep private)

## 2. Run with Docker Compose
From repository root:

```bash
docker compose up -d --build
```

Services started:
- `frontend` (React served via Nginx) on `:3000`
- `backend` (FastAPI) on `:8000`
- `postgres`
- `redis`
- `celery-worker`

To check logs:

```bash
docker compose logs -f backend
docker compose logs -f celery-worker
```

## 3. AWS EC2 Deployment Steps
1. Launch Ubuntu EC2 instance.
2. SSH into instance and install Docker + Compose.
3. Clone repository:
   ```bash
   git clone <repo-url>
   cd Agent
   ```
4. Start stack:
   ```bash
   docker compose up -d --build
   ```
5. Configure Security Group:
   - Allow `3000` (frontend), `8000` (backend) or place behind reverse proxy on `80/443`.
6. (Recommended) Add Nginx + certbot for HTTPS and route domain to `frontend`/`backend`.

## 4. DigitalOcean Droplet Deployment Steps
1. Create Ubuntu droplet.
2. SSH into droplet and install Docker + Compose.
3. Clone repo and start:
   ```bash
   git clone <repo-url>
   cd Agent
   docker compose up -d --build
   ```
4. Configure Cloud Firewall:
   - Open `22`, `80`, `443` (recommended), optionally `3000`/`8000`.
5. Attach domain DNS A record to droplet IP.
6. Add reverse proxy + TLS for production.

## 5. Production Recommendations
- Move secrets to managed secret store / environment files.
- Use managed PostgreSQL (AWS RDS / DO Managed DB).
- Use managed Redis (ElastiCache / DO Managed Redis).
- Run `celery beat` separately if you need Celery-based periodic tasks.
- Use CI/CD pipeline for image build and rolling deploy.
