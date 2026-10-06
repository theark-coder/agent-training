import os
import json

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


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


def calculate(expression: str):
    return f"计算结果：{eval(expression)}"


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



def test_native_tool_calling():
    chat = ChatSession()

    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "进行数学计算",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "要计算的数学表达式",
                        }
                    },
                    "required": ["expression"],
                },
            },
        }
    ]

    messages = [
        {
            "role": "user",
            "content": "请计算 123 * 456，并告诉我最终结果。",
        }
    ]

    completion = chat.client.chat.completions.create(
        model="qwen-plus",
        messages=messages,
        tools=tools,
    )

    message = completion.choices[0].message

    print("第一次模型输出：")
    print(message)

    if message.tool_calls:
        tool_call = message.tool_calls[0]

        tool_name = tool_call.function.name

        arguments = json.loads(
            tool_call.function.arguments
        )

        print("\n工具名称：")
        print(tool_name)

        print("\n工具参数：")
        print(arguments)

        if tool_name == "calculate":
            result = calculate(**arguments)

            print("\n工具执行结果：")
            print(result)

            # 把模型第一次的 tool call 加入消息历史
            messages.append(message)

            # 把工具执行结果告诉模型
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )

            # 再次调用 LLM
            final_completion = chat.client.chat.completions.create(
                model="qwen-plus",
                messages=messages,
                tools=tools,
            )

            final_message = final_completion.choices[0].message

            print("\n最终模型回答：")
            print(final_message.content)
if __name__ == "__main__":
    test_native_tool_calling()