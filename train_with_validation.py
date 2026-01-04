"""
Train model with Train/Validation/Test split (70/15/15)
Uses processed dataset produced from raw_data/youtube_videos_improved.csv

This script also writes a single source of truth into models/model_metadata.pkl:
- split sizes
- validation metrics (for best model)
- per-model test metrics table (results_summary)
"""
import os
import sys
import numpy as np
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.improved_model_training import ImprovedModelTrainer


def main() -> int:
    print("=" * 60)
    print("TRAIN/VALIDATION/TEST SPLIT VE MODEL EGITIMI (70/15/15)")
    print("=" * 60)

    trainer = ImprovedModelTrainer()

    input_path = "processed_data/youtube_videos_processed_all.csv"
    if not os.path.exists(input_path):
        print(f"Error: Processed data not found: {input_path}")
        return 1

    print(f"\nGiris dosyasi: {input_path}")
    df = trainer.load_data(input_path)

    X, y = trainer.prepare_data(df)
    print(f"\nOzellik sayisi: {X.shape[1]}, Toplam ornek: {X.shape[0]}")

    print("\n" + "=" * 60)
    print("VERI BOLUNMESI (70% Train / 15% Validation / 15% Test)")
    print("=" * 60)

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=42
    )

    print(f"Train seti: {len(X_train)} video ({len(X_train)/len(X)*100:.1f}%)")
    print(f"Validation seti: {len(X_val)} video ({len(X_val)/len(X)*100:.1f}%)")
    print(f"Test seti: {len(X_test)} video ({len(X_test)/len(X)*100:.1f}%)")

    # Less aggressive outlier filter on training only (2*IQR)
    print("\nTraining setinden outlier filtreleme (2*IQR)...")
    q1 = y_train.quantile(0.25)
    q3 = y_train.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 2.0 * iqr
    upper = q3 + 2.0 * iqr

    mask = (y_train >= lower) & (y_train <= upper)
    X_train_clean = X_train[mask]
    y_train_clean = y_train[mask]
    removed = int(len(X_train) - len(X_train_clean))
    print(f"Filtrelenen outlier: {removed} video ({removed/len(X_train)*100:.1f}%)")
    print(f"Final train seti: {len(X_train_clean)} video")

    # Scale features
    X_train_scaled = trainer.scaler.fit_transform(X_train_clean)
    X_val_scaled = trainer.scaler.transform(X_val)
    X_test_scaled = trainer.scaler.transform(X_test)

    print("\n" + "=" * 60)
    print("MODEL EGITIMI BASLIYOR")
    print("=" * 60)

    results = trainer.train_all_models(X_train_scaled, X_test_scaled, y_train_clean, y_test)

    # Build per-model test metrics summary for the article
    results_summary = {}
    for model_key, payload in (results or {}).items():
        metrics = payload.get("metrics", {}) if isinstance(payload, dict) else {}
        results_summary[model_key] = {
            "test_r2": float(metrics.get("test_r2", 0.0)),
            "test_mae": float(metrics.get("test_mae", 0.0)),
            "test_rmse": float(metrics.get("test_rmse", 0.0)),
            "test_mape": float(metrics.get("test_mape", 0.0)),
            "cv_r2_mean": float(metrics.get("cv_r2_mean", 0.0)),
            "cv_r2_std": float(metrics.get("cv_r2_std", 0.0)),
            "train_r2": float(metrics.get("train_r2", 0.0)),
        }

    # Validation evaluation for best model
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    if not trainer.best_model:
        print("Hata: Model egitilemedi!")
        return 1

    y_val_pred = trainer.best_model.predict(X_val_scaled)
    val_mae = mean_absolute_error(y_val, y_val_pred)
    val_rmse = np.sqrt(mean_squared_error(y_val, y_val_pred))
    val_r2 = r2_score(y_val, y_val_pred)

    print("\n" + "=" * 60)
    print("VALIDATION SET PERFORMANSI (Best Model)")
    print("=" * 60)
    print(f"Best Model: {trainer.best_model_name}")
    print(f"  Validation R²:  {val_r2:.4f}")
    print(f"  Validation MAE: {val_mae:,.0f}")
    print(f"  Validation RMSE: {val_rmse:,.0f}")

    # Save model artifacts (best_model.pkl, scaler.pkl, feature_names.pkl, model_metadata.pkl)
    trainer.save_model()

    # Enrich metadata with split & validation & per-model results
    import joblib

    metadata_path = os.path.join("models", "model_metadata.pkl")
    try:
        metadata = joblib.load(metadata_path)
        metadata["validation_r2"] = float(val_r2)
        metadata["validation_mae"] = float(val_mae)
        metadata["validation_rmse"] = float(val_rmse)
        metadata["train_samples"] = int(len(X_train_clean))
        metadata["val_samples"] = int(len(X_val))
        metadata["test_samples"] = int(len(X_test))
        metadata["dataset_total_rows_raw"] = 2653
        metadata["dataset_processed_rows"] = int(len(X))
        metadata["split"] = {"train": 0.70, "val": 0.15, "test": 0.15, "random_state": 42}
        metadata["training_outlier_filter"] = {"method": "IQR", "multiplier": 2.0, "removed": int(removed)}
        metadata["results_summary"] = results_summary
        joblib.dump(metadata, metadata_path)
        print(f"\nMetadata guncellendi: {metadata_path}")
    except Exception as e:
        print(f"Uyari: Metadata guncellenemedi: {e}")

    print("\n" + "=" * 60)
    print("MODEL EGITIMI TAMAMLANDI")
    print("=" * 60)
    print(f"En iyi model: {trainer.best_model_name}")
    print(f"Train/Val/Test: {len(X_train_clean)}/{len(X_val)}/{len(X_test)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())



