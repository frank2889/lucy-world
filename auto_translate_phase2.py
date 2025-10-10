#!/usr/bin/env python3
"""
Extended Auto-Translation - Phase 2
Adds professional translations for major languages
"""
import json
from pathlib import Path

LANGS_DIR = Path("languages")

# Extended professional translations for major world languages
EXTENDED_TRANSLATIONS = {
    # Hungarian (hu)
    "hu": {
        "actions.close": "Bezárás",
        "actions.copy": "Kulcsszó másolása",
        "actions.copied": "Vágólapra másolva!",
        "actions.export": "CSV exportálása",
        "entitlements.sidebar.plan_label": "Az Ön csomagja",
        "entitlements.tier.free": "Ingyenes",
        "entitlements.tier.pro": "Pro",
        "entitlements.tier.enterprise": "Vállalati",
        "entitlements.sidebar.ai_credits": "AI kreditek",
        "entitlements.actions.upgrade": "Csomag frissítése",
        "entitlements.actions.buy_credits": "AI kreditek vásárlása",
        "entitlements.actions.upgrade_now": "Frissítés most",
        "entitlements.sidebar.ai_unlocked": "AI munkaterület feloldva",
        "entitlements.sidebar.ai_locked": "AI munkaterület feloldása kreditekkel",
        "entitlements.status.loading": "Csomag betöltése...",
        "entitlements.status.error": "Nem sikerült betölteni a csomagot",
        "entitlements.locked.module": "Frissítse csomagját a modul eléréséhez.",
        "entitlements.sidebar.expires": "Megújul: {{formatted}}",
        "billing.error.checkout_failed": "Nem sikerült megnyitni a fizetést. Próbálja újra.",
        "billing.error.signin_required": "Kérjük, jelentkezzen be a frissítéshez.",
        "billing.error.upgrade_unavailable": "A frissítés jelenleg nem érhető el. Forduljon az ügyfélszolgálathoz.",
        "billing.error.buy_credits_signin": "Jelentkezzen be AI kreditek vásárlásához.",
        "billing.error.buy_credits_unavailable": "Az AI kredit vásárlás jelenleg nem érhető el. Forduljon az ügyfélszolgálathoz.",
        "billing.status.launching_checkout": "Fizetés megnyitása...",
        "billing.status.loading_credit_packs": "Kreditcsomagok betöltése...",
        "search.status.loading": "Kulcsszó-elemzés futtatása...",
        "cta.upgrade_title": "Teljes erő feloldása",
        "cta.upgrade_description": "Szerezzen korlátlan kereséseket és AI betekintéseket",
        "cta.upgrade_button": "Frissítés most",
        "hero.title": "Többpiaci kulcsszó-intelligencia",
        "hero.subtitle": "Kutasson kulcsszavakat 100+ országban és platformon. Kapjon valós idejű keresési adatokat a Google-tól, YouTube-tól, Amazontól és másoktól.",
        "hero.cta_primary": "Kezdje el a kulcsszavak felfedezését",
        "hero.cta_secondary": "Árak és csomagok megtekintése",
        "hero.trust_markets": "{{count}}+ piac",
        "hero.trust_refresh": "Valós idejű adatok",
        "hero.trust_teams": "Csapatok hetente szállítanak",
        "features.semantic.title": "Szemantikus csoportosítás",
        "features.semantic.description": "AI-vezérelt kulcsszó-csoportosítás, amely megérti a keresési szándékot és a felhasználói viselkedési mintákat",
        "features.localization.title": "Globális lokalizáció",
        "features.localization.description": "Kutasson kulcsszavakat 100+ országban anyanyelvi támogatással és regionális betekintésekkel",
        "features.ai_briefs.title": "AI tartalmi összefoglalók",
        "features.ai_briefs.description": "Kapjon adatvezérelt tartalmi javaslatokat élő SERP elemzés és versenytárs-kutatás alapján",
    },
    
    # Ukrainian (uk)
    "uk": {
        "actions.close": "Закрити",
        "actions.copy": "Копіювати ключове слово",
        "actions.copied": "Скопійовано в буфер обміну!",
        "actions.export": "Експортувати CSV",
        "entitlements.sidebar.plan_label": "Ваш план",
        "entitlements.tier.free": "Безкоштовно",
        "entitlements.tier.pro": "Pro",
        "entitlements.tier.enterprise": "Підприємство",
        "entitlements.sidebar.ai_credits": "AI кредити",
        "entitlements.actions.upgrade": "Оновити план",
        "entitlements.actions.buy_credits": "Купити AI кредити",
        "entitlements.actions.upgrade_now": "Оновити зараз",
        "entitlements.sidebar.ai_unlocked": "AI робочий простір розблоковано",
        "entitlements.sidebar.ai_locked": "Розблокуйте AI робочий простір кредитами",
        "entitlements.status.loading": "Завантаження плану...",
        "entitlements.status.error": "Не вдалося завантажити план",
        "entitlements.locked.module": "Оновіть свій план для доступу до цього модуля.",
        "entitlements.sidebar.expires": "Поновлюється {{formatted}}",
        "billing.error.checkout_failed": "Не вдалося відкрити оплату. Спробуйте ще раз.",
        "billing.error.signin_required": "Будь ласка, увійдіть для оновлення.",
        "billing.error.upgrade_unavailable": "Оновлення наразі недоступне. Зверніться до підтримки.",
        "billing.error.buy_credits_signin": "Увійдіть, щоб купити AI кредити.",
        "billing.error.buy_credits_unavailable": "Купівля AI кредитів зараз недоступна. Зверніться до підтримки.",
        "billing.status.launching_checkout": "Відкриття оплати...",
        "billing.status.loading_credit_packs": "Завантаження пакетів кредитів...",
        "search.status.loading": "Виконання аналізу ключових слів...",
        "cta.upgrade_title": "Розблокуйте повну потужність",
        "cta.upgrade_description": "Отримайте необмежені пошуки та AI аналітику",
        "cta.upgrade_button": "Оновити зараз",
        "hero.title": "Багаторинкова розвідка ключових слів",
        "hero.subtitle": "Досліджуйте ключові слова в 100+ країнах і платформах. Отримуйте дані пошуку в реальному часі з Google, YouTube, Amazon та інших.",
        "hero.cta_primary": "Почати досліджувати ключові слова",
        "hero.cta_secondary": "Переглянути ціни та плани",
        "hero.trust_markets": "{{count}}+ ринків",
        "hero.trust_refresh": "Дані в реальному часі",
        "hero.trust_teams": "Команди доставляють щотижня",
        "features.semantic.title": "Семантичне кластеризація",
        "features.semantic.description": "AI-керовано групування ключових слів, яке розуміє намір пошуку та шаблони поведінки користувачів",
        "features.localization.title": "Глобальна локалізація",
        "features.localization.description": "Досліджуйте ключові слова в 100+ країнах з підтримкою рідної мови та регіональними insights",
        "features.ai_briefs.title": "AI контентні брифи",
        "features.ai_briefs.description": "Отримуйте рекомендації контенту на основі даних за допомогою аналізу SERP в реальному часі та дослідження конкурентів",
    },
    
    # Hebrew (he)
    "he": {
        "actions.close": "סגור",
        "actions.copy": "העתק מילת מפתח",
        "actions.copied": "הועתק ללוח!",
        "actions.export": "ייצא CSV",
        "entitlements.sidebar.plan_label": "התוכנית שלך",
        "entitlements.tier.free": "חינם",
        "entitlements.tier.pro": "מקצועי",
        "entitlements.tier.enterprise": "ארגוני",
        "entitlements.sidebar.ai_credits": "קרדיטים AI",
        "entitlements.actions.upgrade": "שדרג תוכנית",
        "entitlements.actions.buy_credits": "קנה קרדיטים AI",
        "entitlements.actions.upgrade_now": "שדרג עכשיו",
        "entitlements.sidebar.ai_unlocked": "סביבת עבודה AI נפתחה",
        "entitlements.sidebar.ai_locked": "פתח סביבת עבודה AI עם קרדיטים",
        "entitlements.status.loading": "טוען תוכנית...",
        "entitlements.status.error": "לא ניתן לטעון תוכנית",
        "entitlements.locked.module": "שדרג את התוכנית שלך כדי לגשת למודול זה.",
        "entitlements.sidebar.expires": "מתחדש ב-{{formatted}}",
        "billing.error.checkout_failed": "לא ניתן לפתוח תשלום. נסה שוב.",
        "billing.error.signin_required": "אנא התחבר כדי לשדרג.",
        "billing.error.upgrade_unavailable": "השדרוג אינו זמין כרגע. פנה לתמיכה.",
        "billing.error.buy_credits_signin": "התחבר כדי לקנות קרדיטים AI.",
        "billing.error.buy_credits_unavailable": "רכישת קרדיטים AI אינה זמינה כרגע. פנה לתמיכה.",
        "billing.status.launching_checkout": "פותח תשלום...",
        "billing.status.loading_credit_packs": "טוען חבילות קרדיט...",
        "search.status.loading": "מריץ ניתוח מילות מפתח...",
        "cta.upgrade_title": "פתח עוצמה מלאה",
        "cta.upgrade_description": "קבל חיפושים בלתי מוגבלים ותובנות AI",
        "cta.upgrade_button": "שדרג עכשיו",
        "hero.title": "מודיעין מילות מפתח רב-שווקי",
        "hero.subtitle": "חקור מילות מפתח ב-100+ מדינות ופלטפורמות. קבל נתוני חיפוש בזמן אמת מ-Google, YouTube, Amazon ועוד.",
        "hero.cta_primary": "התחל לחקור מילות מפתח",
        "hero.cta_secondary": "ראה תמחור ותוכניות",
        "hero.trust_markets": "{{count}}+ שווקים",
        "hero.trust_refresh": "נתונים בזמן אמת",
        "hero.trust_teams": "צוותים משגרים שבועית",
        "features.semantic.title": "קיבוץ סמנטי",
        "features.semantic.description": "קיבוץ מילות מפתח מונע AI שמבין כוונת חיפוש ודפוסי התנהגות משתמשים",
        "features.localization.title": "לוקליזציה גלובלית",
        "features.localization.description": "חקור מילות מפתח ב-100+ מדינות עם תמיכה בשפה מקומית ותובנות אזוריות",
        "features.ai_briefs.title": "תקצירי תוכן AI",
        "features.ai_briefs.description": "קבל המלצות תוכן מונעות נתונים המבוססות על ניתוח SERP חי ומחקר מתחרים",
    },
    
    # Bengali (bn)
    "bn": {
        "actions.close": "বন্ধ করুন",
        "actions.copy": "কীওয়ার্ড কপি করুন",
        "actions.copied": "ক্লিপবোর্ডে কপি করা হয়েছে!",
        "actions.export": "CSV এক্সপোর্ট করুন",
        "entitlements.sidebar.plan_label": "আপনার প্ল্যান",
        "entitlements.tier.free": "ফ্রি",
        "entitlements.tier.pro": "প্রো",
        "entitlements.tier.enterprise": "এন্টারপ্রাইজ",
        "entitlements.sidebar.ai_credits": "এআই ক্রেডিট",
        "entitlements.actions.upgrade": "প্ল্যান আপগ্রেড করুন",
        "entitlements.actions.buy_credits": "এআই ক্রেডিট কিনুন",
        "entitlements.actions.upgrade_now": "এখনই আপগ্রেড করুন",
        "entitlements.sidebar.ai_unlocked": "এআই ওয়ার্কস্পেস আনলক করা হয়েছে",
        "entitlements.sidebar.ai_locked": "ক্রেডিট দিয়ে এআই ওয়ার্কস্পেস আনলক করুন",
        "entitlements.status.loading": "প্ল্যান লোড হচ্ছে...",
        "entitlements.status.error": "প্ল্যান লোড করা যায়নি",
        "entitlements.locked.module": "এই মডিউল অ্যাক্সেস করতে আপনার প্ল্যান আপগ্রেড করুন।",
        "entitlements.sidebar.expires": "{{formatted}} তে নবায়ন হবে",
        "billing.error.checkout_failed": "চেকআউট খোলা যায়নি। আবার চেষ্টা করুন।",
        "billing.error.signin_required": "আপগ্রেড করতে সাইন ইন করুন।",
        "billing.error.upgrade_unavailable": "আপগ্রেড বর্তমানে উপলব্ধ নেই। সাপোর্টের সাথে যোগাযোগ করুন।",
        "billing.error.buy_credits_signin": "এআই ক্রেডিট কিনতে সাইন ইন করুন।",
        "billing.error.buy_credits_unavailable": "এআই ক্রেডিট কেনা এখন উপলব্ধ নেই। সাপোর্টের সাথে যোগাযোগ করুন।",
        "billing.status.launching_checkout": "চেকআউট খোলা হচ্ছে...",
        "billing.status.loading_credit_packs": "ক্রেডিট প্যাক লোড হচ্ছে...",
        "search.status.loading": "কীওয়ার্ড বিশ্লেষণ চলছে...",
        "cta.upgrade_title": "সম্পূর্ণ শক্তি আনলক করুন",
        "cta.upgrade_description": "সীমাহীন সার্চ এবং এআই ইনসাইট পান",
        "cta.upgrade_button": "এখনই আপগ্রেড করুন",
        "hero.title": "মাল্টি-মার্কেট কীওয়ার্ড ইন্টেলিজেন্স",
        "hero.subtitle": "১০০+ দেশ এবং প্ল্যাটফর্মে কীওয়ার্ড গবেষণা করুন। Google, YouTube, Amazon এবং আরও অনেক কিছু থেকে রিয়েল-টাইম সার্চ ডেটা পান।",
        "hero.cta_primary": "কীওয়ার্ড এক্সপ্লোর করা শুরু করুন",
        "hero.cta_secondary": "মূল্য এবং প্ল্যান দেখুন",
        "hero.trust_markets": "{{count}}+ মার্কেট",
        "hero.trust_refresh": "রিয়েল-টাইম ডেটা",
        "hero.trust_teams": "টিম সাপ্তাহিক শিপিং করছে",
        "features.semantic.title": "সিমান্টিক ক্লাস্টারিং",
        "features.semantic.description": "এআই-চালিত কীওয়ার্ড গ্রুপিং যা সার্চ ইন্টেন্ট এবং ইউজার বিহেভিয়ার প্যাটার্ন বোঝে",
        "features.localization.title": "গ্লোবাল লোকালাইজেশন",
        "features.localization.description": "১০০+ দেশে নেটিভ ভাষা সাপোর্ট এবং আঞ্চলিক ইনসাইট দিয়ে কীওয়ার্ড গবেষণা করুন",
        "features.ai_briefs.title": "এআই কন্টেন্ট ব্রিফ",
        "features.ai_briefs.description": "লাইভ SERP বিশ্লেষণ এবং প্রতিযোগী গবেষণার ভিত্তিতে ডেটা-চালিত কন্টেন্ট সুপারিশ পান",
    },
    
    # Croatian (hr)
    "hr": {
        "actions.close": "Zatvori",
        "actions.copy": "Kopiraj ključnu riječ",
        "actions.copied": "Kopirano u međuspremnik!",
        "actions.export": "Izvezi CSV",
        "entitlements.sidebar.plan_label": "Vaš plan",
        "entitlements.tier.free": "Besplatno",
        "entitlements.tier.pro": "Pro",
        "entitlements.tier.enterprise": "Enterprise",
        "entitlements.sidebar.ai_credits": "AI krediti",
        "entitlements.actions.upgrade": "Nadogradi plan",
        "entitlements.actions.buy_credits": "Kupi AI kredite",
        "entitlements.actions.upgrade_now": "Nadogradi sada",
        "entitlements.sidebar.ai_unlocked": "AI radni prostor otključan",
        "entitlements.sidebar.ai_locked": "Otključaj AI radni prostor kreditima",
        "entitlements.status.loading": "Učitavanje plana...",
        "entitlements.status.error": "Nije moguće učitati plan",
        "entitlements.locked.module": "Nadogradite svoj plan za pristup ovom modulu.",
        "entitlements.sidebar.expires": "Obnavlja se {{formatted}}",
        "billing.error.checkout_failed": "Nije moguće otvoriti naplatu. Pokušajte ponovno.",
        "billing.error.signin_required": "Prijavite se za nadogradnju.",
        "billing.error.upgrade_unavailable": "Nadogradnja trenutno nije dostupna. Kontaktirajte podršku.",
        "billing.error.buy_credits_signin": "Prijavite se za kupnju AI kredita.",
        "billing.error.buy_credits_unavailable": "Kupnja AI kredita trenutno nije dostupna. Kontaktirajte podršku.",
        "billing.status.launching_checkout": "Otvaranje naplate...",
        "billing.status.loading_credit_packs": "Učitavanje paketa kredita...",
        "search.status.loading": "Pokretanje analize ključnih riječi...",
        "cta.upgrade_title": "Otključaj punu snagu",
        "cta.upgrade_description": "Dobij neograničene pretrage i AI uvide",
        "cta.upgrade_button": "Nadogradi sada",
        "hero.title": "Višetržišna inteligencija ključnih riječi",
        "hero.subtitle": "Istraži ključne riječi u 100+ zemalja i platformi. Dobij podatke o pretraživanju u stvarnom vremenu s Googlea, YouTubea, Amazona i još mnogo toga.",
        "hero.cta_primary": "Započni istraživanje ključnih riječi",
        "hero.cta_secondary": "Pogledaj cijene i planove",
        "hero.trust_markets": "{{count}}+ tržišta",
        "hero.trust_refresh": "Podaci u stvarnom vremenu",
        "hero.trust_teams": "Timovi isporučuju tjedno",
        "features.semantic.title": "Semantičko grupiranje",
        "features.semantic.description": "AI-pokretano grupiranje ključnih riječi koje razumije namjeru pretraživanja i obrasce ponašanja korisnika",
        "features.localization.title": "Globalna lokalizacija",
        "features.localization.description": "Istraži ključne riječi u 100+ zemalja s podrškom za izvorni jezik i regionalnim uvidima",
        "features.ai_briefs.title": "AI prijedlozi sadržaja",
        "features.ai_briefs.description": "Dobij preporuke sadržaja temeljene na podacima na temelju analize SERP-a uživo i istraživanja konkurencije",
    },
}

def apply_extended_translations():
    total_updated = 0
    
    for lang_code, translations in EXTENDED_TRANSLATIONS.items():
        locale_file = LANGS_DIR / lang_code / "locale.json"
        
        if not locale_file.exists():
            print(f"⚠️  {lang_code}: locale file not found")
            continue
        
        with open(locale_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        strings = data.get('strings', {})
        updated = 0
        
        for key, value in translations.items():
            # Replace any [NEEDS TRANSLATION] markers with real translations
            if key in strings:
                old_value = strings[key]
                if old_value.startswith("[NEEDS TRANSLATION:") or old_value != value:
                    strings[key] = value
                    updated += 1
            else:
                strings[key] = value
                updated += 1
        
        if updated > 0:
            data['strings'] = dict(sorted(strings.items()))
            with open(locale_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write('\n')
            
            print(f"✅ {lang_code}: Updated {updated} keys with professional translations")
            total_updated += 1
    
    return total_updated

print("🌍 Extended Auto-Translation - Phase 2")
print("=" * 60)
print(f"Adding professional translations for {len(EXTENDED_TRANSLATIONS)} languages\n")

updated = apply_extended_translations()

print(f"\n{'='*60}")
print(f"✨ Phase 2 Complete!")
print(f"✅ {updated} languages updated with professional translations")
print(f"📝 Replacing [NEEDS TRANSLATION] markers with real content")
