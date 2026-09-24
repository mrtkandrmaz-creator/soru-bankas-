import streamlit as st
import random
import json
import time
import math
import uuid

# Sayfa Yapılandırması
st.set_page_config(page_title="MEB 5. Sınıf Soru Bankası Engine", page_icon="🎓", layout="wide")

# =========================================================
# 1. API KEY OKUMA
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
if "sorular_hazir" not in st.session_state:
    st.session_state["sorular_hazir"] = False
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
if "baslangic_zamani" not in st.session_state:
    st.session_state["baslangic_zamani"] = None
if "toplam_sure_sn" not in st.session_state:
    st.session_state["toplam_sure_sn"] = 0

# MEB MÜFREDATI
MEB_MUFREDAT = {
    "Matematik": [
        "1. Ünite: Doğal Sayılar ve Doğal Sayılarla İşlemler",
        "2. Ünite: Kesirler ve Kesirlerle İşlemler",
        "3. Ünite: Ondalık Gösterim ve Yüzdeler",
        "4. Ünite: Temel Geometrik Kavramlar, Çizimler ve Üçgen/Dörtgenler",
        "5. Ünite: Veri İşleme ve Uzunluk/Zaman Ölçme",
        "6. Ünite: Alan Ölçme ve Geometrik Cisimler"
    ],
    "Fen Bilimleri": [
        "1. Ünite: Güneş, Dünya ve Ay",
        "2. Ünite: Canlılar Dünyası",
        "3. Ünite: Kuvvetin Ölçülmesi ve Sürtünme",
        "4. Ünite: Madde ve Değişim",
        "5. Ünite: Işığın Yayılması, Yansıması ve Tam Gölge",
        "6. Ünite: İnsan ve Çevre",
        "7. Ünite: Elektrik Devre Elemanları"
    ],
    "Türkçe": [
        "1. Tema: Sözcükte ve Söz Öbeklerinde Anlam",
        "2. Tema: Cümlede Anlam ve Metin Türleri",
        "3. Tema: Paragrafta Anlam ve Ana Fikir",
        "4. Tema: Noktalama İşaretleri ve Yazım Kuralları",
        "5. Tema: Görsel Okuma ve Tablo Yorumlama"
    ],
    "Sosyal Bilgiler": [
        "1. Ünite: Birey ve Toplum",
        "2. Ünite: Kültür ve Miras",
        "3. Ünite: İnsanlar, Yerler ve Çevreler",
        "4. Ünite: Bilim, Teknoloji ve Toplum",
        "5. Ünite: Üretim, Dağıtım ve Tüketim"
    ],
    "Din Kültürü ve Ahlak Bilgisi": [
        "1. Ünite: Allah İnancı",
        "2. Ünite: Ramazan ve Oruç",
        "3. Ünite: Adap ve Nezaket"
    ],
    "İngilizce": [
        "Unit 1: Hello!",
        "Unit 2: My Town",
        "Unit 3: Games and Hobbies",
        "Unit 4: My Daily Routine"
    ]
}

# =========================================================
# 2. SVG GÖRSEL MOTORU
# =========================================================
def svg_iletki_aci_ciz(derece):
    rad = math.radians(180 - derece)
    x = int(140 + 95 * math.cos(rad))
    y = int(120 - 95 * math.sin(rad))
    return f'''
    <svg width="280" height="140" viewBox="0 0 280 140" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#f8fafc" rx="12" stroke="#e2e8f0"/>
      <path d="M 35 110 A 105 105 0 0 1 245 110 Z" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>
      <line x1="35" y1="110" x2="245" y2="110" stroke="#334155" stroke-width="3"/>
      <line x1="140" y1="110" x2="{x}" y2="{y}" stroke="#2563eb" stroke-width="4" stroke-linecap="round"/>
      <circle cx="140" cy="110" r="5" fill="#2563eb"/>
      <text x="140" y="25" font-family="sans-serif" font-size="12" font-weight="bold" fill="#1e293b" text-anchor="middle">Açı: ?°</text>
    </svg>
    '''

def svg_kesir_ciz(pay, payda):
    dilimler = ""
    for i in range(payda):
        fill = "#3b82f6" if i < pay else "#e2e8f0"
        x = 15 + i * (230 / payda)
        w = (230 / payda) - 3
        dilimler += f'<rect x="{x}" y="35" width="{w}" height="45" fill="{fill}" rx="4"/>'
    return f'''
    <svg width="260" height="110" viewBox="0 0 260 110" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#ffffff" rx="12" stroke="#cbd5e1"/>
      {dilimler}
      <text x="130" y="95" font-family="sans-serif" font-size="12" font-weight="bold" fill="#334155" text-anchor="middle">Kesir Modeli</text>
    </svg>
    '''

# =========================================================
# 3. KONTROL VE FİLTRE MOTORU (CEVAP SIZINTISI ENGELLEME)
# =========================================================
def cevap_kontrolü_ve_temizlik(soru_metni, dogru_cevap, siklar):
    """
    Sorunun metninde cevabın açık edilmediğinden ve şıkların eşsiz olduğundan emin olur.
    """
    metin = soru_metni.lower()
    cevap = str(dogru_cevap).lower().strip()
    
    # Cevap 3 karakterden büyükse ve metinde aynen geçiyorsa engelle
    if len(cevap) > 3 and cevap in metin:
        return False
        
    # Şıkların hepsi birbirinden farklı olmalı
    if len(set(siklar)) != len(siklar):
        return False
        
    return True

# =========================================================
# 4. ONBİNLERCE KOMBİNASYON ÜRETEN DİNAMİK MİMARİ
# =========================================================
def devasa_sablon_engine(ders, unite):
    u_lower = unite.lower()
    
    # Çoklu Değişken Matrisi
    isimler = ["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Ali", "Fatma", "Deniz", "Ömer", "Selin", "Kaan", "Cem"]
    sehirler = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Konya", "Trabzon", "Erzurum", "Eskişehir", "Gaziantep"]
    nesneler = ["kitap", "kalem", "bilye", "ceviz", "elma", "çikolata", "sayfa", "pul", "kart"]
    
    # -----------------------------------------------------
    # MATEMATİK
    # -----------------------------------------------------
    if ders == "Matematik":
        if "geometrik" in u_lower or "açı" in u_lower:
            aci = random.randint(15, 175)
            if aci == 90:
                tur, celd = "Dik Açı", ["Dar Açı", "Geniş Açı", "Doğru Açı"]
            elif aci < 90:
                tur, celd = "Dar Açı", ["Dik Açı", "Geniş Açı", "Tam Açı"]
            else:
                tur, celd = "Geniş Açı", ["Dar Açı", "Dik Açı", "Doğru Açı"]
                
            siklar = [tur] + celd
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": f"Görseldeki iletki üzerinde ölçümü gösterilen x açısının değeri {aci}° olarak hesaplanmıştır. Bu açının çeşidi nedir?",
                "gorsel_svg": svg_iletki_aci_ciz(aci), "siklar": siklar, "dogru": tur, "kaynak": "Dinamik Geometri Motoru"
            }
        elif "kesir" in u_lower:
            payda = random.choice([5, 6, 8, 10, 12, 15, 20])
            pay = random.randint(1, payda - 1)
            dogru_str = f"{pay}/{payda}"
            siklar = [dogru_str, f"{payda-pay}/{payda}", f"{pay}/{payda+2}", f"{pay+1}/{payda}"]
            siklar = list(dict.fromkeys(siklar))
            while len(siklar) < 4:
                siklar.append(f"{random.randint(1,4)}/{payda+3}")
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": "Verilen modelde boyalı kısımların bütün içerisindeki oranını gösteren kesir hangisidir?",
                "gorsel_svg": svg_kesir_ciz(pay, payda), "siklar": siklar, "dogru": dogru_str, "kaynak": "Dinamik Kesir Motoru"
            }
        else: # Problem ve Sayı Üreteci
            kisi = random.choice(isimler)
            nesne = random.choice(nesneler)
            s1 = random.randint(150, 950)
            s2 = random.randint(25, 120)
            islem = random.choice(["toplam", "fark", "kat"])
            
            if islem == "toplam":
                ans = s1 + s2
                q_text = f"{kisi}'in {s1} adet {nesne}si vardır. Arkadaşı ona {s2} adet daha verirse toplam kaç {nesne}si olur?"
            elif islem == "fark":
                ans = s1 - s2
                q_text = f"{kisi} elindeki {s1} adet {nesne}nin {s2} tanesini kardeşine vermiştir. Geride kaç {nesne} kalmıştır?"
            else:
                ans = s1 * 2
                q_text = f"{kisi}'in {nesne} sayısı {s1} tanedir. Can'ın {nesne} sayısı {kisi}'inkinin 2 katı olduğuna göre Can'ın kaç {nesne}si vardır?"

            siklar = [str(ans), str(ans + random.choice([5, 10, 100])), str(abs(ans - 15)), str(ans + 20)]
            siklar = list(dict.fromkeys(siklar))
            while len(siklar) < 4:
                siklar.append(str(ans + random.randint(25, 80)))
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": q_text, "gorsel_svg": None, "siklar": siklar, "dogru": str(ans), "kaynak": "Dinamik Problem Motoru"
            }

    # -----------------------------------------------------
    # FEN BİLİMLERİ
    # -----------------------------------------------------
    elif ders == "Fen Bilimleri":
        if "güneş" in u_lower or "ay" in u_lower:
            konular = [
                ("Ay'ın Dünya'ya en yakın olduğu ve tamamen aydınlık göründüğü evre hangisidir?", "Dolunay", ["Yeni Ay", "İlk Dördün", "Son Dördün"]),
                ("Güneş, Dünya ve Ay'ın büyüklük sıralaması büyükten küçüğe nasıl olmalıdır?", "Güneş > Dünya > Ay", ["Dünya > Güneş > Ay", "Ay > Dünya > Güneş", "Güneş > Ay > Dünya"]),
                ("Ay'ın ana evreleri arasındaki zaman dilimi yaklaşık ne kadardır?", "1 Hafta", ["1 Gün", "1 Yıl", "1 Saat"])
            ]
            q, ans, celd = random.choice(konular)
            siklar = [ans] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q, "gorsel_svg": None, "siklar": siklar, "dogru": ans, "kaynak": "Dinamik Fen Motoru"}
        else:
            kavramlar = [
                ("Kuvvetin büyüklüğünü ölçen yayın esneklik özelliğinden yararlanan araç hangisidir?", "Dinamometre", ["Termometre", "Barometre", "Eşit Kollu Terazi"]),
                ("Pürüzsüz buzlu bir yüzeyde kayan kızak için hangisi söylenebilir?", "Sürtünme kuvveti azdır", ["Sürtünme kuvveti çok fazladır", "Kuvvet ölçülemez", "Hareket imkansızdır"]),
                ("Sıvı bir maddenin ısı alarak gaz haline geçmesi olayına ne ad verilir?", "Buharlaşma", ["Donma", "Yoğuşma", "Kırağılaşma"])
            ]
            q, ans, celd = random.choice(kavramlar)
            siklar = [ans] + celd
            random.shuffle(siklar)
            return {"ders": ders, "unite": unite, "soru": q, "gorsel_svg": None, "siklar": siklar, "dogru": ans, "kaynak": "Dinamik Fen Motoru"}

    # -----------------------------------------------------
    # TÜRKÇE & SOSYAL & DİN & İNGİLİZCE (GENEL DİNAMİK HAVUZ)
    # -----------------------------------------------------
    elif ders == "Türkçe":
        kaliplar = [
            ("Aşağıdaki cümlelerin hangisinde 'mecaz anlamlı' bir sözcük kullanılmıştır?", "Onun bu soğuk davranışları herkesi kırdı.", ["Güneş açınca hava ısındı.", "Masadaki bardağı yere düşürdü.", "Otobüs zamanında durağa geldi."]),
            ("Hangisinde yazım kuralı ihlali yapılmıştır?", "Ahmet'de bizimle gelecek mi?", ["Ankara'ya otobüsle gitti.", "10 Kasım törenle anıldı.", "Kitabını evde unutmuş."]),
            ("Hangisi 'zıt anlamlı' kelime çiftidir?", "Uzun - Kısa", ["Al - Kırmızı", "Fayda - Yarar", "Cevap - Yanıt"])
        ]
        q, ans, celd = random.choice(kaliplar)
        siklar = [ans] + celd
        random.shuffle(siklar)
        return {"ders": ders, "unite": unite, "soru": q, "gorsel_svg": None, "siklar": siklar, "dogru": ans, "kaynak": "Dinamik Dil Motoru"}

    else:
        # Genel Sosyal / Din / İngilizce Kalıpları
        kisi = random.choice(isimler)
        sehir = random.choice(sehirler)
        generic_qs = [
            (f"{kisi}, {sehir} gezisinde tarihi ve doğal güzellikleri fotoğraflamıştır. Hangisi doğal bir varlıktır?", "Peri Bacaları", ["Sümela Manastırı", "Topkapı Sarayı", "Galata Kulesi"]),
            ("Bilinçli bir tüketicinin alışveriş sırasında yapması gereken ilk davranış nedir?", "Ürünün son kullanma tarihini kontrol etmek", ["En pahalı ürünü almak", "Reklamı yapılanı seçmek", "Ambalajı yırtık ürünü almak"]),
            ("Allah'ın her şeyi işitmesi anlamına gelen sıfat hangisidir?", "Semi", ["İlim", "Basar", "Kudret"])
        ]
        q, ans, celd = random.choice(generic_qs)
        siklar = [ans] + celd
        random.shuffle(siklar)
        return {"ders": ders, "unite": unite, "soru": q, "gorsel_svg": None, "siklar": siklar, "dogru": ans, "kaynak": "Dinamik Sosyal/Din Motoru"}

# =========================================================
# 5. EŞİT DAĞILIMLI SORU ÜRETİM ALGORİTMASI (ROUND-ROBIN)
# =========================================================
def esit_dagilimli_soru_uret(secilen_uniteler, hedef_soru_sayisi):
    soru_havuzu = []
    üretilen_metinler = set()
    
    if not secilen_uniteler:
        return []
        
    u_count = len(secilen_uniteler)
    taban_soru = hedef_soru_sayisi // u_count
    kalan_soru = hedef_soru_sayisi % u_count
    
    # Her üniteye düşen soru sayısını hesapla (Eşit Dağılım)
    dagilim = [taban_soru + (1 if i < kalan_soru else 0) for i in range(u_count)]
    
    for index, (h_ders, h_unite) in enumerate(secilen_uniteler):
        istenen_adet = dagilim[index]
        üretilen_adet = 0
        deneme = 0
        
        while üretilen_adet < istenen_adet and deneme < 50:
            deneme += 1
            s = devasa_sablon_engine(h_ders, h_unite)
            
            # Filtreleme Kontrolleri
            if s["soru"] not in üretilen_metinler:
                if cevap_kontrolü_ve_temizlik(s["soru"], s["dogru"], s["siklar"]):
                    üretilen_metinler.add(s["soru"])
                    soru_havuzu.append(s)
                    üretilen_adet += 1
                    
    random.shuffle(soru_havuzu)
    return soru_havuzu

# =========================================================
# 6. STREAMLIT ARAYÜZÜ
# =========================================================
st.title("🎓 MEB 5. Sınıf Soru Bankası Test Sistemi")

st.sidebar.header("⚙️ Ünite ve Ders Seçimi")
secilen_uniteler = []

for ders_adi, uniteler in MEB_MUFREDAT.items():
    with st.sidebar.expander(f"📚 {ders_adi}", expanded=False):
        select_all = st.checkbox(f"Tüm {ders_adi} Üniteleri", key=f"all_{ders_adi}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
        for idx, u in enumerate(uniteler):
            cb = st.checkbox(u, value=select_all, key=f"cb_{ders_adi}_{idx}", disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])
            if cb:
                secilen_uniteler.append((ders_adi, u))

st.sidebar.divider()
soru_sayisi = st.sidebar.number_input("Toplam Soru Sayısı:", min_value=1, max_value=50, value=10, step=1, disabled=st.session_state["test_aktif"] or st.session_state["sorular_hazir"])

# --- HAZIRLIK EKRANI ---
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.subheader("📋 Test Oluşturma Paneli")
    if secilen_uniteler:
        st.success(f"Seçilen Ünite Sayısı: **{len(secilen_uniteler)}**. Seçilen tüm ünitelerden **eşit sayıda** soru dağıtılacaktır.")
        
        if st.button("🚀 Eşit Dağılımlı Soru Havuzunu Üret", type="primary"):
            with st.spinner("Sorular eşit oranlarda filtrelenerek üretiliyor..."):
                sorular = esit_dagilimli_soru_uret(secilen_uniteler, soru_sayisi)
                st.session_state["soru_listesi"] = sorular
                st.session_state["toplam_sure_sn"] = len(sorular) * 80
                st.session_state["sorular_hazir"] = True
                st.rerun()
    else:
        st.warning("⚠️ Lütfen sol taraftaki menüden en az 1 ünite seçin.")

# --- BAŞLATMA EKRANI ---
elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.success("✅ Sorular başarıyla oluşturuldu! Şıklarda çakışma ve cevap sızıntısı engellendi.")
    
    toplam_sn = st.session_state["toplam_sure_sn"]
    st.markdown(f"**Toplam Soru Sayısı:** {len(st.session_state['soru_listesi'])} | **Süre:** {toplam_sn // 60} Dk {toplam_sn % 60} Sn")
    
    col1, col2 = st.columns(2)
    if col1.button("⏱️ Testi Başlat", type="primary"):
        st.session_state["test_aktif"] = True
        st.session_state["baslangic_zamani"] = time.time()
        st.session_state["kullanici_cevaplari"] = {}
        st.session_state["mevcut_soru_index"] = 0
        st.rerun()
        
    if col2.button("🔄 Ayarları Sıfırla"):
        st.session_state["sorular_hazir"] = False
        st.rerun()

# --- AKTİF TEST EKRANI ---
elif st.session_state["test_aktif"]:
    gecen_sure = int(time.time() - st.session_state["baslangic_zamani"])
    kalan_sure = st.session_state["toplam_sure_sn"] - gecen_sure

    if kalan_sure <= 0:
        st.warning("⏰ Süreniz doldu!")
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = True
        st.rerun()

    idx = st.session_state["mevcut_soru_index"]
    q = st.session_state["soru_listesi"][idx]

    c_left, c_right = st.columns([3, 1])
    c_left.caption(f"📌 {q['ders']} - {q['unite']}")
    c_right.metric("⏳ Kalan Süre", f"{kalan_sure // 60:02d}:{kalan_sure % 60:02d}")

    st.markdown(f"### **Soru {idx + 1}:** {q['soru']}")

    if q.get("gorsel_svg"):
        st.components.v1.html(q["gorsel_svg"], height=155)

    onceki_cevap = st.session_state["kullanici_cevaplari"].get(idx, None)
    secim_index = q["siklar"].index(onceki_cevap) if onceki_cevap in q["siklar"] else None

    secim = st.radio("Şıkkınızı seçin:", q["siklar"], index=secim_index, key=f"radio_{idx}")
    if secim:
        st.session_state["kullanici_cevaplari"][idx] = secim

    st.divider()
    b1, b2 = st.columns(2)
    if idx > 0 and b1.button("⬅️ Önceki Soru"):
        st.session_state["mevcut_soru_index"] -= 1
        st.rerun()

    if idx + 1 < len(st.session_state["soru_listesi"]):
        if b2.button("Sonraki Soru ➡️", type="primary"):
            st.session_state["mevcut_soru_index"] += 1
            st.rerun()
    else:
        if b2.button("🏁 Testi Bitir", type="primary"):
            st.session_state["test_aktif"] = False
            st.session_state["test_bitti"] = True
            st.rerun()

# --- SONUÇ EKRANI ---
elif st.session_state["test_bitti"]:
    st.balloons()
    st.header("📊 Test Sonu Karnesi")
    
    toplam = len(st.session_state["soru_listesi"])
    dogru = sum(1 for i, q in enumerate(st.session_state["soru_listesi"]) if st.session_state["kullanici_cevaplari"].get(i) == q["dogru"])
    
    st.metric("Doğru / Toplam", f"{dogru} / {toplam}")
    st.progress(dogru / toplam if toplam > 0 else 0)
    
    if st.button("🔄 Yeni Test Yap"):
        st.session_state["sorular_hazir"] = False
        st.session_state["test_bitti"] = False
        st.session_state["test_aktif"] = False
        st.rerun()
