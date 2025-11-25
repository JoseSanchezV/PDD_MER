@echo off
title Script de Actualización - PDD_MER
echo Iniciando proceso de actualizacion. NO CIERRE esta ventana.
echo.

:: 1. Define los nombres de los archivos
set "OLD_EXE=PDD_MER.exe"
set "NEW_EXE=PDD_MER_new.exe"
set "BAT_FILE=updater.bat"

:: 2. Terminar el proceso antiguo si está en ejecución (Soluciona "Acceso denegado")
echo Intentando cerrar la version anterior de %OLD_EXE%...
taskkill /F /IM "%OLD_EXE%" > nul 2>&1
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
    goto :end_cleanup_fail
)

:: 5. Reemplazo exitoso
echo ✅ Eliminación exitosa.
echo Reemplazando el ejecutable...
rename "%NEW_EXE%" "%OLD_EXE%"

:: 6. Verificar el renombrado
if not exist "%OLD_EXE%" (
    echo.
    echo ERROR CRITICO: No se pudo renombrar el archivo %NEW_EXE% a %OLD_EXE%.
    echo El archivo %NEW_EXE% se mantuvo con el nombre temporal.
    pause
    goto :end_cleanup_fail
)

echo ✅ Actualización completada.
echo Lanzando la nueva version...
start "" "%OLD_EXE%"

:: 7. Autodestrucción (Solución al fallo de borrado del BAT)
:end_cleanup_success
echo.
echo Iniciando autodestruccion del script de actualizacion...
:: Lanza un script temporal en segundo plano para borrar este BAT
echo ping 127.0.0.1 -n 2 > temp_del.bat
echo del "%BAT_FILE%" >> temp_del.bat
start "" cmd /c temp_del.bat
goto :exit_main

:end_cleanup_fail
:: Si fallamos, no podemos autolimpiar confiablemente, dejamos el archivo para revision.
echo.
echo Se mantuvo el script de actualizacion para debugging.

:exit_main
exit
