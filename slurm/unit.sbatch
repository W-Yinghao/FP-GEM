#!/bin/bash
#SBATCH --partition=A40,V100,V100-32GB,V100-16GB,A100,L40S,H100
#SBATCH --exclude=node54
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=64G
#SBATCH --time=1-00:00:00
#SBATCH --output=/home/infres/yinwang/fpgem_store/logs/%x-%j.out
#SBATCH --error=/home/infres/yinwang/fpgem_store/logs/%x-%j.err
set -euo pipefail
: "${FPGEM_REPO:?}" "${FPGEM_STORE:?}" "${FPGEM_WAVE:?}" "${FPGEM_UNIT:?}" "${FPGEM_LAUNCH_SHA:?}"
cd "$FPGEM_REPO"
[ "$(git rev-parse HEAD)" = "$FPGEM_LAUNCH_SHA" ] || { echo "FATAL: HEAD moved" >&2; exit 3; }   # stale-code guard
export PYTHONPATH="$FPGEM_REPO" PYTHONUNBUFFERED=1 PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-6}" MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK:-6}"
export CUBLAS_WORKSPACE_CONFIG=:4096:8
export _MNE_FAKE_HOME_DIR="/tmp/mne_home_${SLURM_JOB_ID}"; mkdir -p "$_MNE_FAKE_HOME_DIR/.mne"
PY=/home/infres/yinwang/anaconda3/envs/icml/bin/python
DONE="$FPGEM_STORE/runs/$FPGEM_WAVE/$FPGEM_UNIT/DONE.json"
if [ -s "$DONE" ]; then echo "SKIP $FPGEM_UNIT"; exit 0; fi
echo "host=$(hostname) job=${SLURM_JOB_ID} unit=$FPGEM_UNIT sha=${FPGEM_LAUNCH_SHA:0:12}"
"$PY" -c "import torch; x=torch.ones(8,device='cuda'); (x@x).item(); print('gpu', torch.cuda.get_device_name(0))" \
  || { echo "FATAL: CUDA kernel test failed on $(hostname)" >&2; exit 4; }
"$PY" -m scripts.run_unit --wave "$FPGEM_WAVE" --unit "$FPGEM_UNIT"
