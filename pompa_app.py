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
# --- 6. AI RAPORLAMA (GÜNCELLENMİŞ VE HATASIZ) ---
if st.button("Profesyonel Raporu Oluştur"):
    if not api_key:
        st.warning("Lütfen sol panelden Gemini API Key giriniz.")
    else:
        try:
            # 1. API Yapılandırması (REST protokolüne zorlayarak bağlantıyı stabilize ediyoruz)
            genai.configure(api_key=api_key, transport='rest')
            
            # 2. TEŞHİS: Mevcut modelleri listele ve uygun olanı bul
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            # Eğer model listesi boşsa anahtarda sorun vardır
            if not available_models:
                st.error("API Anahtarınız için kullanılabilir model bulunamadı.")
                st.stop()
            
            # 3. STRATEJİK SEÇİM: Önce 1.5 Flash'ı, yoksa Pro'yu, o da yoksa ilk bulduğunu seç
            # 404 hatasını önlemek için tam model yolunu (models/...) kullanıyoruz
            selected_model_name = ""
            preferred_models = [
                'models/gemini-1.5-flash', 
                'models/gemini-1.5-flash-latest', 
                'models/gemini-pro'
            ]
            
            for pref in preferred_models:
                if pref in available_models:
                    selected_model_name = pref
                    break
            
            if not selected_model_name:
                selected_model_name = available_models[0] # Hiçbiri yoksa ilki seç
                
            st.info(f"Sistem şu modeli kullanıyor: {selected_model_name}")
            
            # 4. MODELİ ÇALIŞTIR
            model = genai.GenerativeModel(model_name=selected_model_name)
            
            prompt = f"""
            Role: Expert Mechanical Engineer. 
            Write a technical report for a {pump_series} pump. 
            Data: {q_target} m3/h, {h_target} mSS, Material: {material}. 
            Focus: EU 2026 CBAM Carbon Compliance.
            """
            
            with st.spinner('Analiz yapılıyor...'):
                response = model.generate_content(prompt)
                if response and response.text:
                    st.session_state['full_report'] = response.text
                    st.markdown(response.text)
                else:
                    st.error("Modelden yanıt alınamadı.")
                    
        except Exception as e:
            st.error(f"Kritik Hata: {e}")
            st.info("Lütfen API anahtarınızın 'Generative Language API' için etkinleştirildiğinden emin olun.")
