#!/bin/bash

# Buscar el PID del proceso que está ejecutando la aplicación Flask  
PID=$(pgrep -f "python3 -u server.py")

if [ -z "$PID" ]; then  
    echo "No se encontró ningún servidor Flask en ejecución."
else  
    # Terminar el proceso  
    kill $PID  
    echo "Servidor Flask detenido. PID: $PID"
fi
