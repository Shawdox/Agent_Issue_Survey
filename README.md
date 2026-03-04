# Codex Issue Survey

OpenAI Codex 仓库 Bug Issues 完整分析报告。

**分析范围**: `openai/codex` 仓库所有 bug-labeled issues（共 **3,938** 条）

**仓库地址**: https://github.com/Shawdox/Agent_Issue_Survey

---

## 📊 核心发现

| 指标 | 数值 |
|------|------|
| 总 Issue 数 | 3,938 |
| 主要 Bug 类型 | tui/rendering (29.5%) |
| 次要 Bug 类型 | other (25.9%) |
| 分析时间 | 2026-03-04 |

---

## 📁 文件结构

```
codex_survey/
├── README.md                     # 本文件
├── analysis_summary_report.md    # 执行摘要 + 分类统计
├── final_bug_report.md           # 完整分析表格（3,938 行）
├── batch_fetch.py                # 批量抓取脚本
├── checkpoint_base.json          # 基础列表（issue 元数据）
└── checkpoint_detail.json        # 完整分析数据
```

---

## 📊 Bug 分类分布

| Bug 类型 | 数量 | 占比 |
|----------|------|------|
| `tui/rendering` | 1,161 | 29.5% |
| `other` | 1,019 | 25.9% |
| `platform/windows` | 526 | 13.4% |
| `performance/resource` | 406 | 10.3% |
| `docs/site` | 344 | 8.7% |
| `integration/auth/billing` | 337 | 8.6% |
| `web/desktop-ui` | 145 | 3.7% |

---

## 📄 核心文件说明

| 文件 | 大小 | 用途 |
|------|------|------|
| `final_bug_report.md` | ~1 MB | 主报告 - 3,938 个 issue 的完整分析表格 |
| `analysis_summary_report.md` | ~5 KB | 摘要报告 - 执行摘要 + 分类统计 |
| `checkpoint_detail.json` | ~8 MB | 完整分析数据（JSON 格式） |
| `checkpoint_base.json` | ~1 MB | 基础元数据 |

---

## 🛠️ 使用方法

```bash
# 查看完整报告
cat final_bug_report.md

# 查看摘要报告
cat analysis_summary_report.md

# 使用分析数据
python3 -c "
import json
data = json.load(open('checkpoint_detail.json'))
from collections import Counter
counts = Counter(d['bug_type'] for d in data)
print(counts)
"
```

---

## 📋 技术架构

与 `anomalyco/opencode` 分析相同的三阶段流水线：

1. **Stage 1 - Downloader**: 分页抓取基础列表（40 页 × 100 条）
2. **Stage 2 - Analyzer**: 批量获取详情 + 实时分类
3. **Stage 3 - Report Generator**: 生成 Markdown 表格 + 统计

**关键技术**：
- Token 轮询（16+ GitHub PATs）
- Batch 处理（1000 条/批）
- Checkpoint 机制（每 100 条保存）
- 启发式分类（基于 labels + 关键词）

---

**生成时间**: 2026-03-04
**分析工具**: Python + token_pool.py (GitHub API 轮询)
