import feedparser

with open("tests/example.xml", 'r') as f:
    example_feed = f.read()

parser = feedparser.parse(example_feed)
print(parser.entries[0].title)
for entry in parser.entries:
    print(entry.title)
    print(entry.summary)
