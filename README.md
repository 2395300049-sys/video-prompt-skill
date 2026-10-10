# 视频提示词 Skill

把创意、文案、小说片段或参考图整理成可使用的视频脚本、分镜、文生图与图生视频提示词。默认中文，支持产品展示、口播、微电影、漫剧角色、萌宠、奇幻变身与 MV 画面设计。

Skill 标识：`video-creation-prompts`。GitHub 仓库：`video-prompt-skill`。

## 使用

安装到支持本地 Skills 的环境后，可以这样发起任务：

```text
使用 $video-creation-prompts，把“雨后书店重新开门”做成15秒微故事，9:16，三镜以内。给分镜和每镜可复制的视频提示词。
```

```text
使用 $video-creation-prompts，依据这张产品图设计30秒展示片，保持产品结构和颜色。重点展示开合动作，只使用我提供的功能信息。
```

```text
使用 $video-creation-prompts，检查这份运镜提示词为何动作太多，保留故事目的，改成可执行的单镜头版本。
```

## 安装

克隆仓库到本地技能目录中的 `video-creation-prompts` 文件夹。例如：

```bash
git clone https://github.com/2395300049-sys/video-prompt-skill.git "${CODEX_HOME:-$HOME/.codex}/skills/video-creation-prompts"
```

如果目标目录已经存在，先检查现有内容，不要直接覆盖。安装后在新会话中确认技能已被发现。

## 内容

- [SKILL.md](SKILL.md)：调用入口和工作流程。
- [选题与口播](references/story-and-copy.md)、[分镜与时间](references/storyboards.md)、[镜头语言](references/camera-language.md)、[角色与美术](references/characters-and-art.md)、[十二类提示模板](references/prompt-recipes.md)、[修改与检查](references/revision-and-adaptation.md)。
- [完整来源索引](references/source-index.md)：152 份文件逐项记录，146 个独立文件，6 个完全重复文件。
- `data/prompt-catalog.jsonl`：1,974 条带来源位置的短词条、组合字段和图片方法记录。
- [分镜模板](assets/storyboard-template.md)与[原创 JSON 示例](assets/storyboard-example.json)。

## 离线工具

只需要 Python 3 标准库，无 API Key，也不会调用生成服务或消耗视频积分。从仓库根目录运行：

```bash
python3 scripts/search_library.py "环绕" --limit 6
python3 scripts/search_library.py "口播" --kind sources --limit 5
python3 scripts/search_library.py --source S145 --kind prompts --limit 4
python3 scripts/check_storyboard.py assets/storyboard-example.json
python3 -m unittest discover -s tests -v
```

检索支持多词同时匹配、来源过滤和重复来源重定向。分镜检查器验证成片时间连续性、总时长、必需字段与角色/产品引用；实际配音、画面连续性和生成效果仍以试读及作品为准。

## 蒸馏原则

将原资料拆成方法、字段、词汇和案例，修正镜头术语、时长冲突及错误画幅描述。示例中的 15 秒、固定对白语言、服装、LoRA 和模型参数不作为全局要求。风格词库与旧教程只提供参考，不保证当前工具能力、流量、审核或生成效果。

公开仓库提供蒸馏笔记和检索资料；原始文档、完整文本与 OCR 档案保留本地。第三方原资料的署名和权利不因本次整理改变，本仓库未给原作品另授许可。详细覆盖、计数口径与限制见[来源索引](references/source-index.md)。

提示词交付与视频生成是两个阶段；这个 Skill 不把脚本或提示词称作已完成的视频。
