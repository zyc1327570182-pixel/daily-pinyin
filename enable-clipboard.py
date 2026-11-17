#!/usr/bin/env python3
"""Enable Fcitx5 clipboard history and release GNOME's Win+V binding."""
import argparse,datetime,json,os,tempfile
from pathlib import Path
from install import session_environment

CONFIG='fcitx://config/addon/clipboard'

def main():
    ap=argparse.ArgumentParser(description='启用 Win+V 剪贴板历史；--restore 撤销最近一次设置')
    ap.add_argument('--restore',action='store_true');args=ap.parse_args()
    os.environ.update(session_environment())
    # dconf's cache is disposable; do not depend on a launcher's cache permissions.
    with tempfile.TemporaryDirectory(prefix='daily-pinyin-dconf-') as cache:
        os.environ['XDG_CACHE_HOME']=cache
        from gi.repository import Gio,GLib
        bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
        def call(method,signature,args):
            return bus.call_sync('org.fcitx.Fcitx5','/controller','org.fcitx.Fcitx.Controller1',method,GLib.Variant(signature,args),None,Gio.DBusCallFlags.NO_AUTO_START,10000,None).unpack()
        def variant(value):
            if isinstance(value,dict):return GLib.Variant('a{sv}',{k:variant(v) for k,v in value.items()})
            return GLib.Variant('s',str(value))
        old=call('GetConfig','(s)',(CONFIG,))[0]
        settings=None;shell_keys=None
        schema=Gio.SettingsSchemaSource.get_default().lookup('org.gnome.shell.keybindings',True)
        if schema and 'GNOME' in os.environ.get('XDG_CURRENT_DESKTOP','').upper():
            settings=Gio.Settings.new_full(schema,None,None);shell_keys=settings.get_strv('toggle-message-tray')
        state=Path.home()/'.local/share/daily-pinyin';state.mkdir(parents=True,exist_ok=True)
        pointer=state/'latest-clipboard-backup'
        if args.restore:
            saved=json.loads(Path(pointer.read_text()).read_text())
            call('SetConfig','(sv)',(CONFIG,variant(saved['fcitx'])))
            if settings is not None and saved['shell_keys'] is not None:
                if not settings.set_strv('toggle-message-tray',saved['shell_keys']):raise RuntimeError('无法恢复桌面快捷键。')
                Gio.Settings.sync()
            print('已恢复之前的剪贴板快捷键设置。');return
        backup=state/'clipboard-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup.parent.mkdir(parents=True,exist_ok=True)
        backup.write_text(json.dumps({'fcitx':old,'shell_keys':shell_keys},ensure_ascii=False,indent=2))
        config=dict(old);keys=config.get('TriggerKey')
        keys=list(keys.values()) if isinstance(keys,dict) else []
        keys=list(dict.fromkeys(['Super+V','Control+semicolon']+[k for k in keys if k.lower()!='super+v']))
        config['TriggerKey']={str(i):k for i,k in enumerate(keys)};config['Number of entries']='20'
        try:
            call('SetConfig','(sv)',(CONFIG,variant(config)))
            if settings is not None:
                updated=[k for k in shell_keys if k.lower() not in {'<super>v','<mod4>v'}]
                if not settings.set_strv('toggle-message-tray',updated):raise RuntimeError('无法释放 GNOME 的 Win+V 快捷键。')
                Gio.Settings.sync()
            actual=call('GetConfig','(s)',(CONFIG,))[0]
            if 'Super+V' not in actual['TriggerKey'].values():raise RuntimeError('快捷键未生效。')
            pointer.write_text(str(backup))
        except Exception:
            call('SetConfig','(sv)',(CONFIG,variant(old)))
            if settings is not None:settings.set_strv('toggle-message-tray',shell_keys);Gio.Settings.sync()
            raise
        print('已启用 Win+V 剪贴板历史，保留 Ctrl+; 备用键，最多 20 条。')
        print('在应用输入框中使用；数字选取，Esc 关闭，Backspace/Delete 清空历史。')
        print('仅保存在当前输入法进程内存中，重启后清空；当前版本支持文本。')
        print('撤销：python3 enable-clipboard.py --restore')
if __name__=='__main__':main()
