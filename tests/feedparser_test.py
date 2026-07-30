import feedparser

with open("tests/example.xml", 'r') as f:
    example_feed = f.read()

with open("tests/example2.xml", 'r') as f2:
    example_feed2 = f2.read()

'''
parser = feedparser.parse(example_feed)
print(parser.entries[0].title)
for entry in parser.entries:
    print(entry)
    print("\n\n\n")
'''

parser = feedparser.parse(example_feed2)
unallowed_chars = ['â', '€', '™', '’', '“', '”', '–', '<p>']
for entry in parser.entries:
    print(entry)
    title = entry.title
    summary = entry.summary
    for char in unallowed_chars:
        title = title.replace(char, "")
        summary = summary.replace(char, "")

    
    