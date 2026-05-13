import asyncio
import json
import os
from typing import Optional

class MCPClient:
    def __init__(self, name: str, cmd: list):
        self.name = name
        self.cmd = cmd
        self.proc: Optional[asyncio.subprocess.Process] = None
        self.req_id = 0
        self._lock = asyncio.Lock()

    async def ensure_running(self):
        if self.proc and self.proc.returncode is None:
            return
        self.proc = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )

    async def call(self, tool: str, args: dict) -> dict:
        await self.ensure_running()
        self.req_id += 1
        req = {
            "jsonrpc": "2.0",
            "id": self.req_id,
            "method": "tools/call",
            "params": {"name": tool, "arguments": args},
        }
        async with self._lock:
            self.proc.stdin.write((json.dumps(req) + "\n").encode())
            await self.proc.stdin.drain()
            line = await asyncio.wait_for(self.proc.stdout.readline(), timeout=30)
        result = json.loads(line)
        return result

    async def close(self):
        if self.proc and self.proc.returncode is None:
            self.proc.terminate()
            try:
                await asyncio.wait_for(self.proc.wait(), timeout=5)
            except asyncio.TimeoutError:
                self.proc.kill()


class SequentialThinkingMCP(MCPClient):
    def __init__(self):
        super().__init__("sequential-thinking", [
            "npx", "-y", "@modelcontextprotocol/server-sequential-thinking"
        ])

    async def think(self, thought: str, thought_number: int = 1,
                    total_thoughts: int = 3, next_needed: bool = True) -> dict:
        return await self.call("sequentialthinking", {
            "thought": thought,
            "thoughtNumber": thought_number,
            "totalThoughts": total_thoughts,
            "nextThoughtNeeded": next_needed,
        })

    async def run_sequence(self, thoughts: list) -> str:
        full = ""
        n = len(thoughts)
        for i, t in enumerate(thoughts):
            is_last = (i == n - 1)
            result = await self.think(t, i + 1, n, not is_last)
            if "error" in result:
                continue
            content = result.get("result", {}).get("content", [])
            for c in content:
                if c.get("type") == "text":
                    full += c["text"] + "\n"
        return full.strip()


class MCPManager:
    def __init__(self):
        self._clients = {}
        self._initialized = False

    async def init(self):
        if self._initialized:
            return
        self._clients["sequential-thinking"] = SequentialThinkingMCP()
        await self._clients["sequential-thinking"].ensure_running()
        scihub_cmd = ["python3", os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "mcp", "scihub_server.py"
        )]
        self._clients["scihub"] = MCPClient("scihub", scihub_cmd)
        await self._clients["scihub"].ensure_running()
        self._initialized = True
        print(f"  MCP: sequential-thinking + scihub attivi")

    def get(self, name: str):
        return self._clients.get(name)

    async def sequential_think(self, thoughts: list) -> str:
        st = self.get("sequential-thinking")
        if not st:
            return ""
        return await st.run_sequence(thoughts)

    async def fetch_paper(self, doi: str) -> str:
        sh = self.get("scihub")
        if not sh:
            return ""
        result = await sh.call("fetch_paper", {"doi": doi})
        content = result.get("result", {}).get("content", [])
        for c in content:
            if c.get("type") == "text":
                return c["text"]
        return ""

    async def close_all(self):
        for client in self._clients.values():
            await client.close()
        self._initialized = False


mcp_manager = MCPManager()
