# API Documentation

This directory contains the backend API service for the Vector Research Scout. It uses FastAPI to expose endpoints for searching, ingesting, and analyzing research papers.

## Search API Contract

### `POST /search`

Performs a semantic search over the indexed documents (papers/notes) using vector similarity. Supports various metadata filters.

#### Request Body
The request accepts a JSON object with the following fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `query` | string | Yes | The natural language search query. |
| `top_k` | integer | No | Number of results to return. Defaults to 10. |
| `filters` | object | No | Metadata filters to narrow down results. |

**Filters Object:**

| Field | Type | Description |
|---|---|---|
| `authors` | list[string] | Filter for papers by specific authors. |
| `year_min` | integer | Minimum publication year (inclusive). |
| `year_max` | integer | Maximum publication year (inclusive). |
| `tags` | list[string] | List of tags to include. |

#### Example Request

```json
{
  "query": "transformer architecture in computer vision",
  "top_k": 5,
  "filters": {
    "authors": ["Dosovitskiy", "Vaswani"],
    "year_min": 2020,
    "year_max": 2024,
    "tags": ["deep learning", "vit"]
  }
}
```

#### Response Body
Returns a JSON object containing a list of ranked search results.

| Field | Type | Description |
|---|---|---|
| `results` | list[Result] | List of matching documents sorted by relevance score. |

**Result Object:**

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier of the document. |
| `score` | float | Similarity score (e.g., cosine similarity). |
| `metadata` | object | Document metadata (title, authors, year, abstract, etc.). |

#### Example Response

```json
{
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "score": 0.89,
      "metadata": {
        "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
        "authors": ["Dosovitskiy, Alexey", "et al."],
        "year": 2020,
        "abstract": "While the Transformer architecture has become...",
        "tags": ["vision transformer", "deep learning"]
      }
    }
  ]
}
```
---

### `GET /documents/{document_id}`

Retrieves a specific document by its unique identifier.

#### Response Body
Returns a JSON object containing the document metadata.

| Field | Type | Description |
|---|---|---|
| `result` | Result | The matching document. |

**Result Object:**

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier of the document. |
| `metadata` | object | Document metadata (title, authors, year, abstract, etc.). |

#### Example Response

```json
{
  "result": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "metadata": {
      "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
      "authors": ["Dosovitskiy, Alexey", "et al."],
      "year": 2020,
      "abstract": "While the Transformer architecture has become...",
      "tags": ["vision transformer", "deep learning"]
    }
  }
}
```
---

### `GET /library/map`

Retrieves the 2D projection of the document library for visualization, including cluster assignments.

#### Response Body

Returns an object containing the map points and cluster definitions.

| Field | Type | Description |
|---|---|---|
| `points` | list[Point] | List of documents with 2D coordinates. |
| `clusters` | list[Cluster] | List of identified topic clusters. |

**Point Object:**

| Field | Type | Description |
|---|---|---|
| `id` | string | Document ID. |
| `x` | float | X-coordinate (e.g., from UMAP). |
| `y` | float | Y-coordinate (e.g., from UMAP). |
| `cluster_id` | integer | ID of the assigned cluster. |
| `title` | string | Document title for tooltip. |

**Cluster Object:**

| Field | Type | Description |
|---|---|---|
| `id` | integer | Cluster ID. |
| `label` | string | Generated label for the topic (e.g., "Transformers"). |
| `color` | string | Hex color code for visualization. |

#### Example Response

```json
{
  "points": [
    { "id": "1", "x": 0.5, "y": -1.2, "cluster_id": 0, "title": "Paper A" },
    { "id": "2", "x": 0.6, "y": -1.1, "cluster_id": 0, "title": "Paper B" }
  ],
  "clusters": [
    { "id": 0, "label": "Machine Learning", "color": "#FF5733" }
  ]
}
```

---

### `GET /connections`

Identifies and retrieves "bridge" papers that connect different topic clusters.

#### Response Body

| Field | Type | Description |
|---|---|---|
| `connections` | list[Connection] | List of bridging connections between topics. |

**Connection Object:**

| Field | Type | Description |
|---|---|---|
| `source_cluster` | string | Name/ID of the first topic. |
| `target_cluster` | string | Name/ID of the second topic. |
| `papers` | list[PaperSummary] | Papers that bridge these two topics. |
| `score` | float | Strength or relevance of the connection. |

#### Example Response

```json
{
  "connections": [
    {
      "source_cluster": "Computer Vision",
      "target_cluster": "NLP",
      "score": 0.85,
      "papers": [
        { "id": "123", "title": "ViT: An Image is Worth 16x16 Words" }
      ]
    }
  ]
}
```

---

### `GET /gaps`

Identifies under-explored intersections or "structural holes" in the research landscape.

#### Response Body

| Field | Type | Description |
|---|---|---|
| `gaps` | list[Gap] | List of identified research gaps. |

**Gap Object:**

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique ID for the gap analysis. |
| `description` | string | Human-readable specific description of the gap. |
| `score` | float | Magnitude/Importance of the gap. |
| `surrounding_clusters` | list[string] | Topics that surround this gap. |

#### Example Response

```json
{
  "gaps": [
    {
      "id": "gap-001",
      "description": "Lack of research combining Reinforcement Learning with Historical Climate Data.",
      "score": 0.92,
      "surrounding_clusters": ["Reinforcement Learning", "Climate Science"]
    }
  ]
}
```
