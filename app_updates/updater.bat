@echo off
echo Iniciando proceso de actualizacion. NO CIERRE esta ventana.
timeout /t 3 /nobreak > nul

:: 1. Define los nombres de los archivos
:: Nombre del .exe que se va a reemplazar (nombre_de_tu_app.exe)
set "OLD_EXE=PDD_MER.exe"
:: Nombre del .exe descargado del Release (app_new.exe)
set "NEW_EXE=PDD_MER_new.exe"
set "BAT_FILE=updater.bat"

echo Intentando eliminar el archivo antiguo...

:: 2. Intentar eliminar el ejecutable viejo 
del "%OLD_EXE%"

:: 3. Verificar si la eliminacion fue exitosa
if not exist "%OLD_EXE%" (
    echo Reemplazando el ejecutable...
    :: Renombrar el nuevo archivo al nombre del viejo
    rename "%NEW_EXE%" "%OLD_EXE%"
    echo Lanzando la nueva version...
    :: Iniciar la nueva aplicacion
    start "" "%OLD_EXE%"
) else (
    echo.
    echo ERROR CRITICO: No se pudo eliminar el ejecutable anterior (%OLD_EXE%).
    pause
)

:: 4. Autodestruccion: Eliminar el script .bat temporal
del "%BAT_FILE%"

:: Salir
exit
