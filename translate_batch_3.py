#!/usr/bin/env python3
"""
Translation Batch 3: en, id, nl, sv, no
English (base reference), Indonesian, Dutch, Swedish, Norwegian
"""
import json
from pathlib import Path

LANGS_DIR = Path("languages")

TRANSLATIONS_BATCH_3 = {
    # Actions (already exist in EN but including for consistency)
    "actions.close": {
        "en": "Close", "id": "Tutup", "nl": "Sluiten", "sv": "Stäng", "no": "Lukk"
    },
    "actions.copy": {
        "en": "Copy Keyword", "id": "Salin Kata Kunci", "nl": "Kopieer zoekwoord", 
        "sv": "Kopiera nyckelord", "no": "Kopier nøkkelord"
    },
    "actions.copied": {
        "en": "Copied to clipboard!", "id": "Disalin ke clipboard!", "nl": "Gekopieerd naar klembord!", 
        "sv": "Kopierat till urklipp!", "no": "Kopiert til utklippstavle!"
    },
    "actions.export": {
        "en": "Export CSV", "id": "Ekspor CSV", "nl": "Exporteer CSV", 
        "sv": "Exportera CSV", "no": "Eksporter CSV"
    },
    
    # Entitlements (MISSING in EN - adding base English)
    "entitlements.sidebar.plan_label": {
        "en": "Your plan", "id": "Paket Anda", "nl": "Uw abonnement", "sv": "Ditt abonnemang", "no": "Din plan"
    },
    "entitlements.tier.free": {
        "en": "Free", "id": "Gratis", "nl": "Gratis", "sv": "Gratis", "no": "Gratis"
    },
    "entitlements.tier.pro": {
        "en": "Pro", "id": "Pro", "nl": "Pro", "sv": "Pro", "no": "Pro"
    },
    "entitlements.tier.enterprise": {
        "en": "Enterprise", "id": "Enterprise", "nl": "Enterprise", "sv": "Enterprise", "no": "Bedrift"
    },
    "entitlements.sidebar.ai_credits": {
        "en": "AI Credits", "id": "Kredit AI", "nl": "AI-credits", "sv": "AI-krediter", "no": "AI-kreditter"
    },
    "entitlements.actions.upgrade": {
        "en": "Upgrade plan", "id": "Tingkatkan paket", "nl": "Upgrade abonnement", 
        "sv": "Uppgradera abonnemang", "no": "Oppgrader plan"
    },
    "entitlements.actions.buy_credits": {
        "en": "Buy AI credits", "id": "Beli kredit AI", "nl": "Koop AI-credits", 
        "sv": "Köp AI-krediter", "no": "Kjøp AI-kreditter"
    },
    "entitlements.actions.upgrade_now": {
        "en": "Upgrade now", "id": "Tingkatkan sekarang", "nl": "Nu upgraden", 
        "sv": "Uppgradera nu", "no": "Oppgrader nå"
    },
    "entitlements.sidebar.ai_unlocked": {
        "en": "AI workspace unlocked", "id": "Ruang kerja AI terbuka", "nl": "AI-werkruimte ontgrendeld", 
        "sv": "AI-arbetsyta upplåst", "no": "AI-arbeidsområde låst opp"
    },
    "entitlements.sidebar.ai_locked": {
        "en": "Unlock AI workspace with credits", "id": "Buka ruang kerja AI dengan kredit", 
        "nl": "Ontgrendel AI-werkruimte met credits", "sv": "Lås upp AI-arbetsyta med krediter", 
        "no": "Lås opp AI-arbeidsområde med kreditter"
    },
    "entitlements.status.loading": {
        "en": "Loading plan...", "id": "Memuat paket...", "nl": "Abonnement laden...", 
        "sv": "Laddar abonnemang...", "no": "Laster plan..."
    },
    "entitlements.status.error": {
        "en": "Could not load plan", "id": "Tidak dapat memuat paket", "nl": "Kan abonnement niet laden", 
        "sv": "Kunde inte ladda abonnemang", "no": "Kunne ikke laste plan"
    },
    "entitlements.locked.module": {
        "en": "Upgrade your plan to access this module.", 
        "id": "Tingkatkan paket Anda untuk mengakses modul ini.", 
        "nl": "Upgrade uw abonnement om toegang te krijgen tot deze module.", 
        "sv": "Uppgradera ditt abonnemang för att få tillgång till denna modul.", 
        "no": "Oppgrader planen din for å få tilgang til denne modulen."
    },
    "entitlements.sidebar.expires": {
        "en": "Renews on {{formatted}}", "id": "Diperpanjang pada {{formatted}}", 
        "nl": "Verlengt op {{formatted}}", "sv": "Förnyas {{formatted}}", "no": "Fornyes {{formatted}}"
    },
    
    # Billing (already exist in EN)
    "billing.error.checkout_failed": {
        "en": "Unable to open checkout. Please try again.", 
        "id": "Tidak dapat membuka checkout. Silakan coba lagi.", 
        "nl": "Kan checkout niet openen. Probeer het opnieuw.", 
        "sv": "Kan inte öppna kassan. Försök igen.", 
        "no": "Kan ikke åpne kassen. Vennligst prøv igjen."
    },
    "billing.error.signin_required": {
        "en": "Please sign in to upgrade.", "id": "Silakan masuk untuk meningkatkan.", 
        "nl": "Log in om te upgraden.", "sv": "Vänligen logga in för att uppgradera.", 
        "no": "Vennligst logg inn for å oppgradere."
    },
    "billing.error.upgrade_unavailable": {
        "en": "Upgrade is currently unavailable. Please contact support.", 
        "id": "Peningkatan saat ini tidak tersedia. Silakan hubungi dukungan.", 
        "nl": "Upgrade is momenteel niet beschikbaar. Neem contact op met ondersteuning.", 
        "sv": "Uppgradering är för närvarande inte tillgänglig. Vänligen kontakta support.", 
        "no": "Oppgradering er for øyeblikket ikke tilgjengelig. Vennligst kontakt support."
    },
    "billing.error.buy_credits_signin": {
        "en": "Sign in to buy AI credits.", "id": "Masuk untuk membeli kredit AI.", 
        "nl": "Log in om AI-credits te kopen.", "sv": "Logga in för att köpa AI-krediter.", 
        "no": "Logg inn for å kjøpe AI-kreditter."
    },
    "billing.error.buy_credits_unavailable": {
        "en": "AI credit purchase is unavailable right now. Please contact support.", 
        "id": "Pembelian kredit AI tidak tersedia saat ini. Silakan hubungi dukungan.", 
        "nl": "AI-creditaankoop is momenteel niet beschikbaar. Neem contact op met ondersteuning.", 
        "sv": "AI-kreditköp är inte tillgängligt just nu. Vänligen kontakta support.", 
        "no": "AI-kredittkjøp er ikke tilgjengelig akkurat nå. Vennligst kontakt support."
    },
    "billing.status.launching_checkout": {
        "en": "Opening checkout…", "id": "Membuka checkout...", "nl": "Checkout openen...", 
        "sv": "Öppnar kassan...", "no": "Åpner kassen..."
    },
    "billing.status.loading_credit_packs": {
        "en": "Loading credit packs…", "id": "Memuat paket kredit...", "nl": "Creditpakketten laden...", 
        "sv": "Laddar kreditpaket...", "no": "Laster kredittpakker..."
    },
    
    # Search
    "search.status.loading": {
        "en": "Running keyword analysis…", "id": "Menjalankan analisis kata kunci...", 
        "nl": "Zoekwoordanalyse uitvoeren...", "sv": "Kör nyckelordsanalys...", 
        "no": "Kjører nøkkelordsanalyse..."
    },
    
    # CTA & Hero
    "cta.upgrade_title": {
        "en": "Unlock Full Power", "id": "Buka Kekuatan Penuh", "nl": "Ontgrendel volledige kracht", 
        "sv": "Lås upp full kraft", "no": "Lås opp full kraft"
    },
    "cta.upgrade_description": {
        "en": "Get unlimited searches and AI insights", "id": "Dapatkan pencarian tanpa batas dan wawasan AI", 
        "nl": "Krijg onbeperkte zoekopdrachten en AI-inzichten", "sv": "Få obegränsade sökningar och AI-insikter", 
        "no": "Få ubegrensede søk og AI-innsikt"
    },
    "cta.upgrade_button": {
        "en": "Upgrade Now", "id": "Tingkatkan Sekarang", "nl": "Nu upgraden", 
        "sv": "Uppgradera nu", "no": "Oppgrader nå"
    },
    "hero.title": {
        "en": "Multi-Market Keyword Intelligence", "id": "Intelijen Kata Kunci Multi-Pasar", 
        "nl": "Multi-markt zoekwoordintelligentie", "sv": "Nyckelordsintelligens för flera marknader", 
        "no": "Nøkkelordsintelligens for flere markeder"
    },
    "hero.subtitle": {
        "en": "Research keywords across 100+ countries and platforms. Get real-time search data from Google, YouTube, Amazon, and more.", 
        "id": "Teliti kata kunci di 100+ negara dan platform. Dapatkan data pencarian real-time dari Google, YouTube, Amazon, dan lainnya.", 
        "nl": "Onderzoek zoekwoorden in 100+ landen en platforms. Krijg real-time zoekgegevens van Google, YouTube, Amazon en meer.", 
        "sv": "Undersök nyckelord i 100+ länder och plattformar. Få söksdata i realtid från Google, YouTube, Amazon och mer.", 
        "no": "Undersøk nøkkelord på tvers av 100+ land og plattformer. Få sanntids søkedata fra Google, YouTube, Amazon og mer."
    },
    "hero.cta_primary": {
        "en": "Start exploring keywords", "id": "Mulai jelajahi kata kunci", "nl": "Begin met zoekwoorden verkennen", 
        "sv": "Börja utforska nyckelord", "no": "Begynn å utforske nøkkelord"
    },
    "hero.cta_secondary": {
        "en": "See pricing & plans", "id": "Lihat harga & paket", "nl": "Bekijk prijzen & abonnementen", 
        "sv": "Se priser & abonnemang", "no": "Se priser og planer"
    },
    "hero.trust_markets": {
        "en": "{{count}}+ markets", "id": "{{count}}+ pasar", "nl": "{{count}}+ markten", 
        "sv": "{{count}}+ marknader", "no": "{{count}}+ markeder"
    },
    "hero.trust_refresh": {
        "en": "Real-time data", "id": "Data real-time", "nl": "Real-time gegevens", 
        "sv": "Realtidsdata", "no": "Sanntidsdata"
    },
    "hero.trust_teams": {
        "en": "Teams shipping weekly", "id": "Tim mengirim mingguan", "nl": "Teams leveren wekelijks", 
        "sv": "Team levererar varje vecka", "no": "Team leverer ukentlig"
    },
    
    # Features
    "features.semantic.title": {
        "en": "Semantic Clustering", "id": "Pengelompokan Semantik", "nl": "Semantische clustering", 
        "sv": "Semantisk klustring", "no": "Semantisk gruppering"
    },
    "features.semantic.description": {
        "en": "AI-powered keyword grouping that understands search intent and user behavior patterns", 
        "id": "Pengelompokan kata kunci bertenaga AI yang memahami maksud pencarian dan pola perilaku pengguna", 
        "nl": "AI-aangedreven zoekwoordgroepering die zoekintentie en gebruikersgedragspatronen begrijpt", 
        "sv": "AI-driven nyckelordgruppering som förstår sökintention och användarbeteendemönster", 
        "no": "AI-drevet nøkkelordgruppering som forstår søkehensikt og bruksmønstre"
    },
    "features.localization.title": {
        "en": "Global Localization", "id": "Lokalisasi Global", "nl": "Wereldwijde lokalisatie", 
        "sv": "Global lokalisering", "no": "Global lokalisering"
    },
    "features.localization.description": {
        "en": "Research keywords in 100+ countries with native language support and regional insights", 
        "id": "Teliti kata kunci di 100+ negara dengan dukungan bahasa asli dan wawasan regional", 
        "nl": "Onderzoek zoekwoorden in 100+ landen met moedertaalondersteuning en regionale inzichten", 
        "sv": "Undersök nyckelord i 100+ länder med modersmålsstöd och regionala insikter", 
        "no": "Undersøk nøkkelord i 100+ land med morsmålsstøtte og regionale innsikter"
    },
    "features.ai_briefs.title": {
        "en": "AI Content Briefs", "id": "Ringkasan Konten AI", "nl": "AI-contentbriefs", 
        "sv": "AI-innehållsbriefingar", "no": "AI-innholdsbriefinger"
    },
    "features.ai_briefs.description": {
        "en": "Get data-driven content recommendations based on live SERP analysis and competitor research", 
        "id": "Dapatkan rekomendasi konten berbasis data berdasarkan analisis SERP langsung dan riset pesaing", 
        "nl": "Krijg datagestuurde contentaanbevelingen op basis van live SERP-analyse en concurrentieonderzoek", 
        "sv": "Få datadrivna innehållsrekommendationer baserade på live SERP-analys och konkurrentforskning", 
        "no": "Få datadrevne innholdsanbefalinger basert på live SERP-analyse og konkurrentforskning"
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
        added = 0
        
        for key, translations in TRANSLATIONS_BATCH_3.items():
            if lang_code in translations:
                if key not in strings:
                    added += 1
                else:
                    updated += 1
                strings[key] = translations[lang_code]
        
        if updated > 0 or added > 0:
            data['strings'] = dict(sorted(strings.items()))
            with open(locale_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write('\n')
            
            if added > 0:
                print(f"✅ {lang_code}: Added {added} keys, updated {updated} keys")
            else:
                print(f"✅ {lang_code}: Updated {updated} keys")

# Apply to batch 3 languages
batch_3_langs = ['en', 'id', 'nl', 'sv', 'no']
print(f"🌍 Translating Batch 3: {', '.join(batch_3_langs)}")
print(f"📝 NOTE: Adding missing entitlements keys to English (en)\n")
apply_translations(batch_3_langs)
print(f"\n🎉 Batch 3 complete! Translated keys for: {', '.join(batch_3_langs)}")
print(f"✨ English (en) now has all base reference translations!")
