# 安装、升级和恢复

## 支持范围与依赖

当前包验证于 Ubuntu 24.04 x86_64、GNOME Wayland、Fcitx5 5.1.7。需要桌面 systemd 用户服务；安装脚本须在当前用户的桌面终端运行，不要用 sudo 运行安装脚本。

系统应提供 Fcitx5、Classic UI、适合桌面的 GTK/Qt 输入模块、Python 3、python3-yaml、Noto Sans CJK，以及 librime 的常见系统依赖：glog、gflags、yaml-cpp 0.8、OpenCC 1.1、marisa 和 C++ 运行库。

Ubuntu 24.04 可通过系统软件管理器安装这些包；例如（依赖安装需要管理员权限）：

```bash
sudo apt install fcitx5 fcitx5-modules fcitx5-frontend-gtk3 fcitx5-frontend-gtk4 fcitx5-frontend-qt5 fcitx5-frontend-qt6 python3-yaml python3-gi fonts-noto-cjk libgoogle-glog0v6t64 libgflags2.2 libyaml-cpp0.8 libopencc1.1 libmarisa0
```

按照 [Fcitx5 的发行版配置说明](https://fcitx-im.org/wiki/Setup_Fcitx_5) 将桌面输入法框架设为 Fcitx5。包不自动改全局环境变量；首次切换框架后可能需要注销登录。

## 首次联网安装版

下载文件名以 `-online.tar.gz` 结尾的包，校验解压后执行 `./install-online.sh`。它先从万象官方 GitHub 下载约 389 MiB 的固定模型，验证 SHA256，通过后才进入安装流程。下载失败或校验失败时不修改当前输入法，重试不会覆盖已校验的模型。安装完成后输入完全离线。

## 完整离线包新装

从 Releases 下载具名离线包，核对 SHA256SUMS，解压后执行 `./install.sh`。预编译词库已包含，无需现场编译。脚本会备份受影响的 Fcitx5 配置、Rime 目录、日用拼音运行库和皮肤，随后安装并短暂重启输入法。

该包会将 Rime 设为第一组的默认输入法，采用简体、半角、中文标点。原有输入法条目会保留。已有 Rime 用户应注意：此安装是完整方案安装，当前 Rime 数据会先备份；不要把 `install.sh` 当作合并个人方案的工具。

备份：`~/.local/share/daily-pinyin/backups/`。

## 升级

已有旧版日用拼音执行 `./upgrade.sh`。它仅更新本次定制、编译后的 schema/prism 和皮肤；个人词库保持原位。新版本编译 schema 以本项目默认方案为基础，深度定制过方案的用户请先检查差异。

升级备份：`~/.local/share/daily-pinyin/upgrades/`。它不覆盖最初安装的备份。

## 恢复

- `./restore-upgrade.sh`：撤销最近一次智能与皮肤升级，个人词库保留。
- `./restore.sh`：恢复最近一次完整安装前的配置，并将安装后学习的词库及配置另存到该备份下的“使用后保存”目录。

请保留这些备份及安装脚本目录，直至确认日常使用正常。

## Firefox Snap

输入法通过 `systemd-run --user` 交给桌面用户服务启动，避免从受限应用继承不兼容的 AppArmor 标签。修复没有更改 Firefox 的安全规则。若其他应用尚未识别输入法，先重新聚焦输入框；必要时重启应用。

## 诊断

确认当前状态显示“中”，输入 `nihao` 应能看到“你好”。如果状态显示“en”，按一次 Shift。若所有应用均无候选，检查 Fcitx5 是否运行以及当前选中的输入法是否为日用拼音；若仅某个应用异常，记录其版本、安装方式（原生、Snap、Flatpak）及 X11/Wayland 类型。

运行日志位于 `~/.local/share/daily-pinyin/session.log`。分享日志前请删掉可能包含的私人输入。不要分享 `*.userdb`、`user.yaml`、`installation.yaml`、同步和备份目录。

## Win+V 剪贴板历史

安装后运行 `./enable-clipboard.sh`。使用基于 Fcitx5 剪贴板模块修改的扩展，无需另装常驻服务。首次升级此扩展会短暂重启 Fcitx5。最多 20 条文本，仅保存在进程内存中；重启 Fcitx5 后清空。复制文本后聚焦应用输入框，Win+V 打开，上下方向键选取，左右方向键翻页，Enter 插入，Esc 关闭；Delete 仅删当前项，Ctrl+Shift+Delete 后 Enter 确认清空。Backspace 不删除历史。保留 Ctrl+分号作为备用快捷键，中英文状态均可用。

GNOME 的通知中心原来占用 Win+V，脚本只解除这一绑定，保留 Win+M。旧配置单独备份，可运行 `./enable-clipboard.sh --restore` 恢复；此操作与完整安装、升级恢复相互独立。脚本不保存、读取或上传历史文本。

部分应用绕过输入法，或未配置 Fcitx5 输入模块，可能不能打开该面板。它是输入框里的文本历史，不是文件或图片剪贴板管理器。
