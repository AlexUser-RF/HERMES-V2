---
name: kira-image-gen-setup
description: Use when configuring image generation for the kira profile.
---
# Hermes — генерация фото через RouterAI (GPT Image 2.5 Sunburst)

- Провайдер: RouterAI (`https://routerai.ru/api/v1`), в конфиге имя провайдера = `openrouter` (OpenAI-совместимый роутер, ключ в credential_pool как "RouterAI").
- Конфиг image_gen (во всех профилях и общем конфиге):
  ```yaml
  image_gen:
    provider: openrouter
    openrouter:
      model: openai/gpt-image-2.5-sunburst
  ```
- Точка проверки доступности модели: GET `{base_url}/models`, искать `openai/gpt-image-2.5-sunburst`. Smoke-тест: POST `{base_url}/images` с `{"model":"openai/gpt-image-2.5-sunburst","prompt":...,"size":"1024x1024"}`.
- Pitfall: статус credentials в auth.json (`last_status: exhausted`, 403) бывает устаревшим кэшем — реальный запрос к /models решает, работает ли ключ.
- Alternatives на RouterAI для фото: google/gemini-3-pro-image, bytedance-seed/seedream-5-0-pro, microsoft/mai-image-2.6-pro, black-forest-labs/flux-3-image.
