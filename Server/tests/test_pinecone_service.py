import pytest
from Server.core.services.pinecone_service import pinecone_service, embed_texts, upsert_location_embeddings, query_location_embedding, delete_location_embeddings

SAMPLE_TEXT = "Madrid is the capital of Spain."
SAMPLE_TEXTS = ["Madrid is the capital of Spain.", "Barcelona is a city in Spain."]

@pytest.mark.parametrize("text", [SAMPLE_TEXT])
def test_embed_text(text):
    vec = pinecone_service.embed_text(text)
    assert isinstance(vec, list)
    assert len(vec) > 0


def test_embed_texts():
    vecs = pinecone_service.embed_texts(SAMPLE_TEXTS)
    assert isinstance(vecs, list)
    assert len(vecs) == len(SAMPLE_TEXTS)
    assert all(isinstance(v, list) for v in vecs)


def test_upsert_and_query():
    vecs = pinecone_service.embed_texts(SAMPLE_TEXTS)
    upserted = pinecone_service.upsert_vectors([
        {"id": f"test_{i}", "values": vec, "metadata": {"text": txt}}
        for i, (vec, txt) in enumerate(zip(vecs, SAMPLE_TEXTS))
    ])
    assert upserted is not None
    # Query for first text
    results = pinecone_service.query(vecs[0], top_k=2)
    assert isinstance(results, list)
    assert len(results) > 0


def test_delete():
    vecs = pinecone_service.embed_texts(SAMPLE_TEXTS)
    ids = [f"del_{i}" for i in range(len(vecs))]
    pinecone_service.upsert_vectors([
        {"id": id_, "values": vec, "metadata": {"text": txt}}
        for id_, vec, txt in zip(ids, vecs, SAMPLE_TEXTS)
    ])
    deleted = pinecone_service.delete(ids)
    assert deleted is not None


def test_get_index_stats():
    stats = pinecone_service.get_index_stats()
    assert isinstance(stats, dict)
    assert "vectors_stored" in stats or "namespaces" in stats


def test_health_check():
    status = pinecone_service.get_status()
    assert isinstance(status, dict)
    assert "pinecone_available" in status
    assert "faiss_available" in status
    assert "embedding_model_loaded" in status


def test_helpers():
    embeddings = embed_texts(SAMPLE_TEXTS)
    assert isinstance(embeddings, list)
    upserted = upsert_location_embeddings([
        {"id": f"helper_{i}", "embedding": emb, "metadata": {"text": txt}}
        for i, (txt, emb) in enumerate(zip(SAMPLE_TEXTS, embeddings))
    ])
    assert upserted is not None
    q_emb = embed_texts([SAMPLE_TEXTS[0]])[0]
    results = query_location_embedding(q_emb, top_k=2)
    assert isinstance(results, list)
    deleted = delete_location_embeddings([f"helper_{i}" for i in range(len(SAMPLE_TEXTS))])
    assert deleted is not None
