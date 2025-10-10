# DoD Implementation Plan - October 8, 2025
<!-- markdownlint-disable MD013 MD031 MD009 MD040 -->

## Status: 2/70 Complete

### 🎨 Design Governance Gate (Applies to Every Task)
- The canonical specification lives at `design/design.md`; treat it as the
  single source of truth for any visual, motion, or spectral change.
- Before marking any DoD item ✅, run
  `python3 design/compile_design.py` to regenerate
  `design/tokens.json`, `design/variables.css`, `design/theme.ts`, and
  `design/renderer.config.json`, then include the regenerated artefacts in
  the commit.
- Direct edits to generated artefacts are prohibited—update
  `design/design.md`, recompile, and verify.

### ✅ Completed
1. Search error differentiation (network/timeout/no-results)
2. Global locale detection (geo-IP + CDN headers)

### 🚧 In Progress: Phase 1 - Core UX/Frontend

#### Task 3: Clickable Result Cards with Detail Drawer
**Files to modify:**
- `frontend/src/App.tsx` - Add state for selected keyword
- `frontend/src/styles.css` - Add drawer styling

**Implementation:**
```typescript
// State addition
const [selectedKeyword, setSelectedKeyword] = useState<KeywordDetail | null>(null)

// KeywordDetail type
interface KeywordDetail {
  keyword: string
  search_volume: number
  category: string
  trend?: string
  difficulty?: number
}

// Click handler
const handleKeywordClick = (keyword: KeywordDetail) => {
  setSelectedKeyword(keyword)
  // Track analytics
  if (window.dataLayer) {
    window.dataLayer.push({
      event: 'keyword_detail_opened',
      keyword: keyword.keyword,
      category: keyword.category
    })
  }
}

// Drawer component
<div className={`keyword-drawer ${selectedKeyword ? 'open' : ''}`}>
  {selectedKeyword && (
    <>
      <button onClick={() => setSelectedKeyword(null)}>×</button>
      <h3>{selectedKeyword.keyword}</h3>
      <div className="metrics">
        <div><label>{translate('metrics.search_volume')}</label><span>{selectedKeyword.search_volume}</span></div>
        <div><label>{translate('metrics.category')}</label><span>{selectedKeyword.category}</span></div>
      </div>
      <div className="actions">
        <button onClick={() => exportKeyword(selectedKeyword)}>
          {translate('actions.export')}
        </button>
      </div>
    </>
  )}
</div>

// Keyboard navigation
useEffect(() => {
  const handleEscape = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && selectedKeyword) {
      setSelectedKeyword(null)
    }
  }
  document.addEventListener('keydown', handleEscape)
  return () => document.removeEventListener('keydown', handleEscape)
}, [selectedKeyword])
```

**CSS additions:**
```css
.keyword-drawer {
  position: fixed;
  right: -400px;
  top: 0;
  width: 400px;
  height: 100vh;
  background: var(--card-bg);
  border-left: 1px solid var(--border);
  transition: right 0.3s ease;
  z-index: 1000;
  padding: 24px;
  overflow-y: auto;
}

.keyword-drawer.open {
  right: 0;
}

.keyword-drawer .metrics {
  display: grid;
  gap: 16px;
  margin: 24px 0;
}

.keyword-drawer .metrics > div {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  background: var(--bg);
  border-radius: 8px;
}
```

**Locale keys needed:**
```json
{
  "metrics.search_volume": "Search Volume",
  "metrics.category": "Category",
  "metrics.trend": "Trend",
  "metrics.difficulty": "Difficulty",
  "actions.export": "Export",
  "actions.close": "Close"
}
```

**DoD Completion:** Result cards clickable ✅, Detail drawer ✅, Metrics ✅, Keyboard nav ✅, Export controls ✅

---

#### Task 4: CTA Ribbon in Sidebar
**Files to modify:**
- `frontend/src/App.tsx` - Add sticky CTA component in sidebar
- `frontend/src/styles.css` - Sticky positioning

**Implementation:**
```tsx
// In sidebar, after plan summary
{entitlements?.tier === 'free' && (
  <div className="sidebar-cta-ribbon">
    <div className="cta-content">
      <h4>{translate('cta.upgrade_title')}</h4>
      <p>{translate('cta.upgrade_description')}</p>
      <button 
        className="btn-primary"
        onClick={handleUpgradeClick}
      >
        {translate('entitlements.actions.upgrade')}
      </button>
    </div>
  </div>
)}
```

**CSS:**
```css
.sidebar-cta-ribbon {
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
  padding: 20px;
  margin: 0 -20px -20px -20px;
  border-radius: 0 0 12px 12px;
}
```

**Analytics:**
```javascript
// Track scroll depth
useEffect(() => {
  const handleScroll = () => {
    const scrolled = window.scrollY / (document.body.scrollHeight - window.innerHeight)
    if (scrolled > 0.5 && !ctaImpressionTracked) {
      window.dataLayer?.push({ event: 'cta_upgrade_impression' })
      setCtaImpressionTracked(true)
    }
  }
  window.addEventListener('scroll', handleScroll)
  return () => window.removeEventListener('scroll', handleScroll)
}, [ctaImpressionTracked])
```

**DoD Completion:** Sticky CTA ✅, Analytics ✅, Translations ✅

---

### 📋 Phase 2: Marketing/Hero Surface

#### Task 5: Hero Deck with CTAs
**File:** `frontend/src/components/Hero.tsx` (new)

**Structure:**
- Gradient glassmorphism background
- Primary CTA: "Start exploring keywords"
- Secondary CTA: "See pricing & plans" → upgrade_url
- Trust metrics chips
- Platform coverage badges

#### Task 6: Sample Insight Cards
**Implementation:** Show cached/static sample data for anonymous users

#### Task 7: Premium Modal Styling
**Files:** Update modal CSS with glass morphism

---

### 📋 Phase 3: Backend/API

#### Task 8: `/billing/credits` Endpoint
**File:** `backend/routes_billing.py`
- Serve localized copy
- Return Stripe purchase URLs
- Record credit grants
- No JSON 404s

#### Task 9: `/billing/upgrade` Endpoint
- Redirect to `/pricing` (localized)
- Or launch Stripe Checkout if no upgrade_url

#### Task 10: Search Dispatcher Tests
**File:** `backend/tests/test_search_dispatcher.py` (new)
- Google happy path
- Bing happy path
- DuckDuckGo happy path
- Error handling

#### Task 11: Redis Caching
**Files:** 
- `backend/extensions.py` - Add Redis client
- `backend/routes_*.py` - Cache search responses
- Target: < 600ms for identical queries

---

### 📋 Phase 4: Infrastructure/Monitoring

#### Task 12: Sentry Integration
- Correlation IDs for all errors
- Locale tagging
- Environment: staging + production

#### Task 13: Analytics Events
- CTA clicks
- Overlay impressions
- Login attempts
- Schema validation

#### Task 14: Metrics Dashboard
- Upgrades tracking
- Credit burn rate
- AI adoption metrics
- 7-day retention

---

### 📋 Phase 5: Testing & Quality

#### Task 15: Cypress Tests
- Hero presence
- Modal interactions
- Free vs signed-in flows
- CTA clicks

#### Task 16: Contract Tests
- JSON Schema for `/api/entitlements`
- Schema versioning
- CI enforcement

---

### 📋 Phase 6: Enterprise Features

#### Task 17: AI Credit Gating
- Visibility controls
- Usage tracking
- Ledger updates

#### Task 18: Enterprise RBAC
- Role-based access
- Advanced connectors
- Audit logging

---

### 📋 Phase 7: Final Polish

#### Task 19: Unsplash Country Backgrounds
**Structure:**
```
/markets/
  NL/
    backgrounds/
      hero-1.jpg  (Amsterdam canals)
      hero-2.jpg  (Windmills)
      hero-3.jpg  (Tulip fields)
  US/
    backgrounds/
      hero-1.jpg  (NYC skyline)
      hero-2.jpg  (Golden Gate)
      hero-3.jpg  (Grand Canyon)
  ... (all countries)
```

**Implementation:**
- Unsplash API or curated collection
- Local imagery per country
- Lazy loading
- Responsive srcset

#### Task 20: Professional UX/CRO Review
**After all DoD complete:**
1. Hire professional UX/CRO specialist
2. Design audit
3. Conversion optimization
4. A/B test planning

---

## Execution Strategy

**Estimated Time:**
- Phase 1: 4 hours
- Phase 2: 3 hours
- Phase 3: 4 hours
- Phase 4: 3 hours
- Phase 5: 2 hours
- Phase 6: 4 hours
- Phase 7: 2 hours
- **Total: ~22 hours of focused development**

**Next Steps:**
1. Complete remaining Phase 1 tasks (detail drawer, CTA ribbon)
2. Build Phase 2 marketing surfaces
3. Backend API completion
4. Infrastructure setup
5. Testing suite
6. Unsplash integration
7. Professional design review

---

## Progress Tracking

Update this document as tasks complete. Mark with ✅ when done.

**Last Updated:** October 8, 2025
**Status:** 2/70 complete, Phase 1 in progress
