# 下一词联想

本功能在选词上屏后，基于刚提交的中文及其末尾提供接词候选，采用本地统计表。原来的拼音词频学习、语法模型和个人词库继续保留。

默认不选中任何联想：直接 Enter 留给应用发送或换行，空格原样输入，数字 1–5 / 鼠标明确选择，或上下键选中后 Enter 接词。继续拼音会收起联想并进入正常组词。Esc / Backspace 收起联想；切换输入法和焦点不会自动接词。最多显示 5 个，连续接词最多 3 次。

## 升级和恢复

已有日用拼音，使用完整联想升级包执行 `./upgrade-prediction.sh`。脚本先备份静态运行库和编译配置，再合并联想补丁，针对现有方案重新编译，不替换个人用户词库。通过桌面用户服务重启以保留 Firefox Snap 兼容。

`./upgrade-prediction.sh --restore` 恢复最近一次联想升级前的运行库与方案，保留个人词库。`./upgrade-prediction.sh --disable` 安装并设为默认关闭。备份位于 `~/.local/share/daily-pinyin/prediction-backups/`，与初始安装、皮肤和剪贴板备份独立。

## 构建

在原生构建源码中加入 `predict-source.tar.gz`（上游 920bd41），应用 `sources/predict-user-experience.patch` 后与 Lua/Octagram 一起合并编入 librime。`scripts/build_native.sh` 已包含此步骤。

预测表以官方 data-1.0 的 predict.txt 为输入，通过 OpenCC t2s、去重和中文项过滤生成，再用插件附带的 build_predict 编译。输入/输出哈希见 sources/prediction-data.json；原始资源 URL：https://github.com/rime/librime-predict/releases/download/data-1.0/predict.txt 。

测试源 `tests/prediction/engine_interaction.cpp` 使用 Rime C API。请复制干净的静态方案数据和联想数据库到独立测试目录运行，不得指向正在使用的个人词库；学习行为检查会修改测试词库。

数据可精确重建（需要系统 OpenCC 库）：

```bash
python3 scripts/prepare_prediction_data.py --input predict.txt --output build/predict.tsv
build/native/rime/plugins/predict/bin/build_predict payload/rime/daily-predict.db < build/predict.tsv
```

转换器先核对官方输入文件 SHA256；重建的 TSV 应与 sources/prediction-data.json 中的 tsv_sha256 一致。
