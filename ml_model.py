import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
from datetime import datetime
import random

class AdOptimizerModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = 'models/model.pkl'
        self.scaler_path = 'models/scaler.pkl'
        self.is_trained = False
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
    def generate_training_data(self, n_samples=1000):
        """Generate realistic training data for ad campaign optimization"""
        np.random.seed(42)
        
        data = {
            'impressions': np.random.randint(1000, 100000, n_samples),
            'spend': np.random.uniform(100, 10000, n_samples),
            'current_CTR': np.random.uniform(0.01, 0.1, n_samples),
            'current_CPC': np.random.uniform(2, 30, n_samples),
            'engagement_rate': np.random.uniform(0.02, 0.2, n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Generate realistic target variables with some business logic
        # Predicted CTR: influenced by current CTR, engagement, and spend efficiency
        df['predicted_CTR'] = (
            df['current_CTR'] * 0.6 + 
            df['engagement_rate'] * 0.3 +
            (df['spend'] / df['impressions']) * 10000 * 0.1 +
            np.random.normal(0, 0.005, n_samples)
        ).clip(0.005, 0.15)
        
        # Predicted CPC: influenced by current CPC, impressions, and engagement
        df['predicted_CPC'] = (
            df['current_CPC'] * 0.7 +
            (100000 / df['impressions']) * 0.2 +
            (0.1 / df['engagement_rate']) * 0.1 +
            np.random.normal(0, 0.5, n_samples)
        ).clip(1, 35)
        
        return df

    def train_model(self):
        """Train the ML model on generated data"""
        try:
            print("🔄 Generating training data...")
            df = self.generate_training_data(500)
            
            # Features for prediction
            features = ['impressions', 'spend', 'current_CTR', 'current_CPC', 'engagement_rate']
            X = df[features]
            
            # Targets
            y_ctr = df['predicted_CTR']
            y_cpc = df['predicted_CPC']
            
            # Split data
            X_train, X_test, y_ctr_train, y_ctr_test = train_test_split(
                X, y_ctr, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model for CTR prediction
            self.model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            self.model.fit(X_train_scaled, y_ctr_train)
            
            # Calculate performance metrics
            y_ctr_pred = self.model.predict(X_test_scaled)
            mae_ctr = mean_absolute_error(y_ctr_test, y_ctr_pred)
            r2_ctr = r2_score(y_ctr_test, y_ctr_pred)
            
            print(f"✅ Model trained successfully")
            print(f"   CTR Prediction - MAE: {mae_ctr:.4f}, R²: {r2_ctr:.4f}")
            
            # Save model and scaler
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            self.is_trained = True
            
            return {
                'status': 'success',
                'message': 'Model trained successfully',
                'metrics': {
                    'ctr_mae': mae_ctr,
                    'ctr_r2': r2_ctr
                }
            }
            
        except Exception as e:
            print(f"❌ Error training model: {e}")
            return {'status': 'error', 'message': str(e)}

    def load_model(self):
        """Load pre-trained model and scaler"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.is_trained = True
                print("✅ Model loaded successfully")
                return True
            else:
                print("⚠️ No pre-trained model found. Training new model...")
                return self.train_model() is not None
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False

    def predict(self, input_data):
        """Make predictions for given input data"""
        if not self.is_trained:
            if not self.load_model():
                return {'status': 'error', 'message': 'Model not trained'}
        
        try:
            # Prepare features
            features = ['impressions', 'spend', 'current_CTR', 'current_CPC', 'engagement_rate']
            X = np.array([[input_data[feature] for feature in features]])
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Make predictions
            predicted_ctr = self.model.predict(X_scaled)[0]
            predicted_cpc = self._predict_cpc(input_data, predicted_ctr)
            
            # Generate label and recommendation
            label = self._generate_label(predicted_ctr, input_data['current_CTR'])
            recommendation = self._generate_recommendation(predicted_ctr, predicted_cpc, input_data)
            
            return {
                'status': 'success',
                'predicted_CTR': round(predicted_ctr, 4),
                'predicted_CPC': round(predicted_cpc, 2),
                'label': label,
                'recommendation': recommendation
            }
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return {'status': 'error', 'message': str(e)}

    def _predict_cpc(self, input_data, predicted_ctr):
        """Simple CPC prediction based on CTR and spend efficiency"""
        # Business logic: Better CTR often leads to better CPC due to platform favor
        base_cpc = input_data['current_CPC']
        ctr_improvement = predicted_ctr - input_data['current_CTR']
        
        # If CTR improves, CPC might decrease due to better quality score
        if ctr_improvement > 0:
            cpc_adjustment = -ctr_improvement * 100  # $1 decrease per 1% CTR improvement
        else:
            cpc_adjustment = ctr_improvement * 50   # Smaller increase for worse CTR
            
        predicted_cpc = max(1, base_cpc + cpc_adjustment)
        return predicted_cpc

    def _generate_label(self, predicted_ctr, current_ctr):
        """Generate performance label based on predicted vs current CTR"""
        improvement = (predicted_ctr - current_ctr) / current_ctr
        
        if improvement > 0.1:  # >10% improvement
            return "High"
        elif improvement > 0:  # 0-10% improvement
            return "Medium"
        else:  # No improvement or worse
            return "Low"

    def _generate_recommendation(self, predicted_ctr, predicted_cpc, input_data):
        """Generate business recommendation based on predictions"""
        ctr_improvement = predicted_ctr - input_data['current_CTR']
        cpc_change = predicted_cpc - input_data['current_CPC']
        
        recommendations = []
        
        if ctr_improvement > 0.02:
            recommendations.append("Increase budget by 15-20% for maximum ROI")
        elif ctr_improvement > 0:
            recommendations.append("Consider a 5-10% budget increase")
        else:
            recommendations.append("Pause campaign and test new creatives")
            
        if cpc_change < -2:
            recommendations.append("Great CPC efficiency - scale this approach")
        elif cpc_change > 3:
            recommendations.append("High CPC detected - optimize targeting")
            
        if input_data['engagement_rate'] < 0.05:
            recommendations.append("Low engagement - improve ad relevance")
            
        if len(recommendations) == 0:
            recommendations.append("Maintain current strategy and monitor performance")
            
        return " | ".join(recommendations)

    def optimize_campaigns(self, user_metrics, budget_range, confidence_threshold):
        """Generate optimization actions for user campaigns"""
        try:
            # Mock optimization logic - in real scenario, this would use actual campaign data
            optimization_actions = []
            
            # Sample campaigns with mock data
            sample_campaigns = [
                {"name": "Google Ads Q4", "current_spend": 2500, "current_ctr": 0.032},
                {"name": "Facebook Prospecting", "current_spend": 1800, "current_ctr": 0.045},
                {"name": "Instagram Story Ads", "current_spend": 1200, "current_ctr": 0.028},
            ]
            
            for campaign in sample_campaigns:
                # Mock prediction for each campaign
                mock_input = {
                    'impressions': random.randint(10000, 50000),
                    'spend': campaign['current_spend'],
                    'current_CTR': campaign['current_ctr'],
                    'current_CPC': random.uniform(8, 22),
                    'engagement_rate': random.uniform(0.03, 0.12)
                }
                
                prediction = self.predict(mock_input)
                
                if prediction['status'] == 'success':
                    confidence = random.uniform(0.6, 0.95)
                    
                    if confidence >= confidence_threshold / 100:  # Convert to decimal
                        if prediction['label'] == 'High':
                            action = f"Increase budget by 20% to ${campaign['current_spend'] * 1.2:.0f}"
                        elif prediction['label'] == 'Medium':
                            action = f"Maintain current budget of ${campaign['current_spend']:.0f}"
                        else:
                            action = f"Decrease budget by 15% to ${campaign['current_spend'] * 0.85:.0f}"
                            
                        optimization_actions.append({
                            'campaign': campaign['name'],
                            'action': action,
                            'confidence': round(confidence, 3),
                            'predicted_ctr': prediction['predicted_CTR'],
                            'predicted_cpc': prediction['predicted_CPC']
                        })
            
            return optimization_actions
            
        except Exception as e:
            print(f"❌ Optimization error: {e}")
            return []