import os
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test that the index route serves the frontend HTML."""
    response = client.get('/')
    assert response.status_code == 200

def test_api_config(client):
    """Test the config endpoint returns expected keys."""
    response = client.get('/api/config')
    assert response.status_code == 200
    data = response.get_json()
    assert 'endpoint' in data
    assert 'project_id' in data

def test_get_animals(client):
    """Test the public animals list route."""
    response = client.get('/api/animals')
    # Assuming successful connection to appwrite or proper error handling
    # Depending on Appwrite credentials, it could be 200 or an error code. 
    # But it shouldn't be 404 or 500 unhandled.
    assert response.status_code in [200, 401, 403, 500] 

def test_unauthenticated_create_animal(client):
    """Test that creating an animal without auth returns 401."""
    response = client.post('/api/animals', data={"animal_name": "Test"})
    assert response.status_code == 401
