"""
Main Flask application for WhatsApp Bot
Handles webhook verification and message routing
"""

from flask import Flask, request, jsonify
import logging
from config import Config
from handlers import handle_message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Webhook verification endpoint for Meta's WhatsApp API
    """
    verify_token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if verify_token == app.config['VERIFY_TOKEN']:
        logger.info("Webhook verified successfully")
        return challenge
    
    logger.warning("Webhook verification failed - invalid token")
    return "Verification token mismatch", 403

@app.route('/webhook', methods=['POST'])
def receive_message():
    """
    Receive messages from WhatsApp and process them
    """
    try:
        data = request.get_json()
        logger.info(f"Received webhook data: {data}")
        
        # Check if this is a message event
        if data.get('object') == 'whatsapp_business_account':
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    if change.get('field') == 'messages':
                        messages = change.get('value', {}).get('messages', [])
                        contacts = change.get('value', {}).get('contacts', [])
                        
                        for message in messages:
                            phone_number_id = change.get('value', {}).get('metadata', {}).get('phone_number_id')
                            sender_phone = message.get('from')
                            sender_name = contacts[0].get('profile', {}).get('name') if contacts else 'User'
                            message_text = message.get('text', {}).get('body', '')
                            
                            logger.info(f"Message from {sender_name} ({sender_phone}): {message_text}")
                            
                            # Handle the message
                            response = handle_message(message_text, sender_name)
                            
                            # Send response back
                            send_message(phone_number_id, sender_phone, response)
        
        return jsonify({'status': 'received'}), 200
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500


def send_message(phone_number_id, recipient_phone, message_text):
    """
    Send message back to WhatsApp user via Meta API
    """
    import requests
    
    url = f"https://graph.instagram.com/v18.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {app.config['ACCESS_TOKEN']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone,
        "type": "text",
        "text": {
            "body": message_text
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            logger.info(f"Message sent to {recipient_phone}")
        else:
            logger.error(f"Failed to send message: {response.text}")
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint
    """
    return jsonify({'status': 'healthy'}), 200

@app.route('/', methods=['GET'])
def home():
    """
    Home endpoint
    """
    return jsonify({
        'message': 'WhatsApp Bot is running',
        'endpoints': {
            'webhook': '/webhook',
            'health': '/health'
        }
    }), 200

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], port=app.config['PORT'])