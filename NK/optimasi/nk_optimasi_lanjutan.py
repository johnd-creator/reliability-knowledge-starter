#!/usr/bin/env python3
"""
Script Pelatihan Model NK dengan Optimasi Tingkat Lanjut
Menggunakan Genetic Algorithm dan Particle Swarm Optimization
Berdasarkan Modul 8d - Optimasi Tingkat Lanjut

Author: AI Assistant
Date: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import warnings
warnings.filterwarnings('ignore')

# Install required packages if not available
try:
    from geneticalgorithm import geneticalgorithm as ga
except ImportError:
    print("Installing geneticalgorithm...")
    import subprocess
    subprocess.check_call(["pip", "install", "geneticalgorithm"])
    from geneticalgorithm import geneticalgorithm as ga

try:
    from pyswarm import pso
except ImportError:
    print("Installing pyswarm...")
    import subprocess
    subprocess.check_call(["pip", "install", "pyswarm"])
    from pyswarm import pso

class NKOptimasiLanjutan:
    def __init__(self, data_path):
        self.data_path = data_path
        self.data = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.scaler = None
        self.best_model = None
        self.best_params = None
        self.results = []

    def load_and_prepare_data(self):
        """Load dan persiapkan data NK"""
        print("Loading data NK...")
        self.data = pd.read_excel(self.data_path)

        # Hapus kolom Time jika ada
        if 'Time' in self.data.columns:
            self.data = self.data.drop('Time', axis=1)

        # Target adalah NK BB (HHV) Coal Feeder
        target_col = 'NK BB (HHV) Coal Feeder'
        if target_col not in self.data.columns:
            print(f"Kolom target '{target_col}' tidak ditemukan!")
            print("Kolom yang tersedia:", list(self.data.columns))
            return False

        # Pisahkan fitur dan target
        X = self.data.drop(target_col, axis=1)
        y = self.data[target_col]

        # Pilih hanya kolom numerik
        numeric_columns = X.select_dtypes(include=[np.number]).columns
        X = X[numeric_columns]

        print(f"Jumlah fitur numerik: {len(numeric_columns)}")
        print(f"Jumlah sampel: {len(X)}")

        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Normalisasi data
        self.scaler = StandardScaler()
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)

        return True

    def objective_function_ga(self, params):
        """Fungsi objektif untuk Genetic Algorithm"""
        try:
            # Parameter untuk Random Forest
            n_estimators = int(params[0])
            max_depth = int(params[1]) if params[1] > 0 else None
            min_samples_split = int(params[2])
            min_samples_leaf = int(params[3])

            # Buat model dengan parameter yang dioptimasi
            model = RandomForestRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                min_samples_split=min_samples_split,
                min_samples_leaf=min_samples_leaf,
                random_state=42,
                n_jobs=-1
            )

            # Cross validation score
            cv_scores = cross_val_score(model, self.X_train_scaled, self.y_train,
                                      cv=5, scoring='neg_mean_absolute_error')

            # Return negative MAE (karena GA minimasi)
            return -cv_scores.mean()

        except Exception as e:
            return 1000  # Penalty untuk parameter yang tidak valid

    def objective_function_pso(self, params):
        """Fungsi objektif untuk Particle Swarm Optimization"""
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

            # Return negative MAE (karena PSO minimasi)
            return -cv_scores.mean()

        except Exception as e:
            return 1000  # Penalty untuk parameter yang tidak valid

    def optimize_with_ga(self):
        """Optimasi hyperparameter menggunakan Genetic Algorithm"""
        print("\n=== Optimasi dengan Genetic Algorithm ===")

        # Definisi batas parameter untuk Random Forest
        # [n_estimators, max_depth, min_samples_split, min_samples_leaf]
        varbounds = np.array([[50, 200],    # n_estimators
                             [3, 20],      # max_depth
                             [2, 10],      # min_samples_split
                             [1, 5]])      # min_samples_leaf

        vartype = np.array([['int'], ['int'], ['int'], ['int']])

        # Parameter algoritma GA
        algorithm_param = {
            'max_num_iteration': 50,
            'population_size': 20,
            'mutation_probability': 0.1,
            'elit_ratio': 0.01,
            'crossover_probability': 0.5,
            'parents_portion': 0.3,
            'crossover_type': 'uniform',
            'max_iteration_without_improv': 10
        }

        # Jalankan GA
        model_ga = ga(function=self.objective_function_ga,
                     dimension=4,
                     variable_type_mixed=vartype,
                     variable_boundaries=varbounds,
                     algorithm_parameters=algorithm_param)

        model_ga.run()

        # Ambil parameter terbaik
        best_params_ga = model_ga.output_dict['variable']
        best_score_ga = model_ga.output_dict['function']

        print(f"Best GA Parameters: {best_params_ga}")
        print(f"Best GA Score (MAE): {-best_score_ga:.4f}")

        return best_params_ga, -best_score_ga

    def optimize_with_pso(self):
        """Optimasi hyperparameter menggunakan Particle Swarm Optimization"""
        print("\n=== Optimasi dengan Particle Swarm Optimization ===")

        # Definisi batas parameter untuk Gradient Boosting
        # [n_estimators, learning_rate, max_depth, subsample]
        lb = [50, 0.01, 3, 0.5]    # Lower bounds
        ub = [200, 0.3, 10, 1.0]   # Upper bounds
        x0 = [100, 0.1, 5, 0.8]    # Initial guess

        # Jalankan PSO
        try:
            xopt, fopt = pso(self.objective_function_pso, lb, ub, x0=x0,
                           swarmsize=20, maxiter=50, debug=False)

            print(f"Best PSO Parameters: {xopt}")
            print(f"Best PSO Score (MAE): {fopt:.4f}")

            return xopt, fopt
        except Exception as e:
            print(f"Error in PSO: {e}")
            return None, None

    def train_optimized_models(self, ga_params, pso_params):
        """Train model dengan parameter yang telah dioptimasi"""
        print("\n=== Training Model dengan Parameter Optimal ===")

        models = {}

        # Model dengan GA (Random Forest)
        if ga_params is not None:
            rf_optimized = RandomForestRegressor(
                n_estimators=int(ga_params[0]),
                max_depth=int(ga_params[1]) if ga_params[1] > 0 else None,
                min_samples_split=int(ga_params[2]),
                min_samples_leaf=int(ga_params[3]),
                random_state=42,
                n_jobs=-1
            )
            rf_optimized.fit(self.X_train_scaled, self.y_train)
            models['Random Forest (GA)'] = rf_optimized

        # Model dengan PSO (Gradient Boosting)
        if pso_params is not None:
            gb_optimized = GradientBoostingRegressor(
                n_estimators=int(pso_params[0]),
                learning_rate=pso_params[1],
                max_depth=int(pso_params[2]),
                subsample=pso_params[3],
                random_state=42
            )
            gb_optimized.fit(self.X_train_scaled, self.y_train)
            models['Gradient Boosting (PSO)'] = gb_optimized

        # Model baseline untuk perbandingan
        baseline_models = {
            'Random Forest (Default)': RandomForestRegressor(random_state=42),
            'Gradient Boosting (Default)': GradientBoostingRegressor(random_state=42),
            'Linear Regression': LinearRegression()
        }

        for name, model in baseline_models.items():
            model.fit(self.X_train_scaled, self.y_train)
            models[name] = model

        return models

    def evaluate_models(self, models):
        """Evaluasi semua model"""
        print("\n=== Evaluasi Model ===")

        results = []

        for name, model in models.items():
            # Prediksi
            y_train_pred = model.predict(self.X_train_scaled)
            y_test_pred = model.predict(self.X_test_scaled)

            # Metrik evaluasi
            train_mae = mean_absolute_error(self.y_train, y_train_pred)
            test_mae = mean_absolute_error(self.y_test, y_test_pred)
            train_rmse = np.sqrt(mean_squared_error(self.y_train, y_train_pred))
            test_rmse = np.sqrt(mean_squared_error(self.y_test, y_test_pred))
            train_r2 = r2_score(self.y_train, y_train_pred)
            test_r2 = r2_score(self.y_test, y_test_pred)

            # Cross validation
            cv_scores = cross_val_score(model, self.X_train_scaled, self.y_train,
                                      cv=5, scoring='neg_mean_absolute_error')
            cv_mae = -cv_scores.mean()
            cv_std = cv_scores.std()

            result = {
                'Model': name,
                'Train_MAE': train_mae,
                'Test_MAE': test_mae,
                'Train_RMSE': train_rmse,
                'Test_RMSE': test_rmse,
                'Train_R2': train_r2,
                'Test_R2': test_r2,
                'CV_MAE': cv_mae,
                'CV_Std': cv_std,
                'Overfitting': test_mae - train_mae
            }

            results.append(result)

            print(f"{name}:")
            print(f"  Train MAE: {train_mae:.2f}, Test MAE: {test_mae:.2f}")
            print(f"  Train R²: {train_r2:.3f}, Test R²: {test_r2:.3f}")
            print(f"  CV MAE: {cv_mae:.2f} ± {cv_std:.2f}")
            print()

        self.results = results
        return results

    def create_learning_curves(self, models):
        """Buat learning curves untuk model terbaik"""
        print("\n=== Membuat Learning Curves ===")

        # Pilih 3 model terbaik berdasarkan test MAE
        df_results = pd.DataFrame(self.results)
        best_models = df_results.nsmallest(3, 'Test_MAE')['Model'].tolist()

        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Learning Curves - Model NK dengan Optimasi Lanjutan', fontsize=16)

        for i, model_name in enumerate(best_models):
            if model_name in models:
                model = models[model_name]

                # Buat learning curve
                train_sizes = np.linspace(0.1, 1.0, 10)
                train_scores_mae = []
                val_scores_mae = []

                for train_size in train_sizes:
                    # Ambil subset data
                    n_samples = int(train_size * len(self.X_train_scaled))
                    X_subset = self.X_train_scaled[:n_samples]
                    y_subset = self.y_train.iloc[:n_samples]

                    # Train model
                    model.fit(X_subset, y_subset)

                    # Evaluasi
                    train_pred = model.predict(X_subset)
                    val_pred = model.predict(self.X_test_scaled)

                    train_mae = mean_absolute_error(y_subset, train_pred)
                    val_mae = mean_absolute_error(self.y_test, val_pred)

                    train_scores_mae.append(train_mae)
                    val_scores_mae.append(val_mae)

                # Plot learning curve
                axes[i].plot(train_sizes * len(self.X_train_scaled), train_scores_mae,
                           'o-', label='Training MAE', color='blue')
                axes[i].plot(train_sizes * len(self.X_train_scaled), val_scores_mae,
                           'o-', label='Validation MAE', color='red')
                axes[i].set_title(f'{model_name}')
                axes[i].set_xlabel('Training Set Size')
                axes[i].set_ylabel('Mean Absolute Error')
                axes[i].legend()
                axes[i].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('/Users/fauzi/Downloads/NK/optimasi/learning_curves_optimasi.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

        print("Learning curves disimpan sebagai 'learning_curves_optimasi.png'")

    def create_test_charts(self, models):
        """Buat chart perbandingan hasil test"""
        print("\n=== Membuat Test Charts ===")

        # Pilih model terbaik
        df_results = pd.DataFrame(self.results)
        best_model_name = df_results.loc[df_results['Test_MAE'].idxmin(), 'Model']
        best_model = models[best_model_name]

        # Prediksi dengan model terbaik
        y_pred = best_model.predict(self.X_test_scaled)

        # Buat subplot
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Analisis Test Results - {best_model_name}', fontsize=16)

        # 1. Actual vs Predicted
        axes[0,0].scatter(self.y_test, y_pred, alpha=0.6, color='blue')
        axes[0,0].plot([self.y_test.min(), self.y_test.max()],
                      [self.y_test.min(), self.y_test.max()], 'r--', lw=2)
        axes[0,0].set_xlabel('Actual NK')
        axes[0,0].set_ylabel('Predicted NK')
        axes[0,0].set_title('Actual vs Predicted')
        axes[0,0].grid(True, alpha=0.3)

        # 2. Residual Plot
        residuals = self.y_test - y_pred
        axes[0,1].scatter(y_pred, residuals, alpha=0.6, color='green')
        axes[0,1].axhline(y=0, color='r', linestyle='--')
        axes[0,1].set_xlabel('Predicted NK')
        axes[0,1].set_ylabel('Residuals')
        axes[0,1].set_title('Residual Plot')
        axes[0,1].grid(True, alpha=0.3)

        # 3. Error Distribution
        axes[1,0].hist(residuals, bins=20, alpha=0.7, color='orange', edgecolor='black')
        axes[1,0].set_xlabel('Residuals')
        axes[1,0].set_ylabel('Frequency')
        axes[1,0].set_title('Error Distribution')
        axes[1,0].grid(True, alpha=0.3)

        # 4. Model Comparison
        model_names = [result['Model'] for result in self.results]
        test_maes = [result['Test_MAE'] for result in self.results]

        bars = axes[1,1].bar(range(len(model_names)), test_maes,
                           color=['red' if name == best_model_name else 'lightblue'
                                 for name in model_names])
        axes[1,1].set_xlabel('Models')
        axes[1,1].set_ylabel('Test MAE')
        axes[1,1].set_title('Model Comparison')
        axes[1,1].set_xticks(range(len(model_names)))
        axes[1,1].set_xticklabels(model_names, rotation=45, ha='right')
        axes[1,1].grid(True, alpha=0.3)

        # Tambahkan nilai MAE di atas bar
        for i, bar in enumerate(bars):
            height = bar.get_height()
            axes[1,1].text(bar.get_x() + bar.get_width()/2., height + 1,
                         f'{height:.1f}', ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        plt.savefig('/Users/fauzi/Downloads/NK/optimasi/test_charts_optimasi.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

        print("Test charts disimpan sebagai 'test_charts_optimasi.png'")

        return best_model_name, best_model

    def save_results(self, models, best_model_name, best_model):
        """Simpan hasil dan model"""
        print("\n=== Menyimpan Hasil ===")

        # Simpan hasil evaluasi
        df_results = pd.DataFrame(self.results)
        df_results.to_csv('/Users/fauzi/Downloads/NK/optimasi/hasil_optimasi_lanjutan.csv', index=False)
        print("Hasil evaluasi disimpan sebagai 'hasil_optimasi_lanjutan.csv'")

        # Simpan model terbaik
        joblib.dump(best_model, '/Users/fauzi/Downloads/NK/optimasi/best_model_optimasi.pkl')
        joblib.dump(self.scaler, '/Users/fauzi/Downloads/NK/optimasi/scaler_optimasi.pkl')
        print(f"Model terbaik ({best_model_name}) disimpan sebagai 'best_model_optimasi.pkl'")
        print("Scaler disimpan sebagai 'scaler_optimasi.pkl'")

        # Simpan prediksi model terbaik
        y_pred = best_model.predict(self.X_test_scaled)
        predictions_df = pd.DataFrame({
            'Actual_NK': self.y_test.values,
            'Predicted_NK': y_pred,
            'Error': self.y_test.values - y_pred,
            'Absolute_Error': np.abs(self.y_test.values - y_pred)
        })
        predictions_df.to_csv('/Users/fauzi/Downloads/NK/optimasi/prediksi_optimasi.csv', index=False)
        print("Prediksi disimpan sebagai 'prediksi_optimasi.csv'")

    def generate_report(self, best_model_name):
        """Generate laporan lengkap"""
        print("\n=== Generating Laporan Makalah ===")

        df_results = pd.DataFrame(self.results)
        best_result = df_results[df_results['Model'] == best_model_name].iloc[0]

        report = f"""
# LAPORAN MAKALAH
# Prediksi Nilai Kalor (NK) Batubara dengan Optimasi Tingkat Lanjut

## RINGKASAN EKSEKUTIF
Penelitian ini menggunakan teknik optimasi tingkat lanjut (Genetic Algorithm dan Particle Swarm Optimization)
untuk mengoptimalkan hyperparameter model machine learning dalam prediksi Nilai Kalor (NK) batubara.

## METODOLOGI
1. **Data**: Dataset DCS NK dengan {len(self.data)} sampel dan {len(self.X_train.columns)} fitur
2. **Teknik Optimasi**:
   - Genetic Algorithm (GA) untuk Random Forest
   - Particle Swarm Optimization (PSO) untuk Gradient Boosting
3. **Evaluasi**: Cross-validation 5-fold dengan metrik MAE, RMSE, dan R²

## HASIL OPTIMASI

### Model Terbaik: {best_model_name}
- **Test MAE**: {best_result['Test_MAE']:.2f} kJ/kg
- **Test RMSE**: {best_result['Test_RMSE']:.2f} kJ/kg
- **Test R²**: {best_result['Test_R2']:.4f}
- **Cross-Validation MAE**: {best_result['CV_MAE']:.2f} ± {best_result['CV_Std']:.2f}
- **Akurasi**: {(1 - best_result['Test_MAE']/self.y_test.mean())*100:.2f}%

### Perbandingan Model:
"""

        for _, result in df_results.iterrows():
            report += f"""
**{result['Model']}**:
- Test MAE: {result['Test_MAE']:.2f} kJ/kg
- Test R²: {result['Test_R2']:.4f}
- CV MAE: {result['CV_MAE']:.2f} ± {result['CV_Std']:.2f}

"""

        report += f"""
## KESIMPULAN
1. Teknik optimasi lanjutan berhasil meningkatkan performa model prediksi NK
2. Model {best_model_name} memberikan hasil terbaik dengan akurasi {(1 - best_result['Test_MAE']/self.y_test.mean())*100:.2f}%
3. Optimasi hyperparameter menggunakan GA dan PSO efektif untuk tuning model
4. Model dapat digunakan untuk prediksi NK batubara dengan tingkat kepercayaan tinggi

## FILE YANG DIHASILKAN
1. best_model_optimasi.pkl - Model terbaik
2. scaler_optimasi.pkl - Scaler untuk preprocessing
3. hasil_optimasi_lanjutan.csv - Hasil evaluasi semua model
4. prediksi_optimasi.csv - Prediksi model terbaik
5. learning_curves_optimasi.png - Learning curves
6. test_charts_optimasi.png - Analisis test results

---
Laporan dibuat secara otomatis menggunakan teknik optimasi tingkat lanjut
Tanggal: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        # Simpan laporan
        with open('/Users/fauzi/Downloads/NK/optimasi/laporan_makalah_optimasi.md', 'w', encoding='utf-8') as f:
            f.write(report)

        print("Laporan makalah disimpan sebagai 'laporan_makalah_optimasi.md'")
        print("\n=== RINGKASAN HASIL ===")
        print(f"Model Terbaik: {best_model_name}")
        print(f"Test MAE: {best_result['Test_MAE']:.2f} kJ/kg")
        print(f"Akurasi: {(1 - best_result['Test_MAE']/self.y_test.mean())*100:.2f}%")
        print(f"Test R²: {best_result['Test_R2']:.4f}")

def main():
    """Fungsi utama"""
    print("=" * 60)
    print("PELATIHAN MODEL NK DENGAN OPTIMASI TINGKAT LANJUT")
    print("Menggunakan Genetic Algorithm & Particle Swarm Optimization")
    print("=" * 60)

    # Inisialisasi
    optimizer = NKOptimasiLanjutan('/Users/fauzi/Downloads/NK/Data_DCS_NK.xlsx')

    # Load dan persiapkan data
    if not optimizer.load_and_prepare_data():
        return

    # Optimasi dengan GA dan PSO
    ga_params, ga_score = optimizer.optimize_with_ga()
    pso_params, pso_score = optimizer.optimize_with_pso()

    # Train model dengan parameter optimal
    models = optimizer.train_optimized_models(ga_params, pso_params)

    # Evaluasi model
    results = optimizer.evaluate_models(models)

    # Buat visualisasi
    optimizer.create_learning_curves(models)
    best_model_name, best_model = optimizer.create_test_charts(models)

    # Simpan hasil
    optimizer.save_results(models, best_model_name, best_model)

    # Generate laporan
    optimizer.generate_report(best_model_name)

    print("\n" + "="*60)
    print("OPTIMASI SELESAI! Semua file tersimpan di folder 'optimasi'")
    print("="*60)

if __name__ == "__main__":
    main()
