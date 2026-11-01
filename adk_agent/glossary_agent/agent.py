"""Google ADK 版の用語集エージェント。"""

from google.adk.agents import Agent

from app import tools
from app.agent import INSTRUCTIONS

# app.agent の指示を再利用する。ただし今回は承認付き保存ツールを登録しないため、
# そのツールを使う指示だけADK版から除外する（app/ 側のファイルは変更しない）。
adk_instructions = "\n".join(
    line for line in INSTRUCTIONS.splitlines() if "save_learning_log" not in line
)

# ADKでは、既存のPython関数を tools に渡すとツールとして利用できる。
# 課題の比較対象にする用語検索・講義要約・確認問題作成だけを登録する。
# Pydantic AI版（app/agent.py）では、同じ設定を作成とツール登録に分けて書く:
# agent = Agent(instructions=INSTRUCTIONS, output_type=[str, DeferredToolRequests])
# agent.tool_plain(tools.search_glossary)
# agent.tool_plain(tools.get_lecture_summary)
# agent.tool_plain(tools.make_quiz)
# 承認付きの保存ツールは、今回のADK課題では登録対象外。
root_agent = Agent(
    model="gemini-3.5-flash-lite",
    name="glossary_agent",
    instruction=adk_instructions,
    tools=[
        tools.search_glossary,
        tools.get_lecture_summary,
        tools.make_quiz,
    ],
)
