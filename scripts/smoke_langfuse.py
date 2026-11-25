from dotenv import load_dotenv
load_dotenv()

from langfuse import observe, get_client

@observe(as_type="generation", name="smoke-test")
def fake_call():
    get_client().update_current_generation(
        model="test-model",
        input=[{"role": "user", "content": "hello"}],
        output="hi",
        metadata={"route": "local", "sources": ["docs/example.pdf#p1"]},
    )
    return "hi"

fake_call()
get_client().flush()