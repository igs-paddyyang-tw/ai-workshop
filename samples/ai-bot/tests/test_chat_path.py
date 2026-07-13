"""測試完整對話路徑：L4 agent_loop。"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


async def test():
    print("=== 測試完整對話路徑 ===\n")

    # 1. Provider 初始化
    from src.llm.provider import get_default_provider
    p = get_default_provider()
    print(f"1. Provider: {p.name} model={p.model} OK")

    # 2. Tools 註冊
    import src.llm.tools
    from src.llm.tool_registry import registry
    names = registry.all_names()
    print(f"2. Tools: {len(names)} registered OK")

    # 3. Context Builder
    from src.llm.context_builder import build_default_system_prompt
    prompt = await build_default_system_prompt(query="hello")
    print(f"3. Context: {len(prompt)} chars OK")

    # 4. Agent Loop（真正呼叫 Gemini）
    from src.llm.agent_loop import agent_loop
    print("4. Calling agent_loop (may take 3-5s)...")
    result = await agent_loop(
        user_message="你好，你是誰？",
        system_prompt=prompt,
        max_iterations=2,
    )
    if result.text:
        print(f"   Reply: {result.text[:80]}...")
        print(f"   Iterations: {result.iterations}")
        print("   OK!")
    else:
        print("   FAIL: no reply text")
        print(f"   tool_calls_log: {result.tool_calls_log}")

    print("\n=== DONE ===")


if __name__ == "__main__":
    asyncio.run(test())
