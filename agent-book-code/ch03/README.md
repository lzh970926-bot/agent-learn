# Ch3｜Prompt Engineering 进阶

> 本章目标：从"会写 Prompt"到"工程化管理 Prompt"。

## 章节结构

| 节 | 内容 | 字数目标 |
|---|---|---|
| 3.1 | Prompt 工程化：5 要素模板 | 2000 |
| 3.2 | 推理增强：CoT、ToT、Self-Consistency | 2500 |
| 3.3 | 防御性 Prompt：Delimiter、Schema | 1500 |
| 3.4 | 结构化输出：JSON Mode + Pydantic | 2000 |
| 3.5 | Prompt 版本管理与 A/B | 1500 |
| 3.6 | 小结与思考 | 500 |

## 文件说明

- `01_structured.py`：5 要素模板演示
- `02_cot.py`：CoT/ToT/Self-Consistency 对比
- `03_json_output.py`：Pydantic + JSON Mode
- `04_capstone.py`：金融分析助手（综合项目前奏）

## 运行

```bash
uv run python ch03/01_structured.py
uv run python ch03/03_json_output.py
```

## 关键 takeaway

1. **结构 > 文字**：Role/Task/Context/Format/Constraint 五要素缺一不可
2. **推理能力可激发**：CoT 让小模型也能做复杂任务
3. **结构化输出是 Agent 的基石**：Pydantic 校验比"祈祷 JSON 合法"靠谱
