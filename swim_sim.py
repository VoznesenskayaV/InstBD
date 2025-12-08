#!/usr/bin/env python3
"""
swim_sim.py
Простой синхронный симулятор «эпидемической» рассылки (SWIM-like).
Вызывается с аргументами CLI; сохраняет CSV с результатами (t, run, aware_fraction).
"""
import argparse
import os
import random
import math
import csv
from multiprocessing import Pool
import numpy as np

def simulate_one(run_id, nodes, fanout, loss, interval, max_steps):
    # nodes: число узлов
    # fanout: сколько случайных соседей шлёт каждый осведомлённый узел в шаг
    # loss: доля потерь пакетов (0..1)
    # interval: временной шаг (s) — в csv будем записывать время = step * interval
    # max_steps: максимум шагов симуляции

    # Состояние: известность события (True/False) у каждого узла
    aware = [False] * nodes
    # выбираем источник: узел 0
    aware[0] = True

    time_series = []
    # на каждом шаге каждый aware-узел выбирает fanout уникальных случайных получателей (не себя)
    for step in range(max_steps):
        # считаем текущую aware-фракцию
        aware_fraction = sum(1 for x in aware if x) / nodes
        time_series.append((step * interval, run_id, aware_fraction))
        if aware_fraction >= 1.0:
            break

        # сбор входящих оповещений — отмечаем тех, кто получит сообщение
        new_awareness = [False] * nodes

        # каждый aware узел шлёт fanout сообщений
        for i in range(nodes):
            if not aware[i]:
                continue
            # выбираем получателей (без повторов)
            targets = set()
            # если fanout >= nodes-1, шлём всем остальным
            possible = list(range(nodes))
            possible.remove(i)
            if fanout >= (nodes - 1):
                targets = set(possible)
            else:
                while len(targets) < min(fanout, nodes - 1):
                    targets.add(random.choice(possible))

            # отправляем сообщения с вероятностью потери
            for t in targets:
                if random.random() < (1.0 - loss):
                    # сообщение дошло
                    new_awareness[t] = True

        # обновляем aware: те кто уже знали или получили новое сообщение
        for i in range(nodes):
            if new_awareness[i]:
                aware[i] = True

    return time_series

def run_serial_or_parallel(args):
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    runs = args.runs

    # параметры для метаданных
    meta = {
        'nodes': args.nodes,
        'fanout': args.fanout,
        'loss': args.loss,
        'interval': args.interval,
        'runs': runs
    }
    # CSV имя
    csv_path = os.path.join(outdir, f"swim_nodes{args.nodes}_fan{args.fanout}_loss{int(args.loss*100)}.csv")

    max_steps = int(args.max_time / args.interval)

    # подготовка аргументов для прогонов
    jobs = [(rid, args.nodes, args.fanout, args.loss, args.interval, max_steps) for rid in range(runs)]

    # используем Pool
    if args.processes > 1:
        with Pool(processes=args.processes) as p:
            results = p.starmap(simulate_one, jobs)
    else:
        results = [simulate_one(*job) for job in jobs]

    # Записываем результаты в CSV: колонки time, run, aware_fraction
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['time', 'run', 'aware_fraction'])
        for run_series in results:
            for (t, run_id, fraction) in run_series:
                writer.writerow([t, run_id, fraction])

    print("Saved:", csv_path)
    # сохраняем мета-инфо
    with open(os.path.join(outdir, "meta.txt"), "w") as mf:
        for k,v in meta.items():
            mf.write(f"{k}={v}\n")
    return csv_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SWIM-like gossip simulator")
    parser.add_argument("--nodes", type=int, default=50)
    parser.add_argument("--fanout", type=int, default=5)
    parser.add_argument("--loss", type=float, default=0.1, help="packet loss fraction 0..1")
    parser.add_argument("--interval", type=float, default=0.1, help="gossip interval seconds")
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--max-time", type=float, default=60.0, help="max sim time seconds")
    parser.add_argument("--outdir", type=str, default="swim_results")
    parser.add_argument("--processes", type=int, default=4)
    args = parser.parse_args()
    run_serial_or_parallel(args)
