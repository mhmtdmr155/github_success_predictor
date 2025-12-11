"""
Improve Model - Complete Pipeline
Re-runs preprocessing with advanced features and trains improved model
"""
import os
import sys

def run_preprocessing():
    """Run improved data preprocessing"""
    print("\n" + "="*60)
    print("STEP 1: IMPROVED DATA PREPROCESSING")
    print("="*60)
    from src.data_preprocessing import DataPreprocessor
    preprocessor = DataPreprocessor()
    df = preprocessor.preprocess('raw_data/youtube_videos_raw.csv')
    X, y = preprocessor.select_features(df)
    print(f"\nFinal dataset: {X.shape}")
    print(f"Target stats: mean={y.mean():,.0f}, std={y.std():,.0f}, min={y.min():,.0f}, max={y.max():,.0f}")
    return True

def run_training():
    """Run improved model training"""
    print("\n" + "="*60)
    print("STEP 2: IMPROVED MODEL TRAINING")
    print("="*60)
    from src.improved_model_training import ImprovedModelTrainer
    trainer = ImprovedModelTrainer()
    
    input_path = 'processed_data/youtube_videos_processed.csv'
    
    if not os.path.exists(input_path):
        print(f"Error: Processed data not found: {input_path}")
        return False
    
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
        trainer.get_feature_importance(trainer.best_model, trainer.feature_names, top_n=15)
    
    # Save model
    trainer.save_model()
    
    print("\n" + "="*60)
    print("MODEL IMPROVEMENT COMPLETE")
    print("="*60)
    
    return True

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("YOUTUBE SUCCESS PREDICTOR - MODEL IMPROVEMENT")
    print("="*60)
    
    # Check if raw data exists
    if not os.path.exists('raw_data/youtube_videos_raw.csv'):
        print("\nError: Raw data not found!")
        print("Please run create_sample_data.py first to create sample data.")
        print("Or use data_collection.py to collect real data from YouTube API.")
        return
    
    # Step 1: Preprocessing
    if not run_preprocessing():
        print("Preprocessing failed. Exiting.")
        return
    
    # Step 2: Training
    if not run_training():
        print("Training failed. Exiting.")
        return
    
    print("\n" + "="*60)
    print("SUCCESS! Model has been improved.")
    print("="*60)
    print("\nYou can now:")
    print("  1. Restart Flask app: python app.py")
    print("  2. Test predictions at: http://localhost:5000")
    print("  3. Check model performance in models/ directory")

if __name__ == '__main__':
    main()

