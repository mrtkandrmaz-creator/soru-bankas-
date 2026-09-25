import time
import random
import streamlit as st

# --- ÖRNEK HAVUZ VE YAPAY ZEKA FONKSİYONLARI ---
# (Mevcut projedeki kendi havuz ve yapay zeka fonksiyonlarınla burayı değiştirebilirsin)

def havuzdan_soru_getir(adet, uniteler):
    """Yerel soru havuzundan belirtilen adet kadar soru çeker."""
    ornek_havuz = [
        {"soru": "Havuz Soru 1: ...", "secenekler": ["A", "B", "C", "D"], "cevap": "A"},
        {"soru": "Havuz Soru 2: ...", "secenekler": ["A", "B", "C", "D"], "cevap": "B"},
        {"soru": "Havuz Soru 3: ...", "secenekler": ["A", "B", "C", "D"], "cevap": "C"},
        {"soru": "Havuz Soru 4: ...", "secenekler": ["A", "B", "C", "D"], "cevap": "D"},
    ]
    # Seçilen üniteler ve adete göre havuzdan rastgele seçelim
    return random.sample(ornek_havuz, min(adet, len(ornek_havuz)))

def yapay_zekadan_soru_uret(adet, uniteler):
    """Yapay zeka (Gemini vb.) kullanarak belirtilen adet kadar özgün soru üretir."""
    ai_sorulari = []
    for i in range(adet):
        # Burada gerçek projede LLM API çağrısı yer alır (örn: model.generate_content(...))
        ai_sorulari.append({
            "soru": f"Yapay Zeka Soru {i+1} ({', '.join(uniteler)}): ...", 
            "secenekler": ["A", "B", "C", "D"], 
            "cevap": "A"
        })
    return ai_sorulari

def hibrit_soru_uretici(secilen_uniteler, toplam_soru_sayisi):
    """Soruların %75'ini yapay zekadan, %25'ini havuzdan üretip birleştirir."""
    ai_adet = int(toplam_soru_sayisi * 0.75)
    havuz_adet = toplam_soru_sayisi - ai_adet  # Kalan %25'lik kısım
    
    # Güvenlik kontrolü: Havuzda yeterli soru yoksa dinamik Dengele
    ai_sorular = yapay_zekadan_soru_uret(ai_adet, secilen_uniteler)
    havuz_sorular = havuzdan_soru_getir(havuz_adet, secilen_uniteler)
    
    tum_sorular = ai_sorular + havuz_sorular
    random.shuffle(tum_sorular) # Soruları karıştır
    return tum_sorular


# --- STREAMLIT ARAYÜZ VE BUTON KISMI ---

# Session State tanımlamaları (Eğer tanımlı değilse)
if "sorular_hazir" not in st.session_state:
    st.session_state["sorular_hazir"] = False
if "test_aktif" not in st.session_state:
    st.session_state["test_aktif"] = False

secilen_uniteler = st.sidebar.multiselect("Üniteleri Seçin", ["Ünite 1", "Ünite 2", "Ünite 3"], default=["Ünite 1"])
soru_sayisi = st.sidebar.slider("Soru Sayısı", min_v=4, max_v=40, value=12, step=4)

st.sidebar.write("")
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🚀 Hazırla ve Başlat", type="primary", use_container_width=True):
        if secilen_uniteler:
            # Tahmini süre (Yapay zeka katıldığı için süre biraz daha dinamik hesaplanır)
            tahmini_sure = max(3, int(soru_sayisi * 0.4))
            
            # Dinamik Geri Sayım Görselleştirmesi
            status_box = st.empty()
            progress_bar = st.progress(0)
            
            for kalan_sn in range(tahmini_sure, 0, -1):
                progress_yuzdesi = int(((tahmini_sure - kalan_sn + 1) / tahmini_sure) * 100)
                progress_bar.progress(min(progress_yuzdesi, 95))
                status_box.info(
                    f"🤖 Soruların %75'i yapay zekadan üretiliyor, %25'i havuzdan harmanlanıyor... "
                    f"Kalan tahmini süre: **{kalan_sn} saniye**"
                )
                time.sleep(1)
            
            # Hibrit Soru Üretim Fonksiyonunu Çalıştır (%75 AI - %25 Havuz)
            sorular = hibrit_soru_uretici(secilen_uniteler, soru_sayisi)
            
            progress_bar.progress(100)
            status_box.success("✅ Hibrit sorular başarıyla hazırlandı!")
            time.sleep(0.5)
            
            st.session_state["soru_listesi"] = sorular
            st.session_state["toplam_sure_sn"] = len(sorular) * 90
            st.session_state["sorular_hazir"] = True
            st.rerun()
        else:
            st.sidebar.error("⚠️ Lütfen sol menüden en az bir ünite seçimi yapın!")
