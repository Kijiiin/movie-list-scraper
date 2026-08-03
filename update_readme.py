from pathlib import Path
import re

config = Path("config.py").read_text(encoding="utf-8")
readme_path = Path("README.md")
readme = readme_path.read_text(encoding="utf-8")

match = re.search(
    r'^\s*STREAMING_DOMAIN\s*=\s*["\']([^"\']+)["\']',
    config,
    re.MULTILINE
)

if not match:
    raise SystemExit("STREAMING_DOMAIN non trovato in config.py")

domain = match.group(1)

# Aggiunge https:// se non è già presente
if not domain.startswith(("http://", "https://")):
    domain = f"https://{domain}"

start = "<!-- BASE_URL -->"
end = "<!-- /BASE_URL -->"

replacement = f"{start}\n{domain}\n{end}"

pattern = re.escape(start) + r".*?" + re.escape(end)

new_readme, count = re.subn(
    pattern,
    replacement,
    readme,
    flags=re.DOTALL
)

if count == 0:
    raise SystemExit(
        "Marcatori BASE_URL non trovati nel README.md"
    )

readme_path.write_text(new_readme, encoding="utf-8")

print(f"BASE_URL aggiornato nel README: {domain}")
