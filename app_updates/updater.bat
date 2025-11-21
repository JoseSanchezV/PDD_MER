@echo off
echo Iniciando proceso de actualizacion. NO CIERRE esta ventana.
timeout /t 3 /nobreak > nul

:: 1. Define los nombres de los archivos
:: **ASEGURATE que OLD_EXE coincida con NOMBRE_EXE_PRINCIPAL en Python**
set "OLD_EXE=nombre_de_tu_app.exe"
:: **ASEGURATE que NEW_EXE coincida con NOMBRE_EXE_TEMPORAL en Python**
set "NEW_EXE=app_new.exe"
set "BAT_FILE=updater.bat"

echo Intentando eliminar el archivo antiguo...

:: 2. Intentar eliminar el ejecutable viejo (liberado por Python)
del "%OLD_EXE%"

:: 3. Verificar si la eliminacion fue exitosa
if not exist "%OLD_EXE%" (
    echo Reemplazando el ejecutable...
    :: Mover/Renombrar el nuevo archivo al nombre del viejo
    rename "%NEW_EXE%" "%OLD_EXE%"
    echo Lanzando la nueva version...
    :: Iniciar la nueva aplicacion y continuar
    start "" "%OLD_EXE%"
) else (
    echo.
    echo ERROR CRITICO: No se pudo eliminar el ejecutable anterior (%OLD_EXE%).
    echo Por favor, cierre todos los procesos relacionados y reinicie la aplicacion.
    pause
)

:: 4. Autodestruccion: Eliminar el script .bat temporal
del "%BAT_FILE%"

:: Salir
exit
