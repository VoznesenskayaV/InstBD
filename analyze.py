#!/usr/bin/env python3
import argparse
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

def analyze(csv_path, outdir, window_savgol=11):
    df = pd.read_csv(csv_path)

    if df.empty:
        print("CSV пустой, анализ пропущен")
        return

    times = sorted(df['time'].unique())
    runs = sorted(df['run'].unique())

    # матрица time x runs
    mat = np.full((len(times), len(runs)), np.nan)
    time_to_idx = {t:i for i,t in enumerate(times)}
    run_to_idx = {r:i for i,r in enumerate(runs)}

    for _, row in df.iterrows():
        t = row['time']
        r = int(row['run'])
        val = row['aware_fraction']
        mat[time_to_idx[t], run_to_idx[r]] = val

    # заполнение пропусков
    for j in range(mat.shape[1]):
        mat[:, j] = pd.Series(mat[:, j]).ffill().bfill().fillna(0).values

    mean_curve = np.nanmean(mat, axis=1)
    std_curve = np.nanstd(mat, axis=1)

    # ===== УСТОЙЧИВОЕ СГЛАЖИВАНИЕ (исправленный блок) =====

    n = len(mean_curve)

    if n < 5:
        smooth = mean_curve.copy()
    else:
        win = min(window_savgol, n)
        if win % 2 == 0:
            win -= 1
        if win < 5:
            win = 5

        poly = 3
        if poly >= win:
            poly = win - 2

        smooth = savgol_filter(mean_curve, win, poly)

    # ===== расчёт отклонений =====

    dev = np.abs(mean_curve - smooth)
    idx_max = int(np.nanargmax(dev))
    percent_at_max = mean_curve[idx_max] * 100.0
    t_at_max = times[idx_max]
    dev_max = dev[idx_max]

    # ===== функции времени достижения порогов =====

    def time_to_threshold(curve, times, thr):
        for i, v in enumerate(curve):
            if v >= thr:
                return times[i]
        return None

    t10 = time_to_threshold(mean_curve, times, 0.10)
    t50 = time_to_threshold(mean_curve, times, 0.50)
    t90 = time_to_threshold(mean_curve, times, 0.90)
    t99 = time_to_threshold(mean_curve, times, 0.99)

    t_10_90 = (t90 - t10) if (t10 is not None and t90 is not None) else None

    # ===== построение графика =====

    plt.fill_between(times, mean_curve - std_curve, mean_curve + std_curve, alpha=0.2)
    plt.plot(times, mean_curve, label='mean', linewidth=2)
    plt.plot(times, smooth, label='smooth', linewidth=2, linestyle='--')
    plt.scatter([t_at_max], [mean_curve[idx_max]], color='red',
                label=f'max dev at {percent_at_max:.1f}% (t={t_at_max}s)')

    plt.xlabel('time (s)')
    plt.ylabel('aware fraction')
    plt.ylim(-0.02, 1.02)
    plt.legend()
    plt.grid(True)

    os.makedirs(outdir, exist_ok=True)

    base = os.path.splitext(os.path.basename(csv_path))[0]
    png = os.path.join(outdir, base + ".png")
    plt.savefig(png)
    plt.close()

    # ===== сохранение метрик =====

    metrics = {
        'csv': csv_path,
        't_at_max_dev': t_at_max,
        'percent_at_max_dev': percent_at_max,
        'dev_max': dev_max,
        't10': t10,
        't50': t50,
        't90': t90,
        't99': t99,
        't10_90': t_10_90
    }

    metrics_path = os.path.join(outdir, base + "_metrics.txt")
    with open(metrics_path, 'w') as mf:
        for k, v in metrics.items():
            mf.write(f"{k}={v}\n")

    print("✅ Analysis saved:", png, metrics_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--outdir", default="swim_results/analysis")
    args = parser.parse_args()

    analyze(args.csv, args.outdir)
