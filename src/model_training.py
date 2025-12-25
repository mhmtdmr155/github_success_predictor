"""
Model Training Script
Trains and compares multiple ML models for YouTube video success prediction
"""
import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import MODEL_DIR, BEST_MODEL_NAME, SCALER_NAME, FEATURE_NAMES_NAME, MODEL_METADATA_NAME


class ModelTrainer:
    """Trains and evaluates ML models for video success prediction"""
    
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.best_model = None
        self.best_model_name = None
        self.feature_names = None
        
    def load_data(self, filepath):
        """Load processed data"""
        df = pd.read_csv(filepath)
        print(f"Loaded data: {df.shape}")
        return df
    
    def prepare_data(self, df, target_col='target_first_week_views'):
        """Prepare features and target"""
        # Exclude non-feature columns and future information
        exclude_cols = [
            'video_id', 'title', 'description', 'channel_id', 'channel_name',
            'published_at', 'category_id', 'tags', 'default_language',
            'default_audio_language', 'publish_day', 'time_of_day',
            'duration_category', 'channel_size', target_col,
            # Exclude engagement metrics that we won't have for new videos
            'view_count', 'like_count', 'comment_count',
            'likes_per_1k_views', 'comments_per_1k_views'
        ]
        
        # Get numeric features only
        feature_cols = [col for col in df.columns 
                       if col not in exclude_cols 
                       and df[col].dtype in [np.int64, np.float64, np.bool_]]
        
        X = df[feature_cols].fillna(0)
        y = df[target_col]
        
        # Remove rows with NaN in target
        mask = ~y.isna()
        X = X[mask]
        y = y[mask]
        
        self.feature_names = list(X.columns)
        
        return X, y
    
    def train_test_split_data(self, X, y, test_size=0.2, random_state=42):
        """Split data into train and test sets"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def train_linear_regression(self, X_train, y_train):
        """Train Linear Regression model"""
        print("\nTraining Linear Regression...")
        model = LinearRegression()
        model.fit(X_train, y_train)
        return model
    
    def train_random_forest(self, X_train, y_train):
        """Train Random Forest model"""
        print("Training Random Forest...")
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        return model
    
    def train_xgboost(self, X_train, y_train):
        """Train XGBoost model"""
        print("Training XGBoost...")
        model = xgb.XGBRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=8,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        return model
    
    def train_gradient_boosting(self, X_train, y_train):
        """Train Gradient Boosting model"""
        print("Training Gradient Boosting...")
        model = GradientBoostingRegressor(
            n_estimators=150,
            learning_rate=0.05,
            max_depth=8,
            subsample=0.8,
            random_state=42
        )
        model.fit(X_train, y_train)
        return model
    
    def evaluate_model(self, model, X_test, y_test, model_name):
        """Evaluate model performance"""
        y_pred = model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        # MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((y_test - y_pred) / (y_test + 1))) * 100
        
        metrics = {
            'MAE': mae,
            'RMSE': rmse,
            'R²': r2,
            'MAPE': mape
        }
        
        print(f"\n{model_name} Performance:")
        print(f"  MAE:  {mae:,.0f}")
        print(f"  RMSE: {rmse:,.0f}")
        print(f"  R²:   {r2:.4f}")
        print(f"  MAPE: {mape:.2f}%")
        
        return metrics, y_pred
    
    def cross_validate(self, model, X_train, y_train, cv=5):
        """Perform cross-validation"""
        scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='r2')
        return scores.mean(), scores.std()
    
    def train_all_models(self, X_train, X_test, y_train, y_test):
        """Train and evaluate all models"""
        print("\n" + "=" * 60)
        print("MODEL TRAINING")
        print("=" * 60)
        
        results = {}
        
        # Train Linear Regression
        lr_model = self.train_linear_regression(X_train, y_train)
        lr_metrics, _ = self.evaluate_model(lr_model, X_test, y_test, "Linear Regression")
        results['Linear Regression'] = {'model': lr_model, 'metrics': lr_metrics}
        
        # Train Random Forest
        rf_model = self.train_random_forest(X_train, y_train)
        rf_metrics, _ = self.evaluate_model(rf_model, X_test, y_test, "Random Forest")
        results['Random Forest'] = {'model': rf_model, 'metrics': rf_metrics}
        
        # Train XGBoost
        xgb_model = self.train_xgboost(X_train, y_train)
        xgb_metrics, _ = self.evaluate_model(xgb_model, X_test, y_test, "XGBoost")
        results['XGBoost'] = {'model': xgb_model, 'metrics': xgb_metrics}
        
        # Train Gradient Boosting
        gb_model = self.train_gradient_boosting(X_train, y_train)
        gb_metrics, _ = self.evaluate_model(gb_model, X_test, y_test, "Gradient Boosting")
        results['Gradient Boosting'] = {'model': gb_model, 'metrics': gb_metrics}
        
        # Find best model (based on R² score)
        best_model_name = max(results.keys(), key=lambda k: results[k]['metrics']['R²'])
        self.best_model = results[best_model_name]['model']
        self.best_model_name = best_model_name
        
        print("\n" + "=" * 60)
        print("MODEL COMPARISON")
        print("=" * 60)
        print(f"{'Model':<25} {'R²':<10} {'MAE':<15} {'RMSE':<15}")
        print("-" * 60)
        for name, result in results.items():
            metrics = result['metrics']
            print(f"{name:<25} {metrics['R²']:<10.4f} {metrics['MAE']:<15,.0f} {metrics['RMSE']:<15,.0f}")
        
        print(f"\n[Best Model] {best_model_name} (R² = {results[best_model_name]['metrics']['R²']:.4f})")
        
        return results
    
    def get_feature_importance(self, model, feature_names, top_n=10):
        """Get feature importance from tree-based models"""
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1][:top_n]
            
            print(f"\nTop {top_n} Most Important Features:")
            print("-" * 60)
            for i, idx in enumerate(indices, 1):
                feat_name = feature_names[idx]
            if len(feat_name) > 40:
                feat_name = feat_name[:37] + "..."
            print(f"{i:2d}. {feat_name:<40} {importances[idx]:.4f}")
            
            return dict(zip([feature_names[i] for i in indices], [importances[i] for i in indices]))
        return None
    
    def save_model(self):
        """Save best model and related files"""
        if self.best_model is None:
            print("No model to save. Train models first.")
            return
        
        os.makedirs(MODEL_DIR, exist_ok=True)
        
        # Save model
        model_path = os.path.join(MODEL_DIR, BEST_MODEL_NAME)
        joblib.dump(self.best_model, model_path)
        print(f"\nModel saved to: {model_path}")
        
        # Save scaler
        scaler_path = os.path.join(MODEL_DIR, SCALER_NAME)
        joblib.dump(self.scaler, scaler_path)
        print(f"Scaler saved to: {scaler_path}")
        
        # Save feature names
        feature_path = os.path.join(MODEL_DIR, FEATURE_NAMES_NAME)
        joblib.dump(self.feature_names, feature_path)
        print(f"Feature names saved to: {feature_path}")
        
        # Save metadata
        metadata = {
            'model_name': self.best_model_name,
            'training_date': datetime.now().isoformat(),
            'feature_count': len(self.feature_names),
            'feature_names': self.feature_names
        }
        metadata_path = os.path.join(MODEL_DIR, MODEL_METADATA_NAME)
        joblib.dump(metadata, metadata_path)
        print(f"Metadata saved to: {metadata_path}")


def main():
    """Main execution function"""
    trainer = ModelTrainer()
    
    input_path = 'processed_data/youtube_videos_processed.csv'
    
    if not os.path.exists(input_path):
        print(f"Error: Processed data not found: {input_path}")
        print("Please run data_preprocessing.py first.")
        return
    
    # Load data
    df = trainer.load_data(input_path)
    
    # Prepare data
    X, y = trainer.prepare_data(df)
    print(f"\nFeatures: {X.shape[1]}, Samples: {X.shape[0]}")
    
    # Split data
    X_train, X_test, y_train, y_test = trainer.train_test_split_data(X, y)
    print(f"Train set: {X_train.shape[0]}, Test set: {X_test.shape[0]}")
    
    # Train all models
    results = trainer.train_all_models(X_train, X_test, y_train, y_test)
    
    # Feature importance
    if trainer.best_model and hasattr(trainer.best_model, 'feature_importances_'):
        trainer.get_feature_importance(trainer.best_model, trainer.feature_names)
    
    # Save best model
    trainer.save_model()
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()


