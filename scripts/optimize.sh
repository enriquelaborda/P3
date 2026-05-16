#!/bin/bash

# Este script iterará sobre diferentes parámetros de pot, r1norm y rmaxnorm
# y guardará los resultados de error usando pitch_evaluate.

DB_TRAIN="pitch_db/train"
EST_DIR="${DB_TRAIN}/est"
REF_DIR="${DB_TRAIN}/ref"

# Crear directorio para estimaciones si no existe
mkdir -p "$EST_DIR"

# Parámetros a probar (ejemplo inicial)
POTS=(-50)
R1NORMS=(0.4 0.5 0.6)
RMAXNORMS=(0.3 0.4 0.5)

echo "Iniciando optimización de parámetros..."

best_score=0
best_params=""

for p in "${POTS[@]}"; do
    for r1 in "${R1NORMS[@]}"; do
        for rmax in "${RMAXNORMS[@]}"; do
            echo "Evaluando: --pot $p --r1norm $r1 --rmaxnorm $rmax"
            
            # Generar estimaciones
            for wav in ${DB_TRAIN}/*.wav; do
                base=$(basename "$wav" .wav)
                ~/PAV/bin/get_pitch --pot "$p" --r1norm "$r1" --rmaxnorm "$rmax" "$wav" "${DB_TRAIN}/${base}.f0" > /dev/null 2>&1
            done
            
            # Evaluar
            # pitch_evaluate devuelve un texto con los errores. 
            # El Score suele aparecer al final.
            output=$(~/PAV/bin/pitch_evaluate ${DB_TRAIN}/*.f0ref)
            
            # Mostrar el resultado (opcionalmente podemos filtrar para ver solo TOTAL)
            total_line=$(echo "$output" | grep -i "TOTAL")
            echo "$total_line"
            
        done
    done
done

echo "Optimización completada."
