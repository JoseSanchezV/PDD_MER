@echo off
title Script de Actualización - PDD_MER
echo Iniciando proceso de actualizacion. NO CIERRE esta ventana.
echo.

:: 1. Define los nombres de los archivos y procesos
set "OLD_EXE=PDD_MER.exe"
set "NEW_EXE=PDD_MER_new.exe"
set "BAT_FILE=updater.bat"

:: 2. Terminar el proceso antiguo si está en ejecución (Soluciona el "Acceso denegado")
echo Intentando cerrar la version anterior de %OLD_EXE%...
taskkill /F /IM "%OLD_EXE%" > nul 2>&1
:: taskkill devuelve un error si el proceso no está corriendo,
:: el > nul 2>&1 suprime este mensaje.
timeout /t 1 /nobreak > nul

:: 3. Intentar eliminar el ejecutable viejo
echo Intentando eliminar el archivo antiguo...
del /F /Q "%OLD_EXE%"

:: 4. Verificar el resultado de la eliminación
if exist "%OLD_EXE%" (
    echo.
    echo ERROR CRITICO: No se pudo eliminar el ejecutable anterior (%OLD_EXE%).
    echo Por favor, cierre %OLD_EXE% manualmente e intente de nuevo.
    pause
    goto :end
)

:: 5. Reemplazo exitoso
echo ✅ Eliminación exitosa.
echo Reemplazando el ejecutable...
rename "%NEW_EXE%" "%OLD_EXE%"

:: 6. Verificar el renombrado
if exist "%OLD_EXE%" (
    echo ✅ Actualización completada.
    echo Lanzando la nueva version...
    start "" "%OLD_EXE%"
) else (
    echo.
    echo ERROR: No se pudo renombrar el archivo %NEW_EXE%.
    pause
)

:: 7. Autodestrucción y Salida
:end
echo.
echo Eliminando script de actualizacion...
del "%BAT_FILE%" > nul 2>&1
exit
