---
tags: [nocturne, models, routerai, llm, stack]
---

# 🌙 Nocturne — Model Stack

> [[Главная|🏠 Главная]] / [[05_Nocturne/Nocturne|🌙 Nocturne]] / [[05_Nocturne/Model_Stack|🧠 Model Stack]]
> Канонический файл: `D:\HERMES FILES\nocturne\MODEL_STACK.md` · Зафиксировано 09.10.2026

## Стек по ролям (RouterAI, ₽/1M)

| Роль | Модель | Вход | Выход |
|---|---|---|---|
| **Дефолт: чат + премисы** | `openai/gpt-6-luna` | 11 | 56 |
| Промпты (фото-рефы → видео) | `moonshotai/kimi-k3` | 230 | 1149 |
| Флагман (1 ролик) | `anthropic/claude-opus-5` | 555 | 2776 |
| Опция вместо Kimi (быстрее) | `anthropic/claude-sonnet-5` | 222 | 1110 |
| Зрение (только картинки) | `google/gemini-3.8-flash` | 83 | 416 |
| Эконом-креатив | `meta/muse-spark-1.3` | 139 | 472 |
| Делегирование | `moonshotai/kimi-k3` | 230 | 1149 |

## Цепочка эпизода
1. Новый чат → **30 премисов** на `gpt-6-luna` (дефолт, ~0,5 ₽)
2. Выбрал → **промпты** (фото-рефы, потом видео) на `kimi-k3`
3. Отличная идея → флагманский промпт на `claude-opus-5`
4. Зрение (разбор кадров) — `gemini-3.8-flash` (авто)

## Переключение моделей
Избранное в десктопе Hermes (панель справа от чата). Алиасов нет — одна кнопка.

## Ризонинг по моделям (`agent.reasoning_overrides`)
| Модель | Роль | Ризонинг |
|---|---|---|
| `gpt-6-luna` | **дефолт: чат + премисы** | medium |
| `kimi-k3` | промпты | high (фикс.) |
| `claude-opus-5` | флагман | high |
| `claude-sonnet-5` | опция вместо Kimi | medium |
| `gemini-3.8-flash` | зрение (только) | none |

На лету: `/reasoning high` (сессия) · `/reasoning high --global` (навсегда).

## Экономика (ОПУС дорогой — заменяем)
- Эпизод: Opus 5 ≈ 123 ₽ → **Kimi K3 ≈ 51 ₽** (97% креатива Опуса) → Muse Spark ≈ 23 ₽
- Месяц 20 эпизодов: Opus 2454 ₽ → Kimi K3 **1016 ₽** → Muse Spark 461 ₽

## Критерий
Креатив: Opus 5 (2121) > Kimi K3 (2071) > Muse Spark (1916) > GLM-5.2 (1753). **Цена/качество — Kimi K3.**

## TODO
- [x] Слепой A/B (09.10): все три (`kimi`/`muse`/`opus`) дали годный промпт — вывод «не умеют» был артефактом `max_tokens=1100`
- [ ] Проверить `claude-haiku-5.5` (11/56 ₽ — подозрительно дёшево)
- [ ] Сверять цены живым запросом к RouterAI `/models`
