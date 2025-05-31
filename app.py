import os
import string
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///urls.db').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class ShortLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    clicks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

# Initialize database
with app.app_context():
    db.create_all()

# Health check endpoint
@app.route('/')
def home():
    return "URL Shortener Backend is Running!"

# Generate short code
def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# URL Shortening Endpoint
@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    try:
        data = request.get_json()
        original_url = data.get('url')
        
        if not original_url:
            return jsonify({"error": "URL is required"}), 400
        
        # Generate short code
        short_code = generate_short_code()
        
        # Set expiration (14 days by default)
        expires_at = datetime.utcnow() + timedelta(days=14)
        
        # Create new short link
        new_link = ShortLink(
            original_url=original_url,
            short_code=short_code,
            expires_at=expires_at
        )
        
        db.session.add(new_link)
        db.session.commit()
        
        # Build short URL using Railway's domain
        railway_url = os.getenv('RAILWAY_STATIC_URL', request.host_url)
        short_url = f"{railway_url.rstrip('/')}/{short_code}"
        
        return jsonify({
            "shortUrl": short_url,
            "expires": expires_at.isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Redirect Endpoint
@app.route('/<short_code>')
def redirect_to_url(short_code):
    link = ShortLink.query.filter_by(short_code=short_code).first()
    
    if not link:
        return jsonify({"error": "Short URL not found"}), 404
    
    # Check if expired
    if datetime.utcnow() > link.expires_at:
        return jsonify({"error": "This link has expired"}), 410
    
    # Increment click count
    link.clicks += 1
    db.session.commit()
    
    return redirect(link.original_url)

# Tracking Endpoint
@app.route('/api/track/<short_code>', methods=['GET'])
def track_click(short_code):
    link = ShortLink.query.filter_by(short_code=short_code).first()
    
    if not link:
        return jsonify({"error": "Short URL not found"}), 404
    
    # Increment click count
    link.clicks += 1
    db.session.commit()
    
    return jsonify({
        "status": "success",
        "clicks": link.clicks
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
