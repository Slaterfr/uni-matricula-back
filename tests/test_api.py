def test_read_root(client):
    """
    Verifica que el endpoint raíz funcione correctamente.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_login_invalid(client):
    """
    Verifica que el login falle con credenciales inválidas.
    """
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@user.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Correo o contraseña incorrectos"

def test_admin_login(client):
    """
    Verifica que el usuario administrador inicial sembrado en el lifespan pueda autenticarse.
    """
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@universidad.com", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    assert data["email"] == "admin@universidad.com"
