from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
theme = ROOT / 'payload/theme/fluent-light'
theme.mkdir(parents=True, exist_ok=True)

# Nine-slice assets: fixed corners keep the radius and shadow at any width.
size = 64
shadow = Image.new('RGBA', (size, size))
draw = ImageDraw.Draw(shadow)
draw.rounded_rectangle((8, 9, 55, 56), radius=8, fill=(0, 0, 0, 36))
shadow = shadow.filter(ImageFilter.GaussianBlur(3))
draw = ImageDraw.Draw(shadow)
draw.rounded_rectangle((8, 6, 55, 53), radius=8,
                       fill='#ffffff', outline='#dedede', width=1)
shadow.save(theme / 'panel.png')

tile = Image.new('RGBA', (24, 24))
ImageDraw.Draw(tile).rounded_rectangle((0, 0, 23, 23), radius=4, fill='#e7f1fb')
tile.save(theme / 'highlight.png')

for name, points in [('prev', [(11, 5), (7, 9), (11, 13)]),
                     ('next', [(7, 5), (11, 9), (7, 13)])]:
    img = Image.new('RGBA', (18, 18))
    ImageDraw.Draw(img).line(points, fill='#7a7a7a', width=2)
    img.save(theme / (name + '.png'))

(theme / 'theme.conf').write_text('''[Metadata]
Name=Fluent Light
Name[zh_CN]=微软风格·浅色
Version=1
Author=Daily Pinyin
Description=Clean white candidate panel with blue accents
ScaleWithDPI=True

[InputPanel]
NormalColor=#202020
HighlightColor=#ffffff
HighlightBackgroundColor=#0078d4
HighlightCandidateColor=#0067c0
FullWidthHighlight=False
PageButtonAlignment=Last Candidate

[InputPanel/TextMargin]
Left=8
Right=8
Top=7
Bottom=7

[InputPanel/ContentMargin]
Left=13
Right=13
Top=9
Bottom=11

[InputPanel/Background]
Image=panel.png

[InputPanel/Background/Margin]
Left=18
Right=18
Top=16
Bottom=20

[InputPanel/ShadowMargin]
Left=8
Right=8
Top=6
Bottom=10

[InputPanel/Highlight]
Image=highlight.png

[InputPanel/Highlight/Margin]
Left=4
Right=4
Top=4
Bottom=4

[InputPanel/PrevPage]
Image=prev.png

[InputPanel/PrevPage/ClickMargin]
Left=3
Right=3
Top=7
Bottom=7

[InputPanel/NextPage]
Image=next.png

[InputPanel/NextPage/ClickMargin]
Left=3
Right=3
Top=7
Bottom=7

[Menu]
NormalColor=#202020
HighlightCandidateColor=#0067c0
Spacing=3

[Menu/Background]
Image=panel.png

[Menu/Background/Margin]
Left=18
Right=18
Top=16
Bottom=20

[Menu/ContentMargin]
Left=12
Right=12
Top=10
Bottom=12

[Menu/TextMargin]
Left=8
Right=8
Top=6
Bottom=6

[Menu/Highlight]
Image=highlight.png

[Menu/Highlight/Margin]
Left=4
Right=4
Top=4
Bottom=4

[Menu/Separator]
Color=#e8e8e8
''', encoding='utf-8')

(ROOT / 'payload/classicui.conf').write_text('''Vertical Candidate List=False
WheelForPaging=True
Font=Noto Sans CJK SC 11
MenuFont=Noto Sans CJK SC 10
TrayFont=Noto Sans CJK SC 10
PreferTextIcon=True
Theme=fluent-light
DarkTheme=fluent-light
UseDarkTheme=False
UseAccentColor=False
UseInputMethodLanguageToDisplayText=True
''', encoding='utf-8')
print(theme)
