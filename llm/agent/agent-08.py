import os
import json
from dotenv import load_dotenv
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

GRAPHQL_ENDPOINT = os.getenv(
  "GRAPHQL_ENDPOINT",
  "https://countries.trevorblades.com/",
)


def execute_graphql(
  endpoint: str,
  query: str,
  variables: dict | None = None,
  headers: dict | None = None,
) -> dict:
  response = requests.post(
    endpoint,
    json={
      "query": query,
      "variables": variables or {},
    },
    headers={
      "Content-Type": "application/json",
      **(headers or {}),
    },
    timeout=30,
  )
  response.raise_for_status()

  result = response.json()
  if result.get("errors"):
    raise RuntimeError(json.dumps(result["errors"], ensure_ascii=False, indent=2))
  return result["data"]


def get_auth_headers() -> dict:
  token = os.getenv("GRAPHQL_TOKEN")
  if not token:
    return {}
  return {"Authorization": f"Bearer {token}"}


if __name__ == "__main__":
  query = """
  query GetCountry($code: ID!) {
    country(code: $code) {
      code
      name
      native
      capital
      currency
      languages {
        code
        name
      }
    }
  }
  """

  variables = {"code": "CN"}
  data = execute_graphql(
    GRAPHQL_ENDPOINT,
    query,
    variables=variables,
    headers=get_auth_headers(),
  )

  print(json.dumps(data, ensure_ascii=False, indent=2))
