import pytest
import requests

def test_health_check():
    """Test the health check endpoint of the Flask app."""
    response = requests.get("http://flask-app:5050/api/portfolio/health")
    assert response.status_code == 200
