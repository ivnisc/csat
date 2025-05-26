#!/bin/bash

TCP_PORT=54321
UDP_PORT=54322

# cerrar procesos en el puerto TCP
for pid in $(lsof -ti tcp:$TCP_PORT); do
    kill -9 $pid
done

# cerrar procesos en el puerto UDP
for pid in $(lsof -ti udp:$UDP_PORT); do
    kill -9 $pid
done

# verificar si los puertos están libres
echo "Verificando puertos..."
lsof -i tcp:$TCP_PORT
lsof -i udp:$UDP_PORT 