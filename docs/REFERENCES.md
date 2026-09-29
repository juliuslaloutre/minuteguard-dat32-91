# Références techniques

Sources officielles consultées le 29 septembre 2026 :

- [OpenAI — Prompt engineering](https://developers.openai.com/api/docs/guides/prompt-engineering)
- [OpenAI — Structured model outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [OpenAI — Rate limits et exponential backoff](https://developers.openai.com/api/docs/guides/rate-limits)

Les choix correspondants sont : Responses API, `text.format` avec JSON Schema
strict, et retry borné avec prise en compte de `Retry-After`. Les versions de
modèles et de SDK pouvant évoluer, elles sont configurables et bornées dans le
projet plutôt que supposées immuables.

