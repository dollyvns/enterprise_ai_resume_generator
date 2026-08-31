import logging
import time
from abc import ABC, abstractmethod
from typing import Any

from app.services.llm import StructuredLLM


class BaseAgent(ABC):
    name: str

    def __init__(self, llm: StructuredLLM):
        self.llm = llm
        self.logger = logging.getLogger(f"app.agent.{self.name}")

    async def run(self, **kwargs: Any):
        start = time.perf_counter()
        self.logger.info(
            "agent_started",
            extra={"event": "agent_started", "agent": self.name},
        )
        try:
            result = await self.execute(**kwargs)
            return result
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            self.logger.info(
                "agent_completed",
                extra={
                    "event": "agent_completed",
                    "agent": self.name,
                    "duration_ms": round(duration_ms, 2),
                },
            )

    @abstractmethod
    async def execute(self, **kwargs: Any):
        raise NotImplementedError
