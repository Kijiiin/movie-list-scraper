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

start = "<!-- STREAMING_DOMAIN -->"
end = "<!-- /STREAMING_DOMAIN -->"

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
        "Marcatori STREAMING_DOMAIN non trovati nel README.md"
    )

readme_path.write_text(new_readme, encoding="utf-8")

print(f"Streaming domain: {domain}")
