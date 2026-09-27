#!/usr/bin/env bash
# FP-GEM era cleanup: commands for the owner to run by hand. Claude did NOT run any of these.
# Generated 2026-09-27 from a read-only audit. Every item was checked by a separate skeptic agent
# for unique content (verdicts: sprint0/audit_raw/cleanup_verdicts.json).
#
# Usage:   bash CLEANUP_COMMANDS.sh <section>      e.g.  bash CLEANUP_COMMANDS.sh A1
#          bash CLEANUP_COMMANDS.sh                 (lists sections, does nothing)
# Each section is idempotent-ish and stops on the first error (set -e).
# NEVER run a bare `git worktree prune` (stale ACAR_V* registrations exist).
set -euo pipefail
R=/home/infres/yinwang/CMI_AAAI
H=$R/H2CMI
C=/home/infres/yinwang/.cache/h2cmi_training_caches
Q=$H/CMI_AAAI_qxu/results/h2cmi

# ───────────── Tier A: safe now, nothing to salvage ─────────────

A1() { # C01a: 3 spdim_p6 shard worktrees that never ran (empty status --ignored), ~81M
  for s in cho19_52 lee1_27 lee28_54; do
    git -C $R worktree remove $H/_frozen_shards/CMI_AAAI_spdim_p6_${s}_6a6e5b7
  done
}

A2() { # C01c: 3 P7 Lee shard worktrees, ~144M. All 495 outputs are byte-identical in shard_results_salvaged/p7_w1_repaired.
       # After this, shard_results_salvaged/p7_w1_repaired is the ONLY copy of the 162 Lee P7 bundles -> pin a manifest first.
  (cd $H/shard_results_salvaged/p7_w1_repaired && find . -type f -print0 | sort -z | xargs -0 sha256sum > ../p7_w1_repaired.sha256)
  wc -l $H/shard_results_salvaged/p7_w1_repaired.sha256
  for s in lee00 lee18 lee36; do
    git -C $R worktree remove --force $H/_frozen_shards/CMI_AAAI_p7_${s}_ab93820
  done
}

A3() { # C02: standalone clone .codex_p12_launch_f34cc8b (only superseded smoke job 893416), ~54M. All commits on origin.
  rm -rf $H/.codex_p12_launch_f34cc8b
}

A4() { # C07: P13 launch-snapshot clone repo_7b48813 (checkpoint-gate job only; fleet ran from repo_afa21f2), ~46M
  rm -rf $C/fp_gem_p13/repo_7b48813
}

A5() { # C10: __pycache__ dirs (164 dirs / 726 .pyc, ~17M), never inside .git
  find $H $R/h2cmi $C/fp_gem_p13 $C/regime_analysis_20260728T064406 \
       -name .git -prune -o -type d -name __pycache__ -prune -exec rm -rf {} +
}

A6() { # C12: _TRASH (2.3M). acar/ = blobs in 9e34e09f on origin/acar; oaci report identical to fbe7e8af; rest empty/pyc.
  rm -rf $R/_TRASH
}

A7() { # C15: 10 refs/codex/turn-diffs/* (Codex snapshot trees, not commits; 0 bytes freed until gc)
  git -C $R for-each-ref --format='delete %(refname)' refs/codex/turn-diffs/ | git -C $R update-ref --stdin
  git -C $R for-each-ref refs/codex/ | wc -l   # expect 0
}

# ───────────── Tier B: delete only after the salvage inside the function succeeds ─────────────

B1() { # C01b: 8 spdim_p6 shard worktrees, ~224M. Results already salvaged; 32 SLURM logs (~90K) are unique -> copy first.
  SRC=$H/_frozen_shards; DST=$H/shard_results_salvaged/spdim_w1_seed0/slurm_logs
  mkdir -p "$DST"
  SH="cho19_29 cho30_40 cho41_52 lee01_11 lee12_22 lee23_33 lee34_44 lee45_54"
  for s in $SH; do cp -p "$SRC/CMI_AAAI_spdim_p6_${s}_6a6e5b7/h2cmi/results/review_completion/slurm/logs/"spdim-p6-* "$DST/"; done
  [ "$(ls "$DST" | grep -c spdim-p6-)" -eq 32 ] || { echo "expected 32 logs"; return 1; }
  for s in $SH; do for f in "$SRC/CMI_AAAI_spdim_p6_${s}_6a6e5b7/h2cmi/results/review_completion/slurm/logs/"spdim-p6-*; do
    cmp -s "$f" "$DST/$(basename "$f")" || { echo "MISMATCH $f"; return 1; }; done; done
  (cd "$DST" && sha256sum spdim-p6-* > SHA256SUMS.txt)
  for s in $SH; do git -C $R worktree remove --force $SRC/CMI_AAAI_spdim_p6_${s}_6a6e5b7; done
}

B2() { # C01d: spdim_clean_a8b9368 worktree (HEAD 493f6499), ~34M. 3 of its 32 SLURM logs are unique -> copy all 32 first.
  SRC=$H/_frozen_shards/CMI_AAAI_spdim_clean_a8b9368/h2cmi/results/review_completion/slurm/logs
  DST=$H/shard_results_salvaged/spdim_clean_a8b9368_slurm_logs
  mkdir -p "$DST" && cp -p "$SRC"/* "$DST"/
  for f in "$SRC"/*; do cmp -s "$f" "$DST/$(basename "$f")" || { echo "MISMATCH $f"; return 1; }; done
  (cd "$DST" && sha256sum * > SHA256SUMS.txt)
  git -C $R worktree remove $H/_frozen_shards/CMI_AAAI_spdim_clean_a8b9368 \
    || git -C $R worktree remove --force $H/_frozen_shards/CMI_AAAI_spdim_clean_a8b9368
}

B3() { # C04: qxu sleep_cache/subj*.npz = 20 files byte-identical to p0_sleep_cache (75-subject superset), ~696M.
       # benchmark.json (199 B) is unique -> stays; symlinks keep run_w2_sleep.py's default --cache working.
  for f in $Q/sleep_cache/subj*.npz; do
    [ -L "$f" ] && continue
    cmp -s "$f" "$Q/p0_sleep_cache/$(basename "$f")" || { echo "DIFF/MISSING $f"; return 1; }
  done
  cp -p $Q/sleep_cache/benchmark.json $Q/w2_pre_p0_sleep_cache_benchmark.json
  for f in $Q/sleep_cache/subj*.npz; do
    [ -L "$f" ] && continue
    b=$(basename "$f"); rm -f "$f"; ln -s "$Q/p0_sleep_cache/$b" "$Q/sleep_cache/$b"
  done
}

B4() { # C05: BTTA-DG preprocessed MOABB arrays (X.npy, 2.9G). Regenerable from the datalake via BTTA-DG download_data.py.
       # NOTE: a reviewer asked for a BTTA-DG baseline. Code, checkpoints, tar and patch are KEPT; only data/ goes.
       # RECOMMEND DEFER: this is the only copy and MOABB regeneration may not be byte-exact.
  W=$H/CMI_AAAI_qxu/w1b_external
  (cd $W/BTTA-DG && sha256sum data/*/X.npy data/*/labels.npy data/*/meta.csv > $W/w1b_data_sha256.txt)
  cp -p /home/infres/yinwang/slurm_logs/w1b_download.slurm /home/infres/yinwang/slurm_logs/w1b-download-860163.out $W/ || true
  mkdir -p $W/data_labels_meta
  (cd $W/BTTA-DG/data && cp --parents */labels.npy */meta.csv $W/data_labels_meta/)
  rm -r $W/BTTA-DG/data
}

B5() { # C09: ~/slurm_logs failed-attempt logs: 8,372 byte-identical 'dirty working tree @829d27db' p0w2rep pairs
       # + 2,077 determinism-crash w0p2 pairs (20,898 files, ~180M on NFS). Keeps lists, stat manifest, 4 representative files.
       # The successful p0w2pri_/p0w2sec_/p0w2det_ logs (Table 1 Sleep execution logs) are NOT touched.
  cd /home/infres/yinwang/slurm_logs
  P=_purged_failed_attempts_20260927; mkdir -p $P
  grep -l "refusing to run: dirty working tree at 829d27db7751" p0w2rep_*.err | sort -V > $P/p0w2rep_dirty829d27db_errlist.txt
  grep -l "adaptive_avg_pool2d_backward_cuda does not have a deterministic implementation" w0p2_*.err | sort -V > $P/w0p2_determinism_errlist.txt
  wc -l $P/*.txt   # expect 8372 and 2077
  while IFS= read -r f; do stat -c '%n %s %y' "$f" "${f%.err}.out"; done < <(cat $P/*_errlist.txt) > $P/stat_manifest.txt
  cp -p p0w2rep_0-866863.err p0w2rep_0-866863.out w0p2_bnci001-883831.err w0p2_bnci001-883831.out $P/
  printf 'Representative copies of byte-identical failed-attempt logs purged 2026-09-27. p0w2rep: dirty tree @829d27db, fixed by 9a35cc97. w0p2: determinism crash-loop, fixed by 82e411a8.\n' > $P/README.txt
  cat $P/*_errlist.txt | while IFS= read -r f; do
    case "$f" in p0w2rep_*.err|w0p2_*.err) rm -f -- "$f" "${f%.err}.out";; esac
  done
  ls p0w2rep_*.err | wc -l; ls w0p2_*.err | wc -l   # expect 75 and 47 left
}

B6() { # C13: qxu smoke / superseded-preflight outputs (~2.2M). None backs a paper number. Copy the 4 small files first.
  DEST=$H/shard_results_salvaged/qxu_b1a_v2_smoke_audit; mkdir -p "$DEST"
  cp -p $Q/b1a_hard_identity_preflight_v1_tooeasy.jsonl $Q/b1a_hard_identity_preflight_v1_tooeasy.jsonl.manifest.json \
        $Q/v2_smoke.jsonl $Q/v2_smoke.report.json "$DEST/"
  for f in b1a_hard_identity_preflight_v1_tooeasy.jsonl b1a_hard_identity_preflight_v1_tooeasy.jsonl.manifest.json v2_smoke.jsonl v2_smoke.report.json; do
    cmp -s "$Q/$f" "$DEST/$f" || { echo "MISMATCH $f"; return 1; }; done
  rm -r -- $Q/v2_bundles_smoke
  rm -- $Q/v2_smoke.jsonl $Q/v2_smoke.report.json $Q/p0_w1_smoke.jsonl \
        $Q/b1a_hard_identity_preflight_v1_tooeasy.jsonl $Q/b1a_hard_identity_preflight_v1_tooeasy.jsonl.manifest.json
}

# ───────────── Tier C: DEFER until Sprint-0 re-inference and T1 are closed (listed, not implemented) ─────────────
#  C03  $H/.codex_p12_launch_5b71ee8 (132M)  — every ~/.cache fp_gem_* .slurm is hard-wired to it; runners need a clean tree.
#  C08  $C/fp_gem_p13/repo_afa21f2 (46M)     — launch provenance of the P13 fleet.
#
# ───────────── Optional re-filing (NOT deletion) ─────────────
#  H2CMI/CMI_AAAI_p12_extract (707M) and H2CMI/paper_data are the CMI-Trace "P12 supplement", not FP-GEM P12.
#  ~414 of its tos_cmi/results files exist nowhere else. If you want them under CMITRACE/:
#    git -C $R worktree move $H/CMI_AAAI_p12_extract $R/CMITRACE/CMI_AAAI_p12_extract
#    mv $H/paper_data $R/CMITRACE/p12_paper_data
#
# ───────────── KEEP (only copies of paper-backing or Sprint-0 inputs) ─────────────
#  $Q/p0_sleep_cache (3.1G), p0_w2_bundles/, p0_w2_primary_all.jsonl, p0_w*_all.jsonl, wave0_* raw   (Table 1 Sleep column)
#  $C/fp_gem_p12 (345 TSMNet checkpoints), fp_gem_cho, fp_gem_ea, fp_gem_stage2, fp_gem_stage2_sleep,
#     regime_analysis_20260728T064406, FP_GEM_RESULTS_SO_FAR.md, p8_monolithic_891435_partial_excluded (C11)
#  $H/shard_results_salvaged, $H/CMI_AAAI_qxu (worktree; do NOT update/checkout it — 26 commits behind)
#  branches exp/h2cmi-review-p0-corrections, exp/h2cmi-responsibility-qxu (C14), origin/exp/h2cmi-wave0-mechanism,
#     origin/agent/fp-gem-stage2 (diverged at e6c49156 — neither contains the other)
#  FP-GEM/*.md, *.pdf (C16: no other copy; v2 is hash-pinned by v3)

if [ $# -eq 0 ]; then
  grep -E '^[AB][0-9]\(\) \{' "$0" | sed 's/() {//'
  exit 0
fi
"$1"
