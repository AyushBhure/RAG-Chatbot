from io import BytesIO


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_upload_and_ask(client):
    files = {
        "files": (
            "sample.txt",
            BytesIO(b"LangChain helps build RAG systems quickly."),
            "text/plain",
        )
    }
    upload = client.post("/upload", files=files)
    assert upload.status_code == 200
    payload = {"query": "What does LangChain help with?"}
    ask = client.post("/ask", json=payload)
    assert ask.status_code == 200
    data = ask.json()
    assert "answer" in data
    assert len(data["sources"]) >= 0

