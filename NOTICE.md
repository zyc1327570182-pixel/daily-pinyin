# 第三方组件、数据与修改说明

日用拼音由现有开源组件组成。下表中的项目名、作者、许可证和源地址保留各自归属，不暗示上游或微软对本项目的背书。

| 组件 | 来源与版本 | 许可 | 本项目处理 |
| --- | --- | --- | --- |
| Fcitx5 | https://github.com/fcitx/fcitx5；系统安装 | LGPL-2.1-or-later 等，上游为准 | 使用系统框架，不随包替换 |
| fcitx5-rime | https://github.com/fcitx/fcitx5-rime；5.1.4，034ddf9 | LGPL-2.1-or-later；部分构建文件 GPL-2.0-or-later | 修改目录回退与中/en 标识；附原始源码和补丁 |
| librime | https://github.com/rime/librime；1.17.0，a52a340 | BSD-3-Clause | 合并构建下列 Lua 与 Octagram 插件 |
| librime-lua | https://github.com/hchunhui/librime-lua；6da5d6c | BSD-3-Clause | 合并到 librime，保留上游代码 |
| librime-octagram | https://github.com/lotem/librime-octagram；57d18b9 | BSD-3-Clause | 合并到 librime，保留上游代码 |
| 万象拼音 | amzxyz 及上游贡献者，https://github.com/amzxyz/rime-wanxiang；v18.1.13 Base | CC-BY-4.0，详见 wanxiang-LICENSE | 采用其方案、词库、Lua 与 OpenCC 数据；自定义补丁调整按键、显示、候选、上下文与限定拼写容错；预编译词库 |
| 万象语法模型 | amzxyz 及上游贡献者，https://github.com/amzxyz/rime-wanxiang-data；wanxiang-lts-zh-hans.gram | CC-BY-4.0，详见 wanxiang-data-LICENSE | 模型原样使用，SHA256 见 versions.json |
| LevelDB 1.23 | https://github.com/google/leveldb；Ubuntu 包 libleveldb1d 1.23-5build1 | BSD-3-Clause 等 | 原样附带运行库 |
| Lua 5.4.6 | https://www.lua.org/；Ubuntu 包 liblua5.4-0 5.4.6-3build2 | MIT 等 | 原样附带运行库 |

各组件完整版权文本与 Debian 包版权声明位于 `third-party/`。离线安装包的 `sources/` 附带本次构建所用的 librime、Lua 插件、Octagram 插件、fcitx5-rime 源码压缩包以及前端补丁；这些源代码的许可不被根目录 MIT 许可替换。

系统提供的 glog、gflags、yaml-cpp、OpenCC、marisa、Fcitx5、C/C++ 运行库等继续由发行版维护，不随本包替换。相关归属声明也保留于 `third-party/`。

Fluent Light 皮肤图片由本项目绘制，采用通用白底圆角与蓝色选中风格，未使用微软图标、字体文件或商标资产。Noto Sans CJK SC 字体由系统提供。

## 剪贴板交互模块

`src/clipboard/` 基于 Fcitx5 5.1.7 的剪贴板模块（CSSlayer 及贡献者，LGPL-2.1-or-later），保留版权头和完整修改后源码。修改包括：方向键选择与跨页、翻页自动选中、Delete 单项删除、Backspace 不删除、清空二次确认与中文操作提示。`orderedset.h` 是上游 `misc_p.h` 中 OrderedSet 的原样提取，保留原许可。

当前预编译扩展通过 X11/XWayland 收集文本，在已验证的 GNOME Wayland 桌面通过 XWayland 剪贴板桥接使用；原生 wlr-data-control 支持不在此构建中启用。系统 Fcitx5 库保持原样。

## 下一词联想插件和数据

采用 [rime/librime-predict](https://github.com/rime/librime-predict) 的 920bd41 源码及 data-1.0 发布中的 predict.txt。保留其 BSD-3-Clause 许可证于 `third-party/librime-predict-LICENSE`，原始源码归档的 SHA256 见 sources/manifest.json。

本项目修改记录于 `sources/predict-user-experience.patch`：不默认选中建议、Enter 防误选、空格及标点透传、显式方向键选择、上下文重置防止旧候选重现、会话独立、候选数限制和整句末尾回退。前端补丁增加“联想”标题并阻止切换输入法时提交零编码建议。

数据经 OpenCC t2s 转为简体，合并重复键值并保留最高频次，过滤非中文项，每个上下文最多保留 16 个接词供引擎取前 5 个。原始来源和输入/输出哈希见 sources/prediction-data.json。输入过程不下载数据、不访问网络、不读取其他应用输入框。
