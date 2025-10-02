import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import logging
from flask_cors import CORS  # New import

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # New line: Enable CORS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hyros API configuration
HYROS_API_KEY = os.getenv('HYROS_API_KEY')
HYROS_POSTBACK_URL = 'https://app.hyros.com/api/v1/sale'  # Standard Hyros S2S endpoint

def post_to_hyros(event_data):
    """Send a tracking event to Hyros."""
    headers = {'X-Hyros-API-Key': HYROS_API_KEY, 'Content-Type': 'application/json'}
    payload = {
        'email': event_data.get('email', 'test@example.com'),
        'revenue': event_data.get('revenue', 0),
        'currency': 'USD',
        'event_type': event_data.get('type', 'test'),
        'ad_platform': event_data.get('source', 'manual'),
        'timestamp': event_data.get('timestamp', '2025-10-01T21:00:00Z')
    }
    try:
        response = requests.post(HYROS_POSTBACK_URL, json=payload, headers=headers)
        response.raise_for_status()
        logger.info(f"Hyros postback success: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Hyros error: {e}")
        return False

@app.route('/test-hyros', methods=['POST'])
def test_hyros():
    """Test endpoint to send a sample event to Hyros."""
    event_data = {
        'email': 'testuser@example.com',
        'revenue': 100.00,
        'type': 'sale',
        'source': 'manual_test'
    }
    if post_to_hyros(event_data):
        return jsonify({'status': 'success', 'message': 'Test event sent to Hyros'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send to Hyros'}), 500

@app.route('/track-purchase', methods=['POST'])
def track_purchase():
    """Endpoint to track a purchase from the website."""
    data = request.json
    email = data.get('email', 'unknown@example.com')
    revenue = data.get('revenue', 0)
    source = data.get('source', 'website_test')

    event_data = {
        'email': email,
        'revenue': revenue,
        'type': 'sale',
        'source': source
    }
    if post_to_hyros(event_data):
        return jsonify({'status': 'success', 'message': f'Purchase tracked for {email}'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Failed to track purchase'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)