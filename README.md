# Vector Research Scout

Local-first vector database and research gap/connection finder for scientific papers. Built on Mac with Docker and deployed to Jetson Nano.

## Overview
This project ingests papers and notes (PDF + text), stores embeddings in a vector DB, and surfaces:
- semantic search with filters
- cross-topic connections (bridging papers)
- research gaps (under-explored intersections)
- a web UI you can access remotely with auth

## North Star
- Ingest papers/notes (PDF + text; BibTeX later).
- Semantic search with filters (author/year/tags).
- Surface connections between topics.
- Surface gaps in the literature with explainable signals.
- Provide a clean, online-accessible UI.

## Constraints
- Jetson Nano = ARM64 and limited RAM, so models must be small and batch-friendly.
- Gap discovery is a bundle of heuristics plus optional LLM summarization.

## Architecture
Core services:
- Qdrant: vector database (ARM64 friendly)
- API: FastAPI backend (search, ingest, analysis endpoints)
- Worker: ingestion + offline analysis jobs (chunking, embeddings, clustering)
- UI: Next.js web frontend (recommended); Streamlit is the quick prototype option

## Repository Layout
```
vector-research-scout/
  docker-compose.yml
  services/
    api/
    worker/
    ui/
  data/
    inbox/
    processed/
    qdrant_storage/   # local dev persistence
  .env
  config.yaml
  README.md
```

## Configuration
- `.env`: secrets, ports, and service URLs (keep real values local).
- `config.yaml`: chunk sizes, model name, batch sizes, and analysis settings.

## Ingestion Pipeline (Truth Layer)
Deliverable behavior for the worker:
1. Watch `data/inbox/` (or a manual ingest trigger).
2. Extract text from PDFs.
3. Split into chunks (with overlap).
4. Generate embeddings.
5. Upsert into Qdrant with metadata.

Minimal metadata schema (start small, expand later):
- doc_id (stable hash)
- title (best effort)
- authors (optional)
- year (optional)
- source_path
- chunk_id, chunk_index
- page (for PDFs)
- text (store chunk text for fast UI preview)
- tags (user-defined)

Dedup and versioning:
- Detect re-ingestion by hash and update doc version as needed.
- Maintain a docs table (SQLite or Postgres) for doc-level metadata.

Search endpoint baseline:
- POST /search
- query -> embedding -> Qdrant search
- returns top-k chunks + doc metadata
- supports filters (year, tags, author)

## Connections and Gaps (Insight Layer)
These run as offline analyses and store artifacts back into Qdrant plus a small relational store.

Document embedding + topic map:
- doc-level embedding per paper
- store in a docs_vectors collection
- clustering (HDBSCAN or KMeans)
- 2D projection (UMAP) for visualization

Connection discovery (bridges between clusters):
- score docs as bridges when neighbors span multiple clusters
- score cluster-to-cluster links by cross edges

Gap discovery (under-explored intersections):
- sparse cross-cluster edges with high centroid similarity
- concept co-occurrence gaps (keyphrases that should co-occur but do not)
- outlier docs (novel or niche)
- time-based gaps (old-heavy or new-heavy topics)

Optional LLM summaries:
- used as a summarizer, not an oracle
- produce gap briefs with citations to underlying docs

## UI (Online Accessible)
MVP pages:
- Search (query + results with previews)
- Document view (metadata + chunks + similar docs)
- Library map (UMAP scatter with clusters)
- Connections (bridging docs + cluster links)
- Gaps (ranked gaps with explanations)

UI notes:
- Next.js recommended for a more polished UI
- Plotly or ECharts for interactive UMAP
- Auth: API key + login page, or NextAuth with credentials

## Deployment
- Docker-first, multi-arch from day one (linux/amd64 + linux/arm64)
- Reverse proxy for HTTPS and routing (/api -> FastAPI, / -> UI)
- Run the full stack on Jetson with resource-tuned models and batch sizes
- Remote access via Tailscale or secure port-forwarding with TLS

## Milestones
- A: Local search works end-to-end
- B: UI search + document view looks good
- C: Library map + clustering works
- D: Connections + gaps dashboards work (heuristics)
- E: Deployed on Jetson and reachable online
- F: LLM-assisted gap briefs + improved ranking

## Definition of Done
- Drop a PDF into `data/inbox/`
- Search from a clean web UI
- See a topic map
- Get ranked, explainable gaps
- Access remotely with auth
- Run on Jetson without overheating

## Status
Scaffold only: folders and README. No code has been written yet.
