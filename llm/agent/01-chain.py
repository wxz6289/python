from langchain_core.runnables import chain

@chain
def add_val(x: dict) -> dict:
  return {"val": x["val"] + 1 }

result = add_val({"val": 2})
print(result)
