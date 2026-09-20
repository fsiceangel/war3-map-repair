# war3-map-repair

[中文](#中文) | [English](#english)

## 中文

面向《魔兽争霸 III：重制版》（Warcraft III: Reforged）旧自定义地图的兼容性诊断 skill 与最小修复工具，采用 [MIT 许可证](LICENSE)。

从《人族无敌 II 2.3a》《逆天问道 3.1》的实际修复中提取：旧版内嵌 SLK 的模型字段迁移、可选的能力等级列回退、原图保护与 MPQ 校验。**不是所有 RPG 的一键修复器，也未证明是统一的 API 故障。**

- [完整修复说明、证据与未解决问题（中文）](skills/war3-map-repair/references/case-study.md)
- [Skill 入口（英文）](skills/war3-map-repair/SKILL.md)
- [离线回归记录](skills/war3-map-repair/references/regression.json)


### 问题背景：重制版 3.0 更新

本项目源于重制版随新 DLC **Forsaken Kingdom** 推出的 **3.0 更新**之后，旧自定义地图无法正常运行的实际反馈。暴雪的[官方介绍](https://news.blizzard.com/zh-tw/article/24302500/iii)确认了 DLC、3.0 更新与新增画面模式的发布背景。

这两张地图的故障是在该次更新后由用户报告的；尚未记录当时客户端的精确 build，也未通过逐版本对照定位引入故障的具体改动。因此，本项目聚焦 **Reforged 3.0 更新后的旧地图兼容问题**，并不声称所有旧地图都受影响，或购买 DLC 本身会导致故障。

### 安装 skill

将 `skills/war3-map-repair` 整个目录复制到 `~/.codex/skills/war3-map-repair`（或你的 agent 支持的 skills 目录），重新加载会话后使用 `$war3-map-repair`。不要把仓库根目录直接当作 skill。

### 命令行

在仓库根目录运行以下命令。需要 Windows、Python 3.10+，以及从 [StormLib 官方项目](https://github.com/ladislav-zezula/StormLib) 获取的与 Python 位数相符的 DLL。本仓库不附带游戏文件或 DLL。

```powershell
python -m pip install -r skills/war3-map-repair/scripts/requirements.txt
$env:STORMLIB_DLL = "C:\Tools\StormLib.dll"

# 只读诊断
python skills/war3-map-repair/scripts/repair_map.py "map.w3x"

# 输出新文件；拒绝覆盖原图或已有输出
python skills/war3-map-repair/scripts/repair_map.py "map.w3x" --output "map.compat.w3x" --migrate-models
```

仅在明确需要第 5/6 级回退时追加 `--extend-levels`。该选项复制第 4 级值，可能影响高等级技能的预期数值，因此不默认启用。

工具保留输入，生成独立候选地图和 JSON 报告。已有 skin 文件需要人工合并；工具拒绝覆盖。静态校验不能代替进游戏测试。失败时可能留下未完成的候选文件，请检查异常和报告，确认校验通过后再测试。

### 验证与已知限制

历史组合补丁得到用户“不闪退”的反馈；**小地图异常仍未解决**。新 CLI 在两张原始地图上进行了离线回归，复现此前修复结果，不等于在每个客户端版本中实测。由于历史修复同时应用了多项改动，也不能据此认定某一项就是唯一的崩溃根因。

仓库不包含地图、解包资源、第三方二进制、账号信息或个人路径，也不包含掉率改动。

### 测试与问题反馈

```powershell
python -m unittest discover -s tests -v
```

提交问题时请给出客户端精确 build、地图的 SHA-256、故障触发阶段、诊断报告，以及原版地图是否也能复现。先删除本地路径等个人信息。

## English

A skill and minimal repair toolkit for diagnosing legacy custom-map compatibility issues in **Warcraft III: Reforged**. Released under the [MIT License](LICENSE).

Extracted from repairs of 《人族无敌 II 2.3a》 (*Renzu Wudi II 2.3a*) and 《逆天问道 3.1》 (*Nitian Wendao 3.1*): migration of model fields in embedded legacy SLK tables, optional ability-level column fallback, source-map preservation, and MPQ integrity checks. **This is not a universal one-click RPG repair tool, and the evidence does not establish a shared API failure.**

- [Repair case study, evidence, and unresolved issues (Chinese)](skills/war3-map-repair/references/case-study.md)
- [Skill entry point (English)](skills/war3-map-repair/SKILL.md)
- [Offline regression records](skills/war3-map-repair/references/regression.json)


### Context: the Reforged 3.0 update

This project began with reports of legacy custom maps failing after the **3.0 update** released alongside the new **Forsaken Kingdom DLC** for Warcraft III: Reforged. Blizzard's [official overview](https://news.blizzard.com/en-us/article/24298590/warcraft-iii-reforged-forsaken-kingdom-deep-dive-recap) documents the DLC, patch 3.0, and new graphics mode.

The user reported these two maps failing after that update. The exact client build was not recorded, and a version-by-version comparison has not isolated the specific change that introduced the failures. The focus is therefore **legacy-map compatibility after Reforged 3.0**, without claiming that every old map is affected or that purchasing the DLC itself causes the problem.

### Install the skill

Copy the entire `skills/war3-map-repair` directory to `~/.codex/skills/war3-map-repair`, or to the skills directory supported by your agent. Reload the session and invoke `$war3-map-repair`. The repository root itself is not the skill directory.

### Command-line usage

Run these commands from the repository root. Requirements: Windows, Python 3.10+, and a DLL from the [official StormLib project](https://github.com/ladislav-zezula/StormLib) matching your Python architecture. Game files and DLLs are not bundled.

```powershell
python -m pip install -r skills/war3-map-repair/scripts/requirements.txt
$env:STORMLIB_DLL = "C:\Tools\StormLib.dll"

# Read-only diagnosis
python skills/war3-map-repair/scripts/repair_map.py "map.w3x"

# Create a separate output; refuse to overwrite the input or an existing output
python skills/war3-map-repair/scripts/repair_map.py "map.w3x" --output "map.compat.w3x" --migrate-models
```

Append `--extend-levels` only when a level 5/6 fallback is specifically justified. This option copies level 4 values and may affect the intended values of higher-level abilities, so it is disabled by default.

The tool preserves the input and creates a separate candidate map and JSON report. Existing skin files require a manual merge; the tool refuses to overwrite them. Static checks do not replace in-game testing. A failed run may leave an incomplete candidate file: inspect the exception and report, and confirm validation passed before testing it.

### Validation and known limitations

The user reported that the historical combined patch stopped the crashes; **the minimap issue remains unresolved**. Offline regression on the two original maps reproduced the previous repair outputs. This does not constitute in-game testing on every client version. Because the historical repair applied multiple changes together, it also does not identify any single change as the sole crash fix.

The repository contains no maps, extracted game assets, third-party binaries, account information, personal paths, or drop-rate modifications.

### Tests and issue reports

```powershell
python -m unittest discover -s tests -v
```

When reporting an issue, include the exact client build, map SHA-256, failure stage, diagnostic report, and whether the original map reproduces the problem. Remove personal information such as local paths first.
