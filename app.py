import streamlit as st
import random
import json
import time
import math

# Sayfa Yapılandırması
st.set_page_config(page_title="MEB 5. Sınıf Çoklu Ünite Sınav Platformu", page_icon="🎓", layout="wide")

# =========================================================
# 1. API KEY OKUMA MOTORU
# =========================================================
def get_api_key():
    keys_to_check = ["GEMINI_API_KEY", "API_KEY", "gemini_api_key", "api_key"]
    for k in keys_to_check:
        try:
            if k in st.secrets and str(st.secrets[k]).strip():
                return str(st.secrets[k]).strip()
        except Exception:
            pass
            
    for section in ["general", "default", "secrets"]:
        try:
            if section in st.secrets:
                for k in keys_to_check:
                    if k in st.secrets[section] and str(st.secrets[section][k]).strip():
                        return str(st.secrets[section][k]).strip()
        except Exception:
            pass
    return None

API_KEY = get_api_key()

# Session State Başlatma
if "test_aktif" not in st.session_state:
    st.session_state["test_aktif"] = False
if "test_bitti" not in st.session_state:
    st.session_state["test_bitti"] = False
if "soru_listesi" not in st.session_state:
    st.session_state["soru_listesi"] = []
if "kullanici_cevaplari" not in st.session_state:
    st.session_state["kullanici_cevaplari"] = {}
if "mevcut_soru_index" not in st.session_state:
    st.session_state["mevcut_soru_index"] = 0

# =========================================================
# MEB 5. SINIF EKSİKSİZ TÜM DERSLER VE ÜNİTELER
# =========================================================
MEB_MUFREDAT = {
    "Matematik": [
        "1. Ünite: Doğal Sayılar ve Doğal Sayılarla İşlemler",
        "2. Ünite: Kesirler ve Kesirlerle İşlemler",
        "3. Ünite: Ondalık Gösterim ve Yüzdeler",
        "4. Ünite: Temel Geometrik Kavramlar, Çizimler ve Üçgen/Dörtgenler",
        "5. Ünite: Veri İşleme ve Uzunluk/Zaman Ölçme",
        "6. Ünite: Alan Ölçme ve Geometrik Cisimler (Dikdörtgenler Prizması)"
    ],
    "Fen Bilimleri": [
        "1. Ünite: Güneş, Dünya ve Ay (Yapısı, Boyutları, Evreleri)",
        "2. Ünite: Canlılar Dünyası (Mikroskobik Canlılar, Mantarlar, Bitkiler, Hayvanlar)",
        "3. Ünite: Kuvvetin Ölçülmesi ve Sürtünme",
        "4. Ünite: Madde ve Değişim (Hal Değişimi, Genleşme, Büzülme)",
        "5. Ünite: Işığın Yayılması, Yansıması ve Tam Gölge",
        "6. Ünite: İnsan ve Çevre (Biyoçeşitlilik, Çevre Sorunları)",
        "7. Ünite: Elektrik Devre Elemanları (Devre Şemaları ve Bağlantılar)"
    ],
    "Türkçe": [
        "1. Tema: Sözcükte ve Söz Öbeklerinde Anlam",
        "2. Tema: Cümlede Anlam ve Metin Türleri",
        "3. Tema: Paragrafta Anlam, Ana Fikir ve Yardımcı Fikirler",
        "4. Tema: Noktalama İşaretleri ve Yazım Kuralları",
        "5. Tema: Görsel Okuma, Grafik ve Tablo Yorumlama",
        "6. Tema: Sesteş (Eş Sesli) Sözcükler ve Kök/Ek Bilgisi"
    ],
    "Sosyal Bilgiler": [
        "1. Ünite: Birey ve Toplum (Hak, Sorumluluk, Gruplar)",
        "2. Ünite: Kültür ve Miras (Tarihi Mekanlar, Doğal Varoluşlar)",
        "3. Ünite: İnsanlar, Yerler ve Çevreler (Harita, Yeryüzü Şekilleri, İklim)",
        "4. Ünite: Bilim, Teknoloji ve Toplum (Doğru Bilgiye Ulaşma, Medya)",
        "5. Ünite: Üretim, Dağıtım ve Tüketim (Ekonomik Faaliyetler, Meslekler)",
        "6. Ünite: Etkin Vatandaşlık (Bilinçli Tüketici, Yerel Yönetimler)",
        "7. Ünite: Küresel Bağlantılar (Uluslararası Ticaret ve İş Birliği)"
    ],
    "Din Kültürü ve Ahlak Bilgisi": [
        "1. Ünite: Allah İnancı (Rahman, Rahim, Basar, İlim)",
        "2. Ünite: Ramazan ve Oruç",
        "3. Ünite: Adap ve Nezaket",
        "4. Ünite: Hz. Muhammed ve Aile Hayatı",
        "5. Ünite: Çevremizde Dinin İzleri (Mimaride, Musikide, Edebiyatta)"
    ],
    "İngilizce": [
        "Unit 1: Hello! (School Subjects, Countries, Languages)",
        "Unit 2: My Town (Locations, Directions)",
        "Unit 3: Games and Hobbies",
        "Unit 4: My Daily Routine",
        "Unit 5: Health (Illnesses, Suggestions)",
        "Unit 6: Movies (Movie Types, Expressing Likes)",
        "Unit 7: Party Time (Days, Months, Dates, Ordering)",
        "Unit 8: Fitness (Sports, Making Suggestions)",
        "Unit 9: Animal Shelter (Present Continuous, Farm Animals)",
        "Unit 10: Festivals (National and Religious Celebrations)"
    ]
}

# =========================================================
# 2. SVG GÖRSEL MOTORU
# =========================================================
def svg_iletki_aci_ciz_modern(derece):
    rad = math.radians(180 - derece)
    x = int(140 + 95 * math.cos(rad))
    y = int(120 - 95 * math.sin(rad))
    accent_color = random.choice(["#3b82f6", "#10b981", "#8b5cf6", "#f59e0b", "#ec4899"])
    
    return f'''
    <svg width="280" height="150" viewBox="0 0 280 150" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
          <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.08"/>
        </filter>
        <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#ffffff"/>
          <stop offset="100%" stop-color="#f8fafc"/>
        </linearGradient>
      </defs>
      <rect width="100%" height="100%" fill="url(#bgGrad)" rx="16" filter="url(#shadow)"/>
      <path d="M 35 120 A 105 105 0 0 1 245 120 Z" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="2"/>
      <line x1="35" y1="120" x2="245" y2="120" stroke="#475569" stroke-width="3" stroke-linecap="round"/>
      <line x1="140" y1="120" x2="{x}" y2="{y}" stroke="{accent_color}" stroke-width="4" stroke-linecap="round"/>
      <circle cx="140" cy="120" r="6" fill="{accent_color}"/>
      <circle cx="140" cy="120" r="2" fill="#ffffff"/>
      <rect x="95" y="10" width="90" height="26" rx="8" fill="#e2e8f0"/>
      <text x="140" y="27" font-family="system-ui, sans-serif" font-size="12" font-weight="700" fill="#334155" text-anchor="middle">Açı: ?°</text>
    </svg>
    '''

def svg_kesir_ciz_modern(pay, payda):
    renk = "#3b82f6"
    dilimler = ""
    for i in range(payda):
        fill_color = renk if i < pay else "#e2e8f0"
        x = 20 + i * (220 / payda)
        w = (220 / payda) - 4
        dilimler += f'<rect x="{x}" y="45" width="{w}" height="50" fill="{fill_color}" rx="6"/>'
        
    return f'''
    <svg width="260" height="130" viewBox="0 0 260 130" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#ffffff" rx="16" stroke="#f1f5f9" stroke-width="2"/>
      {dilimler}
      <text x="130" y="112" font-family="system-ui, sans-serif" font-size="13" font-weight="700" fill="#334155" text-anchor="middle">Modelleme: {pay}/{payda}</text>
    </svg>
    '''

def svg_ay_evresi_ciz_modern(evre_adi):
    maskeler = {
        "Yeni Ay": '<circle cx="100" cy="70" r="45" fill="#0f172a"/>',
        "İlk Dördün": '<circle cx="100" cy="70" r="45" fill="#f8fafc"/><path d="M 100 25 A 45 45 0 0 0 100 115 Z" fill="#0f172a"/>',
        "Dolunay": '<circle cx="100" cy="70" r="45" fill="#fef08a" stroke="#facc15" stroke-width="2"/>',
        "Son Dördün": '<circle cx="100" cy="70" r="45" fill="#0f172a"/><path d="M 100 25 A 45 45 0 0 0 100 115 Z" fill="#f8fafc"/>'
    }
    cizim = maskeler.get(evre_adi, maskeler["Dolunay"])
    return f'''
    <svg width="200" height="150" viewBox="0 0 200 150" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#020617" rx="16"/>
      <circle cx="30" cy="30" r="1" fill="#ffffff" opacity="0.6"/>
      <circle cx="170" cy="40" r="1.5" fill="#ffffff" opacity="0.8"/>
      <circle cx="150" cy="120" r="1" fill="#ffffff" opacity="0.4"/>
      {cizim}
      <rect x="40" y="122" width="120" height="20" rx="6" fill="#1e293b"/>
      <text x="100" y="136" font-family="system-ui, sans-serif" font-size="11" font-weight="600" fill="#f1f5f9" text-anchor="middle">{evre_adi}</text>
    </svg>
    '''

# =========================================================
# 3. DİNAMİK ŞABLON MOTORU
# =========================================================
def sablon_soru_uret(ders, unite):
    u_lower = unite.lower()
    
    if ders == "Matematik":
        if "geometrik" in u_lower or "açı" in u_lower:
            aci = random.choice([30, 45, 60, 90, 120, 135, 150])
            tur = "Dar Açı" if aci < 90 else ("Dik Açı" if aci == 90 else "Geniş Açı")
            siklar = ["Dar Açı", "Dik Açı", "Geniş Açı", "Doğru Açı"]
            random.shuffle(siklar)
            return {
                "ders": ders,
                "unite": unite,
                "soru": f"Yukarıdaki açı ölçer (iletki) görselinde verilen {aci}°'lik açı hangi açı türüdür?",
                "gorsel_svg": svg_iletki_aci_ciz_modern(aci),
                "siklar": siklar,
                "dogru": tur,
                "kaynak": "Şablon Motoru"
            }
        elif "kesir" in u_lower:
            payda = random.choice([4, 5, 6, 8])
            pay = random.randint(1, payda - 1)
            siklar = [f"{pay}/{payda}", f"{payda-pay}/{payda}", f"{pay}/{payda+1}", f"{pay+1}/{payda}"]
            siklar = list(set(siklar))
            while len(siklar) < 4:
                siklar.append(f"{random.randint(1,3)}/{payda}")
            random.shuffle(siklar)
            return {
                "ders": ders,
                "unite": unite,
                "soru": "Yukarıda modellenen kesrin değeri aşağıdakilerden hangisidir?",
                "gorsel_svg": svg_kesir_ciz_modern(pay, payda),
                "siklar": siklar,
                "dogru": f"{pay}/{payda}",
                "kaynak": "Şablon Motoru"
            }

    elif ders == "Fen Bilimleri":
        if "güneş" in u_lower or "ay" in u_lower:
            evreler = ["Yeni Ay", "İlk Dördün", "Dolunay", "Son Dördün"]
            secilen_evre = random.choice(evreler)
            siklar = evreler.copy()
            random.shuffle(siklar)
            return {
                "ders": ders,
                "unite": unite,
                "soru": "Görselde karanlık uzay zemininde modellenen Ay'ın ana evresi aşağıdakilerden hangisidir?",
                "gorsel_svg": svg_ay_evresi_ciz_modern(secilen_evre),
                "siklar": siklar,
                "dogru": secilen_evre,
                "kaynak": "Şablon Motoru"
            }

    return {
        "ders": ders,
        "unite": unite,
        "soru": f"[{ders} - {unite}] konusuna ait temel kavram aşağıdakilerden hangisidir?",
        "gorsel_svg": None,
        "siklar": ["Doğru Seçenek A", "Yanlış Seçenek B", "Yanlış Seçenek C", "Yanlış Seçenek D"],
        "dogru": "Doğru Seçenek A",
        "kaynak": "Müfredat Şablonu"
    }

# =========================================================
# 4. GEMINI AI MOTORU
# =========================================================
def gemini_soru_uret(api_key, ders, unite):
    if not api_key:
        return None
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        prompt = (
            f"Sen uzman bir MEB 5. Sınıf öğretmenisin.\n"
            f"DERS: {ders}\n"
            f"ÜNİTE: {unite}\n\n"
            f"Görevin: '{unite}' ünitesine tam uygun 1 adet 4 şıklı test sorusu üretmektir.\n"
            "Yanıtını YALNIZCA aşağıdaki JSON formatında ver, başka metin ekleme:\n"
            "{\n"
            '  "soru": "Soru metni",\n'
            '  "gorsel_tasvir": "Varsa tablo/görsel tasviri yoksa null",\n'
            '  "siklar": ["A Şıkkı", "B Şıkkı", "C Şıkkı", "D Şıkkı"],\n'
            '  "dogru": "Doğru şık metni"\n'
            "}"
        )
        
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        clean_json = response.text.strip().replace("```json", "").replace("```", "").strip()
        veri = json.loads(clean_json)
        veri["ders"] = ders
        veri["unite"] = unite
        veri["kaynak"] = f"Yapay Zekâ (Gemini)"
        return veri
    except Exception:
        return None

def soru_hazirla(api_key, ders, unite):
    if api_key and random.random() < 0.85:
        ai_soru = gemini_soru_uret(api_key, ders, unite)
        if ai_soru:
            return ai_soru
    return sablon_soru_uret(ders, unite)

# =========================================================
# 5. STREAMLIT ARAYÜZ (CHECK-BOX YAPI)
# =========================================================
st.title("🎓 MEB 5. Sınıf Çoklu Ders ve Ünite Sınav Motoru")

st.sidebar.header("⚙️ Ders ve Ünite Seçimi")
st.sidebar.caption("Sınava dahil etmek istediğiniz üniteleri işaretleyin:")

secilen_uniteler = []  # [(Ders_Adı, Ünite_Adı), ...]

# HER DERS İÇİN EXPANDER VE CHECKBOX LİSTESİ
for ders_adi, uniteler in MEB_MUFREDAT.items():
    with st.sidebar.expander(f"📚 {ders_adi}", expanded=False):
        # Tümünü Seç/Kaldır hızlı aksiyonu
        select_all = st.checkbox(f"Tüm {ders_adi} Ünitelerini Seç", key=f"all_{ders_adi}", disabled=st.session_state["test_aktif"])
        
        st.divider()
        for idx, u in enumerate(uniteler):
            # Eğer 'Tümünü Seç' tıklanmışsa varsayılan True olur
            default_val = select_all
            cb = st.checkbox(u, value=default_val, key=f"cb_{ders_adi}_{idx}", disabled=st.session_state["test_aktif"])
            if cb:
                secilen_uniteler.append((ders_adi, u))

st.sidebar.divider()
soru_sayisi = st.sidebar.number_input("Toplam Soru Sayısı:", min_value=1, max_value=50, value=10, step=1, disabled=st.session_state["test_aktif"])

# BAŞLANGIÇ EKRANI
if not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.subheader("📋 Seçilen Sınav Müfredatı Kapsamı")
    
    if secilen_uniteler:
        st.success(f"Toplam **{len(secilen_uniteler)}** adet ünite/tema seçildi.")
        
        # Seçilen ünitelerin derslere göre gruplanıp gösterilmesi
        ders_bazli = {}
        for d, u in secilen_uniteler:
            ders_bazli.setdefault(d, []).append(u)
            
        for d_ad, u_list in ders_bazli.items():
            st.markdown(f"**{d_ad} ({len(u_list)} Ünite):**")
            for u_ad in u_list:
                st.caption(f"• {u_ad}")
                
        if st.button("🚀 Seçilen Ünitelerden Sınavı Başlat", type="primary"):
            with st.spinner("Seçilen tüm ünitelerden karma sorular hazırlanıyor..."):
                sorular = []
                # Üniteler arasında soru sayısını dengeli dağıtma
                for i in range(soru_sayisi):
                    hedf_ders, hedf_unite = secilen_uniteler[i % len(secilen_uniteler)]
                    sorular.append(soru_hazirla(API_KEY, hedf_ders, hedf_unite))
                
                random.shuffle(sorular)  # Soruları karma sıraya koy
                st.session_state["soru_listesi"] = sorular
                st.session_state["kullanici_cevaplari"] = {}
                st.session_state["mevcut_soru_index"] = 0
                st.session_state["test_aktif"] = True
                st.session_state["test_bitti"] = False
                st.rerun()
    else:
        st.warning("⚠️ Lütfen sınav oluşturmak için sol menüden en az 1 ünite işaretleyin (check-box).")

# TEST EKRANI
elif st.session_state["test_aktif"]:
    idx = st.session_state["mevcut_soru_index"]
    q = st.session_state["soru_listesi"][idx]

    st.caption(f"📌 **Ders:** {q['ders']} | **Ünite:** {q['unite']}")
    st.write(f"📝 **Soru:** {idx + 1} / {len(st.session_state['soru_listesi'])}")
    st.progress((idx + 1) / len(st.session_state["soru_listesi"]))
    st.divider()

    st.markdown(f"### **Soru {idx + 1}:** {q['soru']}")

    if q.get("gorsel_svg"):
        st.components.v1.html(q["gorsel_svg"], height=165)
    elif q.get("gorsel_tasvir"):
        st.info(f"📊 **Ünite İllüstrasyonu / Tablo:**\n{q['gorsel_tasvir']}")

    onceki_cevap = st.session_state["kullanici_cevaplari"].get(idx, None)
    secim_index = q["siklar"].index(onceki_cevap) if onceki_cevap in q["siklar"] else None

    secim = st.radio("Cevabınızı İşaretleyin:", q["siklar"], index=secim_index, key=f"radio_{idx}")
    if secim is not None:
        st.session_state["kullanici_cevaplari"][idx] = secim

    st.divider()
    col_prev, col_next = st.columns([1, 1])

    if idx > 0 and col_prev.button("⬅️ Önceki Soru"):
        st.session_state["mevcut_soru_index"] -= 1
        st.rerun()

    if idx + 1 < len(st.session_state["soru_listesi"]):
        if col_next.button("Sonraki Soru ➡️", type="primary"):
            st.session_state["mevcut_soru_index"] += 1
            st.rerun()
    else:
        if col_next.button("🏁 Sınavı Tamamla", type="primary"):
            st.session_state["test_aktif"] = False
            st.session_state["test_bitti"] = True
            st.rerun()

# SONUÇ EKRANI
elif st.session_state["test_bitti"]:
    st.balloons()
    st.header("📊 Karma Sınav Sonuç Karnesi")

    toplam_soru = len(st.session_state["soru_listesi"])
    dogru_sayisi = sum(1 for i, q in enumerate(st.session_state["soru_listesi"]) if st.session_state["kullanici_cevaplari"].get(i) == q["dogru"])
    puan = int((dogru_sayisi / toplam_soru) * 100)

    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Soru", toplam_soru)
    c2.metric("Doğru Sayısı", dogru_sayisi)
    c3.metric("Başarı Puanı", f"{puan} / 100")

    st.divider()
    for i, q in enumerate(st.session_state["soru_listesi"]):
        k_cevabi = st.session_state["kullanici_cevaplari"].get(i, "Boş Bırakıldı")
        d_cevabi = q["dogru"]
        durum = "✅ Doğru" if k_cevabi == d_cevabi else "❌ Yanlış"
        
        with st.expander(f"Soru {i+1} [{q['ders']} - {q['unite']}]: {durum}"):
            st.write(f"**Soru:** {q['soru']}")
            st.write(f"👉 **Sizin Cevabınız:** {k_cevabi}")
            st.write(f"✅ **Doğru Cevap:** {d_cevabi}")
            st.caption(f"Kaynak: {q.get('kaynak', 'Sistem')}")

    if st.button("🔄 Yeni Sınav Oluştur"):
        st.session_state["test_bitti"] = False
        st.session_state["test_aktif"] = False
        st.rerun()
