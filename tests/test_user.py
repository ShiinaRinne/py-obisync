from fastapi.testclient import TestClient
from obsync.config import config
from obsync.main import app


client = TestClient(app)

token = ""

def test_signup_success():
    response = client.post("/user/signup", json={
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User",
        "signup_key": "qwe"
    })
    assert response.status_code == 200
    assert response.json() == {"email": "test@example.com", "name": "Test User"}
    

def test_signup_invalid_key():
    response = client.post("/user/signup", json={
        "email": "test2@example.com",
        "password": "password123",
        "name": "Test User",
        "signup_key": "wrong_key"
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid signup key"}


def test_signin_success():
    response = client.post("/user/signin", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    global token
    token = response.json()["token"]


# user not found
def test_signin_invalid_users():
    response = client.post("/user/signin", json={
        "email": "test_signin_invalid_users@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid username or password"}


def test_signin_invalid_password():
    response = client.post("/user/signin", json={
    "email":"test@example.com",
    "password" : "invalid_password"
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid username or password"}
    
    
def test_user_info_success():
    response = client.post("/user/info", json={
        "token": token
    })
    assert response.status_code == 200
    data = response.json()
    assert "email" in data and "name" in data


def _test_user_info_unauthorized():
    response = client.post("/user/info", json={
        "token": token
    })
    assert response.status_code == 401
    assert response.json() == {"detail": "Not logged in"}


def test_signout():
    response = client.post("/user/signout")
    assert response.status_code == 200
    assert response.json() == {}
    
    
def test_delete_user():
    response = client.post("/user/delete", json={
        "token": token
    })
    assert response.status_code == 200