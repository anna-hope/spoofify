import httpx
import quart

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


async def query_llm(payload: dict) -> str:
    httpx_client: httpx.AsyncClient = quart.current_app.httpx_client
    base_url = app.config["LLAMA_URL"]
    response = await httpx_client.post(f"{base_url}/api/generate", json=payload)
    try:
        return response.json()["response"]
    except Exception as e:
        print(response)


async def get_band_info(genre: str) -> dict:
    prompt = (
        f"You are given a fictional genre: {genre}."
        "Respond with fictional band information, as JSON in the format "
        "with keys {band_name: string, band_members: [2..5][string], top_songs[5][string]}. "
        "In your response, give only 1 JSON object with no formatting, and no other output."
    )
    payload = make_llm_payload(prompt)
    llm_response = await query_llm(payload)
    band_info = {"genre": genre, **quart.json.loads(llm_response)}
    return band_info


async def wake_up_model():
    """Sends a dummy empty prompt to the model to make sure it's loaded"""
    payload = make_llm_payload("")
    await query_llm(payload)


@app.before_serving
async def startup():
    app.httpx_client = httpx.AsyncClient()
    app.add_background_task(wake_up_model)


@app.after_serving
async def shutdown():
    await app.httpx_client.aclose()


@app.route("/")
async def index():
    genre = await get_genre()
    assert genre
    band_info = await get_band_info(genre)
    return quart.jsonify(band_info)


def main():
    app.run(debug=app.config.get("DEBUG"))
