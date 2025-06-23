import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

import firebase_admin
from firebase_admin import credentials, firestore

# Firebase Admin SDK'yı başlat
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_service_account.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ------------------- Firestore Veri Fonksiyonları -------------------

def kayitlari_yukle():
    users_ref = db.collection('users')
    docs = users_ref.stream()
    kullanicilar = {}
    for doc in docs:
        kullanicilar[doc.id] = doc.to_dict()
    return kullanicilar

def kayitlari_kaydet(kullanicilar):
    users_ref = db.collection('users')
    # Tüm kullanıcıları temizle (küçük projeler için kabul edilir)
    docs = users_ref.stream()
    for doc in docs:
        users_ref.document(doc.id).delete()
    # Güncel kullanıcıları ekle
    for username, data in kullanicilar.items():
        users_ref.document(username).set(data)

# ------------------- Sayiyi Okunabilir Yap -------------------

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

# ------------------- Kullanıcı Girişi -------------------

def login():
    st.subheader("Giriş Yap")
    username = st.text_input("Kullanıcı Adı", key="login_username")
    password = st.text_input("Şifre", type="password", key="login_password")

    if st.button("Giriş Yap"):
        users = st.session_state.get("users", {})
        if username in users and users[username]["password"] == password:
            st.session_state["logged_in_user"] = username
            st.success(f"Hoşgeldin {username}!")
            st.experimental_rerun()
        else:
            st.error("Kullanıcı adı veya şifre yanlış.")

# ------------------- Kayıt Ol -------------------

def register():
    st.subheader("Kayıt Ol")
    username = st.text_input("Yeni Kullanıcı Adı", key="register_username")
    password = st.text_input("Yeni Şifre", type="password", key="register_password")

    if st.button("Kayıt Ol"):
        users = st.session_state.get("users", {})
        if username in users:
            st.error("Bu kullanıcı adı zaten alınmış.")
        elif username.strip() == "" or password.strip() == "":
            st.error("Kullanıcı adı ve şifre boş olamaz.")
        else:
            users[username] = {"password": password, "profile": None, "ihaleler": [], "operasyonel_giderler": []}
            kayitlari_kaydet(users)
            st.success("Kayıt başarılı! Lütfen giriş yapınız.")
            st.experimental_rerun()

# ------------------- Profil Bilgisi -------------------

def get_profile_info():
    st.subheader("Profil Bilgilerinizi Girin")

    username = st.session_state["logged_in_user"]
    users = st.session_state["users"]
    mevcut_profil = users[username].get("profile")

    if mevcut_profil:
        garage_level = st.number_input("Garaj Seviyeniz", min_value=1, max_value=100, step=1, value=mevcut_profil.get("garage_level", 1))
        vehicle_count = st.number_input("Araç Sayınız", min_value=0, max_value=100, step=1, value=mevcut_profil.get("vehicle_count", 0))
        vehicle_names = mevcut_profil.get("vehicle_names", [])
        trailer_count = st.number_input("Toplam Dorse Sayınız", min_value=0, max_value=100, step=1, value=mevcut_profil.get("trailer_count", 0))
    else:
        garage_level = st.number_input("Garaj Seviyeniz", min_value=1, max_value=100, step=1)
        vehicle_count = st.number_input("Araç Sayınız", min_value=0, max_value=100, step=1)
        vehicle_names = []
        trailer_count = st.number_input("Toplam Dorse Sayınız", min_value=0, max_value=100, step=1)

    yeni_vehicle_names = []
    for i in range(vehicle_count):
        default_name = vehicle_names[i] if i < len(vehicle_names) else ""
        name = st.text_input(f"{i+1}. Araç Adı", value=default_name, key=f"vehicle_{i}")
        yeni_vehicle_names.append(name)

    if st.button("Profil Bilgilerini Kaydet"):
        if any(name.strip() == "" for name in yeni_vehicle_names) and vehicle_count > 0:
            st.error("Tüm araç isimlerini doldurmalısınız.")
            return

        users[username]["profile"] = {
            "garage_level": garage_level,
            "vehicle_count": vehicle_count,
            "vehicle_names": yeni_vehicle_names,
            "trailer_count": trailer_count
        }
        kayitlari_kaydet(users)
        st.success("Profil bilgileri kaydedildi.")

# ------------------- İhale Girişi -------------------

def ihale_girisi():
    st.subheader("İhale Girişi")

    ihale_turu = st.text_input("İhale Türü (örneğin: Kimyasal)")
    ihale_bedeli = st.number_input("İhalenin Toplam Bedeli (Dolar)", min_value=0.0, step=0.01, format="%.2f")
    urun_birim_maliyeti = st.number_input("Birim Ürün Maliyeti (Dolar)", min_value=0.0, step=0.01, format="%.2f")
    urun_sayisi = st.number_input("Ürün Sayısı (Adet)", min_value=0)

    if st.button("İhale Kaydet"):
        if ihale_turu.strip() == "":
            st.error("İhale türü boş olamaz.")
            return
        username = st.session_state["logged_in_user"]
        users = st.session_state["users"]

        yeni_ihale = {
            "ihale_turu": ihale_turu,
            "ihale_bedeli": ihale_bedeli,
            "urun_birim_maliyeti": urun_birim_maliyeti,
            "urun_sayisi": urun_sayisi,
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        users[username]["ihaleler"].append(yeni_ihale)
        kayitlari_kaydet(users)
        st.success("İhale kaydedildi.")

# ------------------- Operasyonel Giderler -------------------

def operasyonel_giderler():
    st.subheader("Operasyonel Giderler")

    users = st.session_state["users"]
    username = st.session_state["logged_in_user"]
    user = users[username]

    kategori = st.selectbox("Gider Kategorisi", [
        "Garaj Bakımı",
        "Garaj Seviye Yükseltmesi",
        "Maaş Ödemesi",
        "Araç Bakımı",
        "Araç Alımı",
        "Araç Satımı",
        "Dorse Alımı",
        "Emeklilik ve İşten Kovma",
        "Araç Yükseltme Bedeli"
    ])

    gider_detay = {}
    if kategori == "Garaj Bakımı":
        tutar = st.number_input("Garaj Bakım Tutarı (Dolar)", min_value=0.0, step=0.01, format="%.2f")
        gider_detay["tutar"] = tutar
    elif kategori == "Garaj Seviye Yükseltmesi":
        yeni_seviye = st.number_input("Yeni Garaj Seviyesi", min_value=1, max_value=100, step=1)
        maliyet = st.number_input("Yükseltme Maliyeti (Dolar)", min_value=0.0, step=0.01, format="%.2f")
        gider_detay["yeni_seviye"] = yeni_seviye
        gider_detay["tutar"] = maliyet
    elif kategori == "Maaş Ödemesi":
        sofor_adi = st.text_input("Şoför Adı")
        maas = st.number_input("Maaş Tutarı (Dolar)", min_value=0.0, step=0.01, format="%.2f")
        gider_detay["sofor_adi"] = sofor_adi
        gider_detay["tutar"] = maas
    elif kategori == "Araç Bakımı":
        arac_listesi = user["profile"]["vehicle_names"] if user.get("profile") else []
        arac_secimi = st.selectbox("Araç Seçin", arac_listesi)
        bakim_tutari = st.number_input("Bakım Maliyeti (Dolar)", min_value=0.0, step=0.01, format="%.2f")
        gider_detay["arac_adi"] = arac_secimi
        gider_detay["tutar"] = bakim_tutari
    elif kategori == "Araç Alımı":
        arac_adi = st.text_input("Alınan Araç Adı")
        maliyet = st.number_input("Araç Maliyeti (Dolar)", min_value=0.0, step=0.01, format="%.2f")
        gider_detay["arac_adi"] = arac_adi
        gider_detay["tutar"] = maliyet
    elif kategori == "Araç Satımı":
        arac_listesi = user["profile"]["vehicle_names"] if user.get("profile") else []
        arac_secimi = st.selectbox("Satılan Araç", arac_listesi)
        satis_tutari = st.number_input("Satış Tutarı (Dolar)", min_value=0.0, step=0.01, format="%.2f")
        gider_detay["arac_adi"] = arac_secimi
        gider_detay["tutar"] = -satis_tutari  # negatif gider olarak işlem
    elif kategori == "Dorse Alımı":
        dorse_tipi = st.text_input("Dorse Tipi")
        maliyet = st.number_input("Dorse Maliyeti (Dolar)", min_value=0.0, step=0.01, format="%.2f")
        gider_detay["dorse_tipi"] = dorse_tipi
        gider_detay["tutar"] = maliyet
    elif kategori == "Emeklilik ve İşten Kovma":
        sofor_adi = st.text_input("Şoför Adı")
        tazminat = st.number_input("Tazminat Tutarı (Dolar)", min_value=0.0, step=0.01, format="%.2f")
        gider_detay["sofor_adi"] = sofor_adi
        gider_detay["tutar"] = tazminat
    elif kategori == "Araç Yükseltme Bedeli":
        arac_listesi = user["profile"]["vehicle_names"] if user.get("profile") else []
        arac_secimi = st.selectbox("Araç Seçin", arac_listesi)
        tutar = st.number_input("Yükseltme Bedeli (Dolar)", min_value=0.0, step=0.01, format="%.2f")
        gider_detay["arac_adi"] = arac_secimi
        gider_detay["tutar"] = tutar

    if st.button("Gider Kaydet"):
        if "tutar" not in gider_detay:
            st.error("Lütfen tutar bilgisi girin.")
            return
        users[username]["operasyonel_giderler"].append({
            "kategori": kategori,
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **gider_detay
        })
        # Garaj seviyesi yükseltme varsa güncelle
        if kategori == "Garaj Seviye Yükseltmesi":
            users[username]["profile"]["garage_level"] = gider_detay["yeni_seviye"]
        # Araç alımıysa araç listesine ekle
        if kategori == "Araç Alımı":
            users[username]["profile"]["vehicle_names"].append(gider_detay["arac_adi"])
            users[username]["profile"]["vehicle_count"] += 1

        kayitlari_kaydet(users)
        st.success("Operasyonel gider kaydedildi.")
        st.experimental_rerun()

# ------------------- Günlük Rapor -------------------

def gunluk_rapor():
    st.subheader("Günlük Rapor")

    username = st.session_state["logged_in_user"]
    users = st.session_state["users"]
    user = users[username]

    bugun = datetime.now().date()

    ihaleler_bugun = [ih for ih in user.get("ihaleler", []) if datetime.strptime(ih["tarih"], "%Y-%m-%d %H:%M:%S").date() == bugun]
    giderler_bugun = [gd for gd in user.get("operasyonel_giderler", []) if datetime.strptime(gd["tarih"], "%Y-%m-%d %H:%M:%S").date() == bugun]

    toplam_ihale_sayisi = len(ihaleler_bugun)
    toplam_ihale_geliri = sum(ih["ihale_bedeli"] for ih in ihaleler_bugun)
    toplam_urun_maliyeti = sum(ih["urun_birim_maliyeti"] * ih["urun_sayisi"] for ih in ihaleler_bugun)
    toplam_operasyonel_maliyet = sum(gd["tutar"] for gd in giderler_bugun)
    toplam_kar = toplam_ihale_geliri - toplam_urun_maliyeti - toplam_operasyonel_maliyet

    st.write(f"Günlük Toplam İhale Sayısı: {toplam_ihale_sayisi}")
    st.write(f"Günlük Toplam İhale Geliri: {sayi_formatla(int(toplam_ihale_geliri))} $")
    st.write(f"Günlük Ürün Maliyeti: {sayi_formatla(int(toplam_urun_maliyeti))} $")
    st.write(f"Günlük Operasyonel Maliyet: {sayi_formatla(int(toplam_operasyonel_maliyet))} $")
    st.write(f"Günlük Toplam Kar: {sayi_formatla(int(toplam_kar))} $")

# ------------------- Haftalık / Aylık Rapor -------------------

def haftalik_aylik_rapor():
    st.subheader("Haftalık / Aylık Rapor")

    username = st.session_state["logged_in_user"]
    users = st.session_state["users"]
    user = users[username]

    rapor_tipi = st.selectbox("Rapor Tipi Seçin", ["Haftalık", "Aylık"])
    bugun = datetime.now().date()

    if rapor_tipi == "Haftalık":
        baslangic = bugun - timedelta(days=7)
    else:
        baslangic = bugun - timedelta(days=30)

    ihaleler_filtreli = [ih for ih in user.get("ihaleler", []) if baslangic <= datetime.strptime(ih["tarih"], "%Y-%m-%d %H:%M:%S").date() <= bugun]
    giderler_filtreli = [gd for gd in user.get("operasyonel_giderler", []) if baslangic <= datetime.strptime(gd["tarih"], "%Y-%m-%d %H:%M:%S").date() <= bugun]

    toplam_ihale_sayisi = len(ihaleler_filtreli)
    toplam_ihale_geliri = sum(ih["ihale_bedeli"] for ih in ihaleler_filtreli)
    toplam_urun_maliyeti = sum(ih["urun_birim_maliyeti"] * ih["urun_sayisi"] for ih in ihaleler_filtreli)
    toplam_operasyonel_maliyet = sum(gd["tutar"] for gd in giderler_filtreli)
    toplam_kar = toplam_ihale_geliri - toplam_urun_maliyeti - toplam_operasyonel_maliyet

    st.write(f"{rapor_tipi} Toplam İhale Sayısı: {toplam_ihale_sayisi}")
    st.write(f"{rapor_tipi} Toplam İhale Geliri: {sayi_formatla(int(toplam_ihale_geliri))} $")
    st.write(f"{rapor_tipi} Ürün Maliyeti: {sayi_formatla(int(toplam_urun_maliyeti))} $")
    st.write(f"{rapor_tipi} Operasyonel Maliyet: {sayi_formatla(int(toplam_operasyonel_maliyet))} $")
    st.write(f"{rapor_tipi} Toplam Kar: {sayi_formatla(int(toplam_kar))} $")

# ------------------- Ana Sayfa -------------------

def main():
    st.title("İhale ve Operasyon Takip Uygulaması")

    # Kullanıcı verilerini yükle (Firestore'dan)
    if "users" not in st.session_state:
        st.session_state["users"] = kayitlari_yukle()

    if "logged_in_user" not in st.session_state:
        login()
        st.info("Henüz hesabınız yoksa Kayıt Ol sekmesine geçiniz.")
        st.stop()

    # Giriş yapmış kullanıcı
    kullanici = st.session_state["logged_in_user"]
    st.sidebar.write(f"Hoşgeldiniz, **{kullanici}**")
    secim = st.sidebar.radio("Menü", ["Profil", "İhale Girişi", "Operasyonel Giderler", "Günlük Rapor", "Haftalık/Aylık Rapor", "Çıkış", "Kayıt Ol"])

    if secim == "Çıkış":
        del st.session_state["logged_in_user"]
        st.experimental_rerun()
    elif secim == "Kayıt Ol":
        register()
    elif secim == "Profil":
        get_profile_info()
    elif secim == "İhale Girişi":
        ihale_girisi()
    elif secim == "Operasyonel Giderler":
        operasyonel_giderler()
    elif secim == "Günlük Rapor":
        gunluk_rapor()
    elif secim == "Haftalık/Aylık Rapor":
        haftalik_aylik_rapor()

if __name__ == "__main__":
    main()
