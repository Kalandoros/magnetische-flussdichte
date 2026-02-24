::@ ECHO OFF
:: Die folgende Zeile wird nur gebraucht wenn Miniconda anstelle von Anaconda verwendet wird.
:: call C:\Users\%USERNAME%\miniconda3\Scripts\activate.bat
call C:\Users\%USERNAME%\anaconda3\Scripts\activate.bat
call cd %~dp0
call conda activate Taipy
call cd \

:: Die folgenden 2 Zeilen werden nur gebraucht wenn unbedingt der absolute Pfad erforderlich ist.
:: 
:: call chdir Users\%USERNAME%
call cd %~dp0
call python main.py