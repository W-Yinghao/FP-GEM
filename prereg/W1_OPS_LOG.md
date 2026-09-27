# W1 operations log

| When (CEST) | Event |
|---|---|
| 2026-09-27 11:58 | Fleet launched from commit a97e9d6 (driver `fpg-drv-W1`, cap 8 SLURM tasks incl. the driver); QOS `normal`, partitions A40/V100 family/A100/L40S/H100. |
| 2026-09-27 12:0x | Lee cache rebuild finished; Lee `MANIFEST.json` written by a dependency job. |
| 2026-09-27 15:08 | Owner instruction: submit with QOS `runfill` on V100 partitions only. Driver stopped via STOP flag after 92/657 units; pending units moved with `scontrol update` to QOS `runfill`, partitions V100/V100-32GB/V100-16GB; new driver started with `SBATCH_QOS=runfill`, `SBATCH_PARTITION=V100,V100-32GB,V100-16GB`, `SBATCH_REQUEUE=1` (same launch commit, so completed units still count). `runfill` is preemptible (REQUEUE): a preempted unit restarts from scratch and leaves a `FAILED_<n>.json` (reason `SystemExit`, code 143); its final outputs come from the completed run. |
| 2026-09-27 17:09 | Checked limits: QOS `runfill` allows 10 GPUs per user (no job-count or submit limit), separate from QOS `normal` (8 GPUs, 30 submits per user). With the owner's go, the driver cap was raised from 8 to 11 (10 runfill V100 units + the CPU driver) by restarting the driver with `FPGEM_CAP=11`; 166/657 units were done at that point. |

Each unit's `DONE.json` records the GPU model and host it ran on; bit-exact replays must use the same GPU type.
