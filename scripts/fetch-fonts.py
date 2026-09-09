"""Завантажує потрібні підмножини IBM Plex з Google Fonts і генерує локальний @font-face CSS."""
import re, os, pathlib, urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

OUT = pathlib.Path(r"D:\creation\site saas\assets\fonts")
OUT.mkdir(parents=True, exist_ok=True)

WANTED_SUBSETS = {"latin", "latin-ext", "cyrillic", "cyrillic-ext"}
FAMILIES = {
    "IBM Plex Sans": [400, 500, 600],
    "IBM Plex Mono": [400, 500, 600],
}
SLUG = {"IBM Plex Sans": "ibm-plex-sans", "IBM Plex Mono": "ibm-plex-mono"}


def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as r:
        return r.read() if binary else r.read().decode("utf-8")


def build_url():
    parts = []
    for fam, weights in sorted(FAMILIES.items()):
        parts.append(f"family={fam.replace(' ', '+')}:wght@" + ";".join(str(w) for w in weights))
    return "https://fonts.googleapis.com/css2?" + "&".join(parts) + "&display=swap"


css = get(build_url())

# Кожен блок передує коментарем із назвою підмножини
blocks = re.split(r"/\*\s*([a-z-]+)\s*\*/", css)
faces, downloaded = [], 0

for i in range(1, len(blocks), 2):
    subset, body = blocks[i], blocks[i + 1]
    if subset not in WANTED_SUBSETS:
        continue
    fam = re.search(r"font-family:\s*'([^']+)'", body).group(1)
    weight = int(re.search(r"font-weight:\s*(\d+)", body).group(1))
    url = re.search(r"url\((https://[^)]+\.woff2)\)", body).group(1)
    urange = re.search(r"unicode-range:\s*([^;]+);", body).group(1).strip()
    if fam not in FAMILIES or weight not in FAMILIES[fam]:
        continue

    name = f"{SLUG[fam]}-{weight}-{subset}.woff2"
    (OUT / name).write_bytes(get(url, binary=True))
    downloaded += 1
    faces.append((fam, weight, subset, name, urange))

lines = []
for fam, weight, subset, name, urange in faces:
    lines.append(
        "@font-face{font-family:'%s';font-style:normal;font-weight:%d;font-display:swap;"
        "src:url('assets/fonts/%s') format('woff2');unicode-range:%s}"
        % (fam, weight, name, urange)
    )

pathlib.Path(
    r"C:\Users\User\AppData\Local\Temp\claude\D--creation-site-saas"
    r"\8fa74983-2acf-4340-a752-2374736f285e\scratchpad\fontface.css"
).write_text("\n".join(lines), encoding="utf-8")

total = sum(f.stat().st_size for f in OUT.glob("*.woff2"))
print(f"downloaded {downloaded} files, {total/1024:.0f} KB total")
print(f"@font-face rules: {len(lines)}")
