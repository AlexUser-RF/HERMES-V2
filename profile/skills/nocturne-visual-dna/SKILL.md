---
name: nocturne-visual-dna
description: "Use for nocturne dark & moody Instagram visual DNA."
version: 1.0.0
license: MIT
platforms: [windows]
---

# Nocturne — Dark & Moody Cinematic Visuals

Instagram-проект: кинематографичный dark & moody визуал в духе @offstreamvisuals (off.stream). Не аниме. Реализм + плёнка + ночная меланхолия.

## Рабочая папка
`D:\HERMES FILES\nocturne\` → `prompts/`, `renders/`, `reels/`, `audio/`, `scripts/`
Профиль Hermes: `nocturne`. Никнейм IG: согласовать с Алексеем (кандидаты: nocturne.shift, deadsignal.raw, silentdrifts, afterhours.raw, outpost.zero, voidroute).

## Visual & Color DNA (не отступать)
Палитра — ровно 3 доминанты:
1. **Deep Teal / Petrol Blue / Pitch Black** — тени и фон (ночное небо, мокрый асфальт, лес).
2. **Amber / Tungsten Glow (2800K–3200K)** — точечные тёплые источники (приборка, фары, неон мотеля, костёр).
3. **Muted Slate Grey** — туман, дымка, мокрые поверхности.

Оптика: имитация плёнки **CineStill 800T** (янтарно-красные гало вокруг ночных огней) + **35mm anamorphic** (широкая перспектива, мягкий блюр краёв). Никакого «цифрового нейро-мыла» — всегда film grain, shallow DOF.

## Master Style Lock (вклеивается в КАЖДЫЙ промпт без изменений)
```
cinematic 35mm photograph, shot on CineStill 800T, dark and moody aesthetic,
high atmospheric depth, misty night, muted teal and rich amber color grading,
wet surfaces with subtle reflections, film grain, photorealistic texture,
shallow depth of field --ar 9:16 --style raw
```
Формула промпта: `[Сюжет/Объект] + [Lighting & Weather] + [Master Style Lock]`

## Camera Grammar (I2V — только эти 4 движения, ничего хаотичного)
1. **Slow Push-In** — медленный наезд к объекту (стекло, окно, фары).
2. **Static Drift** — штатив; движется только физика: дождь по стеклу, пар, туман, мерцание лампы.
3. **Slow Pan/Tilt** — плавный перевод (приборка → трасса).
4. **Tracking Shot** — объект медленно удаляется в туман/тоннель.

Анимировать ТОЛЬКО микро-динамику. Экшен/ходьбу — нельзя (ломается).

## I2V-промпты для Hailuo/Kling (коротко, на английском)
Шаблон: `subtle motion only: <2-3 физических элемента>, slow <camera move>, no character movement, seamless loop feel`
Пример: `rain droplets sliding down windshield, headlight glow pulsing through fog, very slow push-in, static interior framing, no people moving, seamless loop`

## Копирайтинг
В описании ролика — ОДНО слово или короткая недосказанность, со строчной буквы и точкой: `disconnect.` `no signal.` `somewhere far.` `shelter.` `2:14 am.` Без эмодзи-простыней, без хэштег-спама (3-5 рабочих: #cinematic #moodygrams #35mm #nightdrive #lofi).

## Пайплайн 1 ролика (~15 мин)
1. Выбор микро-сюжета из рубрикатора.
2. Генерация кадра 9:16 (Midjourney v6 `--niji` НЕ использовать; Flux/MJ + Style Lock).
3. Отбор по QA-чеклисту.
4. Апскейл при необходимости.
5. I2V 5 сек (Hailuo > Kling) с одним из 4 движений камеры.
6. Звук: ASMR-слой (дождь/двигатель/костёр) + низкий эмбиент (бэклог AloneSoundLab / трендовый звук IG).
7. CapCut/DaVinci: зерно плёнки + короткий тайтл-слово.
8. Публикация. Лучшее время: поздний вечер (аудитория night owls).

## Рубрикатор сюжетов (для контент-плана)
- **Night Drive:** салон ретро-авто, мокрое стекло, фары в тумане, дальний свет на серпантине.
- **Roadside Solitude:** одинокий мотель с неоном, пустая заправка ночью, машина у обочины.
- **Water & Silence:** берег туманного озера, пирс, отражения огней в стоячей воде.
- **Forest Cabin:** домик в глуши, дым из трубы, свет окна в чёрном лесу.
- **Overpass/Rain:** мокрый путепровод, боке городских огней, капли на перилах.

## QA-чеклист перед публикацией
- [ ] Палитра = teal + amber + slate (нет случайных цветов)?
- [ ] Гало на источниках света есть (CineStill-эффект)?
- [ ] Нет пластиковости/артефактов ИИ (пальцы, текст, кривые отражения)?
- [ ] Вертикаль 9:16, композиция под мобильный экран?
- [ ] Движение в видео = одно из 4 разрешённых, петля плавная?
- [ ] Тайтл = одно слово, строчная, точка?

## Связка с экосистемой Алексея
- Музыка/эмбиент — из пайплайна @AloneSoundLab (Suno/Veo), тон дарк-эмбиент подходит идеально.
- Визуал cozy-ниши потенциально кормит принты для WB «Галерея 17» (кружки в таких сценах — центральный предмет).
