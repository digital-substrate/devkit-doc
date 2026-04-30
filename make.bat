@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=build

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://www.sphinx-doc.org/
	exit /b 1
)

if "%DOC_VERSION%" == "" set DOC_VERSION=1.2

if "%1" == "" goto help
if "%1" == "notebooklm" goto notebooklm
if "%1" == "distzip" goto distzip
if "%1" == "check" goto check

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:check
%SPHINXBUILD% -M doctest %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
if errorlevel 1 goto end
%SPHINXBUILD% -M linkcheck %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
if errorlevel 1 goto end
%SPHINXBUILD% -M coverage %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
if errorlevel 1 goto end
echo all checks passed
goto end

:notebooklm
set SOURCE_DIR=%SOURCEDIR%
set BUILD_DIR=%BUILDDIR%
python tools\build_notebooklm.py
goto end

:distzip
%SPHINXBUILD% -M html %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
if errorlevel 1 goto end
if not exist "%BUILDDIR%\dist" mkdir "%BUILDDIR%\dist"
if exist "%BUILDDIR%\dist\devkit-%DOC_VERSION%-doc.zip" del "%BUILDDIR%\dist\devkit-%DOC_VERSION%-doc.zip"
powershell -Command "Compress-Archive -Path '%BUILDDIR%\html' -DestinationPath '%BUILDDIR%\dist\devkit-%DOC_VERSION%-doc.zip'"
echo wrote %BUILDDIR%\dist\devkit-%DOC_VERSION%-doc.zip
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
