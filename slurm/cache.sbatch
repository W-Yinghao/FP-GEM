#!/bin/bash
#SBATCH --partition=CPU
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=2-00:00:00
#SBATCH --output=/home/infres/yinwang/fpgem_store/logs/%x-%j.out
#SBATCH --error=/home/infres/yinwang/fpgem_store/logs/%x-%j.err
# usage: sbatch -J fpg-cache-<ds>-<k> slurm/cache.sbatch <dataset> <subjects...>
set -euo pipefail
: "${FPGEM_REPO:?}" "${FPGEM_LAUNCH_SHA:?}"
cd "$FPGEM_REPO"
[ "$(git rev-parse HEAD)" = "$FPGEM_LAUNCH_SHA" ] || { echo "FATAL: HEAD moved" >&2; exit 3; }
export PYTHONPATH="$FPGEM_REPO" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-4}" MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK:-4}"
DL=/projects/EEG-foundation-model/datalake/raw
export MNE_DATA="$DL" MNE_DATASETS_BNCI_PATH="$DL" MNE_DATASETS_GIGADB_PATH="$DL"
export _MNE_FAKE_HOME_DIR="/tmp/mne_home_${SLURM_JOB_ID}"; mkdir -p "$_MNE_FAKE_HOME_DIR/.mne"
PY=/home/infres/yinwang/anaconda3/envs/icml/bin/python
echo "host=$(hostname) job=${SLURM_JOB_ID} sha=${FPGEM_LAUNCH_SHA:0:12} args=$*"
"$PY" -m scripts.build_cache --skip-existing --dataset "$1" --subjects "${@:2}"
