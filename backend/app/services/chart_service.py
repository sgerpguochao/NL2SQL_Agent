"""
图表服务层 - AI 图表类型决策 + ECharts option JSON 生成
通过 Qwen3-max 分析查询结果，自动选择最合适的图表类型并生成配置
"""

import json
import re
from typing import Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from app.services.llm_service import get_llm

CHART_SYSTEM_PROMPT = """你是一个数据可视化专家。根据用户的查询问题和 SQL 查询结果，你需要：

1. 判断最合适的图表类型（bar/line/pie/table）
2. 生成完整的 ECharts option 配置 JSON
3. 同时生成表格数据

返回严格的 JSON 格式（不要包含任何其他文字或 markdown 标记），结构如下：
{
  "chartType": "bar|line|pie|table",
  "echartsOption": { ... 完整的 ECharts option 配置 ... },
  "tableData": {
    "columns": ["列名1", "列名2"],
    "rows": [["值1", "值2"], ...]
  }
}

图表选择规则：
- 比较不同类别的数值（如各部门销售额）-> bar（柱状图）
- 展示时间趋势变化（如月度销售额）-> line（折线图）
- 展示占比分布（如产品销售占比）-> pie（饼图）
- 数据行列较多或无明显可视化需求 -> table（纯表格）

ECharts 配置要求：
- 使用深色主题配色：背景透明，文字颜色 #c0c0c0
- 柱状图/折线图必须包含 xAxis, yAxis, series, tooltip
- 饼图必须包含 series[0].type='pie', series[0].data, tooltip, legend
- 数值使用千分位格式化
- 图表标题不需要（前端会显示）"""


def generate_chart(
    question: str,
    sql: str,
    query_result: str,
) -> Optional[dict[str, Any]]:
    """
    根据查询结果生成图表配置

    Args:
        question: 用户的原始问题
        sql: 执行的 SQL 语句
        query_result: SQL 查询结果字符串

    Returns:
        包含 chartType, echartsOption, tableData 的字典，失败时返回降级的 table 类型
    """
    llm = get_llm()

    user_prompt = f"""用户问题: {question}

执行的 SQL:
{sql}

查询结果:
{query_result}

请分析以上数据，选择最合适的图表类型，并生成完整的 ECharts 配置和表格数据。
只返回 JSON，不要任何其他文字。"""

    try:
        response = llm.invoke([
            SystemMessage(content=CHART_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])

        # 从回复中提取 JSON
        content = response.content.strip()

        # ① 去除 Qwen3 <think>...</think> 思考标签
        content = re.sub(r"<think>[\s\S]*?</think>", "", content).strip()

        # ② 去除 markdown 代码块标记
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\s*\n?", "", content)
            content = re.sub(r"\n?```\s*$", "", content)

        # ③ 兜底提取：从第一个 { 到最后一个 } 之间的内容
        if not content.startswith("{"):
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                content = content[start:end + 1]

        chart_data = json.loads(content)

        # 校验必要字段
        if "chartType" not in chart_data:
            chart_data["chartType"] = "table"

        print(f"[ChartService] 成功生成图表: type={chart_data.get('chartType')}, "
              f"hasEchartsOption={'echartsOption' in chart_data and chart_data['echartsOption'] is not None}")

        return {
            "chart_type": chart_data.get("chartType", "table"),
            "echarts_option": chart_data.get("echartsOption"),
            "table_data": chart_data.get("tableData"),
        }

    except (json.JSONDecodeError, Exception) as e:
        print(f"[ChartService] 解析失败，降级为表格: {e}")
        # 降级：解析失败返回纯表格
        return _fallback_table(query_result, str(e))


def _fallback_table(query_result: str, error: str = "") -> dict[str, Any]:
    """
    降级方案：将查询结果转为简单表格

    Args:
        query_result: SQL 查询结果字符串
        error: 错误信息

    Returns:
        table 类型的图表数据
    """
    try:
        # 尝试解析查询结果
        data = eval(query_result) if query_result else []

        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], dict):
                columns = list(data[0].keys())
                rows = [[str(row.get(c, "")) for c in columns] for row in data]
            elif isinstance(data[0], (tuple, list)):
                columns = [f"列{i+1}" for i in range(len(data[0]))]
                rows = [[str(v) for v in row] for row in data]
            else:
                columns = ["结果"]
                rows = [[str(v)] for v in data]
        else:
            columns = ["结果"]
            rows = [[str(query_result)]]

    except Exception:
        columns = ["结果"]
        rows = [[str(query_result)]]

    return {
        "chart_type": "table",
        "echarts_option": None,
        "table_data": {
            "columns": columns,
            "rows": rows,
        },
    }
