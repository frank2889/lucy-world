# Translation Rules & Standards
**Project:** Lucy World  
**Date:** October 9, 2025  
**Status:** ENFORCED

## Core Rules

### ❌ FORBIDDEN
1. **NO English text in non-English locale files**
   - Exception: Universal tech terms (AI, CSV, Pro, Enterprise) when no native equivalent exists
   - Must use native script/alphabet for the target language

2. **NO fallback markers**
   - No `[NEEDS TRANSLATION: ...]`
   - No `[MISSING: ...]`
   - No placeholder text

3. **NO mixed languages**
   - Each locale file must be 100% in its target language
   - Use native terminology

### ✅ REQUIRED

1. **Native Language Translation**
   - All UI strings must be translated to the target language
   - Use proper grammar and natural phrasing
   - Respect cultural context

2. **Script Compliance**
   - RTL languages (ar, he, fa, ur) must use RTL script properly
   - Cyrillic languages must use Cyrillic alphabet
   - Asian languages must use their native scripts

3. **Professional Quality**
   - Natural, fluent translations
   - Culturally appropriate
   - Technically accurate

## Translation Strategy by Language Type

### Category 1: Professional Native Translations
**Languages:** ar, de, es, fr, it, ja, ko, pt, ru, zh, hi, tr, pl, vi, th, en, id, nl, sv, no, da, fi, el, cs, ro, hu, uk, he, bn, hr

**Status:** ✅ Complete with professional translations

### Category 2: High-Priority Languages (Need Native Translation)
**Languages:** fa (Persian), ur (Urdu), ta (Tamil), sw (Swahili), af (Afrikaans), ms (Malay), sr (Serbian), sq (Albanian), ka (Georgian), hy (Armenian)

**Action Required:** Professional translation service or native speaker

### Category 3: Medium-Priority Languages
**Languages:** az, be, bg, bs, ca, et, eu, ga, gl, hr, is, kk, lt, lv, mk, mt, sk, sl, tt, uz

**Action Required:** Use cognates and loanwords where appropriate, translate core terms natively

### Category 4: Lower-Volume Languages
**Languages:** am, co, cy, eo, fy, gd, gu, ha, ht, ig, jv, km, kn, ku, ky, la, lb, lo, mg, mi, ml, mn, mr, my, ne, ny, or, pa, ps, rw, sd, si, sm, sn, so, st, su, te, tg, tk, tl, ug, xh, yi, yo, zu

**Action Required:** Basic translation, acceptable to use international tech terms

## Key Translation Principles

### 1. Technical Terms
- **AI** - Usually kept as "AI" globally, or translated as:
  - Chinese: 人工智能
  - Arabic: الذكاء الاصطناعي
  - Russian: ИИ
  
- **Credits** - Translate to native word for "credits/points/tokens"

- **Upgrade** - Always use native word for "upgrade/enhance/improve"

### 2. UI Actions
- **Close** - Must be translated (关闭, Cerrar, Fermer, etc.)
- **Copy** - Must be translated (复制, Copiar, Copier, etc.)
- **Export** - Often kept similar but in native form

### 3. Plan Tiers
- **Free** - Always translate to native word for "free/gratis/libre"
- **Pro** - Can keep as "Pro" if commonly used in that market
- **Enterprise** - Translate or keep based on market norms

### 4. Status Messages
- **Loading...** - Always translate with proper grammar
- **Error** - Always translate to native error terminology

## Verification Checklist

Before marking a language as complete:

- [ ] No English strings (except universal tech terms)
- [ ] All keys present from English reference
- [ ] Proper script/alphabet used
- [ ] Natural, fluent phrasing
- [ ] Culturally appropriate
- [ ] No fallback markers
- [ ] Proper punctuation for language
- [ ] Tested in UI (if possible)

## Quality Standards

### ⭐ Gold Standard (Target)
- Professional native translation
- Culturally adapted
- Technically accurate
- Natural phrasing

### ✅ Acceptable Minimum
- Accurate translation of meaning
- Grammatically correct
- Uses native script
- No English fallbacks (except universal terms)

### ❌ Unacceptable
- English text in non-English files
- Placeholder markers
- Machine translation without review
- Mixed language content

## Maintenance

### Adding New Keys
1. Add to English (en) first as reference
2. Translate to all Category 1 languages immediately
3. Schedule translation for other categories
4. NO fallback markers - use English temporarily only if absolutely necessary, mark with TODO comment

### Updating Existing Keys
1. Update English reference
2. Update all professional translations (30 languages)
3. Create translation task for remaining languages
4. Track in translation backlog

## Current Status Summary

✅ **30 languages** - Professional native translations  
⚠️ **75 languages** - Need proper native translations (currently using English - TEMPORARY)

## Next Steps

1. **Immediate:** Translate high-priority languages (fa, ur, ta, sw, af, ms, sr, sq, ka, hy)
2. **Short-term:** Complete medium-priority languages
3. **Long-term:** Cover all 105 languages with native translations

---

**Rule:** NO ENGLISH IN NON-ENGLISH LOCALE FILES  
**Exception:** Universal tech terms only (AI, CSV, URL, etc.)  
**Enforcement:** Automated checks + manual review
