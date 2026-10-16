# Quant-Arena manuscript

当前稿以真实历史市场数据上的智能体量化研究 benchmark 为主线，延续原稿的英文论文文体。主文档为 [main.tex](main.tex)，编译后生成 `main.pdf`。

## 正文结构

| 文件 | 内容 |
| --- | --- |
| `Sections/0_abstract.tex`、`Sections/1_introduction.tex` | 研究问题与 benchmark、金融评测、Arena 三项贡献 |
| `Sections/2_method.tex` | 任务合同、研究交互、资源约束、时间边界、收益与评分公式 |
| `Sections/2_arena.tex` | 平台职责、数据授权、隔离执行、共享评测、恢复与实验记录 |
| `Sections/2_rsi_harness.tex` | RSI Harness 的独立章节和实现说明占位 |
| `Sections/3_experiments.tex` | 实验设计、leaderboard、对照与验证安排 |
| `Sections/4_relatedworks.tex`、`Sections/5_conclusion.tex` | 相关工作、贡献总结与后续工作 |
| `Tables/TabDailyProtocol.tex` | 当前日频协议的固定约定 |
| `Tables/TabLeaderboard.tex` | 待填 leaderboard，所有单元格均为占位 |
| `Sections/6_appendix_registry.tex` | 待补的真实数据、场次与运行登记 |
| `Sections/7_appendix_boundary.tex` | 信息边界、多样性公式和指标资格 |

leaderboard 与 RSI Harness 的实现和结果后续补充。正文没有沿用原稿的模型排名、方法增益或跨市场结果。原有表格与汇总图文件保留，当前 `main.tex` 不引用它们。

本仓库包含英文论文的 LaTeX 源码、参考文献、模板和图表资源。中文译文与论文理解文档在研究工作区单独维护。

## 后续填写

先完成附录中的场次登记，再将正式终测 scorecard 填入 leaderboard，并据此撰写结果分析。RSI Harness 章节预留了研究状态、工具与先验、候选生成、修复、预算分配、最终选择及方法冻结条件。原有文献引用继续保留，本轮未重新核验其外部来源。

## 编译

在 Overleaf 中将 `main.tex` 设为主文档，使用 pdfLaTeX 编译。具备完整 TeX Live 环境时，也可运行 `bash build.sh`。构建依次执行 pdfLaTeX、BibTeX 和三轮 pdfLaTeX，使交叉引用稳定；发生编译错误时停止。

模板使用 LaTeX extra、pictures 及 Latin babel 等组件。缺少依赖的精简 TeX 环境需要先补齐对应包。占位内容会在 PDF 中明确显示，投稿前应完成或移除。

## 上传到 Overleaf

首次导入可下载 GitHub 的源码 ZIP，在 Overleaf 首页选择 **New Project → Upload Project**。导入后确认 `main.tex` 位于项目根目录，主文档设为 `main.tex`，编译器设为 **pdfLaTeX**。

更新已有项目时，在对应目录上传修改过的同名文件并覆盖，保持 `Sections/`、`Tables/` 等目录结构，再点击 **Recompile**。若有人在 Overleaf 上修改过，先下载并合并这些修改。编译生成的 `main.pdf` 和辅助文件由 `.gitignore` 排除；图表与模板使用的 PDF 资源仍保留。

## 更新 GitHub

在本仓库目录中运行：

```sh
git status
git add main.tex ref.bib Sections Tables Figures assets style README.md build.sh .gitattributes .gitignore
git commit -m "Update manuscript"
git push origin main
```

GitHub 上传与 Overleaf 文件更新需要分别执行。
