#!/usr/bin/env python3
"""
Automated Translation System - Translates ALL remaining languages
Processes in batches of 5 languages at a time
"""
import json
from pathlib import Path
import time

LANGS_DIR = Path("languages")

# All translation keys with base English text
TRANSLATION_KEYS = {
    # Actions
    "actions.close": "Close",
    "actions.copy": "Copy Keyword",
    "actions.copied": "Copied to clipboard!",
    "actions.export": "Export CSV",
    
    # Entitlements
    "entitlements.sidebar.plan_label": "Your plan",
    "entitlements.tier.free": "Free",
    "entitlements.tier.pro": "Pro",
    "entitlements.tier.enterprise": "Enterprise",
    "entitlements.sidebar.ai_credits": "AI Credits",
    "entitlements.actions.upgrade": "Upgrade plan",
    "entitlements.actions.buy_credits": "Buy AI credits",
    "entitlements.actions.upgrade_now": "Upgrade now",
    "entitlements.sidebar.ai_unlocked": "AI workspace unlocked",
    "entitlements.sidebar.ai_locked": "Unlock AI workspace with credits",
    "entitlements.status.loading": "Loading plan...",
    "entitlements.status.error": "Could not load plan",
    "entitlements.locked.module": "Upgrade your plan to access this module.",
    "entitlements.sidebar.expires": "Renews on {{formatted}}",
    
    # Billing
    "billing.error.checkout_failed": "Unable to open checkout. Please try again.",
    "billing.error.signin_required": "Please sign in to upgrade.",
    "billing.error.upgrade_unavailable": "Upgrade is currently unavailable. Please contact support.",
    "billing.error.buy_credits_signin": "Sign in to buy AI credits.",
    "billing.error.buy_credits_unavailable": "AI credit purchase is unavailable right now. Please contact support.",
    "billing.status.launching_checkout": "Opening checkout…",
    "billing.status.loading_credit_packs": "Loading credit packs…",
    
    # Search
    "search.status.loading": "Running keyword analysis…",
    
    # CTA & Hero
    "cta.upgrade_title": "Unlock Full Power",
    "cta.upgrade_description": "Get unlimited searches and AI insights",
    "cta.upgrade_button": "Upgrade Now",
    "hero.title": "Multi-Market Keyword Intelligence",
    "hero.subtitle": "Research keywords across 100+ countries and platforms. Get real-time search data from Google, YouTube, Amazon, and more.",
    "hero.cta_primary": "Start exploring keywords",
    "hero.cta_secondary": "See pricing & plans",
    "hero.trust_markets": "{{count}}+ markets",
    "hero.trust_refresh": "Real-time data",
    "hero.trust_teams": "Teams shipping weekly",
    
    # Features
    "features.semantic.title": "Semantic Clustering",
    "features.semantic.description": "AI-powered keyword grouping that understands search intent and user behavior patterns",
    "features.localization.title": "Global Localization",
    "features.localization.description": "Research keywords in 100+ countries with native language support and regional insights",
    "features.ai_briefs.title": "AI Content Briefs",
    "features.ai_briefs.description": "Get data-driven content recommendations based on live SERP analysis and competitor research",
}

# Professional translations for all languages (pre-translated)
ALL_TRANSLATIONS = {
    # Danish (da)
    "da": {
        "actions.close": "Luk",
        "actions.copy": "Kopiér nøgleord",
        "actions.copied": "Kopieret til udklipsholder!",
        "actions.export": "Eksportér CSV",
        "entitlements.sidebar.plan_label": "Din plan",
        "entitlements.tier.free": "Gratis",
        "entitlements.tier.pro": "Pro",
        "entitlements.tier.enterprise": "Enterprise",
        "entitlements.sidebar.ai_credits": "AI-kreditter",
        "entitlements.actions.upgrade": "Opgrader plan",
        "entitlements.actions.buy_credits": "Køb AI-kreditter",
        "entitlements.actions.upgrade_now": "Opgrader nu",
        "entitlements.sidebar.ai_unlocked": "AI-arbejdsområde låst op",
        "entitlements.sidebar.ai_locked": "Lås AI-arbejdsområde op med kreditter",
        "entitlements.status.loading": "Indlæser plan...",
        "entitlements.status.error": "Kunne ikke indlæse plan",
        "entitlements.locked.module": "Opgrader din plan for at få adgang til dette modul.",
        "entitlements.sidebar.expires": "Fornyes {{formatted}}",
        "billing.error.checkout_failed": "Kan ikke åbne kassen. Prøv igen.",
        "billing.error.signin_required": "Log venligst ind for at opgradere.",
        "billing.error.upgrade_unavailable": "Opgradering er i øjeblikket ikke tilgængelig. Kontakt venligst support.",
        "billing.error.buy_credits_signin": "Log ind for at købe AI-kreditter.",
        "billing.error.buy_credits_unavailable": "AI-kreditkøb er ikke tilgængeligt lige nu. Kontakt venligst support.",
        "billing.status.launching_checkout": "Åbner kassen...",
        "billing.status.loading_credit_packs": "Indlæser kreditpakker...",
        "search.status.loading": "Kører nøgleordsanalyse...",
        "cta.upgrade_title": "Lås fuld kraft op",
        "cta.upgrade_description": "Få ubegrænsede søgninger og AI-indsigter",
        "cta.upgrade_button": "Opgrader nu",
        "hero.title": "Multi-marked nøgleordsintelligens",
        "hero.subtitle": "Undersøg nøgleord på tværs af 100+ lande og platforme. Få realtidssøgedata fra Google, YouTube, Amazon og mere.",
        "hero.cta_primary": "Begynd at udforske nøgleord",
        "hero.cta_secondary": "Se priser og planer",
        "hero.trust_markets": "{{count}}+ markeder",
        "hero.trust_refresh": "Realtidsdata",
        "hero.trust_teams": "Teams leverer ugentligt",
        "features.semantic.title": "Semantisk gruppering",
        "features.semantic.description": "AI-drevet nøgleordgruppering der forstår søgeintention og brugeradfærdsmønstre",
        "features.localization.title": "Global lokalisering",
        "features.localization.description": "Undersøg nøgleord i 100+ lande med modersmålsstøtte og regionale indsigter",
        "features.ai_briefs.title": "AI-indholdsbriefinger",
        "features.ai_briefs.description": "Få datadrevne indholdsanbefalinger baseret på live SERP-analyse og konkurrentforskning",
    },
    
    # Finnish (fi)
    "fi": {
        "actions.close": "Sulje",
        "actions.copy": "Kopioi avainsana",
        "actions.copied": "Kopioitu leikepöydälle!",
        "actions.export": "Vie CSV",
        "entitlements.sidebar.plan_label": "Pakettisi",
        "entitlements.tier.free": "Ilmainen",
        "entitlements.tier.pro": "Pro",
        "entitlements.tier.enterprise": "Yritys",
        "entitlements.sidebar.ai_credits": "AI-krediitit",
        "entitlements.actions.upgrade": "Päivitä paketti",
        "entitlements.actions.buy_credits": "Osta AI-krediittejä",
        "entitlements.actions.upgrade_now": "Päivitä nyt",
        "entitlements.sidebar.ai_unlocked": "AI-työtila avattu",
        "entitlements.sidebar.ai_locked": "Avaa AI-työtila krediiteillä",
        "entitlements.status.loading": "Ladataan pakettia...",
        "entitlements.status.error": "Paketin lataus epäonnistui",
        "entitlements.locked.module": "Päivitä pakettisi käyttääksesi tätä moduulia.",
        "entitlements.sidebar.expires": "Uusiutuu {{formatted}}",
        "billing.error.checkout_failed": "Kassaa ei voitu avata. Yritä uudelleen.",
        "billing.error.signin_required": "Kirjaudu sisään päivittääksesi.",
        "billing.error.upgrade_unavailable": "Päivitys ei ole tällä hetkellä saatavilla. Ota yhteyttä tukeen.",
        "billing.error.buy_credits_signin": "Kirjaudu sisään ostaaksesi AI-krediittejä.",
        "billing.error.buy_credits_unavailable": "AI-krediittien osto ei ole saatavilla juuri nyt. Ota yhteyttä tukeen.",
        "billing.status.launching_checkout": "Avataan kassaa...",
        "billing.status.loading_credit_packs": "Ladataan krediittipaketteja...",
        "search.status.loading": "Suoritetaan avainsana-analyysiä...",
        "cta.upgrade_title": "Avaa täysi teho",
        "cta.upgrade_description": "Hanki rajoittamattomat haut ja AI-oivallukset",
        "cta.upgrade_button": "Päivitä nyt",
        "hero.title": "Monimarkkinainen avainsanaintelligens",
        "hero.subtitle": "Tutki avainsanoja yli 100 maassa ja alustalla. Saa reaaliaikaista hakudataa Googlesta, YouTubesta, Amazonista ja muista.",
        "hero.cta_primary": "Aloita avainsanojen tutkiminen",
        "hero.cta_secondary": "Katso hinnat ja paketit",
        "hero.trust_markets": "{{count}}+ markkinaa",
        "hero.trust_refresh": "Reaaliaikainen data",
        "hero.trust_teams": "Tiimit toimittavat viikoittain",
        "features.semantic.title": "Semanttinen ryhmittely",
        "features.semantic.description": "AI-vetoinen avainsanaryhmittely, joka ymmärtää hakutarkoituksen ja käyttäjien käyttäytymismallit",
        "features.localization.title": "Globaali lokalisointi",
        "features.localization.description": "Tutki avainsanoja yli 100 maassa äidinkielituella ja alueellisilla oivalluksilla",
        "features.ai_briefs.title": "AI-sisältöbriiffit",
        "features.ai_briefs.description": "Saa datalähtöisiä sisältösuosituksia live SERP-analyysin ja kilpailija-analyysin perusteella",
    },
    
    # Greek (el)
    "el": {
        "actions.close": "Κλείσιμο",
        "actions.copy": "Αντιγραφή λέξης-κλειδιού",
        "actions.copied": "Αντιγράφηκε στο πρόχειρο!",
        "actions.export": "Εξαγωγή CSV",
        "entitlements.sidebar.plan_label": "Το πλάνο σας",
        "entitlements.tier.free": "Δωρεάν",
        "entitlements.tier.pro": "Pro",
        "entitlements.tier.enterprise": "Επιχείρηση",
        "entitlements.sidebar.ai_credits": "Πιστώσεις AI",
        "entitlements.actions.upgrade": "Αναβάθμιση πλάνου",
        "entitlements.actions.buy_credits": "Αγορά πιστώσεων AI",
        "entitlements.actions.upgrade_now": "Αναβάθμιση τώρα",
        "entitlements.sidebar.ai_unlocked": "Ο χώρος εργασίας AI ξεκλειδώθηκε",
        "entitlements.sidebar.ai_locked": "Ξεκλειδώστε τον χώρο εργασίας AI με πιστώσεις",
        "entitlements.status.loading": "Φόρτωση πλάνου...",
        "entitlements.status.error": "Αδυναμία φόρτωσης πλάνου",
        "entitlements.locked.module": "Αναβαθμίστε το πλάνο σας για πρόσβαση σε αυτή τη λειτουργία.",
        "entitlements.sidebar.expires": "Ανανεώνεται στις {{formatted}}",
        "billing.error.checkout_failed": "Αδυναμία ανοίγματος ταμείου. Δοκιμάστε ξανά.",
        "billing.error.signin_required": "Παρακαλώ συνδεθείτε για αναβάθμιση.",
        "billing.error.upgrade_unavailable": "Η αναβάθμιση δεν είναι διαθέσιμη αυτή τη στιγμή. Επικοινωνήστε με την υποστήριξη.",
        "billing.error.buy_credits_signin": "Συνδεθείτε για να αγοράσετε πιστώσεις AI.",
        "billing.error.buy_credits_unavailable": "Η αγορά πιστώσεων AI δεν είναι διαθέσιμη αυτή τη στιγμή. Επικοινωνήστε με την υποστήριξη.",
        "billing.status.launching_checkout": "Άνοιγμα ταμείου...",
        "billing.status.loading_credit_packs": "Φόρτωση πακέτων πιστώσεων...",
        "search.status.loading": "Εκτέλεση ανάλυσης λέξεων-κλειδιών...",
        "cta.upgrade_title": "Ξεκλειδώστε πλήρη δύναμη",
        "cta.upgrade_description": "Αποκτήστε απεριόριστες αναζητήσεις και πληροφορίες AI",
        "cta.upgrade_button": "Αναβάθμιση τώρα",
        "hero.title": "Πολυ-αγοραία νοημοσύνη λέξεων-κλειδιών",
        "hero.subtitle": "Ερευνήστε λέξεις-κλειδιά σε 100+ χώρες και πλατφόρμες. Λάβετε δεδομένα αναζήτησης σε πραγματικό χρόνο από Google, YouTube, Amazon και άλλα.",
        "hero.cta_primary": "Ξεκινήστε την εξερεύνηση λέξεων-κλειδιών",
        "hero.cta_secondary": "Δείτε τιμές και πλάνα",
        "hero.trust_markets": "{{count}}+ αγορές",
        "hero.trust_refresh": "Δεδομένα σε πραγματικό χρόνο",
        "hero.trust_teams": "Ομάδες που παραδίδουν εβδομαδιαία",
        "features.semantic.title": "Σημασιολογική ομαδοποίηση",
        "features.semantic.description": "Ομαδοποίηση λέξεων-κλειδιών με AI που κατανοεί την πρόθεση αναζήτησης και τα μοτίβα συμπεριφοράς χρηστών",
        "features.localization.title": "Παγκόσμια τοπικοποίηση",
        "features.localization.description": "Ερευνήστε λέξεις-κλειδιά σε 100+ χώρες με υποστήριξη μητρικής γλώσσας και περιφερειακές πληροφορίες",
        "features.ai_briefs.title": "Σύνοψη περιεχομένου AI",
        "features.ai_briefs.description": "Λάβετε συστάσεις περιεχομένου βασισμένες σε δεδομένα με βάση ζωντανή ανάλυση SERP και έρευνα ανταγωνισμού",
    },
    
    # Czech (cs)
    "cs": {
        "actions.close": "Zavřít",
        "actions.copy": "Kopírovat klíčové slovo",
        "actions.copied": "Zkopírováno do schránky!",
        "actions.export": "Exportovat CSV",
        "entitlements.sidebar.plan_label": "Váš plán",
        "entitlements.tier.free": "Zdarma",
        "entitlements.tier.pro": "Pro",
        "entitlements.tier.enterprise": "Enterprise",
        "entitlements.sidebar.ai_credits": "AI kredity",
        "entitlements.actions.upgrade": "Upgradovat plán",
        "entitlements.actions.buy_credits": "Koupit AI kredity",
        "entitlements.actions.upgrade_now": "Upgradovat nyní",
        "entitlements.sidebar.ai_unlocked": "AI pracovní prostor odemčen",
        "entitlements.sidebar.ai_locked": "Odemknout AI pracovní prostor kredity",
        "entitlements.status.loading": "Načítání plánu...",
        "entitlements.status.error": "Nelze načíst plán",
        "entitlements.locked.module": "Upgradujte svůj plán pro přístup k tomuto modulu.",
        "entitlements.sidebar.expires": "Obnovuje se {{formatted}}",
        "billing.error.checkout_failed": "Nelze otevřít pokladnu. Zkuste to znovu.",
        "billing.error.signin_required": "Pro upgrade se prosím přihlaste.",
        "billing.error.upgrade_unavailable": "Upgrade momentálně není k dispozici. Kontaktujte podporu.",
        "billing.error.buy_credits_signin": "Přihlaste se pro nákup AI kreditů.",
        "billing.error.buy_credits_unavailable": "Nákup AI kreditů momentálně není k dispozici. Kontaktujte podporu.",
        "billing.status.launching_checkout": "Otevírání pokladny...",
        "billing.status.loading_credit_packs": "Načítání balíčků kreditů...",
        "search.status.loading": "Spouštění analýzy klíčových slov...",
        "cta.upgrade_title": "Odemkněte plnou sílu",
        "cta.upgrade_description": "Získejte neomezené vyhledávání a AI insights",
        "cta.upgrade_button": "Upgradovat nyní",
        "hero.title": "Multimarketingová inteligence klíčových slov",
        "hero.subtitle": "Zkoumejte klíčová slova ve více než 100 zemích a platformách. Získejte data vyhledávání v reálném čase z Google, YouTube, Amazon a dalších.",
        "hero.cta_primary": "Začít prozkoumávat klíčová slova",
        "hero.cta_secondary": "Zobrazit ceny a plány",
        "hero.trust_markets": "{{count}}+ trhů",
        "hero.trust_refresh": "Data v reálném čase",
        "hero.trust_teams": "Týmy dodávají týdně",
        "features.semantic.title": "Sémantické shlukování",
        "features.semantic.description": "AI-poháněné seskupování klíčových slov, které rozumí záměru vyhledávání a vzorcům chování uživatelů",
        "features.localization.title": "Globální lokalizace",
        "features.localization.description": "Zkoumejte klíčová slova ve více než 100 zemích s podporou rodného jazyka a regionálními poznatky",
        "features.ai_briefs.title": "AI obsahové briefy",
        "features.ai_briefs.description": "Získejte doporučení obsahu založená na datech na základě živé SERP analýzy a výzkumu konkurence",
    },
    
    # Romanian (ro)
    "ro": {
        "actions.close": "Închide",
        "actions.copy": "Copiază cuvântul cheie",
        "actions.copied": "Copiat în clipboard!",
        "actions.export": "Exportă CSV",
        "entitlements.sidebar.plan_label": "Planul tău",
        "entitlements.tier.free": "Gratuit",
        "entitlements.tier.pro": "Pro",
        "entitlements.tier.enterprise": "Enterprise",
        "entitlements.sidebar.ai_credits": "Credite AI",
        "entitlements.actions.upgrade": "Actualizează planul",
        "entitlements.actions.buy_credits": "Cumpără credite AI",
        "entitlements.actions.upgrade_now": "Actualizează acum",
        "entitlements.sidebar.ai_unlocked": "Spațiu de lucru AI deblocat",
        "entitlements.sidebar.ai_locked": "Deblochează spațiul de lucru AI cu credite",
        "entitlements.status.loading": "Se încarcă planul...",
        "entitlements.status.error": "Nu s-a putut încărca planul",
        "entitlements.locked.module": "Actualizează-ți planul pentru a accesa acest modul.",
        "entitlements.sidebar.expires": "Se reînnoiește pe {{formatted}}",
        "billing.error.checkout_failed": "Nu s-a putut deschide casa de marcat. Încercați din nou.",
        "billing.error.signin_required": "Vă rugăm să vă autentificați pentru a actualiza.",
        "billing.error.upgrade_unavailable": "Actualizarea nu este disponibilă momentan. Contactați asistența.",
        "billing.error.buy_credits_signin": "Autentifică-te pentru a cumpăra credite AI.",
        "billing.error.buy_credits_unavailable": "Achiziția de credite AI nu este disponibilă acum. Contactați asistența.",
        "billing.status.launching_checkout": "Se deschide casa de marcat...",
        "billing.status.loading_credit_packs": "Se încarcă pachetele de credite...",
        "search.status.loading": "Se rulează analiza cuvintelor cheie...",
        "cta.upgrade_title": "Deblochează puterea completă",
        "cta.upgrade_description": "Obține căutări nelimitate și informații AI",
        "cta.upgrade_button": "Actualizează acum",
        "hero.title": "Inteligență cuvinte cheie multi-piață",
        "hero.subtitle": "Cercetează cuvinte cheie în peste 100 de țări și platforme. Obține date de căutare în timp real de la Google, YouTube, Amazon și altele.",
        "hero.cta_primary": "Începe să explorezi cuvinte cheie",
        "hero.cta_secondary": "Vezi prețuri și planuri",
        "hero.trust_markets": "{{count}}+ piețe",
        "hero.trust_refresh": "Date în timp real",
        "hero.trust_teams": "Echipe care livrează săptămânal",
        "features.semantic.title": "Grupare semantică",
        "features.semantic.description": "Grupare cuvinte cheie alimentată de AI care înțelege intenția de căutare și pattern-urile de comportament ale utilizatorilor",
        "features.localization.title": "Localizare globală",
        "features.localization.description": "Cercetează cuvinte cheie în peste 100 de țări cu suport pentru limba nativă și informații regionale",
        "features.ai_briefs.title": "Briefuri de conținut AI",
        "features.ai_briefs.description": "Obține recomandări de conținut bazate pe date pe baza analizei SERP live și cercetării concurenței",
    },
}

# Get all completed languages
completed_languages = {'en', 'ar', 'de', 'es', 'fr', 'it', 'ja', 'ko', 'pt', 'ru', 'zh', 
                       'hi', 'tr', 'pl', 'vi', 'th', 'id', 'nl', 'sv', 'no'}

# Get all available languages
all_lang_dirs = [d.name for d in LANGS_DIR.iterdir() if d.is_dir() and len(d.name) == 2]
remaining_languages = [lang for lang in all_lang_dirs if lang not in completed_languages]

print(f"🌍 Auto-Translation System Starting...")
print(f"📊 Total languages: {len(all_lang_dirs)}")
print(f"✅ Already complete: {len(completed_languages)}")
print(f"⏳ Remaining: {len(remaining_languages)}")
print(f"\n🔄 Processing in batches of 5...\n")

# Process in batches
batch_size = 5
batch_num = 4  # Starting from batch 4 (batches 1-3 already done)

for i in range(0, len(remaining_languages), batch_size):
    batch_langs = remaining_languages[i:i+batch_size]
    
    print(f"{'='*60}")
    print(f"📦 BATCH {batch_num}: {', '.join(batch_langs)}")
    print(f"{'='*60}\n")
    
    for lang_code in batch_langs:
        locale_file = LANGS_DIR / lang_code / "locale.json"
        
        if not locale_file.exists():
            print(f"⚠️  {lang_code}: locale file not found, skipping")
            continue
        
        with open(locale_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        strings = data.get('strings', {})
        added = 0
        updated = 0
        
        # Check if we have pre-translated content
        if lang_code in ALL_TRANSLATIONS:
            translations = ALL_TRANSLATIONS[lang_code]
            for key, value in translations.items():
                if key not in strings:
                    added += 1
                else:
                    updated += 1
                strings[key] = value
        else:
            # Use English as fallback with [NEEDS TRANSLATION] marker
            for key, en_value in TRANSLATION_KEYS.items():
                if key not in strings:
                    strings[key] = f"[NEEDS TRANSLATION: {en_value}]"
                    added += 1
        
        # Save updated file
        if added > 0 or updated > 0:
            data['strings'] = dict(sorted(strings.items()))
            with open(locale_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write('\n')
            
            status = "✅" if lang_code in ALL_TRANSLATIONS else "⚠️ "
            if added > 0 and updated > 0:
                print(f"{status} {lang_code}: Added {added} keys, updated {updated} keys")
            elif added > 0:
                print(f"{status} {lang_code}: Added {added} keys")
            else:
                print(f"{status} {lang_code}: Updated {updated} keys")
    
    print(f"\n✨ Batch {batch_num} complete!\n")
    batch_num += 1
    time.sleep(0.5)  # Small delay between batches

print(f"\n{'='*60}")
print(f"🎉 AUTO-TRANSLATION COMPLETE!")
print(f"{'='*60}")
print(f"✅ All {len(all_lang_dirs)} languages processed")
print(f"📝 {len([l for l in remaining_languages if l in ALL_TRANSLATIONS])} languages with proper translations")
print(f"⚠️  {len([l for l in remaining_languages if l not in ALL_TRANSLATIONS])} languages with fallback markers")
print(f"\n💡 Languages with [NEEDS TRANSLATION] markers need professional translation")
