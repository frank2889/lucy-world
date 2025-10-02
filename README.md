# 🆓 FREE Semantic Keyword Research Tool

Een **100% GRATIS** Python tool voor het vinden van semantische zoekwoorden met **echte data** van Google Trends, Google Autocomplete en Wikipedia. Perfect voor SEO specialisten, content creators en digitale marketeers die geen geld willen uitgeven aan dure keyword tools!

## 💰 Waarom Gratis?

- ✅ **Geen API kosten** - Gebruikt alleen gratis data bronnen
- ✅ **Echte Google data** - Google Trends & Autocomplete zijn officieel gratis
- ✅ **Unlimited gebruik** - Geen dagelijkse limieten
- ✅ **Open source** - Volledig transparant en aanpasbaar

## ✨ Functies

### 🆓 **FREE Tool (`free_keyword_tool.py`)** ⭐ AANBEVOLEN

- **🔍 Google Autocomplete Data**: Echte suggesties die mensen typen
- **📈 Google Trends Analysis**: Werkelijke populariteit en trends over 12 maanden
- **📚 Wikipedia Gerelateerde Termen**: Semantische context uit Wikipedia
- **❓ Slimme Vraag Generatie**: Nederlandse vraagpatronen
- **📊 Volume Schatting**: Gebaseerd op echte trends data
- **🎯 Opportuniteiten Analyse**: Vindt de beste gratis keyword kansen
- **💾 CSV Export**: Gratis export naar spreadsheets
- **🌐 Web Interface**: Mooie browser interface

### 🎯 Basis Tool (`semantic_keyword_tool.py`)

- **Semantische zoekwoorden**: Vindt gerelateerde keywords bij je hoofdzoekwoord
- **Gerelateerde vragen**: Genereert "People Also Ask" type vragen  
- **Zoekvolume data**: Toont geschat zoekvolume voor elk keyword
- **CPC en Difficulty**: Analyseert kosten per klik en SEO moeilijkheidsgraad
- **CSV Export**: Exporteer resultaten naar spreadsheet

### 🚀 Geavanceerde Tool (`advanced_keyword_tool.py`)

- **Uitgebreide keyword categorieën**: 
  - People Also Ask vragen
  - Gerelateerde zoekopdrachten  
  - Semantische varianten
  - Long-tail keywords
- **Opportuniteiten analyse**: Identificeert de beste keyword kansen
- **Commerciële intent detectie**: Vindt keywords met koopintentie
- **Lokale SEO**: Ondersteunt locatie-gebaseerde zoekwoorden
- **Trend analyse**: Toont keyword trends (stijgend/dalend/stabiel)

## 🚀 Installatie

1. **Clone de repository**:
```bash
cd /Users/Frank/Documents/we-code/Topicals
```

2. **Installeer dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configureer API keys** (optioneel):
```bash
cp .env.example .env
# Bewerk .env en voeg je API keys toe
```

## 💻 Gebruik

### Basis Tool
```bash
python semantic_keyword_tool.py
```

### Geavanceerde Tool (Aanbevolen)
```bash
python advanced_keyword_tool.py
```

## 📖 Voorbeeld

**Input**: `taart bestellen`

**Output**:
```
🔍 PEOPLE ALSO ASK:
1. waar kan ik taart bestellen (Volume: 2,340 | Difficulty: 45/100)
2. hoeveel kost taart bestellen (Volume: 1,890 | Difficulty: 38/100)
3. beste taart bestellen online (Volume: 1,560 | Difficulty: 52/100)

🔗 SEMANTISCHE ZOEKWOORDEN:
1. taart bezorgen (Volume: 3,200 | Difficulty: 41/100)
2. verjaardagstaart bestellen (Volume: 2,800 | Difficulty: 43/100)
3. bruidstaart op maat (Volume: 1,200 | Difficulty: 35/100)

🎯 KEYWORD OPPORTUNITEITEN:
🏆 LOW COMPETITION:
1. taart bestellen Utrecht (Volume: 890, Difficulty: 28)
2. goedkope taart bestellen (Volume: 1,340, Difficulty: 32)
```

## 🔧 API Integratie

De tool ondersteunt verschillende API providers voor echte data:

### Ondersteunde APIs:
- **SerpAPI**: Voor Google "People Also Ask" en gerelateerde zoekopdrachten
- **SEMrush**: Voor zoekvolume en competitie data
- **Ahrefs**: Voor backlink en keyword difficulty data
- **Google Ads**: Voor advertentie data en CPC

### API Setup:
1. Krijg API keys van je gewenste provider(s)
2. Voeg ze toe aan je `.env` bestand:
```env
SERP_API_KEY=your_key_here
SEMRUSH_API_KEY=your_key_here
```

## 📊 Output Formaten

### Console Output
- Kleurgecodeerde resultaten
- Emoji indicators voor volume en difficulty
- Georganiseerd per categorie

### CSV Export
- Alle keywords met metadata
- Importeerbaar in Excel/Google Sheets
- Filters voor verdere analyse

## 🎯 Use Cases

### 🏢 Voor Bedrijven
- **SEO Strategy**: Vind nieuwe keyword opportuniteiten
- **Content Planning**: Identificeer onderwerpen voor blog posts
- **PPC Campaigns**: Ontdek long-tail keywords met lage CPC

### 📝 Voor Content Creators
- **Blog Topics**: Vind populaire vragen in je niche
- **Video Ideas**: Ontdek wat je doelgroep zoekt
- **FAQ Secties**: Genereer veelgestelde vragen

### 🎨 Voor E-commerce
- **Product Descriptions**: Vind relevante product keywords
- **Category Pages**: Optimaliseer categorie pagina's
- **Local SEO**: Vind lokale zoekvariant

## 🔮 Geplande Features

- [ ] **Real-time API integratie** voor live data
- [ ] **Keyword clustering** voor thematische groepering
- [ ] **Competitor analysis** voor benchmarking
- [ ] **Search intent classification** (informational/commercial/navigational)
- [ ] **Seasonal trend analysis** voor tijdgebonden keywords
- [ ] **Multi-language support** voor internationale SEO
- [ ] **Web interface** voor gebruiksvriendelijkheid

## 🛠️ Technische Details

### Dependencies
- `requests`: HTTP requests voor API calls
- `python-dotenv`: Omgevingsvariabelen beheer
- `beautifulsoup4`: HTML parsing (toekomstig gebruik)
- `pandas`: Data manipulatie en analyse
- `matplotlib/seaborn`: Data visualisatie

### Architectuur
```
semantic_keyword_tool.py     # Basis implementatie
advanced_keyword_tool.py     # Geavanceerde features
├── RealAPIIntegration      # API connecties
├── AdvancedKeywordTool     # Hoofdlogica
└── KeywordData            # Data model
```

## 📈 Performance

- **Mock mode**: ~50 keywords per seconde
- **API mode**: Afhankelijk van rate limits (typisch 1-10 requests/sec)
- **Memory usage**: ~10-50MB afhankelijk van dataset grootte

## 🤝 Contributing

Contributions zijn welkom! Zie onze [contributing guidelines](CONTRIBUTING.md) voor meer info.

## 📄 License

MIT License - zie [LICENSE](LICENSE) bestand voor details.

## 🆘 Support

Vragen of problemen? Open een [issue](../../issues) of stuur een email.

---

**Made with ❤️ for the SEO community**
 
---

## Frontend (React) — Development & Build

This project includes an optional React single-page app (Vite + React + TypeScript) located in `frontend/`.

Development:

1. Start the Flask backend (port 5000)
2. In another terminal, start the React dev server:

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies API calls (`/api/*`, `/search`, `/health`) to `http://localhost:5000`.

Build for production:

```bash
cd frontend
npm install
npm run build
```

The build outputs to `static/app`. In production, Flask will automatically serve `/` from `static/app/index.html` if it exists. Otherwise, it falls back to `templates/lucy_index.html`.

