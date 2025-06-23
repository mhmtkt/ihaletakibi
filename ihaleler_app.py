import streamlit as st
from datetime import datetime
import pandas as pd

# ------------------- Yardımcı Fonksiyon -------------------

def sayi_formatla(sayi):
    if sayi >= 1_000_000:
        milyon = sayi // 1_000_000
        kalan = sayi % 1_000_000
        if kalan == 0:
            return f"{milyon} milyon"
        else:
            binler = kalan // 1000
            yuzler = kalan % 1000
            parcalar = []
            if binler > 0:
                parcalar.append(f"{binler} bin")
            if yuzler > 0:
                parcalar.append(f"{yuzler}")
            return f"{milyon} milyon " + " ".join(parcalar)
    elif sayi >= 1000:
        binler = sayi // 1000
        yuzler = sayi % 1000
        if yuzler == 0:
            return f"{binler} bin"
        else:
            return f"{binler} bin {yuzler}"
    else:
        return str(sayi)

# ------------------- Kullanıcı Yönetimi -------------------

if "users" not in st.session_state:
    st.session_state["users"] = {}  # kullanıcılar {"kullanici_adi": {"password": "...", "profile": {...}, "ihaleler": [...], "operasyonel_giderler": [...] }}

if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

def register():
    st.header("Kayıt Ol")
    yeni_kullanici = st.text_input("Kullanıcı Adı", key="register_user")
    yeni_sifre = st.text_input("Şifre", type="password", key="register_pass")
    if st.button("Kayıt Ol"):
        if yeni_kullanici in st.session_state["users"]:
            st.error("Bu kullanıcı adı zaten alınmış.")
        elif yeni_kullanici == "" or yeni_sifre == "":
            st.error("Kullanıcı adı ve şifre boş olamaz.")
        else:
            st.session_state["users"][yeni_kullanici] = {
                "password": yeni_sifre,
                "profile": None,
                "ihaleler": [],
                "operasyonel_giderler": []
            }
            st.success("Kayıt başarılı! Lütfen giriş yap.")
            st.session_state["logged_in_user"] = None

def login():
    st.header("Giriş Yap")
    kullanici = st.text_input("Kullanıcı Adı", key="login_user")
    sifre = st.text_input("Şifre", type="password", key="login_pass")
    if st.button("Giriş"):
        if kullanici not in st.session_state["users"]:
            st.error("Böyle bir kullanıcı yok.")
        elif st.session_state["users"][kullanici]["password"] != sifre:
            st.error("Şifre yanlış.")
        else:
            st.session_state["logged_in_user"] = kullanici
            st.success(f"Hoşgeldin {kullanici}!")
            st.experimental_rerun()

def logout():
    st.session_state["logged_in_user"] = None
    st.experimental_rerun()

# ------------------- Profil Bilgileri -------------------

def get_profile_info():
    if "profil_kaydedildi" not in st.session_state:
        st.session_state["profil_kaydedildi"] = False

    st.header("Profil Bilgilerinizi Girin")

    with st.form("profil_form"):
        garage_level = st.number_input("Garaj Seviyeniz", min_value=1, max_value=100, step=1)
        arac_sayisi = st.number_input("Araç Sayınız", min_value=0, max_value=100, step=1)

        arac_adlari = []
        for i in range(arac_sayisi):
            arac_adi = st.text_input(f"{i+1}. Araç Adı", key=f"arac_adi_{i}")
            arac_adlari.append(arac_adi)

        dorse_sayisi = st.number_input("Toplam Dorse Sayınız", min_value=0, max_value=100, step=1)

        submitted = st.form_submit_button("Kaydet")

    if submitted:
        user = st.session_state["users"][st.session_state["logged_in_user"]]
        user["profile"] = {
            "garage_level": garage_level,
            "arac_sayisi": arac_sayisi,
            "arac_adlari": arac_adlari,
            "dorse_sayisi": dorse_sayisi
        }
        st.session_state["profil_kaydedildi"] = True
        st.experimental_rerun()

# ------------------- İhale Girişi -------------------

def ihale_girisi():
    st.header("İhale Girişi")
    user = st.session_state["users"][st.session_state["logged_in_user"]]

    with st.form("ihale_form"):
        ihale_turu = st.text_input("İhale Türü")
        ihale_bedeli = st.number_input("İhalenin Toplam Bedeli (USD)", min_value=0.0, format="%.2f")
        birim_urun_maliyeti = st.number_input("Birim Ürün Maliyeti (USD)", min_value=0.0, format="%.2f")
        urun_sayisi = st.number_input("Ürün Sayısı (Adet)", min_value=0)

        submitted = st.form_submit_button("Kaydet")

    if submitted:
        ihale = {
            "ihale_turu": ihale_turu,
            "ihale_bedeli": ihale_bedeli,
            "birim_urun_maliyeti": birim_urun_maliyeti,
            "urun_sayisi": urun_sayisi,
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        user["ihaleler"].append(ihale)
        st.success("İhale kaydedildi.")

# ------------------- Operasyonel Giderler -------------------

def operasyonel_giderler():
    st.header("Operasyonel Giderler")
    user = st.session_state["users"][st.session_state["logged_in_user"]]

    gider_turleri = [
        "Garaj Bakımı",
        "Garaj Seviye Yükseltmesi",
        "Maaş Ödemesi",
        "Araç Bakımı",
        "Araç Alımı",
        "Araç Satımı",
        "Dorse Alımı",
        "Emeklilik / İşten Kovma",
        "Araç Yükseltme Bedeli"
    ]

    secim = st.selectbox("Gider Türü Seçin", gider_turleri)

    with st.form("gider_form"):
        if secim == "Garaj Bakımı":
            tutar = st.number_input("Garaj Bakım Tutarı (USD)", min_value=0.0, format="%.2f")
        elif secim == "Garaj Seviye Yükseltmesi":
            yeni_seviye = st.number_input("Yeni Garaj Seviyesi", min_value=1, max_value=100, step=1)
            maliyet = st.number_input("Yükseltme Maliyeti (USD)", min_value=0.0, format="%.2f")
        elif secim == "Maaş Ödemesi":
            sofor_adi = st.text_input("Şoför Adı")
            maas = st.number_input("Maaş (USD)", min_value=0.0, format="%.2f")
        elif secim == "Araç Bakımı":
            arac = st.selectbox("Araç Seçin", user["profile"]["arac_adlari"])
            bakim_tutari = st.number_input("Bakım Maliyeti (USD)", min_value=0.0, format="%.2f")
        elif secim == "Araç Alımı":
            arac_adi = st.text_input("Alınan Araç Adı")
            maliyet = st.number_input("Maliyet (USD)", min_value=0.0, format="%.2f")
        elif secim == "Araç Satımı":
            arac = st.selectbox("Satılan Araç", user["profile"]["arac_adlari"])
            tutar = st.number_input("Satış Tutarı (USD)", min_value=0.0, format="%.2f")
        elif secim == "Dorse Alımı":
            dorse_tipi = st.text_input("Dorse Tipi")
            maliyet = st.number_input("Maliyet (USD)", min_value=0.0, format="%.2f")
        elif secim == "Emeklilik / İşten Kovma":
            sofor_adi = st.text_input("Şoför Adı")
            tazminat = st.number_input("Tazminat (USD)", min_value=0.0, format="%.2f")
        elif secim == "Araç Yükseltme Bedeli":
            arac = st.selectbox("Araç Seçin", user["profile"]["arac_adlari"])
            tutar = st.number_input("Yükseltme Bedeli (USD)", min_value=0.0, format="%.2f")

        submitted = st.form_submit_button("Kaydet")

    if submitted:
        gider = {
            "tip": secim,
            "tutar": 0.0,
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Tutarları ve diğer bilgileri ayarla
        if secim == "Garaj Bakımı":
            gider["tutar"] = tutar
        elif secim == "Garaj Seviye Yükseltmesi":
            gider["tutar"] = maliyet
            # Garaj seviyesini güncelle
            user["profile"]["garage_level"] = yeni_seviye
        elif secim == "Maaş Ödemesi":
            gider["tutar"] = maas
            gider["sofor"] = sofor_adi
        elif secim == "Araç Bakımı":
            gider["tutar"] = bakim_tutari
            gider["arac"] = arac
        elif secim == "Araç Alımı":
            gider["tutar"] = maliyet
            gider["arac"] = arac_adi
            # Aracı profile ekle
            user["profile"]["arac_adlari"].append(arac_adi)
            user["profile"]["arac_sayisi"] += 1
        elif secim == "Araç Satımı":
            gider["tutar"] = -tutar  # giderden düşülecek gelir olarak negatif yazıyoruz
            gider["arac"] = arac
            # Araç listesinden çıkar
            if arac in user["profile"]["arac_adlari"]:
                user["profile"]["arac_adlari"].remove(arac)
                user["profile"]["arac_sayisi"] -= 1
        elif secim == "Dorse Alımı":
            gider["tutar"] = maliyet
            gider["dorse_tipi"] = dorse_tipi
            # Dorse sayısını arttır
            user["profile"]["dorse_sayisi"] += 1
        elif secim == "Emeklilik / İşten Kovma":
            gider["tutar"] = tazminat
            gider["sofor"] = sofor_adi
        elif secim == "Araç Yükseltme Bedeli":
            gider["tutar"] = tutar
            gider["arac"] = arac

        user["operasyonel_giderler"].append(gider)
        st.success("Operasyonel gider kaydedildi.")

# ------------------- Günlük Rapor -------------------

def gunluk_rapor():
    st.header("Günlük Rapor")
    user = st.session_state["users"][st.session_state["logged_in_user"]]

    ihaleler = user["ihaleler"]
    giderler = user["operasyonel_giderler"]

    bugun = datetime.now().date()

    bugun_ihaleler = [ih for ih in ihaleler if datetime.strptime(ih["tarih"], "%Y-%m-%d %H:%M:%S").date() == bugun]
    bugun_giderler = [g for g in giderler if datetime.strptime(g["tarih"], "%Y-%m-%d %H:%M:%S").date() == bugun]

    toplam_ihale_sayisi = len(bugun_ihaleler)
    toplam_ihale_geliri = sum(ih["ihale_bedeli"] for ih in bugun_ihaleler)
    toplam_urun_maliyeti = sum(ih["birim_urun_maliyeti"] * ih["urun_sayisi"] for ih in bugun_ihaleler)
    toplam_operasyonel_gider = sum(g["tutar"] for g in bugun_giderler)
    toplam_kar = toplam_ihale_geliri - toplam_urun_maliyeti - toplam_operasyonel_gider

    st.write(f"Günlük Toplam İhale Sayısı: {toplam_ihale_sayisi}")
    st.write(f"Günlük Toplam İhale Geliri (USD): {sayi_formatla(int(toplam_ihale_geliri))}")
    st.write(f"Günlük Ürün Maliyeti (USD): {sayi_formatla(int(toplam_urun_maliyeti))}")
    st.write(f"Günlük Operasyonel Maliyet (USD): {sayi_formatla(int(toplam_operasyonel_gider))}")
    st.write(f"Günlük Toplam Kar (USD): {sayi_formatla(int(toplam_kar))}")

# ------------------- Grafiksel Rapor -------------------

def grafiksel_rapor():
    st.header("Grafiksel Raporlar")
    user = st.session_state["users"][st.session_state["logged_in_user"]]

    ihaleler = pd.DataFrame(user["ihaleler"])
    giderler = pd.DataFrame(user["operasyonel_giderler"])

    if ihaleler.empty:
        st.info("Henüz ihale girişi yapılmadı.")
        return

    st.subheader("Tarih Aralığı Seçin")
    min_tarih = datetime.strptime(ihaleler["tarih"].min(), "%Y-%m-%d %H:%M:%S").date()
    max_tarih = datetime.strptime(ihaleler["tarih"].max(), "%Y-%m-%d %H:%M:%S").date()
    tarih_araligi = st.date_input("Tarih Aralığı", [min_tarih, max_tarih])

    if len(tarih_araligi) != 2:
        st.warning("Lütfen geçerli bir tarih aralığı seçin.")
        return

    baslangic, bitis = tarih_araligi

    ihaleler["tarih_dt"] = pd.to_datetime(ihaleler["tarih"])
    ihaleler_filtered = ihaleler[(ihaleler["tarih_dt"].dt.date >= baslangic) & (ihaleler["tarih_dt"].dt.date <= bitis)]

    if not giderler.empty:
        giderler["tarih_dt"] = pd.to_datetime(giderler["tarih"])
        giderler_filtered = giderler[(giderler["tarih_dt"].dt.date >= baslangic) & (giderler["tarih_dt"].dt.date <= bitis)]
    else:
        giderler_filtered = pd.DataFrame()

    # 1. Grafik: İhale Türü Dağılımı
    st.subheader("İhale Türü Dağılımı")
    ihale_turleri = ihaleler_filtered["ihale_turu"].value_counts()
    if ihale_turleri.empty:
        st.write("Seçilen dönemde ihale bulunamadı.")
    else:
        st.bar_chart(ihale_turleri)

    # 2. Grafik: İhale Türlerine Göre Gelirler
    st.subheader("İhale Türlerine Göre Gelirler")
    gelirler = ihaleler_filtered.groupby("ihale_turu")["ihale_bedeli"].sum()
    if gelirler.empty:
        st.write("Seçilen dönemde ihale bulunamadı.")
    else:
        # Sayıları formatla
        gelirler_fmt = gelirler.apply(lambda x: sayi_formatla(int(x)))
        st.bar_chart(gelirler)

    # 3. Grafik: Operasyonel Giderlerin Dağılımı
    st.subheader("Operasyonel Giderlerin Dağılımı")
    if giderler_filtered.empty:
        st.write("Seçilen dönemde operasyonel gider bulunamadı.")
    else:
        gider_turleri = giderler_filtered.groupby("tip")["tutar"].sum()
        st.bar_chart(gider_turleri)

# ------------------- Ana Fonksiyon -------------------

def main():
    st.title("İhale Oyunu Takip Uygulaması")

    if st.session_state["logged_in_user"] is None:
        secim = st.radio("Giriş veya Kayıt Ol", ["Giriş Yap", "Kayıt Ol"])
        if secim == "Giriş Yap":
            login()
        else:
            register()
    else:
        user_data = st.session_state["users"][st.session_state["logged_in_user"]]

        if user_data.get("profile") is None:
            get_profile_info()
            return

        st.sidebar.title(f"Hoşgeldin, {st.session_state['logged_in_user']}")
        sekme = st.sidebar.selectbox("Sekmeler", ["İhale Girişi", "Operasyonel Giderler", "Günlük Rapor", "Raporlar"])

        if st.sidebar.button("Çıkış Yap"):
            logout()
            return

        if sekme == "İhale Girişi":
            ihale_girisi()
        elif sekme == "Operasyonel Giderler":
            operasyonel_giderler()
        elif sekme == "Günlük Rapor":
            gunluk_rapor()
        elif sekme == "Raporlar":
            grafiksel_rapor()

if __name__ == "__main__":
    main()
