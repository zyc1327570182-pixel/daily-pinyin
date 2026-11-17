# 已完成的验证

## 输入与按键

真实 Rime 引擎测试包含 21 项检查：整句提交、左右 Shift 原样提交英文、继续英文、切回中文、退格、Esc、Enter、数字选词、翻页、标点、Caps Lock 以及词频学习。源码 `tests/behavior_test.cpp`，结果 `tests/key-behavior.tsv`。

桌面 Fcitx5 接口验证了整句上屏、Shift 保留英文、英文继续输入、返回中文；固定测试结果见 `tests/desktop-results.jsonl`。用户还在原 Firefox Snap 输入框中确认中文输入恢复正常。

## 容错对比

25 组固定输入见 `tests/candidate-cases.txt`。增加三类定向规则后，`jintain` 首选由“今天爱你”变为“今天”，`wansahng` 首选由“我暗杀那个”变为“晚上”，其余 23 组首选不变。记录见 `tests/typo-comparison.json`。这组样例不是总体准确率测量。

## 安装脚本

`python3 -m unittest discover -s tests -v` 使用临时用户目录验证备份、安装、恢复、升级、撤销升级及个人词库保留，不重启当前桌面输入法。

## 测试边界

已验证环境为 Ubuntu 24.04 x86_64 / GNOME Wayland。未覆盖所有桌面、发行版、应用、输入速度和长期词频学习行为，尚未做与微软拼音的整体准确率对照。

候选和按键原生测试必须指向独立的测试数据副本，不能直接使用正在运行的个人词库。测试会学习测试句子；打包时禁止带入这些用户词库。
