---
name: xmp-to-capture-one
description: "Convert Lightroom XMP presets to Capture One costyle."
version: 1.0.0
platforms: [windows]
metadata:
  hermes:
    tags: [photo, capture-one, lightroom, presets, costyle]
---

# XMP to Capture One Preset Converter

Use this skill when converting Adobe Lightroom / Camera Raw presets (`.xmp`) into native Capture One styles (`.costyle`) and installable `.costylepack` packages.

## What It Does
- Maps 4 tone curves (RGB, R, G, B) to C1 `GradationCurve*`.
- Maps Exposure, Contrast, High Dynamic Range (HighlightRecoveryEx, ShadowRecovery, WhiteRecovery, BlackRecovery).
- Maps Clarity & Structure (Texture).
- Maps Split Toning to C1 3-way `ColorBalance` (Highlight & Shadow RGB vectors).
- Maps 8-channel HSL adjustments & Camera Calibration to C1 `ColorCorrections`.
- Maps Film Grain and Sharpening.
- Installs directly into `%LOCALAPPDATA%\CaptureOne\Styles` and creates a `.costylepack` archive.

## Execution
Run `scripts/convert.py`:
```bash
python scripts/convert.py --input "PATH_TO_XMP_DIR" [--name "Pack Name"] [--no-install]
```
