# war3-map-repair

魔兽争霸 III 旧自定义地图兼容性诊断 skill 与最小修复工具。MIT 开源。

从《人族无敌 II 2.3a》《逆天问道 3.1》的实际修复中提取：旧版内嵌 SLK 的模型字段迁移、可选的能力等级列回退、原图保护与 MPQ 校验。**不是所有 RPG 的一键修复器，也未证明是统一的 API 故障。**

- [完整修复说明、证据与未解决问题](skills/war3-map-repair/references/case-study.md)
- [Skill 入口](skills/war3-map-repair/SKILL.md)

## 安装 skill

将 `skills/war3-map-repair` 整个目录复制到 `~/.codex/skills/war3-map-repair`（或你的 agent 支持的 skills 目录），重新加载会话后使用 `$war3-map-repair`。不要把仓库根目录直接当作 skill。

## 命令行

需要 Windows、Python 3.10+，以及从 [StormLib 官方项目](https://github.com/ladislav-zezula/StormLib) 获取的与 Python 位数相符的 DLL。本仓库不附带游戏文件或 DLL。

```powershell
python -m pip install -r skills/war3-map-repair/scripts/requirements.txt
$env:STORMLIB_DLL = "C:\Tools\StormLib.dll"
# 只读诊断
python skills/war3-map-repair/scripts/repair_map.py "map.w3x"
# 输出新文件；拒绝覆盖原图或已有输出
python skills/war3-map-repair/scripts/repair_map.py "map.w3x" --output "map.compat.w3x" --migrate-models
# 仅在明确需要第 5/6 级回退时追加 --extend-levels
```

工具始终保留输入，输出独立候选和 JSON 报告。已有 skin 文件需要人工合并；不支持直接覆盖。报告的静态校验不能代替进游戏测试。生成失败会留下标记为未验证的候选，请检查异常而非直接使用。

历史组合补丁得到用户“不闪退”的反馈；小地图异常仍未解决。新 CLI 在原始两张地图上做离线回归，不等于在每个客户端版本中实测。仓库不包含地图、解包资源、第三方二进制、账号信息或个人路径，也不包含掉率改动。

## 测试

```powershell
python -m unittest discover -s tests -v
```

提交问题时请给出客户端精确 build、图的 SHA-256、触发阶段、诊断报告和是否能用原版复现。先删除本地路径等个人信息。
