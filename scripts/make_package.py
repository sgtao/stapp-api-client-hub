# scripts/make_package.py
import subprocess
import shutil
import os
import sys

# ─── 設定 ────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR     = os.path.join(PROJECT_ROOT, "dist")
BUILD_DIR    = os.path.join(PROJECT_ROOT, "build")
PACKAGE_DIR  = os.path.join(DIST_DIR, "package")

SPEC_FILES   = ["api_server.spec", "run_stapp.spec"]
COPY_TARGETS = ["src", ".streamlit", "hooks"]  # copy-to-dist 対象
MERGE_TARGETS = ["api_server", "run_stapp"]    # package にマージする dist サブディレクトリ
ASSET_DIR    = os.path.join(PROJECT_ROOT, "assets")
# ─────────────────────────────────────────────────────


def run(cmd: list[str], cwd: str = PROJECT_ROOT, **kwargs) -> subprocess.CompletedProcess:
    """コマンドを実行し、失敗時は即終了する"""
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, **kwargs)
    if result.returncode != 0:
        print(f"[ERROR] Command failed: {' '.join(cmd)}", file=sys.stderr)
        sys.exit(result.returncode)
    return result


def step(title: str) -> None:
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print('─' * 50)


def rm_dist() -> None:
    """Step 1: build/ dist/ を削除"""
    step("Step 1: clean build & dist")
    for d in [BUILD_DIR, DIST_DIR]:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"Removed: {d}")


def build() -> None:
    """Step 2: PyInstaller でビルド"""
    step("Step 2: pyinstaller build")
    for spec in SPEC_FILES:
        run(["pyinstaller", spec, "--clean"])


def copy_to_dist() -> None:
    """Step 3: 追加ファイルを dist/run_stapp/ にコピー"""
    step("Step 3: copy additional files to dist/run_stapp")
    dest = os.path.join(DIST_DIR, "run_stapp")
    for target in COPY_TARGETS:
        src = os.path.join(PROJECT_ROOT, target)
        if not os.path.exists(src):
            print(f"[SKIP] Not found: {src}")
            continue
        dst = os.path.join(dest, os.path.basename(target))
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
        print(f"Copied: {src} -> {dst}")


def merge_package() -> None:
    """Step 4: api_server/ と run_stapp/ を package/ にマージ"""
    step("Step 4: merge into dist/package")
    os.makedirs(PACKAGE_DIR, exist_ok=True)

    for target in MERGE_TARGETS:
        src_dir = os.path.join(DIST_DIR, target)
        if not os.path.exists(src_dir):
            print(f"[SKIP] Not found: {src_dir}")
            continue
        print(f"# {target}")
        tar_proc = subprocess.run(
            ["tar", "cf", "-", "."],
            cwd=src_dir,
            stdout=subprocess.PIPE,
        )
        subprocess.run(
            ["tar", "xf", "-"],
            cwd=PACKAGE_DIR,
            input=tar_proc.stdout,
        )

    # assets を package/ にコピー
    if os.path.exists(ASSET_DIR):
        dst = os.path.join(PACKAGE_DIR, "assets")
        shutil.copytree(ASSET_DIR, dst, dirs_exist_ok=True)
        print(f"Copied: assets -> {dst}")

    print(f"\nDone: {PACKAGE_DIR}")


STEPS = {
    "rm-dist":      rm_dist,
    "build":        build,
    "copy-to-dist": copy_to_dist,
    "merge-package": merge_package,
}


def main() -> None:
    """
    引数なし → 全ステップ実行
    引数あり → 指定ステップのみ実行（複数可）

    例:
        python scripts/make_package.py
        python scripts/make_package.py build
        python scripts/make_package.py copy-to-dist merge-package
    """
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(STEPS.keys())

    for t in targets:
        if t not in STEPS:
            print(f"[ERROR] Unknown step: '{t}'  available: {list(STEPS.keys())}", file=sys.stderr)
            sys.exit(1)
        STEPS[t]()

    step("All steps completed successfully")


if __name__ == "__main__":
    main()