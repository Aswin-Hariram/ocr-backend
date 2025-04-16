from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.rest import Client
import easyocr
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Twilio credentials from environment variables
account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')
twilio_number = os.getenv('TWILIO_NUMBER')

# Initialize Twilio client
client = Client(account_sid, auth_token)

# Initialize EasyOCR reader once (reuse across requests)
reader = easyocr.Reader(['en'])  # You can add other languages, e.g., ['en', 'hi', 'ta']


@app.route('/detect-text', methods=['POST'])
def detect_text():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        image_bytes = image_file.read()

        # Perform OCR
        results = reader.readtext(image_bytes)
        extracted_text = ' '.join([res[1] for res in results])
        print(f"Extracted text: {extracted_text}")

        if not extracted_text.strip():
            return jsonify({"message": "No text detected"}), 200
        

        return jsonify({"detected_text": extracted_text.strip()}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/send-sms', methods=['POST'])
def send_sms():
    try:
        if 'phone_number' not in request.form or 'message' not in request.form:
            return jsonify({"error": "Phone number or message not provided"}), 400

        phone_number = request.form['phone_number']
        message_body = request.form['message']

        message = client.messages.create(
            body=message_body,
            from_=twilio_number,
            to=phone_number
        )
        
        return jsonify({"message": "SMS sent successfully", "sms_sid": message.sid}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False)
