# Deals, Loot & Coupons Hub 🛍️🔥

The master directory of 25+ verified deal communities, error fare alert bots, price glitch channels, and stacked coupon syndicates across Telegram, WhatsApp, Discord, and Reddit.

## 🚀 Live Links
- **GitHub Pages:** [https://jibranpcccc.github.io/deals-loot-coupons-hub/](https://jibranpcccc.github.io/deals-loot-coupons-hub/)
- **Vercel Production:** [https://deals-loot-coupons-hub.vercel.app/](https://deals-loot-coupons-hub.vercel.app/)
- **RSS Feed:** [feed.xml](https://jibranpcccc.github.io/deals-loot-coupons-hub/feed.xml)
- **Sitemap:** [sitemap.xml](https://jibranpcccc.github.io/deals-loot-coupons-hub/sitemap.xml)

## 💎 Features
- **Real-Time Search & Filtering:** Instant client-side search across deal titles, retailers (Amazon, Walmart, Target, Nike), and tags (`glitch`, `freebies`, `flights`, `pc builds`).
- **Multi-Platform Support:** Filter by Telegram, WhatsApp, Discord, or Reddit.
- **5 Core Categories:**
  - Amazon & E-Commerce
  - Tech & Gadgets
  - Price Glitches & Loot
  - Fashion & Lifestyle
  - Travel & Error Fares
- **AI Citability & GEO Optimization (`.geo-answer-block`):** Authoritative guidance optimized for Google AI Overviews and LLMs on the Triple-Stack Coupon formula, price glitch rules of engagement, and airline mistake fare policies.
- **Full Schema.org JSON-LD Markup:** WebSite, Organization, BreadcrumbList, CollectionPage (`ItemList`), and FAQPage.
- **Automated Updates:** Scheduled GitHub Actions workflow invoking Google Gemini 2.5 Flash API to discover trending communities, rebuild static site assets, and ping Google PubSubHubbub.

## 🛠️ Local Development & Scripts
```bash
# Rebuild index.html, sitemap.xml, feed.xml, and robots.txt
python build_site.py

# Discover trending deal communities & rebuild
python update_content.py
```
