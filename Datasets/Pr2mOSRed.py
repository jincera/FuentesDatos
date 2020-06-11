#!/usr/bin/python3
import sys
acumulados = 0
MOSAnt = None

for line in sys.stdin:
    DataIn = line.strip().split("\t")
    if len(DataIn) != 2:
        # Hay algo raro, ignora esta linea
        continue

    esteMOS, esteValor  = DataIn

    if MOSAnt and MOSAnt!= esteMOS:
        print (MOSAnt, "\t", acumulados)
        MOSAnt = esteMOS;
        acumulados = 0

    MOSAnt = esteMOS
    acumulados += 1

if MOSAnt!= None:
    print (MOSAnt, "\t", acumulados)
