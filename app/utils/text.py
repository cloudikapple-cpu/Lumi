import re


def split_text(text: str, max_length: int = 4096) -> list[str]:
    if len(text) <= max_length:
        return [text]

    parts: list[str] = []
    while text:
        if len(text) <= max_length:
            parts.append(text)
            break

        split_pos = _find_split_position(text, max_length)
        parts.append(text[:split_pos].rstrip())
        text = text[split_pos:].lstrip()

    return parts


def _find_split_position(text: str, max_length: int) -> int:
    search_zone = text[:max_length]

    code_block_pattern = re.compile(r'```')
    matches = list(code_block_pattern.finditer(search_zone))
    open_blocks = sum(1 for m in matches) % 2
    if open_blocks % 2 != 0 and len(matches) >= 2:
        last_match = matches[-2] if open_blocks else matches[-1]
        return last_match.end()

    for sep in ["\n\n", "\n", ". ", "! ", "? ", ", ", " "]:
        pos = search_zone.rfind(sep)
        if pos > max_length * 0.3:
            return pos + len(sep)

    return max_length


def truncate_text(text: str, max_length: int = 200) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_search_context(results: list) -> str:
    if not results:
        return ""
    parts = []
    for i, r in enumerate(results, 1):
        parts.append(f"[{i}] {r.title}\n{r.snippet}\nURL: {r.url}")
    return "\n\n".join(parts)
