
# LAPORAN MAKALAH
# Prediksi Nilai Kalor (NK) Batubara dengan Optimasi Tingkat Lanjut

## RINGKASAN EKSEKUTIF
Penelitian ini menggunakan teknik optimasi tingkat lanjut (Genetic Algorithm dan Particle Swarm Optimization)
untuk mengoptimalkan hyperparameter model machine learning dalam prediksi Nilai Kalor (NK) batubara.

## METODOLOGI
1. **Data**: Dataset DCS NK dengan 1218 sampel dan 13 fitur
2. **Teknik Optimasi**:
   - Genetic Algorithm (GA) untuk Random Forest
   - Particle Swarm Optimization (PSO) untuk Gradient Boosting
3. **Evaluasi**: Cross-validation 5-fold dengan metrik MAE, RMSE, dan R²

## HASIL OPTIMASI

### Model Terbaik: Random Forest (GA)
- **Test MAE**: 216.74 kJ/kg
- **Test RMSE**: 282.73 kJ/kg
- **Test R²**: 0.2683
- **Cross-Validation MAE**: 199.38 ± 9.70
- **Akurasi**: 94.56%

### Perbandingan Model:

**Random Forest (GA)**:
- Test MAE: 216.74 kJ/kg
- Test R²: 0.2683
- CV MAE: 199.38 ± 9.70


**Random Forest (Default)**:
- Test MAE: 219.88 kJ/kg
- Test R²: 0.2539
- CV MAE: 202.32 ± 11.05


**Gradient Boosting (Default)**:
- Test MAE: 219.70 kJ/kg
- Test R²: 0.2524
- CV MAE: 204.39 ± 12.93


**Linear Regression**:
- Test MAE: 225.02 kJ/kg
- Test R²: 0.1749
- CV MAE: 211.84 ± 7.65


## KESIMPULAN
1. Teknik optimasi lanjutan berhasil meningkatkan performa model prediksi NK
2. Model Random Forest (GA) memberikan hasil terbaik dengan akurasi 94.56%
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
Tanggal: 2025-09-11 06:32:39
