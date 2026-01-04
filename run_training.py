"""Run model training"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.model_training import ModelTrainer

if __name__ == '__main__':
    trainer = ModelTrainer()
    
    input_path = 'processed_data/youtube_videos_processed.csv'
    
    if not os.path.exists(input_path):
        print(f"Error: Processed data not found: {input_path}")
        exit(1)
    
    df = trainer.load_data(input_path)
    X, y = trainer.prepare_data(df)
    print(f"\nFeatures: {X.shape[1]}, Samples: {X.shape[0]}")
    
    # Split into train, validation, and test sets
    X_train, X_val, X_test, y_train, y_val, y_test = trainer.train_test_split_data(X, y)
    
    results = trainer.train_all_models(X_train, X_val, X_test, y_train, y_val, y_test)
    
    if trainer.best_model and hasattr(trainer.best_model, 'feature_importances_'):
        trainer.get_feature_importance(trainer.best_model, trainer.feature_names)
    
    trainer.save_model()
    
    print("\n" + "=" * 60)
    print("[OK] TRAINING COMPLETE!")
    print("=" * 60)

