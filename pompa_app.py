import streamlit as st
import google.generativeai as genai
import plotly.graph_objects as go
import numpy as np

# --- 1. SAYFA KONFİGÜRASYONU ---
st.set_page_config(page_title="PumpDoc-AI Pro 2026", layout="wide", page_icon="⚙️")

# --- CUSTOM CSS (Kurumsal Görünüm) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .metric-card { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_stdio=True)

st.title("⚙️ PumpDoc-AI Pro: Mühendislik & İhracat Analiz Portalı")
st.caption("2026 AB Makine Yönetmeliği ve SKDM (CBAM) Uyumluluk Sistemi")

# --- 2. SOL PANEL (GİRDİLER) ---
with st.sidebar:
    st.header("🔑 Güvenli Erişim")
    api_key = st.text_input("Gemini API Key", type="password")
    
    st.header("📋 Teknik Veriler")
    pump_type = st.selectbox("Pompa Serisi", ["H-Series Kademeli", "V-Series Dikey", "P-Series Proses"])
    q_target = st.number_input("Tasarım Debisi (Q - m3/h)", value=60.0)
    h_target = st.number_input("Basma Yüksekliği (H - mSS)", value=120.0)
    
    st.subheader("🛡️ Emme Koşulları")
    npsha = st.number_input("Mevcut NPSH (NPSHa - m)", value=5.5)
    npshr = st.number_input("Gerekli NPSH (NPSHr - m)", value=3.2)
    
    st.subheader("⚡ Enerji & Malzeme")
    motor_class = st.selectbox("Motor Verim Sınıfı", ["IE2", "IE3", "IE4", "IE5"])
    material = st.selectbox("Malzeme", ["AISI 316L", "AISI 304", "Duplex", "GG25 Döküm"])
    op_hours = st.slider("Yıllık Çalışma Saati", 1000, 8760, 4500)

# --- 3. MÜHENDİSLİK HESAP MOTORU ---
rho = 1000 # kg/m3
g = 9.81
eta_pump = 0.74 # %74 Verim varsayımı
p_hyd = (q_target * h_target * rho * g) / (3.6 * 10**6)
p_shaft = p_hyd / eta_pump
suggested_motor = round(p_shaft * 1.15, 1)

# Karbon ve Enerji Analizi
efficiency_map = {"IE2": 0.88, "IE3": 0.91, "IE4": 0.94, "IE5": 0.96}
annual_energy_kwh = (p_shaft / efficiency_map[motor_class]) * op_hours
co2_annual = (annual_energy_kwh * 0.42) / 1000 # Ton CO2/Yıl

# Kavitasyon Riski
cavitation_status = "GÜVENLİ" if npsha > (npshr + 0.5) else "RİSKLİ"

# --- 4. GÖRSEL ANALİZ (Plotly) ---
st.header("📈 Hidrolik Performans Analizi")
q_curve = np.linspace(0, q_target * 1.4, 50)
h_curve = h_target * 1.2 * (1 - (q_curve / (q_target * 1.8))**2)

fig = go.Figure()
fig.add_trace(go.Scatter(x=q_curve, y=h_curve, name='Pompa Eğrisi (H-Q)', line=dict(color='#1f77b4', width=4)))
fig.add_trace(go.Scatter(x=[q_target], y=[h_target], name='Çalışma Noktası', mode='markers', marker=dict(color='red', size=15, symbol='cross')))
fig.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_view=True)
