"""
Complete Pipeline Runner
Runs data collection, preprocessing, and model training in sequence
"""
import os
import sys

def run_data_collection():
    """Run data collection"""
    print("\n" + "="*60)
    print("STEP 1: DATA COLLECTION")
    print("="*60)
    from src.data_collection import main
    main()

def run_preprocessing():
    """Run data preprocessing"""
    print("\n" + "="*60)
    print("STEP 2: DATA PREPROCESSING")
    print("="*60)
    from src.data_preprocessing import main
    main()

def run_training():
    """Run model training"""
    print("\n" + "="*60)
    print("STEP 3: MODEL TRAINING")
    print("="*60)
    from src.model_training import main
    main()

def main():
    """Run complete pipeline"""
    print("\n" + "="*60)
    print("YOUTUBE SUCCESS PREDICTOR - COMPLETE PIPELINE")
    print("="*60)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("\n⚠️  WARNING: .env file not found!")
        print("Please create a .env file with your YouTube API key.")
        print("See .env.example for reference.")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Step 1: Data Collection
    try:
        run_data_collection()
    except Exception as e:
        print(f"\n❌ Error in data collection: {e}")
        print("Skipping to preprocessing (if data exists)...")
    
    # Step 2: Preprocessing
    try:
        run_preprocessing()
    except Exception as e:
        print(f"\n❌ Error in preprocessing: {e}")
        print("Skipping to training (if processed data exists)...")
    
    # Step 3: Training
    try:
        run_training()
    except Exception as e:
        print(f"\n❌ Error in training: {e}")
        return
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETE!")
    print("="*60)
    print("\nYou can now run the Flask app:")
    print("  python app.py")
    print("\nThen visit: http://localhost:5000")

if __name__ == '__main__':
    main()

