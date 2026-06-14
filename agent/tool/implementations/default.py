from agent.tool.base import Tool


class DefaultTool(Tool):
    """No-op tool. Returns empty string.

    Used as a placeholder for testing.
    """

    @property
    def name(self) -> str:
        return "default"

    @property
    def description(self) -> str:
        return "A no-op tool that returns an empty string."

    def invoke(self, input: str) -> str:
        return ""