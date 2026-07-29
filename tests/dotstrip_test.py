string = "  Trumpâ€™s attacks on mail balloting and concerns over delays turn midterms spotlight on Postal Service  "

'''
print(string)
print(string.strip())
string = string.replace("â", "")
print(string)
'''

unallowed_chars = ['â', '€', '™', '’', '“', '”', '–']
for char in unallowed_chars:
    string = string.replace(char, "")

print(string)