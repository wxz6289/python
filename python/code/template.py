import re, fileinput

filed_pattern = re.compile(r"\[(.+?)\]")

scope = {}


def replacement(match):
    code = match.group(1)
    try:
        return str(eval(code, scope))
    except SyntaxError:
        exec(code, scope)
        return ""


lines = []
for line in fileinput.input():
    lines.append(line)

text = "".join(lines)

print(filed_pattern.sub(replacement, text))
