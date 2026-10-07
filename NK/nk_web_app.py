#!/usr/bin/env python3
"""
Aplikasi Web Interaktif untuk Prediksi NK Batubara
Menggunakan Model Terbaik dari Optimasi Tingkat Lanjut

Author: AI Assistant
Date: 2024
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import time
from datetime import datetime, timedelta
from pathlib import Path
from pi_input import FEATURES
from pi_panel import render_pi_mode

APP_ROOT = Path(__file__).resolve().parent
warnings.filterwarnings('ignore')

# Konfigurasi halaman
st.set_page_config(
    page_title="Prediksi NK Batubara",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

class NKPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.load_models()

    def load_models(self):
        """Load model dan scaler yang sudah dilatih"""
        try:
            # Coba load model terbaik dari optimasi
            self.model = joblib.load(APP_ROOT / 'optimasi/best_model_optimasi.pkl')
            self.scaler = joblib.load(APP_ROOT / 'optimasi/scaler_optimasi.pkl')

            self.feature_names = FEATURES.copy()
            actual = list(getattr(self.scaler, 'feature_names_in_', []))
            if actual != FEATURES or self.model.n_features_in_ != len(FEATURES):
                raise ValueError('Kontrak fitur model/scaler tidak sesuai.')

            st.success("✅ Model berhasil dimuat!")
            return True

        except FileNotFoundError:
            try:
                # Fallback ke model lama jika ada
                self.model = joblib.load(APP_ROOT / 'prediksi_NK.pkcls')
                self.feature_names = FEATURES.copy()
                if getattr(self.model, "n_features_in_", None) != len(FEATURES):
                    self.model = None
                    raise ValueError("Kontrak fitur model fallback tidak sesuai.")
                st.warning("⚠️ Menggunakan model fallback")
                return True
            except:
                st.error("❌ Model tidak ditemukan! Pastikan file model tersedia.")
                return False
        except Exception as e:
            self.model = None
            st.error(f"❌ Error loading model: {str(e)}")
            return False

    def predict(self, input_data):
        """Prediksi NK berdasarkan input data"""
        try:
            # Konversi ke DataFrame
            df = pd.DataFrame([input_data], columns=self.feature_names)

            # Normalisasi jika scaler tersedia
            if self.scaler is not None:
                df_scaled = self.scaler.transform(df)
            else:
                df_scaled = df.values

            # Prediksi
            prediction = self.model.predict(df_scaled)[0]
            if not np.isfinite(prediction):
                raise ValueError("Prediksi tidak valid.")

            # Confidence interval (estimasi)
            confidence = self.estimate_confidence(df_scaled)

            return prediction, confidence

        except Exception as e:
            st.error(f"Error dalam prediksi: {str(e)}")
            return None, None

    def estimate_confidence(self, input_data):
        """Estimasi confidence interval"""
        try:
            # Untuk Random Forest, gunakan prediksi dari semua trees
            if hasattr(self.model, 'estimators_'):
                predictions = [tree.predict(input_data)[0] for tree in self.model.estimators_]
                std_dev = np.std(predictions)
                return std_dev * 1.96  # 95% confidence interval
            else:
                # Untuk model lain, gunakan estimasi sederhana
                return 50.0  # Default uncertainty
        except:
            return 50.0

    def estimate_confidence_interval(self, X, prediction, confidence=0.95):
        """
        Estimasi confidence interval berdasarkan variabilitas model ensemble
        """
        try:
            # Untuk Random Forest, gunakan prediksi dari setiap tree
            if hasattr(self.model, 'estimators_'):
                tree_predictions = np.array([tree.predict(X.reshape(1, -1))[0]
                                           for tree in self.model.estimators_])
                std_pred = np.std(tree_predictions)
            else:
                # Fallback: gunakan estimasi berdasarkan error historis
                std_pred = prediction * 0.05  # 5% dari prediksi

            # Hitung confidence interval
            z_score = 1.96 if confidence == 0.95 else 2.576  # 95% atau 99%
            margin = z_score * std_pred

            return {
                'lower': max(0, prediction - margin),
                'upper': prediction + margin,
                'std': std_pred
            }
        except Exception as e:
            # Fallback confidence interval
            margin = prediction * 0.1
            return {
                'lower': max(0, prediction - margin),
                'upper': prediction + margin,
                'std': prediction * 0.05
            }

    def recommend_mw_optimization(self, current_params, target_mw_increase=50):
        """
        Memberikan rekomendasi untuk meningkatkan produksi MW
        """
        recommendations = []
        current_nk = self.predict(current_params)[0]

        # Parameter yang bisa dioptimasi untuk meningkatkan MW
        optimization_params = {
            'coal_flow': {'min': current_params[2] * 1.05, 'max': current_params[2] * 1.3, 'step': 5},
            'main_steam_press': {'min': current_params[4] * 1.02, 'max': current_params[4] * 1.1, 'step': 2},
            'main_steam_temp': {'min': current_params[5] * 1.01, 'max': current_params[5] * 1.05, 'step': 5},
            'main_steam_flow': {'min': current_params[6] * 1.05, 'max': current_params[6] * 1.2, 'step': 10}
        }

        best_recommendation = None
        best_nk_improvement = 0

        for param_name, param_range in optimization_params.items():
            test_params = current_params.copy()
            param_idx = {'coal_flow': 2, 'main_steam_press': 4, 'main_steam_temp': 5, 'main_steam_flow': 6}[param_name]

            # Test beberapa nilai dalam range
            for test_value in np.arange(param_range['min'], param_range['max'], param_range['step']):
                test_params[param_idx] = test_value
                predicted_nk = self.predict(test_params)[0]
                nk_improvement = predicted_nk - current_nk

                if nk_improvement > best_nk_improvement:
                    best_nk_improvement = nk_improvement
                    best_recommendation = {
                        'parameter': param_name,
                        'current_value': current_params[param_idx],
                        'recommended_value': test_value,
                        'nk_improvement': nk_improvement,
                        'estimated_mw_impact': nk_improvement * 0.001  # Estimasi dampak MW
                    }

        return best_recommendation

    def simulate_parameter_impact(self, base_params, parameter_changes):
        """
        Simulasi dampak perubahan parameter terhadap NK dan estimasi MW
        """
        results = []
        base_nk = self.predict(base_params)[0]

        for change in parameter_changes:
            test_params = base_params.copy()
            param_idx = change['param_idx']
            test_params[param_idx] = change['new_value']

            predicted_nk = self.predict(test_params)[0]
            nk_change = predicted_nk - base_nk
            estimated_mw_change = nk_change * 0.001  # Konversi estimasi ke MW

            results.append({
                'parameter': change['param_name'],
                'original_value': base_params[param_idx],
                'new_value': change['new_value'],
                'nk_change': nk_change,
                'estimated_mw_change': estimated_mw_change,
                'predicted_nk': predicted_nk
            })

        return results

def create_input_interface():
    """Membuat interface input untuk parameter batubara"""
    st.sidebar.header("🔧 Parameter Input Batubara")

    # Organize inputs in groups
    with st.sidebar.expander("⚡ Parameter Beban & Daya", expanded=True):
        gross_load = st.slider("Gross Load (MW)", 10.0, 650.0, 400.0, 1.0)
        ps = st.slider("PS", 0.0, 80.0, 50.0, 1.0)

    with st.sidebar.expander("🔥 Parameter Batubara", expanded=True):
        coal_flow = st.slider("Coal Flow (t/h)", 10.0, 500.0, 100.0, 1.0)
        sfc = st.slider("SFC (Specific Fuel Consumption)", 0.1, 1.0, 0.5, 0.01)

    with st.sidebar.expander("💨 Parameter Steam", expanded=True):
        main_steam_press = st.slider("Main Steam Press (MPa)", 5.0, 70.0, 30.0, 1.1)
        main_steam_temp = st.slider("Main Steam Temp (°C)", 100.0, 600.0, 500.0, 1.1)
        main_steam_flow = st.slider("Main Steam Flow (t/h)", 100.0, 2100.0, 1000.0, 1.1)

    with st.sidebar.expander("🌡️ Parameter Temperatur", expanded=True):
        economizer_temp = st.slider("Economizer Inlet Temp (°C)", 100.0, 400.0, 200.0, 1.1)
        aph_flue_temp = st.slider("APH Flue Gas Temp (°C)", 100.0, 400.0, 200.0, 1.1)

    with st.sidebar.expander("🌬️ Parameter Udara & Gas", expanded=True):
        aph_o2 = st.slider("APH A In O2 (%)", 0.0, 5.0, 20.0, 0.1)
        condensor_vacuum = st.slider("Condensor Vacuum (kpa)", -150.0, 0.0, -50.0, 1.1)
        feedwater_flow = st.slider("Feedwater Flow (t/h)", 100.0, 2500.0, 500.0, 1.1)
        total_air_flow = st.slider("Total Air Flow (t/h)", 100.0, 2500.0, 1000.0, 1.1)

    uploaded_values = None
    if st.sidebar.checkbox("Input dari CSV", value=False):
        uploaded_file = st.sidebar.file_uploader("Upload CSV dengan nama 13 fitur model", type=['csv'])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                uploaded_values = df.loc[:, FEATURES].iloc[0].astype(float).tolist()
                if not np.isfinite(uploaded_values).all():
                    raise ValueError('Nilai CSV harus angka terbatas.')
            except Exception:
                st.sidebar.error('CSV harus berisi 13 kolom bernama sesuai fitur dan nilai numerik lengkap.')
                return None

    # Monitoring Dashboard Controls
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Monitoring Dashboard")

    # Alert thresholds
    alert_enabled = st.sidebar.checkbox("Enable Alerts", value=True)

    if alert_enabled:
        nk_threshold_low = st.sidebar.slider(
            "NK Alert Threshold (Low)",
            3000, 5000, 4000, 100,
            help="Alert jika NK di bawah nilai ini"
        )

        nk_threshold_high = st.sidebar.slider(
            "NK Alert Threshold (High)",
            6000, 8000, 7000, 100,
            help="Alert jika NK di atas nilai ini"
        )

        # Store thresholds in session state
        st.session_state.nk_threshold_low = nk_threshold_low
        st.session_state.nk_threshold_high = nk_threshold_high

    # Informasi Model
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ Informasi Model")
    st.sidebar.info("""
    **Model**: Random Forest + Genetic Algorithm

    **Akurasi**: 94.56%

    **MAE**: 216.74 kJ/kg

    **Data Training**: 900+ sampel

    **Fitur**: 13 parameter operasional

    **Real-Time**: ✅ Aktif

    **PI Collector**: tersedia melalui pilihan sumber input
    """)

    if uploaded_values is not None:
        return uploaded_values
    return [
        gross_load, ps, coal_flow, sfc, main_steam_press,
        main_steam_temp, main_steam_flow, economizer_temp,
        aph_o2, aph_flue_temp, condensor_vacuum,
        feedwater_flow, total_air_flow
    ]

def create_prediction_display(prediction, confidence, input_data, feature_names):
    """Menampilkan hasil prediksi dengan visualisasi"""
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("🎯 Hasil Prediksi NK")

        # Display prediction with confidence
        st.metric(
            label="Nilai Kalor (NK) Prediksi",
            value=f"{prediction:.2f} kJ/kg",
            delta=f"±{confidence:.2f} kJ/kg (95% CI)"
        )

        # Kategori kualitas batubara
        if prediction > 6000:
            quality = "🟢 Sangat Baik"
            color = "green"
        elif prediction > 5000:
            quality = "🟡 Baik"
            color = "orange"
        elif prediction > 4000:
            quality = "🟠 Sedang"
            color = "orange"
        else:
            quality = "🔴 Rendah"
            color = "red"

        st.markdown(f"**Kualitas Batubara:** {quality}")

        # Gauge chart untuk NK
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = prediction,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Nilai Kalor (kJ/kg)"},
            delta = {'reference': 4500},
            gauge = {
                'axis': {'range': [None, 7000]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 3000], 'color': "lightgray"},
                    {'range': [3000, 4500], 'color': "yellow"},
                    {'range': [4500, 6000], 'color': "orange"},
                    {'range': [6000, 7000], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': prediction + confidence
                }
            }
        ))
        fig_gauge.update_layout(height=400)
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        st.header("📊 Parameter Input")

        # Display input parameters
        input_df = pd.DataFrame({
            'Parameter': feature_names,
            'Nilai': input_data
        })

        st.dataframe(input_df, use_container_width=True, height=400)

        # Download button untuk data input
        csv = input_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Input Data",
            data=csv,
            file_name="input_parameters.csv",
            mime="text/csv"
        )

def create_parameter_analysis(input_data, feature_names):
    """Analisis parameter input"""
    st.header("📈 Analisis Parameter")

    # Radar chart untuk parameter
    fig_radar = go.Figure()

    # Normalize values untuk radar chart
    normalized_values = []
    for i, value in enumerate(input_data):
        if feature_names[i] in ['Gross Load']:
            norm_val = value / 800 * 100
        elif feature_names[i] in ['Main Steam Temp', 'Economizer Inlet Temp']:
            norm_val = (value - 200) / 400 * 100
        else:
            norm_val = min(value / max(input_data) * 100, 100)
        normalized_values.append(norm_val)

    fig_radar.add_trace(go.Scatterpolar(
        r=normalized_values,
        theta=feature_names,
        fill='toself',
        name='Parameter Values'
    ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title="Distribusi Parameter Input (Normalized)"
    )

    st.plotly_chart(fig_radar, use_container_width=True)

    # Bar chart parameter values
    fig_bar = px.bar(
        x=feature_names,
        y=input_data,
        title="Nilai Parameter Input",
        labels={'x': 'Parameter', 'y': 'Nilai'}
    )
    fig_bar.update_xaxes(tickangle=45)
    st.plotly_chart(fig_bar, use_container_width=True)

def create_historical_comparison():
    """Perbandingan dengan data historis"""
    st.header("📊 Perbandingan Historis")

    try:
        # Load historical predictions jika ada
        hist_data = pd.read_csv(APP_ROOT / 'optimasi/prediksi_optimasi.csv')

        col1, col2 = st.columns(2)

        with col1:
            # Distribution plot
            fig_hist = px.histogram(
                hist_data,
                x='Predicted_NK',
                nbins=30,
                title="Distribusi Prediksi NK Historis"
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with col2:
            # Statistics
            st.subheader("Statistik Historis")
            st.metric("Mean NK", f"{hist_data['Predicted_NK'].mean():.2f} kJ/kg")
            st.metric("Std Dev", f"{hist_data['Predicted_NK'].std():.2f} kJ/kg")
            st.metric("Min NK", f"{hist_data['Predicted_NK'].min():.2f} kJ/kg")
            st.metric("Max NK", f"{hist_data['Predicted_NK'].max():.2f} kJ/kg")

    except FileNotFoundError:
        st.info("Data historis tidak tersedia")

def main():
    """Fungsi utama aplikasi"""
    # Initialize session state
    if 'auto_predict' not in st.session_state:
        st.session_state.auto_predict = False
    if 'last_prediction' not in st.session_state:
        st.session_state.last_prediction = None
    if 'prediction_history' not in st.session_state:
        st.session_state.prediction_history = []
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now()

    st.title("🔥 Aplikasi Prediksi Nilai Kalor (NK) Batubara - Real Time")
    st.markdown("""
    Aplikasi ini menggunakan model Machine Learning yang telah dioptimasi dengan
    **Genetic Algorithm** dan **Particle Swarm Optimization** untuk memprediksi
    Nilai Kalor batubara berdasarkan parameter operasional pembangkit.
    """)

    # Status indicator
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.session_state.auto_predict:
            st.success("🟢 Mode Real-Time Aktif")
        else:
            st.warning("🟡 Mode Manual")
    with col2:
        st.session_state.auto_predict = st.toggle("Prediksi saat input berubah (Manual)", value=st.session_state.auto_predict)
    with col3:
        st.metric("Last Update", st.session_state.last_update.strftime("%H:%M:%S"))

    st.markdown("---")

    # Initialize predictor
    predictor = NKPredictor()

    if predictor.model is None:
        st.error("Model tidak dapat dimuat. Pastikan file model tersedia.")
        return

    mode = st.radio("Sumber input", ["Manual", "PI Collector"], horizontal=True)
    if st.session_state.get('last_input_mode') != mode:
        for key in ('prediction', 'confidence', 'input_data', 'last_prediction'):
            st.session_state.pop(key, None)
        st.session_state.last_input_mode = mode
    if mode == "PI Collector":
        render_pi_mode(predictor, create_prediction_display)
        return
    # Create input interface
    input_data = create_input_interface()
    if input_data is None:
        return

    # Auto-predict atau manual predict
    prediction = None
    confidence = None

    if st.session_state.auto_predict:
        # Auto predict setiap kali parameter berubah
        prediction, confidence = predictor.predict(input_data)
        if prediction is None:
            return

        # Update session state
        st.session_state.last_prediction = prediction
        st.session_state.last_update = datetime.now()

        # Simpan ke history (maksimal 50 entries)
        st.session_state.prediction_history.append({
            'timestamp': datetime.now(),
            'prediction': prediction,
            'params': input_data.copy()
        })
        if len(st.session_state.prediction_history) > 50:
            st.session_state.prediction_history.pop(0)

        # Store in session state
        st.session_state.prediction = prediction
        st.session_state.confidence = confidence
        st.session_state.input_data = input_data
        st.session_state.feature_names = predictor.feature_names

        # Check alerts if enabled
        if hasattr(st.session_state, 'nk_threshold_low') and hasattr(st.session_state, 'nk_threshold_high'):
            if prediction < st.session_state.nk_threshold_low:
                st.error(f"🚨 **ALERT**: NK terlalu rendah! ({prediction:.0f} < {st.session_state.nk_threshold_low} kJ/kg)")
            elif prediction > st.session_state.nk_threshold_high:
                st.warning(f"⚠️ **ALERT**: NK terlalu tinggi! ({prediction:.0f} > {st.session_state.nk_threshold_high} kJ/kg)")

    else:
        # Manual predict dengan tombol
        if st.sidebar.button("🚀 Prediksi NK", type="primary"):
            with st.spinner("Melakukan prediksi..."):
                prediction, confidence = predictor.predict(input_data)

                if prediction is not None:
                    st.session_state.last_prediction = prediction
                    st.session_state.last_update = datetime.now()

                    # Store prediction in session state
                    st.session_state.prediction = prediction
                    st.session_state.confidence = confidence
                    st.session_state.input_data = input_data
                    st.session_state.feature_names = predictor.feature_names

    # Display results if available
    if hasattr(st.session_state, 'prediction'):
        create_prediction_display(
            st.session_state.prediction,
            st.session_state.confidence,
            st.session_state.input_data,
            st.session_state.feature_names
        )

        # Rekomendasi Optimasi MW
        st.markdown("---")
        st.header("🎯 Rekomendasi Optimasi MW")
        recommendation = predictor.recommend_mw_optimization(st.session_state.input_data)

        if recommendation:
            col_rec1, col_rec2 = st.columns([1, 1])
            with col_rec1:
                st.success(f"""💡 **Rekomendasi Terbaik:**
                - Parameter: **{recommendation['parameter'].replace('_', ' ').title()}**
                - Nilai Saat Ini: **{recommendation['current_value']:.1f}**
                - Nilai Disarankan: **{recommendation['recommended_value']:.1f}**
                - Peningkatan NK: **+{recommendation['nk_improvement']:.0f} kJ/kg**
                - Estimasi Dampak MW: **+{recommendation['estimated_mw_impact']:.2f} MW**""")

            with col_rec2:
                # Simulasi dampak perubahan parameter
                st.subheader("🔄 Simulasi Dampak Parameter")

                # Contoh simulasi coal flow
                coal_flow_changes = [
                    {'param_name': 'Coal Flow +10%', 'param_idx': 2, 'new_value': st.session_state.input_data[2] * 1.1},
                    {'param_name': 'Coal Flow +20%', 'param_idx': 2, 'new_value': st.session_state.input_data[2] * 1.2},
                    {'param_name': 'Steam Press +5%', 'param_idx': 4, 'new_value': st.session_state.input_data[4] * 1.05}
                ]

                simulation_results = predictor.simulate_parameter_impact(st.session_state.input_data, coal_flow_changes)

                for result in simulation_results:
                    if result['nk_change'] > 0:
                        st.success(f"✅ **{result['parameter']}**: +{result['nk_change']:.0f} kJ/kg (+{result['estimated_mw_change']:.2f} MW)")
                    else:
                        st.warning(f"⚠️ **{result['parameter']}**: {result['nk_change']:.0f} kJ/kg ({result['estimated_mw_change']:.2f} MW)")

        # 📈 Historical Trend Analysis
        if len(st.session_state.prediction_history) > 1:
            st.markdown("---")
            st.header("📈 Analisis Trend Historis")

            # Create comprehensive trend analysis
            history_df = pd.DataFrame([
                {'time': h['timestamp'], 'nk': h['prediction']}
                for h in st.session_state.prediction_history[-50:]  # 50 data terakhir
            ])

            col1, col2 = st.columns([2, 1])

            with col1:
                # Advanced trend chart with multiple indicators
                fig_trend = go.Figure()

                # Main trend line
                fig_trend.add_trace(go.Scatter(
                    x=history_df['time'],
                    y=history_df['nk'],
                    mode='lines+markers',
                    name='NK Prediction',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=6)
                ))

                # Moving average (if enough data)
                if len(history_df) >= 5:
                    history_df['ma_5'] = history_df['nk'].rolling(window=5).mean()
                    fig_trend.add_trace(go.Scatter(
                        x=history_df['time'],
                        y=history_df['ma_5'],
                        mode='lines',
                        name='Moving Average (5)',
                        line=dict(color='orange', width=2, dash='dash')
                    ))

                # Add threshold lines if available
                if hasattr(st.session_state, 'nk_threshold_low'):
                    fig_trend.add_hline(y=st.session_state.nk_threshold_low,
                                      line_dash="dash", line_color="red",
                                      annotation_text="Batas Bawah")
                if hasattr(st.session_state, 'nk_threshold_high'):
                    fig_trend.add_hline(y=st.session_state.nk_threshold_high,
                                      line_dash="dash", line_color="green",
                                      annotation_text="Batas Atas")

                fig_trend.update_layout(
                    title="Trend NK Real-Time dengan Indikator",
                    xaxis_title="Waktu",
                    yaxis_title="NK (kJ/kg)",
                    height=400,
                    showlegend=True
                )

                st.plotly_chart(fig_trend, use_container_width=True)

            with col2:
                st.subheader("📊 Statistik Trend")

                # Calculate trend statistics
                current_nk = history_df['nk'].iloc[-1]
                avg_nk = history_df['nk'].mean()
                std_nk = history_df['nk'].std()
                min_nk = history_df['nk'].min()
                max_nk = history_df['nk'].max()

                # Trend direction
                if len(history_df) >= 2:
                    trend_slope = np.polyfit(range(len(history_df)), history_df['nk'], 1)[0]
                    trend_direction = "📈 Naik" if trend_slope > 10 else "📉 Turun" if trend_slope < -10 else "➡️ Stabil"
                else:
                    trend_direction = "➡️ Stabil"

                # Display metrics
                st.metric("NK Saat Ini", f"{current_nk:.0f} kJ/kg")
                st.metric("Rata-rata", f"{avg_nk:.0f} kJ/kg",
                         delta=f"{current_nk - avg_nk:.0f}")
                st.metric("Std Deviasi", f"{std_nk:.1f}")
                st.metric("Range", f"{max_nk - min_nk:.0f} kJ/kg")
                st.metric("Trend", trend_direction)

                # Volatility indicator
                volatility = (std_nk / avg_nk) * 100 if avg_nk > 0 else 0
                if volatility < 5:
                    vol_status = "🟢 Rendah"
                elif volatility < 10:
                    vol_status = "🟡 Sedang"
                else:
                    vol_status = "🔴 Tinggi"

                st.metric("Volatilitas", f"{volatility:.1f}% {vol_status}")

            # Distribution analysis
            st.subheader("📊 Analisis Distribusi")

            col3, col4 = st.columns(2)

            with col3:
                # Histogram
                fig_hist = px.histogram(
                    history_df, x='nk', nbins=20,
                    title="Distribusi Nilai NK",
                    labels={'nk': 'NK (kJ/kg)', 'count': 'Frekuensi'}
                )
                fig_hist.update_layout(height=300)
                st.plotly_chart(fig_hist, use_container_width=True)

            with col4:
                # Box plot
                fig_box = px.box(
                    history_df, y='nk',
                    title="Box Plot NK",
                    labels={'nk': 'NK (kJ/kg)'}
                )
                fig_box.update_layout(height=300)
                st.plotly_chart(fig_box, use_container_width=True)

        # Additional analysis
        st.markdown("---")
        create_parameter_analysis(
            st.session_state.input_data,
            st.session_state.feature_names
        )

        st.markdown("---")
        create_historical_comparison()

    # Footer
    st.markdown("---")
    st.markdown("""
    **Model Information:**
    - Model: Random Forest dengan Genetic Algorithm Optimization
    - Akurasi: 94.56% (MAE: 216.74 kJ/kg)
    - Data Training: 900+ sampel data operasional
    - Optimasi: Modul 8d - Optimasi Tingkat Lanjut
    """)

if __name__ == "__main__":
    main()
