import urllib.parse
from urllib.parse import urlsplit, urlunsplit

def canonicalise_url(url: str) -> None:
    """
    Canonicalise a URL for storage in the database
    """
    url = url.strip()
    parsed_url = urllib.parse.urlparse(url)
    print(parsed_url)
    parts = urlsplit(url)
    cleaned = parts._replace(
        scheme=parts.scheme.lower(),
        netloc=parts.netloc.lower(),
        fragment = "",
    )
    rebuilt = urlunsplit(cleaned)
    print(rebuilt)

url = "https://www.example.com/path/to/page?query=param#fragment"
canonicalise_url(url)