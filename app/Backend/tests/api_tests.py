import pytest
import requests

def test_health_check():
    response = requests.get("http://flask-app:5050/api/portfolio/health")
    assert response.status_code == 200
