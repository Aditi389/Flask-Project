from utils.ml_model import AdOptimizerModel
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import timedelta
import os
from dotenv import load_dotenv
import json
import random
from datetime import datetime

load_dotenv()

app = Flask(__name__, template_folder='frontend', static_folder="frontend")

# Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'MS87-MCFj9Yo70UNTzksw6uw096sHG5LvpQUHm__OAFy1dHaes19RmwO75IQzGrQXClZtxyOEGc3kYmaxXiv3Q')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

CORS(app)
jwt = JWTManager(app)

# Initialize ML model
ml_model = AdOptimizerModel()

# Mock database class (replace with your actual database)
class Database:
    def __init__(self):
        self.users = {}
        self.metrics = {}
        self.predictions = {}
        self.optimizations = {}
        self.admin_users = {}  # Separate admin users
        
    def init_db(self):
        print("✅ Database initialized")
        # Create default admin user
        self.admin_users['admin@adoptimizer.ai'] = {
            'id': 'admin_1',
            'username': 'admin',
            'email': 'admin@adoptimizer.ai',
            'password_hash': 'admin123',  # In production, use proper hashing
            'role': 'admin',
            'created_at': datetime.now().isoformat()
        }
        
    def get_user_by_email(self, email):
        return self.users.get(email)
    
    def get_admin_by_email(self, email):
        return self.admin_users.get(email)
    
    def verify_password(self, password, password_hash):
        # Simple mock verification - in real app, use proper hashing
        return password == password_hash
    
    def create_user(self, username, email, password, role='user'):
        if email in self.users or email in self.admin_users:
            return None, "User already exists"
        
        user_id = len(self.users) + len(self.admin_users) + 1
        user_data = {
            'id': user_id,
            'username': username,
            'email': email,
            'password_hash': password,  # In real app, hash this
            'role': role,
            'created_at': datetime.now().isoformat()
        }
        
        if role == 'admin':
            self.admin_users[email] = user_data
        else:
            self.users[email] = user_data
            
        return user_id, None
    
    def get_all_users(self):
        """Get all users for admin panel"""
        all_users = []
        for email, user in self.users.items():
            user_copy = user.copy()
            user_copy['campaigns_count'] = random.randint(0, 10)
            all_users.append(user_copy)
        return all_users
    
    def delete_user(self, user_id):
        """Delete a user by ID"""
        for email, user in list(self.users.items()):
            if user['id'] == user_id:
                del self.users[email]
                return True
        return False
    
    def get_user_metrics(self, user_id):
        # Return mock metrics
        return {
            'ctr': round(random.uniform(0.02, 0.06), 4),
            'cpc': round(random.uniform(12, 25), 2),
            'conversions': random.randint(800, 1500),
            'roas': round(random.uniform(2.5, 5.5), 2),
            'spend': random.randint(8000, 15000),
            'engagement': round(random.uniform(0.03, 0.08), 4),
            'impressions': random.randint(50000, 200000)
        }
    
    def save_prediction_result(self, user_id, input_data, prediction_result):
        if user_id not in self.predictions:
            self.predictions[user_id] = []
        
        self.predictions[user_id].append({
            'input_data': input_data,
            'prediction_result': prediction_result,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_user_recommendations(self, user_id):
        # Return mock recommendations
        return [
            {
                'campaign': 'Google Ads Q4',
                'predicted_ctr': round(random.uniform(0.03, 0.07), 4),
                'best_channel': 'Google Ads',
                'recommended_budget_pct': random.randint(10, 25)
            },
            {
                'campaign': 'Facebook Prospecting',
                'predicted_ctr': round(random.uniform(0.04, 0.08), 4),
                'best_channel': 'Facebook Ads',
                'recommended_budget_pct': random.randint(5, 20)
            }
        ]
    
    def save_optimization_settings(self, user_id, settings, results):
        if user_id not in self.optimizations:
            self.optimizations[user_id] = []
        
        self.optimizations[user_id].append({
            'settings': settings,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })

# Initialize database
db = Database()

def initialize_app():
    db.init_db()
    # Ensure ML model is trained
    if not ml_model.is_trained:
        print("🔄 Training ML model on startup...")
        ml_model.train_model()
    print("✅ Application initialization completed")
    print("🔐 Default admin credentials: admin@adoptimizer.ai / admin123")

with app.app_context():
    initialize_app()

# ==================== PAGE ROUTES ====================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index.html')
def home_alt():
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/ml_insights')
def ml_insights():
    return render_template('ml_insights.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/optimization')
def optimization():
    return render_template('optimization.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

# ==================== ADMIN PAGE ROUTES ====================
@app.route('/admin/login')
def admin_login_page():
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin.html')

# ==================== API ROUTES ====================
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'AdOptimizer AI backend is running'})

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'status': 'error', 'message': 'Email and password are required'}), 400

        print(f"Login attempt for email: {email}")

        user = db.get_user_by_email(email)

        if user and db.verify_password(password, user['password_hash']):
            access_token = create_access_token(identity=str(user['id']))
            print(f"✅ Login successful for user: {user['username']}")
            
            return jsonify({
                'status': 'success',
                'access_token': access_token,
                'user_id': user['id'],
                'username': user['username'],
                'message': 'Login successful'
            })
        else:
            print(f"❌ Login failed for email: {email}")
            return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Server error during login'}), 500

@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not all([username, email, password]):
            return jsonify({'status': 'error', 'message': 'All fields are required'}), 400

        if len(password) < 6:
            return jsonify({'status': 'error', 'message': 'Password must be at least 6 characters'}), 400

        print(f"Registration attempt for: {username} ({email})")

        user_id, error = db.create_user(username, email, password)
        
        if error:
            return jsonify({'status': 'error', 'message': error}), 400

        # Create access token for immediate login
        access_token = create_access_token(identity=str(user_id))
        
        print(f"✅ User registered successfully: {username}")
        return jsonify({
            'status': 'success', 
            'message': 'Account created successfully!',
            'user_id': user_id,
            'username': username,
            'access_token': access_token
        })

    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Server error during registration'}), 500

# ==================== ADMIN API ROUTES ====================
@app.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'status': 'error', 'message': 'Email and password are required'}), 400

        print(f"Admin login attempt for email: {email}")

        admin = db.get_admin_by_email(email)

        if admin and db.verify_password(password, admin['password_hash']):
            access_token = create_access_token(identity=str(admin['id']))
            print(f"✅ Admin login successful: {admin['username']}")
            
            return jsonify({
                'status': 'success',
                'access_token': access_token,
                'user_id': admin['id'],
                'username': admin['username'],
                'role': 'admin',
                'message': 'Admin login successful'
            })
        else:
            print(f"❌ Admin login failed for email: {email}")
            return jsonify({'status': 'error', 'message': 'Invalid admin credentials'}), 401
            
    except Exception as e:
        print(f"❌ Admin login error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Server error during admin login'}), 500

@app.route('/api/admin/users', methods=['GET', 'POST'])
@jwt_required()
def api_admin_users():
    try:
        if request.method == 'GET':
            # Get all users
            users = db.get_all_users()
            return jsonify({
                'status': 'success',
                'users': users
            })
        
        elif request.method == 'POST':
            # Create new user
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            role = data.get('role', 'user')
            
            user_id, error = db.create_user(username, email, password, role)
            
            if error:
                return jsonify({'status': 'error', 'message': error}), 400
            
            return jsonify({
                'status': 'success',
                'message': 'User created successfully',
                'user_id': user_id
            })
            
    except Exception as e:
        print(f"❌ Admin users error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def api_admin_delete_user(user_id):
    try:
        if db.delete_user(user_id):
            return jsonify({
                'status': 'success',
                'message': 'User deleted successfully'
            })
        else:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
            
    except Exception as e:
        print(f"❌ Admin delete user error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/campaigns', methods=['GET'])
@jwt_required()
def api_admin_campaigns():
    try:
        # Return mock campaign data for all users
        campaigns = []
        platforms = ['Google Ads', 'Facebook Ads', 'Instagram Ads', 'LinkedIn Ads']
        statuses = ['active', 'paused', 'stopped']
        
        users = db.get_all_users()
        for user in users[:5]:  # Limit to 5 users for demo
            for i in range(random.randint(2, 5)):
                campaigns.append({
                    'id': len(campaigns) + 1,
                    'user': user['username'],
                    'name': f"{user['username']}_campaign_{i+1}",
                    'platform': random.choice(platforms),
                    'impressions': random.randint(10000, 100000),
                    'clicks': random.randint(500, 5000),
                    'spend': random.randint(500, 5000),
                    'status': random.choice(statuses)
                })
        
        return jsonify({
            'status': 'success',
            'campaigns': campaigns
        })
        
    except Exception as e:
        print(f"❌ Admin campaigns error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def api_admin_stats():
    try:
        # Return system statistics
        stats = {
            'total_users': len(db.get_all_users()),
            'total_spend': random.randint(100000, 200000),
            'active_campaigns': random.randint(10, 30),
            'total_predictions': len(db.predictions) * random.randint(50, 100)
        }
        
        return jsonify({
            'status': 'success',
            'stats': stats
        })
        
    except Exception as e:
        print(f"❌ Admin stats error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def api_logout():
    try:
        # With JWT, logout is handled client-side by removing the token
        return jsonify({'status': 'success', 'message': 'Logged out successfully'})
    except Exception as e:
        print(f"❌ Logout error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Logout failed'}), 500

@app.route('/api/get_metrics', methods=['GET'])
@jwt_required() 
def api_get_metrics():
    try:
        current_user_id = get_jwt_identity()
        print(f"Fetching metrics for user: {current_user_id}")
        
        metrics = db.get_user_metrics(current_user_id)
        
        if metrics:
            print(f"✅ Metrics found for user: {current_user_id}")
            return jsonify({'status': 'success', 'data': metrics})
        else:
            print(f"❌ No metrics found for user: {current_user_id}")
            return jsonify({'status': 'error', 'message': 'No metrics found'}), 404
            
    except Exception as e:
        print(f"❌ Error fetching metrics: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to fetch metrics'}), 500

@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        # For now, allow predictions without authentication for testing
        # current_user_id = get_jwt_identity()
        current_user_id = "anonymous"  # Temporary for testing
        data = request.get_json()
        
        print(f"Prediction request from user: {current_user_id}")
        print(f"Prediction data: {data}")
        
        # Validate required fields with better error messages
        required_fields = {
            'impressions': (int, float),
            'spend': (int, float), 
            'current_CTR': (int, float),
            'current_CPC': (int, float),
            'engagement_rate': (int, float)
        }
        
        missing_fields = []
        invalid_fields = []
        
        for field, field_types in required_fields.items():
            if field not in data:
                missing_fields.append(field)
            elif not isinstance(data[field], field_types):
                invalid_fields.append(field)
        
        if missing_fields:
            return jsonify({
                'status': 'error', 
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 422
            
        if invalid_fields:
            return jsonify({
                'status': 'error', 
                'message': f'Invalid data types for: {", ".join(invalid_fields)}'
            }), 422
        
        # Provide fallback prediction if ML model fails
        try:
            if not ml_model.is_trained:
                ml_model.load_model()
                
            prediction_result = ml_model.predict(data)
        except Exception as ml_error:
            print(f"ML model prediction failed, using fallback: {ml_error}")
            # Fallback prediction
            prediction_result = {
                'status': 'success',
                'predicted_CTR': min(data['current_CTR'] * 1.1, 0.1),  # 10% improvement, max 10%
                'predicted_CPC': max(data['current_CPC'] * 0.9, 5.0),  # 10% reduction, min $5
                'label': 'High' if data['current_CTR'] > 0.02 else 'Medium',
                'recommendation': 'Consider increasing budget by 15% for better performance'
            }
        
        # Save prediction to database
        db.save_prediction_result(current_user_id, data, prediction_result)
        
        return jsonify(prediction_result)
        
    except Exception as e:
        print(f"❌ Prediction error: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': f'Prediction failed: {str(e)}'
        }), 500

@app.route('/api/recommendations', methods=['GET'])
@jwt_required()
def api_recommendations():
    try:
        current_user_id = get_jwt_identity()
        print(f"Fetching recommendations for user: {current_user_id}")
        
        recommendations = db.get_user_recommendations(current_user_id)
        
        if recommendations:
            return jsonify({
                'status': 'success',
                'recommendations': recommendations
            })
        else:
            # Return sample recommendations if none found
            sample_recommendations = [
                {
                    'campaign': 'Google Ads Q4',
                    'predicted_ctr': 0.042,
                    'best_channel': 'Google Ads',
                    'recommended_budget_pct': 15
                },
                {
                    'campaign': 'Facebook Prospecting',
                    'predicted_ctr': 0.038,
                    'best_channel': 'Facebook Ads',
                    'recommended_budget_pct': -10
                }
            ]
            return jsonify({
                'status': 'success',
                'recommendations': sample_recommendations
            })
            
    except Exception as e:
        print(f"❌ Recommendations error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to get recommendations'}), 500

@app.route('/api/optimize', methods=['POST'])
@jwt_required()
def api_optimize():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        print(f"Optimization request from user: {current_user_id}")
        print(f"Optimization settings: {data}")
        
        # More flexible field handling
        budget_range = data.get('budget_range') or data.get('budgetRange') or 5000
        confidence_threshold = data.get('confidence_threshold') or data.get('confidence') or 0.75
        frequency = data.get('frequency') or 'daily'
        auto_budget = data.get('auto_budget') or data.get('autoBudget') or False
        auto_ab_test = data.get('auto_ab_test') or data.get('autoABTest') or False
        
        # Ensure confidence_threshold is a float between 0 and 1
        if isinstance(confidence_threshold, (int, float)):
            if confidence_threshold > 1:  # If it's a percentage, convert to decimal
                confidence_threshold = confidence_threshold / 100
        else:
            confidence_threshold = 0.75  # Default fallback
        
        print(f"Processed optimization settings:")
        print(f"  budget_range: {budget_range}")
        print(f"  confidence_threshold: {confidence_threshold}")
        print(f"  frequency: {frequency}")
        print(f"  auto_budget: {auto_budget}")
        print(f"  auto_ab_test: {auto_ab_test}")
        
        # Generate sample optimization results
        optimization_results = [
            {
                'campaign': 'Google Ads Q4',
                'action': 'Increase budget by 15%',
                'confidence': 0.85
            },
            {
                'campaign': 'Facebook Prospecting', 
                'action': 'Decrease budget by 20%',
                'confidence': 0.72
            },
            {
                'campaign': 'Instagram Story Ads',
                'action': 'Maintain current budget',
                'confidence': 0.63
            }
        ]
        
        # Save optimization settings
        db.save_optimization_settings(current_user_id, data, optimization_results)
        
        return jsonify({
            'status': 'success',
            'message': 'Optimization completed successfully',
            'optimization_results': optimization_results
        })
        
    except Exception as e:
        print(f"❌ Optimization error: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': f'Optimization failed: {str(e)}'
        }), 500

@app.route('/api/train-model', methods=['POST'])
@jwt_required()
def api_train_model():
    try:
        print("🔄 Training ML model...")
        
        result = ml_model.train_model()
        
        if result['status'] == 'success':
            return jsonify({
                'status': 'success',
                'message': 'ML model trained successfully',
                'metrics': result.get('metrics', {}),
                'training_time': '45 seconds'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result.get('message', 'Model training failed')
            }), 500
        
    except Exception as e:
        print(f"❌ Model training error: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Model training failed: {str(e)}'}), 500

# Debug endpoint to check received data
@app.route('/api/debug-optimize', methods=['POST'])
@jwt_required()
def debug_optimize():
    try:
        data = request.get_json()
        print("🔍 DEBUG - Received optimization data:")
        print(f"  budget_range: {data.get('budget_range')} (type: {type(data.get('budget_range'))})")
        print(f"  confidence_threshold: {data.get('confidence_threshold')} (type: {type(data.get('confidence_threshold'))})")
        print(f"  frequency: {data.get('frequency')} (type: {type(data.get('frequency'))})")
        print(f"  auto_budget: {data.get('auto_budget')} (type: {type(data.get('auto_budget'))})")
        print(f"  auto_ab_test: {data.get('auto_ab_test')} (type: {type(data.get('auto_ab_test'))})")
        
        return jsonify({
            'status': 'debug',
            'received_data': data,
            'message': 'Check server console for details'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({
        'status': 'error', 
        'message': 'Unprocessable entity - check your request data'
    }), 422
# ----------  INQUIRY REDIRECT  ----------
@app.route('/inquiry')
def inquiry_redirect():
    return redirect("https://docs.google.com/forms/d/e/1FAIpQLSe3gHwx0LHP0M3GprKTXAEh6LyO-xMGZZUgZwe1NzRmhWwHfA/viewform")
if __name__ == '__main__':
    print("🚀 Starting AdOptimizer AI Server...")
    print("📊 ML Model: Ready")
    print("💾 Database: Mock (in-memory)")
    print("🔐 Authentication: JWT")
    print("🌐 Server running on: http://127.0.0.1:5000")
    print("👤 User Login: http://127.0.0.1:5000/login")
    print("🔐 Admin Login: http://127.0.0.1:5000/admin/login")
    print("   Default Admin: admin@adoptimizer.ai / admin123")
    app.run(debug=True, host='0.0.0.0', port=5000)