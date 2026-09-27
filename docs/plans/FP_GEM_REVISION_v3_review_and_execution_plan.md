# FP-GEM 期刊版重构 v3：v2 评议、数学修正与实验执行方案

**工作标题：** *Prevalence Sensitivity and Geometry Recovery in Unlabeled EEG Alignment*  
**中文主题：** 无标签 EEG 对齐中的类别比例敏感性与几何恢复能力  
**日期：** 2026-09-26  
**文档性质：** 对 `REVISION_PLAN_v2_divergent.md` 的评议与整合修订建议。保留 v2 的 N1–N8 编号，以便逐项核对；不覆盖原文件，也不把未执行实验写成结果。  
**使用对象：** 作者、合作者、理论审阅者及服务器端实验 agent。

> **核心决定：接受 v2 的 E 主线，但把“比例敏感性”与“真实几何恢复”并列。**
>
> 不再以证明 FP-GEM 优于 Joint-GEM 为目标。研究的问题是：不同无标签对齐估计量如何响应类别比例与真实几何变化；这种响应由什么统计量、模型假设和优化过程决定；控制比例响应时，是否同时损失了几何恢复能力。
>
> v2 中的“端点二值最优”、联合 EM 的 `S(t)` 收敛率、多类别普遍 `t^4` 阶数，以及 oracle 位移的“当且仅当”解释不能直接使用。本文给出修正、反例及待完成的验证。

---

## 0. 阅读说明与证据状态

### 0.1 本文以什么为依据

本文依据用户提供的 v2 方案、AAAI 正文、技术补充材料、OpenReview 审稿意见，以及上一轮讨论形成的数学核对脚本与结果。文内采用以下来源标记；详细出处见第 17 节。

| 标记 | 来源 | 能支持什么 |
|---|---|---|
| `[V2]` | `REVISION_PLAN_v2_divergent.md` | 原方案的组织、主张、N1–N8 和实验设想 |
| `[MAIN]` | AAAI 投稿正文 | 原模型、定理、算法和正文报告的结果 |
| `[SUPP]` | AAAI 技术补充材料 | 原有证明、实现说明与原稿报告的完整数值 |
| `[REV]` | OpenReview 审稿意见 PDF | 人工评审及 AI review 实际提出的问题 |
| `[CHECK]` | `fpgem_v2_math_checks.py` 与对应 JSON | 指定总体模型的确定性积分、有限差分和风险计算 |
| `[DERIVATION]` | 本轮讨论中的推导或反例 | 本文明确列出条件的数学分析，不是论文已发表结论 |
| `[PLAN]` | 本文新增的研究与执行建议 | 尚未执行，不代表方法已有效或定理已证明 |

**必须区分三类证据：**

1. 原文写有某个结果，只能先表述为“原稿报告”；能否由现存产物重建，属于 G0 的追溯任务。
2. 指定高斯总体模型中的推导与数值核对，不等于真实 EEG 机制已经得到验证。
3. 仓库分支名称、旧总结和已有讨论，不等于对应原始数据、配置及实现已经逐项复核。

### 0.2 本次实际完成的核对

本次写文档时，重新运行了已有 `fpgem_v2_math_checks.py`，输出与已提供的 `fpgem_v2_math_checks.json` 完全一致。该脚本仅检查指定数学模型，**没有训练 EEG 模型，没有重新运行服务器实验，也没有重新审计 GitHub 当前分支**。

核对范围包括：二分类模型的积分与 EM 速率数值；三分类已知协方差模型的 Fisher 积分；固定先验有限迭代的双响应有限差分；一个内部收缩严格优于两端点的风险反例。精确覆盖与限制见附录 A。

文档提及的 `optimal_sim`、CSC atlas、P13、V2P_WEIGHTED、B2b 和其他旧实验，除上述来源已经直接提供的内容外，均保留为**待追溯的项目线索**。不得把本文转成这些结果已经重新核验的声明。

---

## 1. 总体判断：采纳主线，不采纳未经证明的结论

### 1.1 为什么接受 E 主线

v2 建议把 EA、Riemannian re-centering、SPD 归一化、谱对齐和 GEM 视为从类别混合分布中计算对齐映射的不同估计量，并把 FP-GEM 放回这个家族中的一个端点。这个调整值得保留。[V2, §0–§1]

它把研究问题从：

> 怎样进一步提高或解释 FP-GEM？

转成：

> 无标签批次的类别组成怎样影响对齐？这种影响何时只是统计量改变，何时会妨碍恢复真实几何，又何时会影响任务预测？

这更直接回应了审稿意见中的现实机制、适用前提与方法定位问题。[REV, 人工评审 yczf/hTrM；AI review 的机制与 matched no-GEM 意见]

### 1.2 对原三条路线的安排

| 路线 | v3 的处理 |
|---|---|
| E：跨对齐算子的比例响应 | 作为论文骨架，但新增几何恢复这一配对维度 |
| A：估计量家族与迭代分析 | 保留，承担具体可计算模型与优化机制分析 |
| B：不确定先验下的约束 | 保留为估计量比较与偏差—方差问题；不预设方向性约束必然有效 |

二分类先验只有一个自由度，因此所谓方向性先验约束会退化为标量问题。这个批评成立。但是，“退化为标量收缩”**不推出**“内部收缩没有价值”或“两端点 minimax 最优”。第 5 节给出反例。

### 1.3 新的中心问题

建议收束为四个研究问题，而不是同时推动八个相互依赖的大定理。

**RQ1：比例响应。** 在类别条件分布固定时，改变目标类别比例，各个对齐统计量、变换及预测如何变化？

**RQ2：几何恢复。** 同一个估计量对已知、可恢复的几何扰动响应多强？降低比例响应是否只是降低适应强度？

**RQ3：失配与优化。** 真实响应偏离理论时，原因是密度错设、共享几何不成立、惩罚、有限样本、上游归一化，还是未收敛？

**RQ4：先验信息。** 已知或不确定的协议比例，怎样改变估计风险？固定、收缩和自由估计各自适用于什么条件？

这些是研究问题，不是已经确认的结果。

---

## 2. 审稿问题与大修产物的对应

| 审稿问题 | 原稿证据的局限 | v3 应交付的产物 |
|---|---|---|
| FP 相对 Joint 的小幅提升是否稳定？ | 主要报告均值；缺少完整受试者配对不确定性 | 受试者配对差值、区间、胜/平/负及完整覆盖记录 |
| GEM 是否具有净收益？ | 其他行与 GEM 使用不同 readout，不能替代严格 No-GEM | 同 checkpoint、同 readout、同上游归一化的 No-GEM 对照 |
| 比例前提是否合理？ | cue schedule 不等于伪迹剔除、划分后的实际比例 | 事后审计 `rho_A`、`rho_E`、参考比例及样本保留过程 |
| 真实 EEG 是否出现 prior–geometry 机制？ | 仅凭最终准确率不能定位原因 | 比例干预、几何干预、拟合轨迹和局部导数校准 |
| 是否只是简化 Gaussian affine 的现象？ | 原量化理论主要在受限模型中 | 逐算子的矩阵/谱响应推导，以及至少两个实际算子验证 |
| 先验不可靠时如何处理？ | 固定先验的适用条件偏窄 | 完整固定—收缩—联合比较；不提前宣称安全门控 |
| 较早适应、较晚评估是否引入额外漂移？ | 同分布分析不能解释全部跨时间变化 | 同一分布附近的机制实验与自然跨时间迁移分开 |

来源：[REV, yczf Weaknesses/Specific Points；hTrM Weaknesses/Specific Points；AI review Weaknesses/Suggestions]。

**修稿原则：** 统计补齐解决“可信度”；跨算子分析与双响应解决“研究贡献”；二者缺一不可。

---

## 3. N1–N8 的逐项处置表

| 编号 | v2 的中心提议 | v3 决定 | 必须修改的内容 |
|---|---|---|---|
| N1 | 统一比例敏感性泛函 | 保留为核心 | 各方法使用自己的估计方程；删除统一方差排序；区分真实比例、fitting prior、有限迭代 |
| N2 | SPD、EA、谱空间推广 | 保留为核心 | 逐算子求导；不能把类条件矩差直接当成最终变换的导数 |
| N3 | 混淆方向与位移分解 | 降为模型相关诊断 | 删除“任意估计量在正交方向不变”；明确坐标、度量、符号与秩 |
| N4 | oracle 位移诊断类相关几何 | 保留但重写 | 删除“当且仅当”；共同几何加正则也可产生比例响应 |
| N5 | 容忍半径、端点二值最优 | 撤回端点最优命题 | 半径只保留为两个指定端点的局部 MSE 交叉近似 |
| N6 | 迭代深度与 EM 收缩 | 修正后重点保留 | 联合慢速率为 `(1+t^2)S(t)`；新增几何恢复与比例响应的联动 |
| N7 | 无标签可辨识度计和门控 | 降为探索诊断 | 不统一解释 Stage-2 与 B2b；不由低曲率推出 universal uniform fallback |
| N8 | 多类别统一 `t^4` | 撤回普遍阶数并重推 | 锁定 nuisance 集；三分类已知协方差平移模型出现 `t^2` 主导项 |

以上处置针对 `[V2, §3.2–§3.9]`，不是否定原稿已有的二分类定理。

---

## 4. 先锁定对象：三个导数、两个响应、一套坐标约定

### 4.1 概率模型与三种类别权重

沿用原稿：冻结源表示与类条件密度，目标到源的变换为 `T_theta`，

$$
q_{\theta,y}(u)=|\det\nabla T_\theta(u)|p_y(T_\theta(u)),
\qquad
m_{\theta,\pi}(u)=\sum_y\pi_yq_{\theta,y}(u).
$$

必须继续区分：

$$
\rho_T\;\text{真实目标比例},\qquad
\pi_{\mathrm{fit}}\;\text{几何拟合权重},\qquad
\pi_{\mathrm{dec}}\;\text{决策权重}.
$$

再将协议或存储参考写作 `pi_ref`。它可以来自源训练比例或采集协议，但必须记录来源，不自动把两者视为相同。[MAIN, §3.1]

### 4.2 三个不能混用的导数

| 对象 | 改变什么 | 固定什么 | 含义 |
|---|---|---|---|
| 真实比例响应 | 数据生成/经验分布中的 `rho` | 各类条件分布、方法及超参数 | 算法怎样响应样本组成 |
| fitting-prior 响应 | 同一个批次上的 `eta_fit` | 目标数据分布 | 原稿 Proposition 3 / S7 的对象 |
| 迭代响应 | 更新次数、步长或约束 | 数据与初始化 | 有限预算算法怎样接近某个解 |

它们不是同一个导数，不能仅因都涉及“prior”而共用符号或数值。

### 4.3 一般比例响应

设方法 `A` 的总体估计量由

$$
\mathbb E_{P_\rho}[\psi_{\mathcal A}(X,\theta)]=0,
\qquad
P_\rho=\sum_{y=1}^K\rho_yP_y
$$

定义。以第 `K` 类为参考，`rho_K=1-sum_{k<K}rho_k`。在可微、可交换导数与积分、局部解唯一且导数矩阵可逆的条件下，令

$$
H_{\mathcal A}
=\mathbb E_{P_\rho}[\partial_\theta\psi_{\mathcal A}(X,\theta^*)],
$$

则

$$
\boxed{
\frac{\partial\theta^*_{\mathcal A}}{\partial\rho_k}
=-H_{\mathcal A}^{-1}
\left(
\mathbb E_{P_k}\psi_{\mathcal A}
-
\mathbb E_{P_K}\psi_{\mathcal A}
\right).
}
$$

若估计方程还显式依赖 `rho`，需另外保留其显式导数，不能使用上式的简化版本。[DERIVATION；对应 V2 的 N1]

**统一的是计算规则，不是所有算法共享同一个斜率。** EA、Fréchet 均值、密度拟合和信息最大化有不同的 `psi`、不同的曲率和不同的参数空间。

固定惩罚可以并入估计方程，但会改变其解、响应和方差。有限步方法不是自动满足驻点条件的 M 估计量；集合边界处也可能只有分段或方向导数。

### 4.4 方差不允许统一写成 inverse Fisher

对满足适用条件的 iid M 估计量，局部协方差形式为

$$
\frac1nH^{-1}VH^{-\top},
\qquad
V=\operatorname{Var}[\psi(X,\theta^*)].
$$

只有在对应的正确指定 likelihood 与正则条件下，才能化简为 inverse Fisher。固定惩罚、密度错设、已估计的源密度和时间相关样本都需要分别处理。[SUPP, Proposition S8；DERIVATION]

删除 v2 表格中未经限定的“pooled 方差最小”“one-shot 方差小”“约束方差一定介于两者”等标签。每格方差都必须有自己的估计对象与条件。

### 4.5 必须同时定义几何恢复

令 `g` 参数化真实、可恢复的几何变化，并在匹配参考点附近定义

$$
G_{\mathcal A}=\frac{\partial\theta^*_{\mathcal A}}{\partial g},
\qquad
B_{\mathcal A}=\frac{\partial\theta^*_{\mathcal A}}{\partial\rho}.
$$

在估计参数与真实几何使用同一可识别坐标时，理想恢复要求 `G_A` 接近恒等，而不是只要求 `B_A` 小。

对于不同空间的算子，`G_A` 与 `B_A` 不能直接按欧氏参数范数混合排名。必须先定义共同的作用空间、指定探针上的变换效果，或任务相关输出差异。恒等算法的 `B=0` 并不说明它能恢复几何。

---

## 5. N5 修正：内部收缩可以严格优于两端点

### 5.1 v2 需要撤回的命题

v2 拟写“局部、正确指定条件下，先验参与旋钮的最优位置在 `{0,1}`”。这些条件不足以支持该命题。[V2, §3.6]

### 5.2 一个完整的正则高斯反例

考虑

$$
X=a+c\,d+\varepsilon_0,
\qquad
Z=d+\varepsilon_1,
$$

其中 `a` 是几何参数，`d in [-r,r]` 是先验相关 nuisance 偏离，`c != 0`；两噪声独立高斯，方差分别为 `v_0,v_1>0`。

比较连续估计量族

$$
\widehat a_\alpha=X-c\alpha Z,
\qquad 0\le\alpha\le1.
$$

两个端点分别对应不校正与完全利用 nuisance 估计。最坏情形平方风险为

$$
\sup_{|d|\le r}
\mathbb E(\widehat a_\alpha-a)^2
=v_0+c^2\left[(1-\alpha)^2r^2+\alpha^2v_1\right].
$$

直接最小化得到

$$
\boxed{\alpha^*=\frac{r^2}{r^2+v_1}},
$$

只要 `r>0` 且 `v_1>0`，它位于内部，且该族内最坏风险严格低于两个端点。[DERIVATION]

例如：

| 参数/结果 | 数值 |
|---|---:|
| `v_0` | 0.01 |
| `v_1` | 0.04 |
| `r` | 0.2 |
| `c` | 1 |
| 最优内部 `alpha` | 0.5 |
| `alpha=0` 最坏风险 | 0.05 |
| `alpha=1` 最坏风险 | 0.05 |
| `alpha=0.5` 最坏风险 | 0.03 |

这些数字由 `[CHECK]` 复算。它们说明一般端点最优结论不成立；**不表示已证明某个具体 GEM 收缩实现优于 FP-GEM，也不表示已求出所有可能估计量上的全局 minimax 解。**

### 5.3 容忍半径可以怎样保留

二分类局部模型中，若仅比较两个指定端点，并以 `delta=rho_+-1/2` 为失配坐标，可以考虑

$$
\delta^*(t,n)
=
\frac{\sqrt{I_{a|\eta}^{-1}/n-I_{aa}^{-1}/n}}
{|A(t)|}.
$$

它是“固定先验的局部平方偏差”与“联合估计额外方差”相等的近似交叉点。二分类弱分离首项为

$$
\delta^*(t,n)\sim\sqrt{\frac{3}{8n}}t^{-3}.
$$

允许称为：**两个端点的局部 MSE 交叉近似**。

不允许称为：整个估计量家族的最优半径、无标签安全阈值或已经证明的 minimax 分界。半径超过可行比例范围也不意味着整个范围都安全；可能只是局部和渐近近似已经不能用于这种解释。[SUPP, S8、S15；DERIVATION]

`optimal_sim` 中某些内部点未显著优于端点，只能在核对后报告为该网格的经验结果。不能由“未显著”推出内部解没有价值。

---

## 6. N6 修正：联合 EM 的慢速率与有限迭代双响应

### 6.1 明确分析的模型

只分析已知类条件方差与均值间距、未知共享平移及二分类先验的模型：

$$
m_{a,\eta}(x)
=\sigma(\eta)\phi(x+a-t)
+[1-\sigma(\eta)]\phi(x+a+t).
$$

`T_a(x)=x+a` 是目标到源的平移；`t>0`；基点为 `(a,eta)=(0,0)`。

令

$$
H(x)=\tanh(tx),
\qquad
S(t)=\mathbb E_{m_{0,0}}[\operatorname{sech}^2(tX)].
$$

原稿已给出

$$
I_{aa}=1-t^2S,
\quad I_{a\eta}=-\frac{tS}{2},
\quad I_{\eta\eta}=\frac{1-S}{4}.
$$

以及

$$
S(t)=1-t^2+t^4-\frac53t^6+O(t^8).
$$

来源：[MAIN, §3.4；SUPP, S15]。

### 6.2 三种更新问题必须分开

| 更新问题 | 局部速率 |
|---|---:|
| 几何已知，只更新先验 | `S(t)` |
| 先验固定，只更新平移 | `t^2 S(t)` |
| 平移与先验使用同一次 E-step，分别做精确 M-step | `(1+t^2)S(t)` 的联合慢方向 |

对最后一项，精确总体更新是

$$
a^+=t\,\mathbb E[\tanh(t(X+a)+\eta/2)]-\mathbb E[X],
$$

$$
\eta^+=\operatorname{logit}\!\left(
\frac{1+\mathbb E[\tanh(t(X+a)+\eta/2)]}{2}
\right).
$$

在基点求导得到

$$
\boxed{
J_{\mathrm{EM}}
=S(t)
\begin{pmatrix}
t^2&t/2\\
2t&1
\end{pmatrix}.
}
$$

两个特征值为 `0` 与

$$
\boxed{\lambda_{\mathrm{slow}}=(1+t^2)S(t)
=1-\frac23t^6+O(t^8)}.
$$

这是完整联合更新的局部慢速率。v2 将固定几何时的 `S(t)` 误用于联合过程，需要修正。[DERIVATION；V2, §3.7]

### 6.3 数值大小与解释边界

在 `t=0.35`，确定性积分给出：

| 项目 | 数值 |
|---|---:|
| `S(t)` | 0.8901398309 |
| `(1+t^2)S(t)` | 0.9991819602 |
| 已知几何时，局部误差减少 90% 的估算轮数 | 19.79 |
| 联合慢方向，局部误差减少 90% 的估算轮数 | 2813.61 |

轮数按 `log(0.1)/log(lambda)` 计算，是局部线性化结果。它不是任意初始化下的实际总耗时，也不是包含尺度、Student-t 密度、伪计数或有限步 Adam 的高维代码的直接结论。[CHECK]

原补充材料本来就报告过弱分离下较长的严格 EM 轨迹；这些结果可以作为后续追溯对象，不能把本节的平移模型速率直接等同于原四维 affine 实验的速率。[SUPP, F.5、Table S4]

**对服务器的要求：** 分别记录实际更新映射、梯度、目标变化、先验变化和边界命中；不能只因最终先验接近初始化就宣布“弱可辨识导致先验不动”。

### 6.4 新增双响应：提前停止并不自动改善辨别能力

令真实目标到源平移为 `g`，数据由

$$
U\mid Y=y\sim\mathcal N(yt-g,1),
\qquad \Pr(Y=+1)=\frac12+\delta
$$

生成。固定 fitting prior 为 `1/2`，从 `a_0=0` 开始精确总体 EM。写

$$
r_t=t^2S(t),\qquad 0<r_t<1.
$$

在 `(g,delta)=(0,0)` 附近，一阶更新满足

$$
a_{j+1}
=r_ta_j+(1-r_t)g-2tS(t)\delta
+\text{高阶项}.
$$

因此对任意固定正整数 `k`，

$$
\boxed{G_k=\frac{\partial a_k}{\partial g}=1-r_t^k},
$$

$$
\boxed{
B_k=\frac{\partial a_k}{\partial\delta}
=-\frac{2tS(t)}{1-r_t}(1-r_t^k).
}
$$

于是

$$
\boxed{\frac{B_k}{G_k}=-\frac{2tS(t)}{1-r_t}},
$$

在这个指定局部模型中不随迭代深度变化。[DERIVATION]

`t=0.5` 的核对如下：

| `k` | 几何响应 `G_k` | 比例响应 `B_k` | `B_k/G_k` |
|---:|---:|---:|---:|
| 1 | 0.8010135664 | −0.7959457344 | −0.9936732257 |
| 3 | 0.9921210126 | −0.9858440869 | −0.9936732257 |
| 20 | 约 1 | −0.9936732257 | −0.9936732257 |

公式与总体更新的中心有限差分相符，具体误差保存在 `[CHECK]` 中。

**正确解释：** 少迭代减少比例引起的移动，同时也减少对真实几何的恢复。有限迭代仍可能改变有限样本风险，但不能仅凭位移较小就称其“更能区分比例与几何”。

### 6.5 修订后的局部比较表

以下仅针对本节的平移模型、匹配基点和总体一阶响应，不是 EA/SPD/CMMN 的通用排序。

| 估计量 | `G`：真实平移响应 | `B`：真实比例响应 | 主要边界 |
|---|---:|---:|---|
| 恒等，不适应 | 0 | 0 | 完全没有几何恢复 |
| pooled mean 对齐到零均值 | 1 | `−2t` | 比例与均值混合 |
| one-shot 固定 prior | `1−r_t` | `−2tS(t)` | 不等于收敛 FP |
| `k` 轮固定 prior | `1−r_t^k` | `−2tS(t)(1−r_t^k)/(1−r_t)` | 两种响应同步变化 |
| 收敛固定 prior | 1 | `−2tS(t)/(1−r_t)` | 错误 prior 引入总体偏差 |
| 正确指定、可识别、充分求解的自由联合 | 1 | 0 | 有限样本方差和优化可能严重恶化 |

这里使用有符号导数。原稿 `A(t)` 为负；不能将绝对值斜率与有符号响应混在同一公式里。[MAIN, Theorem 6；SUPP, S14–S15；DERIVATION]

---

## 7. N8 修正：多类别阶数取决于类别配置和 nuisance 集

### 7.1 当前不能接受的外推

v2 将正单纯形的多类模型直接写成：类均值差张成空间内一律 `O(t^4)`，并声称已验证 `K=3,4,5`。[V2, §3.9]

在没有写清协方差、尺度、平移及其他 nuisance 是否参与拟合之前，这不是完整命题。二分类的对称性不能直接外推到所有多类配置。

### 7.2 一个必须纳入回归测试的三分类模型

设

$$
X\mid Y=y\sim\mathcal N(tv_y,I_2),\qquad\Pr(Y=y)=1/3,
$$

$$
v_1=(1,0),\quad
v_2=(-1/2,\sqrt3/2),\quad
v_3=(-1/2,-\sqrt3/2).
$$

协方差和 `t` 已知；未知量只有二维共同平移以及两个独立先验 logits。对先验剖面化后，本轮受限模型推导为

$$
\boxed{I_{a|\eta}(t)=\frac{t^2}{4}I_2+O(t^4)}.
$$

它不是二分类的 `t^4` 主导阶。[DERIVATION]

确定性 Gauss–Hermite 积分的代表值：

| `t` | 剖面平移信息特征值（两个相同至数值误差） | 特征值除以 `t^2` |
|---:|---:|---:|
| 0.10 | 0.0024817367 | 0.2481736685 |
| 0.05 | 0.0006238359 | 0.2495343538 |
| 0.025 | 0.0001561769 | 0.2498830075 |

减半 `t` 后信息约缩小四倍，与 `t^2/4` 主项一致。[CHECK]

### 7.3 主项的简要推导

在该模型中，令 `r_y(x)` 为平衡 posterior，`m(x)=sum_y r_y(x)v_y`。softmax 展开给出

$$
m(x)
=\frac t2x+
\frac{t^2}{8}
\begin{pmatrix}
x_1^2-x_2^2\\-2x_1x_2
\end{pmatrix}
+O(t^3).
$$

两个先验 score 的张成空间等于 `m(x)` 两个分量的张成空间。将其缩放为 `(2/t)m(x)`，平移 score 的线性项被投影去除，领先残差为

$$
\frac t4
\begin{pmatrix}
x_1^2-x_2^2\\-2x_1x_2
\end{pmatrix}.
$$

在极限标准二维高斯分布下，这两个二次项的协方差矩阵为 `4 I_2`，得到 `t^2 I_2/4` 主项。由 `t` 变号对应整体反射，剖面平移信息的展开为偶函数；严格余项控制仍需整理进正式证明。

这段推导与数值积分支持**上述锁定模型**，不支持所有 `K`、所有变换族或未知协方差的统一定理。

### 7.4 新研究任务

将 N8 改为：**类别配置的对称性与 nuisance 选择怎样决定信息损失阶数？**

先分别研究已知协方差的共享平移、加入共同尺度、加入对角尺度、再加入更一般协方差。每一层单独定义 score 与 Schur complement，不能在不同模型之间移用阶数。

正式多类证明与独立数值复核完成前，该部分不承担摘要主张。

---

## 8. N3/N4/N7：诊断可以保留，唯一归因与部署保证需要撤回

### 8.1 N3：混淆子空间是模型相关对象

在正确指定、无惩罚的局部 likelihood 下，可以定义

$$
\mathcal V
=\operatorname{col}(I_{\theta\theta}^{-1}I_{\theta\eta}).
$$

这里是子空间定义，整体符号不影响子空间。若讨论固定数据分布上的有符号 fitting-prior 导数，则应使用

$$
D_{\mathrm{fit}}
=-H_{\theta\theta}^{-1}L_{\theta\eta}
=-I_{\theta\theta}^{-1}I_{\theta\eta}
$$

的正确指定无罚特例；有惩罚或错设时使用实际 Hessian 和交叉导数。[SUPP, S7；DERIVATION]

它描述的是**指定模型内部，先验与几何可局部补偿的方向**，不是所有无标签算法的共同响应空间。

因此删除以下两项：[V2, §3.4]

- 任意估计量的比例响应都只发生在 `V` 内。
- `V` 的正交分量必然来自真实几何，或对比例扰动一阶不变。

模型投影不是因果来源分解。

多类时该空间的秩至多为 `K−1`，也受几何维数与交叉信息秩限制，不保证恰好为 `K−1`。

若计算位移投影，需声明正定度量 `M`。取列基矩阵 `V`，可使用

$$
P_{\mathcal V}^{M}
=V(V^\top MV)^\dagger V^\top M.
$$

分母位移为零时投影比例记为 `NA`，不能强行解释。不同参数空间需先定义对应关系。

`csc` 中的 atlas 是否与此对象相同，必须核对构造、坐标、目标函数与数据。现在不能直接复用为“同一对象”。[V2, §6；PLAN]

### 8.2 N4：oracle 位移不等价于类相关几何

原稿 S12 的准确内容是：在共同模型正确指定、共享变换可识别、各类权重为正且无额外惩罚的总体目标中，最优共享变换对这些权重不变。**最优参数不变，不代表目标函数的数值不随权重改变。**[SUPP, S12]

v2 的“oracle 位移非零，当且仅当几何跨类不共享”需要撤回。[V2, §3.5]

反例：所有类别共享真实位置 `a_0`，类噪声方差不同，oracle 拟合带固定 ridge 惩罚：

$$
\mathcal R_w(a)
=\frac12\sum_yw_y\frac{(a-a_0)^2}{\sigma_y^2}
+\frac\lambda2a^2.
$$

令 `c(w)=sum_y w_y/sigma_y^2`，则

$$
\widehat a(w)=\frac{c(w)}{c(w)+\lambda}a_0.
$$

当方差不同、`a_0 != 0`、`lambda>0` 时，参数随权重移动，但真实几何仍然完全共享。[DERIVATION]

有限样本、密度错设、权重归一化变化及未收敛也能产生类似现象。反过来，类相关几何存在也不保证在所测试的权重方向上观察到非零移动。

**保留的诊断逻辑：** oracle 比例敏感性说明 S12 的模型、总体条件或实现条件中至少有一项没有被满足。类相关几何是候选解释，需与正则、错设、样本和优化等因素对照。

另外，固定 `pi_fit` 不等于固定每类在实际目标中的贡献。目标数据分布仍随 `rho_T` 变化，因此不能说 FP 自动把类相关几何的折中“钉在源权重上”。

### 8.3 N7：已知几何和联合估计的信息不同

原模型给出

$$
I_{\eta\eta}=\frac{1-S(t)}4=O(t^2),
$$

$$
I_{\eta|a}
=\frac{1-(1+t^2)S(t)}{4[1-t^2S(t)]}
=\frac16t^6+O(t^8).
$$

第一项是几何已知时的先验信息，第二项才是允许平移作为 nuisance 后的剩余信息。[MAIN, §3.4；SUPP, S15]

Stage-2 将几何冻结后，不能直接沿用第二项解释比例估计或 gate 的失败。估计几何误差的传播仍然重要，但必须另行分析。

同样，B2b 的某个 evidence score 低功效只证明该 score 在相应设计中的表现；没有连接到有效 score 或信息下界之前，不能提升为所有目标统计量的无功效结论。

### 8.4 可辨识度诊断的允许用途

可以探索：未惩罚剖面曲率、归一化耦合谱、实际样本量、有效样本量、责任分配熵及参数不确定性之间的关系。

不能直接部署“曲率小于某值就统一回退 uniform”的规则。需要先说明：

- 曲率针对什么参数化、什么 nuisance 集、什么拟合点；
- 样本量和源密度估计误差如何进入；
- 密度错设或 Hessian 非正定如何处理；
- 该规则对应哪个任务风险，而不是仅对应 likelihood。

对于正确类条件密度下的 balanced accuracy，uniform **decision weights** 有 S9 的依据；对于普通 accuracy 或未经校正的 discriminative posterior，没有相同的 universal fallback 保证。[SUPP, S9]

v3 中 N7 的状态是：**探索诊断，不是已授权的安全门控。**

---

## 9. N2 的具体化：逐个统计量、逐个映射求导

本节给出应研究的指定统计对象。它们是推导与实现核对的规范，不表示已复核所有官方代码。

### 9.1 EA：平均二阶矩与白化矩阵不是同一个对象

设每个 trial 的实际二阶统计为 `R_i`，包括实现所使用的去均值、归一化和 shrinkage 约定。定义

$$
R_y=\mathbb E[R_i\mid Y=y],\qquad
R(\rho)=\sum_y\rho_yR_y.
$$

则

$$
\partial_{\rho_k}R=R_k-R_K.
$$

如果白化矩阵为 `W=R^{-1/2}`，则必须继续求矩阵函数导数。若 `R=U diag(lambda_i) U^T`，

$$
\dot W
=U\left[F\odot(U^\top\dot R U)\right]U^\top,
$$

$$
F_{ij}=
\begin{cases}
\dfrac{\lambda_i^{-1/2}-\lambda_j^{-1/2}}{\lambda_i-\lambda_j},&\lambda_i\ne\lambda_j,\\[6pt]
-\dfrac12\lambda_i^{-3/2},&\lambda_i=\lambda_j.
\end{cases}
$$

不能默认矩阵可交换，再套用标量幂函数公式。[DERIVATION；对应 V2 N2]

若实现对齐的是 pooled 向量中心协方差，则须使用

$$
C(\rho)=\sum_y\rho_y(C_y+\mu_y\mu_y^\top)-\mu_\rho\mu_\rho^\top
$$

及其完整导数。这与“先计算每个去均值 trial 的协方差，再跨 trials 平均”不是同一统计对象。

一个简单反例足以说明为什么不能统一斜率：在一维对称高斯 `N(±t,1)` 中，均值随比例变化，而二阶矩 `1+t^2` 不变。pooled 均值响应 `−2t` 不能直接写到 EA 二阶矩白化那一行。[DERIVATION]

### 9.2 SPD：区分 log-Euclidean 与 affine-invariant

对于明确采用 log-Euclidean 均值的对象，令

$$
L_y=\mathbb E[\log C\mid Y=y],
\qquad M_{LE}(\rho)=\exp\left(\sum_y\rho_yL_y\right).
$$

则在 log 坐标中

$$
\partial_{\rho_k}\log M_{LE}=L_k-L_K.
$$

实际重中心化映射仍需经过矩阵指数、平方根/逆平方根和复合映射的导数。

对于 affine-invariant Fréchet 均值，应从它自己的切空间最优性条件出发，计算切空间 Hessian 与类别分布变化项。不得将 log-Euclidean 的等式当作精确 AIRM 公式。

实际 RCT/SPD normalization 还可能包含离散训练状态、特征变换或缩放参数。先核对它究竟拟合什么，再映射到理论对象。[V2, §3.3；PLAN]

### 9.3 谱对齐：比例改变目标 PSD，再影响滤波器

先锁定一个标量、冻结参考谱的模型：

$$
S_\rho(\omega)=\sum_y\rho_yS_y(\omega),
\qquad
H_\rho(\omega)=\sqrt{\frac{S_{\mathrm{ref}}(\omega)}{S_\rho(\omega)}}.
$$

在谱为正、参考固定且类别条件谱不变时，

$$
\boxed{
\partial_{\rho_k}\log H_\rho(\omega)
=-\frac{S_k(\omega)-S_K(\omega)}{2S_\rho(\omega)}.
}
$$

这是可以直接通过比例干预检查的频率响应公式。[DERIVATION]

实际 CMMN 的 PSD 聚合、源 barycenter、通道处理、谱平滑及稳定化必须另行对照。只有实现吻合时，才能把该简化式标为该实现的预测；否则需加入实际变换的导数。[V2, §3.3；MAIN, Related Work 中的 CMMN 引用]

### 9.4 BN 扩展的范围

BN 均值、方差重估计可以作为混合统计量响应的附加对象。但不能把这部分矩分析当作整个 Tent 的闭式理论，因为后者还涉及实际参数优化。

该扩展降为可选，不应在 EEG 主体仍未闭环时成为必须完成的额外项目。[V2, L6；PLAN]

---

## 10. G0：结果追溯与参考实现，先于新的大规模实验

### 10.1 不能把“发现一套不一致实现”直接写成“旧论文数字全部错误”

既有审阅发现了投稿规格与部分 P12 同名实验在类别数、密度、readout、prior 更新、优化和划分上的差异。v2 据此要求建立追溯表，这项工作必须保留。[V2, §7]

但在每个旧表单元格映射完成前，只能写：**投稿规格与已检查的某些实现存在差异。** 不能推定所有旧数字均来自那套实现，也不能把另一实现的区间直接补进旧表。

### 10.2 必须交付的两张清单

**`manuscript_result_map.csv`：**

```text
table_id,cell_id,dataset,label_set,method,reported_value,
commit,config_path,config_hash,split_manifest,split_hash,
source_checkpoint,checkpoint_hash,density_family,readout,
upstream_normalization,prior_update,optimizer,stopping_rule,
prediction_path,aggregation_script,reproduction_status,notes
```

`reproduction_status` 至少区分：`reproduced`、`located_not_recomputed`、`unresolved`、`known_different_implementation`。未解决的条目不能自动转成已证伪。

**`artifact_capability_matrix.csv`：**

```text
dataset,label_set,subject,seed,raw_signal_available,
pre_normalization_features_available,post_normalization_features_available,
source_density_available,source_validation_available,
checkpoint_available,trial_ids_available,split_available,
can_rerun_latent_adapter,can_rerun_spd_adapter,can_rerun_signal_adapter,
missing_dependency,artifact_hash
```

仅有最终 embeddings 时，不得承诺可以重跑上游 EA、RCT/SPDIM 或 CMMN。二分类 dump 不能通过开关变成四分类证据。

### 10.3 参考实现的最小接口

建议的新接口是设计规格，不是仓库已存在的函数声明：

```text
FrozenSourceBundle
  encoder / classifier / density / source references / preprocessing
  source training and validation manifests

AdaptInput
  target X or features / sample identifiers / admissible metadata
  no labels / no evaluation metrics

AdapterConfig
  transform / prior rule / penalty / optimizer / stopping / failure rule

AdapterOutput
  fitted state / trajectory / convergence flags / hashes

Evaluator
  predictions first, then labels and metrics
```

同一受试者、种子及划分下，所有受控方法共享完全相同的 frozen bundle。

### 10.4 方法族与必要对照

最小受控组保留：No-adaptation/No-GEM、一个 pooled 估计量、one-shot 固定 prior、收敛固定 prior、Pure Joint 和一个预先指定的收缩版本。

进一步扩展时，再加入锚定强度与集合半径路径。**Pure Joint 与 Anchored Joint 必须分名**；不允许都叫 Joint-GEM。

上游不更新和 Recenter 更新要分因子。GEM 若作用在 Recenter 之后，同头 Recenter 就是检验新增 GEM 净收益的关键对照，而不是仅用整个 source-only 管线作比较。[MAIN, §5.2；SUPP, H]

### 10.5 集合约束 M-step 必须定义正确

令 `bar_r` 为平均 responsibilities，精确 constrained prior M-step 是

$$
\pi^+
\in\arg\max_{\pi\in\mathcal U}
\sum_y\bar r_y\log\pi_y.
$$

等价于

$$
\pi^+\in\arg\min_{\pi\in\mathcal U}
\operatorname{KL}(\bar r\|\pi),
$$

而不是未说明度量的欧氏投影。[DERIVATION；V2, §4.1]

若使用 TV 球，明确 `TV(p,q)=0.5*||p-q||_1`、边界支持与数值下界。正向 KL 和反向 KL 不能交换。对精确/广义 EM，分别检查最优性或 surrogate 非下降；若不满足，就如实命名为一般优化算法，而不是默认享有 GEM 保证。

---

## 11. 实验计划：先做小闭环，再扩展算子矩阵

### 11.1 实验分层

| 层 | 目标 | 先做什么 | 不应提前做什么 |
|---|---|---|---|
| L1 数学与数值 | 检查公式、模型条件与优化 | 二分类、三分类、双响应、收缩反例 | 未锁定 nuisance 就跑大规模多类网格 |
| L2 真实数据受控干预 | 分别识别比例响应与注入几何恢复 | 一个 MI、一个 Sleep，小方法集 | 一次展开全部数据集与全部超参数 |
| L3 失配诊断 | 定位理论预测误差 | 惩罚、密度、优化、共享几何对照 | 先把所有反例归于类相关几何 |
| L4 自然迁移 | 评价完整管线效果 | 固定真实划分、同头基线、配对统计 | 用同分布公式解释全部跨时间漂移 |
| L5 决策层 | 分离拟合 prior 与 decision prior | 每个比例条件重拟几何后再校正 | 把两套预测的指标当成同一策略的保证 |
| L6 扩展 | 检验跨算子或跨 host 范围 | 根据 L1–L5 的缺口决定 | 以增加模型复杂度代替问题闭环 |

### 11.2 L1：本地数学回归与未完成项

保留已有 `[CHECK]` 作为基础回归；进一步补：

| 检查 | 当前状态 | 下一步 |
|---|---|---|
| 二分类 `S(t)`、Fisher 块和速率数值 | 已核对指定公式的积分与数值 | 加入完整总体 EM 映射 Jacobian 的独立有限差分 |
| 固定 prior 的 `G_k/B_k` | 已在 `t=0.5, k=1,3,20` 做总体差分 | 扩展 `t`、step size 与积分精度检查 |
| 内部收缩反例 | 有解析风险与数值核对 | 作为反例回归，不用作具体 GEM 胜出的证据 |
| 三类已知协方差平移模型 | 有局部展开与确定性 Fisher 积分 | 完成余项证明，并对不同积分阶数复核 |
| 多类未知尺度/协方差 | 未完成 | nuisance 逐级增加，单独建模 |
| 错设与固定惩罚 | 原方案提出，本文未复跑 | 使用适当 sandwich/经验方差，不沿用 unpenalized 方差 |

### 11.3 L2：比例与几何分开的干预设计

对同一 frozen source、同一受试者和同一基准池，分别设置：

| 条件 | 类别比例 | 注入几何 | 回答的问题 |
|---|---|---|---|
| C0 | 基准 | 无 | 恒等与数值回放 |
| CP | 改变 | 无 | 纯比例响应 |
| CG | 基准 | 改变 | 几何恢复 |
| CPG | 改变 | 改变 | 联合作用及交互 |

先用小幅、中心对称扰动测一阶导数；再用较大扰动探索非线性范围。建议的比例网格如 `0.1…0.9` 属于候选设计，不是已经冻结或执行的实验。

**纯机制层的评价集固定。** 改变 adaptation pool 的比例，不同时改变评价集来制造 accuracy 的机械变化。CG/CPG 的几何扰动施加到相应 adaptation 和评价输入，并保持样本标识可配对。

真实自然迁移时，`rho_A` 与 `rho_E` 可以不同，但该问题放在 L4/L5，不与 CP 的单一干预混合。

### 11.4 权重版与真实子采样版都保留，但解释不同

固定支持的加权版本便于隔离经验测度变化；真实子采样版本更接近实际有限样本批次。两者都记录

$$
n_{\mathrm{eff}}=\frac{(\sum_iw_i)^2}{\sum_iw_i^2},
$$

以及 `n_unique`、各类独立 trial 数、重复计数与时间块结构。

同一个 trial 重复多次不增加等量独立信息。时间相关数据也不能仅靠权重公式声称具有 iid 的有效样本量。

**标签使用边界：** 实验构造器可以用标签生成受控比例，但标签和标签相关权重不得作为额外特征交给 adapter。优先使用无标签的实际采样批次；加权诊断需隔离权重构造与算法输入，明确其为合成测度实验。封装加权归约不等于证明了真实部署协议，因此加权结果必须由真实抽样对照补充。

### 11.5 真实 EEG 中“恢复”能表示什么

在完整生成模型中，可以比较估计变换与已知真实变换。

在真实 EEG 中，给已有样本再施加一个已知可逆扰动，通常只知道**新增扰动**，不知道天然 source–target 之间的绝对真实几何。应把结果称为“已知注入扰动的增量恢复”，而不是“真实跨受试者几何已恢复”。

可在固定探针上比较

$$
\mathcal A(P_gA)(P_gx)
\quad\text{与}\quad
\mathcal A(A)(x),
$$

这里 `A` 表示基准 adaptation pool，`P_g` 表示已知注入算子；两边使用相同的固定读出/作用空间。该比较检验对新增扰动的校正一致性，其任务效用还需另报。

已知传感器变换经过 nonlinear encoder 后，不自动对应已知 latent affine 参数。跨空间恢复指标必须相应定义。

电极丢失、降秩重参考等不可逆操作不能与可逆几何恢复实验同名；可作为模型范围外的压力测试。

### 11.6 主要测量量

每格至少记录：

```text
proportion_response_prediction / proportion_response_observed
geometry_response_prediction / geometry_response_observed
transform_action_on_fixed_probes
class_margin_change / prediction_change
bacc / accuracy / class_recalls / nll
fitting_prior_trajectory / objective_trajectory / surrogate_trajectory
gradient_residual / convergence_status / boundary_hits
n_raw / n_unique / weight_effective_size / time_block_ids
```

概率指标必须对明确定义且统一校准的 posterior 报告。只给硬决策的方法不能编造 NLL。

对不同参数空间，不以原始参数范数直接排优劣。混淆子空间投影是补充诊断，不是独立恢复指标。

### 11.7 第一轮数据和方法范围

建议先选一个 MI 设置和一个 Sleep 设置。具体 MI 使用 B14 二分类还是 Lee，依据 G0 中的产物完整度、可执行性和预先声明的科学需求确定，不能依据哪套数据更容易出现所需排序确定。

Sleep 机制实验优先使用同一夜内、非重叠完整时间块；自然跨夜结果另报。不要把相邻窗口随机打散后当作独立样本。

第一轮方法集维持第 10.4 节的最小组。确认能解释响应及失败后，才扩展到四分类、更多算子、更多强度和确认数据。

---

## 12. 失配、优化与真实分层：禁止结果自动“支持故事”

### 12.1 Oracle 敏感性需要一个排查矩阵

若 oracle 按类拟合也随权重变化，优先依次检查：

| 因素 | 对照 | 目的 |
|---|---|---|
| 固定惩罚 | `lambda=0` 与预设惩罚路径 | 排除惩罚导致的权重依赖 |
| 有限样本 | 同支持重加权、样本增加、重复抽样 | 量化采样误差 |
| 优化 | 更严格驻点残差、确定性多起点、目标回放 | 排除未收敛和局部解切换 |
| 工作密度 | 同头条件下的指定密度变体 | 检查模型错设 |
| 共享几何 | 共享 `T` 与类别特定 `T_y` 的诊断拟合 | 检查共同变换假设 |
| 上游归一化 | 不更新与更新分别运行 | 定位偏差进入的层 |

这些属于诊断实验。类别特定 `T_y` 使用标签时是 oracle，不允许作为 label-free 方法入主表。

### 12.2 不能把未收敛样本删掉后继续报完整方法成功

每次求解区分：`stationary`、`budget_exhausted`、`boundary_solution`、`numerical_failure`。

性能表遵守预先定义的失败处理，例如回退恒等，同时保留失败率；科学分析表分别报告哪些单位满足相应定理条件。不能为获得某个方向而事后剔除失败单位。

同预算比较回答实际计算预算下的表现；严格驻点比较回答估计目标的差别。两张表都可以有价值，但不能互相替代。

### 12.3 分离度、模型表现和可辨识性不是同一量

删除把低 accuracy 组直接称为“BCI illiteracy 即弱可辨识 regime”的写法。[V2, L3]

至少区分：

- 任务可分性：指定表示/分类器能否区分类别；
- 密度辨别能力：工作密度的 responsibilities 是否有信息；
- 模型可辨识性：在声明的 nuisance 集下，先验与几何能否区分。

可以报告中性的“低任务可分性组”“低密度辨别能力组”，但不能用一个概念替换另外两个。

分组若使用目标标签，应明确为事后机制分析。分组定义与效果评价应使用分离的数据或外层交叉拟合，避免在同一结果上先定义差组、再报告差组改进。

### 12.4 不允许自动成立的解释

| 观察 | 不允许直接推出 | 正确处理 |
|---|---|---|
| FP 与 Joint 无显著差异 | 全域弱可辨识 | 查看区间、估计功效、实际更新、密度与约束 |
| one-shot 位移较小 | 更准确区分比例和几何 | 同时检查 `G` 和任务风险 |
| oracle 位移非零 | 类相关几何是唯一原因 | 做第 12.1 节的排查 |
| 目标 likelihood 提升 | 任务准确率提升 | 分开报告 |
| gate 检出率低 | 所有无标签信息都无用 | 限定到统计量、备择与阈值 |
| 某个确认集不符合方向 | 测试不重要或模型本来不适用 | 保留结果，按预先边界讨论 |

---

## 13. 自然迁移、决策层和统计报告

### 13.1 自然迁移不替代机制实验

跨 session/night 可能同时改变几何、比例及类条件结构。它评价的是完整迁移效果，不自动为单分布附近的局部理论提供因果验证。[REV, AI review 的 longitudinal mismatch 意见]

保留每个阶段的比例审计、伪迹剔除规则、时间边界与适应样本数。目标标签只能在预测写出后进入评估与事后审计。

### 13.2 Stage-2 必须重新定义正确的比较

每个比例条件首先重新拟合第一阶段几何，再进行决策校正。保留旧的“固定几何后改变比例”版本，但将其标为纯决策层实验，而不是完整 mixed-shift 方法。

对 density head，明确

$$
h_{BA}(x)=\arg\max_y\widehat p_y(x),
\qquad
h_{Acc}(x)=\arg\max_y\widehat\rho_y\widehat p_y(x).
$$

对于在有效源 prior `pi_src` 下的 calibrated source posterior，转换成对应规则需要除以该 source prior；不能把原始 posterior 的直接 argmax 称为 uniform class-conditional decision。[SUPP, S9；DERIVATION]

**每套实际预测都同时报告 accuracy、bAcc 和各类 recall。** 不允许拿 `h_Acc` 的 accuracy 提升，再拿另一套 `h_BA` 的不变性声称同一部署策略安全。

如果某个 bAcc 计算函数根本不使用估计的目标先验，其“先验不变性”属于构造恒等性质，不是独立的实证安全发现。

### 13.3 收缩和门控比较的最低要求

相同的校准、ensemble、输入样本与预处理必须共享。目标比例 oracle 只作诊断上限。

新的 curvature gate 暂不进入默认配方。它需要独立的构造集、校准集与评估集，明确误适应定义、效用阈值、覆盖和风险。不因测试效果不好就事后调阈值。

### 13.4 统计单位与 estimand

沿用原补充材料的原则：受试者是独立报告单位，不能把 seeds、epochs、trials 或多个夜晚当作额外独立受试者。[SUPP, H]

建议保留受试者内 seeds/相关 sessions 的先汇总，再做配对受试者 bootstrap。预先规定主 estimand 为每数据集、subject-weighted 或 dataset-macro 中哪一个；不能根据显著性切换主结果。

**Seed score 平均与 posterior ensemble 是不同算法。** 必须分开命名，不将某个 ensemble 结果当作单模型跨 seed 平均。

报告区间、效应大小、覆盖、失败数和预先定义的胜/平/负阈值。“区间包含零”不证明无害或非劣；这些结论需要预设容忍界限和相应推断。

受试者 bootstrap 若固定已训练 checkpoint，不包含完整训练流程重新抽样的全部不确定性；重叠 LOSO 源训练集也可能引入跨受试者相关。报告时说明推断所条件化的对象，不把 bootstrap 描述为万能的独立性修复。

### 13.5 确认数据必须真的未参与选择

v2 将某些 MI 数据列为新鲜确认集，但它们是否已在整个 CMI 仓库的其他探索中影响方法选择，仍需盘点。

“未参与当前 GEM 表格”不自动等于“未参与研究开发”。无法满足独立确认时，改称扩展验证；或预先冻结新受试者/新 session/新评估协议，并清楚说明可达到的独立程度。

---

## 14. 服务器交付规格与可证伪关卡

### 14.1 建议的产物目录

以下是建议新增目录结构，不表示这些文件已存在：

```text
journal_revision_v3/
  README.md
  evidence/
    manuscript_result_map.csv
    artifact_capability_matrix.csv
    claim_evidence_ledger.csv
  theory/
    derivation_registry.md
    numerical_checks/
  prereg/
    pilot_protocol.md
    intervention_manifest.json
    metrics_and_failure_rules.md
  configs/
    frozen_reference_config.json
  outputs/
    per_unit_metrics.csv
    intervention_responses.csv
    solver_trajectories/
    source_and_prediction_hashes.csv
  reports/
    pilot_results.md
    diagnostic_findings.md
    claim_updates.md
```

写入新目录，不覆盖旧结果、冻结标签或原始论文表格。任何结果重算保留原版本与新版本之间的对应关系。

### 14.2 每个实验单位必须有的元数据

```text
experiment_id / dataset / label_set / subject_id / session_id / seed
source_checkpoint_hash / density_hash / preprocessing_hash
adapt_manifest_hash / eval_manifest_hash / intervention_hash
geometry_family / geometry_strength / prevalence_condition
upstream_normalization / readout / fitting_prior_rule / decision_rule
penalty / prior_strength / optimizer / iteration_budget / stop_rule
source_data_used / target_labels_used / oracle_flag
status / fallback / gradient_residual / objective_change / boundary_hits
prediction_hash / result_hash / code_commit
```

`target_labels_used` 必须区分实验构造、oracle 拟合、事后诊断和实际 adapter 输入，不能只有一个模糊布尔值。

### 14.3 关卡按证据质量判定，不按是否出现预期正结果判定

| 关卡 | 放行条件 | 不构成放行条件 |
|---|---|---|
| G0：追溯与能力盘点 | 每个旧结果有状态；参考实现和可运行输入明确 | 找到一份看起来相近的旧表 |
| G1：数学与实现 | 公式适用条件明确；数值差分/积分通过；失败可定位 | 曲线大体符合预期 |
| G2：小规模干预 | 两种响应都可测；预测误差、置信范围、非线性范围完整 | 所有方法排序符合 N1 |
| G3：失配与范围 | 主要预测失败被定位或明确保留为未解释 | 所有反例都被 N4 吸收 |
| G4：确认与自然迁移 | 使用冻结设计；完整报告所有预设比较 | 确认集一定同方向或达到显著 |
| G5：论文可重建 | 正文主张有相应定理/数据；所有数值可追溯 | 只有最终平均表 |

G2/G3 出现不符合理论预测的结果时，不应强行放行“原主张成立”。可以完成实验并收缩结论；方法排序负面与科学执行失败不是同一件事。

### 14.4 工作顺序

**阶段 A：追溯与理论修正并行。** 完成 G0；整理 N5 反例、N6 Jacobian、双响应和三分类已知协方差模型；补数值回归缺口。

**阶段 B：一个 MI、一个 Sleep 的最小干预闭环。** 冻结方法与指标；完成 CP/CG/CPG；先解释响应和优化，再看自然迁移净收益。

**阶段 C：逐算子推广。** 根据前一阶段结果，完成 EA/SPD 或谱对象的实际实现匹配、导数验证和对应实验，不同时扩展所有方向。

**阶段 D：确认与成文。** 在方法与解释冻结后扩展数据，补决策层与完整基线，建立论文 claim–evidence 对应。

不在能力盘点之前承诺“全部 CPU 重算”或固定 14 周完成。工期依赖原始信号、checkpoints、SPD 中间状态和原表可追溯程度。

---

## 15. 论文结构、贡献边界与投稿方向

### 15.1 建议的单篇结构

**1. Introduction。** 解释类别组成与真实几何改变为何需要不同处理。明确本文研究估计量响应与恢复，不预设哪个方法获胜。

**2. Setup and scope。** 三种权重、可用信息、共同坐标与可识别条件、总体解/有限步算法的区别。

**3. Sensitivity of alignment estimators。** 一般估计方程及实际统计量的矩阵/谱导数。每个推导对应一个可执行对象。

**4. Geometry recovery and optimization。** 二分类双响应、修正后的联合 EM 慢方向；多类内容按证明进度决定正文或附录位置。

**5. Prior uncertainty and model mismatch。** 固定/收缩/联合的风险比较、端点交叉近似、oracle 诊断边界，不放未经验证的默认安全配方。

**6. Controlled and EEG experiments。** 先报告干预验证，再报告自然迁移及同头 No-GEM 净收益；负面结果保留。

**7. Discussion and limitations。** 真实 EEG 的注入恢复与天然几何区别；密度错设、有限样本、参数维数、时间漂移和信息不足边界。

这不是对期刊当前页数政策的声明。实际篇幅和投稿格式应在投稿准备阶段另行核对。

### 15.2 可用于当前工作稿的贡献表述

现阶段可以写成计划性表述：

> 本研究分析由类别混合分布驱动的 EEG 对齐估计量，区分类别比例引起的响应与真实几何恢复。我们以一般估计方程连接不同对齐统计量，并在明确模型条件下研究先验约束和有限迭代的作用。受控实验将分别检验比例响应、注入几何恢复及其任务影响；自然迁移实验评价这些分析的适用范围。

暂时不能写“真实 EEG 已复现统一排序”“one-shot 在 Sleep 最好”“弱可辨识与某类低表现人群重合”“协议感知配方已安全有效”。这些均应等待相应证据。

### 15.3 TSP 与 TPAMI 的安排

保留此前的研究策略：以 TSP 为主要组织方向，优先把估计理论、实际信号统计量与可复现实验做完整；TPAMI 作为研究范围与方法证据扩展后的条件选项。

这个选择是本项目的规划，不是期刊接收保证，也不是“增加一个非 EEG 正结果就可以升级”的规则。扩展应证明同一问题与分析在另一设置下仍有意义，而不只是增加数据集数量。

暂不将两篇拆分作为默认方案。v2 关于“不构成切片”的判断也不宜预先承诺：两篇是否具有独立问题、独立证据和足够不同的贡献，要等实际结果结构形成后再判断。

### 15.4 哪些方向暂时不纳入

CMI-TRACE、身份去除、FSR、ACAR/OACI 等不因位于同一仓库就合并成本文主体。只有与当前估计量、诊断或数据协议直接对应的资产才考虑复用，并保留来源。

不以加入 diffusion、完整 encoder TTA 或大型非线性 adapter 作为当前主修动作。它们改变拟合能力，但不自动增加区分类别比例与几何所需的信息；需要先有明确、可检验的新增问题。[MAIN, 全局歧义结果；PLAN]

---

## 16. 立即执行清单与最终边界

### 16.1 第一批任务

| 负责人/位置 | 任务 | 产出 |
|---|---|---|
| 作者/理论端 | 确认 E 主线与双响应；撤下 N5/N8 普遍命题及 N4 双向归因 | 更新后的 claim ledger |
| 理论端 | 补完整 EM Jacobian 差分；整理三类余项；完善双响应证明 | derivation registry + 测试结果 |
| 服务器 agent | 只读盘点旧产物、类别映射、source bundles 和可重跑层 | G0 两张清单 |
| 实现端 | 明确 Pure/Anchored/Fixed；加入同头 No-GEM 与轨迹日志 | frozen reference config |
| 作者与实验端 | 按能力与科学需求选定一个 MI、一个 Sleep pilot | 预注册 pilot 协议 |

第一批任务不包括全库重新训练、全方法扫描或根据新结果重写摘要结论。

### 16.2 不可越过的主张边界

- 固定 prior 不等于比例不变。
- 几何位移小不等于恢复能力强。
- 同一 likelihood 的混淆方向不等于所有算子的因果分解。
- oracle 位移不能唯一归因为类相关几何。
- 一般内部收缩不能未经证明排除。
- 已知几何的比例信息与联合问题的剖面信息不同。
- 未显著不等于无害、非劣或全域弱可辨识。
- 真实干预由标签构造，不等于 adapter 获得标签的部署方法。
- 不同 readout、不同上游归一化、不同任务类别数的表格不能拼成同一个受控比较。
- 新公式的指定模型数值核对，不等于真实 EEG 已得到验证。

**最终目标不是统一排序。** 更有价值、也更可检验的结论是：

> 类别比例如何影响无标签对齐，取决于算法使用的统计量、模型假设与优化过程；降低这种影响时，必须同时检查是否保留了对真实几何变化的恢复能力。

---

## 17. 来源与对应位置

本节供离线阅读时定位原材料。本文没有在此次写作中新增外部文献检索，也没有将未查看的外部文献作为新增事实来源。

**[V2]** `REVISION_PLAN_v2_divergent.md`，2026-09-26。重点位置：§0–§2 的主线和摘要级主张；§3.2–§3.9 的 N1–N8；§4 的算法与参考实现；§5 的 L1–L6；§7 的 G0；§9–§10 的关卡与风险解释。

**[MAIN]** `26843_When_Priors_Push_Geometr (2).pdf`，*When Priors Push Geometry: Fixed-Prior Geometry EM for EEG Test-Time Adaptation*。重点位置：§3.1 权重与坐标；§3.2 歧义；§3.3 局部响应与信息；§3.4 二分类 Gaussian；§4 更新与预测；§5.2 EEG 比较与不同 readout。

**[SUPP]** `26843_When_Priors_Push_Geometr_Technical Supplement.pdf`。重点位置：S7 多类 fitting-prior 导数；S8 inverse-Fisher 条件；S9 balanced accuracy 决策；S11 pooled 矩；S12 oracle 共同变换；S13 responsibility-error bias；S14 one-shot；F.5/Table S4 严格 EM；S15 二分类 Fisher；H 实现与配对报告。

**[REV]** `When Priors Push Geometry_ Fixed-Prior Geometry EM for EEG Test-Time Adaptation _ OpenReview.pdf`。人工评审 yczf/hTrM，及 AI review。本文把 AI review 与人工评审分开标识，不将前者表述为额外人工评审。

**[CHECK]** `fpgem_v2_math_checks.py`、`fpgem_v2_math_checks.json`。独立指定模型的计算核对，不含 EEG 结果复现。参见附录 A。

**[DERIVATION]/[PLAN]** 本轮评议新增内容。前者的模型条件和推导在相应章节给出；后者均为建议实施的工作，不属于已经完成的实验。

---

## 附录 A. 数学核对的复现与覆盖

### A.1 运行方法

将已有脚本与本文件放在同一目录，使用具备 NumPy/SciPy 的 Python 环境：

```bash
python fpgem_v2_math_checks.py --output fpgem_v2_math_checks_replay.json
```

脚本头部声明 Python 3.10 及以上。以上命令生成新的回放 JSON，不覆盖原始核对文件。

### A.2 本次回放记录

本次生成的 JSON 与原 `fpgem_v2_math_checks.json` 在解析后的内容上完全一致。

```text
REVISION_PLAN_v2_divergent.md
SHA-256: 3baeb0af4bf418dfaf56a01db2697a00809266a410013723290c846c87c4486b

fpgem_v2_math_checks.py
SHA-256: 14730a4411201ae6f790964d98b7e2dce3713eb2ca5a16fd123862f191da4a94

fpgem_v2_math_checks.json
SHA-256: d1892d1e08404f752df415ac945eabc953d644cf7b251c680bf6677c64e62db8
```

### A.3 不能夸大的核对范围

| 项目 | 脚本真正做了什么 | 没有做什么 |
|---|---|---|
| 二分类 EM | 积分计算 `S(t)`；代入给定 Jacobian 并计算谱半径和局部轮数 | 没有独立差分整个联合 EM 映射来验证 Jacobian 的全部元素 |
| 三分类信息 | 从指定模型的完整 score 积分 Fisher，再做 Schur complement | 没有证明所有 `K` 的阶数；没有引入未知协方差 nuisance |
| 双响应 | 对精确总体固定-prior 更新，用中心有限差分比较两类导数 | 没有 EEG 实验；没有一般 affine/Adam 的同等结论 |
| 收缩反例 | 比较指定高斯风险族的两个端点与内部最优点 | 没有证明具体 constrained GEM 的最优路径 |

这也是为什么正文把相关结果标为“限定模型推导/核对”，而不称为期刊版理论已全部完成。

---

## 附录 B. 建议的 claim–evidence 账本

```text
claim_id
claim_text
scope_and_assumptions
origin: manuscript / v2 / derivation / numerical_check / experiment
status: supported_in_source / derived_scoped / numerically_checked /
        hypothesis / unresolved / withdrawn_as_stated
proof_or_artifact
implementation_and_commit
independent_check
known_counterexample_or_failure
allowed_manuscript_wording
next_required_action
```

建议首先登记：

| Claim ID | 主张 | 当前状态 |
|---|---|---|
| C01 | 一般估计方程的局部比例响应 | 限定条件下推导；待逐算子实现匹配 |
| C02 | 指定二分类精确联合 EM 的慢速率为 `(1+t^2)S(t)` | 限定模型推导与数值评估；完整映射差分待补 |
| C03 | 指定二分类固定-prior 有限迭代的 `B_k/G_k` 不随 `k` 变化 | 限定模型推导与指定网格差分核对 |
| C04 | 内部收缩一般无收益、端点二值最优 | 原表述撤回；存在明确反例 |
| C05 | 三类已知协方差平移模型的剖面信息主项为 `t^2 I/4` | 局部展开与积分支持；严格余项待整理 |
| C06 | 所有正单纯形多类模型均为 `t^4` | 原普遍表述撤回；待指定模型重推 |
| C07 | oracle 位移当且仅当类相关几何 | 撤回；固定惩罚提供反例 |
| C08 | 真实 EEG 中某个统一排序成立 | 待实验；不得写成摘要结果 |
| C09 | 可辨识度门控带来安全的准确率校正 | 未建立；探索诊断 |
| C10 | 控制比例响应时仍保留几何恢复能力 | 研究问题；通过双干预与同头任务指标检验 |

---

**文档结束。本文可作为理论复核与 pilot 设计的依据；大规模实验应在 G0 与 pilot 协议冻结后执行。**
