"""
Generate/update charts used by makale_youtube_success_predictor.html.

Outputs (overwrites):
- article_chart1_accuracy_loss.png
- article_chart2_loss_convergence.png
- article_chart3_feature_importance.png

Charts are generated from:
- models/model_metadata.pkl (results_summary, split info)
- models/best_model.pkl, models/scaler.pkl, models/feature_names.pkl
- processed_data/youtube_videos_processed_all.csv (to reconstruct test split)
"""

from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.api.types import is_numeric_dtype
from sklearn.model_selection import train_test_split


def main() -> int:
    sns.set_theme(style="whitegrid", font="DejaVu Sans")

    meta = joblib.load("models/model_metadata.pkl")
    results = meta.get("results_summary", {}) or {}

    # --- Chart 1: model comparison (Test R2 + Test MAE) ---
    rows: list[dict] = []
    for name, m in results.items():
        rows.append(
            {
                "Model": name,
                "Test R2": float(m.get("test_r2", 0.0)),
                "Test MAE": float(m.get("test_mae", 0.0)),
                "CV R2 (mean)": float(m.get("cv_r2_mean", 0.0)),
                "CV R2 (std)": float(m.get("cv_r2_std", 0.0)),
                "Test RMSE": float(m.get("test_rmse", 0.0)),
                "Test MAPE (%)": float(m.get("test_mape", 0.0)),
            }
        )

    df_metrics = pd.DataFrame(rows)
    if df_metrics.empty:
        raise RuntimeError("results_summary not found in models/model_metadata.pkl")

    order = df_metrics.sort_values("Test R2", ascending=False)["Model"].tolist()

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=200)

    ax = axes[0]
    sns.barplot(
        data=df_metrics, x="Model", y="Test R2", order=order, ax=ax, palette="viridis"
    )
    ax.set_title("Test R² Karşılaştırması")
    ax.set_xlabel("")
    ax.set_ylabel("Test R²")
    ax.set_ylim(0, max(0.6, float(df_metrics["Test R2"].max()) + 0.05))
    ax.tick_params(axis="x", rotation=15)
    for p in ax.patches:
        ax.annotate(
            f"{p.get_height():.4f}",
            (p.get_x() + p.get_width() / 2, p.get_height()),
            ha="center",
            va="bottom",
            fontsize=9,
            xytext=(0, 3),
            textcoords="offset points",
        )

    ax = axes[1]
    df_mae = df_metrics.copy()
    df_mae["Test MAE (k)"] = df_mae["Test MAE"] / 1000.0
    sns.barplot(
        data=df_mae, x="Model", y="Test MAE (k)", order=order, ax=ax, palette="magma"
    )
    ax.set_title("Test MAE Karşılaştırması")
    ax.set_xlabel("")
    ax.set_ylabel("Test MAE (bin)")
    ax.tick_params(axis="x", rotation=15)
    for p in ax.patches:
        ax.annotate(
            f"{p.get_height():.1f}k",
            (p.get_x() + p.get_width() / 2, p.get_height()),
            ha="center",
            va="bottom",
            fontsize=9,
            xytext=(0, 3),
            textcoords="offset points",
        )

    fig.suptitle(
        "Model Performans Karşılaştırması (Test Seti)",
        fontsize=14,
        fontweight="bold",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig("grafikler/article_chart1_accuracy_loss.png", bbox_inches="tight")
    plt.close(fig)

    # --- Chart 2: y_true vs y_pred scatter + residual histogram ---
    processed_path = "processed_data/youtube_videos_processed_all.csv"
    df = pd.read_csv(processed_path)

    exclude = {
        "video_id",
        "title",
        "description",
        "channel_id",
        "channel_name",
        "published_at",
        "category_id",
        "tags",
        "default_language",
        "default_audio_language",
        "publish_day",
        "time_of_day",
        "duration_category",
        "channel_size",
        "target_first_week_views",
        # post-publish fields
        "view_count",
        "like_count",
        "comment_count",
        "likes_per_1k_views",
        "comments_per_1k_views",
        "engagement_ratio",
    }

    feature_cols = [c for c in df.columns if c not in exclude and is_numeric_dtype(df[c])]
    X = df[feature_cols].copy()
    y = df["target_first_week_views"].copy()

    # Same split procedure as train_with_validation.py
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=42
    )

    # training outlier filter (2*IQR) applied only on training set in train_with_validation.py
    q1 = y_train.quantile(0.25)
    q3 = y_train.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 2.0 * iqr
    upper = q3 + 2.0 * iqr
    mask = (y_train >= lower) & (y_train <= upper)
    _ = X_train[mask]  # only for conceptual parity; scaler is loaded from disk

    model = joblib.load("models/best_model.pkl")
    scaler = joblib.load("models/scaler.pkl")
    feature_names = joblib.load("models/feature_names.pkl")

    X_test_use = X_test.reindex(columns=feature_names, fill_value=0)
    X_test_scaled = scaler.transform(X_test_use)

    y_pred = model.predict(X_test_scaled)
    residuals = y_test.values - y_pred

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=200)

    ax = axes[0]
    ax.scatter(
        y_test,
        y_pred,
        s=18,
        alpha=0.55,
        color="#3EA6FF",
        edgecolors="none",
    )
    maxv = max(float(np.max(y_test)), float(np.max(y_pred)))
    ax.plot(
        [0, maxv],
        [0, maxv],
        linestyle="--",
        color="#FF0000",
        linewidth=1.5,
        label="İdeal (y=x)",
    )
    ax.set_title("Test Seti: Gerçek vs Tahmin")
    ax.set_xlabel("Gerçek İlk 7 Gün Görüntülenme")
    ax.set_ylabel("Tahmin İlk 7 Gün Görüntülenme")
    ax.legend(frameon=True)

    ax = axes[1]
    sns.histplot(residuals, bins=30, kde=True, ax=ax, color="#00D084")
    ax.set_title("Residual Dağılımı (Gerçek - Tahmin)")
    ax.set_xlabel("Residual")
    ax.set_ylabel("Frekans")

    fig.suptitle("Best Model Hata Analizi (Test Seti)", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig("grafikler/article_chart2_loss_convergence.png", bbox_inches="tight")
    plt.close(fig)

    # --- Chart 3: feature importance ---
    fi = getattr(model, "feature_importances_", None)
    if fi is not None:
        idx = np.argsort(fi)[::-1][:15]
        top = pd.DataFrame(
            {
                "Feature": [feature_names[i] for i in idx],
                "Importance": [float(fi[i]) for i in idx],
            }
        )

        fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
        sns.barplot(data=top, y="Feature", x="Importance", ax=ax, palette="crest")
        ax.set_title("Özellik Önem Analizi (Top 15)")
        ax.set_xlabel("Önem Skoru")
        ax.set_ylabel("")
        for i, v in enumerate(top["Importance"].values):
            ax.text(v + 0.001, i, f"{v:.4f}", va="center", fontsize=9)
        fig.tight_layout()
        fig.savefig("grafikler/article_chart3_feature_importance.png", bbox_inches="tight")
        plt.close(fig)

    print(
        "Charts regenerated in grafikler/: article_chart1_accuracy_loss.png, "
        "article_chart2_loss_convergence.png, article_chart3_feature_importance.png"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


