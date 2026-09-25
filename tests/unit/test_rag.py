import pytest
from src.rag.retriever import RunbookRetriever

@pytest.fixture
def retriever():
    return RunbookRetriever()

def test_rag_index_loaded(retriever):
    assert len(retriever.chunks) > 0
    assert retriever.tfidf_matrix is not None

def test_rag_query_db_pool_exhaustion(retriever):
    results = retriever.query("Database connection pool exhausted timeout acquiring connection 503 error", top_k=2)
    assert len(results) > 0
    top_match = results[0]
    assert "database_connection_pool_exhausted.md" in top_match["runbook"]
    assert top_match["relevance_score"] > 0.1

def test_rag_query_oom_killed(retriever):
    results = retriever.query("Pod received OOMKilled exit code 137 high memory saturation", top_k=2)
    assert len(results) > 0
    top_match = results[0]
    assert "oom_killed_memory_leak.md" in top_match["runbook"]
    assert top_match["relevance_score"] > 0.1

def test_rag_query_crashloop(retriever):
    results = retriever.query("CrashLoopBackOff readiness probe failed 500 error", top_k=2)
    assert len(results) > 0
    top_match = results[0]
    assert "crash_loop_backoff.md" in top_match["runbook"]
    assert top_match["relevance_score"] > 0.1

def test_rag_query_irrelevant_returns_empty_or_low(retriever):
    results = retriever.query("making pancakes with syrup and butter", top_k=2)
    assert len(results) == 0
