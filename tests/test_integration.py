from fastapi.testclient import TestClient

def test_author_crud_flow(integration_client):
    response = integration_client.post("/add-author", json={"name": "Bob"})
    assert response.status_code == 200
    assert response.json()["success"] == True

    response = integration_client.get("/authors")
    data = response.json()["message"]
    assert len(data) == 1
    assert data[0]["author"] == "Bob"

    response = integration_client.post("/add-author", json={"name": "Tom"})
    assert response.status_code == 200
    assert response.json()["success"] == True

    response = integration_client.get("/authors")
    data = response.json()["message"]
    assert len(data) == 2
    assert data[1]["author"] == "Tom"

    response = integration_client.post("/delete", json={"name": "Bob"})
    assert response.status_code == 200
    assert response.json()["success"] == True

    response = integration_client.get("/authors")
    data = response.json()["message"]
    assert len(data) == 1
    assert data[0]["author"] == "Tom"

    response = integration_client.post("/clear")
    assert response.status_code == 200
    assert response.json()["success"] == True

    response = integration_client.get("/authors")
    data = response.json()["message"]
    assert len(data) == 0

def test_draw_flow(integration_client):
    authors = ["Bob", "Tom", "Kliff"]
    [integration_client.post("/add-author", json={"name": author}) for author in authors]

    response = integration_client.post("/draw")
    assert response.status_code == 200
    assert response.json()["winner"] in authors
    assert response.json()["success"] == True
    assert response.json()["message"] == "Winner drawn"

''' 3. Flow czyszczenia — dodaj autorów → POST /clear → sprawdź pustą listę → POST /draw powinien zwrócić błąd
   #4. Pełny cykl — dodaj autorów → wylosuj → usuń zwyciężcę → dodaj nowego → wylosuj ponownie → wyczyść wszystko → draw powinien zwrócić błąd'''
