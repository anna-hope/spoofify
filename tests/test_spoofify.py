import spoofify


def test_make_llm_payload():
    prompt = spoofify.make_llm_payload("Test")
    assert prompt["model"]
