# TCF AI Complaint & Query Management System

Backend is now implemented with FastAPI + SQLAlchemy + PostgreSQL.

## Run backend locally

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API base

- Base URL: `http://localhost:8000/api/v1`
- Health: `GET /health`

## Implemented endpoints

- `POST /signup`
- `POST /login`
- `POST /complaints`
- `GET /complaints`
- `GET /complaints/{id}`
- `PUT /complaints/{id}/status`
- `POST /queries`
- `GET /queries`
- `GET /departments`
- `POST /chatbot/ask`

## Escalation policy

- 8 hours unresolved -> escalated to Senior Officer (level 1)
- 24 hours unresolved -> escalated to Department Head (level 2)
- Runs via APScheduler background worker.

## NLP Complaint Classification Module

Implemented with HuggingFace Sentence Transformers in `backend/app/services/nlp/complaint_classifier.py`.

Pipeline:
1. preprocess complaint text
2. remove stopwords
3. compute embeddings
4. compare with department keyword embeddings
5. return predicted department

Training + inference script:

```bash
cd backend
python scripts/train_and_infer_classifier.py --text "My tuition voucher payment is delayed"
```

## Query Similarity System (FAISS)

- New query is embedded using sentence-transformers.
- Similarity is computed against stored answered queries via FAISS cosine similarity (inner product on normalized embeddings).
- If similarity `> 0.85`, stored answer is returned automatically.
- Otherwise, query is forwarded to the predicted department and marked `Pending`.


## AI Chatbot (RAG)

Chatbot pipeline:
1. Student sends a question.
2. Retriever searches FAISS knowledge base built from solved complaints, common queries, and policy documents.
3. Retrieved context is passed to an LLM (`google/flan-t5-small` by default).
4. Final grounded answer is generated and returned with context sources.


## Frontend (React + Tailwind)

```bash
cd frontend
npm install
npm run dev
```

Set API URL if needed:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Pages implemented:
- Login page
- Student dashboard
- Submit complaint page
- Complaint tracking page
- Query page
- Chatbot interface
- Admin dashboard
- Staff dashboard


## Docker Deployment

Run full stack (frontend, backend, postgres, redis, celery worker):

```bash
docker compose up -d --build
```

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

Detailed cloud deployment steps: `docs/deployment.md`.


## Docker Build Troubleshooting

If backend build fails at `pip install -r requirements.txt`:

```bash
DOCKER_PLATFORM=linux/amd64 docker compose build backend --no-cache --progress=plain
DOCKER_PLATFORM=linux/amd64 docker compose up -d --build
```

Then inspect logs:

```bash
docker compose logs -f backend
```
