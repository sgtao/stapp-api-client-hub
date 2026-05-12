"""
src/pages/*.py の各ファイルについて、
ローカルimportを再帰的に解析して依存ファイルパスを出力するスクリプト。

Usage:
    python 00_references/list_page_dependencies.py
    python 00_references/list_page_dependencies.py --page 11_simple_api_client.py
"""

import ast
import argparse
from pathlib import Path


SRC_ROOT = Path(__file__).parent.parent / "src"


def resolve_import_path(module: str) -> Path | None:
    """'ui.ApiRequestHeader' → src/ui/ApiRequestHeader.py に変換。存在しなければ None。"""
    candidate = SRC_ROOT / Path(*module.split(".")).with_suffix(".py")
    return candidate if candidate.exists() else None


def extract_local_imports(file_path: Path) -> list[Path]:
    """ファイルからローカルモジュールのimportを抽出してパスのリストを返す。"""
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError):
        return []

    paths = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            resolved = resolve_import_path(node.module)
            if resolved:
                paths.append(resolved)
    return paths


def collect_dependencies(entry: Path, visited: set[Path] | None = None) -> list[Path]:
    """entry ファイルから再帰的に依存ファイルを収集して順序付きリストで返す。"""
    if visited is None:
        visited = set()

    result = []
    if entry in visited:
        return result
    visited.add(entry)

    for dep in extract_local_imports(entry):
        if dep not in visited:
            result.append(dep)
            result.extend(collect_dependencies(dep, visited))

    return result


def print_dependencies(page_file: Path) -> None:
    rel = page_file.relative_to(SRC_ROOT.parent)
    print(rel.as_posix())

    deps = collect_dependencies(page_file)
    for dep in deps:
        print(dep.relative_to(SRC_ROOT.parent).as_posix())

    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="src/pages/*.py の依存ファイル一覧を表示")
    parser.add_argument(
        "--page",
        metavar="FILENAME",
        help="対象ページファイル名 (例: 11_simple_api_client.py)。省略時は全ページ。",
    )
    args = parser.parse_args()

    pages_dir = SRC_ROOT / "pages"

    if args.page:
        targets = [pages_dir / args.page]
    else:
        targets = sorted(pages_dir.glob("*.py"))

    for page in targets:
        if not page.exists():
            print(f"[ERROR] not found: {page}")
            continue
        print_dependencies(page)


if __name__ == "__main__":
    main()
