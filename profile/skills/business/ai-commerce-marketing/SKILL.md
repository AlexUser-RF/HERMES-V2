---
name: ai-commerce-marketing
description: "Use when planning AI-assisted commerce content."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [AI, e-commerce, brand marketing, virtual influencer, UGC, MVP]
    related_skills: [wildberries-automation, youtube-content]
---

# AI-assisted commerce content and MVP workflow

## When to Use

Use when planning AI-generated brand spokespeople or influencer accounts, producing synthetic UGC/product video, or validating a physical product through ecommerce content and a small-batch marketplace launch.

## Always-on rules

- Decide the commercial model before designing content: an owned brand avatar, an independent creator property, and AI-generated UGC are different assets with different audiences, disclosures, and monetization paths.
- Never script a fictional or generated character as a real customer who personally bought, wore, tested, or benefited from a product. Use an explicitly fictional brand presenter, or use a genuine customer/creator testimonial with permission.
- Keep physical-product depictions faithful to an actual sample and verified product facts. AI lifestyle assets can support discovery; they must not invent construction, color, fit, materials, packaging, or results.
- Treat creator-reported views, revenue, and rates as claims, not independently verified benchmarks. Recalculate any reported profit from the stated line items and flag missing costs, attribution, or short test windows.
- If a character reference appears to derive from a known copyrighted character or identifiable person, retain only broad non-identifying inspiration and create a distinct name, face, biography, wardrobe, and story before commercial use.
- Be transparent that a virtual persona is AI-generated. Check current ad-labeling, platform, model-provider, and commercial-use terms before publication; do not state legal compliance without checking the applicable rules.
- Do not confuse FBS or another fulfillment model with permission to sell nonexistent stock. Confirm that each listed unit can be produced and shipped within the marketplace's current rules and deadlines.
- Give the user a concrete recommended path, not a menu of incompatible strategies. Separate verified observations, assumptions, and unavailable evidence.

## Procedure

1. **Classify the goal and choose one primary model.**
   - Build demand for an existing physical brand/product → start with an owned brand avatar/presenter.
   - Build a media property for sponsorship, affiliate, or its own audience-led products → consider an independent influencer, but treat it as a separate venture.
   - Create an ad asset for a brand → AI UGC is a creative format, not proof of a real user's experience; label and script it accordingly.
   State the chosen model and why before discussing tools.

2. **Inspect the actual evidence.**
   - For supplied videos, load `youtube-content` and retrieve available transcripts; extract the workflow, stated results, prices, and caveats separately.
   - Inspect the actual brand storefront, supplier catalog, and reference image where access permits. Do not treat a brand link as a supplier link, and do not claim to have audited inaccessible pages.
   - Keep public-market research separate from private seller-account data. A Seller API token is scoped to its account; never ask the user to paste a secret into chat. Use `wildberries-automation` for WB API and operational details.

3. **Map product constraints before making assets.**
   Record sourcing lead time, sample availability, minimum order quantity, size/color breakdown, unit cost, packaging, labeling, quality-control process, and fulfillment readiness. If a supplier link or data is missing, deliver the strategy with that limitation stated and request only the missing inputs needed to select a SKU or calculate margins.

4. **Choose a low-risk product MVP.**
   Prefer one product with a real sample, short replenishment time, simple fulfillment, and a clear customer benefit. Test a supplier's ready/catalog item, paid samples, a designer's microbatch, or a negotiated small run before committing to a large MOQ. Do not present a zero-stock listing as a valid sales test; use a waitlist or audience-interest test if the product is not yet fulfillable.

5. **Build an original, consistent virtual asset.**
   Turn an approved character sheet into a concise character bible: distinctive identity, stable face/hair/body cues, voice, wardrobe boundaries, backstory, and disclosure wording. Keep the name and story original. For product scenes, provide genuine product references (sample photos, label closeups, material/color references, and correct fit/scale) and inspect generated frames for drift.

6. **Produce honest content.**
   Use the avatar for styling, design rationale, verified product explainers, product-development updates, and clearly fictional brand storytelling. For hyperrealistic video generation in diffusion models (e.g. Seedance 2.5), inject consumer camera imperfections (handheld shake, autofocus shifts, sensor noise) and diegetic audio rather than glossy CGI and background music (see references). Verify current tool plan, commercial rights, generation limits, and output resolution rather than assuming a subscription makes production cost zero.

7. **Run a bounded test and measure the funnel.**
   For marketplace apparel, rely on organic multicast across short-form platforms (Reels, TikTok, Shorts, VK Clips) with direct marketplace discovery rather than multi-hop paid ad funnels (landing pages/bots) that compound drop-off. Test a small set of distinct hooks/creative angles against one SKU; keep product, price, audience, and call-to-action stable enough to learn. Separate organic content metrics from paid traffic. Track reach → product-page visits → add-to-cart/orders → fulfilled/kept sales → returns, and record spend, generation iterations, editing time, and product cost.

8. **Calculate contribution before scaling.**
   Use actual settlement data and costs: contribution per kept sale = seller payout after marketplace deductions − product cost − packaging/labeling − fulfillment/logistics − allocated ads − expected return/defect losses. Include fixed sample/content costs separately. Scale only if contribution, fulfillment reliability, and customer feedback support it; views alone are not a go decision.

9. **Present a decision report.**
   Lead with the recommendation and business-model choice; then give evidence from source material, product constraints, the test plan, economic formula with unknowns, risks, and the exact next inputs/actions. Do not bury the decision under a generic tool list.

## References

- See [virtual talent and physical-product MVPs](references/virtual-talent-and-product-mvp.md) for the role decision table, small-MOQ options, test metrics, and product-fidelity checklist.
