# Lucy World Design Philosophy

## Core Principles

### Professional & Clean
- Daily-use business tool, not flashy marketing site
- Clarity over cleverness
- Consistency over novelty
- Utility over decoration
- Every element serves a purpose

### Prohibited Elements
- Gradients
- Animations (except loading states)
- Shadows (except minimal elevation)
- Trendy effects
- Marketing-style hero sections
- Decorative illustrations

### Required Elements
- Flat, clean surfaces
- Clear typography hierarchy
- Consistent spacing system
- Functional iconography
- Data-first layouts
- Instant, predictable interactions

## Visual Standards

### Color
- Dark theme required
- Teal/green accent for CTAs
- WCAG AA minimum (4.5:1 body text contrast)
- Status colors (error/success/warning) for feedback only

### Typography
- Maximum 3-4 font sizes
- Regular and medium/semibold weights only
- 1.5 line height for body text
- Left-aligned text

### Spacing
- 8px base unit grid
- Use multiples of 8px only
- Generous but not excessive white space
- Information-dense layouts

### Components
- Buttons: Solid or outlined, simple state changes only
- Cards: 1px border or minimal shadow
- Forms: Visible labels, simple borders
- Tables: Striped OR bordered, not both
- Lists: Clean and scannable

## Interaction Standards

### Loading States
- Skeleton loaders only
- Progress indicators for waits > 2 seconds
- Instant button feedback

### Navigation
- Persistent sidebar
- Breadcrumbs for deep navigation only
- Top nav: Product, Pricing, Resources, Support

### Micro-interactions
- Minimal, aids comprehension only
- < 200ms duration
- Fade or slide only, no bounce/elastic

## Accessibility Requirements

- WCAG AA minimum
- Visible focus indicators always
- Semantic HTML with ARIA labels
- No reliance on color alone
- Keyboard navigation support

## Performance Standards

- < 2s initial paint
- Mobile-first responsive
- Minimal dependencies
- Tree-shaking enabled

## Enterprise Requirements

- Reliability: No bugs, predictable behavior
- Speed: Fast load, instant interactions
- Clarity: Obvious next steps
- Consistency: Same patterns throughout
- Data density: Show more, do more
- Professional copy: Concise, benefit-oriented
- Security: Visible trust signals
- Support: Easy contact

## Prohibited Patterns

- Consumer app styling
- Marketing landing pages
- Trendy visual effects
- Over-animation
- Decorative elements
- Gamification
- Modal overuse
- Hidden navigation

## Design Review Checklist

Every UI change must verify:

- [ ] No gradients
- [ ] No animations except loading
- [ ] No shadows except minimal elevation
- [ ] WCAG AA contrast ratios
- [ ] 8px spacing grid
- [ ] Typography hierarchy maintained
- [ ] Mobile-responsive
- [ ] Keyboard accessible
- [ ] Loads < 2 seconds
- [ ] Professional appearance
