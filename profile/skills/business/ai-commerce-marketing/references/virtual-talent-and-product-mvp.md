# Virtual talent and physical-product MVPs

## Choose the asset by its job

| Asset | Owns an audience? | Appropriate use | Key risk |
|---|---|---|---|
| Brand avatar / virtual presenter | The brand owns and discloses the character | Product education, styling, design updates, consistent brand storytelling | Treating a fictional persona as a real customer or allowing generated visuals to misstate the product |
| Independent virtual influencer | The character/account is the media property | Grow a distinct audience, then test sponsorships, affiliate offers, or audience-fit products | Audience may follow for entertainment without buying the sponsor's product; growth and revenue are uncertain |
| AI UGC creative | No; it is an ad format | Produce clearly synthetic creative in a casual creator style | Fake testimonial, unsupported claims, or undisclosed synthetic identity |

For a seller who already has a brand and a product to validate, default to the brand avatar first. Add an independent influencer account only after evidence that the character attracts an audience beyond existing product posts and a separate monetization plan exists. Keep unrelated audiences (for example, men's lifestyle and women's apparel) separate until data supports a bridge.

## Small-MOQ path for apparel and other physical goods

1. Ask whether the supplier has ready stock or a standard catalog item and whether that item may be resold under the intended label.
2. Request paid sample/prototype terms, sample lead time, size set, color options, technical specification, and the minimum order definition (per style, color, or total units).
3. If the supplier's custom-style MOQ is too large, test a catalog item, commission a small microbatch from a local designer/workshop, or negotiate a paid prototype and staged production. A higher unit cost for a small pilot may be worthwhile when it avoids a large unvalidated commitment.
4. For a large MOQ, request a combined size run, fewer colors, staged deliveries, or a paid development/setup agreement; treat any concession as unconfirmed until the supplier agrees in writing.
5. Do not use an unfulfillable marketplace listing as a demand test. If no deliverable stock exists, collect non-binding interest via a compliant waitlist or content test and be explicit about availability/timing.
6. Before scaling, inspect a sample, test measurements/fit and quality, and estimate returns/defects. Apparel demand without size/fit evidence can look attractive in views while losing margin through returns.

## Product-fidelity checklist for AI images and video

Use actual samples and verified references for: front/back/side views, color under neutral light, seams and closures, logos/labels, fabric texture, garment length, fit, scale, and packaging. Treat generated depictions as drafts; compare against the sample frame by frame. Use actual photography for the primary marketplace product representation when generative editing could change product attributes. Use AI-styled scenes as supplementary content only when they remain truthful.

Do not write first-person claims such as “I wore it,” “it cured,” or “I bought it” for a fictional avatar. Safer copy attributes claims to the brand or describes visible/verified characteristics, and states when a model/persona is virtual.

## Test design and economics

- Start with one hero SKU and a bounded number of meaningfully different hooks; do not create many near-identical product listings just to simulate A/B tests.
- Track content reach, qualified product-page visits, add-to-cart, paid orders, fulfilled/kept units, cancellation, return/defect rate, and contribution per kept unit.
- Log model/tool credits, failed generations, editing labor, product samples, ads, marketplace deductions, packaging, and reverse-logistics costs. A creator's reported “free tools” may still hide time, subscription, or attribution costs.
- Calculate: **contribution per kept sale = actual seller payout after marketplace deductions − product cost − packaging/labeling − fulfillment/logistics − allocated advertising − expected return/defect losses**. Keep one-time sampling and content-production cost visible separately.
- Set a scale threshold before launch using the seller's actual required margin and cash constraints; do not invent universal view, conversion, or return-rate thresholds.

## Video-source analysis

When a creator demonstrates an AI-commerce workflow, separate (a) repeatable production steps from (b) claimed business results. Capture sample size, duration, platform, SKU/funnel, gross revenue, platform/payment/tool costs, and whether sales were attributable to the character. Recompute arithmetic from stated figures; label absent attribution or non-audited sales. Treat tool-rate claims and coupon-driven economics as promotional context, not a market benchmark.

## Hyperrealistic video generation recipe (Seedance / Video Diffusion)

To prevent synthetic UGC and product videos from looking like plastic CGI or AI cartoons:
1. **Character reference sheet:** Require a 4-angle reference collage (full body front, full body back, close-up face portrait, strict profile) on neutral background with natural skin texture and identifiable features (e.g. freckles, natural brows). Pass this into multi-reference modes (such as Seedance Omni Reference).
2. **Camera imperfections:** Instruct the model explicitly for consumer camera behavior: `modern smartphone vlog style`, `natural handheld movement`, `subtle camera shake`, `autofocus changes/hunting`, `mild digital noise`, `natural motion blur`, `authentic home-video imperfections`. Human perception interprets lens and sensor flaws as physical reality.
3. **Diegetic audio over background tracks:** Mandate `natural diegetic audio only` (footsteps, ambient room noise, fabric rustle, rain, zip closures) and prohibit generic royalty-free background music.
4. **Negative constraints:** Explicitly negative-prompt: `no CGI look, no beauty-filter skin, no polished commercial cinematography, no face changes, no distorted anatomy, no duplicate characters, no artificial morphing`.

## Premium Athleisure Visuals and Marketplace Card Architecture

1. **Avoid generic gym clichés:** Commercial gyms with black rubber flooring, heavy dumbbells, and iron racks signal cheap mass-market gear. For premium athleisure (Alo Yoga, Set Active, Sporty & Rich style), use:
   - *Architectural minimalism:* warm microcement, light travertine stone, clean geometric window shadows, single wood/stone block.
   - *Private Pilates / Reformer aesthetic:* light maple/ash wood, clean white reformer with leather straps, Japandi minimalism, natural indirect sunlight, indoor plants (strelitzia/monstera).
   - *Urban morning streetstyle ("Coffee Run"):* wet morning asphalt, concrete/glass cafe exterior, oversized layer (bomber or knit) thrown over athletic wear.
2. **Curated Lookbook Referencing (`models.com/db/lookbook`):** Borrow framing, lighting, and pose geometry directly from top luxury athleisure campaigns. Avoid runway avant-garde or resort/beachwear that disconnects from functional compression athletic products.
3. **Marketplace Cover Card (Slide 1) Rules:**
   - *Single coherent frame over split-screen:* Split-screen layouts cut usable area in half on mobile feeds (where 85%+ shopping occurs) and create cognitive overload.
   - *Monochrome styling:* Keep supporting apparel (e.g. sports bra) neutral (black, off-white, heather grey). A bright colored accent top (e.g. bright red) steals the first-second eye contact away from the hero product (e.g. black shorts).
   - *Faux-ugly competitor conversion drivers:* Mass-market competitors often win CTR not through graphic refinement, but by showing pure body transformation (e.g. scrunch-butt contouring in 3/4 rear angle) and immediate objection killers in bold text.
   - *Placement of technical reassurance (Slides 2–3):* Keep slide 1 focused on CTR (silhouette + core outcome + 3 concise text hooks). Place unadorned studio rear views, fabric macro closeups, and specific objection killers ("won't slip", "not see-through", "firm V-belt") on slides 2 and 3.

## Traffic distribution for marketplace apparel: Organic multicast vs. multi-hop funnels

- **Avoid multi-hop conversion funnels for apparel:** Do not route cold traffic from ads through landing pages, lead-capture forms, or Telegram bots before reaching the marketplace (e.g. Wildberries, Ozon). Fashion apparel is an impulse, visual purchase. Each extra redirect or hop sheds 60–80% of potential buyers.
- **Organic Multicast strategy:** Deploy one produced video across all major short-form platforms simultaneously (Instagram Reels, TikTok, YouTube Shorts, VK Clips). Direct viewers straight to the marketplace SKU via search terms ("find brand X on marketplace") or a single link aggregator in the profile bio.
- **FBS inventory synchronization:** When testing an apparel SKU via FBS using a local supplier's catalog items, verify physical warehouse availability before listing stock to avoid fulfillment cancellations and seller rating degradation.
