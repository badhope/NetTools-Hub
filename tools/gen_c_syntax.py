import pathlib
import plistlib

pat = lambda **kw: {k: v for k, v in kw.items() if v is not None}

grammar = {
    "name": "C (Mashang Lite)",
    "scopeName": "source.c",
    "fileTypes": ["c", "h"],
    "patterns": [
        {"name": "comment.block.c", "begin": r"/\*", "end": r"\*/"},
        {"name": "comment.line.double-slash.c", "match": r"//.*$"},
        {"name": "constant.numeric.c", "match": r"\b[0-9]+(\.[0-9]+)?\b"},
        {
            "name": "string.quoted.double.c",
            "begin": '"',
            "end": '"',
            "patterns": [
                {"name": "constant.character.escape.c", "match": r"\\."}
            ],
        },
        {"name": "string.quoted.single.c", "begin": "'", "end": "'"},
        {
            "name": "storage.type.c",
            "match": r"\b(int|double|float|char|void|long|short|unsigned|signed|const|static)\b",
        },
        {
            "name": "keyword.control.c",
            "match": r"\b(if|else|while|for|return|break|continue|switch|case|default|goto|do)\b",
        },
        {
            "name": "keyword.other.c",
            "match": r"\b(struct|typedef|sizeof|enum|union|extern|inline)\b",
        },
        {
            "name": "support.function.c",
            "match": r"\b(printf|scanf|puts|putchar|assert|assertOutput|sqrt|pow|abs)\b",
        },
        {"name": "preprocessor.include.c", "match": r"^\s*#.*$"},
    ],
    "uuid": "E5B7A3C1-4D2F-4A8B-9C6D-1F0E2A3B4C5D",
}

path = pathlib.Path("app/src/main/assets/syntaxes/c.tmLanguage.json")
with open(path, "wb") as f:
    plistlib.dump(grammar, f)

# 回读校验
with open(path, "rb") as f:
    d = plistlib.load(f)
print("scopeName:", d["scopeName"], "| fileTypes:", d["fileTypes"], "| patterns:", len(d["patterns"]))
print("printf regex:", d["patterns"][8]["match"])
