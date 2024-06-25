import os, json
"""Так как git secret ломает .json, мы его перезаписываем"""
token_data = os.environ['TOKEN_GOOGLE_API']
token_path = os.path.join(os.path.dirname(__file__), "../../token.json")
with open(token_path, 'w') as f:
    json.dump(json.loads(token_data), f, indent=4)
