---
name: event-minder
description: Plan, audit, and execute marketing events—new brand launches, product drops, and seasonal campaigns (Black Friday, holiday sales)—using the business brand file. Audits technical launch readiness (HTML tags, SEO, favicon, GSC, GA4), drafts launch copy (LinkedIn, ProductHunt, social profiles), designs viral bundle giveaways, and tracks progress in `brands/<business-slug>/launch-plan.md`.
---

# Event Minder

Plan and run marketing events for a business: brand launches, product drops, and seasonal campaigns. You audit technical readiness from the live site, draft promotional copy in the brand voice, design viral launch incentives, and keep progress in one tracking file.

The user posts, publishes, and configures their own accounts. You audit, plan, and draft.

## Before you start

Read `brands/<business-slug>/brand.md`. If it does not exist, stop and direct the user to `skills/marketing-manager/SKILL.md` to create it first.

From the brand file, read:
- **Brand & Ideal customer**: To align launch positioning and giveaway prizes with people who will actually buy.
- **Offer**: To select product bundles for giveaways and launch offers.
- **Voice**: To draft launch posts, social bios, and ProductHunt submissions in the brand's exact tone.
- **Key dates**: To sequence pre-launch, launch day, and post-launch deadlines.

## Event types

1. **Brand & Store Launch**: First public reveal of a new store, software product, or brand. Focuses on technical setup verification, discovery foundation, and day-one traffic momentum.
2. **Product Drop / Limited Edition**: Focused release for a single product or limited run (e.g., numbered runs, seasonal designs). Focuses on urgency, VIP early access, and social teasers.
3. **Seasonal & Holiday Campaign**: Calendar-driven events (Black Friday / Cyber Monday, Spring refresh, holiday shipping cut-offs).

---

## The Launch Plan Checklist

When preparing a brand or store launch, audit technical items against the live site through a browser session, and draft deliverables for promotional channels:

### 1. Technical & Discovery Audit

Load the live site (using a browser session first) and verify each item. Mark each item as **PASS**, **FAIL**, or **UNCHECKED** with quoted evidence:

- **SEO-Friendly HTML Optimization**:
  - One unique `<title>` tag with primary keywords and brand name (under 60 characters).
  - Meta description present, under 160 characters, with a clear call to action.
  - Open Graph tags (`og:title`, `og:description`, `og:image`, `og:url`) and Twitter card tags (`twitter:card`, `twitter:image`) present and pointing to valid URLs.
  - Viewport meta tag present for mobile responsiveness.
  - Semantic heading structure: exactly one `<h1>` that states what the site offers.
- **SEO Foundations**:
  - `sitemap.xml` accessible and returns 200 (e.g., `/sitemap.xml`).
  - `robots.txt` accessible, allows search crawler indexing, and links to the sitemap.
  - Canonical URL tag (`<link rel="canonical">`) matches the preferred domain and protocol.
- **Favicon**:
  - `<link rel="icon">` or `<link rel="shortcut icon">` present in HTML `<head>`.
  - Icon loads with 200 status and renders cleanly at 16x16 and 32x32.
- **Google Search Console**:
  - Verification tag or DNS verification confirmed.
  - XML sitemap submitted for indexing.
- **Google Analytics 4**:
  - Measurement tag (`gtag.js` or Google Tag Manager) present in page source.
  - Measurement ID (`G-XXXXXXXXXX`) active and collecting data.
- **Pop-up Opt-in / Discount Offer Provider**: Choose a provider such as Justuno, OptiMonk, or Poptin for email opt-ins and launch discount offers. Record the selected provider and offer in the launch plan.

### 2. Social Profiles & Channel Presence

Ensure every public profile shares the same handle, avatar, and positioning:

- **Profile Consistency**: Check handles across Instagram, Facebook, TikTok, X, YouTube, and Pinterest. Flag mismatches.
- **Bio Copy**: Draft a 150-character bio for each platform, incorporating the value proposition and a trackable launch link (`?utm_source=...`).
- **Banner / Header Assets**: Specify required dimensions and key messaging for channel headers.

### 3. Launch Announcements & PR

Draft complete promotional copy tailored to each platform:

- **LinkedIn Launch Post**:
  - Founder narrative explaining the origin story, the problem observed, and why the brand was built.
  - Conversational, authentic tone avoiding corporate jargon.
  - 3–5 industry or topic hashtags.
  - Clear call to action inviting peers to test, comment, or share feedback.
- **ProductHunt Submission Package**:
  - **Product Name**: Official brand/product name.
  - **Tagline**: Under 60 characters, punchy, benefits-focused.
  - **Description**: 2–3 concise sentences explaining who it is for and what makes it distinct.
  - **First Maker Comment**: A warm personal note welcoming the community, explaining the build process, offering an exclusive launch promo code, and asking for specific feedback.
  - **Media Checklist**: 4–5 screenshots/GIFs demonstrating core features or hero products.

### 4. Contests and Giveaways (Recommended Default)

A launch contest or giveaway builds a day-one email list and creates social momentum before the store opens.

#### Default Recommended Mechanic: Viral Product Bundle Giveaway
- **Why a bundle**: Give away an irresistible bundle of the store's own hero products (e.g. Tee + Mug + Notebook + Sticker pack from the Offer section), **not** cash or generic gift cards. This ensures every entrant is an ideal customer who wants your actual products.
- **Entry loop**:
  - 1 entry: Enter email address (builds the core marketing list).
  - +2 bonus entries: Follow on Instagram / TikTok / X.
  - +3 bonus entries: Share launch link with friends (referral link).
  - +1 bonus entry: Comment on the launch announcement post.
- **Timeline**: Launch 10–14 days before official opening. Announce the winner on launch day.
- **Deliverables to draft**:
  - Giveaway landing page / post copy with clear value, prizes, and deadline.
  - Automated confirmation email thanking entrants and sharing their referral link.
  - Post-giveaway consolidation offer: Send all non-winners an exclusive launch discount (e.g. 15% off during launch week) so every entrant converts into an immediate sales opportunity.
  - Official rules: No purchase necessary, eligibility, dates, odds, and platform disclaimers (e.g. "Not sponsored by Instagram/Meta").

---

## What you write

Write the complete launch plan to `brands/<business-slug>/launch-plan.md`. If the file already exists, preserve completed checklist items and update pending milestones.

```markdown
# <Business name> Launch Plan

Site: <url>
Event type: <Brand Launch | Product Drop | Seasonal Campaign>
Target launch date: <YYYY-MM-DD>
Last updated: <YYYY-MM-DD>

## 1. Readiness Checklist

| Category | Item | Status | Finding / Evidence / Next Step |
|---|---|---|---|
| Technical | HTML Meta & Open Graph | PASS / FAIL / PENDING | <Quoted tags or missing elements> |
| Technical | SEO (Sitemap & Robots) | PASS / FAIL / PENDING | <Status of sitemap.xml and robots.txt> |
| Technical | Favicon | PASS / FAIL / PENDING | <Favicon link tag status> |
| Analytics | Google Analytics 4 | PASS / FAIL / PENDING | <Tag presence and Measurement ID> |
| Analytics | Google Search Console | PASS / FAIL / PENDING | <Verification status> |
| Channels | Social Profile Creation | PASS / FAIL / PENDING | <Handles checked across platforms> |
| Promo | Contests & Giveaways | READY / PENDING | <Selected giveaway structure> |
| Promo | Pop-up Opt-in / Discount Offer Provider | SELECTED / PENDING | <Provider (e.g., Justuno, OptiMonk, or Poptin) and offer> |
| Promo | LinkedIn Announcement | DRAFTED / PENDING | <Ready for review> |
| Promo | ProductHunt Submission | DRAFTED / PENDING | <Ready for review> |

## 2. Technical Audit Details
Quotes and findings from the live site read.

## 3. Contest & Giveaway Campaign
- **Prize Bundle**: <Items selected from brand Offer>
- **Entry Mechanics**: <Email capture + viral share actions>
- **Timeline**: <Start date, end date, drawing date>
- **Copy Drafts**: <Landing page copy, social teaser post, rules disclaimer>
- **Consolation Sequence**: <Special discount email sent to non-winners on launch day>

## 4. Launch Copy Deliverables
- **LinkedIn Post Draft**
- **ProductHunt Submission Package (Tagline, Description, Maker Comment)**
- **Social Profile Bios (Instagram, TikTok, X, Facebook)**

## 5. Timeline & Milestones
- T-14 days: Pre-launch contest announcement & waitlist capture opens.
- T-7 days: Technical fixes completed (HTML tags, sitemap, analytics verified).
- T-1 day: Final site walkthrough, test purchase / form submission.
- Launch Day: Store opens, ProductHunt goes live, LinkedIn post published, contest winner announced, consolation discount sent.
- T+3 days: Follow-up email to new subscribers with customer spotlight or hero product story.

## 6. Proposed Brand File Changes
Numbered list proposing additions to `brand.md` under `## Key dates` or `## Channels in use`.
```

## Proposing brand file changes

When launch dates, new social handles, or confirmed campaign dates are established, do not edit `brand.md` directly. Propose them under `## Proposed Brand File Changes`:

```markdown
1. Key dates | Add: 2026-12-01 - Store launch and viral giveaway drawing | [owner] | event-minder
2. Channels in use | Add: Instagram (@mangajdm), TikTok (@mangajdm) | [site] | event-minder
```

Apply accepted changes to `brand.md` using the change log protocol from `skills/marketing-manager/SKILL.md`.
