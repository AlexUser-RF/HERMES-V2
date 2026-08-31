---
name: alone-soundlab-expert
description: "Use for YouTube @AloneSoundLab: Echo lore, video and SEO."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [YouTube, DarkAmbient, AloneSoundLab, VideoAutomation, Lore]
---

# AloneSoundLab Expert & Producer

Экспертный скилл для продюсирования и автоматизации YouTube-канала **@AloneSoundLab** (постапокалиптический Dark Ambient / Drone / Sleep & Focus во вселенной Эхо в стилистике The Last of Us).

## 1. Канон Вселенной Эхо (Echo Lore & Bible)
- **Сеттинг:** Безымянный опустевший мегаполис и прилегающие территории. Никаких дешевых зомби, скримеров или монстров. Главные герои — тишина, ржавый металл, туман, природа, поглощающая цивилизацию, и заброшенные индустриальные объекты.
- **Главный персонаж:** Эхо (Echo) — девушка-скиталица в теплой куртке с капюшоном, рюкзаком и сигнальным факелом/фонарем. Осторожная, внимательная, перемещается от одной точки ориентира к другой.
- **Хронология арок:**
  1. *Rain / Meet Echo (Intro)* — Знакомство, первые шаги под эстакадой.
  2. *Winter Arc (EP.01 – EP.05)* — Зимний путь: Overpass → Cable Bridge → Frozen Ascent → Coastal Climb → Lighthouse in Winter Fog. На маяке пойман сигнал на радио.
  3. *Autumn Arc / Fall Descent (Текущая арка)* — Осенняя меланхолия, заброшенные мокрые дороги, ржавые рельсы, листва на бетоне, холодный осенний дождь и туман.

## 2. Формулы Промптов (AI Pipeline)

### Midjourney / Nano Banana (Visual Base)
- **Стиль:** Cinematic 35mm film photography, The Last of Us atmosphere, muted desaturated cinematic color grading, photorealistic, wet concrete, autumn rust and amber leaves, mist and cold haze, volumetric lighting, 8k, aspect ratio 16:9 for Long, 9:16 for Shorts.
- **Пример:** `cinematic film still of a lone female wanderer (Echo) in hooded weathered jacket walking through an overgrown abandoned railway station in autumn, decaying trains covered in wet amber leaves, dense cold fog, moody twilight, post-apocalyptic atmosphere, 35mm photography, gritty realistic textures, Kodak Portra 400 --ar 16:9`

### Kling / Veo (Motion & Physics Loop)
- **Фокус:** Медленное, медитативное движение без резких рывков.
- **Промпт:** `Slow subtle wind blowing falling wet autumn leaves, gentle cold rain mist drifting through the air, subtle breathing movement, cinematic slow motion, static locked-off camera, seamless loop.`

### Suno (Ambient Drone & Music)
- **Формат:** 3 части (Intro / Drone Core / Deep Outro).
- **Стиль:** `dark ambient, atmospheric drone, deep sub-bass drone, tape hiss, melancholic cello textures, post-rock reverb, distant rain textures, 60 bpm, no drums, no rhythm, no sudden spikes, meditational, sleep focus.`

## 3. SEO и Структура YouTube (English Only)
- Все названия, описания, теги и титры — **строго на английском языке** (для глобального рынка США/Европы).
- **Паттерн названия Long:** `[Location/Atmosphere] (No Talking) | [Duration] Dark Ambient Drone for Sleep & Focus — Autumn Arc EP.01`
- **Структура описания:**
  1. Художественный лор Эхо (2-3 предложения).
  2. Плейлист и номер эпизода.
  3. Таймкоды (Chapters).
  4. Рекомендации по прослушиванию (`Headphones recommended. Keep volume comfortable.`).
  5. Ссылки на связанные Shorts.

## 4. YouTube API & Автоматизация
- Скрипты заливки и управления метаданными используют Google OAuth с YouTube Data API v3 (`https://www.googleapis.com/auth/youtube.upload`, `https://www.googleapis.com/auth/youtube`).
- Автоматическая сборка видео через FFmpeg: сшивка видеолупа из Kling в 2-3 часовой видеоряд с кроссфейдами аудиодорожек из Suno.
