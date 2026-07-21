# Phase 5E — Local Deterministic Embeddings and Vector Retrieval

## 1. Purpose

This document records the locally verified implementation evidence for
Phase 5E.

Phase 5E adds a bounded teaching implementation of deterministic local
embeddings, an immutable synthetic vector index, and permission-aware
vector retrieval.

It does not claim production semantic-search maturity.

## 2. Current Decision

```text
PHASE 5E LOCAL IMPLEMENTATION: COMPLETE
PHASE 5E IMPLEMENTATION COMMIT: AUTHORIZED
PHASE 5E REMOTE CI: PASSED — RUN 29810229699
PHASE 5E CLOSURE: PENDING
PHASE 5F: AUTHORIZED ONLY AFTER CLOSURE-COMMIT CI
```

Phase 5E may be committed for exact-commit CI validation.

Phase 5F hybrid retrieval and reranking remain unauthorized until Phase 5E
is separately closed.

## 3. Authorized Scope Implemented

Phase 5E implements:

Shared authorization and abstention controls for retrieval methods
Deterministic local feature-hash embeddings
Explicit embedding version
Fixed embedding dimensions
Unit-normalized vectors
Cosine-similarity calculation
Immutable synthetic vector-index entries
Explicit vector-index version
Exact corpus-to-index coverage
Content-hash alignment between chunks and vector entries
Deterministic vector retrieval
Authorization filtering before vector scoring
Stable candidate tie-breaking
Policy-controlled result limits
Citation-preserving vector candidates
Explicit vector-retrieval abstention
Public bounded vector-retrieval exports
Focused embedding and vector tests
## 4. Prohibited Scope

Phase 5E does not implement or authorize:

External embedding providers
Downloaded embedding models
OpenAI embeddings
Anthropic services
Vertex AI embeddings
Bedrock embeddings
Sentence Transformers
PyTorch or TensorFlow
Enterprise evidence sources
Production data
Managed vector databases
FAISS
ChromaDB
Pinecone
Weaviate
Qdrant
Hybrid retrieval
Score fusion
Reranking
Context construction
Prompt assembly
Model-provider calls
Tool execution
Retrieval API routes
Infrastructure mutation
Cloud deployment
Production deployment
## 5. Artifact Inventory

Implementation artifacts:

src/incident_diagnostic_api/retrieval/embeddings.py
src/incident_diagnostic_api/retrieval/vector.py
src/incident_diagnostic_api/retrieval/security.py
src/incident_diagnostic_api/retrieval/keyword.py
src/incident_diagnostic_api/retrieval/__init__.py

Test artifacts:

tests/retrieval/test_embeddings.py
tests/retrieval/test_vector.py

Evidence artifacts:

docs/retrieval/PHASE_5E_VECTOR_RETRIEVAL_IMPLEMENTATION_AND_EVIDENCE.md
docs/retrieval/PHASE_5E_VECTOR_RETRIEVAL_GATE.md
docs/interview-accelerator/phases/PHASE_05_PERMISSION_AWARE_RAG.md
## 6. Shared Security Boundary

Keyword and vector retrieval now use the same internal security functions:

authorization_matches_query
authorized_active_chunks
build_abstention_result

This extraction preserves the Phase 5D authority rules while preventing
keyword and vector retrieval from developing different authorization
semantics.

The shared helpers remain internal and are not included in the public
retrieval exports.

## 7. Deterministic Embedding Model

The local embedding version is:

deterministic-feature-hash-v1

The vector dimension is:

256

The embedding function:

Normalizes text into unique lowercase alphanumeric tokens.
Hashes each token with SHA-256 and the embedding-version identifier.
Maps each token into one of 256 dimensions.
Assigns a deterministic positive or negative direction.
Accumulates token features.
Applies unit-length normalization.
Returns a zero vector when no searchable tokens exist.

The implementation is deterministic and dependency-free.

It is a teaching and test embedding. It is not a trained semantic model and
must not be described as equivalent to a production embedding service.

## 8. Cosine Similarity

Cosine similarity compares the direction of two vectors.

The implementation:

Requires both vectors to have exactly 256 dimensions
Returns zero when either vector has zero magnitude
Produces a bounded value between negative one and positive one
Is deterministic for identical inputs
Is symmetric
Gives identical nonzero vectors a score of one

Negative similarity is clamped to zero by the retrieval layer because the
existing retrieval candidate score contract accepts nonnegative confidence
scores.

## 9. Immutable Synthetic Vector Index

The vector-index version is:

synthetic-vector-index-v1

Each immutable vector entry records:

Chunk identifier
Chunk content hash
Embedding version
Fixed-dimensional vector

The vector index records:

Index version
Embedding version
Synthetic corpus
Immutable entry tuple

Index construction requires:

Exactly one entry per corpus chunk
No duplicate chunk entries
Exact corpus coverage
Matching content hashes
Matching embedding versions
Fixed vector dimensions

Corpus chunks are ordered deterministically before index construction.

## 10. Content and Version Lineage

A vector entry is valid only when:

Its chunk identifier exists in the indexed corpus
Its content hash matches the source chunk
Its embedding version matches the index embedding version
Its vector dimension matches the embedding contract
The index version is supported

This prevents a vector from being silently reused for different chunk
content or an incompatible embedding version.

## 11. Authorization Before Vector Scoring

Vector retrieval performs these steps in order:

Validate CT-03 authorization lineage and expiration.
Embed the query locally.
Apply resource, source-type, tenant, service, classification, and
lifecycle filtering.
Resolve vectors only for authorized active chunks.
Calculate cosine similarity.
Apply the query threshold.
Apply stable ranking.
Apply the smaller query or policy result limit.
Return cited candidates or an explicit abstention.

Unauthorized chunks do not reach cosine scoring.

The model, query text, embedding, and similarity score do not grant access.

## 12. Deterministic Ranking

Eligible vector candidates are ordered by:

Descending vector score
Source identifier
Document identifier
Chunk index
Chunk identifier

This produces a stable result when candidates have equal scores and makes
retrieval replayable for the same index, query, policy, and time inputs.

## 13. Citation and Abstention Behavior

Every returned vector candidate retains:

Request identifier
Trace identifier
Policy-decision identifier
Source identifier
Document identifier
Document version
Chunk identifier
Retrieval method
Score
Rank
Freshness
Content-addressed citation

Vector retrieval abstains when:

Authorization is invalid or expired
The query cannot produce an embedding
No active evidence remains after authorization filtering
No authorized evidence meets the configured similarity threshold

No qualifying vector result is treated as a controlled abstention, not an
invitation to fabricate evidence.

## 14. Public API Boundary

Phase 5E publicly exports:

EMBEDDING_DIMENSIONS
EMBEDDING_VERSION
EmbeddingVector
VECTOR_INDEX_VERSION
VectorIndexEntry
SyntheticVectorIndex
embed_text
cosine_similarity
build_vector_index
retrieve_vectors

The shared authorization helpers remain private.

The complete public retrieval export inventory contains 28 names.

## 15. Local Test Evidence

Local verification produced:

Embedding tests: 15 passed
Vector tests: 23 passed
Retrieval tests: 124 passed
Complete repository tests: 814 passed
Ruff linting: Passed
Ruff formatting: Passed
Strict mypy checking: Passed
Dependency validation: Passed
Diff whitespace validation: Passed

Embedding tests prove:

Version and dimension stability
Deterministic output
Case normalization
Token-order independence
Unique-token behavior
Zero-vector behavior
Unit normalization
Cosine identity
Partial-overlap ordering
Symmetry
Dimension rejection
Negative similarity behavior

Vector tests prove:

Deterministic index construction
Exact corpus coverage
Immutability
Missing and duplicate entry rejection
Content-hash validation
Embedding-version validation
Dimension validation
Ranked vector candidates
Citation integrity
Repeatability
Explicit abstention
Tenant, service, classification, and source-type filtering
Filter-before-score behavior
Policy and query result limits
Stable tie-breaking
Tombstone exclusion
## 16. Capability-Boundary Evidence

A source scan found no:

External AI provider SDK
Downloaded model dependency
Managed vector-database client
Network client
Tool-execution capability
Subprocess execution
Socket use
Terraform capability
Kubernetes capability

Phase 5E remains local, deterministic, synthetic, read-only, and
dependency-free.

## 17. Residual Risks

The deterministic feature-hash embedding:

Is not trained on language semantics
May produce hash collisions
Does not understand domain meaning
Does not support multilingual semantic equivalence
Does not provide production retrieval quality
Requires evaluation before any broader use

The synthetic vector index:

Is memory-only
Has no persistence
Has no incremental update process
Has no distributed partitioning
Has no enterprise data connector
Has no production access-control integration
Has no operational telemetry

These limitations are intentional and bounded.

## 18. Remote CI Evidence

Phase 5E passed exact-commit CI run
[`29810229699`](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29810229699) against implementation commit
`fa02cb90e62c5a1279b1ec7b025d54375fba72f3`.

Both required jobs passed:

- Python quality and contract tests
- Local container build and health verification

Phase 5E implementation evidence is verified.

Phase 5E closure remains pending until this evidence update is committed and
that exact closure commit passes CI. Phase 5F remains unavailable until that
closure-commit CI succeeds.

## 19. Current Exit Posture

```text
PHASE 5E LOCAL IMPLEMENTATION: COMPLETE
LOCAL QUALITY: PASSED
REMOTE CI: PASSED — RUN 29810229699
PHASE 5E CLOSURE: PENDING
PHASE 5F HYBRID RETRIEVAL AND RERANKING: AUTHORIZED ONLY AFTER CLOSURE-COMMIT CI
```
