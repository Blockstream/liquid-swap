virtualenv venvfbs
%cd%\venvfbs\Scripts\pip install -r %cd%\tools\fbs\requirements.txt  || echo ERRORFBS && exit /b 1
%cd%\venvfbs\Scripts\pip install . || echo ERRORSINSTALL && exit /b 1
call %cd%\tools\fbs\setup.bat || echo ERRORSETUP && exit /b 1
%cd%\venvfbs\Scripts\fbs freeze || echo ERRORFREEZE && exit /b 1
%cd%\venvfbs\Scripts\fbs installer || echo ERRORINSTALLER && exit /b 1
