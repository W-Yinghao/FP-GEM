# FP-GEM 期刊版大修方案（TSP / TPAMI）

日期：2026-09-26
依据：OpenReview 三份审稿（yczf 5/4，hTrM 5/5，AI reviewer）、AAAI 正文与补充材料、
`W-Yinghao/CMI` 仓库（60 个分支）中与 FP-GEM/H2CMI 相关的全部已提交结果、
本地 `FP-GEM_AAAI2027/` 的仿真与文档、`AAAI_CMI/` 中 22 页长版
《When Alignment Chases Prevalence》。

---

## 0. 一句话结论

**投 TSP，不投 TPAMI。** 把论文从"FP-GEM 这个方法比 Joint-GEM 好 0.8–1.9 个点"
改写成一篇估计理论论文：**无标签对齐 = 从混合分布里联合估计（几何 θ，类别比例 π）；
两者在类别重叠时弱可辨识；不同对齐估计量（pooled 矩匹配 / one-shot 类条件 / 迭代固定先验 EM /
联合 EM）各自的总体目标与偏差有闭式刻画；"先验参与度"是一个可调的方差–偏差旋钮，
应由采集协议而不是无标签批次来设定。** FP-GEM 降级为这个家族中的一个成员和一条推荐配方
（几何用固定先验 → 偏移门控 → 第二阶段估计比例 → 决策权重单独选）。

理由：三份审稿一致认可理论，一致否定"实证足以支撑方法优越性"。仓库里已有的证据
（P12、P13、REVIEW_P0）表明这个实证结论在 MI 上本来就不稳（见第 2 节），
再堆实验也堆不出 TPAMI 要的 SOTA 表；而理论恰好是 TSP 的口味。

---

## 1. 审稿意见归纳

三份审稿的共性只有一条：理论好，实证不够。具体拆成 12 项，后面第 7 节逐项给行动。

| # | 意见 | 来源 |
|---|---|---|
| R1 | 只有均值；Sleep 无标准差；无被试级配对 CI / 胜负计数 / 检验 / bootstrap | yczf, AI |
| R2 | "协议支持的类别比例"这一前提未在真实数据上验证；Sleep 比例天然变化 | yczf, hTrM |
| R3 | 固定先验略错时的敏感性 | yczf |
| R4 | 定位不清：是对 Joint-GEM 的受控修正，还是完整的 EEG 适应管线 | yczf, hTrM |
| R5 | 缺少同读出的"无 GEM"基线，无法区分"FP 有益"与"FP 只是避免 Joint 的伤害" | AI |
| R6 | 真实 EEG 上没有机制诊断（比例失配、Joint 先验位移、responsibility 不确定性、几何位移与增益的关联） | AI |
| R7 | 缺 CMMN（Sleep）和 BTTA-DG（MI）基线 | AI |
| R8 | 跨 session / 跨夜评估引入了理论未覆盖的时间漂移 | AI |
| R9 | 缺"何时该固定先验"的判据；先验未知或差异大时怎么用；如何检测前提失效 | hTrM, AI |
| R10 | 多类弱可辨识分析（五类睡眠） | AI |
| R11 | 冻结编码器 + 对角高斯头过于简化；效果能否推广到非线性 adapter；改进多少来自固定先验、多少来自仿射高斯设定 | hTrM |
| R12 | 写作：第 3 节缺路线图；引言应给三种权重角色和 Joint-GEM 的更新级定义；Prop 4 惩罚项、式(10) argmax、Fig 2A 的 D̂ 定义、"should not" 措辞；引 RAINCOAT、RLSbench | AI |

---

## 2. 现有证据盘点（必须先正视的事实）

### 2.1 AAAI 投稿表（最终一轮 07-27/28 运行）

| 方法 | Sleep | B14 | Cho | Lee |
|---|---|---|---|---|
| Source | 65.7 | 61.0 | 52.3 | 54.9 |
| Recenter | — | 72.7 | 59.8 | 68.2 |
| SPDIM | — | 72.7 | 59.7 | 67.7 |
| Joint-GEM | 63.7 | 71.9 | 59.2 | 66.3 |
| FP-GEM | 65.6 | 73.2 | 60.0 | 67.6 |

被试级原始分数**不在本地**（`output/submission_2026-07-31/FP-GEM` 只有代码包）。
Source/Recenter/SPDIM 的数字与 P12 完全一致，FP/Joint 的数字来自更晚的一轮，
其被试级产物需向服务器索取（`submission_2026-07-28/SERVER_REPRO_CHECKLIST_REQUEST.md`
已经写好了只读提取请求，但没有回执）。

### 2.2 仓库里已有、而 AAAI 稿没用或与之冲突的结果

**(a) P12 同骨干头对头（`agent/fp-gem-stage2` @ `3b52e202`，`h2cmi/results/fp_gem_main/`，含 `fp_gem_per_subject.csv`）**
TSMNet，B14 + Lee，3 seeds，189 units，10k 配对 cluster bootstrap：

| 对比（被试加权 bAcc） | 估计 [95% CI] |
|---|---|
| FP-GEM − Source | +0.115 [+0.096, +0.135] |
| FP-GEM − Joint-GEM | **+0.003 [−0.0003, +0.006]（不显著）** |
| FP-GEM − Recenter | −0.016 [−0.022, −0.010] |
| FP-GEM − SPDIM(geodesic) | −0.012 [−0.017, −0.006] |

**(b) P13 固定池比例应力测试（`exp/h2cmi-wave0-mechanism` @ `b5fb515`，`h2cmi/results/fp_gem_prevalence/`，含 per-subject CSV）**
Lee2019，54×3，q ∈ {0.1, 0.5, 0.9}：

| 指标 | Joint-GEM | FP-GEM |
|---|---|---|
| 比例敏感度 | 0.0303 | 0.0296（差 −0.0007 [−0.0036, +0.0021]，**不支持"FP 更稳"**） |
| Joint 拟合的 class-0 先验 @ q=0.1/0.5/0.9 | 0.464 / 0.485 / 0.501 | 0.5 固定 |
| 几何位移 @ q=0.1 / 0.9 | 1.436 / 1.424 | 1.414 / 1.404 |
| bAcc @ q=0.1/0.5/0.9 | .656/.663/.638 | .658/.666/.639 |

关键读法：真实比例从 0.1 变到 0.9，**Joint 的先验几乎不动（0.46→0.50），几何却位移了 1.4**。
这是弱可辨识在真实数据上的直接表现：先验方向的似然是平的，偏移被几何吸收；
FP 与 Joint 在这个 regime 里几乎是同一个估计量。这个结果原本被冻结在附录当"边界测试"，
在期刊版里它应该是**机制证据的主角**，而不是尴尬的负结果。

**(c) REVIEW_P0 修正版（`exp/h2cmi-review-p0-corrections` @ `5bc9bf0`，`h2cmi/results/REVIEW_P0_RESULTS.md`，analyzer `9a35cc9`）**
Sleep-EDF，75 名被试，夜 1 适应→夜 2 评估，subject bootstrap：

| 算子（统一高斯头、uniform 决策权重） | bAcc | 相对 identity 变差的比例 |
|---|---|---|
| identity | 0.657 | — |
| joint_geometry | 0.637 | 61.3% |
| fixed_iterative（= FP-GEM） | 0.656 | 46.7% |
| **fixed_reference_oneshot** | **0.695** | **30.7%** |
| pooled | 0.660 | 48.0% |
| Latent-IM-Diag | 0.636 | — |
| identity @ π_J（用 Joint 先验做决策） | 0.513 | 98.7% |

配对推断：fixed_iterative − joint = **+0.0185 [+0.0127, +0.0245]**（主协议），
+0.0234 [+0.0112, +0.0377]（夜 2 内前后半分割的次协议，**即 R8 要的非纵向协议，Sleep 已有**）。
决策先验效应 P = −0.144 [−0.159, −0.128]：用拟合先验做决策权重是灾难，
这就是 Lemma S9 的真实数据版本。
**最重要的新事实：one-shot 固定参考类条件（只算一次 responsibility）比迭代 FP-GEM 高 3.9 个点，
比 identity 高 3.8 个点。** AAAI 稿完全没有报告它。

同一分支的 W1（115 名 MI 被试，旧管线）：fixed − joint = +0.0022 [−0.0005, +0.0049]（被试加权，不显著）；
pooled 0.735 ≈ fixed 0.734 ≈ joint 0.732 > one-shot 0.721。
即：**比例匹配时迭代有益（方差降低），比例失配时迭代有害（偏差放大）**——两边真实数据都有。

**(d) Stage-2 两阶段解耦 + 偏移门控（`agent/fp-gem-stage2`，`h2cmi/results/fp_gem_stage2/`）**
几何冻结后用无标签池估计目标比例（MLLS-shrink / BBSE），修正决策权重：
有偏移时 accuracy +0.050 [+0.035, +0.065]，平衡时 −0.0125 [−0.022, −0.004]（硬安全门失败）；
加两比例 z 检验门控后：平衡 −0.006 [−0.012, 0.000]，偏移 +0.011 [+0.0015, +0.021]，
门控误报 4.8%，检出率 33%。bAcc 对第二阶段严格不变（P4 = 0）。
Sleep 的 K=5 卡方门控 runner/analyzer 已提交（`687003ff`, `722e33cd`），**结果未提交**。
这直接回答 R9 / R3 / R4。

**(e) V2P_WEIGHTED（REVIEW_P0）**：同一批 trial 重加权 q∈{.25,.5,.75}，评估嵌入位移：
pooled 0.049 < one-shot 0.314 < fixed_iterative 0.640 = joint 0.640 ≪ oracle label-conditional 1.960。
注意它**推翻了旧 V2P**（occupancy slope 里 pooled 最敏感）。期刊版只能用修正版，
并且 oracle 位移巨大说明真实嵌入里几何**不是跨类共享的**（Theorem S12 的前提在真实数据上不成立），
这本身是值得写的错定诊断。

**(f) W1-B BTTA-DG 原生复现（`e941bb5`，`W1B_REPRODUCTION.md`）**：公开代码 `add_sample()` 从未被调用，
GMM 无效，Δ = 0.0000（35 名被试）；修复后只翻转 1 个预测。回答 R7 的一半，放附录。

**(g) 本地仿真**：`convergence_sim`（严格收敛版 Table S3，结论不变）、`multiclass_sim`（K=4,5，
t=0.5 匹配比例下 FP−Joint MSE −0.09，BA +0.5 pp，但 Joint 严格收敛率只有 63–67%，
当时决定不写进论文）、`optimal_sim`（α 路径：内部 α 最优 18/50 格，超过 5% 改进仅 2/50，
弱分离/近源 12/12 格 FP 胜）、`mechanism_sim`。

### 2.3 由此必须改变的叙事

1. "FP-GEM 在四个数据集上都高于 Joint-GEM"在 MI 上是描述性的、不显著的、
   而且换一轮运行就变成 +0.3。**不能再当主结论。**
2. MI 上 FP ≈ Joint 不是理论失败，而是弱可辨识的**预测**：先验方向平坦，
   早停的 Joint-GEM 停在初始化附近（P13 的先验 0.46–0.50 是直接证据）。
   期刊版要把这一点写成定理级的说明（第 5 节 T6）。
3. Sleep 才是先验能动的 regime：Joint 的先验移动→几何被推→伤害；固定先验止住反馈，
   one-shot 进一步避免偏差放大。这是"先验推动几何"最干净的真实数据证据。
4. 所以论文的主角是**估计量家族 + 可辨识性 + 方差–偏差旋钮**，不是某个方法赢了。

---

## 3. 投稿去向

### 3.1 TSP（推荐）

- 契合点：可辨识性定理、Fisher 信息 Schur 补、profile 似然弱可辨识、错定 EM 的伪真参数、
  受约束 EM 的收敛性质、闭式偏差——全是 TSP 统计信号处理/机器学习信号处理的常规内容。
  EEG 对齐（EA、Riemannian re-centering、SPD 归一化）本身就是信号处理方法，
  pooled 矩匹配偏差定理（S11）直接说的是这些方法。
- 篇幅：常规论文不超过 13 页双栏（含参考文献），超过 10 页按页收费（SPS FAQ）。
  目标 12–13 页正文 + 补充材料。
- 审稿人会问什么：定理的正则性条件、CRB/渐近正态性、EM 单调性与收敛、
  多类推广、方法在"信号"层面的意义。这些都能答。
- 风险：编辑以"应用偏 ML"为由转投。缓解：引言与第 3 节用信号处理语言写（协方差/矩对齐、
  混合模型辨识、EM），EEG 作为应用实例；EDICS 选 MLSP / SSP。
  备选：IEEE TNNLS（方法+理论都收）、IEEE TBME（EEG 社区，收 modest gains）。

### 3.2 TPAMI（不推荐，除非再投 2–3 个月 GPU）

- 常规论文约 14 页（超长付费，具体以 IEEE CS 官网为准）。
- 审稿人是 TTA/DA 社区，会要求：多数据集 SOTA 表、现代 TTA 基线（Tent/SAR/LAME/SHOT/T-TIME/CMMN/BTTA-DG）、
  非线性 adapter，最好还有非 EEG 模态。hTrM 的"简化设定"意见在 TPAMI 会被放大成致命伤。
- 而我们的真实结果是：FP ≈ Joint（MI）、FP ≈ Recenter、低于 SPDIM 1 个点、Sleep 上 one-shot 才最好。
  这张表在 TPAMI 过不了"方法论文"的门槛，作为"分析论文"又缺乏广度。
- 如果坚持 TPAMI，需要额外：BNCI2014-004 / 2015-001 / HGD / Stieger2021（数据湖里都有）、
  一个非线性 transport（如 per-class 全协方差仿射或 SPD 上的测地 transport）在固定/联合先验两种设定下的对照、
  CMMN + T-TIME + Tent/SAR 基线、以及至少一个非 EEG 的 label-shift 基准（RLSbench 子集）。
  估计 2–3 个月 GPU + 分析时间，且仍无法保证 SOTA。

---

## 4. 新主线与标题

**主线（一段话）**：无标签目标批次只观察到混合边缘。源模型的公共稳定子固定了坐标，
但类别比例变化与几何变化仍可产生同一边缘（精确构造），在类别重叠时其可辨识信息按分离度四次方坍缩
（高斯，二类与多类）。常用对齐算子是这一联合估计问题的不同解：pooled 矩匹配把比例变化当几何吸收；
one-shot 类条件把泄漏衰减为 1−κ(t)；迭代固定先验 EM 收敛到固定先验 MLE，偏差再放大 1/(1−t²S(t))；
联合 EM 让先验参与，沿弱方向的更新速度为 S(t)（缺失信息比例），早停时退化为固定先验。
先验参与度（α）、迭代深度（k）、门控（是否允许第二阶段估计比例）是同一方差–偏差权衡的三个旋钮，
应由采集协议设定；我们给出闭式的失配容忍半径作为判据。真实 EEG 上：MI（弱分离、平衡协议）先验不可辨识、
几何吸收比例偏移（P13）；Sleep（五类、比例自然变化）先验可动、联合更新有害、one-shot 最优（REVIEW_P0）；
两阶段门控方案在偏移时获益、平衡时无害（Stage-2）。

**标题候选**（无 AI 味词，陈述式）：
1. *When Priors Push Geometry: Weak Identification and Fixed-Prior EM for Unlabeled EEG Alignment under Class-Proportion Shift*
2. *Class Proportions and Feature Geometry in Unlabeled EEG Alignment: Identifiability, Estimator Bias, and Fixed-Prior EM*
3. *Joint Estimation of Class Proportions and Feature Geometry from Unlabeled Mixtures, with Application to EEG Alignment*

**不做的声明**（沿用仓库 `FINAL_FP_GEM_STORY_FREEZE`）：不称 SOTA；不称比例不变；
不称 FP 比 Joint 在应力下更稳；不称 FP > Joint 在 MI 上显著。

---

## 5. 理论部分：保留、提升、新增

### 5.1 保留并提到正文
- Thm S2/Cor S3（稳定子与对角仿射恒等）——TSP 读者会喜欢这个可辨识性表述。
- Thm 1 + Cor S6（精确歧义 + 两动作 minimax regret g0g1/(g0+g1)）。
- Prop 3（局部先验→几何响应）、Prop 4（Schur 信息，明确 λ=0 或 λ_n→0）、Prop 5（responsibility 误差偏差）。
- Thm 6（高斯弱可辨识，迭代极限），加一张 Fisher 信息坍缩图（长版 Fig 1）。
- Thm S11（pooled 矩匹配的比例泄漏）——直接对应 EA / Recenter，正文必须有。
- Thm S14（one-shot 闭式偏差与 1−κ(t)）——正文必须有。

### 5.2 新增（三条已做数值预检，脚本 `journal_revision/prechecks/precheck_theory.py`）

**T5 失配容忍半径（回答 R3、R9）。**
固定先验 MLE 在失配 δ 下的偏差为 A(t)δ，A(t) = −2tS/(1−t²S)；Joint 的方差为 1/(n I_{a|η})。
令偏差平方等于方差差，得交叉点
δ*(t,n) = sqrt(1/(n I_{a|η}) − 1/(n I_aa)) / |A(t)|，首阶 δ* ≈ sqrt(3/(8n))·t⁻³。
预检（n=500，精确 Fisher 块）：t=0.35 → ρ*>1（FP 永远占优）；0.5 → 0.78；0.75 → 0.60；1.0 → 0.55；1.5 → 0.53。
与 Table S3 的符号模式一致（0.35 全程 FP；0.5 在 0.70 FP、0.92 交叉；0.75 在 0.70 交叉；1.5 在 0.70 已是 Joint）。
这就是 AI reviewer 要的"何时该固定先验"的可操作判据：给定分离度估计 t̂（源密度头的 Bhattacharyya 距离）
与批大小 n，协议保证的比例误差在 δ* 内就固定。

**T6 迭代深度与先验参与：三个旋钮是同一件事（回答 R4、R9、R11 的"改进来自哪里"）。**
(a) one-shot 偏差 b₁ = (2ρ−1)t(κ−1)（已有），收敛后偏差 b_∞ = A(t)δ；
预检显示 b_∞/b₁ = 1/(1−t²S(t)) 精确成立（t=0.35: 1.12；0.5: 1.25；0.75: 1.53；1.0: 1.82）。
即**迭代把固定先验的失配偏差放大 1/(1−γ) 倍**，比例匹配时则只降方差。
这解释 Sleep（one-shot 0.695 > 迭代 0.656）与 MI（迭代 0.734 > one-shot 0.721）的相反排序。
(b) 联合 EM 沿先验方向的收缩率等于缺失信息比例 S(t)（Dempster–Laird–Rubin），
t=0.35 时移动 90% 需 20 次迭代、t=0.2 需 59 次；配合相对目标变化的停止规则，
弱分离下 Joint-GEM 早停在源先验附近，与 FP-GEM 重合——这是 P12/P13 "FP ≈ Joint" 的解释。
(c) Version B 的源锚定路径 π_α = (1−α)π_src + α r̄ 给出连续插值；本地 `optimal_sim` 已表明
内部 α 几乎从不显著优于两端点，所以旋钮的实际形态是"固定 / 早停 / 放开 + 门控"。
建议写成一个小节"先验参与的三个旋钮"，配一张 (α, k) 平面上的偏差–方差示意图。

**T4 多类弱可辨识（回答 R10）。**
K 类正单纯形均值、分离 t：对 K−1 个先验 logit profile 后，落在类均值差张成空间内的平移方向
信息为 O(t⁴)，正交方向保持 O(1)。用 sympy 做 K=3,4,5 的级数验证，
并把 `multiclass_sim` 重跑到严格收敛（提高迭代上限或用直接似然优化，像 `convergence_sim` 那样）。

**T7 第二阶段的性质（回答 R4）。**
两条简单命题：几何冻结后 bAcc 对第二阶段比例估计严格不变（现有 P4 的理论版）；
两比例/卡方门控的功效随 n·t²·δ² 增长——说明门控在弱分离下检出率低（Stage-2 观测到 33%），
与弱可辨识是同一枚硬币。

### 5.3 写法
- 第 3 节开头加路线图：全局不可辨识 → 一般估计量敏感性 → 高斯局部机制 → 估计量家族。
- 引言第二段给出 ρ_T / π_fit / π_dec 三个角色与 Joint-GEM 的一行更新级定义（R12）。
- 修 Prop 4（λ=0）、式(10)（GEM 只需非减）、Fig 2A（D̂ = 导数 × 拟合 logit 位移）、
  "should not" → "should not trigger a geometry correction"。
- 引 RAINCOAT（He 2023）、RLSbench（Garg 2023）、GOPSA（Mellot 2024）、
  CMMN/STMA（Gnassounou 2023/2024）、Latent alignment（Bakas 2025）、
  以及混合模型可辨识（Teicher 1963；Yakowitz–Spragins 1968）、错定 MLE（White 1982）、
  类先验 EM（Saerens 2002；du Plessis–Sugiyama 2014）、BBSE/RLLS/MLLS（Lipton 2018；Azizzadenesheli 2019；Alexandari 2020）。
- 遵守写作规则：不用 audit / leverage / comprehensive 等词；摘要不放数字；一句一意。

---

## 6. 实验部分

标注：【有】= 仓库/本地已有产物，只需重写；【CPU】= 在已存嵌入 dump 上重算，无需训练；
【GPU】= 需要新训练。

### 6.1 受控仿真（本地，全部 CPU）
| 项 | 内容 | 状态 |
|---|---|---|
| S1 | 局部响应校准（R²=0.998）、批大小、失配交叉（Table S3 严格收敛版） | 【有】`convergence_sim`, `mechanism_sim` |
| S2 | 容忍半径 δ*(t,n) 曲线叠加到失配交叉图上；加 n∈{200,1000} 两组新格 | 【CPU】新增，1 天 |
| S3 | 迭代深度 k ∈ {1,2,3,5,10,∞} × 失配 × t 的偏差放大曲线，对照 1/(1−t²S) | 【CPU】新增，1 天 |
| S4 | α 路径（有）+ 与 k 路径合成"三旋钮"图 | 【有】`optimal_sim` + 1 天 |
| S5 | 多类 K=3,4,5 严格收敛版 | 【CPU】重跑 `multiclass_sim`，半天 |
| S6 | Joint-GEM 沿先验方向的收敛速度 vs S(t)，早停规则复现 FP≈Joint | 【CPU】新增，1 天 |

### 6.2 真实 EEG：估计量家族与配对推断（回答 R1、R5、R11）
统一读出（存储的对角高斯头 + uniform 决策权重）下报告：identity、pooled、one-shot、FP-GEM(k=∞)、
FP-GEM(k=1,3,10)、Joint-GEM、α∈{0.25,0.5}；外加管线参照 Recenter / SPDIM / EA / Diag-IM。
- Sleep（EEGNet，75 人）：identity/pooled/one-shot/fixed/joint 及配对 CI 【有】REVIEW_P0；k 扫描与 α 路径【CPU】。
- MI（TSMNet，B14/Cho/Lee）：FP/Joint/Recenter/SPDIM/Source【有】（P12 有 per-subject；最终轮需服务器只读提取）；
  identity-with-Gaussian-head、pooled、one-shot、k 扫描、α 路径【CPU】在 Stage-2 的 npz dump 上跑。
- 统计：被试为单位；seeds 与 session 先在被试内平均；10k 配对 bootstrap；胜/平/负计数；
  Holm 只用于每个面板一个预注册主对比。所有 CI 都印在表里。

### 6.3 真实 EEG：机制诊断（回答 R2、R6、R3）
- M1 P13 比例应力（Lee，q=0.1/0.5/0.9）：Joint 先验 vs 真实比例、几何位移、bAcc 【有】，重画成正文图。
- M2 V2P_WEIGHTED 位移排序 + oracle 位移作为"几何非共享"错定诊断 【有】。
- M3 每被试 regime 变量：适应批的比例失配 d_ρ = ½‖ρ̂_A − π_src‖₁（评估后揭示标签算）、
  源密度头 Bhattacharyya 分离 t̂、identity 处的 responsibility 熵、Joint 先验位移 |η̂_J − η_src|、
  FP–Joint 几何位移、配对 bAcc 差；回归 + 数据集截距 + 被试 bootstrap 【CPU】。
  这一项同时验证 R2（MI 的 d_ρ 应接近 0，Sleep 应分散）并把 δ* 判据落到真实数据。
- M4 Sleep 夜 2 内前后半分割（非纵向）【有】REVIEW_P0 次协议；MI 用后一 session 前后半分割【CPU】（回答 R8）。

### 6.4 两阶段管线与门控（回答 R4、R9）
- P1 MI Stage-2（MLLS-shrink/BBSE/oracle × identity/FP/Joint × q）+ 门控结果 【有】。
- P2 Sleep K=5 卡方门控：runner/analyzer 已有，跑出结果 【CPU/GPU dump 视情况】。
- P3 把"几何固定先验 → 门控 → 第二阶段 → 决策权重"写成算法 2，明确 bAcc 与 accuracy 两个目标各用什么权重。

### 6.5 外部基线（回答 R7）
- BTTA-DG 复现（Δ=0）【有】→ 附录"实现核查"。
- CMMN（Sleep）【GPU】：官方代码，源训练时加 CMMN 归一化，约 1–2 天 GPU。TSP 可选，建议做。
- T-TIME（MI）【GPU】可选。Tent/SAR 在冻结编码器设定下不适用，说明即可。

### 6.6 非线性 adapter（R11）
TSP 版：在"讨论"里说明理论对任意可微 transport 家族成立（Prop 3/5 的形式已是一般的），
并给一个小实验：per-class 共享的全协方差仿射（低秩 + 对角）在固定/联合先验下的对比【CPU】在 dump 上做。
TPAMI 版才需要真正的非线性 transport【GPU】。

---

## 7. 审稿意见 → 行动 映射

| # | 行动 | 证据来源 | 成本 |
|---|---|---|---|
| R1 | 6.2 全表配对 CI | REVIEW_P0（有）+ P12 per-subject（有）+ 最终轮只读提取/重算 | CPU |
| R2 | 6.3 M3 的 d_ρ 分布；正文明确 MI 三数据集按设计平衡（`sources/research_20260728_eeg_tta_regime.md` 已核实） | 有 + CPU | 低 |
| R3 | T5 容忍半径 + S2/S3 + P13 + M3 | 有 + CPU | 低 |
| R4 | 第 4 节定位；6.4 两阶段算法；"不做的声明" | 有 | 写作 |
| R5 | identity-with-Gaussian-head 行；Sleep 已有（0.657） | 有 + CPU | 低 |
| R6 | 6.3 M1–M3 | 有 + CPU | 中 |
| R7 | BTTA-DG 附录 + CMMN | 有 + GPU | 中 |
| R8 | M4 | 有 + CPU | 低 |
| R9 | T5 判据 + Stage-2 门控 + T7 | 有 + 新理论 | 中 |
| R10 | T4 + S5 | CPU | 中 |
| R11 | T6(a) 拆分"固定先验 vs 迭代 vs 家族"的贡献；6.6 | CPU | 中 |
| R12 | 5.3 写法清单 | — | 写作 |

---

## 8. 论文结构（TSP，目标 12–13 页）

1. Introduction（1.2 页）：同一边缘、两种原因；三个权重角色；Joint-GEM 一行定义；贡献四条。
2. Related work（0.8 页）：几何优先的 EEG 对齐；label / mixed shift；混合模型可辨识；EEG TTA。
3. Problem and identifiability（2 页）：稳定子；精确歧义与 minimax；高斯弱可辨识（二类 + 多类 T4）；Fisher 坍缩图。
4. Estimators and their population targets（2.5 页）：pooled（S11）；one-shot（S14）；迭代固定先验（T6a）；
   联合 EM（Prop 3/4 + T6b）；α 路径；容忍半径 T5；三旋钮图。
5. Fixed-prior geometry EM and the two-stage recipe（1.2 页）：算法 1（对角高斯头的闭式/牛顿 M 步、单调性）；
   算法 2（门控 + 第二阶段 + 决策权重）；T7。
6. Controlled experiments（1.5 页）：S1–S6 精选四图。
7. EEG experiments（3 页）：数据与协议；估计量家族表（配对 CI）；机制图（P13、M3）；Stage-2 门控表；
   管线参照与外部基线一段。
8. Discussion and limitations（0.6 页）：measurement–control gap；非线性 transport；类非共享几何。
9. Conclusion（0.3 页）。
补充材料：全部证明、仿真协议、EEG 实现细节、BTTA-DG 核查、V2P_WEIGHTED 全表、可复现性清单。

---

## 9. 时间表（从 10 月初算，约 9–10 周）

| 周 | 本地（理论 + 仿真 + 写作） | 服务器（只读/CPU，必要时 GPU） |
|---|---|---|
| 1 | 冻结本方案；T5/T6 推导 + sympy 账本；S2/S3/S6 | 发出只读提取请求（最终轮 per-subject、迭代日志、dump 清单） |
| 2 | T4 推导；S5 重跑；三旋钮图 | 6.2 MI 家族表（CPU on dump）；6.3 M3 变量 |
| 3 | 第 3、4 节初稿 | Sleep k 扫描 / α 路径；Stage-2 Sleep 门控 |
| 4 | 第 5、6 节初稿 | M4 MI 半分割；6.6 全协方差仿射 |
| 5 | 第 7 节初稿（用 CPU 结果） | CMMN（GPU，可选）；T-TIME（可选） |
| 6 | 全文合并，控制到 13 页 | 复核所有 CI 与表格 |
| 7 | 内部红队（按 `P14_PREWRITE_RED_TEAM` 模式）；补充材料 | 产物哈希与清单 |
| 8–9 | 修改、定稿、投稿（12 月上旬） | — |

---

## 10. 风险与止损规则（事先写好，避免结果导向改叙事）

1. **MI 上 FP−Joint 配对 CI 含 0（大概率）。** 照实报告；正文用 T6(b) 解释；
   FP 的价值改为"良定的估计目标 + 协议信息的使用"，证据在 Sleep 与 P13。
2. **Sleep k 扫描不复现 one-shot > 迭代。** T6(a) 只保留理论与仿真；真实数据段按实际写；
   仍可用 REVIEW_P0 的 0.695 vs 0.656 作为一次冻结运行的记录并说明差异来源。
3. **服务器无法给出最终轮被试级数据。** 在 dump 上重算整张表（CPU），数字会变，
   在补充材料写明与 AAAI 投稿版的差异。期刊版不需要与会议版数字一致。
4. **V2P 新旧版本冲突。** 只用 REVIEW_P0 修正版；oracle 位移写成"几何非共享"的错定诊断，不硬套 1−κ(t)。
5. **TSP 编辑认为范围偏 ML。** 立即转 TNNLS（同一稿，改摘要口径）；不要回头去 TPAMI。
6. **多类严格收敛仍不达标。** 报告 residual-qualified 结果并说明；T4 的理论不依赖仿真。

---

## 11. 产物索引

| 内容 | 位置 |
|---|---|
| AAAI 最终稿源码 | `FP-GEM_AAAI2027/submission_2026-07-28/`（main_submit_ready.tex 等） |
| 22 页长版理论与 W1/W2/V2P 叙述 | `AAAI_CMI/When_Alignment_Chases_Prevalence_final(1).pdf` |
| 本地仿真 | `convergence_sim/`, `mechanism_sim/`, `multiclass_sim/`, `optimal_sim/`, `version_b_optimal/` |
| 新理论预检 | `journal_revision/prechecks/precheck_theory.py`（输出 `precheck_theory_output.txt`） |
| P12 头对头（per-subject） | 分支 `agent/fp-gem-stage2`，`h2cmi/results/fp_gem_main/` |
| P13 比例应力（per-subject） | 分支 `exp/h2cmi-wave0-mechanism` @ `b5fb515`，`h2cmi/results/fp_gem_prevalence/` |
| 方法故事冻结 / 证据层级 / 红队 | 同分支 @ `df47753`（`FINAL_FP_GEM_STORY_FREEZE.md`, `FP_GEM_EVIDENCE_HIERARCHY.md`, `P14_PREWRITE_RED_TEAM.md`） |
| REVIEW_P0（Sleep 75 人、W1 115 人、V2P_WEIGHTED） | 分支 `exp/h2cmi-review-p0-corrections`，`h2cmi/results/REVIEW_P0_RESULTS.md`, `review_p0.report.json` |
| Stage-2 两阶段 + 门控 | 分支 `agent/fp-gem-stage2`，`h2cmi/results/fp_gem_stage2/` |
| BTTA-DG 复现 | `h2cmi/results/W1B_REPRODUCTION.md` |
| Sleep 结果溯源 | `FP-GEM_AAAI2027/notes/sleep_result_provenance.md` |
| 服务器只读提取请求（已写好） | `submission_2026-07-28/SERVER_REPRO_CHECKLIST_REQUEST.md`, `rewrite/SERVER_AGENT_STATUS_QUERY.md` |
