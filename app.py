from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import bcrypt
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'elite_food_packaging'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['user']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        company_name = data.get('company_name')
        phone = data.get('phone')
        address = data.get('address')
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Email already exists!'})
        
        # Insert new user
        cursor.execute("""
            INSERT INTO users (name, email, password, company_name, phone, address) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, email, hashed_password.decode('utf-8'), company_name, phone, address))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'User created successfully!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # Create token
            token = jwt.encode({
                'user': {
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email']
                },
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'])
            
            return jsonify({
                'success': True,
                'message': 'Login successful!',
                'token': token,
                'user': {
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email'],
                    'company_name': user['company_name'],
                    'phone': user['phone'],
                    'address': user['address']
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password!'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/orders', methods=['POST'])
@token_required
def create_order(current_user):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO orders (
                user_id, company_name, email, phone, address,
                bio_small, bio_medium, bio_large,
                paper_small, paper_medium, paper_large,
                container_small, container_medium, container_large,
                recycled_small, recycled_medium, recycled_large,
                payment_mode, total_price, order_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            current_user['id'],
            data.get('company_name'),
            data.get('email'),
            data.get('phone'),
            data.get('address'),
            data.get('bio_small', 0),
            data.get('bio_medium', 0),
            data.get('bio_large', 0),
            data.get('paper_small', 0),
            data.get('paper_medium', 0),
            data.get('paper_large', 0),
            data.get('container_small', 0),
            data.get('container_medium', 0),
            data.get('container_large', 0),
            data.get('recycled_small', 0),
            data.get('recycled_medium', 0),
            data.get('recycled_large', 0),
            data.get('payment_mode'),
            data.get('total_price')
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Order placed successfully!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/reviews', methods=['POST'])
@token_required
def create_review(current_user):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO reviews (user_id, user_name, comment, rating, review_date)
            VALUES (%s, %s, %s, %s, NOW())
        """, (current_user['id'], current_user['name'], data.get('comment'), data.get('rating')))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Review submitted successfully!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT user_name, comment, rating, review_date 
            FROM reviews 
            ORDER BY review_date DESC 
            LIMIT 10
        """)
        
        reviews = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(reviews)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)