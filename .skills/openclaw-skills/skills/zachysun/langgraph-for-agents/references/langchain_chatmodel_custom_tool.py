import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from langchain.tools import tool

load_dotenv()

# =========================
# Create LLM Interfaces
# =========================
llm = ChatOpenAI(
    api_key=os.getenv("your-api-key"),
    base_url="...",
    model="...",
)


# =========================
# Create Custom Tool
# =========================
@tool("calculator", description="Performs arithmetic calculations. Use this for any math problems.")
def calc(expression: str) -> str:
    return str(eval(expression))


if __name__ == "__main__":
    llm_with_tools = llm.bind_tools([calc])
    prompt = "Please calculate 123 * 9873."
    
    messages = [HumanMessage(content=prompt)]
    response = llm_with_tools.invoke(prompt)
    
    while response.tool_calls:
        messages.append(response)
        for tool_call in response.tool_calls:
            tool_result = calc.invoke(tool_call["args"])
            print(
                f"====Calculator result:====\n {tool_result}"
            )

            tool_message = ToolMessage(
                content=str(tool_result), tool_call_id=tool_call["id"]
            )
            messages.append(tool_message)
        response = llm_with_tools.invoke(messages)

    print("======Answer:======\n", response.content)
    