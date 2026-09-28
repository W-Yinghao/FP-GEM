#!/bin/bash
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=64G
#SBATCH --time=1-00:00:00
#SBATCH --requeue
# usage: FPGEM_REPO=<launch worktree> sbatch -p V100,V100-32GB,V100-16GB --qos=runfill -J fpg-W2-s4-k slurm/w2_gpu.sbatch <study> <wave> <unit...>
set -euo pipefail
: "${FPGEM_REPO:?}"
cd "$FPGEM_REPO"
export PYTHONPATH="$FPGEM_REPO" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 CUBLAS_WORKSPACE_CONFIG=:4096:8
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-6}" MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK:-6}"
/home/infres/yinwang/anaconda3/envs/icml/bin/python -m scripts.run_w2 --study "$1" --wave "$2" --unit "${@:3}"
