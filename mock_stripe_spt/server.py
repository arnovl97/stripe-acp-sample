"""
Mock Stripe Shared Payment Token Server
Simulates Stripe's SPT API for European demo purposes
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import secrets
import time
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# In-memory storage for SPTs
# Format: {spt_id: {payment_method, usage_limits, created_at, metadata}}
spt_storage = {}

def generate_spt_id():
    """Generate a realistic SPT ID"""
    return f"spt_{secrets.token_hex(12)}"

@app.route('/v1/shared_payment/issued_tokens', methods=['POST'])
def create_spt():
    """
    Create a Shared Payment Token
    Called by: Chat Backend (simulating OpenAI)
    """
    try:
        data = request.form.to_dict()
        
        # Extract parameters
        payment_method = data.get('payment_method')
        currency = data.get('usage_limits[currency]', 'usd')
        max_amount = data.get('usage_limits[max_amount]')
        expires_at = data.get('usage_limits[expires_at]')
        network_id = data.get('seller_details[network_id]')
        external_id = data.get('seller_details[external_id]')
        
        if not payment_method:
            return jsonify({
                'error': {
                    'type': 'invalid_request',
                    'code': 'missing_payment_method',
                    'message': 'payment_method is required'
                }
            }), 400
        
        # Generate SPT ID
        spt_id = generate_spt_id()
        
        # Store SPT data
        spt_storage[spt_id] = {
            'id': spt_id,
            'payment_method': payment_method,
            'usage_limits': {
                'currency': currency,
                'max_amount': int(max_amount) if max_amount else None,
                'expires_at': int(expires_at) if expires_at else None
            },
            'seller_details': {
                'network_id': network_id,
                'external_id': external_id
            },
            'created_at': int(time.time()),
            'status': 'active'
        }
        
        print(f"✅ Created SPT: {spt_id}")
        print(f"   Payment Method: {payment_method}")
        print(f"   Max Amount: {max_amount} {currency}")
        
        # Return SPT ID (simulating Stripe's response)
        return jsonify({
            'id': spt_id,
            'object': 'shared_payment.issued_token',
            'created': int(time.time()),
            'livemode': False
        }), 201
        
    except Exception as e:
        print(f"❌ Error creating SPT: {str(e)}")
        return jsonify({
            'error': {
                'type': 'processing_error',
                'code': 'internal_error',
                'message': str(e)
            }
        }), 500

@app.route('/v1/shared_payment/granted_tokens/<spt_id>', methods=['GET'])
def get_spt(spt_id):
    """
    Retrieve a Shared Payment Token
    Called by: Seller Backend
    """
    try:
        if spt_id not in spt_storage:
            return jsonify({
                'error': {
                    'type': 'invalid_request',
                    'code': 'spt_not_found',
                    'message': f'Shared payment token {spt_id} not found'
                }
            }), 404
        
        spt_data = spt_storage[spt_id]
        
        # Check if expired
        if spt_data['usage_limits']['expires_at']:
            if int(time.time()) > spt_data['usage_limits']['expires_at']:
                return jsonify({
                    'error': {
                        'type': 'invalid_request',
                        'code': 'spt_expired',
                        'message': 'Shared payment token has expired'
                    }
                }), 400
        
        print(f"✅ Retrieved SPT: {spt_id}")
        print(f"   Payment Method: {spt_data['payment_method']}")
        
        # Return SPT details
        return jsonify({
            'id': spt_id,
            'object': 'shared_payment.granted_token',
            'payment_method': spt_data['payment_method'],
            'usage_limits': spt_data['usage_limits'],
            'seller_details': spt_data['seller_details'],
            'created': spt_data['created_at'],
            'status': spt_data['status'],
            'livemode': False
        }), 200
        
    except Exception as e:
        print(f"❌ Error retrieving SPT: {str(e)}")
        return jsonify({
            'error': {
                'type': 'processing_error',
                'code': 'internal_error',
                'message': str(e)
            }
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'mock-stripe-spt',
        'active_tokens': len(spt_storage)
    }), 200

if __name__ == '__main__':
    import os
    port = int(os.getenv('MOCK_STRIPE_SPT_PORT', 8001))
    
    print("\n🎭 Mock Stripe SPT Server Starting...")
    print(f"📍 Port: {port}")
    print(f"🔗 Base URL: http://localhost:{port}")
    print("\nAvailable endpoints:")
    print("  POST   /v1/shared_payment/issued_tokens    - Create SPT")
    print("  GET    /v1/shared_payment/granted_tokens/<id> - Retrieve SPT")
    print("  GET    /health                             - Health check")
    print("\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)
