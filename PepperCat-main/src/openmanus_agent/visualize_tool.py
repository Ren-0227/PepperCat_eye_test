import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
from src.openmanus_agent.tool_base import BaseTool
from typing import ClassVar, Dict, Any

class VisualizeTool(BaseTool):
    name: str = "visualize"
    description: str = "对数据进行可视化，支持折线图、柱状图、散点图"
    parameters: ClassVar[Dict[str, Any]] = {
        "type": "object",
        "properties": {
            "data": {"type": "string", "description": "CSV格式的数据"},
            "chart_type": {"type": "string", "description": "图表类型(line/bar/scatter)"}
        },
        "required": ["data", "chart_type"]
    }
    async def execute(self, data: str, chart_type: str) -> str:
        try:
            df = pd.read_csv(io.StringIO(data))
            plt.figure()
            if chart_type == "line":
                df.plot()
            elif chart_type == "bar":
                df.plot.bar()
            elif chart_type == "scatter":
                df.plot.scatter(x=df.columns[0], y=df.columns[1])
            else:
                return f"不支持的图表类型: {chart_type}"
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            plt.close()
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode("utf-8")
            return f"data:image/png;base64,{img_base64}"
        except Exception as e:
            return f"可视化失败: {e}" 