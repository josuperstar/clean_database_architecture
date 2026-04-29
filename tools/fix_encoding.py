import pathlib


def _dec(data: bytes) -> str:
    n = len(data)
    if n >= 2 and data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16")
    if data.startswith(b"\xef\xbb\xbf"):
        return data.decode("utf-8-sig")
    sample = min(n, 8000)
    if sample >= 4:
        odd_count = (sample - 1) // 2
        if odd_count > 0:
            odd_zeros = sum(1 for i in range(1, sample, 2) if data[i] == 0)
            if odd_zeros / odd_count >= 0.90:
                return (
                    data.decode("utf-16-le", errors="replace")
                    .replace("\x00", "")
                )
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("cp1252")


def main() -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    paths: list[pathlib.Path] = []
    for name in ("pyproject.toml", "README.md"):
        p = root / name
        if p.is_file():
            paths.append(p)
    for base in (root / "src", root / "tests"):
        if base.is_dir():
            for p in sorted(base.rglob("*.py")):
                if ".venv" in p.parts or "__pycache__" in p.parts:
                    continue
                paths.append(p)
    for p in paths:
        raw = p.read_bytes()
        if not raw:
            raise SystemExit("empty: " + str(p))
        text = _dec(raw).lstrip("\ufeff")
        p.write_text(text, encoding="utf-8", newline="\n")
        print("wrote", p.relative_to(root))


if __name__ == "__main__":
    main()