import os
import json
from dataclasses import dataclass
from typing import Callable
from dotenv import load_dotenv
from openai import OpenAI



import inspect
from dataclasses import dataclass
from typing import Callable, Literal, get_args, get_origin, get_type_hints

load_dotenv()
@dataclass
class Tool:
    function: Callable
    description: str
    parameter_descriptions: dict[str, str]

    @property
    def name(self) -> str:
        return self.function.__name__

    def execute(self, arguments: dict):
        return self.function(**arguments)

    def get_schema(self) -> dict:
        signature = inspect.signature(self.function)
        type_hints = get_type_hints(self.function)

        properties = {}
        required = []

        for param_name, param in signature.parameters.items():
            annotation = type_hints.get(param_name, str)

            param_schema = python_type_to_json_schema(annotation)

            description = self.parameter_descriptions.get(param_name)

            if description:
                param_schema["description"] = description

            properties[param_name] = param_schema

            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }


def python_type_to_json_schema(annotation) -> dict:
    origin = get_origin(annotation)

    # Literal["add", "subtract", ...]
    if origin is Literal:
        values = list(get_args(annotation))

        if values and all(isinstance(value, str) for value in values):
            json_type = "string"
        elif values and all(isinstance(value, int) for value in values):
            json_type = "integer"
        else:
            json_type = "string"

        return {
            "type": json_type,
            "enum": values,
        }

    type_mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
    }

    return {
        "type": type_mapping.get(annotation, "string")
    }


TOOL_REGISTRY: dict[str, Tool] = {}


def tool(
    description: str,
    parameter_descriptions: dict[str, str] | None = None,
):
    def decorator(function: Callable):
        tool_object = Tool(
            function=function,
            description=description,
            parameter_descriptions=parameter_descriptions or {},
        )

        TOOL_REGISTRY[tool_object.name] = tool_object

        return function

    return decorator


@tool(
    description="搜索互联网信息",
    parameter_descriptions={
        "query": "要搜索的关键词或问题",
    },
)
def search_web(query: str):
    return f"""
搜索工具已经完成搜索。

搜索关键词：
{query}

搜索结果：
这是一个模拟搜索结果。
目前这个 Tool 还没有连接真实互联网，因此没有返回真实论文内容。

请不要再次调用搜索工具。
请直接根据这个结果回答用户。
"""


@tool(
    description="进行两个数字之间的基础数学运算",
    parameter_descriptions={
        "a": "第一个数字",
        "b": "第二个数字",
        "operation": "要执行的运算类型",
    },
)
def calculate(
    a: float,
    b: float,
    operation: Literal[
        "add",
        "subtract",
        "multiply",
        "divide",
    ],
):
    if operation == "add":
        result = a + b

    elif operation == "subtract":
        result = a - b

    elif operation == "multiply":
        result = a * b

    elif operation == "divide":
        if b == 0:
            raise ValueError("不能除以零")

        result = a / b

    else:
        raise ValueError(
            f"不支持的运算：{operation}"
        )

    return f"计算结果：{result}"


TOOL_SCHEMAS = [
    tool_object.get_schema()
    for tool_object in TOOL_REGISTRY.values()
]


def execute_tool(
    tool_name: str,
    arguments: dict,
):
    tool_object = TOOL_REGISTRY.get(tool_name)

    if tool_object is None:
        raise ValueError(
            f"Unknown tool: {tool_name}"
        )

    try:
        return tool_object.execute(arguments)

    except TypeError as exc:
        raise ValueError(
            f"Invalid arguments for tool "
            f"'{tool_name}': {exc}"
        ) from exc

    except Exception as exc:
        raise RuntimeError(
            f"Tool '{tool_name}' execution failed: {exc}"
        ) from exc

class ChatSession:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        self.messages = [
            {
                "role": "system",
                "content": "你是一名可靠的 AI Agent，请严格按照用户要求执行任务。",
            }
        ]

    def chat(self, user_message: str) -> str:
        self.messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        completion = self.client.chat.completions.create(
            model="qwen-plus",
            messages=self.messages,
        )

        assistant_message = completion.choices[0].message.content

        self.messages.append(
            {
                "role": "assistant",
                "content": assistant_message,
            }
        )

        return assistant_message



def build_tool_prompt(question: str) -> str:
    return f"""
你是一个 Agent。

你可以使用以下两个工具：

1. search_web
用途：搜索互联网
参数：
- query：搜索关键词

2. calculate
用途：进行数学计算
参数：
- expression：数学表达式

请根据用户的问题决定下一步应该做什么。

如果需要调用工具，请严格按照下面的 JSON 格式回答：

{{
    "action": "tool",
    "tool": "工具名称",
    "arguments": {{
        "参数名": "参数值"
    }}
}}

如果已经有足够的信息，可以直接回答，请严格按照下面的 JSON 格式回答：

{{
    "action": "final",
    "answer": "最终答案"
}}

用户问题：
{question}
"""


class Agent:
    def __init__(self, chat_session: ChatSession):
        self.chat = chat_session

        self.tools = {
            "search_web": search_web,
            "calculate": calculate,
        }

    def run(self, question: str, max_steps: int = 5):
        current_prompt = build_tool_prompt(question)

        last_tool = None
        last_tool_result = None

        for step in range(max_steps):
            print(f"\n===== Agent Step {step + 1} =====")

            answer = self.chat.chat(current_prompt)

            print("LLM 输出：")
            print(answer)

            result = json.loads(answer)

            action = result["action"]

            # LLM 决定结束
            if action == "final":
                return result["answer"]

            # LLM 决定调用 Tool
            if action == "tool":
                tool_name = result["tool"]
                arguments = result["arguments"]

                # 防止同一个 Tool 连续无限调用
                if tool_name == last_tool:
                    print("\n检测到同一个 Tool 被连续调用。")
                    print("停止 Tool 调用，直接生成最终答案。")

                    final_prompt = f"""
用户的问题：
{question}

我们已经调用过工具：
{tool_name}

工具返回结果：
{last_tool_result}

请不要再调用工具。
请直接根据已有信息回答用户。
"""

                    final_answer = self.chat.chat(final_prompt)

                    return final_answer

                last_tool = tool_name

                tool = self.tools.get(tool_name)

                if tool is None:
                    raise ValueError(f"未知工具：{tool_name}")

                tool_result = tool(**arguments)

                last_tool_result = tool_result

                print("Tool 结果：")
                print(tool_result)

                current_prompt = f"""
用户的问题：
{question}

你刚才调用了工具：
{tool_name}

工具参数：
{arguments}

工具返回结果：
{tool_result}

请根据工具结果决定下一步。

如果已经可以回答，请返回：

{{
    "action": "final",
    "answer": "最终答案"
}}

如果确实需要其他工具，请返回：

{{
    "action": "tool",
    "tool": "工具名称",
    "arguments": {{
        "参数名": "参数值"
    }}
}}
"""

            else:
                raise ValueError(f"未知 action：{action}")

        raise RuntimeError(
            f"Agent 超过最大执行次数 {max_steps}"
        )


def build_prompt(concept: str) -> str:
    return f"""
你是一名专业的 Python 教师。

请解释下面这个概念：

{concept}

要求：
1. 用初学者能够理解的语言。
2. 给出一个简单例子。
3. 指出一个常见错误。
"""


def build_intent_prompt(question: str) -> str:
    return f"""
你是一个任务分类器。

请判断用户的问题是否需要搜索互联网。

用户问题：
{question}

请严格按照下面的 JSON 格式回答，不要添加其他内容：

{{
    "need_search": true,
    "reason": "判断原因"
}}
"""
def run_agent(messages, tools, client, max_steps=5):
    step = 0

    while True:
        step += 1

        if step > max_steps:
            return "Agent 达到最大执行步数，停止运行。"

        print(f"\n=== Step {step} ===")

        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=messages,
            tools=tools,
        )

        message = completion.choices[0].message

        if not message.tool_calls:
            return message.content

        messages.append(message)

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            print("\n模型原始参数：")
            print(tool_call.function.arguments)
           
            try:
               arguments = json.loads(tool_call.function.arguments)

            except json.JSONDecodeError as exc:
                result = f"工具参数解析失败：{exc}"

                print("\n工具参数解析结果：")
                print(result)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )

                continue
            print("\n工具名称：")
            print(tool_name)

            print("\n工具参数：")
            print(arguments)
            if not isinstance(arguments, dict):
                result = "工具参数格式错误：arguments 必须是 JSON object"

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )

                continue
            try:
                result = execute_tool(tool_name, arguments)
            except Exception as exc:
                result = f"工具执行失败：{exc}"

            print("\n工具执行结果：")
            print(result)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )


def test_native_tool_calling():
    chat = ChatSession()
   
   

    messages = [
        {
            "role": "user",
            "content": "请计算 123 * 456",
        }
    ]

   
                    # 再次调用 LLM
    result = run_agent(
        messages=messages,
        tools=TOOL_SCHEMAS,
        client=chat.client,
    )

    print("\n最终模型回答：")
    print(result)
if __name__ == "__main__":
    print(TOOL_REGISTRY.keys())
    test_native_tool_calling()