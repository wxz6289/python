from re import compile
from fileinput import input

pat = compile("From: (.*) <.*?>$")

for line in input():
    m = pat.match(line)
    if m:
        print(m.group(1))