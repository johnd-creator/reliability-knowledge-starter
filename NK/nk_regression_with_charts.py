#!/usr/bin/env python3
"""
Model Regresi Prediksi NK Batubara dengan Learning Curves dan Test Charts
Script ini akan membuat model regresi untuk prediksi NK dan menghasilkan visualisasi lengkap
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, learning_curve, validation_curve
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings('ignore')

# Set style untuk plot
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

print("=== MODEL REGRESI PREDIKSI NK BATUBARA ===")
print("Dengan Learning Curves dan Test Charts\n")

# ===== 1. LOAD DAN PREPROCESSING DATA =====
print("1. Loading dan Preprocessing Data...")

# Load data
data = pd.read_excel('Data_DCS_NK.xlsx')
print(f"Data shape: {data.shape}")
print(f"Columns: {list(data.columns)}")

# Prepare features dan target
numeric_columns = data.select_dtypes(include=[np.number]).columns
X = data[numeric_columns].drop(['NK BB (HHV) Coal Feeder'], axis=1)
y = data['NK BB (HHV) Coal Feeder']

print(f"\nFeatures: {list(X.columns)}")
print(f"Number of features: {X.shape[1]}")
print(f"Target: NK BB (HHV) Coal Feeder")
print(f"Target statistics:")
print(f"  Mean: {y.mean():.2f} kJ/kg")
print(f"  Std: {y.std():.2f} kJ/kg")
print(f"  Min: {y.min():.2f} kJ/kg")
print(f"  Max: {y.max():.2f} kJ/kg")

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"\nData split:")
print(f"  Training set: {X_train.shape[0]} samples")
print(f"  Test set: {X_test.shape[0]} samples")

# Scaling features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ===== 2. DEFINISI MODEL =====
print("\n2. Definisi Model Regresi...")

models = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression': Ridge(alpha=1.0),
    'Lasso Regression': Lasso(alpha=1.0),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
    'XGBoost': XGBRegressor(n_estimators=100, random_state=42),
    'LightGBM': LGBMRegressor(n_estimators=100, random_state=42),
    'SVR': SVR(kernel='rbf'),
    'KNN': KNeighborsRegressor(n_neighbors=5),
    'Decision Tree': DecisionTreeRegressor(random_state=42),
    'Neural Network': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
}

print(f"Total models: {len(models)}")

# ===== 3. TRAINING DAN EVALUASI MODEL =====
print("\n3. Training dan Evaluasi Model...")

results = []
trained_models = {}

for name, model in models.items():
    print(f"  Training {name}...")

    # Pilih data yang sesuai (scaled untuk model yang membutuhkan)
    if name in ['Linear Regression', 'Ridge Regression', 'Lasso Regression', 'SVR', 'KNN', 'Neural Network']:
        X_train_use = X_train_scaled
        X_test_use = X_test_scaled
    else:
        X_train_use = X_train
        X_test_use = X_test

    # Training
    model.fit(X_train_use, y_train)

    # Prediksi
    y_train_pred = model.predict(X_train_use)
    y_test_pred = model.predict(X_test_use)

    # Evaluasi
    train_mae = mean_absolute_error(y_train, y_train_pred)
    test_mae = mean_absolute_error(y_test, y_test_pred)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
    train_r2 = r2_score(y_train, y_train_pred)
    test_r2 = r2_score(y_test, y_test_pred)

    # Cross validation
    cv_scores = cross_val_score(model, X_train_use, y_train, cv=5, scoring='neg_mean_absolute_error')
    cv_mae = -cv_scores.mean()
    cv_std = cv_scores.std()

    results.append({
        'Model': name,
        'Train_MAE': train_mae,
        'Test_MAE': test_mae,
        'Train_RMSE': train_rmse,
        'Test_RMSE': test_rmse,
        'Train_R2': train_r2,
        'Test_R2': test_r2,
        'CV_MAE': cv_mae,
        'CV_Std': cv_std,
        'Overfitting': train_mae - test_mae
    })

    # Simpan model yang sudah ditraining
    trained_models[name] = {
        'model': model,
        'X_train': X_train_use,
        'X_test': X_test_use,
        'y_train_pred': y_train_pred,
        'y_test_pred': y_test_pred
    }

# Convert ke DataFrame
results_df = pd.DataFrame(results)
results_df = results_df.sort_values('Test_MAE')

print("\n=== HASIL EVALUASI MODEL ===")
print(results_df[['Model', 'Test_MAE', 'Test_R2', 'CV_MAE', 'Overfitting']].round(4))

# ===== 4. LEARNING CURVES =====
print("\n4. Membuat Learning Curves...")

# Pilih top 3 model terbaik
top_models = results_df.head(3)['Model'].tolist()

fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('Learning Curves - Top Models', fontsize=16, fontweight='bold')

for i, model_name in enumerate(top_models[:4]):
    row = i // 2
    col = i % 2

    model = models[model_name]

    # Pilih data yang sesuai
    if model_name in ['Linear Regression', 'Ridge Regression', 'Lasso Regression', 'SVR', 'KNN', 'Neural Network']:
        X_use = X_train_scaled
    else:
        X_use = X_train

    # Generate learning curve
    train_sizes, train_scores, val_scores = learning_curve(
        model, X_use, y_train, cv=5, n_jobs=-1,
        train_sizes=np.linspace(0.1, 1.0, 10),
        scoring='neg_mean_absolute_error'
    )

    # Convert ke positive MAE
    train_scores = -train_scores
    val_scores = -val_scores

    # Calculate mean dan std
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    val_std = np.std(val_scores, axis=1)

    # Plot
    axes[row, col].plot(train_sizes, train_mean, 'o-', color='blue', label='Training MAE')
    axes[row, col].fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1, color='blue')
    axes[row, col].plot(train_sizes, val_mean, 'o-', color='red', label='Validation MAE')
    axes[row, col].fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.1, color='red')

    axes[row, col].set_title(f'{model_name}', fontweight='bold')
    axes[row, col].set_xlabel('Training Set Size')
    axes[row, col].set_ylabel('MAE (kJ/kg)')
    axes[row, col].legend()
    axes[row, col].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('learning_curves_nk.png', dpi=300, bbox_inches='tight')
print("Learning curves disimpan sebagai: learning_curves_nk.png")

# ===== 5. TEST CHARTS - ACTUAL VS PREDICTED =====
print("\n5. Membuat Test Charts - Actual vs Predicted...")

fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('Test Results: Actual vs Predicted NK', fontsize=16, fontweight='bold')

for i, model_name in enumerate(top_models[:4]):
    row = i // 2
    col = i % 2

    model_data = trained_models[model_name]
    y_test_pred = model_data['y_test_pred']

    # Scatter plot
    axes[row, col].scatter(y_test, y_test_pred, alpha=0.6, s=50)

    # Perfect prediction line
    min_val = min(y_test.min(), y_test_pred.min())
    max_val = max(y_test.max(), y_test_pred.max())
    axes[row, col].plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')

    # Calculate metrics
    mae = mean_absolute_error(y_test, y_test_pred)
    r2 = r2_score(y_test, y_test_pred)

    axes[row, col].set_title(f'{model_name}\nMAE: {mae:.2f} kJ/kg, R²: {r2:.3f}', fontweight='bold')
    axes[row, col].set_xlabel('Actual NK (kJ/kg)')
    axes[row, col].set_ylabel('Predicted NK (kJ/kg)')
    axes[row, col].legend()
    axes[row, col].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('test_charts_actual_vs_predicted.png', dpi=300, bbox_inches='tight')
print("Test charts disimpan sebagai: test_charts_actual_vs_predicted.png")

# ===== 6. COMPREHENSIVE VISUALIZATION =====
print("\n6. Membuat Visualisasi Comprehensive...")

# Model terbaik
best_model_name = results_df.iloc[0]['Model']
best_model_data = trained_models[best_model_name]
best_y_test_pred = best_model_data['y_test_pred']

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle(f'Comprehensive Analysis - Best Model: {best_model_name}', fontsize=16, fontweight='bold')

# 1. Model Performance Comparison
ax1 = axes[0, 0]
top_5_models = results_df.head(5)
ax1.barh(top_5_models['Model'], top_5_models['Test_MAE'], color='skyblue')
ax1.set_xlabel('Test MAE (kJ/kg)')
ax1.set_title('Top 5 Models Performance')
ax1.grid(True, alpha=0.3)

# 2. Residual Plot
ax2 = axes[0, 1]
residuals = y_test - best_y_test_pred
ax2.scatter(best_y_test_pred, residuals, alpha=0.6)
ax2.axhline(y=0, color='r', linestyle='--')
ax2.set_xlabel('Predicted NK (kJ/kg)')
ax2.set_ylabel('Residuals (kJ/kg)')
ax2.set_title('Residual Plot')
ax2.grid(True, alpha=0.3)

# 3. Error Distribution
ax3 = axes[0, 2]
ax3.hist(residuals, bins=30, alpha=0.7, color='lightgreen', edgecolor='black')
ax3.axvline(x=0, color='r', linestyle='--', label='Zero Error')
ax3.set_xlabel('Residuals (kJ/kg)')
ax3.set_ylabel('Frequency')
ax3.set_title('Error Distribution')
ax3.legend()
ax3.grid(True, alpha=0.3)

# 4. R² Comparison
ax4 = axes[1, 0]
ax4.bar(top_5_models['Model'], top_5_models['Test_R2'], color='lightcoral')
ax4.set_ylabel('R² Score')
ax4.set_title('R² Score Comparison')
ax4.tick_params(axis='x', rotation=45)
ax4.grid(True, alpha=0.3)

# 5. Training vs Test Performance
ax5 = axes[1, 1]
ax5.scatter(results_df['Train_MAE'], results_df['Test_MAE'], s=100, alpha=0.7)
for i, model in enumerate(results_df['Model']):
    if i < 5:  # Label top 5 models
        ax5.annotate(model, (results_df.iloc[i]['Train_MAE'], results_df.iloc[i]['Test_MAE']),
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
# Perfect line
min_mae = min(results_df['Train_MAE'].min(), results_df['Test_MAE'].min())
max_mae = max(results_df['Train_MAE'].max(), results_df['Test_MAE'].max())
ax5.plot([min_mae, max_mae], [min_mae, max_mae], 'r--', alpha=0.8)
ax5.set_xlabel('Training MAE (kJ/kg)')
ax5.set_ylabel('Test MAE (kJ/kg)')
ax5.set_title('Training vs Test Performance')
ax5.grid(True, alpha=0.3)

# 6. Feature Importance (untuk tree-based models)
ax6 = axes[1, 2]
if best_model_name in ['Random Forest', 'Gradient Boosting', 'XGBoost', 'LightGBM', 'Decision Tree']:
    best_model = trained_models[best_model_name]['model']
    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_
        feature_names = X.columns
        indices = np.argsort(importances)[::-1][:10]  # Top 10 features

        ax6.barh(range(len(indices)), importances[indices], color='gold')
        ax6.set_yticks(range(len(indices)))
        ax6.set_yticklabels([feature_names[i] for i in indices])
        ax6.set_xlabel('Feature Importance')
        ax6.set_title('Top 10 Feature Importance')
else:
    ax6.text(0.5, 0.5, f'Feature importance\nnot available for\n{best_model_name}',
             ha='center', va='center', transform=ax6.transAxes, fontsize=12)
    ax6.set_title('Feature Importance')

ax6.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('comprehensive_nk_analysis.png', dpi=300, bbox_inches='tight')
print("Comprehensive analysis disimpan sebagai: comprehensive_nk_analysis.png")

# ===== 7. SAVE RESULTS =====
print("\n7. Menyimpan Hasil...")

# Save results to CSV
results_df.to_csv('nk_regression_results.csv', index=False)
print("Hasil evaluasi disimpan sebagai: nk_regression_results.csv")

# Save best model predictions
prediction_results = pd.DataFrame({
    'Actual_NK': y_test.values,
    'Predicted_NK': best_y_test_pred,
    'Residual': y_test.values - best_y_test_pred,
    'Absolute_Error': np.abs(y_test.values - best_y_test_pred)
})
prediction_results.to_csv('nk_predictions_best_model.csv', index=False)
print("Prediksi model terbaik disimpan sebagai: nk_predictions_best_model.csv")

# ===== 8. SUMMARY REPORT =====
print("\n" + "="*60)
print("SUMMARY REPORT - MODEL REGRESI PREDIKSI NK")
print("="*60)

print(f"\n📊 DATASET INFO:")
print(f"   Total samples: {len(data)}")
print(f"   Features: {X.shape[1]}")
print(f"   Target range: {y.min():.2f} - {y.max():.2f} kJ/kg")
print(f"   Training set: {len(X_train)} samples")
print(f"   Test set: {len(X_test)} samples")

print(f"\n🏆 BEST MODEL: {best_model_name}")
best_result = results_df.iloc[0]
print(f"   Test MAE: {best_result['Test_MAE']:.2f} kJ/kg")
print(f"   Test R²: {best_result['Test_R2']:.4f}")
print(f"   Test RMSE: {best_result['Test_RMSE']:.2f} kJ/kg")
print(f"   CV MAE: {best_result['CV_MAE']:.2f} ± {best_result['CV_Std']:.2f} kJ/kg")
print(f"   Accuracy: {100 - (best_result['Test_MAE']/y.mean())*100:.2f}%")

print(f"\n📈 TOP 3 MODELS:")
for i, (_, row) in enumerate(results_df.head(3).iterrows(), 1):
    print(f"   {i}. {row['Model']}: MAE {row['Test_MAE']:.2f} kJ/kg, R² {row['Test_R2']:.4f}")

print(f"\n📁 FILES GENERATED:")
print(f"   • learning_curves_nk.png - Learning curves untuk top models")
print(f"   • test_charts_actual_vs_predicted.png - Actual vs Predicted charts")
print(f"   • comprehensive_nk_analysis.png - Comprehensive analysis")
print(f"   • nk_regression_results.csv - Hasil evaluasi semua model")
print(f"   • nk_predictions_best_model.csv - Prediksi model terbaik")

print(f"\n✅ KESIMPULAN:")
print(f"   Model {best_model_name} memberikan performa terbaik dengan akurasi {100 - (best_result['Test_MAE']/y.mean())*100:.2f}%")
print(f"   MAE {best_result['Test_MAE']:.2f} kJ/kg menunjukkan error rata-rata yang rendah")
print(f"   R² {best_result['Test_R2']:.4f} menunjukkan model dapat menjelaskan {best_result['Test_R2']*100:.1f}% variasi data")

print("\n" + "="*60)
print("ANALISIS SELESAI - SEMUA GRAFIK DAN CHART TELAH DIBUAT!")
print("="*60)
