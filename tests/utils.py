import requests

def signup(email, password, name, signup_key):
    response = requests.post("http://localhost:6666/user/signup", json={
        "email": email,
        "password": password,
        "name": name,
        "signup_key": signup_key
    })
    return response

signup("a@a.com", "qweqwe", "a", "qwe")