"""Core ReACT Agent Logic.
"""

from typing import Sequence
import pandas as pd
import numpy as np
import io
import contextlib

from onetwo import ot
from onetwo.agents import react
from onetwo.stdlib.tool_use import llm_tool_use
from onetwo.stdlib.tool_use import python_tool_use

from prompt_templates import build_exemplars, AGENT_PREAMBLE, PHIA_REACT_PROMPT_TEXT

# Mock Search Tool, TODO: Try to use tavily instead
def mock_search_func(query: str) -> str:
    print(f"Mock Search Called: {query}")
    return "Web search is not available in this demo environment."

# For code generation, create a simple python executor using exec()
def simple_python_executor(code: str, globals: dict) -> str:
    """Executes python code and captures the output."""
    local_scope = {}
    # Use a string buffer to capture any `print()` statements
    string_buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(string_buffer):
            # Execute the code with the provided globals (your dataframes)
            exec(code, globals, local_scope)
        output = string_buffer.getvalue()
        # If the last line of code was an expression, its value is in the buffer
        # This is a simple way to get the return value
        if not output and local_scope:
             # Get the last computed value if nothing was printed
             output = str(list(local_scope.values())[-1])
        return output or "Code executed successfully."
    except Exception as e:
        return f"Error executing code: {e}"

def get_react_agent(
    summary_df: pd.DataFrame,
    activities_df: pd.DataFrame,
    profile_df: pd.DataFrame,
    example_files: Sequence[str],
):
    """Initializes and returns an open-source compatible ReAct agent."""

    # Define the globals dictionary for our code executor
    sandbox_globals = {
        "pd": pd,
        "np": np,
        "summary_df": summary_df,
        "activities_df": activities_df,
        "profile": profile_df,
    }

    # Python tool uses our custom simple_python_executor
    python_tool = llm_tool_use.Tool(
        name='tool_code',
        function=lambda code: simple_python_executor(code, globals=sandbox_globals),
        description='Python interpreter. Executes code on pandas DataFrames (summary_df, activities_df, profile).',
    )

    # Define other tools
    search_tool = llm_tool_use.Tool(
        name="search", function=mock_search_func, description="Mock search engine."
    )
    finish_tool = llm_tool_use.Tool(
        name="finish", function=lambda x: x, description="Returns the final answer."
    )
    agent_tools = [python_tool, search_tool, finish_tool]

    # Load exemplars
    examples = build_exemplars(example_files)

    # Create the agent specfiically with PythonToolUseEnvironmentConfig
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
