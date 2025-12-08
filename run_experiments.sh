#!/usr/bin/env bash
set -e

OUTDIR=~/Downloads/swim_results
mkdir -p "$OUTDIR"

NODES_LIST=(50 100)
FANOUT_LIST=(10 5 3)
LOSS_LIST=(0.1 0.5)

for nodes in "${NODES_LIST[@]}"; do
  for fan in "${FANOUT_LIST[@]}"; do
    for loss in "${LOSS_LIST[@]}"; do

      LOSS_INT=$(echo $loss | awk '{print int($1*100)}')

      subdir="${OUTDIR}/nodes${nodes}_fan${fan}_loss${LOSS_INT}"
      mkdir -p "$subdir"

      echo "Running nodes=$nodes fanout=$fan loss=$loss -> $subdir"

      # запуск симуляции
      python3 ~/Downloads/swim_sim.py \
        --nodes $nodes \
        --fanout $fan \
        --loss $loss \
        --interval 0.1 \
        --runs 30 \
        --max-time 120 \
        --outdir "$subdir" \
        --processes 4

      # ПОИСК настоящего CSV
      CSV_FILE=$(ls "$subdir"/swim_nodes*.csv | head -n 1)

      echo "Found CSV: $CSV_FILE"

      # запуск анализа
      python3 ~/Downloads/analyze.py \
        --csv "$CSV_FILE" \
        --outdir "$subdir"

    done
  done
done

echo "✅ All experiments finished. Results are in $OUTDIR"
