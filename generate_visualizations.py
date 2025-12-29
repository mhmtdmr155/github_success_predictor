"""
Grafik oluşturma scripti - Model karşılaştırma grafikleri
"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # GUI olmadan çalışması için
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.model_training import ModelTrainer

# Türkçe karakter desteği
plt.rcParams['font.family'] = 'DejaVu Sans'
sns.set_style("whitegrid")
sns.set_palette("husl")

def create_comparison_charts(results, output_dir='visualizations'):
    """Model karşılaştırma grafikleri oluştur"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Veriyi hazırla
    models = []
    r2_val = []
    r2_test = []
    mae_val = []
    mae_test = []
    rmse_val = []
    rmse_test = []
    
    for name, result in results.items():
        models.append(name)
        r2_val.append(result['metrics_val']['R²'])
        r2_test.append(result['metrics_test']['R²'])
        mae_val.append(result['metrics_val']['MAE'])
        mae_test.append(result['metrics_test']['MAE'])
        rmse_val.append(result['metrics_val']['RMSE'])
        rmse_test.append(result['metrics_test']['RMSE'])
    
    # 1. R² Skoru Karşılaştırması (Validation vs Test)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    x = np.arange(len(models))
    width = 0.35
    
    # Validation R²
    bars1 = ax1.bar(x - width/2, r2_val, width, label='Validation Set', color='#667eea', alpha=0.8)
    bars2 = ax1.bar(x + width/2, r2_test, width, label='Test Set', color='#764ba2', alpha=0.8)
    
    ax1.set_xlabel('Algoritma', fontsize=12, fontweight='bold')
    ax1.set_ylabel('R² Skoru', fontsize=12, fontweight='bold')
    ax1.set_title('R² Skoru Karşılaştırması (Validation vs Test)', fontsize=14, fontweight='bold', pad=20)
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, rotation=15, ha='right')
    ax1.legend(fontsize=10)
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_ylim([0, max(max(r2_val), max(r2_test)) * 1.2])
    
    # Değerleri çubukların üzerine yaz
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}',
                    ha='center', va='bottom', fontsize=9)
    
    # MAE Karşılaştırması
    bars3 = ax2.bar(x - width/2, mae_val, width, label='Validation Set', color='#84fab0', alpha=0.8)
    bars4 = ax2.bar(x + width/2, mae_test, width, label='Test Set', color='#8fd3f4', alpha=0.8)
    
    ax2.set_xlabel('Algoritma', fontsize=12, fontweight='bold')
    ax2.set_ylabel('MAE (Görüntülenme)', fontsize=12, fontweight='bold')
    ax2.set_title('MAE Karşılaştırması (Validation vs Test)', fontsize=14, fontweight='bold', pad=20)
    ax2.set_xticks(x)
    ax2.set_xticklabels(models, rotation=15, ha='right')
    ax2.legend(fontsize=10)
    ax2.grid(axis='y', alpha=0.3)
    
    # Değerleri çubukların üzerine yaz
    for bars in [bars3, bars4]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:,.0f}',
                    ha='center', va='bottom', fontsize=9, rotation=90)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'model_comparison_metrics.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Grafik kaydedildi: model_comparison_metrics.png")
    
    # 2. Validation Set R² Skoru (Model Seçimi için)
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # En iyi modeli bul (validation setinde)
    best_idx = r2_val.index(max(r2_val))
    best_model_name = models[best_idx]
    
    colors = ['#764ba2' if i == best_idx else '#95a5a6' for i in range(len(models))]
    bars = ax.barh(models, r2_val, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # En iyi modeli vurgula
    bars[best_idx].set_color('#764ba2')
    bars[best_idx].set_edgecolor('#2c3e50')
    bars[best_idx].set_linewidth(2.5)
    
    ax.set_xlabel('R² Skoru (Validation Set)', fontsize=13, fontweight='bold')
    ax.set_title(f'Model Seçimi: Validation Set R² Skorları\n({best_model_name} En İyi Performansı Gösterdi - R²={max(r2_val):.4f})', 
                fontsize=15, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    ax.set_xlim([0, max(r2_val) * 1.15])
    
    # Değerleri yaz
    for i, (bar, val) in enumerate(zip(bars, r2_val)):
        ax.text(val + 0.01, bar.get_y() + bar.get_height()/2,
               f'{val:.4f}',
               va='center', fontsize=11, fontweight='bold' if i == best_idx else 'normal')
    
    # En iyi modeli işaretle
    ax.text(max(r2_val) * 0.5, best_idx, '* EN İYİ MODEL', 
           ha='center', va='center', fontsize=12, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'validation_r2_selection.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Grafik kaydedildi: validation_r2_selection.png")
    
    # 3. Test Set Final Performans
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # En iyi modeli bul (test setinde)
    best_idx = r2_test.index(max(r2_test))
    best_model_name = models[best_idx]
    best_r2 = max(r2_test)
    
    colors = ['#667eea' if i == best_idx else '#95a5a6' for i in range(len(models))]
    bars = ax.barh(models, r2_test, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    bars[best_idx].set_color('#667eea')
    bars[best_idx].set_edgecolor('#2c3e50')
    bars[best_idx].set_linewidth(2.5)
    
    ax.set_xlabel('R² Skoru (Test Set)', fontsize=13, fontweight='bold')
    ax.set_title(f'Final Model Değerlendirmesi: Test Set R² Skorları\n({best_model_name}: R² = {best_r2:.4f})', 
                fontsize=15, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    ax.set_xlim([0, max(r2_test) * 1.15])
    
    for i, (bar, val) in enumerate(zip(bars, r2_test)):
        ax.text(val + 0.01, bar.get_y() + bar.get_height()/2,
               f'{val:.4f}',
               va='center', fontsize=11, fontweight='bold' if i == best_idx else 'normal')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'test_set_performance.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Grafik kaydedildi: test_set_performance.png")
    
    # 4. Tüm Metriklerin Karşılaştırması (Heatmap)
    metrics_df = pd.DataFrame({
        'Model': models,
        'R² (Val)': r2_val,
        'R² (Test)': r2_test,
        'MAE (Val)': mae_val,
        'MAE (Test)': mae_test,
        'RMSE (Val)': rmse_val,
        'RMSE (Test)': rmse_test
    })
    
    # Normalize et (0-1 arası) heatmap için
    metrics_normalized = metrics_df.copy()
    for col in ['R² (Val)', 'R² (Test)']:
        metrics_normalized[col] = (metrics_normalized[col] - metrics_normalized[col].min()) / (metrics_normalized[col].max() - metrics_normalized[col].min())
    for col in ['MAE (Val)', 'MAE (Test)', 'RMSE (Val)', 'RMSE (Test)']:
        metrics_normalized[col] = 1 - (metrics_normalized[col] - metrics_normalized[col].min()) / (metrics_normalized[col].max() - metrics_normalized[col].min())
    
    fig, ax = plt.subplots(figsize=(10, 6))
    heatmap_data = metrics_normalized.set_index('Model').T
    
    sns.heatmap(heatmap_data, annot=True, fmt='.3f', cmap='RdYlGn', 
                cbar_kws={'label': 'Normalize Edilmiş Skor (Yüksek = İyi)'},
                linewidths=0.5, linecolor='gray', ax=ax)
    
    ax.set_title('Model Performans Karşılaştırması (Tüm Metrikler)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Algoritma', fontsize=12, fontweight='bold')
    ax.set_ylabel('Metrik', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'performance_heatmap.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Grafik kaydedildi: performance_heatmap.png")
    
    # 5. Validation vs Test Karşılaştırması (Scatter)
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Test setinde en iyi modeli bul
    best_test_idx = r2_test.index(max(r2_test))
    best_test_model = models[best_test_idx]
    
    for i, model in enumerate(models):
        if i == best_test_idx:
            color = '#764ba2'
            marker = '*'
            size = 200
            label = model
        else:
            color = '#667eea'
            marker = 'o'
            size = 100
            label = None
        ax.scatter(r2_val[i], r2_test[i], s=size, c=color, marker=marker, 
                  edgecolors='black', linewidths=2, label=label, zorder=3)
        ax.annotate(model, (r2_val[i], r2_test[i]), 
                   xytext=(5, 5), textcoords='offset points', fontsize=10, fontweight='bold')
    
    # Diyagonal çizgi (mükemmel uyum)
    min_val = min(min(r2_val), min(r2_test))
    max_val = max(max(r2_val), max(r2_test))
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5, linewidth=2, label='Mükemmel Uyum')
    
    ax.set_xlabel('Validation Set R² Skoru', fontsize=12, fontweight='bold')
    ax.set_ylabel('Test Set R² Skoru', fontsize=12, fontweight='bold')
    ax.set_title('Validation vs Test Set Performans Karşılaştırması\n(Overfitting Kontrolü)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    ax.set_aspect('equal', adjustable='box')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'validation_vs_test.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Grafik kaydedildi: validation_vs_test.png")
    
    return output_dir

def main():
    """Ana fonksiyon"""
    print("="*60)
    print("GRAFIK OLUSTURMA BASLADI")
    print("="*60)
    
    trainer = ModelTrainer()
    
    input_path = 'processed_data/youtube_videos_processed.csv'
    
    if not os.path.exists(input_path):
        print(f"Hata: Veri dosyasi bulunamadi: {input_path}")
        return
    
    # Veriyi yükle ve hazırla
    print("\nVeri yukleniyor...")
    df = trainer.load_data(input_path)
    X, y = trainer.prepare_data(df)
    print(f"Ozellikler: {X.shape[1]}, Ornekler: {X.shape[0]}")
    
    # Veriyi böl
    print("\nVeri bolunuyor...")
    X_train, X_val, X_test, y_train, y_val, y_test = trainer.train_test_split_data(X, y)
    
    # Modelleri eğit
    print("\nModeller egitiliyor...")
    results = trainer.train_all_models(X_train, X_val, X_test, y_train, y_val, y_test)
    
    # Grafikleri oluştur
    print("\n" + "="*60)
    print("GRAFIKLER OLUSTURULUYOR")
    print("="*60)
    output_dir = create_comparison_charts(results)
    
    print("\n" + "="*60)
    print("TAMAMLANDI!")
    print(f"Grafikler '{output_dir}' klasorunde kaydedildi.")
    print("="*60)

if __name__ == '__main__':
    main()

