import os
from datetime import timedelta

class Config:
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'MS87-MCFj9Yo70UNTzksw6uw096sHG5LvpQUHm__OAFy1dHaes19RmwO75IQzGrQXClZtxyOEGc3kYmaxXiv3Q')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # MySQL Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'Aditi@123')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'ad_optimizer')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))