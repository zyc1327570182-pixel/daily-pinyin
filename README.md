# 日用拼音 · Daily Pinyin

给 Linux 日常中文输入做的一套省心配置：整句拼音、个人词频学习、常见错拼容错，以及接近微软拼音操作习惯的浅色候选框。

基于 **Fcitx5 + Rime + 万象拼音**，输入处理在本机完成，无需账号或 API Key。

![浅色候选框实际预览](docs/preview.png)

## 用起来是什么感觉

- 连续输入全拼，空格上屏首选；也支持首字母简拼。
- 中文模式打了 `hello` 才发现想输英文？**按一下 Shift，保留 `hello` 并切到英文**，无需重打。
- 中文显示 **中**，英文显示 **en**。Caps Lock 继续负责大写。
- 每页横排五个候选，白底圆角、蓝色首选，附带 Fluent Light 皮肤。
- 使用本地语法模型、上下文重排和个人词频学习；可学习词组长度上限 12 字。
- 针对有限几类拼写错位增加容错，例如 `jintain → 今天`、`wansahng → 晚上`。
- 安装前自动备份，可恢复旧输入法；升级保留个人词库。
- 可启用 **Win+V 剪贴板历史**，选取最近复制的文本直接插入，保留 Ctrl+分号备用键。

本项目是已有开源输入法组件的集成、配置和体验改进。微软风格指操作习惯与配色，项目与微软无关联。

## 下载与安装

当前预编译包面向 **Ubuntu 24.04 x86_64**，在 **GNOME Wayland + Fcitx5 5.1.7** 上实测。其他发行版和 ARM 暂未验证。

首次联网安装版只省略模型，运行 `./install-online.sh` 会从万象官方 GitHub 下载固定模型并验证 SHA256，完成后自动安装。输入过程始终在本机；适合下载完整离线包较慢的用户。需要联网下载约 389 MiB，之后无需联网。

1. 打开 [Releases](https://github.com/zyc1327570182-pixel/daily-pinyin/releases/latest)，下载 `daily-pinyin-v0.1.0-ubuntu24.04-x86_64-online.tar.gz` 或完整离线包，以及 `SHA256SUMS`。
2. 确保系统已有 Fcitx5，并且已将桌面输入法框架设为 Fcitx5。依赖说明见 [安装指南](docs/INSTALL.md)。
3. 在桌面终端校验并解压，进入目录安装：

```bash
sha256sum -c SHA256SUMS
# 若只下载了离线安装包，其他附件会提示缺失；请确认该安装包一行显示 OK。
tar -xzf daily-pinyin-v0.1.0-ubuntu24.04-x86_64-online.tar.gz
cd daily-pinyin-v0.1.0
./install-online.sh
```

完整离线包解压后运行 `./install.sh`，模型已包含。

安装脚本会短暂退出并重启 Fcitx5。新增运行库放在用户目录，不替换系统库。首次把系统框架改为 Fcitx5 后，可能需要注销登录。

**请下载具名离线安装包。GitHub 自动生成的 “Source code” 压缩包和 `git clone` 仅包含源码，不含运行库、词库和模型，不能直接安装。**

已有旧版日用拼音，请运行 `./upgrade.sh`。恢复最初安装前的配置用 `./restore.sh`；仅撤销最近一次智能与皮肤升级用 `./restore-upgrade.sh`。详情见 [安装与恢复](docs/INSTALL.md)。

## 启用剪贴板历史

安装后在桌面终端运行 `./enable-clipboard.sh`，即可在输入框中按 **Win+V**（或 Ctrl+分号）打开历史，上下方向键选取、左右方向键翻页、Enter 插入、Esc 关闭；Delete 仅删当前项，Ctrl+Shift+Delete 后 Enter 确认清空。最多 20 条文本，仅保存在当前输入法进程内存中，重启后清空。支持英文键盘状态。

GNOME 下会释放原先通知中心占用的 Win+V，保留 Win+M；设置先备份，可用 `./enable-clipboard.sh --restore` 撤销。其他桌面如拦截 Win+V，需自行解除冲突。需要 `python3-gi`。

## 常用按键

| 按键 | 行为 |
| --- | --- |
| Space | 提交首选 |
| 1–5 | 选择候选 |
| Shift | 中英切换；正在组词时原样提交字母并切到英文 |
| Enter | 原样提交字母 |
| Esc | 取消当前输入 |
| PageUp / PageDown，减号 / 等号 | 翻页 |
| Caps Lock | 大写锁定 |
| Ctrl+Space | 开关输入法 |

Shift 转英文仅作用于尚未上屏的字母，已经上屏的汉字不会追溯转换。

## 源码与贡献

- `payload/rime/*.custom.yaml`：拼音与按键定制。
- `payload/theme/fluent-light/`：皮肤配置与原创图片；`scripts/build_theme.py` 可重新生成。
- `install.py`、`upgrade.py`、`restore*.py`：用户级安装、升级和恢复。
- `sources/frontend-user-data.patch`：Fcitx5 Rime 前端的小修改。
- [构建与打包](docs/BUILD.md)：固定版本、源码与离线包打包方法。
- [验证记录](docs/VALIDATION.md)：按键、错拼对比、桌面与 Firefox 验证范围。

欢迎提交问题，附上发行版、桌面环境、X11/Wayland、Fcitx5 版本、出现问题的应用和复现步骤。请勿上传个人词库、同步目录或包含私人输入内容的日志。

## 致谢与许可

感谢 [Fcitx5](https://github.com/fcitx/fcitx5)、[fcitx5-rime](https://github.com/fcitx/fcitx5-rime)、[Rime](https://github.com/rime/librime)、[librime-lua](https://github.com/hchunhui/librime-lua)、[Octagram](https://github.com/lotem/librime-octagram)、[万象拼音](https://github.com/amzxyz/rime-wanxiang) 和[万象词库及语法模型](https://github.com/amzxyz/rime-wanxiang-data)的作者与贡献者。

本项目原创部分采用 MIT 许可；第三方组件、数据及衍生补丁按各自许可证分发。完整归属与修改说明见 [NOTICE.md](NOTICE.md) 和 `third-party/`。
