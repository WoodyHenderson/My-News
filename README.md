# My News

I wanted a small headless app that gives me recent news I am actually interested in, from sources I have chosen to trust. My News fetches articles from configured RSS feeds, works out how well they match my interests, and generates a ranked digest with links back to the original articles, this is accessible as either an HTML viewable in app in a Chromium widget or can be exported to a set location as a PDF.

It is basically a very small personal search engine for news, driven by yaml files that represent providers and categories.

The scoring algorithm actually ended up curating interesting stuff often enough to where I am going to expand to include a GUI as there is a lot of useful functionality that can be added to make QoL and reusability better.

At this point the CLI is pretty much deprecated, it provided the basis of the functionality for moving forward but as its signficantly easier to port the changes to the GUI and easier to use as functionality has increased I won't be updating it much from here on (20/08/26)

## Setup

Python 3.12 or newer is required.

```bash
python3.12 -m venv .venv
source .venv/bin/activate # Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## Using it

The active configuration lives at `config/config.yaml`. Run `my-news init` to create it from the shared base at `config/default.yaml`; `example.yaml` is a fuller reference configuration.

```bash
my-news validate
my-news run
my-news opengui
```

The digest is written to /output as a .html and then can be viewed either in the in built chromium widget in the GUI, the integrated browser in your IDE if it contains one or simply opening it in your default browser.

```bash
my-news run --config example.yaml --output output/my-digest.pdf
my-news run --config example.yaml --output output/my-digest.html # You can open this in VSCode with right click open in Integrated Browser
```

## Configuration and ranking

The default YAML controls the basic network and digest settings, attempting to handle cases where pages may be unavailable and identifying itself to publishers (if you don't have this frequently publishers will reject your http requests). The config catalog contains the yaml files corresponding to each publisher/category that users can then select between in the GUI. The weighting of these is currently static but will likely become dynamic in the future to allow users to decide how important each of these is to them specifically.

Articles are scored using a slightly bastardised BM25 algorithm. Matches in titles and article bodies are weighted separately, then source priority and recency are added before the best results are put into the digest. This lets me heavily favour something specific like gaming while only giving something noisy like AI a slight boost. 

Articles that the user has "Marked as Seen" are populated to a local SQlite3 database instance and then filtered out before ranking happens.

The project currently uses feeds from sources including the BBC, The Guardian, ProPublica, AP and Reuters. Some sources use google news' RSS services as they don't have their own publicly available RSS feeds or require a paid API key for this service. Will continue to try and curate as many sources as I find useful, however, will likely only include mainstream providers.