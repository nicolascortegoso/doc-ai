from agent.tool.implementations.default import DefaultTool


class TestDefaultTool:
    def test_name_returns_string(self):
        tool = DefaultTool()
        assert isinstance(tool.name, str)
        assert tool.name == "default"

    def test_description_returns_non_empty_string(self):
        tool = DefaultTool()
        assert isinstance(tool.description, str)
        assert len(tool.description) > 0

    def test_invoke_returns_empty_string(self):
        tool = DefaultTool()
        assert tool.invoke("any input") == ""

    def test_invoke_never_raises(self):
        tool = DefaultTool()
        result = tool.invoke("")
        assert isinstance(result, str)