# My News

I wanted a small headless app that gives me recent news I am actually interested in, from sources I have chosen to trust. My News fetches articles from configured RSS feeds, works out how well they match my interests, and generates a ranked PDF digest with links back to the original articles.

It is basically a very small personal search engine for news, driven by one YAML file and one command.

The scoring algorithm actually ended up curating interesting stuff often enough to where I am going to expand to include a head as there is a lot of useful functionality that can be added to make QoL and reusability better.

P.S. It also ended up pulling from sources like BBC iPlayer, originally I felt like this was some weird bug but I think its just because sites will tend to refer to their other resources on their news pages and I was going to make a patch for this but after thinking about it I actually think its kind of a neat side effect (feature not bug).

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

The digest is written to `output/` by default as a PDF. If WeasyPrint cannot run on your machine,
you can still generate the same digest as HTML by choosing an `.html` output path, or let the
app fall back automatically when PDF rendering fails:

```bash
my-news run --config example.yaml --output output/my-digest.pdf
my-news run --config example.yaml --output output/my-digest.html # You can open this in VSCode with right click open in Integrated Browser
```

## Configuration and ranking

The YAML controls which sources are enabled, which interests apply to each source, how strongly terms and phrases should be weighted, and things like the lookback window and maximum number of articles.

Articles are scored using a slightly bastardised BM25 algorithm. Matches in titles and article bodies are weighted separately, then source priority and recency are added before the best results are put into the PDF. This lets me heavily favour something specific like gaming while only giving something noisy like AI a slight boost.

The project currently uses feeds from sources including the BBC, The Guardian, ProPublica, AP and Reuters. Some feeds use RSSHub and may depend on the availability of its public service. May (probably will) continue to maintain and update the config for myself and might make the occasional change here and there in general when I find reliable sources I want to use or new topics im interested in.