#!/usr/bin/env python3
"""Offline, per-user installation of the validated daily Pinyin preset."""
import argparse
import configparser
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
TARGETS = [
    '.config/fcitx5/config', '.config/fcitx5/profile',
    '.local/share/fcitx5/addon/rime.conf',
    '.local/share/fcitx5/inputmethod/rime.conf',
    '.local/share/fcitx5/addon/clipboard.conf',
    '.local/share/fcitx5/rime', '.local/lib/daily-pinyin',
    '.config/fcitx5/conf/classicui.conf',
    '.local/share/fcitx5/themes/fluent-light',
]

def read_ini(path):
    c = configparser.ConfigParser(interpolation=None, strict=False)
    c.optionxform = str
    if path.exists():
        c.read(path, encoding='utf-8')
    return c

def write_ini(path, c):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        c.write(f, space_around_delimiters=False)

def copy_path(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, symlinks=True, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)

def session_environment():
    env = os.environ.copy()
    # Recover the actual Fcitx display environment, without copying credentials.
    allowed = {'DISPLAY', 'WAYLAND_DISPLAY', 'XDG_CURRENT_DESKTOP',
               'XDG_SESSION_TYPE', 'XDG_RUNTIME_DIR', 'DBUS_SESSION_BUS_ADDRESS',
               'XAUTHORITY', 'GTK_IM_MODULE', 'QT_IM_MODULE', 'XMODIFIERS'}
    pids = subprocess.run(['pgrep', '-u', str(os.getuid()), '-x', 'fcitx5'],
                          capture_output=True, text=True).stdout.split()
    for pid in pids:
        try:
            for raw in Path('/proc', pid, 'environ').read_bytes().split(b'\0'):
                k, _, v = raw.decode(errors='replace').partition('=')
                if k in allowed:
                    env[k] = v
        except (OSError, ValueError):
            continue
        break
    if not env.get('DBUS_SESSION_BUS_ADDRESS'):
        raise RuntimeError('未找到桌面会话，请在桌面终端运行此脚本。')
    return env

def stop(env):
    subprocess.run(['/usr/bin/fcitx5-remote', '-e'], env=env, check=True, timeout=10)
    for _ in range(50):
        if subprocess.run(['pgrep', '-u', str(os.getuid()), '-x', 'fcitx5'],
                          capture_output=True).returncode != 0:
            return
        time.sleep(0.1)
    raise RuntimeError('原输入法未退出，配置尚未修改。')

def restart(home, env=None):
    if env is None: env = session_environment()
    log = home / '.local/share/daily-pinyin/session.log'
    log.parent.mkdir(parents=True, exist_ok=True)
    # Let the desktop's user manager spawn Fcitx. Starting it directly from
    # this tool can inherit its AppArmor label, which Snap clients reject.
    command = ['systemd-run', '--user', '--collect',
               '--unit=daily-pinyin-' + str(time.monotonic_ns()),
               '--property=Type=exec',
               '--property=StandardOutput=append:' + str(log),
               '--property=StandardError=inherit']
    for name in ['DISPLAY', 'WAYLAND_DISPLAY', 'XDG_RUNTIME_DIR',
                 'DBUS_SESSION_BUS_ADDRESS', 'XAUTHORITY', 'XDG_CURRENT_DESKTOP',
                 'XDG_SESSION_TYPE', 'GTK_IM_MODULE', 'QT_IM_MODULE', 'XMODIFIERS']:
        if name in env: command.append('--setenv=' + name + '=' + env[name])
    command.extend(['/usr/bin/fcitx5', '-D'])
    subprocess.run(command, env=env, check=True, timeout=15,
                   stdin=subprocess.DEVNULL, capture_output=True, text=True)

def main():
    ap = argparse.ArgumentParser(description='安装日用拼音（无需 sudo）')
    ap.add_argument('--home', type=Path, default=Path.home())
    ap.add_argument('--no-restart', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    home = args.home.resolve()
    if not (ROOT / 'payload/runtime/lib/librime.so.1').exists():
        raise SystemExit('缺少运行库，请从 GitHub Releases 下载具名离线安装包；Source code 压缩包不能直接安装。')
    if not (ROOT / 'payload/rime/build/wanxiang.table.bin').is_file():
        raise SystemExit('词库尚未编译完成，不能安装。')
    if args.dry_run:
        print(json.dumps({'home': str(home), 'targets': TARGETS}, ensure_ascii=False, indent=2))
        return
    env = None
    if not args.no_restart:
        env = session_environment()
        stop(env)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup = home / '.local/share/daily-pinyin/backups' / stamp
    backup.mkdir(parents=True)
    exists = []
    for rel in TARGETS:
        src = home / rel
        if src.exists():
            exists.append(rel)
            copy_path(src, backup / rel)
    (backup / 'manifest.json').write_text(json.dumps(
        {'home': str(home), 'targets': TARGETS, 'existed': exists},
        ensure_ascii=False, indent=2), encoding='utf-8')
    try:
        prefix = home / '.local/lib/daily-pinyin'
        copy_path(ROOT / 'payload/runtime', prefix)
        copy_path(ROOT / 'payload/rime', home / '.local/share/fcitx5/rime')
        copy_path(ROOT / 'payload/theme/fluent-light',
                  home / '.local/share/fcitx5/themes/fluent-light')
        copy_path(ROOT / 'payload/classicui.conf',
                  home / '.config/fcitx5/conf/classicui.conf')
        addon = read_ini(ROOT / 'payload/rime-addon.conf')
        addon['Addon']['Library'] = 'export:' + str(prefix / 'fcitx5/librime')
        write_ini(home / '.local/share/fcitx5/addon/rime.conf', addon)
        clipboard_addon = read_ini(ROOT / 'payload/clipboard-addon.conf')
        clipboard_addon['Addon']['Library'] = str(prefix / 'fcitx5/libclipboard')
        write_ini(home / '.local/share/fcitx5/addon/clipboard.conf', clipboard_addon)
        im = read_ini(ROOT / 'payload/rime-inputmethod.conf')
        im['InputMethod'].update({'Name': '日用拼音', 'Name[zh_CN]': '日用拼音',
                                  'Label': '中', 'LangCode': 'zh_CN'})
        write_ini(home / '.local/share/fcitx5/inputmethod/rime.conf', im)

        path = home / '.config/fcitx5/config'
        conf = read_ini(path)
        for section in ['Hotkey', 'Behavior', 'Hotkey/AltTriggerKeys']:
            if section not in conf: conf.add_section(section)
        conf['Hotkey']['EnumerateWithTriggerKeys'] = 'False'
        shifts = [v for v in conf['Hotkey/AltTriggerKeys'].values()
                  if v not in {'Shift_L', 'Shift_R'}]
        conf['Hotkey/AltTriggerKeys'].clear()
        conf['Hotkey/AltTriggerKeys'].update({str(i): v for i, v in enumerate(shifts)})
        conf['Behavior'].update({'ActiveByDefault': 'True', 'DefaultPageSize': '5',
                                'AllowInputMethodForPassword': 'False'})
        write_ini(path, conf)

        path = home / '.config/fcitx5/profile'
        profile = read_ini(path)
        group = 'Groups/0'
        if group not in profile: profile.add_section(group)
        profile[group].update({'Name': profile[group].get('Name', '默认'),
                               'Default Layout': 'us', 'DefaultIM': 'rime'})
        methods = ['keyboard-us', 'rime']
        for s in profile.sections():
            if s.startswith(group + '/Items/'):
                name = profile[s].get('Name')
                if name and name not in methods: methods.append(name)
        for s in list(profile.sections()):
            if s.startswith(group + '/Items/'): profile.remove_section(s)
        for i, name in enumerate(methods):
            profile[f'{group}/Items/{i}'] = {'Name': name, 'Layout': ''}
        if 'GroupOrder' not in profile: profile['GroupOrder'] = {'0': profile[group]['Name']}
        write_ini(path, profile)
        state = home / '.local/share/daily-pinyin/latest-backup'
        state.write_text(str(backup), encoding='utf-8')
        if not args.no_restart: restart(home, env)
    except Exception:
        print('安装未完成，备份位于：' + str(backup), file=sys.stderr)
        raise
    print('日用拼音已安装。备份：' + str(backup))

if __name__ == '__main__':
    main()
