import streamlit as st
import google.generativeai as genai

# --- PROFESYONEL AYARLAR ---
st.set_page_config(page_title="PumpDoc-AI Pro 2026", layout="wide")
st.title("⚙️ PumpDoc-AI Pro: Mühendislik Analiz Portalı")

# --- SIDEBAR: TEKNİK GİRDİLER ---
with st.sidebar:
    st.header("📋 Teknik Spesifikasyonlar")
    api_key = st.text_input("Gemini API Key", type="password")
    
    st.subheader("1. Hidrolik Veriler")
    q = st.number_input("Debi (Q - m3/h)", value=50.0)
    h = st.number_input("Basma Yüksekliği (H - mSS)", value=100.0)
    
    st.subheader("2. Emme Koşulları (NPSH)")
    npsh_available = st.number_input("Mevcut NPSH (NPSHa - m)", value=5.0)
    npsh_required = st.number_input("Gerekli NPSH (NPSHr - m)", value=3.5)
    
    st.subheader("3. Motor & Enerji")
    motor_class = st.selectbox("Motor Verim Sınıfı", ["IE2", "IE3", "IE4", "IE5"])
    material = st.selectbox("Malzeme", ["AISI 316", "AISI 304", "Dökme Demir"])

# --- MÜHENDİSLİK HESAP MOTORU ---
# Hidrolik ve Mil Gücü Hesabı
rho = 1000 # kg/m3 (Su)
g = 9.81
eta_pump = 0.72 # Varsayılan pompa verimi
p_hyd = (q * h * rho * g) / (3.6 * 10**6)
p_shaft = p_hyd / eta_pump
suggested_motor = round(p_shaft * 1.15, 1) # %15 emniyet faktörü

# Kavitasyon Kontrolü
cavitation_risk = npsh_available < (npsh_required + 0.5)

# Enerji Tasarrufu Analizi (IE2'ye göre yıllık kazanç tahmini)
efficiency_map = {"IE2": 0.88, "IE3": 0.91, "IE4": 0.94, "IE5": 0.96}
annual_op_hours = 4000
energy_price = 0.15 # $/kWh
saving = (p_shaft / efficiency_map["IE2"] - p_shaft / efficiency_map[motor_class]) * annual_op_hours * energy_price

# --- ANA EKRAN: TEKNİK ANALİZ ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Mil Gücü ($P_{shaft}$)", f"{round(p_shaft, 2)} kW")
    if cavitation_risk:
        st.error("⚠️ KAVİTASYON RİSKİ! NPSHa değerini artırın.")
    else:
        st.success("✅ NPSH Dengesi Uygun")

with col2:
    st.metric("Yıllık Enerji Tasarrufu", f"${round(saving, 0)}")
    st.caption(f"IE2 sınıfına göre {motor_class} avantajı.")

with col3:
    carbon_val = (p_shaft * annual_op_hours * 0.45) / 1000 # Operasyonel Karbon (ton/yıl)
    st.metric("Yıllık CO2 (Operasyonel)", f"{round(carbon_val, 2)} Ton")

st.divider()

# --- GEMINI AI: TEKNİK DOSYA YAZIMI ---
if st.button("Profesyonel Mühendislik Raporu Oluştur"):
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Sen kıdemli bir mekanik tasarım mühendisisin. Aşağıdaki veriler için teknik bir beyan hazırla:
            - Pompa: {q} m3/h, {h} mSS performansında.
            - NPSH Durumu: NPSHa={npsh_available}m, NPSHr={npsh_required}m.
            - Motor: {motor_class} verimlilik sınıfı.
            - Karbon: Yıllık {carbon_val} ton CO2 salınımı.
            
            Görev:
            1. Ürünün kavitasyon güvenliğini teknik dille analiz et.
            2. {motor_class} motorun işletme maliyeti üzerindeki etkisini vurgula.
            3. AB 2026 Eko-Tasarım (Ecodesign) yönetmeliğine uygunluğunu teyit eden profesyonel bir sonuç paragrafı yaz.
            """
            
            with st.spinner('Mühendislik raporu oluşturuluyor...'):
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state['pro_report'] = response.text
        except Exception as e:
            st.error(f"Hata: {e}")

if 'pro_report' in st.session_state:
    st.download_button("📄 Teknik Dosyayı İndir", st.session_state['pro_report'], file_name="Tech_Analysis.txt")
