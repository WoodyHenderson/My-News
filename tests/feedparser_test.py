import feedparser

with open("tests/example.xml", 'r') as f:
    example_feed = f.read()

'''
parser = feedparser.parse(example_feed)
print(parser.entries[0].title)
for entry in parser.entries:
    print(entry)
    print("\n\n\n")
'''

parser = feedparser.parse(example_feed)
unallowed_chars = ['â', '€', '™', '’', '“', '”', '–']
for entry in parser.entries:
    title = entry.title
    summary = entry.summary
    for char in unallowed_chars:
        title = title.replace(char, "")
        summary = summary.replace(char, "")
    
    