from libs.merger.reducer.models import ReducerInput


class TestReducerInput:
    def test_construction_with_texts_only(self):
        input = ReducerInput(texts=["hello", "world"])
        assert input.texts == ["hello", "world"]
        assert input.prompt_template is None
        assert input.context is None

    def test_construction_with_prompt_template(self):
        input = ReducerInput(texts=["hello"], prompt_template="Summarize: {texts}")
        assert input.prompt_template == "Summarize: {texts}"

    def test_construction_with_context(self):
        input = ReducerInput(texts=["hello"], context={"level": 1})
        assert input.context == {"level": 1}

    def test_construction_with_all_fields(self):
        input = ReducerInput(
            texts=["hello", "world"],
            prompt_template="Summarize: {texts}",
            context={"level": 2},
        )
        assert input.texts == ["hello", "world"]
        assert input.prompt_template == "Summarize: {texts}"
        assert input.context == {"level": 2}

    def test_empty_texts_list(self):
        input = ReducerInput(texts=[])
        assert input.texts == []