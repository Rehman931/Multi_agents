from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()


class PipelineState(TypedDict):
    input_text: str
    edited_text: str
    script_text: str
    final_output: str


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)


def editor_tool(state: PipelineState) -> dict:
    """Stage 1: Cleans up grammar, removes typos and refines the tone."""
    print("--- Executing Editor Tool ---\n")

    prompt = f"""
You are an expert copy editor.

Correct grammar mistakes, fix typos, improve sentence structure,
and make the text sound natural while preserving its meaning.

Text:
{state["input_text"]}
"""

    response = llm.invoke(prompt)

    return {
        "edited_text": response.content.strip()
    }


def script_tool(state: PipelineState) -> dict:
    """Stage 2: Formats the clean text into an engaging video script."""
    print("--- Executing Script Tool ---\n")

    prompt = f"""
You are an expert YouTube content creator.

Convert the following text into an engaging video script.

Text:
{state["edited_text"]}
"""

    response = llm.invoke(prompt)

    return {
        "script_text": response.content.strip()
    }


def final_tool(state: PipelineState) -> dict:
    """Stage 3: Produces the final polished output."""
    print("--- Executing Final Tool ---\n")

    prompt = f"""
You are a professional editor.

Review and polish the following video script while preserving
its meaning and style.

Script:
{state["script_text"]}
"""

    response = llm.invoke(prompt)

    return {
        "final_output": response.content.strip()
    }

graph = StateGraph(PipelineState)

graph.add_node('editor_tool', editor_tool)
graph.add_node('script_tool', script_tool)
graph.add_node('final_tool', final_tool)

graph.add_edge(START, 'editor_tool')
graph.add_edge('editor_tool', 'script_tool')
graph.add_edge('script_tool', 'final_tool')
graph.add_edge('final_tool', END)

app = graph.compile()

results = app.invoke({
    "input_text":"hello everyone welcome back to my channel.Today we are going to learn langgraph."
})

print(results['final_output'])