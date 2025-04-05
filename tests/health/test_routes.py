def test_health_happy_path(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}
