# FP-GEM Sprint 0 服务器端审计：论文 ↔ 代码 ↔ 结果 对应（T1 初稿 + T3/T4 可行性）

日期：2026-09-27  
范围：`/home/infres/yinwang/CMI_AAAI` 全部内容（只读）+ 本文件夹的 v1–v5、kickoff、投稿 PDF、补充材料、OpenReview 页面。  
方法：55 个子代理并行阅读 → 按论文 14 组数值主张逐项追溯 → 每个不一致由第二个代理对抗复查 → 完整性批评。  
约束：未修改或删除任何已有文件，未 checkout 任何分支，未提交 SLURM，未训练。新文件只写在 `FP-GEM/sprint0/`。

本文件夹内容：

| 文件 | 内容 |
|---|---|
| `T1_manuscript_result_map.csv` | 273 行：论文每个数字/陈述 → 生成代码（分支@commit、文件、行号）→ 结果文件及其中的值 → 状态 |
| `T1_artifact_capability_matrix.csv` | 数据集 × 算子：能否从现有产物重跑（v3 的列定义） |
| `T3_rho_audit_draft.csv` | 每被试/session 的协议计数 → 保留 → 适应/评估计数与 ρ_A、ρ_E |
| `repro/theory/` | 定理与命题的独立 sympy/数值复核脚本与日志 |
| `repro/simulation/` | 只依据论文文字独立重写的高斯仿真，复现 Table S3、Fig 2A 等 |
| `CLEANUP_COMMANDS.sh` | 删除清单（分级、带 salvage 步骤），只由你运行 |
| `audit_raw/` | 各阅读代理的完整报告、每组追溯摘要、删除候选的逐项判定 |

---

## 0. 最重要的结论（先看这里）

1. **FP-GEM 的代码不叫 FP-GEM。** 算法本体是 `h2cmi/tta/class_conditional.py`：
   - FP-GEM = 变体 `gen_iterative_diag`，Joint-GEM = `joint_iterative_diag`。
   - 两者唯一的区别在 `_variant_core` L406：`fixed_prior = pi_S_t if spec.update=="prior_fixed"`，据此跳过先验 M 步（L243-245）。
   - 这个文件在所有 FP-GEM 分支上逐字节相同（git blob 6db965db，sha256 270c8933），最后修改于 15838783（06-21）。
   - 根目录 `h2cmi/` 是更早的 Project-A 版本，**没有** FP-GEM 代码。
2. **论文 Table 1 的 Sleep 列、以及 MI 的 Source/EA/Recenter/SPDIM 各格，都能在服务器上逐格复现。**
3. **MI 三个数据集的 FP-GEM 格，以及 B14 的 Joint-GEM 格，在服务器上没有任何产物能对上**（见 §2.2）：
   - 标准差与产物完全相同，均值却恰好高出 +1.0 或 +2.0。
   - 服务器产物给出的 FP−Joint 是 B14 +0.3、Cho −0.2、Lee +0.3。论文写的是 +1.3、+0.8、+1.3。
   - v1 §2.1 说 FP/Joint "来自更晚的一轮，需向服务器索取"。服务器上**不存在**这一轮：`h2cmi/` 下最后一个提交是 04a40e4e（07-27 17:08），最后一个缓存文件写于 07-28 上午。
   - 你自己 07-28 的汇总 `~/.cache/h2cmi_training_caches/FP_GEM_RESULTS_SO_FAR.md` 列的正是产物值 71.2 / 59.0 / 66.6。
   - 这些数字只能在你笔记本上的 `FP-GEM_AAAI2027/theoryfirst/experiment_results_table.tex` 及其编辑历史里查清来源。`~/.claude/history.jsonl` 第 190 行记录了你 07-28 对这个文件的核对提醒。
4. **论文 §5.2 与补充材料 §H 描述的 EEG 协议，与实际产出 Table 1 的代码有 19 处不一致**（见 §3）。影响最大的五处：
   - B14 实际是 2 类，不是 4 类；
   - MI 用 8–30 Hz、0–2 s，不是 4–38 Hz、0.5–3.5 s；
   - 密度是 Student-t，不是对角高斯；
   - MI 读出用冻结的 TSMNet 线性头，不是密度头，与论文 Eq. 12 相矛盾；
   - Sleep 上 FP-GEM 固定的先验是**均匀先验**，不是 π_src。
5. **理论部分全部独立复核通过**（Thm 1、Prop 2–5、Thm 6、S2–S15）。
   - 高斯仿真的原始代码只在笔记本上。
   - 但只依据论文文字独立重写的实现逐格复现了 Table S3（12/12）、Table S2 的 20 个均值、Fig 2A 的 R²=0.998 / 2,038 fits / 1.37%，以及交叉单元格 0.198 [0.126, 0.270]。
6. **`df47753e` 的冻结证据门已经禁止 MI 上 "FP > Joint" 的主张**：P12 给出 +0.0029 [−0.0003, +0.0062]。修复后的 W1（H2CMI 编码器，密度头读出）是 +0.0030 [+0.0007, +0.0054]，方向为正但只有 0.3 个百分点。

---

## 1. FP-GEM 代码与结果的位置

### 1.1 分支（都在 `origin` 上；两个主分支在 e6c49156 处分叉，**谁也不包含谁，两个都要保留**）

| 分支 @tip | 内容 | 本地状态 |
|---|---|---|
| `origin/exp/h2cmi-wave0-mechanism` @df47753e | P12 结果（3bba1d0b）、P13 先验压力（7b48813e→b5fb5158）、P14 故事冻结 `FINAL_FP_GEM_STORY_FREEZE.md` 与 `FP_GEM_EVIDENCE_HIERARCHY.md`、修复后的 W1 与 P7/P8/P9 SPDIM、Wave0 | 本地分支落后 26 个提交，检出在 `H2CMI/CMI_AAAI_qxu`。**不要在那里 pull 或 checkout** |
| `origin/agent/fp-gem-stage2` @04a40e4e | P12 分析输出（3b52e202）、Stage-2 MLLS 与 shift gate（a39a93a2、1ce61180）、Sleep Stage-2（687003ff、722e33cd，未聚合）、Cho 运行器（4be89b0d）、EA 臂（1b89a32d、ab03bd7a） | 没有本地分支。完整 clone 在 `H2CMI/.codex_p12_launch_5b71ee8` |
| `exp/h2cmi-review-p0-corrections` @5bc9bf07 | REVIEW_P0，即 Sleep 列。原始计算在 278fc85e，报告为 `review_p0.report.json` | 已被上面两个分支完全包含 |
| `exp/h2cmi-responsibility-qxu` @09e92499 | W1/W2 与 W1-B BTTA-DG 复现（e941bb5b） | 已被完全包含 |

### 1.2 运行器与数据加载（在分支上的 `h2cmi/` 目录下）

| 用途 | 文件 |
|---|---|
| B14 和 Lee，TSMNet 六方法（P12） | `run_fp_gem.py` |
| Cho | `run_fp_gem_cho.py` |
| EA | `run_ea_b14_lee.py` |
| P13 | `run_fp_gem_prevalence.py` |
| Stage-2 | `run_fp_gem_stage2.py`、`fp_gem_stage2_lib.py` |
| Sleep | `run_w2_p0.py`、`run_w2_sleep.py`、`eval/p0_eval.py`、`p0_source.py` |
| 数据加载 | MI 用 `data/real_eeg.py`；Sleep 用 `data/sleep_eeg.py` |
| 密度 | `density/student_t_mixture.py` |

### 1.3 不在 git 里、但支撑论文数字的产物（**唯一副本**）

- `~/.cache/h2cmi_training_caches/`：
  - `fp_gem_p12/source_checkpoints`：345 个 TSMNet 模型，P9 的哈希无法复现它们，所以是 MI 唯一的模型；
  - `fp_gem_cho`：Cho 列，没有提交；
  - `fp_gem_ea`：EA 行，没有提交；
  - `fp_gem_stage2`：唯一的逐 trial MI logits；
  - `fp_gem_stage2_sleep`；
  - `fp_gem_p13` 的 units、日志和 gate（其中的 launch clone `repo_7b48813` 可删，`repo_afa21f2` 推迟）；
  - `regime_analysis_20260728T064406`：脚本只在这里；
  - `FP_GEM_RESULTS_SO_FAR.md`。
- `H2CMI/CMI_AAAI_qxu/results/h2cmi/`：
  - `p0_w2_primary_all.jsonl`：Sleep 列的原始行，sha 与已提交的 `p0_raw.sha256` 一致；
  - `p0_w2_bundles/`：225 个冻结的 Sleep 模型；
  - `p0_sleep_cache/`：3.1G，唯一的预处理 Sleep 输入；
  - `wave0_*`。
- `H2CMI/shard_results_salvaged/p7_w1_repaired`：Lee 的 P7 bundles，是修复后 W1 的规范副本。

### 1.4 服务器上**不存在**的东西（只在笔记本上）

以下都不在服务器上：
- `journal_revision/prechecks/*.py`、`fpgem` 包、`convergence_sim`、`multiclass_sim`、`optimal_sim`、`mechanism_sim`、`FP-GEM_AAAI2027/`；
- 论文 .tex 源文件；
- `submission_2026-07-2*/`、`SERVER_REPRO_CHECKLIST_REQUEST.md`；
- OpenReview 上的代码 zip 与 reproducibility checklist；
- v4/v5 提到的"第二份"计划 `Downloads/FP_GEM_major_revision_plan_20260926.md`，以及 `fpgem_v2_math_checks.py`。

### 1.5 父目录里名字相似但与 FP-GEM 无关的东西

- `H2CMI/CMI_AAAI_p12_extract` 和 `H2CMI/paper_data` 是 **CMI-Trace/TOS 的 "P12 补充材料提取"**，与 FP-GEM 的 P12 只是同名。它们放错了目录，应移到 `CMITRACE/`。其中大量 `tos_cmi/results` 文件没有其他副本（阅读代理估计约 414 个，复查代理未独立核实这个数），**不能删**。
- 父目录其余各线（CIGL、CMITRACE、FSR、OACI、CSC、S2P、STAR、TOS、ACAR、PROJECT_B、cedar/talos/tta_mech）都不含 GEM 代码，已 grep 确认。

---

## 2. 论文 ↔ 产物逐项对应（T1 摘要；完整 273 行见 CSV）

| 组 | 论文位置 | 状态 | 说明 |
|---|---|---|---|
| G01 | Thm 1、Prop 2、S1–S6（全局不可辨识） | 13/13 解析正确 | 服务器上没有对应代码，论文也没有声称有 |
| G02 | Thm 6 / S15（O(t⁴)、O(t⁶)、O(t³)） | 全部正确 | 符号推导，加直接 KL 最小化交叉验证 |
| G03 | Prop 3–5、S7–S14、Eq 12 | 理论正确；**Eq 12 在 MI 上 MISMATCH** | MI 运行器读的是 TSMNet 线性头 |
| G04 | Fig 2A、局部响应（R²=0.998） | 服务器无原始代码；**独立重写可复现** | `repro/simulation/local_response_fig2a.py` |
| G05 | Table S2、Fig 2B | 同上，20 个均值复现 | `s2_aggs.py`、`g06r_full17g.py` |
| G06 | Table S3、Fig 2C、n_A=500 各对比 | 同上，12/12 格复现 | `g06r_full17g.py`、`g06r_indep_resim.py` |
| G07/G08 | 仿真设计、优化器、strict EM（Table S4） | 服务器上不可追溯 | 代码在笔记本 `convergence_sim/` |
| G09 | **Table 1 Sleep 列** | 数值全部 MATCH；3 处描述 MISMATCH | 见下 |
| G10 | Table 1 B14 列 | Source/EA/Recenter/SPDIM MATCH；**FP、Joint MISMATCH** | |
| G11 | Table 1 Cho 列 | 5 格 MATCH；**FP MISMATCH** | Cho 列只存在于缓存 |
| G12 | Table 1 Lee 列 | 5 个表格格 MATCH（另 1 条文字主张 MATCH）；**FP MISMATCH** | |
| G13 | EEG 协议与超参数 | 48 条：20 MATCH、20 MISMATCH、8 PARTIAL | 见 §3 |
| G14 | 摘要、引言、结论中的总结性主张 | Sleep 部分成立；"四个数据集上 0.8–1.9" 在 MI 上不成立 | |

### 2.1 Sleep 列（REVIEW_P0 W2 primary；EEGNet 风格的 H2 编码器；75 被试 × 3 seeds）

| 论文行 | 代码分支名 | 重算值 | 论文值 |
|---|---|---|---|
| Source | `identity_uniform` | 65.72 | 65.7 |
| EA | `source_recolored_ea` | 65.30 | 65.3 |
| Diag-IM | `latent_im_diag_uniform` | 63.62 | 63.6 |
| Joint-GEM | `joint_geometry_uniform` | 63.72 | 63.7 |
| FP-GEM | `fixed_iterative_geometry_uniform` | 65.57 | 65.6 |

- FP−Joint = +1.849 [+1.27, +2.45]，63/75 被试 FP 胜出。论文写的 "1.9" 是两个四舍五入格相减的结果，直接四舍五入应为 1.8。
- 同一文件里还有 `fixed_reference_oneshot_uniform`（FRSC）= **69.5**，是 Sleep 上最好的算子，论文没有报告。
- 描述上有三处与论文不一致：
  - π_fit 是均匀先验 [.2]×5，不是 π_src；
  - 论文说 "225 个 participant–seed 预测都已存档"。实际原始行只有每个 (participant, seed) 的标量指标和 `pred_hash`，没有逐 trial 预测。混淆矩阵只存了 `identity_uniform` 与 `joint_geometry_uniform` 两个分支，FP-GEM 行没有；7 分支混淆重放（829d27db）被标为 `excluded_strict`；
  - Sleep 的 ±30 分钟裁剪用了 hypnogram，也就是目标标签。

### 2.2 MI 的 GEM 格（请你核对）

| 格 | 论文 | 服务器产物（P12 CSV sha f3e4ca69 / Cho 缓存） | 差 |
|---|---|---|---|
| B14 FP-GEM | 73.2 (11.5) | 71.24 (11.48) | +1.96 |
| B14 Joint-GEM | 71.9 (11.3) | 70.94 (11.34) | +0.96 |
| Cho FP-GEM | 60.0 (7.1) | 58.98 (7.14) | +1.02 |
| Cho Joint-GEM | 59.2 (7.1) | 59.19 (7.13) | 0 |
| Lee FP-GEM | 67.6 (9.3) | 66.56 (9.35) | +1.04 |
| Lee Joint-GEM | 66.3 (9.2) | 66.27 (9.24) | 0 |

- 我本人又从 `origin/exp/h2cmi-wave0-mechanism:h2cmi/results/fp_gem_main/fp_gem_per_subject.csv` 独立重算了一遍 B14/Lee，与上表一致。
- 我又核对了 legacy REVIEW_P0 W1（EEGNet 风格编码器，`p0_w1_all.jsonl`）的逐数据集值，同样对不上。FP/Joint 分别为：B14 71.35 (13.38) / 70.22；Cho 74.66 / 74.73；Lee 72.48 / 72.13。
- 代理共尝试了约 15 种替代聚合和读出方式，都得不到论文的数：单 seed、中位数、adapt/pooled 集、密度 argmax、α-path、P13 各 q 水平、Stage-2、修复后 W1 编码器等。
- 论文里 "FP-GEM is best on B14 and Cho" 在产物中不成立：B14 上 Recenter/SPDIM 72.7 > FP 71.2；Cho 上 FP 在 Recenter 系方法（Recenter/SPDIM/Joint/FP）中最低，且 FP−Joint = −0.21，与论文的 "+0.8" 符号相反。
- **这不是结论，是待解决项。** 在 T1 表中记为 `unresolved`，需要笔记本上的 tex 历史和运行记录才能关闭。

### 2.3 其他需要更正的证据引用（针对 v1/v4 文档本身）

- **P13 的 1.4 不能当作 Joint 特有的证据。** v1 §2.2(b)（L83-87）和 v4 P7（L78）用 "先验几乎不动、几何移动约 1.4" 说明 "先验方向似然平坦、偏移被几何吸收"。但 v1 自己的同一张表里，FP 在先验固定时位移同样约 1.4：q=0.1 时 1.414 对 Joint 1.436，q=0.9 时 1.404 对 1.424（`fp_gem_prevalence_geometry_diagnostic.csv` @b5fb5158）。所以这个数支持不了 Joint 特有的机制。T9 "与 P13 先验移动量对照" 需要重新定义。
- **W1 legacy 已被隔离。** v1 §2.2(c)（L111）引用的 W1（115 被试，+0.0022）已由 `w1_legacy_split_quarantine.md` 标为 `legacy_split_not_confirmatory`，原因是 Cho 在 52/52 个目标上存在单类评估块。规范结果是修复后的 `w1_repaired_h2cmi_method_contrasts.csv`（bc61ee11）：
  - FP−Joint +0.00299 [+0.00067, +0.00540]；
  - dataset-macro +0.0053 [+0.0017, +0.0092]。
- **写作用数字摘要没有被 v1–v5 引用。** `h2cmi/results/review_completion/MANUSCRIPT_NUMBERS_READY.md`（f2808796）和 `WAVE0_MANUSCRIPT_NOTES.md` 是服务器上面向写作的数字摘要。

---

## 3. 论文描述 ≠ 代码（G13 要点；都在 `real_eeg.py`、`class_conditional.py`、`config.py` 中核实到行号）

| 项 | 论文 | 实际代码 |
|---|---|---|
| B14 类别 | 4 类 | 2 类 LeftRight（`real_eeg.py` L72-76） |
| MI 频带与窗口 | 4–38 Hz，0.5–3.5 s | 8–30 Hz，0–2 s，逐 trial 逐通道 z-score（`real_eeg.py` L33-36、L92-96） |
| MI 划分 | 早 session 适应，晚 session 评估 | 只用 session 0，按**目标标签**分层对半（`w1_repaired_split.py` L80-95） |
| 密度 | 对角高斯，方差下限 1e-4 | Student-t，rank-4 + 对角，df 8，下限 1e-2 |
| Joint 先验 M 步 | 平均 responsibility | `(Σr + 6π_S)/(n+6)`，κ=6 |
| 优化与停止 | L-BFGS，≤100 次，相对变化判停 | Adam lr 0.05，20 次外循环 × 3 步，无收敛判据 |
| 正则 | 以恒等为中心 1e-3，log-scale 限制在 [−2, 2] | logdet 1、trust 1/1，无边界 |
| MI 读出 | 密度 argmax + 均匀 π_dec（Eq 12） | 冻结的 TSMNet 线性分类器 |
| 源训练 | ≤100 epochs，patience 15，按被试划分 | 固定 20 epochs（P9），验证集取每被试每类的最后 20% |
| Sleep 滤波 | 0.3–35 Hz | 不滤波，逐 epoch z-score |
| Sleep π_fit | π_src | 均匀先验 |
| "目标标签从不使用" | 适应、选择、停止各环节 | MI 划分与 Sleep 裁剪都用了标签 |

论文所写的 4–38 Hz、0.5–3.5 s 和 4 类 B14，只出现在 LPC-CMI/CIGL 的 `cmi/data/moabb_data.py` 中。FP-GEM 的运行器没有 import 它。

这对大修的意义：**v3 定下的 G0 硬门是对的，而且比预想的更关键。** 修订稿必须二选一：按实际实现改写方法与协议描述，或按论文描述重跑。T2 的统一实现正是做这个决定的地方。

---

## 4. Sprint 0 各任务的当前状态

| 任务 | 状态 | 说明 |
|---|---|---|
| T1 追溯表 | **服务器端初稿完成** | 两张 CSV；剩余 MI GEM 格与仿真代码需要笔记本侧补齐 |
| T2 统一实现 | 被一个决策卡住 | 有两个"旧实现"：笔记本上的 `fpgem`（L-BFGS、对角高斯，用于仿真）和服务器上的 `class_conditional.py`（Adam、Student-t、κ=6，用于全部 EEG）。验收标准 "与旧实现数值一致" 必须说明指哪一个。仿真侧可以用 `repro/simulation/` 作为服务器端参照 |
| T3 ρ 审计 | 初稿完成 | 见下 |
| T4 dump 清点 | 完成 | 见下 |
| T5 理论账本 | 部分完成 | `repro/theory/` 已复核现有结果；v4 新结果（P1 一般 Q、P5 对应性）尚未开始 |
| T6 仿真 | 有基础 | 仿真独立重写已存在，可直接扩展到多类与对角仿射 |
| T7 C1 注入实验 | 可行，但有陷阱 | 两个 loader 都逐 trial 逐通道 z-score，**会精确抵消上游注入的逐通道增益和偏置**，实验会平凡地为零。注入必须放在 z-score 之后，或改用重参考、通道混合等非对角变换。这个 z-score 也可能是 "EA ≈ Source" 的原因，尚未检验 |
| T8 / T9 | 需要 GPU 重推理 | 没有保存 latent 特征。重推理可行，且已验证能逐哈希复现（P13 对 P12） |
| T10 规范 | 未开始 | |

**T3 细节：**
- MI 的 ρ_A = ρ_E = 0.5 是**构造出来的**（按标签对半），所以现有 MI 产物上不存在 "协议比例 ≠ 观测比例" 的差异。
- 真实差异只可能来自被管线忽略的剔除标记，例如 B14 专家伪迹标记、Cho `bad_trial_indices`（s20 左 70、右 47）。
- Sleep 的自然先验移动很大：ρ_A 与 ρ_E 的 TV 距离中位数为 0.139，9/75 被试的适应夜 N3 为 0。
- 还剩三项 CPU 统计，需走 SLURM：
  - Cho `bad_trial_indices`，约 10 GB 读取；
  - Lee 在线阶段计数，约 61 GB；
  - 用 lights-off 时间做不依赖标签的 Sleep 裁剪，需要 `SC-subjects.xls`，而 env 缺 `xlrd`。

**T4 细节：**
- Sleep、B14 2 类、Cho、Lee 的原始信号都在 datalake，冻结的源模型也都在。
- B14 4 类没有 loader 也没有 checkpoint，需要重训 27 个单元。
- 各数据集的时间顺序：Cho 在跨类别层面丢失了（MOABB 按类堆叠），B14 和 Sleep 保持，Lee 的适应段与评估段交错。
- 刺激前片段：任何现有 dump 里都没有，都需要从原始信号重新切片。

---

## 5. 需要你决定或提供的东西（在这些解决前，我不启动任何 GPU 实验）

1. **MI GEM 四格的来源。** 请在笔记本上找 `theoryfirst/experiment_results_table.tex` 的编辑历史与对应运行。若找不到可产生这些数的运行，修订稿应改用服务器产物值（FP−Joint：B14 +0.3、Cho −0.2、Lee +0.3），并相应改写摘要、引言和结论中的 "0.8–1.9 points on four benchmarks"。
2. **协议描述 vs 实现：** 按实际实现改写论文，还是按论文描述重跑？这决定 T2 验收的对象。
3. **B14 4 类：**
   - kickoff 把它冻结为第一轮数据；
   - v3 §16.1 把重训排除在第一批之外；
   - 训练成本不能作为理由。

   是否现在重训 27 个单元？
4. **笔记本侧文件：** 能否把 `fpgem` 包、`convergence_sim`、`journal_revision/prechecks/` 同步到服务器？同步后 T2 和 T6 的对照可以在服务器上完成。
5. **Sprint 0 产物的 git 归属：** `FP-GEM/` 目前不在任何分支里。建议新开分支 `project/fp-gem-journal`，把 `FP-GEM/` 和 `sprint0/` 提交上去。

---

## 6. 删除清单

见 `CLEANUP_COMMANDS.sh`。运行 `bash CLEANUP_COMMANDS.sh` 会列出各段，逐段运行，例如 `bash CLEANUP_COMMANDS.sh A1`。

| 级别 | 段 | 内容 | 释放空间 |
|---|---|---|---|
| A，现在可删 | A1 | 3 个从未运行的 spdim_p6 shard worktree | 81M |
|  | A2 | 3 个 P7 shard worktree（产物已在 salvaged；先写 sha 清单） | 144M |
|  | A3 | `.codex_p12_launch_f34cc8b` clone | 54M |
|  | A4 | P13 的 `repo_7b48813` | 46M |
|  | A5 | `__pycache__` | 17M |
|  | A6 | `_TRASH` | 2.3M |
|  | A7 | `refs/codex/turn-diffs` | 0 |
| B，先 salvage 再删（函数内自动先拷贝并校验） | B1 | 8 个 spdim_p6 worktree（先拷 32 个唯一 SLURM 日志） | 224M |
|  | B2 | spdim_clean worktree | 34M |
|  | B3 | qxu `sleep_cache` 中 20 个与 `p0_sleep_cache` 逐字节相同的 npz（改为软链接） | 696M |
|  | B4 | BTTA-DG 预处理数据。**建议推迟**：这是唯一副本，从 datalake 再生不一定逐字节一致，而审稿人要过 BTTA-DG 基线（代码和权重不在删除范围） | 2.9G |
|  | B5 | 20,898 个失败重试日志（保留列表和样本） | 约 180M（NFS 1 MiB 块；表观 15MB） |
|  | B6 | qxu 的 smoke 输出 | 2.2M |
| C，Sprint 0 重推理完成前**不要删** | — | `.codex_p12_launch_5b71ee8`（所有 fp_gem `.slurm` 都硬编码指向它）、`repo_afa21f2` | — |
| 必须保留 | — | 脚本末尾列出的唯一副本 | — |

A 级合计约 0.34G，B 级合计约 4.0G（不含 B4 约 1.1G）。

补充说明：
- A5 会删掉根目录 `h2cmi/` 里 4 个 .pyc，它们是 Project-A 某些从未提交的草稿版本的唯一字节码痕迹。与 FP-GEM 无关，可以忽略。
- 运行 A5、B3、B5 前，请确认没有别的交互会话正在 H2CMI/qxu 或 `~/slurm_logs` 下工作。

从未建议 `git worktree prune`。`FP-GEM/` 中的计划文档和 PDF 都没有其他副本（v2 的哈希被 v3 钉住），所以建议保留，不列入删除。
