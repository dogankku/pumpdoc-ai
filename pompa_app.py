import streamlit as st
import google.generativeai as genai
import plotly.graph_objects as go
import numpy as np

# --- 1. SAYFA KONFİGÜRASYONU ---
st.set_page_config(page_title="PumpDoc-AI Pro 2026", layout="wide", page_icon="⚙️")

# --- KURUMSAL TASARIM ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True) # <--- Burası 'html' olmalı

st.title("⚙️ PumpDoc-AI Pro: Mühendislik & İhracat Analiz Portalı")
st.caption("2026 AB Makine Yönetmeliği ve SKDM (CBAM) Uyumluluk Sistemi")

# --- 2. SOL PANEL (GİRDİLER) ---
with st.sidebar:
    st.header("🔑 Güvenli Erişim")
    api_key = st.text_input("Gemini API Key", type="password", help="Google AI Studio'dan aldığınız anahtar.")
    
    st.header("📋 Teknik Spesifikasyonlar")
    pump_series = st.selectbox("Pompa Serisi", ["H-Series (Kademeli)", "V-Series (Dikey)", "P-Series (Proses)"])
    q_target = st.number_input("Tasarım Debisi (Q - m3/h)", value=60.0)
    h_target = st.number_input("Basma Yüksekliği (H - mSS)", value=120.0)
    
    st.subheader("🛡️ Emme Koşulları (NPSH)")
    npsha = st.number_input("Mevcut NPSH (NPSHa - m)", value=5.5)
    npshr = st.number_input("Gerekli NPSH (NPSHr - m)", value=3.2)
    
    st.subheader("⚡ Enerji & Malzeme")
    motor_class = st.selectbox("Motor Verim Sınıfı", ["IE2", "IE3", "IE4", "IE5"])
    material = st.selectbox("Ana Malzeme", ["AISI 316L Paslanmaz", "AISI 304 Paslanmaz", "Duplex Çelik", "GG25 Döküm"])
    op_hours = st.slider("Yıllık Çalışma Saati", 1000, 8760, 4500)

# --- 3. MÜHENDİSLİK HESAP MOTORU ---
rho = 1000 # kg/m3 (Su)
g = 9.81
eta_pump = 0.74 # %74 Pompa Verimi
p_hyd = (q_target * h_target * rho * g) / (3.6 * 10**6)
p_shaft = p_hyd / eta_pump
suggested_motor = round(p_shaft * 1.15, 1)

# Enerji ve Karbon Analizi
efficiency_map = {"IE2": 0.88, "IE3": 0.91, "IE4": 0.94, "IE5": 0.96}
annual_energy_kwh = (p_shaft / efficiency_map[motor_class]) * op_hours
co2_annual_ton = (annual_energy_kwh * 0.42) / 1000 

# NPSH Denetimi
npsh_margin = npsha - npshr
cavitation_risk = npsh_margin < 0.5

# --- 4. GÖRSEL ANALİZ (H-Q Grafiği) ---
st.header("📈 Hidrolik Performans Eğrisi")
q_curve = np.linspace(0, q_target * 1.5, 50)
h_curve = h_target * 1.25 * (1 - (q_curve / (q_target * 2.0))**2)

fig = go.Figure()
fig.add_trace(go.Scatter(x=q_curve, y=h_curve, name='H-Q Eğrisi', line=dict(color='#007bff', width=3)))
fig.add_trace(go.Scatter(x=[q_target], y=[h_target], name='Çalışma Noktası', mode='markers', marker=dict(color='red', size=15, symbol='diamond')))
fig.update_layout(height=400, template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
st.plotly_chart(fig, use_container_view=True)

# --- 5. ANALİZ ÖZETİ (Dashboard) ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Mil Gücü (kW)", f"{round(p_shaft, 2)}")
with c2:
    st.metric("Motor Gücü (kW)", f"{suggested_motor}")
with c3:
    status_label = "GÜVENLİ" if not cavitation_risk else "RİSKLİ"
    st.metric("NPSH Marjı (m)", f"{round(npsh_margin, 1)}", delta=status_label)
with c4:
    st.metric("Yıllık Karbon (Ton)", f"{round(co2_annual_ton, 1)}")

st.divider()

# --- 6. AI RAPORLAMA ---
st.header("📜 Uluslararası Teknik Beyanname (AI)")
if st.button("Profesyonel Raporu Oluştur"):
    if not api_key:
        st.warning("Lütfen sol panelden Gemini API Key giriniz.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Sen uzman bir makine mühendisi ve AB regülasyon denetçisisin. 
            Aşağıdaki verilere sahip pompa sistemi için ISO 2026 standartlarında bir rapor yaz.
            
            VERİLER:
            - Tip: {pump_series}, Malzeme: {material}
            - Kapasite: {q_target} m3/h @ {h_target} mSS
            - Enerji: {motor_class} Verim Sınıfı, {round(p_shaft,2)} kW Mil Gücü
            - Karbon: Yıllık {round(co2_annual_ton, 2)} Ton CO2 salınımı
            - Güvenlik: NPSH Marjı {round(npsh_margin, 1)} metre ({'GÜVENLİ' if not cavitation_risk else 'KAVİTASYON RİSKİ'})
            """
            
            with st.spinner('Yapay zeka teknik dosyayı analiz ediyor...'):
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state['full_report'] = response.text
                
        except Exception as e:
            st.error(f"Model Bağlantı Hatası: {e}")
