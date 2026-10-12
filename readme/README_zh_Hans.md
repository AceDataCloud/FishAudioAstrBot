# AstrBot 的 Fish Audio 插件

通过自己的 Ace Data Cloud 账号，在 AstrBot 对话中合成短 MP3 语音、查找公开音色。插件提供 `fish_generate_speech` 和 `fish_search_voices` 两个工具。

[English guide](../README.md) · [Fish TTS API](https://platform.acedata.cloud/documents/fish-tts?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=fishaudioastrbot_readme_documents_fish_tts) · [Fish 音色检索](https://platform.acedata.cloud/documents/fish-model-query?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=fishaudioastrbot_readme_documents_fish_model_query) · [当前价格](https://platform.acedata.cloud/models?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=fishaudioastrbot_readme_pricing)

## 搜索与安装

在 AstrBot WebUI 打开 **Extensions → Plugins → AstrBot Plugin Market**，搜索 **Fish Audio**。核对卡片名称 **Fish Audio by Ace Data Cloud**、作者 **acedatacloud** 和 [Fish 服务图标](https://cdn.acedata.cloud/e40fccc727.png)，安装后到 **Installed** 检查加载状态。

AstrBot Cloud 官方上架尚未完成。源码合并发布后，可在 **Installed → Install (+) → Install from URL** 输入 `https://github.com/AceDataCloud/FishAudioAstrBot` 预览。URL 安装不代表官方市场已上架或市场安装已验证。

## 配置 Key

首次使用请先注册并登录；如果应用页还没有通用应用，点击 **初始化通用应用（Initialize General Application）**，再按下面步骤管理密钥。

到 [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=fishaudioastrbot_readme_api_key) 复制 General application 的生成 API Key，或创建同时允许 `/fish/tts` 和 `/fish/model` 的 Key。调用前检查 Fish Audio 当前价格和余额。在插件设置 **Ace Data Cloud API key with Fish Audio access** 中粘贴 Key 本身；不要加 `Bearer `，也不要使用 `platform-...` 管理 Token。AstrBot WebUI 会遮蔽字段，但数据目录会保存原值，请保护该目录。

选择支持工具调用的聊天模型，并在当前 Profile 和 Persona 里允许 `fish_generate_speech`、`fish_search_voices`。

## 在聊天中使用

默认音色短语音示例：

> 只调用一次 `fish_generate_speech`，用 `s2-pro` 朗读“你好，AstrBot”，给我完成后的 MP3 链接。

工具同步调用一次 `POST /fish/tts`，把模型放在 HTTP `model` 请求头，发送 `format: "mp3"`，返回完成后的 `audio_url`。可显式选择 `s1`、`s2-pro` 或 `s2.1-pro`；插件不会自动切换模型或重试付费请求。单次文本上限为 4096 UTF-8 字节。

查找公开音色示例：

> 用 `fish_search_voices` 查找名称含“narration”的英语音色，返回最多五个 `reference_id` 和 `state`。

将已训练音色的 `reference_id` 传给 `fish_generate_speech`。音色 ID 可留空。首版支持公开或自己已有的音色 ID，不创建音色，也不接收参考音频做克隆。请仅使用有权使用的音色。

## 用量与排障

到 Ace Data Cloud 应用用量页核对返回的 trace ID。若响应没有 trace ID，按 API 和时间筛选只能得到关联线索，不能精确归属某条账单。Fish TTS 按目标文本的 UTF-8 字节数计费；以当前价格为准。音色检索与语音合成是不同请求。

| 现象 | 检查项 |
| --- | --- |
| 插件加载失败 | AstrBot 版本、**Failed to Load Plugins**、**Data & Logs → Logs**。 |
| 看不到工具 | 插件启用、当前 Profile/Persona 允许工具、聊天模型支持工具调用。 |
| HTTP 401/403 | Key 类型、Allowed APIs 路径和账号权限。 |
| 网络错误或缺少音频 URL | 再次生成前查请求历史；超时的请求可能已产生费用。 |
| 未查到音色 | 扩大名称范围或取消语言筛选，只选已训练的音色。 |

Key 只发送到 `https://api.acedata.cloud`，重定向会被拒绝。插件只向模型返回完成后的音频链接或精简公开音色字段，不透出上游原始响应。运行只需 Python 标准库。

## 已验证的本地运行与图标

官方 AstrBot `v4.28.2` 的隔离实例以 editable 方式加载两个工具。ChatUI 对 `fish_search_voices` 调用一次，得到 3 个公开音色结果；另一个会话对 `fish_generate_speech` 调用一次，以 `s2-pro` 合成一段短文本。返回的 MP3 链接为 HTTP 200、`audio/mpeg`，`ffprobe` 解码时长约 1.698 秒。响应没有 trace ID，因此不声称精确匹配某条用量记录。[脱敏结果](../tests/e2e-results.json)记载了验证边界。Cloud 投稿、官方市场安装、市场安装后的首次调用仍待完成。

`logo.png` 是未经修改的 32×32 [当前 Fish 服务图标](https://cdn.acedata.cloud/e40fccc727.png)，SHA-256 `aa20f99ea4423d4fd10976b62a6927bb96c9b9a5ab97a6ad5ba9d33993f28a10`。
