---
name: nocturne-frame-pipeline
description: "Use when creating @outpost.frame Reels and photo content."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [Instagram, Reels, AI-Video, Syntx, Kling, Hailuo, Sunburst, DarkMoody]
---

# NOCTURNE (@outpost.frame) — Content Production Pipeline

Стандарт продакшна для Instagram @outpost.frame, закреплённый с Алексеем на релизах «Дом в лесу» и «Озеро».

## 1. Закон композиции 80/20 (Отрицательное пространство)
Главная ошибка прошлых версий — теснота и отсутствие «воздуха».
- **Strict Extreme Wide Establishing Shot** на 24mm / анаморфот. Никаких дефолтных `exterior view` (они дают 50mm с 15 метров, забивая 70% кадра объектом).
- Главный объект занимает максимум 10–15% нижней трети. Он должен быть буквально «раздавлен» монолитом дикой природы (`tiny isolated cabin dwarfed by colossal towering dark pines, massive negative space`).
- Разнообразие ракурсов в серии: высокий каменистый берег, сверхнизкий уровень воды у свай, удалённая точка с гребня холма.

## 2. Формула T2I-промпта базового кадра (9:16)
Пишется единым монолитным блоком (Sunburst 2.5 понимает физику буквально):
`[Ракурс + оптика 24mm] + [Масштаб объекта в пустоте] + [Практический источник света 2800K с ореолом halation] + [Многослойный туман] + [Элемент живого мира] + [Плёночный CineStill 800T лок]`

Обязательный плёночный хвост (Variant A):
```text
shot on 35mm CineStill 800T, muted petrol-teal and deep tungsten-amber color grade, heavy coarse organic film grain, crisp tactile analog texture, deep focus f/5.6, strictly no foreground bokeh, no moonlight, no digital gloss --ar 9:16 --style raw
```

## 3. Режиссёрский I2V-промпт (Слоёная физика, никаких однострочников)
Короткие промпты (`rain, slow push-in`) запрещены — они дают плоский 2D-зум и мёртвый кадр. Каждый видеопромпт строго делится на секции:
1. **Camera rig & optics:** `locked-off heavy tripod, authentic optical stability, subtle wind resonance, strictly no digital zoom, zero 2D zoom, extremely subtle anamorphic lens breathing, organic micro-jitter`.
2. **Atmospheric & fluid dynamics:** разноскоростной туман на разных планах (глубинный параллакс), круги на воде от свай с отражением янтаря, мокрые блики по закону Френеля (`wet reflective surfaces catching grazing amber light at low angles`), дождь разделён на взвесь в лучах и сток по поверхностям.
3. **Living world elements:** 1–2 элемента на сцену:
   - Одинокий ворон, бесшумно планирующий сквозь верхний туман к горизонту.
   - Холодные далёкие звёзды, мерцающие в разрывах низких облаков.
   - Неподвижный силуэт оленя с рогами на дальней опушке (никогда не анимировать ходьбу — нейросеть ломает ноги).
   - Дрожание нити накаливания 2800K, преломление горячего воздуха (`subtle heat shimmer distortion rising from hot lantern glass / exhaust / neon transformer`).
4. **Light physics:** органичное мерцание пламени/лампы/неона, расплывающийся ореол на мокром дереве/асфальте, глубокие проваленные тени.
5. **Loop clause:** `seamless calm dark loop, authentic analog film motion`.

Генерация строго по 5 секунд. Зацикливание в DaVinci методом Split & Cross Dissolve (12–18 кадров). Звук из бэклога @AloneSoundLab.

## 4. Оформление публикации
- Заголовок: ровно 1 слово строчными с точкой (`shelter.` `stillness.` `drift.` `silence.`).
- Пустая строка, точка `.`, пустая строка.
- Ровно 5–7 тегов: `#cinematic #moodygrams #35mm #darkaesthetic #cinestill800t #atmospheric #solitude #midnightvibes`.

## 5. Выдача по запросу нового кадра
В одном ответе всегда давать:
1. Готовый блок заголовка и тегов для копирования.
2. T2I-промпт базового кадра.
3. Многослойный режиссёрский I2V-промпт.
4. Рекомендацию по звуку из бэклога Alone Sound Lab.
