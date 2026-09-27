#!/bin/bash
# FP-GEM self-healing submit driver. CPU-light: git/squeue/sbatch/test only, never compute.
#
# Run ONE driver at a time for the whole project (it owns the 8-task cap):
#   login-safe loop (not a SLURM task, but dies when the Bash host allocation ends):
#     nohup bash slurm/driver.sh W1 configs/units_W1.txt >>/home/infres/yinwang/fpgem_store/logs/driver.log 2>&1 &
#   or as a CPU job (counts as 1 of the 8 because its name starts with fpg- -> at most 7 units in flight):
#     sbatch -p CPU -c 1 --mem=1G --time=4-00:00:00 -J fpg-drv-W1 \
#       -o /home/infres/yinwang/fpgem_store/logs/%x-%j.out -e /home/infres/yinwang/fpgem_store/logs/%x-%j.out \
#       --wrap "bash /home/infres/yinwang/CMI_AAAI/FP-GEM/slurm/driver.sh W1 configs/units_W1.txt"
# Stop cleanly from any node:  touch /home/infres/yinwang/fpgem_store/control/STOP   (or control/STOP_W1)
#   -> no new submissions; in-flight units finish. To also cancel units, by job id only (never ps/kill):
#      squeue -u "$USER" -h -o '%i %j' | awk '$2 ~ /^fpg-W1-/ {print $1}' | xargs -r scancel
set -uo pipefail
WAVE=${1:?usage: fpgem_driver.sh WAVE UNITS_FILE}; UNITS_FILE=${2:?usage: fpgem_driver.sh WAVE UNITS_FILE}
REPO=${FPGEM_REPO:-/home/infres/yinwang/CMI_AAAI/FP-GEM}
STORE=${FPGEM_STORE:-/home/infres/yinwang/fpgem_store}   # NFS; never /tmp (node-local)
CAP=${FPGEM_CAP:-8}            # HARD cap on concurrent fpg-* SLURM tasks (user authorization)
PREFIX=fpg-                    # every job of this project: fpg-<wave>-<unit>, driver job fpg-drv-<wave>
POLL=${FPGEM_POLL:-60}
MAX_ATTEMPTS=${FPGEM_MAX_ATTEMPTS:-3}
UNIT_SBATCH="$REPO/slurm/unit.sbatch"
CTL="$STORE/control"; ATT="$CTL/attempts/$WAVE"
mkdir -p "$STORE/logs" "$ATT" || exit 2
log(){ printf '%s [drv %s] %s\n' "$(date -Is)" "$WAVE" "$*"; }
is_done(){ [ -s "$1" ] && grep -q '"status": "ok"' "$1"; }   # DONE.json written last + atomically by the runner

cd "$REPO" || exit 2
LAUNCH_SHA=$(git rev-parse HEAD) || { log "REFUSE: no commit in $REPO"; exit 2; }
[ -z "$(git status --porcelain --untracked-files=no)" ] || { log "REFUSE: tracked changes in $REPO"; exit 2; }
[ -f "$UNIT_SBATCH" ] || { log "REFUSE: missing $UNIT_SBATCH"; exit 2; }
mapfile -t UNITS < <(grep -vE '^[[:space:]]*(#|$)' "$UNITS_FILE"); N=${#UNITS[@]}
[ "$N" -gt 0 ] || { log "REFUSE: empty unit list $UNITS_FILE"; exit 2; }

# single-driver lock: mkdir is atomic on NFS; a lock whose heartbeat is >10 min old is stale (driver was SIGKILLed)
LOCK="$CTL/driver.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  if [ -n "$(find "$CTL/driver.state" -mmin -10 2>/dev/null)" ]; then log "REFUSE: live driver ($(cat "$CTL/driver.state"))"; exit 2; fi
  log "taking over stale lock"
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT
trap 'log "signal -> exit"; exit 143' TERM INT HUP

log "start N=$N CAP=$CAP sha=${LAUNCH_SHA:0:12} host=$(hostname) pid=$$"
while :; do
  if [ -e "$CTL/STOP" ] || [ -e "$CTL/STOP_$WAVE" ]; then log "STOP flag -> exit (in-flight jobs keep running)"; break; fi
  [ "$(git rev-parse HEAD)" = "$LAUNCH_SHA" ] || { log "HEAD moved -> stop submitting"; break; }
  # ONE squeue snapshot per cycle (-r expands arrays). If squeue errors, do NOT treat it as "nothing queued":
  # that is how a driver resubmits duplicates of running units.
  if ! Q=$(squeue -u "$USER" -h -r -o '%j' 2>&1); then log "squeue error: ${Q:0:160}"; sleep "$POLL"; continue; fi
  inflight=$(grep -c "^$PREFIX" <<<"$Q")
  room=$((CAP - inflight)); done_n=0; capped=0; subbed=0
  for u in "${UNITS[@]}"; do
    if is_done "$STORE/runs/$WAVE/$u/DONE.json"; then done_n=$((done_n+1)); continue; fi   # complete
    jn="fpg-$WAVE-$u"
    grep -qxF "$jn" <<<"$Q" && continue                                                   # queued/running
    na=$(cat "$ATT/$u" 2>/dev/null || echo 0)
    if [ "$na" -ge "$MAX_ATTEMPTS" ]; then capped=$((capped+1)); continue; fi              # fail loud: human
    [ "$room" -ge 1 ] || continue
    if jid=$(sbatch --parsable -J "$jn" -o "$STORE/logs/%x-%j.out" -e "$STORE/logs/%x-%j.err" \
          --export=ALL,FPGEM_REPO="$REPO",FPGEM_STORE="$STORE",FPGEM_WAVE="$WAVE",FPGEM_UNIT="$u",FPGEM_LAUNCH_SHA="$LAUNCH_SHA" \
          "$UNIT_SBATCH" 2>&1); then
      echo $((na+1)) >"$ATT/$u"; room=$((room-1)); subbed=$((subbed+1)); Q+=$'\n'"$jn"
      log "submit $jn job=$jid attempt=$((na+1))"
    else
      log "sbatch refused $jn: $(tr '\n' ' ' <<<"$jid" | tail -c 160)"; room=0               # e.g. QOSMaxSubmitJobPerUserLimit
    fi
  done
  pend=$(squeue -u "$USER" -h -o '%j %T %r' 2>/dev/null | awk -v p="^$PREFIX" '$1 ~ p && $2 == "PENDING" {print $3}' | sort | uniq -c | tr -s ' \n' ' ')
  log "done=$done_n/$N inflight=$((inflight+subbed)) submitted=$subbed attempt_capped=$capped pending=[${pend}]"
  printf '{"wave":"%s","done":%d,"n":%d,"inflight":%d,"attempt_capped":%d,"sha":"%s","host":"%s","pid":%d,"ts":"%s"}\n' \
    "$WAVE" "$done_n" "$N" "$((inflight+subbed))" "$capped" "$LAUNCH_SHA" "$(hostname)" "$$" "$(date -Is)" \
    >"$CTL/driver.state.tmp" && mv -f "$CTL/driver.state.tmp" "$CTL/driver.state"
  [ "$done_n" -ge "$N" ] && { log "ALL $N DONE"; break; }
  if [ $((done_n + capped)) -ge "$N" ] && ! grep -q "^fpg-$WAVE-" <<<"$Q"; then
    log "only attempt-capped units remain ($capped) -> exit for human review"; break
  fi
  sleep "$POLL"
done
