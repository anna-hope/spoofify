import asyncio
import datetime as dt
from json.decoder import JSONDecodeError
from typing import Final

import httpx
import quart
from result import Result, Ok, Err, as_result, as_async_result, do_async

app = quart.Quart(__name__)
app.config.from_prefixed_env("SPOOFIFY")

safe_json_loads: Final = as_result(JSONDecodeError)(quart.json.loads)


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
    safe_post = as_async_result(httpx.NetworkError, httpx.TimeoutException)(
        httpx_client.post
    )

    safe_get_response = as_result(httpx.RequestError, KeyError)(
        lambda response: response.json()["response"]
    )

    if (response := await safe_post(f"{base_url}/api/generate", json=payload)).is_err():
        return response.err()

    return safe_get_response(response.ok())


async def get_band_info(genre: str) -> Result[dict, str]:
    while not quart.current_app.model_ready:
        await asyncio.sleep(5)

    prompt = (
        f"You are given a fictional genre: {genre}."
        "Respond with fictional band information, as JSON in the format "
        "with keys "
        "{band_name: string, band_members: [1-5][string], top_songs[5][string], "
        "related_bands[5][string]}, next_tour_date: YYYY-MM-DD. "
        "In your response, give only 1 JSON object with no formatting, and no other output."
        f"Current date is {dt.date.today()}"
    )
    payload = make_llm_payload(prompt)
    return await do_async(
        Ok({"genre": genre, **parsed_llm_response})
        for llm_response in await query_llm(payload)
        for parsed_llm_response in safe_json_loads(llm_response)
    )


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
    if not genre:
        return "Couldn't get a genre", 502

    match await get_band_info(genre):
        case Ok(band_info):
            return quart.jsonify(band_info)
        case Err(e):
            return f"Failed to get response from LLM: {e}", 502


def main():
    app.run()
