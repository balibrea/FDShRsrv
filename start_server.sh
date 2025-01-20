#!/bin/bash

# Generar un nombre de archivo de log basado en la fecha y hora actuales  
LOG_FILE="logs/app_$(date +'%Y-%m-%d_%H-%M-%S').log"

# Comando para ejecutar tu aplicación Flask  
FLASK_APP="server.py"

# Ejecutar la aplicación en segundo plano y redirigir stdout y stderr al archivo de log  
nohup python3 -u $FLASK_APP >> $LOG_FILE 2>&1 &

# Imprimir el ID del proceso  
echo "La aplicación Flask está corriendo en segundo plano con el PID: $!"
echo "Los registros se guardan en: $LOG_FILE"
