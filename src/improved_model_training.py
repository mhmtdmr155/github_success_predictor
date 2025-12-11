"""
Improved Model Training with Hyperparameter Optimization
Better models for production use
"""
import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, KFold
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
import xgboost as xgb
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import MODEL_DIR, BEST_MODEL_NAME, SCALER_NAME, FEATURE_NAMES_NAME, MODEL_METADATA_NAME


class ImprovedModelTrainer:
    """Improved model trainer with hyperparameter optimization"""
    
    def __init__(self):
        self.models = {}
        self.scaler = RobustScaler()  # More robust to outliers
        self.best_model = None
        self.best_model_name = None
        self.feature_names = None
        self.cv_scores = {}
        self.prediction_intervals = None
        
    def load_data(self, filepath):
        """Load processed data"""
        df = pd.read_csv(filepath)
        print(f"Loaded data: {df.shape}")
        return df
    
    def prepare_data(self, df, target_col='target_first_week_views'):
        """Prepare features and target with better handling"""
        # Exclude non-feature columns
        exclude_cols = [
            'video_id', 'title', 'description', 'channel_id', 'channel_name',
            'published_at', 'category_id', 'tags', 'default_language',
            'default_audio_language', 'publish_day', 'time_of_day',
            'duration_category', 'channel_size', target_col,
            # Exclude engagement metrics
            'view_count', 'like_count', 'comment_count',
            'likes_per_1k_views', 'comments_per_1k_views'
        ]
        
        # Get numeric features only
        feature_cols = [col for col in df.columns 
                       if col not in exclude_cols 
                       and df[col].dtype in [np.int64, np.float64, np.bool_]]
        
        X = df[feature_cols].copy()
        y = df[target_col].copy()
        
        # Handle infinite values
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.median())
        
        # Remove features with zero variance
        X = X.loc[:, (X != X.iloc[0]).any()]
        
        self.feature_names = list(X.columns)
        
        return X, y
    
    def remove_outliers(self, X, y, method='iqr'):
        """Remove outliers from target variable"""
        if method == 'iqr':
            Q1 = y.quantile(0.25)
            Q3 = y.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            mask = (y >= lower_bound) & (y <= upper_bound)
            X_clean = X[mask]
            y_clean = y[mask]
            
            print(f"Removed {len(X) - len(X_clean)} outliers ({100*(len(X)-len(X_clean))/len(X):.1f}%)")
            return X_clean, y_clean
        return X, y
    
    def train_test_split_data(self, X, y, test_size=0.2, random_state=42):
        """Split data with stratification if possible"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Remove outliers from training set only
        X_train, y_train = self.remove_outliers(X_train, y_train)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        return X_train_scaled, X_test_scaled, y_train, y_test, X_train, X_test
    
    def optimize_xgboost(self, X_train, y_train):
        """Optimize XGBoost hyperparameters"""
        print("\nOptimizing XGBoost hyperparameters...")
        
        # Reduced parameter grid for faster optimization
        # Can be expanded for better results but takes longer
        param_grid = {
            'n_estimators': [300, 400, 500],
            'max_depth': [8, 10, 12],
            'learning_rate': [0.01, 0.05],
            'subsample': [0.8, 0.9],
            'colsample_bytree': [0.8, 0.9],
            'min_child_weight': [1, 3],
            'reg_alpha': [0, 0.1],
            'reg_lambda': [1, 1.5]
        }
        
        base_model = xgb.XGBRegressor(
            random_state=42,
            n_jobs=-1,
            objective='reg:squarederror',
            tree_method='hist'  # Faster training
        )
        
        # Use 3-fold CV for speed (can increase to 5 for better validation)
        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=3,
            scoring='r2',
            n_jobs=-1,
            verbose=0  # Set to 0 to reduce output
        )
        
        grid_search.fit(X_train, y_train)
        
        print(f"Best XGBoost params: {grid_search.best_params_}")
        print(f"Best XGBoost CV score: {grid_search.best_score_:.4f}")
        
        return grid_search.best_estimator_
    
    def optimize_random_forest(self, X_train, y_train):
        """Optimize Random Forest hyperparameters"""
        print("\nOptimizing Random Forest hyperparameters...")
        
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 15, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2']
        }
        
        base_model = RandomForestRegressor(random_state=42, n_jobs=-1)
        
        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=3,
            scoring='r2',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        print(f"Best Random Forest params: {grid_search.best_params_}")
        print(f"Best Random Forest CV score: {grid_search.best_score_:.4f}")
        
        return grid_search.best_estimator_
    
    def optimize_gradient_boosting(self, X_train, y_train):
        """Optimize Gradient Boosting hyperparameters"""
        print("\nOptimizing Gradient Boosting hyperparameters...")
        
        param_grid = {
            'n_estimators': [100, 200, 300],
            'learning_rate': [0.01, 0.05, 0.1],
            'max_depth': [5, 7, 9],
            'subsample': [0.8, 0.9, 1.0],
            'min_samples_split': [2, 5, 10]
        }
        
        base_model = GradientBoostingRegressor(random_state=42)
        
        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=3,
            scoring='r2',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        print(f"Best Gradient Boosting params: {grid_search.best_params_}")
        print(f"Best Gradient Boosting CV score: {grid_search.best_score_:.4f}")
        
        return grid_search.best_estimator_
    
    def train_ensemble_model(self, X_train, y_train, models):
        """Create ensemble of best models"""
        print("\nTraining ensemble model...")
        
        ensemble = VotingRegressor(
            estimators=[(name, model) for name, model in models.items()],
            weights=None  # Equal weights, can be optimized
        )
        
        ensemble.fit(X_train, y_train)
        return ensemble
    
    def evaluate_model_comprehensive(self, model, X_train, X_test, y_train, y_test, model_name):
        """Comprehensive model evaluation"""
        # Train predictions
        y_train_pred = model.predict(X_train)
        
        # Test predictions
        y_test_pred = model.predict(X_test)
        
        # Calculate metrics
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        
        # MAPE
        train_mape = mean_absolute_percentage_error(y_train, y_train_pred) * 100
        test_mape = mean_absolute_percentage_error(y_test, y_test_pred) * 100
        
        # Cross-validation score
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
        
        metrics = {
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'train_mape': train_mape,
            'test_mape': test_mape,
            'cv_r2_mean': cv_mean,
            'cv_r2_std': cv_std
        }
        
        print(f"\n{model_name} Performance:")
        print(f"  Train R²:  {train_r2:.4f}")
        print(f"  Test R²:   {test_r2:.4f}")
        print(f"  CV R²:     {cv_mean:.4f} (±{cv_std:.4f})")
        print(f"  Test MAE:  {test_mae:,.0f}")
        print(f"  Test RMSE: {test_rmse:,.0f}")
        print(f"  Test MAPE: {test_mape:.2f}%")
        
        self.cv_scores[model_name] = {'mean': cv_mean, 'std': cv_std}
        
        return metrics, y_test_pred
    
    def calculate_prediction_intervals(self, model, X_test, y_test, y_pred, confidence=0.95):
        """Calculate prediction intervals for uncertainty quantification"""
        # Calculate residuals
        residuals = y_test - y_pred
        residual_std = np.std(residuals)
        
        # For tree-based models, use residual distribution
        # For linear models, could use analytical intervals
        z_score = 1.96  # For 95% confidence
        
        # Prediction intervals
        lower_bound = y_pred - z_score * residual_std
        upper_bound = y_pred + z_score * residual_std
        
        # Ensure non-negative
        lower_bound = np.maximum(lower_bound, 0)
        
        return lower_bound, upper_bound, residual_std
    
    def train_all_models(self, X_train, X_test, y_train, y_test):
        """Train and evaluate all models with optimization"""
        print("\n" + "=" * 60)
        print("IMPROVED MODEL TRAINING WITH OPTIMIZATION")
        print("=" * 60)
        
        results = {}
        trained_models = {}
        
        # Train optimized models
        try:
            xgb_model = self.optimize_xgboost(X_train, y_train)
            xgb_metrics, xgb_pred = self.evaluate_model_comprehensive(
                xgb_model, X_train, X_test, y_train, y_test, "XGBoost (Optimized)"
            )
            results['XGBoost'] = {'model': xgb_model, 'metrics': xgb_metrics, 'predictions': xgb_pred}
            trained_models['xgb'] = xgb_model
        except Exception as e:
            print(f"Error optimizing XGBoost: {e}")
            # Fallback to default
            xgb_model = xgb.XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=8, random_state=42, n_jobs=-1)
            xgb_model.fit(X_train, y_train)
            xgb_metrics, xgb_pred = self.evaluate_model_comprehensive(
                xgb_model, X_train, X_test, y_train, y_test, "XGBoost (Default)"
            )
            results['XGBoost'] = {'model': xgb_model, 'metrics': xgb_metrics, 'predictions': xgb_pred}
            trained_models['xgb'] = xgb_model
        
        try:
            rf_model = self.optimize_random_forest(X_train, y_train)
            rf_metrics, rf_pred = self.evaluate_model_comprehensive(
                rf_model, X_train, X_test, y_train, y_test, "Random Forest (Optimized)"
            )
            results['Random Forest'] = {'model': rf_model, 'metrics': rf_metrics, 'predictions': rf_pred}
            trained_models['rf'] = rf_model
        except Exception as e:
            print(f"Error optimizing Random Forest: {e}")
            # Fallback to default
            rf_model = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
            rf_model.fit(X_train, y_train)
            rf_metrics, rf_pred = self.evaluate_model_comprehensive(
                rf_model, X_train, X_test, y_train, y_test, "Random Forest (Default)"
            )
            results['Random Forest'] = {'model': rf_model, 'metrics': rf_metrics, 'predictions': rf_pred}
            trained_models['rf'] = rf_model
        
        try:
            gb_model = self.optimize_gradient_boosting(X_train, y_train)
            gb_metrics, gb_pred = self.evaluate_model_comprehensive(
                gb_model, X_train, X_test, y_train, y_test, "Gradient Boosting (Optimized)"
            )
            results['Gradient Boosting'] = {'model': gb_model, 'metrics': gb_metrics, 'predictions': gb_pred}
            trained_models['gb'] = gb_model
        except Exception as e:
            print(f"Error optimizing Gradient Boosting: {e}")
            # Fallback to default
            gb_model = GradientBoostingRegressor(n_estimators=200, learning_rate=0.05, max_depth=8, random_state=42)
            gb_model.fit(X_train, y_train)
            gb_metrics, gb_pred = self.evaluate_model_comprehensive(
                gb_model, X_train, X_test, y_train, y_test, "Gradient Boosting (Default)"
            )
            results['Gradient Boosting'] = {'model': gb_model, 'metrics': gb_metrics, 'predictions': gb_pred}
            trained_models['gb'] = gb_model
        
        # Train ensemble
        if len(trained_models) >= 2:
            try:
                ensemble_model = self.train_ensemble_model(X_train, y_train, trained_models)
                ensemble_metrics, ensemble_pred = self.evaluate_model_comprehensive(
                    ensemble_model, X_train, X_test, y_train, y_test, "Ensemble"
                )
                results['Ensemble'] = {'model': ensemble_model, 'metrics': ensemble_metrics, 'predictions': ensemble_pred}
                trained_models['ensemble'] = ensemble_model
            except Exception as e:
                print(f"Error training ensemble: {e}")
        
        # Find best model (based on test R²)
        best_model_name = max(results.keys(), key=lambda k: results[k]['metrics']['test_r2'])
        self.best_model = results[best_model_name]['model']
        self.best_model_name = best_model_name
        
        # Calculate prediction intervals for best model
        best_pred = results[best_model_name]['predictions']
        lower, upper, residual_std = self.calculate_prediction_intervals(
            self.best_model, X_test, y_test, best_pred
        )
        self.prediction_intervals = {
            'lower': lower,
            'upper': upper,
            'residual_std': residual_std
        }
        
        print("\n" + "=" * 60)
        print("MODEL COMPARISON")
        print("=" * 60)
        print(f"{'Model':<30} {'Test R²':<12} {'CV R²':<15} {'Test MAE':<15} {'Test MAPE':<12}")
        print("-" * 90)
        for name, result in results.items():
            metrics = result['metrics']
            print(f"{name:<30} {metrics['test_r2']:<12.4f} {metrics['cv_r2_mean']:<15.4f} {metrics['test_mae']:<15,.0f} {metrics['test_mape']:<12.2f}%")
        
        print(f"\n[Best Model] {best_model_name}")
        print(f"  Test R²: {results[best_model_name]['metrics']['test_r2']:.4f}")
        print(f"  CV R²:   {results[best_model_name]['metrics']['cv_r2_mean']:.4f} (±{results[best_model_name]['metrics']['cv_r2_std']:.4f})")
        print(f"  Test MAE: {results[best_model_name]['metrics']['test_mae']:,.0f}")
        print(f"  Residual STD: {residual_std:,.0f}")
        
        return results
    
    def get_feature_importance(self, model, feature_names, top_n=15):
        """Get feature importance"""
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1][:top_n]
            
            print(f"\nTop {top_n} Most Important Features:")
            print("-" * 70)
            for i, idx in enumerate(indices, 1):
                feat_name = feature_names[idx]
                if len(feat_name) > 50:
                    feat_name = feat_name[:47] + "..."
                print(f"{i:2d}. {feat_name:<50} {importances[idx]:.4f}")
            
            return dict(zip([feature_names[i] for i in indices], [importances[i] for i in indices]))
        return None
    
    def save_model(self):
        """Save best model and metadata"""
        if self.best_model is None:
            print("No model to save.")
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
        
        # Save metadata with prediction intervals
        metadata = {
            'model_name': self.best_model_name,
            'training_date': datetime.now().isoformat(),
            'feature_count': len(self.feature_names),
            'feature_names': self.feature_names,
            'cv_scores': self.cv_scores,
            'prediction_interval_std': float(self.prediction_intervals['residual_std']) if self.prediction_intervals else None
        }
        metadata_path = os.path.join(MODEL_DIR, MODEL_METADATA_NAME)
        joblib.dump(metadata, metadata_path)
        print(f"Metadata saved to: {metadata_path}")


def main():
    """Main execution"""
    trainer = ImprovedModelTrainer()
    
    input_path = 'processed_data/youtube_videos_processed.csv'
    
    if not os.path.exists(input_path):
        print(f"Error: Processed data not found: {input_path}")
        return
    
    # Load data
    df = trainer.load_data(input_path)
    
    # Prepare data
    X, y = trainer.prepare_data(df)
    print(f"\nFeatures: {X.shape[1]}, Samples: {X.shape[0]}")
    
    # Split data
    X_train, X_test, y_train, y_test, X_train_raw, X_test_raw = trainer.train_test_split_data(X, y)
    print(f"Train set: {X_train.shape[0]}, Test set: {X_test.shape[0]}")
    
    # Train models
    results = trainer.train_all_models(X_train, X_test, y_train, y_test)
    
    # Feature importance
    if trainer.best_model and hasattr(trainer.best_model, 'feature_importances_'):
        trainer.get_feature_importance(trainer.best_model, trainer.feature_names)
    
    # Save model
    trainer.save_model()
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()

