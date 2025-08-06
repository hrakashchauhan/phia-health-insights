"""Core ReACT Agent Logic.
"""

from typing import Sequence
import pandas as pd
import numpy as np
from onetwo.agents import react
from onetwo.stdlib.tool_use import llm_tool_use
from onetwo.stdlib.tool_use import python_tool_use

from prompt_templates import build_exemplars, AGENT_PREAMBLE, PHIA_REACT_PROMPT_TEXT

# Mock Search Tool for open source version
def mock_search_func(query: str) -> str:
    print(f"Mock Search Called: {query}")
    return "Web search is not available in this demo environment. Sorry!"

def get_react_agent(
    summary_df: pd.DataFrame,
    activities_df: pd.DataFrame,
    profile_df: pd.DataFrame,
    example_files: Sequence[str],
):
    """Initializes and returns an open-source compatible ReAct agent."""

    # Sandbox for python tool - uses standard exec, be mindful of security.
    sandbox = python_tool_use.PythonToolUseEnvironment(
        extra_locals={
            "pd": pd,
            "np": np,
            "summary_df": summary_df,
            "activities_df": activities_df,
            "profile": profile_df,
        },
        sandbox_type="exec"
    )
    python_tool = llm_tool_use.Tool(
        name="tool_code",
        function=sandbox.execute,
        description="Python interpreter. Executes code on pandas DataFrames (summary_df, activities_df, profile).",
    )

    search_tool = llm_tool_use.Tool(
        name="search",
        function=mock_search_func,
        description="Mock search engine. Returns a placeholder message.",
    )

    finish_tool = llm_tool_use.Tool(
        name="finish",
        function=lambda x: x,
        description="Returns the final answer to the user.",
    )

    agent_tools = [python_tool, search_tool, finish_tool]

    print(f"Loading exemplars from: {example_files}")
    examples = build_exemplars(example_files)
    print(f"Loaded {len(examples)} exemplars.")

    agent = react.ReActAgent(
        exemplars=examples,
        environment_config=python_tool_use.PythonToolUseEnvironmentConfig(
            tools=agent_tools,
        ),
        max_steps=10,
        stop_prefix="",
    )

    agent.prompt = react.ReActPromptJ2(
        text=AGENT_PREAMBLE + PHIA_REACT_PROMPT_TEXT
    )
    return agent

QUESTION_PREFIX = (
    "Use tools such as tool_code to execute Python code and search to find "
    "external relevant information as needed. Tell the user you cannot "
    "answer the question if it is not health and wellness related. "
    "Take into account that questions may have typos or grammatical "
    "mistakes and try to reinterpret them before answering. Follow all "
    "instructions and the ReAct template carefully. Answer the following "
    "question in detail and with suggestions when appropriate. Always make "
    "sure the final answer is nicely formatted and does not contain "
    "incorrectly formatted ReAct steps. Remember to use user data whenever "
    "relevant to enhance your answers! Question: "
)
