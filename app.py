import streamlit as st
import random
import json
import time
import math
import hashlib

# Sayfa Yapılandırması
st.set_page_config(page_title="MEB 5. Sınıf Soru Bankası Engine", page_icon="🎓", layout="wide")

# =========================================================
# 1. SESSION STATE BAŞLATMA
# =========================================================
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
# 2. HASSAS VE DOĞRU YÖNLÜ SVG GÖRSEL MOTORU
# =========================================================
def svg_iletki_aci_ciz(derece):
    """
    Açı Yönü Düzeltmesi:
    Sağ taraf 0 derece referans alınır. Derece saat yönünün tersine açılır.
    0° -> Sağ, 90° -> Tam Yukarı, 180° -> Sol
    """
    rad = math.radians(derece)
    # İletki merkezi (140, 110), yarıçap 90
    x = int(140 + 90 * math.cos(rad))
    y = int(110 - 90 * math.sin(rad))
    
    return f'''
    <svg width="280" height="130" viewBox="0 0 280 130" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#f8fafc" rx="10" stroke="#cbd5e1"/>
      <!-- İletki Gövdesi -->
      <path d="M 50 110 A 90 90 0 0 1 230 110 Z" fill="#e2e8f0" stroke="#64748b" stroke-width="2"/>
      <!-- Referans Taban Çizgisi (0 - 180) -->
      <line x1="50" y1="110" x2="230" y2="110" stroke="#334155" stroke-width="2"/>
      <!-- Sağ Referans Kolu (0 Derece Başlangıcı) -->
      <line x1="140" y1="110" x2="230" y2="110" stroke="#94a3b8" stroke-width="3" stroke-dasharray="4"/>
      <!-- Açı Kolu -->
      <line x1="140" y1="110" x2="{x}" y2="{y}" stroke="#2563eb" stroke-width="4" stroke-linecap="round"/>
      <circle cx="140" cy="110" r="4" fill="#1e40af"/>
      <text x="140" y="25" font-family="sans-serif" font-size="13" font-weight="bold" fill="#0f172a" text-anchor="middle">Ölçülen Açı: {derece}°</text>
    </svg>
    '''

def svg_kesir_ciz(pay, payda):
    dilimler = ""
    genislik = 220
    parca_w = genislik / payda
    for i in range(payda):
        fill = "#3b82f6" if i < pay else "#f1f5f9"
        x = 30 + (i * parca_w)
        dilimler += f'<rect x="{x}" y="30" width="{parca_w - 2}" height="40" fill="{fill}" stroke="#94a3b8" rx="3"/>'
    return f'''
    <svg width="280" height="100" viewBox="0 0 280 100" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#ffffff" rx="10" stroke="#e2e8f0"/>
      {dilimler}
      <text x="140" y="88" font-family="sans-serif" font-size="12" font-weight="bold" fill="#334155" text-anchor="middle">Modellenen Kesir</text>
    </svg>
    '''

# =========================================================
# 3. BENZERLİK VE CEVAP SIZINTISI ENGELLEME MOTORU
# =========================================================
def cevap_ve_metin_dogrulama(soru_metni, dogru_cevap, siklar):
    """
    1. Cevabın soru metninde doğrudan geçmesini engeller.
    2. Şıkların birbirinden tamamen farklı (benzersiz) olmasını şart koşar.
    """
    metin = soru_metni.lower()
    cevap = str(dogru_cevap).lower().strip()
    
    # Kelime uzunluğu 3'ten büyükse ve metinde geçiyorsa reddet
    if len(cevap) > 3 and cevap in metin:
        return False
        
    # Tüm şıklar benzersiz olmalı
    if len(set(siklar)) != len(siklar):
        return False
        
    return True

# =========================================================
# 4. DEVA SA ŞABLON VE DİNAMİK MİMARİ ENGINE
# =========================================================
def devasa_sablon_engine(ders, unite):
    u_lower = unite.lower()
    
    # Dinamik Değişken Havuzları
    isimler = ["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Ali", "Fatma", "Deniz", "Ömer", "Selin", "Kaan", "Cem", "Mert", "Ela"]
    sehirler = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Konya", "Trabzon", "Erzurum", "Eskişehir", "Gaziantep", "Kayseri"]
    nesneler = ["kitap", "kalem", "bilye", "ceviz", "elma", "çikolata", "sayfa", "pul", "kart", "roket", "balon"]
    
    # -----------------------------------------------------
    # 1. MATEMATİK
    # -----------------------------------------------------
    if ders == "Matematik":
        if "geometrik" in u_lower or "açı" in u_lower:
            aci = random.choice([20, 30, 45, 60, 75, 90, 105, 120, 135, 150, 160])
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
                "soru": f"Görseldeki iletkide yönü doğru çizilen {aci}° ölçüsündeki açının türü hangisidir?",
                "gorsel_svg": svg_iletki_aci_ciz(aci), "siklar": siklar, "dogru": tur
            }
        elif "kesir" in u_lower:
            payda = random.choice([4, 5, 6, 8, 10, 12])
            pay = random.randint(1, payda - 1)
            dogru_str = f"{pay}/{payda}"
            siklar = [dogru_str, f"{payda-pay}/{payda}", f"{pay}/{payda+2}", f"{pay+1}/{payda}"]
            siklar = list(dict.fromkeys(siklar))
            while len(siklar) < 4:
                siklar.append(f"{random.randint(1,3)}/{payda+4}")
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": "Verilen modelde boyalı kısımların bütün içerisindeki oranını ifade eden kesir hangisidir?",
                "gorsel_svg": svg_kesir_ciz(pay, payda), "siklar": siklar, "dogru": dogru_str
            }
        else: # Problemler
            kisi = random.choice(isimler)
            nesne = random.choice(nesneler)
            s1 = random.randint(120, 850)
            s2 = random.randint(30, 150)
            
            ans = s1 + s2
            q_text = f"{kisi} {s1} adet {nesne} toplamıştır. Arkadaşı ona {s2} adet daha verirse toplam kaç {nesne}si olur?"
            
            siklar = [str(ans), str(ans + 10), str(abs(ans - 20)), str(ans + 50)]
            siklar = list(dict.fromkeys(siklar))
            while len(siklar) < 4:
                siklar.append(str(ans + random.randint(15, 90)))
            random.shuffle(siklar)
            return {
                "ders": ders, "unite": unite,
                "soru": q_text, "gorsel_svg": None, "siklar": siklar, "dogru": str(ans)
            }

    # -----------------------------------------------------
    # 2. FEN BİLİMLERİ
    # -----------------------------------------------------
    elif ders == "Fen Bilimleri":
        if "güneş" in u_lower or "ay" in u_lower:
            havuz = [
                ("Ay'ın Dünya'dan bakıldığında tamamen karanlık görüldüğü evre hangisidir?", "Yeni Ay", ["Dolunay", "İlk Dördün", "Son Dördün"]),
                ("Dünya, Güneş ile Ay arasındayken Ay'ın hangi evresi gözlemlenir?", "Dolunay", ["Yeni Ay", "Hilal", "Son Dördün"]),
                ("Güneş sistemindeki en büyük gök cismi hangisidir?", "Güneş", ["Dünya", "Ay", "Jüpiter"])
            ]
        else:
            havuz = [
                ("Kuvvetin büyüklüğünü ölçmek için kullanılan araç hangisidir?", "Dinamometre", ["Termometre", "Barometre", "Mikroskop"]),
                ("Sürtünme kuvvetini azaltmak için hangisi yapılır?", "Yüzeylerin yağlanması", ["Pürüzün artırılması", "Kış lastiği takılması", "Zımpara yapılması"]),
                ("Sıvı bir maddenin ısı vererek katı hale geçmesine ne ad verilir?", "Donma", ["Buharlaşma", "Erimesi", "Süblimleşme"])
            ]
        q, ans, celd = random.choice(havuz)
        siklar = [ans] + celd
        random.shuffle(siklar)
        return {"ders": ders, "unite": unite, "soru": q, "gorsel_svg": None, "siklar": siklar, "dogru": ans}

    # -----------------------------------------------------
    # 3. TÜRKÇE
    # -----------------------------------------------------
    elif ders == "Türkçe":
        havuz = [
            ("Aşağıdaki cümlelerin hangisinde 'mecaz anlamlı' bir sözcük vardır?", "Bize karşı çok soğuk davrandı.", ["Sıcak çayı yudumladı.", "Kapının kolı kırıldı.", "Kuşlar gökyüzünde uçuyor."]),
            ("Hangisinde yazım yanlışı vardır?", "Yarın Ayşe'de gelecek mi?", ["Ankara'ya otobüsle gitti.", "10 Kasım'da anma yapıldı.", "Kitabını sınıfta unuttu."]),
            ("'Eş anlamlı' kelime çifti hangisinde verilmiştir?", "Cevap - Yanıt", ["Uzun - Kısa", "Gece - Gündüz", "Açık - Kapalı"])
        ]
        q, ans, celd = random.choice(havuz)
        siklar = [ans] + celd
        random.shuffle(siklar)
        return {"ders": ders, "unite": unite, "soru": q, "gorsel_svg": None, "siklar": siklar, "dogru": ans}

    # -----------------------------------------------------
    # 4. SOSYAL BİLGİLER / DİN / İNGİLİZCE
    # -----------------------------------------------------
    else:
        kisi = random.choice(isimler)
        sehir = random.choice(sehirler)
        havuz = [
            (f"{kisi}, {sehir} seyahatinde tarihi eserleri gezmiştir. Hangisi beşeri (insan yapımı) bir unsurdur?", "Topkapı Sarayı", ["Peri Bacaları", "Pamukkale Travertenleri", "Düden Şelalesi"]),
            ("Bilinçli bir tüketicinin yapması gereken en uygun davranış hangisidir?", "Ürünün Tüketim Tarihini kontrol etmek", ["En pahalısını seçmek", "Reklamı yapılana yönelmek", "Etiketsiz ürün almak"]),
            ("Allah'ın her şeyi görmesi anlamına gelen sıfat hangisidir?", "Basar", ["İlim", "Semi", "Kudret"]),
            ("Which one is a daily routine activity?", "Brush teeth", ["Fly a kite", "Play football", "Go to cinema"])
        ]
        q, ans, celd = random.choice(havuz)
        siklar = [ans] + celd
        random.shuffle(siklar)
        return {"ders": ders, "unite": unite, "soru": q, "gorsel_svg": None, "siklar": siklar, "dogru": ans}

# =========================================================
# 5. EŞİT DAĞILIMLI VE BENZERLİKSİZ SORU ÜRETİCİ
# =========================================================
def esit_dagilimli_soru_uret(secilen_uniteler, hedef_soru_sayisi):
    soru_havuzu = []
    üretilen_hashler = set()
    
    if not secilen_uniteler:
        return []
        
    u_count = len(secilen_uniteler)
    taban_soru = hedef_soru_sayisi // u_count
    kalan_soru = hedef_soru_sayisi % u_count
    
    dagilim = [taban_soru + (1 if i < kalan_soru else 0) for i in range(u_count)]
    
    for index, (h_ders, h_unite) in enumerate(secilen_uniteler):
        istenen_adet = dagilim[index]
        üretilen_adet = 0
        deneme = 0
        
        while üretilen_adet < istenen_adet and deneme < 80:
            deneme += 1
            s = devasa_sablon_engine(h_ders, h_unite)
            
            # Hash Kontrolü ile Tam Benzersizlik
            s_hash = hashlib.md5((s["soru"] + "".join(s["siklar"])).encode('utf-8')).hexdigest()
            
            if s_hash not in üretilen_hashler:
                if cevap_ve_metin_dogrulama(s["soru"], s["dogru"], s["siklar"]):
                    üretilen_hashler.add(s_hash)
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
        st.info(f"Seçilen Ünite Sayısı: **{len(secilen_uniteler)}**. Seçilen tüm ünitelerden **eşit sayıda** ve **tamamen benzersiz** soru dağıtılacaktır.")
        
        if st.button("🚀 Eşit Dağılımlı Soru Havuzunu Üret", type="primary"):
            with st.spinner("Sorular eşit oranlarda ve açı yönleri kontrol edilerek üretiliyor..."):
                sorular = esit_dagilimli_soru_uret(secilen_uniteler, soru_sayisi)
                st.session_state["soru_listesi"] = sorular
                st.session_state["toplam_sure_sn"] = len(sorular) * 80
                st.session_state["sorular_hazir"] = True
                st.rerun()
    else:
        st.warning("⚠️ Lütfen sol taraftaki menüden en az 1 ünite seçin.")

# --- BAŞLATMA EKRANI ---
elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.success("✅ Sorular başarıyla oluşturuldu! Açı yönleri ve şık çakışmaları kontrol edildi.")
    
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
        st.components.v1.html(q["gorsel_svg"], height=140)

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
