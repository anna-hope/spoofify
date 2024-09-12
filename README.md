# spoofify

[Genrenator](https://binaryjazz.us/genrenator-api/)
is a free public API that generates music genres that
don't exist... but maybe should!

Examples:
- rhythm and euphonium chill 
- punk didgeridoo 
- czech pianostep 

Don't these sound just like your next favorite genre
that you would *love* to show up in your
favorite music service?

Except... How do you find a performer who
really represents your new favorite genre, so
that you know where to start exploring it?

What are their top tracks? (You'll get to their back
catalog and deep cuts eventually, 
of course, but I find that it helps to start with the more
popular songs.)

And who even *is* in this musical collective?

I have no idea! They're not a real band (yet)!

But I know [an excellent kind of tool](https://en.wikipedia.org/wiki/Large_language_model)
that would gladly tell me things that don't exist.

So let's use it to find your next musical obsession!

### Run the project

Prerequisites:

- [Rye](https://rye.astral.sh/)

#### Run locally

- `rye sync`
- `export SPOOFIFY_LLAMA_URL=<url_of_llama_instance>`
- `rye run`

You can either run your own local ollama 
(with `llama3.1:8b-instruct-q8_0`, currently hardcoded)
or ask @anna-hope for a URL to her own instance
(if you're a Recurser or another friend, you should
know where to find her!)

### Run tests

You can run the *extensive* test suite with

`rye test`

(Uses pytest)

### Format

`rye fmt`

(Uses Black)

### Lint

`rye lint`

(Uses Ruff)

## LLM notes

I chose `llama3.1:8b-instruct-q8_0` because I found it to
have a good balance between being fast enough to get
a response, understanding the prompt well enough,
and good enough at returning a response in the expected
format. 

This model requires about 10GB of VRAM (on my M2 Max).

Because it is an LLM, it might occasionally generate
responses that satisfy the expected format, but are otherwise
strange or otherwise not ideal. Or sometimes it might completely fail to
do what we want.


## Additional information

This project was originally created as a way to demonstrate
the project management capabilities of Rye versus other
Python tooling. The code is not really the point, but
I did try to make it do something fun.
