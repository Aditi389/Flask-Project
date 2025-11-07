import mysql.connector
from mysql.connector import Error
import bcrypt
import os
import json
from datetime import datetime, timedelta
import random

class Config:
    """Configuration class with default values"""
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'MS87-MCFj9Yo70UNTzksw6uw096sHG5LvpQUHm__OAFy1dHaes19RmwO75IQzGrQXClZtxyOEGc3kYmaxXiv3Q')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # MySQL Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'Aditi@123')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'ad_optimizer')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))

class Database:
    def __init__(self):
        self.config = {
            'host': Config.MYSQL_HOST,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'database': Config.MYSQL_DATABASE,
            'port': Config.MYSQL_PORT
        }
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor(dictionary=True)
            print("✅ Connected to MySQL database")
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            # Try connecting without database first to create it
            self.create_database_if_not_exists()
            raise

    def create_database_if_not_exists(self):
        """Create database if it doesn't exist"""
        try:
            # Connect without specifying database
            temp_config = self.config.copy()
            temp_config.pop('database', None)
            conn = mysql.connector.connect(**temp_config)
            cursor = conn.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DATABASE}")
            print(f"✅ Database '{Config.MYSQL_DATABASE}' created or already exists")
            
            cursor.close()
            conn.close()
            
            # Reconnect with database
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor(dictionary=True)
            print("✅ Connected to MySQL database")
            
        except Error as e:
            print(f"❌ Error creating database: {e}")
            raise

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return self.cursor
        except Error as e:
            print(f"❌ Database error: {e}")
            if self.connection:
                self.connection.rollback()
            raise

    def fetch_one(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        except Error as e:
            print(f"❌ Database fetch error: {e}")
            return None

    def fetch_all(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ Database fetch error: {e}")
            return []

    def close(self):
        if self.connection and self.connection.is_connected():
            if self.cursor:
                self.cursor.close()
            self.connection.close()
            print("✅ Database connection closed")

    def init_db(self):
        """Initialize database tables and sample data"""
        try:
            # Create users table
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create campaign_metrics table
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS campaign_metrics (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    date DATE NOT NULL,
                    impressions INT NOT NULL,
                    clicks INT NOT NULL,
                    spend DECIMAL(10,2) NOT NULL,
                    conversions INT NOT NULL,
                    platform VARCHAR(50) NOT NULL,
                    campaign_name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')

            # Create recommendations table
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    campaign_name VARCHAR(255) NOT NULL,
                    recommendation_text TEXT NOT NULL,
                    confidence_score DECIMAL(5,4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')

            print("✅ Database tables created successfully")
            self.generate_sample_data()
            
        except Error as e:
            print(f"❌ Error initializing database: {e}")

    def generate_sample_data(self):
        """Generate sample users and campaign data for testing"""
        try:
            # Check if sample users already exist
            existing_users = self.fetch_all("SELECT COUNT(*) as count FROM users")
            if existing_users and existing_users[0]['count'] > 0:
                print("✅ Sample data already exists")
                return

            # Create sample users
            sample_users = [
                ('john_doe', 'john@example.com', self.hash_password('password123')),
                ('jane_smith', 'jane@example.com', self.hash_password('password123')),
                ('demo_user', 'demo@example.com', self.hash_password('demo123'))
            ]

            for username, email, password_hash in sample_users:
                self.execute_query(
                    "INSERT IGNORE INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                    (username, email, password_hash)
                )

            # Get user IDs
            users = self.fetch_all("SELECT id FROM users")
            
            # Platforms for sample data
            platforms = ['Google Ads', 'Facebook Ads', 'Instagram Ads', 'LinkedIn Ads']
            
            # Generate campaign metrics for last 90 days
            for user in users:
                user_id = user['id']
                for i in range(90):
                    date = datetime.now() - timedelta(days=90 - i)
                    
                    for platform in platforms:
                        # Generate realistic campaign data
                        impressions = random.randint(1000, 50000)
                        ctr = random.uniform(0.01, 0.08)  # 1-8% CTR
                        clicks = int(impressions * ctr)
                        cpc = random.uniform(5, 25)  # $5-25 CPC
                        spend = clicks * cpc
                        conversion_rate = random.uniform(0.02, 0.15)  # 2-15% conversion rate
                        conversions = int(clicks * conversion_rate)
                        
                        campaign_name = f"{platform.replace(' ', '_')}_Campaign_{i+1}"
                        
                        self.execute_query('''
                            INSERT INTO campaign_metrics 
                            (user_id, date, impressions, clicks, spend, conversions, platform, campaign_name)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (user_id, date, impressions, clicks, spend, conversions, platform, campaign_name))

                # Generate sample recommendations
                sample_recommendations = [
                    ("Google Ads Campaign", "Increase budget by 15% for better performance", 0.85),
                    ("Facebook Prospecting", "Test new ad creatives to improve CTR", 0.72),
                    ("Instagram Story Ads", "Reallocate budget to top-performing segments", 0.91)
                ]
                
                for campaign, recommendation, confidence in sample_recommendations:
                    self.execute_query('''
                        INSERT INTO recommendations (user_id, campaign_name, recommendation_text, confidence_score)
                        VALUES (%s, %s, %s, %s)
                    ''', (user_id, campaign, recommendation, confidence))

            print("✅ Sample data generated successfully")

        except Error as e:
            print(f"❌ Error generating sample data: {e}")

    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password, password_hash):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            print(f"❌ Password verification error: {e}")
            return False

    def create_user(self, username, email, password):
        """Create a new user in the database"""
        try:
            # Check if user already exists
            existing_user = self.get_user_by_email(email)
            if existing_user:
                return None, "User already exists with this email"
            
            password_hash = self.hash_password(password)
            self.execute_query(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash)
            )
            user_id = self.cursor.lastrowid
            return user_id, None
        except Error as e:
            print(f"❌ Error creating user: {e}")
            return None, f"Database error: {str(e)}"

    def get_user_by_email(self, email):
        """Get user by email address"""
        return self.fetch_one("SELECT * FROM users WHERE email = %s", (email,))

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return self.fetch_one("SELECT * FROM users WHERE id = %s", (user_id,))

    def get_user_metrics(self, user_id, days=30):
        """Get aggregated metrics for a user"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        query = '''
            SELECT 
                SUM(impressions) as total_impressions,
                SUM(clicks) as total_clicks,
                SUM(spend) as total_spend,
                SUM(conversions) as total_conversions,
                CASE 
                    WHEN SUM(impressions) > 0 THEN SUM(clicks) / SUM(impressions)
                    ELSE 0 
                END as ctr,
                CASE 
                    WHEN SUM(clicks) > 0 THEN SUM(spend) / SUM(clicks)
                    ELSE 0 
                END as cpc,
                CASE 
                    WHEN SUM(spend) > 0 THEN SUM(conversions) / SUM(spend)
                    ELSE 0 
                END as conversion_rate,
                CASE 
                    WHEN SUM(spend) > 0 THEN (SUM(conversions) * 100) / SUM(spend)  -- Assuming $100 value per conversion
                    ELSE 0 
                END as roas,
                CASE 
                    WHEN SUM(clicks) > 0 THEN SUM(conversions) / SUM(clicks)
                    ELSE 0 
                END as engagement_rate
            FROM campaign_metrics 
            WHERE user_id = %s AND date BETWEEN %s AND %s
        '''
        
        result = self.fetch_one(query, (user_id, start_date, end_date))
        
        # Format the result for the frontend
        if result:
            return {
                'ctr': float(result['ctr'] or 0),
                'cpc': float(result['cpc'] or 0),
                'conversions': int(result['total_conversions'] or 0),
                'roas': float(result['roas'] or 0),
                'spend': float(result['total_spend'] or 0),
                'engagement': float(result['engagement_rate'] or 0),
                'impressions': int(result['total_impressions'] or 0),
                'clicks': int(result['total_clicks'] or 0)
            }
        return None

    def get_campaign_metrics(self, user_id, platform=None, days=30):
        """Get detailed campaign metrics for a user"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        query = '''
            SELECT 
                campaign_name,
                platform,
                SUM(impressions) as impressions,
                SUM(clicks) as clicks,
                SUM(spend) as spend,
                SUM(conversions) as conversions,
                CASE 
                    WHEN SUM(impressions) > 0 THEN SUM(clicks) / SUM(impressions)
                    ELSE 0 
                END as ctr,
                CASE 
                    WHEN SUM(clicks) > 0 THEN SUM(spend) / SUM(clicks)
                    ELSE 0 
                END as cpc,
                CASE 
                    WHEN SUM(spend) > 0 THEN (SUM(conversions) * 100) / SUM(spend)
                    ELSE 0 
                END as roas
            FROM campaign_metrics 
            WHERE user_id = %s AND date BETWEEN %s AND %s
        '''
        
        params = [user_id, start_date, end_date]
        
        if platform and platform != 'all':
            query += ' AND platform = %s'
            params.append(platform)
            
        query += ' GROUP BY campaign_name, platform ORDER BY spend DESC'
        
        return self.fetch_all(query, params)

    def get_user_recommendations(self, user_id, limit=10):
        """Get recommendations for a user"""
        query = '''
            SELECT campaign_name, recommendation_text, confidence_score, created_at
            FROM recommendations 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        '''
        return self.fetch_all(query, (user_id, limit))

    def save_recommendation(self, user_id, campaign_name, recommendation_text, confidence_score):
        """Save a new recommendation for a user"""
        try:
            self.execute_query('''
                INSERT INTO recommendations (user_id, campaign_name, recommendation_text, confidence_score)
                VALUES (%s, %s, %s, %s)
            ''', (user_id, campaign_name, recommendation_text, confidence_score))
            return True
        except Error as e:
            print(f"❌ Error saving recommendation: {e}")
            return False

    def save_prediction_result(self, user_id, input_data, prediction_result):
        """Save ML prediction results for a user"""
        try:
            # Create a new table for prediction history if it doesn't exist
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS prediction_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    input_data JSON NOT NULL,
                    prediction_result JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            self.execute_query('''
                INSERT INTO prediction_history (user_id, input_data, prediction_result)
                VALUES (%s, %s, %s)
            ''', (user_id, json.dumps(input_data), json.dumps(prediction_result)))
            
            return True
        except Error as e:
            print(f"❌ Error saving prediction: {e}")
            return False

    def get_prediction_history(self, user_id, limit=5):
        """Get prediction history for a user"""
        try:
            # Check if table exists
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS prediction_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    input_data JSON NOT NULL,
                    prediction_result JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            query = '''
                SELECT input_data, prediction_result, created_at
                FROM prediction_history 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            '''
            return self.fetch_all(query, (user_id, limit))
        except Error as e:
            print(f"❌ Error getting prediction history: {e}")
            return []

    def save_optimization_settings(self, user_id, settings, results):
        """Save optimization settings and results"""
        try:
            # Create a new table for optimization history if it doesn't exist
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS optimization_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    settings JSON NOT NULL,
                    results JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            self.execute_query('''
                INSERT INTO optimization_history (user_id, settings, results)
                VALUES (%s, %s, %s)
            ''', (user_id, json.dumps(settings), json.dumps(results)))
            
            return True
        except Error as e:
            print(f"❌ Error saving optimization settings: {e}")
            return False

    def get_optimization_history(self, user_id, limit=5):
        """Get optimization history for a user"""
        try:
            # Check if table exists
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS optimization_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    settings JSON NOT NULL,
                    results JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            query = '''
                SELECT settings, results, created_at
                FROM optimization_history 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            '''
            return self.fetch_all(query, (user_id, limit))
        except Error as e:
            print(f"❌ Error getting optimization history: {e}")
            return []

    def get_recent_campaigns(self, user_id, limit=5):
        """Get recent campaigns for a user"""
        query = '''
            SELECT DISTINCT campaign_name, platform
            FROM campaign_metrics 
            WHERE user_id = %s 
            ORDER BY date DESC 
            LIMIT %s
        '''
        return self.fetch_all(query, (user_id, limit))

    def add_campaign_metrics(self, user_id, metrics_data):
        """Add new campaign metrics for a user"""
        try:
            self.execute_query('''
                INSERT INTO campaign_metrics 
                (user_id, date, impressions, clicks, spend, conversions, platform, campaign_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                user_id,
                metrics_data.get('date', datetime.now().date()),
                metrics_data.get('impressions', 0),
                metrics_data.get('clicks', 0),
                metrics_data.get('spend', 0),
                metrics_data.get('conversions', 0),
                metrics_data.get('platform', 'Unknown'),
                metrics_data.get('campaign_name', 'Unnamed Campaign')
            ))
            return True
        except Error as e:
            print(f"❌ Error adding campaign metrics: {e}")
            return False

# Singleton instance for the application
db_instance = Database()

def get_db():
    """Get database instance"""
    return db_instance