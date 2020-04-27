#!/bin/bash
ttyd/ttyd -p 8580 -i lo bash & sudo websockify/run 6080 --token-plugin JWTTokenApi & python3 hypervisor/manage.py runserver & python3 docker-console/TerminalSocket.py
