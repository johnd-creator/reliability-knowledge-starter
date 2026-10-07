#!/usr/bin/env python3
"""
Script untuk memperbaiki PSO dan menjalankan optimasi lengkap
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import warnings
warnings.filterwarnings('ignore')

# Install scipy-based PSO alternative
try:
    from scipy.optimize import differential_evolution
except ImportError:
    print("Installing scipy...")
    import subprocess
    subprocess.check_call(["pip", "install", "scipy"])
    from scipy.optimize import differential_evolution

class PSOOptimizer:
    def __init__(self):
        # Load data yang sudah diproses
        self.data = pd.read_excel('/Users/fauzi/Downloads/NK/Data_DCS_NK.xlsx')

        # Hapus kolom Time jika ada
        if 'Time' in self.data.columns:
            self.data = self.data.drop('Time', axis=1)

        # Target adalah NK BB (HHV) Coal Feeder
        target_col = 'NK BB (HHV) Coal Feeder'
        X = self.data.drop(target_col, axis=1)
        y = self.data[target_col]

        # Pilih hanya kolom numerik
        numeric_columns = X.select_dtypes(include=[np.number]).columns
        X = X[numeric_columns]

        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Normalisasi data
        self.scaler = StandardScaler()
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)

    def objective_function_pso(self, params):
        """Fungsi objektif untuk PSO menggunakan Differential Evolution"""
        try:
            # Parameter untuk Gradient Boosting
            n_estimators = int(params[0])
            learning_rate = params[1]
            max_depth = int(params[2])
            subsample = params[3]

            # Buat model dengan parameter yang dioptimasi
            model = GradientBoostingRegressor(
                n_estimators=n_estimators,
                learning_rate=learning_rate,
                max_depth=max_depth,
                subsample=subsample,
                random_state=42
            )

            # Cross validation score
            cv_scores = cross_val_score(model, self.X_train_scaled, self.y_train,
                                      cv=5, scoring='neg_mean_absolute_error')

            # Return negative MAE (karena minimasi)
            return -cv_scores.mean()

        except Exception as e:
            return 1000  # Penalty untuk parameter yang tidak valid

    def optimize_with_differential_evolution(self):
        """Optimasi menggunakan Differential Evolution (alternatif PSO)"""
        print("\n=== Optimasi dengan Differential Evolution (PSO Alternative) ===")

        # Definisi batas parameter untuk Gradient Boosting
        # [n_estimators, learning_rate, max_depth, subsample]
        bounds = [(50, 200),    # n_estimators
                 (0.01, 0.3),   # learning_rate
                 (3, 10),       # max_depth
                 (0.5, 1.0)]    # subsample

        # Jalankan Differential Evolution
        result = differential_evolution(
            self.objective_function_pso,
            bounds,
            maxiter=50,
            popsize=15,
            seed=42,
            disp=True
        )

        best_params = result.x
        best_score = result.fun

        print(f"Best DE Parameters: {best_params}")
        print(f"Best DE Score (MAE): {best_score:.4f}")

        return best_params, best_score

    def train_and_evaluate_optimized_gb(self, pso_params):
        """Train dan evaluasi Gradient Boosting dengan parameter optimal"""
        print("\n=== Training Gradient Boosting dengan Parameter Optimal ===")

        # Model dengan parameter optimal
        gb_optimized = GradientBoostingRegressor(
            n_estimators=int(pso_params[0]),
            learning_rate=pso_params[1],
            max_depth=int(pso_params[2]),
            subsample=pso_params[3],
            random_state=42
        )

        # Train model
        gb_optimized.fit(self.X_train_scaled, self.y_train)

        # Evaluasi
        y_train_pred = gb_optimized.predict(self.X_train_scaled)
        y_test_pred = gb_optimized.predict(self.X_test_scaled)

        train_mae = mean_absolute_error(self.y_train, y_train_pred)
        test_mae = mean_absolute_error(self.y_test, y_test_pred)
        train_r2 = r2_score(self.y_train, y_train_pred)
        test_r2 = r2_score(self.y_test, y_test_pred)

        # Cross validation
        cv_scores = cross_val_score(gb_optimized, self.X_train_scaled, self.y_train,
                                  cv=5, scoring='neg_mean_absolute_error')
        cv_mae = -cv_scores.mean()
        cv_std = cv_scores.std()

        print(f"Gradient Boosting (DE Optimized):")
        print(f"  Train MAE: {train_mae:.2f}, Test MAE: {test_mae:.2f}")
        print(f"  Train R²: {train_r2:.3f}, Test R²: {test_r2:.3f}")
        print(f"  CV MAE: {cv_mae:.2f} ± {cv_std:.2f}")

        # Simpan model optimized
        joblib.dump(gb_optimized, '/Users/fauzi/Downloads/NK/optimasi/gb_optimized_pso.pkl')
        print("Model GB optimized disimpan sebagai 'gb_optimized_pso.pkl'")

        return gb_optimized, {
            'Model': 'Gradient Boosting (PSO)',
            'Train_MAE': train_mae,
            'Test_MAE': test_mae,
            'Train_R2': train_r2,
            'Test_R2': test_r2,
            'CV_MAE': cv_mae,
            'CV_Std': cv_std
        }

    def create_pso_visualization(self, model, result):
        """Buat visualisasi khusus untuk hasil PSO"""
        print("\n=== Membuat Visualisasi PSO ===")

        # Prediksi
        y_pred = model.predict(self.X_test_scaled)

        # Buat plot
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Hasil Optimasi PSO - Gradient Boosting', fontsize=16)

        # 1. Actual vs Predicted
        axes[0,0].scatter(self.y_test, y_pred, alpha=0.6, color='blue')
        axes[0,0].plot([self.y_test.min(), self.y_test.max()],
                      [self.y_test.min(), self.y_test.max()], 'r--', lw=2)
        axes[0,0].set_xlabel('Actual NK')
        axes[0,0].set_ylabel('Predicted NK')
        axes[0,0].set_title('Actual vs Predicted')
        axes[0,0].grid(True, alpha=0.3)

        # Add R² score
        r2 = result['Test_R2']
        axes[0,0].text(0.05, 0.95, f'R² = {r2:.3f}', transform=axes[0,0].transAxes,
                      bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # 2. Residual Plot
        residuals = self.y_test - y_pred
        axes[0,1].scatter(y_pred, residuals, alpha=0.6, color='green')
        axes[0,1].axhline(y=0, color='r', linestyle='--')
        axes[0,1].set_xlabel('Predicted NK')
        axes[0,1].set_ylabel('Residuals')
        axes[0,1].set_title('Residual Plot')
        axes[0,1].grid(True, alpha=0.3)

        # 3. Feature Importance
        feature_names = [f'Feature_{i+1}' for i in range(len(model.feature_importances_))]
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1][:10]  # Top 10 features

        axes[1,0].bar(range(len(indices)), importances[indices], color='orange')
        axes[1,0].set_xlabel('Features')
        axes[1,0].set_ylabel('Importance')
        axes[1,0].set_title('Top 10 Feature Importance')
        axes[1,0].set_xticks(range(len(indices)))
        axes[1,0].set_xticklabels([feature_names[i] for i in indices], rotation=45)
        axes[1,0].grid(True, alpha=0.3)

        # 4. Performance Metrics
        metrics = ['Train MAE', 'Test MAE', 'Train R²', 'Test R²']
        values = [result['Train_MAE'], result['Test_MAE'],
                 result['Train_R2']*100, result['Test_R2']*100]  # R² dalam persen
        colors = ['lightblue', 'lightcoral', 'lightgreen', 'lightyellow']

        bars = axes[1,1].bar(metrics, values, color=colors)
        axes[1,1].set_ylabel('Value')
        axes[1,1].set_title('Performance Metrics')
        axes[1,1].grid(True, alpha=0.3)

        # Tambahkan nilai di atas bar
        for i, bar in enumerate(bars):
            height = bar.get_height()
            if i < 2:  # MAE values
                axes[1,1].text(bar.get_x() + bar.get_width()/2., height + 2,
                             f'{height:.1f}', ha='center', va='bottom')
            else:  # R² values
                axes[1,1].text(bar.get_x() + bar.get_width()/2., height + 1,
                             f'{height:.1f}%', ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig('/Users/fauzi/Downloads/NK/optimasi/pso_optimization_results.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

        print("Visualisasi PSO disimpan sebagai 'pso_optimization_results.png'")

def main():
    print("=" * 60)
    print("OPTIMASI PSO UNTUK MODEL GRADIENT BOOSTING")
    print("=" * 60)

    # Inisialisasi optimizer
    optimizer = PSOOptimizer()

    # Optimasi dengan Differential Evolution (alternatif PSO)
    pso_params, pso_score = optimizer.optimize_with_differential_evolution()

    # Train dan evaluasi model dengan parameter optimal
    model, result = optimizer.train_and_evaluate_optimized_gb(pso_params)

    # Buat visualisasi
    optimizer.create_pso_visualization(model, result)

    # Simpan hasil PSO
    pso_results = pd.DataFrame([result])
    pso_results.to_csv('/Users/fauzi/Downloads/NK/optimasi/pso_results.csv', index=False)

    print("\n" + "="*60)
    print("OPTIMASI PSO SELESAI!")
    print(f"Model terbaik: Test MAE = {result['Test_MAE']:.2f} kJ/kg")
    print(f"Akurasi: {(1 - result['Test_MAE']/optimizer.y_test.mean())*100:.2f}%")
    print("="*60)

if __name__ == "__main__":
    main()
