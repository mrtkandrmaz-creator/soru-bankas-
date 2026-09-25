import streamlit as st
import random
import time
import hashlib

st.set_page_config(page_title="MEB 5. Sınıf Soru Bankası & Deneme Sınavı Motoru", page_icon="🎓", layout="wide")

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

# =========================================================
# 2. DERSLER VE MEB MÜFREDAT SIRASI
# =========================================================
DERS_ONCELIK_SIRASI = [
    "Türkçe",
    "Matematik",
    "Fen Bilimleri",
    "Sosyal Bilgiler",
    "Din Kültürü ve Ahlak Bilgisi",
    "İngilizce",
    "🏆 Bilgi Yarışması"
]

MEB_MUFREDAT = {
    "Türkçe": [
        "1. Tema: Sözcükte Anlam ve Mantık Muhakeme",
        "2. Tema: Cümlede Anlam ve Metin Türleri",
        "3. Tema: Paragraf Analizi ve Görsel Okuma",
        "4. Tema: Noktalama İşaretleri ve Yazım Kuralları"
    ],
    "Matematik": [
        "1. Ünite: Doğal Sayılar ve İşlemler",
        "2. Ünite: Kesirler ve Kesirlerle İşlemler",
        "3. Ünite: Ondalık Gösterim ve Yüzdeler",
        "4. Ünite: Temel Geometrik Kavramlar ve Açı Ölçme",
        "5. Ünite: Üçgende Açılar ve Üçgen Çeşitleri",
        "6. Ünite: Veri İşleme ve Ölçme"
    ],
    "Fen Bilimleri": [
        "1. Ünite: Güneş, Dünya ve Ay",
        "2. Ünite: Canlılar Dünyası",
        "3. Ünite: Kuvvetin Ölçülmesi ve Sürtünme",
        "4. Ünite: Madde ve Değişim",
        "5. Ünite: Işığın Yayılması ve Tam Gölge"
    ],
    "Sosyal Bilgiler": [
        "1. Ünite: Birey ve Toplum (Hak ve Sorumluluklar)",
        "2. Ünite: Kültür ve Miras",
        "3. Ünite: İnsanlar, Yerler ve Çevreler",
        "4. Ünite: Bilim, Teknoloji ve Toplum"
    ],
    "Din Kültürü ve Ahlak Bilgisi": [
        "1. Ünite: Allah İnancı",
        "2. Ünite: Ramazan ve Oruç",
        "3. Ünite: Adap ve Nezaket"
    ],
    "İngilizce": [
        "Unit 1: Hello! & Nationalities",
        "Unit 2: My Town & Directions",
        "Unit 3: Games and Hobbies",
        "Unit 4: My Daily Routine"
    ],
    "🏆 Bilgi Yarışması": [
        "1. Kategori: Dünya Başkentleri ve Coğrafya",
        "2. Kategori: Türk Mutfağı ve Yöresel Lezzetler",
        "3. Kategori: Dünya Mutfakları ve Lezzetler",
        "4. Kategori: Harita Bilgisi ve Yönler",
        "5. Kategori: Bilim Tarihi ve İcatlar",
        "6. Kategori: Genel Kültür ve Doğa Harikaları",
        "7. Kategori: Popüler Kültür",
        "8. Kategori: Spor ve Müzik"
    ]
}

MEB_HAFTALIK_MAPI = {}
for h in range(1, 41):
    MEB_HAFTALIK_MAPI[h] = []
    t_idx = min((h - 1) // 10, len(MEB_MUFREDAT["Türkçe"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Türkçe", MEB_MUFREDAT["Türkçe"][t_idx]))

    m_idx = min((h - 1) // 7, len(MEB_MUFREDAT["Matematik"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Matematik", MEB_MUFREDAT["Matematik"][m_idx]))

    f_idx = min((h - 1) // 8, len(MEB_MUFREDAT["Fen Bilimleri"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Fen Bilimleri", MEB_MUFREDAT["Fen Bilimleri"][f_idx]))

    s_idx = min((h - 1) // 10, len(MEB_MUFREDAT["Sosyal Bilgiler"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Sosyal Bilgiler", MEB_MUFREDAT["Sosyal Bilgiler"][s_idx]))

    d_idx = min((h - 1) // 13, len(MEB_MUFREDAT["Din Kültürü ve Ahlak Bilgisi"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("Din Kültürü ve Ahlak Bilgisi", MEB_MUFREDAT["Din Kültürü ve Ahlak Bilgisi"][d_idx]))

    i_idx = min((h - 1) // 10, len(MEB_MUFREDAT["İngilizce"]) - 1)
    MEB_HAFTALIK_MAPI[h].append(("İngilizce", MEB_MUFREDAT["İngilizce"][i_idx]))

ISIMLER = ["Ahmet", "Zeynep", "Elif", "Mehmet", "Can", "Ece", "Burak", "Ayşe", "Kaan", "Duru", "Bora", "Selin", "Mert", "Deniz", "Kerem"]

# =========================================================
# 3. MEB SORU TİPLERİNE UYGUN DİNAMİK SORU ÜRETİCİ
# =========================================================
def dinamik_soru_uret(ders, unite):
    kisi = random.choice(ISIMLER)
    
    if ders == "Matematik":
        tip = random.choice(["islem", "problem", "sayi_oruntusu"])
        if tip == "islem":
            a = random.randint(1200, 8900)
            b = random.randint(300, 1500)
            islem_turu = random.choice(["toplam", "fark"])
            if islem_turu == "toplam":
                dogru = a + b
                soru = f"<b>[İşlem Sorusu]</b> İşlemin sonucu kaçtır?<br><br><b>{a} + {b} = ?</b>"
            else:
                if a < b: a, b = b, a
                dogru = a - b
                soru = f"<b>[İşlem Sorusu]</b> İşlemin sonucu kaçtır?<br><br><b>{a} - {b} = ?</b>"
            
            y1 = dogru + random.randint(5, 25)
            y2 = dogru - random.randint(3, 20)
            y3 = dogru + random.randint(30, 80)
            siklar = [str(dogru), str(y1), str(y2), str(y3)]
            return {"soru": soru, "siklar": siklar, "dogru": str(dogru)}
            
        elif tip == "problem":
            urun = random.choice(["bilgisayar", "bisiklet", "televizyon", "tablet"])
            fiyat = random.randint(1500, 6000)
            taksit = random.choice([4, 6, 8, 10])
            dogru = fiyat // taksit
            # Tam bölünme garantisi için ayarlayalım
            fiyat = dogru * taksit
            
            y1 = dogru + random.choice([25, 50, 100])
            y2 = dogru - random.randint(10, 40)
            y3 = dogru + random.randint(150, 250)
            siklar = [str(dogru), str(y1), str(y2), str(y3)]
            return {
                "soru": f"<b>[Problem Analizi]</b> {kisi}, fiyatı <b>{fiyat} TL</b> olan bir {urun} satın almıştır. Bu tutarı <b>{taksit}</b> eşit taksitte ödeyeceğine göre, bir aylık taksit tutarı kaç TL olur?",
                "siklar": siklar,
                "dogru": str(dogru)
            }
        else:
            baslangic = random.randint(5, 20)
            artis = random.randint(3, 9)
            dizi = [baslangic + i * artis for i in range(4)]
            dogru = dizi[-1] + artis
            soru = f"<b>[Örüntü Sorusu]</b> Aşağıdaki sayı örüntüsünde soru işaretli (?) yerine hangi sayı gelmelidir?<br><br><b>{dizi[0]} - {dizi[1]} - {dizi[2]} - {dizi[3]} - ?</b>"
            y1 = dogru + artis
            y2 = dogru - 2
            y3 = dogru + 5
            siklar = [str(dogru), str(y1), str(y2), str(y3)]
            return {"soru": soru, "siklar": siklar, "dogru": str(dogru)}

    elif ders == "Fen Bilimleri":
        tip = random.choice(["oncul", "tablo", "yorumlama"])
        if tip == "oncul":
            dogru = "Yalnız I ve II"
            yanlislar = ["Yalnız III", "I, II ve III", "Yalnız II"]
            return {
                "soru": f"<b>[Öncüllü Soru]</b> {kisi}, Güneş, Dünya ve Ay ile ilgili şu bilgileri vermiştir:<br>I. Güneş kendi ekseni etrafında döner.<br>II. Dünya'nın tek doğal uydusu Ay'dır.<br>III. Ay'ın kendi ışık kaynağı vardır.<br><br><b>Yukarıdaki ifadelerden hangileri doğrudur?</b>",
                "siklar": [dogru] + yanlislar,
                "dogru": dogru
            }
        elif tip == "tablo":
            dogru = "Güneş, Dünya'dan çok daha büyük ve sıcaktır."
            yanlislar = [
                "Dünya, Güneş'ten daha büyüktür.",
                "Ay, Güneş ile aynı boyuttadır.",
                "Güneş ve Ay'ın sıcaklık değerleri eşittir."
            ]
            return {
                "soru": f"<b>[Karşılaştırma Soru Tipi]</b> {kisi} gök cisimlerinin büyüklük ve sıcaklık özelliklerini karşılaştırıyor. Aşağıdaki yargılardan hangisi bilimsel olarak doğrudur?",
                "siklar": [dogru] + yanlislar,
                "dogru": dogru
            }
        else:
            dogru = "Yeniay -> İlk Dördün -> Dolunay -> Son Dördün"
            yanlislar = [
                "Dolunay -> Yeniay -> Son Dördün -> İlk Dördün",
                "İlk Dördün -> Dolunay -> Yeniay -> Son Dördün",
                "Yeniay -> Dolunay -> İlk Dördün -> Son Dördün"
            ]
            return {
                "soru": f"<b>[Görsel / Sıralama Soru Tipi]</b> Ay'ın ana evrelerinin doğru kronolojik sıralaması hangi seçenekte eksiksiz verilmiştir?",
                "siklar": [dogru] + yanlislar,
                "dogru": dogru
            }

    elif ders == "Türkçe":
        tip = random.choice(["sozcuk_anlam", "cumle_anlam", "noktalama"])
        if tip == "sozcuk_anlam":
            dogru = "Güneş yavaş yavaş tepelerin arkasından görünmeye başladı."
            yanlislar = [
                "Bu mont kardeşime biraz küçük geldi.",
                "Toplantıdan en son ben ayrıldım.",
                "Merdivenleri çıkarken nefes nefese kaldı."
            ]
            return {
                "soru": f"<b>[Sözcükte Anlam]</b> 'Çıkmak' sözcüğü aşağıdaki cümlelerin hangisinde <u>'ortaya çıkmak, görünmek'</u> anlamında kullanılmıştır?",
                "siklar": [dogru] + yanlislar,
                "dogru": dogru
            }
        elif tip == "cumle_anlam":
            dogru = "Hava sağanak yağışlı olduğundan maç ertelendi."
            yanlislar = [
                "Başarılı olmak için her gün düzenli ders çalışıyor.",
                "Sabah uyanınca elini yüzünü yıkadı.",
                "Yarın akşam eski arkadaşlarıyla buluşacak."
            ]
            return {
                "soru": f"<b>[Cümlede Anlam]</b> Aşağıdaki cümlelerin hangisinde <u>neden-sonuç (gerekçe)</u> ilişkisi vardır?",
                "siklar": [dogru] + yanlislar,
                "dogru": dogru
            }
        else:
            dogru = "Eyvah, elimdeki bardak yere düştü!"
            yanlislar = [
                "Bugün okulda hangi dersleri işlediniz?",
                "Ödevlerimi bitirip odamı topladım.",
                "Ankara Türkiye'nin başkentidir."
            ]
            return {
                "soru": f"<b>[Noktalama İşaretleri]</b> Aşağıdaki cümlelerin hangisinde <u>ünlem işareti (!)</u> yanlış ya da gereksiz kullanılmıştır?",
                "siklar": [dogru] + yanlislar,
                "dogru": dogru
            }

    elif ders == "Sosyal Bilgiler":
        dogru = "Aile bütçesine katkı sağlamak ve ortak ev işlerinde yardımlaşmak"
        yanlislar = [
            "Evdeki tüm kuralları tek başına değiştirmek",
            "Gün boyu sadece kendi odasında vakit geçirmek",
            "Hiçbir sorumluluk almadan dışarıda oyun oynamak"
        ]
        return {
            "soru": f"<b>[Sözel Mantık / Öncül]</b> {kisi}, 'Birey ve Toplum' ünitesinde ev içi hak ve sorumlulukları incelemektedir. Buna göre bir çocuğun ev içerisindeki temel sorumluluklarından biri hangisidir?",
            "siklar": [dogru] + yanlislar,
            "dogru": dogru
        }

    elif ders == "Din Kültürü ve Ahlak Bilgisi":
        dogru = "Evrendeki kusursuz düzen, uyum ve planlı yaratılış"
        yanlislar = [
            "Evrenin tamamen tesadüfi olaylarla var olması",
            "Doğadaki varlıkların hiçbir amaca hizmet etmemesi",
            "Mevsim döngülerinin tamamen düzensiz gerçekleşmesi"
        ]
        return {
            "soru": f"<b>[Kavram Analizi]</b> {kisi}, 'Allah İnancı' ünitesinde evrendeki nizamı araştırmaktadır. Aşağıdakilerden hangisi Yaratıcı'nın varlığına ve birliğine delil gösterilebilir?",
            "siklar": [dogru] + yanlislar,
            "dogru": dogru
        }

    elif ders == "İngilizce":
        dogru = "I am from Turkey and I am Turkish."
        yanlislar = [
            "I like playing football and tennis.",
            "My school starts at nine o'clock.",
            "I get up early in the morning."
        ]
        return {
            "soru": f"<b>[Diyalog / Tanışma]</b> {kisi} İngilizce dersinde kendisini tanıtmaktadır. Hangi ifade {kisi}'nin ülkesini ve milliyetini belirtir?",
            "siklar": [dogru] + yanlislar,
            "dogru": dogru
        }

    else:
        secimler = [
            ("Türkiye Cumhuriyeti'nin başkenti hangi şehirdir?", "Ankara", ["İstanbul", "İzmir", "Bursa"]),
            ("Dünyanın en büyük okyanusu hangisidir?", "Pasifik Okyanusu", ["Atlantik Okyanusu", "Hint Okyanusu", "Arktik Okyanusu"]),
            ("Yer kabuğunun ana maddesi nedir?", "Kayaçlar ve mineraller", ["Sadece su kütleleri", "Saf demir tabakası", "Gaz bulutları"])
        ]
        q, ans, celd = random.choice(secimler)
        return {"soru": f"<b>[Genel Kültür]</b> {q}", "siklar": [ans] + celd, "dogru": ans}

def ders_sirali_ve_dengeli_uret(secilen_uniteler, hedef_sayi):
    if not secilen_uniteler:
        return []

    sirali_uniteler = []
    for d in DERS_ONCELIK_SIRASI:
        for item in secilen_uniteler:
            if item[0] == d and item not in sirali_uniteler:
                sirali_uniteler.append(item)
                
    toplam_secilen = len(sirali_uniteler)
    temel_pay = hedef_sayi // toplam_secilen
    kalan = hedef_sayi % toplam_secilen

    ham_soru_listesi = []
    hash_set = set()

    for idx, (ders, unite) in enumerate(sirali_uniteler):
        bu_unite_hedef = temel_pay + (1 if idx < kalan else 0)
        uretilen = 0
        
        while uretilen < bu_unite_hedef:
            s = dinamik_soru_uret(ders, unite)
            s["ders"] = ders
            s["unite"] = unite
            
            correct_ans = s["dogru"]
            random.shuffle(s["siklar"])
            if correct_ans not in s["siklar"]:
                s["siklar"][0] = correct_ans
                random.shuffle(s["siklar"])
                
            fingerprint = hashlib.sha256((s["soru"] + str(s["siklar"])).encode('utf-8')).hexdigest()
            if fingerprint not in hash_set:
                hash_set.add(fingerprint)
                ham_soru_listesi.append(s)
                uretilen += 1

    nihai_liste = []
    for ders_adi in DERS_ONCELIK_SIRASI:
        ders_sorulari = [s for s in ham_soru_listesi if s["ders"] == ders_adi]
        nihai_liste.extend(ders_sorulari)

    return nihai_liste[:hedef_sayi]

# =========================================================
# 4. STREAMLIT ARAYÜZÜ (SOL MENÜ)
# =========================================================
st.title("🎓 MEB 5. Sınıf Soru Bankası & Deneme Sınavı Motoru")
st.sidebar.header("⚙️ Müfredat ve Sınav Ayarları")

is_disabled = st.session_state["test_aktif"] or st.session_state["sorular_hazir"]

with st.sidebar.expander("📌 Çalışma Modu Seçiniz", expanded=True):
    mod_deneme = st.checkbox("📅 40 Haftalık MEB Deneme Sınavları", value=False, disabled=is_disabled)
    mod_serbest = st.checkbox("📚 Serbest Konu / Ünite Seçimi", value=False, disabled=is_disabled)
    mod_bilgi = st.checkbox("🏆 Bilgi Yarışması Modu", value=False, disabled=is_disabled)

secilen_uniteler = []
deneme_secimleri = []

if mod_deneme:
    with st.sidebar.expander("📅 40 Haftalık MEB Deneme Sınavları", expanded=True):
        for h in range(1, 41):
            if st.checkbox(f"{h}. Hafta Deneme Sınavı", value=False, disabled=is_disabled, key=f"deneme_cb_{h}"):
                deneme_secimleri.append(h)
        for h in deneme_secimleri:
            for k in range(1, h + 1):
                secilen_uniteler.extend(MEB_HAFTALIK_MAPI[k])

if mod_serbest:
    st.sidebar.subheader("📚 Ünite Seçimi")
    for ders_adi in DERS_ONCELIK_SIRASI[:-1]:
        uniteler = MEB_MUFREDAT[ders_adi]
        with st.sidebar.expander(f"{ders_adi}", expanded=False):
            select_all = st.checkbox(f"Tümünü Seç ({ders_adi})", value=False, key=f"all_{ders_adi}", disabled=is_disabled)
            for idx, u in enumerate(uniteler):
                if st.checkbox(u, value=select_all, key=f"cb_{ders_adi}_{idx}", disabled=is_disabled):
                    secilen_uniteler.append((ders_adi, u))

if mod_bilgi:
    with st.sidebar.expander("🏆 Bilgi Yarışması Kategorileri", expanded=True):
        select_all_bilgi = st.checkbox("Tüm Bilgi Yarışması Kategorilerini Seç", value=False, key="all_Bilgi_Yarismasi", disabled=is_disabled)
        for idx, u in enumerate(MEB_MUFREDAT["🏆 Bilgi Yarışması"]):
            if st.checkbox(u, value=select_all_bilgi, key=f"cb_Bilgi_Yarismasi_{idx}", disabled=is_disabled):
                secilen_uniteler.append(("🏆 Bilgi Yarışması", u))

st.sidebar.divider()
soru_sayisi = st.sidebar.slider("Toplam Soru Sayısı:", min_value=20, max_value=100, value=20, step=5, disabled=is_disabled)

st.sidebar.write("")
if not st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🚀 Hazırla ve Başlat", type="primary", use_container_width=True):
        if secilen_uniteler:
            status_box = st.empty()
            progress_bar = st.progress(0)
            
            for sn in range(3, 0, -1):
                progress_bar.progress(int((4 - sn) * 25))
                status_box.info(f"🔄 Tamamen özgün MEB tarzı sorular üretiliyor... ({sn}s)")
                time.sleep(0.5)
            
            sorular = ders_sirali_ve_dengeli_uret(secilen_uniteler, soru_sayisi)
            
            progress_bar.progress(100)
            status_box.success("✅ Sorular başarıyla oluşturuldu!")
            time.sleep(0.5)
            
            st.session_state["soru_listesi"] = sorular
            st.session_state["toplam_sure_sn"] = len(sorular) * 90
            st.session_state["sorular_hazir"] = True
            st.rerun()
        else:
            st.sidebar.error("⚠️ Lütfen en az bir mod ve ünite seçimi yapın!")

elif st.session_state["sorular_hazir"] and not st.session_state["test_aktif"]:
    if st.sidebar.button("🔄 Yeniden Hazırla", use_container_width=True):
        st.session_state["sorular_hazir"] = False
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = False
        st.rerun()

# =========================================================
# 5. TEST EKRANI
# =========================================================
if st.session_state["sorular_hazir"] and not st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    st.info(f"🎉 **{len(st.session_state['soru_listesi'])} adet özgün soru** hazır!")
    if st.button("🏁 Sınavı Şimdi Başlat", type="primary", use_container_width=True):
        st.session_state["test_aktif"] = True
        st.session_state["baslangic_zamani"] = time.time()
        st.rerun()

if st.session_state["test_aktif"] and not st.session_state["test_bitti"]:
    top_col1, top_col2 = st.columns([4, 1])
    with top_col1:
        st.info("💡 İstediğin an testi sonlandırıp puanını ve detaylı cevap anahtarını görebilirsin.")
    with top_col2:
        if st.button("🏁 Sınavı Bitir", type="secondary", use_container_width=True):
            st.session_state["test_aktif"] = False
            st.session_state["test_bitti"] = True
            st.rerun()

    soru_listesi = st.session_state["soru_listesi"]
    idx = st.session_state["mevcut_soru_index"]
    
    if idx < len(soru_listesi):
        s = soru_listesi[idx]
        
        st.subheader(f"Soru {idx + 1} / {len(soru_listesi)} | Ders: **{s['ders']}** ({s['unite']})")
        st.markdown(s["soru"], unsafe_allow_html=True)
        
        onceki_cevap = st.session_state["kullanici_cevaplari"].get(idx)
        secim_index = s["siklar"].index(onceki_cevap) if onceki_cevap in s["siklar"] else None
            
        secim = st.radio(
            "Seçenekleriniz:", 
            s["siklar"], 
            key=f"soru_r_{idx}",
            index=secim_index
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if idx > 0 and st.button("⬅️ Önceki Soru"):
                if secim is not None:
                    st.session_state["kullanici_cevaplari"][idx] = secim
                st.session_state["mevcut_soru_index"] -= 1
                st.rerun()
        with col2:
            if idx < len(soru_listesi) - 1:
                if st.button("Sonraki Soru ➡️", type="primary"):
                    if secim is not None:
                        st.session_state["kullanici_cevaplari"][idx] = secim
                    st.session_state["mevcut_soru_index"] += 1
                    st.rerun()
            else:
                if st.button("🏁 Sınavı Bitir ve Puanı Gör", type="primary"):
                    if secim is not None:
                        st.session_state["kullanici_cevaplari"][idx] = secim
                    st.session_state["test_aktif"] = False
                    st.session_state["test_bitti"] = True
                    st.rerun()
    else:
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = True
        st.rerun()

# =========================================================
# 6. SONUÇLAR VE CEVAP ANAHTARI
# =========================================================
if st.session_state["test_bitti"]:
    st.balloons()
    st.header("📊 Sınav Sonuçları ve Detaylı Cevap Anahtarı")
    
    dogru_sayisi = 0
    yanlis_sayisi = 0
    bos_sayisi = 0
    
    for idx, s in enumerate(st.session_state["soru_listesi"]):
        k_cevabi = st.session_state["kullanici_cevaplari"].get(idx)
        if not k_cevabi:
            bos_sayisi += 1
        elif k_cevabi == s["dogru"]:
            dogru_sayisi += 1
        else:
            yanlis_sayisi += 1
            
    toplam_soru = len(st.session_state["soru_listesi"])
    puan = int((dogru_sayisi / toplam_soru) * 100) if toplam_soru > 0 else 0
    
    st.metric(label="Notunuz / Puanınız", value=f"{puan} Puan")
    st.write(f"✅ Doğru Sayısı: **{dogru_sayisi}** | ❌ Yanlış Sayısı: **{yanlis_sayisi}** | ⚠️ Boş Sayısı: **{bos_sayisi}**")
    
    st.divider()
    st.subheader("📝 Detaylı Cevap Anahtarı")
    
    for idx, s in enumerate(st.session_state["soru_listesi"]):
        k_cevabi = st.session_state["kullanici_cevaplari"].get(idx, "Boş bırakıldı")
        d_cevabi = s["dogru"]
        
        durum_ikonu = "✅" if k_cevabi == d_cevabi else "❌"
        
        with st.expander(f"Soru {idx + 1} ({s['ders']}) - {durum_ikonu}"):
            st.markdown(s["soru"], unsafe_allow_html=True)
            st.write(f"📌 **Ünite / Konu:** {s['unite']}")
            st.write(f"👤 **Senin Cevabın:** {k_cevabi}")
            st.write(f"🎯 **Doğru Cevap:** {d_cevabi}")

    st.write("")
    if st.button("🔄 Yeni Sınav Başlat", type="primary"):
        st.session_state["sorular_hazir"] = False
        st.session_state["test_aktif"] = False
        st.session_state["test_bitti"] = False
        st.session_state["soru_listesi"] = []
        st.session_state["kullanici_cevaplari"] = {}
        st.session_state["mevcut_soru_index"] = 0
        st.rerun()
