import fileinput, re

pat = re.compile(r"[\w]+@[\w]+", re.IGNORECASE)
addresses = set()

for line in fileinput.input():
  for address in pat.findall(line):
    addresses.add(address)

for address in sorted(addresses):
  print(address)
