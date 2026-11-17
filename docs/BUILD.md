# 构建和发布

仓库保留本项目源码、自定义 Rime 补丁、Fcitx5 皮肤、前端补丁和测试。大词库、语法模型与本机编译的运行库由具名 Releases 离线包提供。

## 对应源代码

离线包 `sources/` 中的四个压缩包就是本次原生构建的源代码，归档 SHA256 见 `sources/manifest.json`：

- librime 1.17.0：`rime/librime`，a52a340。
- librime-lua：`hchunhui/librime-lua`，6da5d6c。
- librime-octagram：`lotem/librime-octagram`，57d18b9。
- fcitx5-rime 5.1.4：`fcitx/fcitx5-rime`，034ddf9。修改完整保留于 `frontend-user-data.patch`。

## 原生库重建

在 Ubuntu 24.04 上准备 CMake、G++、pkg-config、gettext、extra-cmake-modules、patchelf、patch，以及 Boost、glog、gflags、yaml-cpp、LevelDB、marisa、OpenCC、Lua 5.4、X11、Fcitx5 Core/Modules 的开发包。发行版包名可参考：

```bash
sudo apt install build-essential cmake pkg-config gettext extra-cmake-modules patchelf patch libboost-all-dev libgoogle-glog-dev libgflags-dev libyaml-cpp-dev libleveldb-dev libmarisa-dev libopencc-dev liblua5.4-dev libx11-dev libfcitx5core-dev libfcitx5config-dev libfcitx5utils-dev fcitx5-modules-dev
```

将离线包中的四份源码压缩包放在仓库 `sources/` 下，再运行：

```bash
./scripts/build_native.sh
```

Lua 与 Octagram 合并编入 librime。前端使用自己的运行库搜索路径。`-ffile-prefix-map` 消除构建机目录，程序不依赖构建机原路径。

离线包另外携带 Ubuntu 的 `libleveldb1d` 和 `liblua5.4-0` 运行库；它们的上游代码未修改。用系统版本替换时应保留 SONAME 与 ABI 兼容。其他动态链接依赖由发行版提供，可用 `ldd payload/runtime/fcitx5/librime.so` 和 `ldd payload/runtime/lib/librime.so.1.17.0` 检查。

## 词库与模型

采用万象拼音 v18.1.13 的 `rime-wanxiang-base.zip`：
https://github.com/amzxyz/rime-wanxiang/releases/download/v18.1.13/rime-wanxiang-base.zip

语法模型为 `wanxiang-lts-zh-hans.gram`，源项目 https://github.com/amzxyz/rime-wanxiang-data ，本版本的固定 SHA256 见 `versions.json`。源项目滚动更新，因此不要假定最新同名文件与本包完全相同。

开发时以一份干净数据副本为底，叠加 `payload/rime/` 的自定义补丁，在含 Lua/Octagram 的本次引擎中部署生成 schema、prism 和 table。`tests/engine_probe.cpp` 可调用引擎部署并检查候选；`tests/behavior_test.cpp` 检查按键。两者始终使用临时数据目录，测试后删除个人学习产物，再打包。

## 测试与打包

```bash
python3 -m unittest discover -s tests -v
python3 scripts/package_release.py --payload-from /path/to/validated-offline-directory --output dist
# 省略模型，首次安装下载并校验：
python3 scripts/package_release.py --payload-from /path/to/validated-offline-directory --output dist/online --online
```

`--payload-from` 指向含 `payload/`、`sources/` 的已验证离线包目录。脚本使用该目录的运行库和干净上游数据，并叠加仓库中的配置与主题。若修改了 Rime 方案，必须先重新部署并验证该目录的 `build/` 产物；打包器不会替代引擎编译方案。

打包器拒绝个人词库、用户标识、同步目录、日志、备份及逃出包外的符号链接，统一 tar 的所有者字段，并生成 `SHA256SUMS`。发布前仍需检查 NOTICE、源码归档和安装结果。

CI 只验证脚本与临时用户目录的备份/恢复行为。原生引擎与真实桌面验证记录见 `docs/VALIDATION.md`。
