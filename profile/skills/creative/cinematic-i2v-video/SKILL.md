---
name: cinematic-i2v-video
description: "Use when prompting cinematic AI video. Guide I2V & loops."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [I2V, AI-Video, Kling, Syntx, Hailuo, DaVinci-Resolve, Reels, Cinematics]
---

# Cinematic I2V Video Production & Loop Engineering

A class-level skill for generating, directing, and editing cinematic Image-to-Video (I2V) assets (Kling, Syntx/Seedance, Hailuo, Runway) and assembling seamless, high-retention loops in DaVinci Resolve for short-form video (Instagram Reels / Shorts).

## When to Use

Use when:
- Writing or refining Image-to-Video (I2V) prompts for cinematic generators (Syntx, Seedance, Kling, Hailuo, Runway).
- Directing physical fluid dynamics (rain, splashes, waterfalls) or atmospheric effects (mist, fog, exhaust) without freezing or digital artifacts.
- Enforcing optical camera movement (pan, dolly, tracking) and preventing cheap 2.5D digital zoom.
- Assembling seamless, non-reversing loops in DaVinci Resolve or NLEs for Instagram Reels, Shorts, and TikTok.
- Designing high-contrast social avatars and channel icons under circular cropping constraints.

## Always-on Rules & Core Pitfalls

### 1. The Fluid & Atmospheric Physics Rule (Anti-Freeze)
- **Pitfall:** Prompting simply "heavy rain" or "storm" causes diffusion models to freeze the image like a still postcard with static water textures or artificial lens droplets.
- **Rule:** Always split fluid physics into three explicit interaction layers:
  1. *Airborne dynamics:* Rapid vertical rain streaks cutting through light beams (`rapid vertical rain streaks cutting sharply through practical light beams`).
  2. *Impact & runoff:* Water pouring in sheets off solid surfaces with violent splashing (`cascades of water pouring off the rusted awning, splattering violently onto the metal hood with bouncing mist droplets`).
  3. *Ground churn:* Surface liquid ripples and splashes (`ground puddles furiously churning with concentric ripple rings and liquid reflections`).
  4. *Atmosphere:* Exhaust vapor, cold steam, or rolling fog (`faint white exhaust vapor rising into damp cold air`).

### 2. The Optical Parallax Rule (Anti-2D-Zoom)
- **Pitfall:** Generic terms like "slow push-in" or "camera moves forward" trigger cheap 2.5D digital crop zooms that flatten depth and freeze background parallax.
- **Rule:** Explicitly mandate physical camera motion rigs and forbid digital scaling:
  - Use: `cinematic slow dolly pan`, `camera glides on a low tripod with authentic optical parallax`, `slow dolly drift to the left`.
  - Always enforce negative constraint in the main prompt and negative field: `strictly no digital zoom`, `no 2D zoom`, `no flat digital push-in`.

### 3. Background Life & Motion Continuity
- **Pitfall:** AI generators freeze distant background vehicles and people in mid-motion, creating awkward unmoving silhouettes.
- **Rule:**
  - For active traffic: Explicitly describe progressive displacement: `The vehicle on the dark highway in the background is slowly driving forward through the mist, its headlights cutting through the wet darkness`.
  - For stationary loops: Explicitly state the vehicle is idling to prevent frozen-in-motion looks: `Distant vehicle headlights are idling stationary on the dark shoulder`.

### 4. Single-Input UI Structuring (Syntx / Seedance)
- In interfaces lacking motion brushes or camera sliders, structure the prompt in strict linear execution order:
  `[Camera Rig & Motion Constraint] + [Active Dynamic Background/Subject] + [Environmental & Fluid Physics] + [Lighting, Halation & Emulation]`.

### 5. Clip Duration: The 5-Second Threshold
- **Rule:** Generate **5-second** clips rather than 8–10 seconds.
- **Why:** Diffusion models accumulate geometric drift, line warping, and text melting past 5 seconds. A 5-second generation yields a pristine, artifact-free 4–4.2s loopable slice.

### 6. The Non-Reversible Looping Law (DaVinci Resolve)
- **Pitfall:** Never use reverse / ping-pong looping on environmental or fluid scenes.
- **Why:** Reversing fluid physics makes rain fall into the sky and water climb up gutters, immediately breaking realism.
- **Procedure:** Always use the **Split & Cross Dissolve** method:
  1. Place the 5-second clip on timeline.
  2. Blade exactly at midpoint (`02:15` or `02:12`).
  3. Swap segments: place Part B at the start, Part A at the end (the middle seam is now 100% continuous motion).
  4. Apply a **Cross Dissolve of 12–18 frames (0.5–0.7s)** across the newly formed center seam.
  5. In rain, fog, and water scenes, the dissolve is invisible. Duplicate the resulting ~4s block 3–4 times for a 12–16s Reel.

### 7. Resolving Moving Objects in Loops
- When background traffic or headlights move across the scene:
  - *Natural traffic illusion:* With a 15–20 frame dissolve, a distant car fading into fog while a new one appears reads naturally as continuous highway traffic.
  - *Track isolation:* If headlights double or ghost, duplicate clip onto tracks V1 and V2. Apply a soft feathered power window (mask) to the highway on V2, while looping the ambient environment on V1.

### 8. Base Image Selection for Reels (T2I -> I2V)
- **Aspect Ratio:** Generate or crop to native vertical **9:16** (1080×1920) or **4:5**; horizontal 16:9 crops lose vital composition anchors (signs, vehicles, road).
- **Tactile Narrative Anchors:** Select base images with living details (a warm lit window in room #6, rusted sign lettering, glowing tail-lights, wet gritty asphalt) rather than sterile, empty digital glossy renders.

### 9. Social Avatar & Icon Readability
- A complex scenic render turns to mud inside a 40×40px circle.
- For dark/moody profile avatars:
  - Strict **1:1** aspect ratio with centered composition for circular masking.
  - High-contrast central silhouette (watchtower, glowing cabin, solitary lantern, or macro raindrop with bokeh).
  - Strict palette consistency: Deep Teal base + warm 3000K Amber glow / Red CineStill halation.
