"""LLM CLI Skill — Agent CLI 多後端封裝。"""
import asyncio
import os
import platform
from src.skills.base import BaseSkill, SkillResult, SkillType


class LLMCliSkill(BaseSkill):
    """透過 CLI subprocess 呼叫 LLM（Gemini/Kiro/Claude）。"""

    skill_id = "llm_cli"
    skill_type = SkillType.LLM
    description = "Agent CLI 多後端呼叫（chat/codegen/evaluate）"
    version = "1.0.0"

    BACKENDS = ["gemini", "kiro", "claude"]

    async def execute(self, params: dict) -> SkillResult:
        """執行 LLM CLI。params: prompt, mode, backend（選填）。"""
        prompt = params.get("prompt", "")
        mode = params.get("mode", "chat")
        backend = params.get("backend") or os.getenv("LLM_BACKEND", "gemini")

        if not prompt:
            return SkillResult(success=False, error="prompt 不可為空")

        # 包裝 prompt
        wrapped = self._wrap_prompt(prompt, mode)

        # 嘗試指定後端，失敗則 fallback
        backends_to_try = [backend] + [b for b in self.BACKENDS if b != backend]
        for b in backends_to_try:
            result = await self._call_cli(b, wrapped)
            if result.success:
                result.data["backend"] = b
                return result

        return SkillResult(success=False, error="所有 LLM 後端均不可用")

    def _wrap_prompt(self, prompt: str, mode: str) -> str:
        """依模式包裝 prompt。"""
        if mode == "codegen":
            return f"只回傳程式碼，不要解釋。需求：{prompt}"
        if mode == "evaluate":
            return (
                f"判斷意圖並回傳 JSON：{{\"intent\":\"...\",\"skill_id\":\"...\","
                f"\"params\":{{}}}}。使用者說：{prompt}"
            )
        return prompt

    async def _call_cli(self, backend: str, prompt: str) -> SkillResult:
        """呼叫單個 CLI 後端。"""
        cmd = self._build_cmd(backend, prompt)
        if not cmd:
            return SkillResult(success=False, error=f"{backend} CLI 指令無法建構")

        env = os.environ.copy()
        env["GEMINI_CLI_TRUST_WORKSPACE"] = "true"

        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=os.getenv("AI_BOT_WORKSPACE", "."),
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
            output = stdout.decode("utf-8", errors="replace").strip()

            if output:
                return SkillResult(success=True, data={"output": output})
            return SkillResult(success=False, error=stderr.decode("utf-8", errors="replace")[:300])
        except asyncio.TimeoutError:
            return SkillResult(success=False, error=f"{backend} timeout")
        except Exception as e:
            return SkillResult(success=False, error=str(e)[:300])

    def _build_cmd(self, backend: str, prompt: str) -> str | None:
        """建構 CLI 指令字串。"""
        safe_prompt = prompt.replace('"', '\\"')
        is_win = platform.system() == "Windows"
        suffix = ".cmd" if is_win else ""

        if backend == "gemini":
            return f'gemini{suffix} -p "{safe_prompt}"'
        if backend == "kiro":
            return f'kiro-cli{suffix} chat --trust-all-tools --legacy-ui --message "{safe_prompt}"'
        if backend == "claude":
            return f'claude{suffix} -p "{safe_prompt}"'
        return None
