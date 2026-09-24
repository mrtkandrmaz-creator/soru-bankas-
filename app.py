import streamlit as st
import random

# Sayfa Yapılandırması
st.set_page_config(page_title="5. Sınıf Soru Üretici", page_icon="📚")

st.title("📚 5. Sınıf Otomatik Soru Üretici")
st.write("Soru çözmek istediğin dersi ve konuyu seç!")

# Yan Menü (Sidebar)
ders = st.sidebar.selectbox("Ders Seçin", ["Matematik", "Türkçe"])

if ders == "Matematik":
    konu = st.sidebar.selectbox("Konu Seçin", ["Doğal Sayılarla Çarpma", "Kesirlerde Toplama"])
    
    st.subheader(f"📌 Ders: Matematik | Konu: {konu}")
    
    if st.button("🎲 Yeni Soru Üret"):
        if konu == "Doğal Sayılarla Çarpma":
            sayi1 = random.randint(100, 999)
            sayi2 = random.randint(10, 99)
            dogru_cevap = sayi1 * sayi2
            
            st.session_state["soru"] = f"{sayi1} × {sayi2} işleminin sonucu kaçtır?"
            st.session_state["dogru"] = dogru_cevap
            
            # Yanlış şıklar üretme
            yanlislar = [dogru_cevap + 10, dogru_cevap - 5, dogru_cevap + 100]
            secenekler = [dogru_cevap] + yanlislar
            random.shuffle(secenekler)
            st.session_state["siklar"] = secenekler

    # Soru ekrana geldiyse göster
    if "soru" in st.session_state:
        st.markdown(f"### **Soru:** {st.session_state['soru']}")
        
        secim = st.radio(
            "Cevabınızı Seçin:",
            [
                f"A) {st.session_state['siklar'][0]}",
                f"B) {st.session_state['siklar'][1]}",
                f"C) {st.session_state['siklar'][2]}",
                f"D) {st.session_state['siklar'][3]}"
            ]
        )
        
        if st.button("Cevabı Kontrol Et"):
            secilen_val = int(secim.split(") ")[1])
            if secilen_val == st.session_state["dogru"]:
                st.success("🎉 Harika! Doğru Cevap.")
            else:
                st.error(f"❌ Maalesef yanlış. Doğru cevap: {st.session_state['dogru']}")

elif ders == "Türkçe":
    st.info("Türkçe modülü yakında eklenecek!")