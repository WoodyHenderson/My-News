# My News

I wanted a small headless app that gives me recent news I am actually interested in, from sources I have chosen to trust. My News fetches articles from configured RSS feeds, works out how well they match my interests, and generates a ranked PDF digest with links back to the original articles.

It is basically a very small personal search engine for news, driven by one YAML file and one command.

## Setup

Python 3.12 or newer is required.

```bash
python3.12 -m venv .venv
source .venv/bin/activate # Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## Using it

The active configuration lives at `config/config.yaml`, with `example.yaml` kept as a useful starting point.

```bash
my-news validate
my-news run
```

The PDF is written to `output/` by default. A different path or configuration can also be supplied:

```bash
my-news run --config example.yaml --output output/my-digest.pdf
```

## Configuration and ranking

The YAML controls which sources are enabled, which interests apply to each source, how strongly terms and phrases should be weighted, and things like the lookback window and maximum number of articles.

Articles are scored using a slightly bastardised BM25 algorithm. Matches in titles and article bodies are weighted separately, then source priority and recency are added before the best results are put into the PDF. This lets me heavily favour something specific like gaming while only giving something noisy like AI a slight boost.

The project currently uses feeds from sources including the BBC, The Guardian, ProPublica, AP and Reuters. Some feeds use RSSHub and may depend on the availability of its public service. May (probably will) continue to maintain and update the config for myself and might make the occasional change here and there in general when I find reliable sources I want to use or new topics im interested in.