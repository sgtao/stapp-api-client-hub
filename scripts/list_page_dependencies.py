"""
指定ファイルのローカルimportを再帰的に解析して依存ファイルパスを出力するスクリプト。

Usage:
    # 指定ファイルの依存関係を表示
    python scripts/list_page_dependencies.py ./src/pages/11_simple_api_client.py

    # 複数ファイル指定
    python scripts/list_page_dependencies.py ./src/pages/11_simple_api_client.py ./src/pages/12_config_api_client.py

    # 引数なし: src/ 配下の全 .py ファイルを対象
    python scripts/list_page_dependencies.py
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
    parser = argparse.ArgumentParser(
        description="指定ファイルのローカルimport依存関係を再帰的に表示。引数なしは src/ 配下の全 .py を対象。"
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="対象ファイルの相対/絶対パス。省略時は src/ 配下の全 .py ファイル。",
    )
    args = parser.parse_args()

    if args.files:
        targets = [Path(f).resolve() for f in args.files]
    else:
        targets = sorted(SRC_ROOT.rglob("*.py"))

    for target in targets:
        if not target.exists():
            print(f"[ERROR] not found: {target}")
            continue
        print_dependencies(target)


if __name__ == "__main__":
    main()
