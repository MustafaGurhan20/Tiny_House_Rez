# 🛖 Tiny House Reservation System

![Kotlin](https://img.shields.io/badge/Language-Kotlin-purple)
![Database](https://img.shields.io/badge/Database-SQLite-blue)
![Platform](https://img.shields.io/badge/Platform-Android-green)

## 🚀 Proje Hakkında
Bu proje, modern konaklama trendlerinden olan "Tiny House" işletmeleri için geliştirilmiş, **Native Android** tabanlı bir rezervasyon ve yönetim sistemidir.

Bulut tabanlı sistemlerden farklı olarak, **Offline-First** (Çevrimdışı Öncelikli) mimari prensibiyle tasarlanmış olup, tüm verileri **SQLite** kullanarak yerel cihazda güvenli bir şekilde saklar. Nesne Yönelimli Programlama (OOP) prensiplerine sadık kalınarak, sürdürülebilir bir kod yapısı (Clean Code) hedeflenmiştir.

## ✨ Temel Özellikler
* **Rezervasyon Yönetimi:** Müsaitlik durumuna göre tarih seçimi ve rezervasyon oluşturma algoritması.
* **Veri Kalıcılığı (Persistence):** SQLite veritabanı ile kullanıcı verilerinin, rezervasyon geçmişinin ve ödeme kayıtlarının kalıcı olarak saklanması.
* **Kullanıcı Geri Bildirimi:** Yorum ve puanlama sistemi entegrasyonu.
* **Ödeme Simülasyonu:** Güvenli ödeme akışını simüle eden modüler yapı.

## 🛠️ Tech Stack
* **Dil:** Kotlin
* **Veritabanı:** SQLite (Open Helper)
* **UI (Arayüz):** XML Layouts
* **IDE:** Android Studio

## 🏗️ Veritabanı Şeması (Basitleştirilmiş)
Projenin temel veri modeli ilişkisel veritabanı mantığına dayanır:

* **Users Table:** (ID, Name, Email, Password)
* **Houses Table:** (ID, Location, Price, Features)
* **Reservations Table:** (ID, UserID, HouseID, DateRange, Status)

## 💻 Kurulum ve Çalıştırma

Proje Android Studio ile tam uyumludur.

1. **Repoyu klonlayın:**
   ```bash
   git clone [https://github.com/MustafaGurhan20/Tiny_House_Rez.git](https://github.com/MustafaGurhan20/Tiny_House_Rez.git)
