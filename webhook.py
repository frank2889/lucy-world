#!/usr/bin/env python3
"""
GitHub Webhook Handler for Lucy World Search
Automatically deploys when you push to GitHub
"""

from flask import Flask, request, jsonify
import subprocess
import hashlib
import hmac
import os

app = Flask(__name__)

# Configuration
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'your-webhook-secret')
DEPLOY_SCRIPT = '/var/www/lucy-world-search/auto-deploy.sh'

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle GitHub webhook"""
    
    # Verify GitHub signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        return jsonify({'error': 'No signature provided'}), 400
    
    # Calculate expected signature
    expected_signature = 'sha256=' + hmac.new(
        WEBHOOK_SECRET.encode(),
        request.data,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Parse payload
    payload = request.json
    
    # Only deploy on push to main branch
    if (payload.get('ref') == 'refs/heads/main' and 
        payload.get('repository', {}).get('name') == 'lucy-world-search'):
        
        try:
            # Run deployment script
            result = subprocess.run(
                [DEPLOY_SCRIPT],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return jsonify({
                    'status': 'success',
                    'message': 'Deployment completed successfully',
                    'output': result.stdout
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Deployment failed',
                    'error': result.stderr
                }), 500
                
        except subprocess.TimeoutExpired:
            return jsonify({
                'status': 'error',
                'message': 'Deployment timed out'
            }), 500
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Deployment error: {str(e)}'
            }), 500
    
    return jsonify({'status': 'ignored', 'message': 'Not a main branch push'})

@app.route('/health')
def health():
    """Health check for webhook service"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=False)