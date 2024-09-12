import asyncio

import httpx
import quart
from result import Result, Ok, Err

app = quart.Quart(__name__)
app.config.from_prefixed_env("SPOOFIFY")


def make_llm_payload(prompt: str) -> dict:
    return {
        "model": "llama3.1:8b-instruct-q8_0",
        "prompt": prompt,
        "stream": False,
        "keep_alive": "3h",
        "context": [],
    }


async def get_genre() -> str:
    httpx_client: httpx.AsyncClient = app.httpx_client
    response = await httpx_client.get(
        "https://binaryjazz.us/wp-json/genrenator/v1/genre/1"
    )

    # The above API returns a JSON string, so we call `response.json()` to evaluate it.
    return response.json()


async def query_llm(payload: dict) -> Result[str, str]:
    httpx_client: httpx.AsyncClient = quart.current_app.httpx_client
    base_url = app.config["LLAMA_URL"]
    try:
        response = await httpx_client.post(f"{base_url}/api/generate", json=payload)
        return Ok(response.json()["response"])
    except Exception as e:
        return Err(f"Failed to get the LLM response: {e}")


async def get_band_info(genre: str) -> Result[dict, str]:
    while not quart.current_app.model_ready:
        await asyncio.sleep(5)

    prompt = (
        f"You are given a fictional genre: {genre}."
        "Respond with fictional band information, as JSON in the format "
        "with keys {band_name: string, band_members: [1..5][string], top_songs[5][string]}. "
        "In your response, give only 1 JSON object with no formatting, and no other output."
    )
    payload = make_llm_payload(prompt)
    result = await query_llm(payload)
    match result:
        case Ok(llm_response):
            band_info = {"genre": genre, **quart.json.loads(llm_response)}
            return Ok(band_info)
        case _:
            return result


async def wake_up_model():
    """Sends a dummy empty prompt to the model to make sure it's loaded"""
    payload = make_llm_payload("")
    await query_llm(payload)
    quart.current_app.model_ready = True


@app.before_serving
async def startup():
    app.httpx_client = httpx.AsyncClient()
    app.add_background_task(wake_up_model)


@app.after_serving
async def shutdown():
    await app.httpx_client.aclose()


@app.route("/")
async def index():
    if not app.model_ready:
        return "LLM isn't ready", 503

    genre = await get_genre()
    assert genre
    match await get_band_info(genre):
        case Ok(band_info):
            return quart.jsonify(band_info)
        case Err(e):
            return f"Failed to get response from LLM: {e}", 502


def main():
    app.run()
