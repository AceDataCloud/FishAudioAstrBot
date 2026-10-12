# Fish Audio for AstrBot

Generate short MP3 speech and find public Fish voices in an AstrBot conversation through your own Ace Data Cloud account. The plugin registers `fish_generate_speech` and `fish_search_voices`.

[简体中文指南](readme/README_zh_Hans.md) · [Fish TTS API](https://platform.acedata.cloud/documents/fish-tts?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=fishaudioastrbot_readme_documents_fish_tts) · [Fish Model Query](https://platform.acedata.cloud/documents/fish-model-query?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=fishaudioastrbot_readme_documents_fish_model_query) · [Current prices](https://platform.acedata.cloud/models?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=fishaudioastrbot_readme_pricing)

## Find and install

In AstrBot WebUI, open **Extensions → Plugins → AstrBot Plugin Market** and search **Fish Audio**. Confirm the card says **Fish Audio by Ace Data Cloud**, the author is **acedatacloud**, and the logo matches the [Fish service icon](https://cdn.acedata.cloud/e40fccc727.png). Install it, then check **Installed** for a load error.

The official AstrBot Cloud listing is pending. After the source release is merged, **Installed → Install (+) → Install from URL** with `https://github.com/AceDataCloud/FishAudioAstrBot` can preview the plugin. A URL installation does not prove market publication or market installation.

## Configure your key

New account? Register and sign in first. If the Applications page has no General application yet, choose **Initialize General Application**, then continue with the key steps below.

In [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=fishaudioastrbot_readme_api_key), copy a generation API key from your General application or create a key that permits both `/fish/tts` and `/fish/model`. Check the current Fish Audio price and your balance before synthesizing. Paste the key into the plugin's **Ace Data Cloud API key with Fish Audio access** setting; do not include `Bearer ` or use a `platform-...` management token. AstrBot masks the field in WebUI but stores the original value in its data directory, which should be protected.

Select an active chat model that supports tool calling. Allow `fish_generate_speech` and `fish_search_voices` in the conversation's profile and persona.

## Use the tools

For a short default-voice MP3, ask:

> Use `fish_generate_speech` once to say “Hello from AstrBot.” Choose `s2-pro` and show the returned MP3 link.

The tool sends one synchronous `POST /fish/tts` request. It puts the model in the HTTP `model` header, sends `format: "mp3"`, and returns a finished `audio_url`. `s1`, `s2-pro`, and `s2.1-pro` are explicit choices; the plugin never switches models or retries a paid call automatically. One request accepts at most 4096 UTF-8 bytes of text.

To choose a public voice, ask:

> Use `fish_search_voices` to find five voices whose title contains “narration” in English. Give me their `reference_id` values and `state`.

Pass the chosen trained voice's `reference_id` to `fish_generate_speech`. A voice ID is optional. This first version supports public or already owned voice IDs; it does not create voices or accept reference audio for cloning. Only use a voice when you have the right to use it.

## Verify and troubleshoot

Open your Ace Data Cloud application usage and match a returned trace ID when one is available. If the response has no trace ID, API and time are correlation only. Fish TTS billing depends on the text's UTF-8 byte count; check the current price rather than relying on a fixed example amount. Voice search and speech generation are separate calls.

| Symptom | Check |
| --- | --- |
| Plugin fails to load | AstrBot version, **Failed to Load Plugins**, and **Data & Logs → Logs**. |
| Tools are missing | Plugin enabled, active profile and persona allow the tools, chat model supports tool calling. |
| HTTP 401 or 403 | Key type, allowed API paths, and account access. |
| Network error or missing audio URL | Inspect request history before generating again; a timeout may still have incurred a charge. |
| No voice results | Search a broader title or remove the language filter; use only trained voices. |

The key goes only to `https://api.acedata.cloud`; redirects are rejected. The plugin exposes a finished audio URL or a short list of public voice fields to the model, without raw provider responses. It uses Python's standard library and needs no runtime package installation.

## Verified local run and asset

On official AstrBot `v4.28.2`, an isolated editable installation loaded both tools. ChatUI called `fish_search_voices` once and received three public voice results. A separate ChatUI conversation called `fish_generate_speech` once with `s2-pro` and a short default-voice text. The returned MP3 URL responded HTTP 200 with `audio/mpeg`; `ffprobe` decoded a 1.698-second MP3. No trace ID was returned, so this run does not claim an exact usage-row match. The [sanitized result](tests/e2e-results.json) records the test boundary. Official Cloud submission, market installation, and first call from a market installation remain open.

`logo.png` is the unmodified 32×32 [current Fish service icon](https://cdn.acedata.cloud/e40fccc727.png), SHA-256 `aa20f99ea4423d4fd10976b62a6927bb96c9b9a5ab97a6ad5ba9d33993f28a10`.
