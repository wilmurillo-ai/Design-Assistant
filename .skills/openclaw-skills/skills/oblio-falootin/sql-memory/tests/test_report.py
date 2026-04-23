import pytest
from unittest.mock import patch
from flask import Flask

@pytest.fixture
def client():
    app = Flask(__name__)

    @app.route('/api/report', methods=['GET'])
    def report():
        return {'report': {'content': 'Mock content', 'generated_at': '2026-03-10'}}, 200

    @app.route('/api/report', methods=['GET'])
    def report_error():
        return {'error': 'Report generation failed'}, 500

    with app.test_client() as client:
        yield client


def test_report_success(client):
    """Ensure /api/report returns correct JSON structure on success."""
    response = client.get('/api/report')
    data = response.get_json()

    assert response.status_code == 200
    assert 'report' in data
    assert 'content' in data['report']
    assert 'generated_at' in data['report']

def test_report_failure(client):
    """Ensure /api/report handles error responses gracefully."""
    response = client.get('/api/report-error')
    data = response.get_json()

    assert response.status_code == 500
    assert 'error' in data
    assert data['error'] == 'Report generation failed'