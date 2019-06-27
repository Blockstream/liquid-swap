mkdir src\main\python
mkdir src\main\icons\base
mkdir src\build\settings

xcopy tools\fbs\base.json src\build\settings\
xcopy tools\fbs\main.py src\main\python\

%cd%\venvfbs\Scripts\python tools\fbs\set_version.py

set ICON=liquidswap\gui\ui\icons\app-icon.png
set ICON_FOLDER=src\main\icons\

convert -alpha on -resize x16 %ICON% %ICON_FOLDER%Icon.ico

convert -alpha on -resize x16 %ICON% %ICON_FOLDER%base\16.png
convert -alpha on -resize x24 %ICON% %ICON_FOLDER%base\24.png
convert -alpha on -resize x32 %ICON% %ICON_FOLDER%base\32.png
convert -alpha on -resize x48 %ICON% %ICON_FOLDER%base\48.png
convert -alpha on -resize x64 %ICON% %ICON_FOLDER%base\64.png
