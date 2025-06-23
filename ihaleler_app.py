import streamlit as st
from datetime import datetime
import pandas as pd
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
    st.session_state["users"] = {}

if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

if "profil_kaydedildi" not in st.session_state:
    st.session_state["profil_kaydedildi"] = False

def register():
    st.subheader("Kayıt Ol")
    username = st.text_input("Kullanıcı Adı", key="register_username")
    password = st.text_input("Şifre", type="password", key="register_password")
    if st.button("Kayıt Ol"):
        if username.strip() == "" or password.strip() == "":
            st.warning("Kullanıcı adı ve şifre boş olamaz!")
        elif username in st.session_state["users"]:
            st.error("Bu kullanıcı adı zaten mevcut!")
        else:
            st.session_state["users"][username] = {
                "password": password,
                "profile": None,
                "ihaleler": [],
                "operasyonel_giderler": []
            }
            st.success("Kayıt başarılı, giriş yapabilirsiniz.")

def login():
    st.subheader("Giriş Yap")
    username = st.text_input("Kullanıcı Adı", key="login_username")
    password = st.text_input("Şifre", type="password", key="login_password")
    if st.button("Giriş Yap"):
        if username in st.session_state["users"]:
            if st.session_state["users"][username]["password"] == password:
                st.session_state["logged_in_user"] = username
                st.experimental_rerun()
            else:
                st.error("Şifre yanlış!")
        else:
            st.error("Kullanıcı bulunamadı.")

def logout():
    st.session_state["logged_in_user"] = None
    st.experimental_rerun()

# ------------------- Profil Bilgileri -------------------

def get_profile_info():
    st.subheader("Profil Bilgileri - İlk Kayıt")
    garage_level = st.number_input("Garaj Seviyeniz", min_value=1, max_value=100, step=1)
    vehicle_count = st.number_input("Araç Sayınız", min_value=0, step=1)
    
    vehicle_names = []
    for i in range(vehicle_count):
        name = st.text_input(f"Araç {i+1} Adı", key=f"vehicle_name_{i}")
        vehicle_names.append(name)
    
    trailer_count = st.number_input("Toplam Dorse Sayınız", min_value=0, step=1)

    if st.button("Profil Bilgilerini Kaydet"):
        if vehicle_count > 0 and any(name.strip() == "" for name in vehicle_names):
            st.warning("Lütfen tüm araç isimlerini doldurun.")
            return
        user = st.session_state["users"][st.session_state["logged_in_user"]]
        user["profile"] = {
            "garage_level": garage_level,
            "vehicle_count": vehicle_count,
            "vehicle_names": vehicle_names,
            "trailer_count": trailer_count
        }
        st.session_state["profil_kaydedildi"] = True
        st.success("Profil bilgileri kaydedildi.")

# ------------------- İhale Girişi -------------------

def ihale_girisi():
    st.header("İhale Girişi")
    ihale_turu = st.text_input("İhale Türü (örn: Kimyasal)")
    ihale_bedeli = st.number_input("Toplam İhale Bedeli (USD)", min_value=0.0, step=0.01)
    birim_urun_maliyeti = st.number_input("Birim Ürün Maliyeti (USD)", min_value=0.0, step=0.01)
    urun_sayisi = st.number_input("Ürün Sayısı (Adet)", min_value=0, step=1)

    if st.button("İhale Kaydet"):
        if ihale_turu.strip() == "":
            st.warning("Lütfen ihale türünü girin.")
            return
        ihale = {
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ihale_turu": ihale_turu,
            "ihale_bedeli": ihale_bedeli,
            "birim_urun_maliyeti": birim_urun_maliyeti,
            "urun_sayisi": urun_sayisi
        }
        st.session_state["users"][st.session_state["logged_in_user"]]["ihaleler"].append(ihale)
        st.success("İhale kaydedildi!")

# ------------------- Operasyonel Giderler -------------------

def operasyonel_giderler():
    st.header("Operasyonel Giderler Ekleme")
    user = st.session_state["users"][st.session_state["logged_in_user"]]
    profile = user["profile"]
    if profile is None:
        st.warning("Önce profil bilgilerinizi kaydedin.")
        return

    # Garaj Bakımı
    garaj_bakimi = st.number_input("Garaj Bakımı Tutarı (USD)", min_value=0.0, step=0.01)

    # Garaj Yükseltme
    col1, col2 = st.columns(2)
    with col1:
        yeni_garaj_seviyesi = st.number_input("Garaj Seviye Yükseltme (Yeni Seviye)", min_value=profile["garage_level"], max_value=100, step=1)
    with col2:
        yuksektme_maliyeti = st.number_input("Yükseltme Maliyeti (USD)", min_value=0.0, step=0.01)

    if st.button("Garaj Yükseltmesini Kaydet"):
        if yeni_garaj_seviyesi > profile["garage_level"]:
            profile["garage_level"] = yeni_garaj_seviyesi
            user["operasyonel_giderler"].append({
                "tip": "Garaj Seviye Yükseltme",
                "tutar": yuksektme_maliyeti,
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success("Garaj seviyesi yükseltildi ve maliyet kaydedildi.")
            st.experimental_rerun()
        else:
            st.warning("Yeni seviye mevcut seviyeden yüksek olmalı.")

    if st.button("Garaj Bakımı Kaydet"):
        if garaj_bakimi > 0:
            user["operasyonel_giderler"].append({
                "tip": "Garaj Bakımı",
                "tutar": garaj_bakimi,
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success("Garaj bakımı gideri kaydedildi.")
            st.experimental_rerun()
        else:
            st.warning("Pozitif tutar girin.")

    # Şoför Maaşları
    st.subheader("Şoför Maaşları")
    maas_adi = st.text_input("Şoför Adı", key="maas_adi")
    maas_tutari = st.number_input("Maaş Tutarı (USD)", min_value=0.0, step=0.01, key="maas_tutari")
    if st.button("Maaş Ekle"):
        if maas_adi.strip() == "":
            st.warning("Şoför adını girin.")
        else:
            user["operasyonel_giderler"].append({
                "tip": "Maaş Ödemesi",
                "ad": maas_adi,
                "tutar": maas_tutari,
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success(f"{maas_adi} için maaş eklendi.")
            st.experimental_rerun()

    # Araç Bakımı
    st.subheader("Araç Bakımı")
    araclar = profile["vehicle_names"]
    if not araclar:
        st.info("Önce profil bölümünden araç ekleyin.")
    else:
        arac_secimi = st.selectbox("Bakımı Yapılan Aracı Seçin", araclar)
        arac_bakim_maliyeti = st.number_input("Bakım Maliyeti (USD)", min_value=0.0, step=0.01, key="arac_bakim_maliyeti")
        if st.button("Araç Bakımı Ekle"):
            user["operasyonel_giderler"].append({
                "tip": "Araç Bakımı",
                "arac": arac_secimi,
                "tutar": arac_bakim_maliyeti,
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success(f"{arac_secimi} için araç bakımı eklendi.")
            st.experimental_rerun()

    # Araç Alımı
    st.subheader("Araç Alımı")
    yeni_arac_adi = st.text_input("Alınan Araç Adı", key="arac_alim_adi")
    yeni_arac_maliyeti = st.number_input("Araç Maliyeti (USD)", min_value=0.0, step=0.01, key="arac_alim_maliyet")
    if st.button("Araç Alımı Kaydet"):
        if yeni_arac_adi.strip() == "":
            st.warning("Araç adını girin.")
        else:
            profile["vehicle_names"].append(yeni_arac_adi)
            profile["vehicle_count"] += 1
            user["operasyonel_giderler"].append({
                "tip": "Araç Alımı",
                "arac": yeni_arac_adi,
                "tutar": yeni_arac_maliyeti,
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success(f"{yeni_arac_adi} aracı alındı ve listeye eklendi.")
            st.experimental_rerun()

    # Araç Satımı
    st.subheader("Araç Satımı")
    if not araclar:
        st.info("Satılacak araç yok.")
    else:
        satilacak_arac = st.selectbox("Satılan Aracı Seçin", araclar, key="satilan_arac_secimi")
        satis_tutari = st.number_input("Satış Tutarı (USD)", min_value=0.0, step=0.01, key="satis_tutari")
        if st.button("Araç Satışını Kaydet"):
            if satilacak_arac in profile["vehicle_names"]:
                profile["vehicle_names"].remove(satilacak_arac)
                profile["vehicle_count"] -= 1
                user["operasyonel_giderler"].append({
                    "tip": "Araç Satımı",
                    "arac": satilacak_arac,
                    "tutar": -satis_tutari,
                    "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success(f"{satilacak_arac} satıldı ve listeden çıkarıldı.")
                st.experimental_rerun()
            else:
                st.warning("Araç listede yok veya zaten satıldı.")

    # Dorse Alımı
    st.subheader("Dorse Alımı")
    dorse_tipi = st.text_input("Alınan Dorse Tipi", key="dorse_tipi")
    dorse_maliyeti = st.number_input("Dorse Maliyeti (USD)", min_value=0.0, step=0.01, key="dorse_maliyeti")
    if st.button("Dorse Alımını Kaydet"):
        if dorse_tipi.strip() == "":
            st.warning("Dorse tipini girin.")
        else:
            user["operasyonel_giderler"].append({
                "tip": "Dorse Alımı",
                "dorse_tipi": dorse_tipi,
                "tutar": dorse_maliyeti,
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            profile["trailer_count"] += 1
            st.success(f"{dorse_tipi} tipi dorse alındı.")
            st.experimental_rerun()

    # Emeklilik / İşten Kovma
    st.subheader("Emeklilik ve İşten Kovma")
    kovulan_sofor = st.text_input("İşten Kovulan veya Emekli Olan Şoför Adı", key="kovulan_sofor")
    tazminat_tutari = st.number_input("Tazminat Tutarı (USD)", min_value=0.0, step=0.01, key="tazminat_tutari")
    if st.button("Emeklilik/Kovma Kaydet"):
        if kovulan_sofor.strip() == "":
            st.warning("Şoför adını girin.")
        else:
            user["operasyonel_giderler"].append({
                "tip": "Emeklilik/İşten Kovma",
                "ad": kovulan_sofor,
                "tutar": tazminat_tutari,
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success(f"{kovulan_sofor} için tazminat kaydedildi.")
            st.experimental_rerun()

    # Araç Yükseltme Bedeli
    st.subheader("Araç Yükseltme Bedeli")
    if not araclar:
        st.info("Önce araç ekleyin.")
    else:
        arac_yukseltme = st.selectbox("Yükseltilecek Aracı Seçin", araclar, key="arac_yukseltme_secimi")
        yukseltme_tutari = st.number_input("Yükseltme Tutarı (USD)", min_value=0.0, step=0.01, key="yukseltme_tutari")
        if st.button("Araç Yükseltme Kaydet"):
            user["operasyonel_giderler"].append({
                "tip": "Araç Yükseltme",
                "arac": arac_yukseltme,
                "tutar": yukseltme_tutari,
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success(f"{arac_yukseltme} için yükseltme kaydedildi.")
            st.experimental_rerun()

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


def grafiksel_rapor():
    st.header("Grafiksel Raporlar")
    user = st.session_state["users"][st.session_state["logged_in_user"]]

    ihaleler = pd.DataFrame(user["ihaleler"])
    giderler = pd.DataFrame(user["operasyonel_giderler"])

    if ihaleler.empty:
        st.info("Henüz ihale girişi yapılmadı.")
        return
    if giderler.empty:
        st.info("Henüz operasyonel gider girişi yapılmadı.")
        return

    # Filtre için tarih aralığı seçimi
    st.subheader("Tarih Aralığı Seçin")
    min_tarih = datetime.strptime(ihaleler["tarih"].min(), "%Y-%m-%d %H:%M:%S").date()
    max_tarih = datetime.strptime(ihaleler["tarih"].max(), "%Y-%m-%d %H:%M:%S").date()
    tarih_araligi = st.date_input("Tarih Aralığı", [min_tarih, max_tarih])

    if len(tarih_araligi) != 2:
        st.warning("Lütfen geçerli bir tarih aralığı seçin.")
        return

    baslangic, bitis = tarih_araligi

    ihaleler["tarih_dt"] = pd.to_datetime(ihaleler["tarih"])
    giderler["tarih_dt"] = pd.to_datetime(giderler["tarih"])

    ihaleler_filtered = ihaleler[(ihaleler["tarih_dt"].dt.date >= baslangic) & (ihaleler["tarih_dt"].dt.date <= bitis)]
    giderler_filtered = giderler[(giderler["tarih_dt"].dt.date >= baslangic) & (giderler["tarih_dt"].dt.date <= bitis)]

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
        st.bar_chart(gelirler)

    # 3. Grafik: Operasyonel Giderlerin Dağılımı
    st.subheader("Operasyonel Giderlerin Dağılımı")
    gider_turleri = giderler_filtered.groupby("tip")["tutar"].sum()
    if gider_turleri.empty:
        st.write("Seçilen dönemde operasyonel gider bulunamadı.")
    else:
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

        # Profil bilgisi yoksa profil formu göster
        if user_data["profile"] is None:
            get_profile_info()
            # Profil kaydedildiyse sayfayı yenile
            if st.session_state["profil_kaydedildi"]:
                st.session_state["profil_kaydedildi"] = False
                st.experimental_rerun()
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
