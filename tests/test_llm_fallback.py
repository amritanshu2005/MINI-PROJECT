from services.coaching.llm import LLMCoach


class BrokenChatCompletions:
    def create(self, **kwargs):
        raise Exception("model_not_found")


class BrokenClient:
    def __init__(self):
        self.chat = type("Chat", (), {"completions": BrokenChatCompletions()})()


def test_llm_falls_back_when_model_is_unavailable():
    coach = LLMCoach(BrokenClient())
    text = coach.give_feedback("workout_started", "The user is leaning too far forward.")

    assert isinstance(text, str)
    assert len(text) > 0
    assert "form" in text.lower() or "good work" in text.lower() or "keep" in text.lower()
