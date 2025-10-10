#!/usr/bin/env python3
"""
Translation Batch 2: hi, tr, pl, vi, th
Hindi, Turkish, Polish, Vietnamese, Thai
"""
import json
from pathlib import Path

LANGS_DIR = Path("languages")

TRANSLATIONS_BATCH_2 = {
    # Actions
    "actions.close": {
        "hi": "बंद करें", "tr": "Kapat", "pl": "Zamknij", "vi": "Đóng", "th": "ปิด"
    },
    "actions.copy": {
        "hi": "कीवर्ड कॉपी करें", "tr": "Anahtar kelimeyi kopyala", "pl": "Kopiuj słowo kluczowe", 
        "vi": "Sao chép từ khóa", "th": "คัดลอกคำหลัก"
    },
    "actions.copied": {
        "hi": "क्लिपबोर्ड पर कॉपी किया गया!", "tr": "Panoya kopyalandı!", "pl": "Skopiowano do schowka!", 
        "vi": "Đã sao chép vào clipboard!", "th": "คัดลอกไปยังคลิปบอร์ดแล้ว!"
    },
    "actions.export": {
        "hi": "CSV निर्यात करें", "tr": "CSV dışa aktar", "pl": "Eksportuj CSV", 
        "vi": "Xuất CSV", "th": "ส่งออก CSV"
    },
    
    # Entitlements
    "entitlements.sidebar.plan_label": {
        "hi": "आपकी योजना", "tr": "Planınız", "pl": "Twój plan", "vi": "Gói của bạn", "th": "แผนของคุณ"
    },
    "entitlements.tier.free": {
        "hi": "मुफ़्त", "tr": "Ücretsiz", "pl": "Darmowy", "vi": "Miễn phí", "th": "ฟรี"
    },
    "entitlements.tier.pro": {
        "hi": "प्रो", "tr": "Pro", "pl": "Pro", "vi": "Pro", "th": "โปร"
    },
    "entitlements.tier.enterprise": {
        "hi": "एंटरप्राइज", "tr": "Kurumsal", "pl": "Firma", "vi": "Doanh nghiệp", "th": "องค์กร"
    },
    "entitlements.sidebar.ai_credits": {
        "hi": "एआई क्रेडिट", "tr": "AI Kredileri", "pl": "Kredyty AI", "vi": "Tín dụng AI", "th": "เครดิต AI"
    },
    "entitlements.actions.upgrade": {
        "hi": "प्लान अपग्रेड करें", "tr": "Planı yükselt", "pl": "Ulepsz plan", "vi": "Nâng cấp gói", "th": "อัปเกรดแผน"
    },
    "entitlements.actions.buy_credits": {
        "hi": "एआई क्रेडिट खरीदें", "tr": "AI Kredisi satın al", "pl": "Kup kredyty AI", 
        "vi": "Mua tín dụng AI", "th": "ซื้อเครดิต AI"
    },
    "entitlements.actions.upgrade_now": {
        "hi": "अभी अपग्रेड करें", "tr": "Şimdi yükselt", "pl": "Ulepsz teraz", "vi": "Nâng cấp ngay", "th": "อัปเกรดตอนนี้"
    },
    "entitlements.sidebar.ai_unlocked": {
        "hi": "एआई वर्कस्पेस अनलॉक किया गया", "tr": "AI çalışma alanı kilidi açıldı", "pl": "Obszar roboczy AI odblokowany", 
        "vi": "Không gian làm việc AI đã mở khóa", "th": "ปลดล็อกพื้นที่ทำงาน AI แล้ว"
    },
    "entitlements.sidebar.ai_locked": {
        "hi": "क्रेडिट से एआई वर्कस्पेस अनलॉक करें", "tr": "Kredi ile AI çalışma alanı kilidini aç", 
        "pl": "Odblokuj obszar roboczy AI kredytami", "vi": "Mở khóa không gian làm việc AI bằng tín dụng", 
        "th": "ปลดล็อกพื้นที่ทำงาน AI ด้วยเครดิต"
    },
    "entitlements.status.loading": {
        "hi": "प्लान लोड हो रहा है...", "tr": "Plan yükleniyor...", "pl": "Ładowanie planu...", 
        "vi": "Đang tải gói...", "th": "กำลังโหลดแผน..."
    },
    "entitlements.status.error": {
        "hi": "प्लान लोड नहीं हो सका", "tr": "Plan yüklenemedi", "pl": "Nie można załadować planu", 
        "vi": "Không thể tải gói", "th": "ไม่สามารถโหลดแผน"
    },
    "entitlements.locked.module": {
        "hi": "इस मॉड्यूल तक पहुंचने के लिए अपनी योजना अपग्रेड करें।", 
        "tr": "Bu modüle erişmek için planınızı yükseltin.", 
        "pl": "Ulepsz swój plan, aby uzyskać dostęp do tego modułu.", 
        "vi": "Nâng cấp gói của bạn để truy cập mô-đun này.", 
        "th": "อัปเกรดแผนของคุณเพื่อเข้าถึงโมดูลนี้"
    },
    "entitlements.sidebar.expires": {
        "hi": "{{formatted}} को नवीनीकृत होता है", "tr": "{{formatted}} tarihinde yenilenir", 
        "pl": "Odnawia się {{formatted}}", "vi": "Gia hạn vào {{formatted}}", "th": "ต่ออายุเมื่อ {{formatted}}"
    },
    
    # Billing
    "billing.error.checkout_failed": {
        "hi": "चेकआउट नहीं खोल सके। पुनः प्रयास करें।", "tr": "Ödeme açılamadı. Lütfen tekrar deneyin.", 
        "pl": "Nie można otworzyć kasy. Spróbuj ponownie.", "vi": "Không thể mở thanh toán. Vui lòng thử lại.", 
        "th": "ไม่สามารถเปิดชำระเงินได้ โปรดลองอีกครั้ง"
    },
    "billing.error.signin_required": {
        "hi": "अपग्रेड करने के लिए कृपया साइन इन करें।", "tr": "Yükseltmek için lütfen giriş yapın.", 
        "pl": "Zaloguj się, aby uaktualnić.", "vi": "Vui lòng đăng nhập để nâng cấp.", 
        "th": "กรุณาเข้าสู่ระบบเพื่ออัปเกรด"
    },
    "billing.error.upgrade_unavailable": {
        "hi": "अपग्रेड वर्तमान में उपलब्ध नहीं है। कृपया सहायता से संपर्क करें।", 
        "tr": "Yükseltme şu anda mevcut değil. Lütfen destek ile iletişime geçin.", 
        "pl": "Aktualizacja jest obecnie niedostępna. Skontaktuj się z pomocą techniczną.", 
        "vi": "Nâng cấp hiện không khả dụng. Vui lòng liên hệ hỗ trợ.", 
        "th": "การอัปเกรดไม่พร้อมใช้งานในขณะนี้ กรุณาติดต่อฝ่ายสนับสนุน"
    },
    "billing.error.buy_credits_signin": {
        "hi": "एआई क्रेडिट खरीदने के लिए साइन इन करें।", "tr": "AI Kredisi satın almak için giriş yapın.", 
        "pl": "Zaloguj się, aby kupić kredyty AI.", "vi": "Đăng nhập để mua tín dụng AI.", 
        "th": "เข้าสู่ระบบเพื่อซื้อเครดิต AI"
    },
    "billing.error.buy_credits_unavailable": {
        "hi": "एआई क्रेडिट खरीद अभी उपलब्ध नहीं है। कृपया सहायता से संपर्क करें।", 
        "tr": "AI Kredisi satın alma şu anda mevcut değil. Lütfen destek ile iletişime geçin.", 
        "pl": "Zakup kredytów AI jest obecnie niedostępny. Skontaktuj się z pomocą techniczną.", 
        "vi": "Mua tín dụng AI hiện không khả dụng. Vui lòng liên hệ hỗ trợ.", 
        "th": "การซื้อเครดิต AI ไม่พร้อมใช้งานในขณะนี้ กรุณาติดต่อฝ่ายสนับสนุน"
    },
    "billing.status.launching_checkout": {
        "hi": "चेकआउट खोला जा रहा है...", "tr": "Ödeme açılıyor...", "pl": "Otwieranie kasy...", 
        "vi": "Đang mở thanh toán...", "th": "กำลังเปิดชำระเงิน..."
    },
    "billing.status.loading_credit_packs": {
        "hi": "क्रेडिट पैक लोड हो रहे हैं...", "tr": "Kredi paketleri yükleniyor...", "pl": "Ładowanie pakietów kredytowych...", 
        "vi": "Đang tải gói tín dụng...", "th": "กำลังโหลดแพ็กเครดิต..."
    },
    
    # Search
    "search.status.loading": {
        "hi": "कीवर्ड विश्लेषण चल रहा है...", "tr": "Anahtar kelime analizi çalışıyor...", 
        "pl": "Uruchamianie analizy słów kluczowych...", "vi": "Đang chạy phân tích từ khóa...", 
        "th": "กำลังวิเคราะห์คำหลัก..."
    },
    
    # CTA & Hero
    "cta.upgrade_title": {
        "hi": "पूर्ण शक्ति अनलॉक करें", "tr": "Tam Gücü Açın", "pl": "Odblokuj pełną moc", 
        "vi": "Mở khóa toàn bộ sức mạnh", "th": "ปลดล็อกพลังเต็มรูปแบบ"
    },
    "cta.upgrade_description": {
        "hi": "असीमित खोज और एआई इनसाइट्स प्राप्त करें", "tr": "Sınırsız arama ve AI içgörüleri edinin", 
        "pl": "Uzyskaj nieograniczone wyszukiwania i analizy AI", "vi": "Nhận tìm kiếm không giới hạn và thông tin chi tiết về AI", 
        "th": "รับการค้นหาไม่จำกัดและข้อมูลเชิงลึก AI"
    },
    "cta.upgrade_button": {
        "hi": "अभी अपग्रेड करें", "tr": "Şimdi Yükselt", "pl": "Ulepsz teraz", "vi": "Nâng cấp ngay", "th": "อัปเกรดตอนนี้"
    },
    "hero.title": {
        "hi": "बहु-बाजार कीवर्ड इंटेलिजेंस", "tr": "Çok Pazarlı Anahtar Kelime İstihbaratı", 
        "pl": "Wielorynkowa inteligencja słów kluczowych", "vi": "Thông tin từ khóa đa thị trường", 
        "th": "ข้อมูลคำหลักหลายตลาด"
    },
    "hero.subtitle": {
        "hi": "100+ देशों और प्लेटफ़ॉर्म पर कीवर्ड रिसर्च करें। Google, YouTube, Amazon और अधिक से रियल-टाइम सर्च डेटा प्राप्त करें।", 
        "tr": "100'den fazla ülke ve platformda anahtar kelime araştırması yapın. Google, YouTube, Amazon ve daha fazlasından gerçek zamanlı arama verisi alın.", 
        "pl": "Badaj słowa kluczowe w ponad 100 krajach i platformach. Uzyskaj dane wyszukiwania w czasie rzeczywistym z Google, YouTube, Amazon i innych.", 
        "vi": "Nghiên cứu từ khóa trên hơn 100 quốc gia và nền tảng. Nhận dữ liệu tìm kiếm thời gian thực từ Google, YouTube, Amazon và nhiều hơn nữa.", 
        "th": "วิจัยคำหลักใน 100+ ประเทศและแพลตฟอร์ม รับข้อมูลการค้นหาแบบเรียลไทม์จาก Google, YouTube, Amazon และอื่นๆ"
    },
    "hero.cta_primary": {
        "hi": "कीवर्ड एक्सप्लोर करना शुरू करें", "tr": "Anahtar kelimeleri keşfetmeye başlayın", 
        "pl": "Zacznij eksplorować słowa kluczowe", "vi": "Bắt đầu khám phá từ khóa", "th": "เริ่มสำรวจคำหลัก"
    },
    "hero.cta_secondary": {
        "hi": "मूल्य निर्धारण और योजनाएं देखें", "tr": "Fiyatlandırma ve planları görün", 
        "pl": "Zobacz ceny i plany", "vi": "Xem giá và gói", "th": "ดูราคาและแผน"
    },
    "hero.trust_markets": {
        "hi": "{{count}}+ बाजार", "tr": "{{count}}+ pazar", "pl": "{{count}}+ rynków", 
        "vi": "{{count}}+ thị trường", "th": "{{count}}+ ตลาด"
    },
    "hero.trust_refresh": {
        "hi": "रियल-टाइम डेटा", "tr": "Gerçek zamanlı veri", "pl": "Dane w czasie rzeczywistym", 
        "vi": "Dữ liệu thời gian thực", "th": "ข้อมูลแบบเรียลไทม์"
    },
    "hero.trust_teams": {
        "hi": "टीमें साप्ताहिक रूप से शिपिंग कर रही हैं", "tr": "Haftalık gönderi yapan ekipler", 
        "pl": "Zespoły dostarczające cotygodniowo", "vi": "Các nhóm xuất bản hàng tuần", 
        "th": "ทีมที่ส่งมอบรายสัปดาห์"
    },
    
    # Features
    "features.semantic.title": {
        "hi": "सिमेंटिक क्लस्टरिंग", "tr": "Anlamsal Kümeleme", "pl": "Klastrowanie semantyczne", 
        "vi": "Phân cụm ngữ nghĩa", "th": "การจัดกลุ่มตามความหมาย"
    },
    "features.semantic.description": {
        "hi": "एआई-संचालित कीवर्ड ग्रुपिंग जो खोज इरादे और उपयोगकर्ता व्यवहार पैटर्न को समझती है", 
        "tr": "Arama amacını ve kullanıcı davranış modellerini anlayan AI destekli anahtar kelime gruplama", 
        "pl": "Grupowanie słów kluczowych wspomagane AI, które rozumie intencje wyszukiwania i wzorce zachowań użytkowników", 
        "vi": "Nhóm từ khóa hỗ trợ AI hiểu ý định tìm kiếm và mô hình hành vi người dùng", 
        "th": "การจัดกลุ่มคำหลักด้วย AI ที่เข้าใจเจตนาการค้นหาและรูปแบบพฤติกรรมผู้ใช้"
    },
    "features.localization.title": {
        "hi": "वैश्विक स्थानीयकरण", "tr": "Küresel Yerelleştirme", "pl": "Globalna lokalizacja", 
        "vi": "Bản địa hóa toàn cầu", "th": "การแปลเป็นภาษาท้องถิ่นทั่วโลก"
    },
    "features.localization.description": {
        "hi": "100+ देशों में मूल भाषा समर्थन और क्षेत्रीय अंतर्दृष्टि के साथ कीवर्ड रिसर्च करें", 
        "tr": "100'den fazla ülkede yerel dil desteği ve bölgesel içgörülerle anahtar kelime araştırması yapın", 
        "pl": "Badaj słowa kluczowe w ponad 100 krajach z rodzimym wsparciem językowym i regionalnymi spostrzeżeniami", 
        "vi": "Nghiên cứu từ khóa ở hơn 100 quốc gia với hỗ trợ ngôn ngữ bản địa và thông tin chi tiết khu vực", 
        "th": "วิจัยคำหลักใน 100+ ประเทศพร้อมการสนับสนุนภาษาท้องถิ่นและข้อมูลเชิงลึกในภูมิภาค"
    },
    "features.ai_briefs.title": {
        "hi": "एआई सामग्री ब्रीफ", "tr": "AI İçerik Özeti", "pl": "Briefy treści AI", 
        "vi": "Tóm tắt nội dung AI", "th": "สรุปเนื้อหา AI"
    },
    "features.ai_briefs.description": {
        "hi": "लाइव SERP विश्लेषण और प्रतियोगी अनुसंधान के आधार पर डेटा-संचालित सामग्री अनुशंसाएं प्राप्त करें", 
        "tr": "Canlı SERP analizi ve rakip araştırmasına dayalı veri odaklı içerik önerileri alın", 
        "pl": "Uzyskaj rekomendacje treści oparte na danych w oparciu o analizę SERP na żywo i badania konkurencji", 
        "vi": "Nhận đề xuất nội dung dựa trên dữ liệu dựa trên phân tích SERP trực tiếp và nghiên cứu đối thủ cạnh tranh", 
        "th": "รับคำแนะนำเนื้อหาที่ขับเคลื่อนด้วยข้อมูลตามการวิเคราะห์ SERP สดและการวิจัยคู่แข่ง"
    },
}

def apply_translations(lang_codes):
    for lang_code in lang_codes:
        locale_file = LANGS_DIR / lang_code / "locale.json"
        if not locale_file.exists():
            print(f"⚠️  {lang_code} locale file not found")
            continue
        
        with open(locale_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        strings = data.get('strings', {})
        updated = 0
        
        for key, translations in TRANSLATIONS_BATCH_2.items():
            if key in strings and lang_code in translations:
                strings[key] = translations[lang_code]
                updated += 1
        
        if updated > 0:
            data['strings'] = dict(sorted(strings.items()))
            with open(locale_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write('\n')
            print(f"✅ Updated {updated} keys in {lang_code}")

# Apply to batch 2 languages
batch_2_langs = ['hi', 'tr', 'pl', 'vi', 'th']
print(f"🌍 Translating Batch 2: {', '.join(batch_2_langs)}\n")
apply_translations(batch_2_langs)
print(f"\n🎉 Batch 2 complete! Translated keys for: {', '.join(batch_2_langs)}")
