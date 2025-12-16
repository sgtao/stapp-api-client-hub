# -*- mode: python ; coding: utf-8 -*-
# api_server.spec - PyInstallerの設定ファイル
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# FastAPI/Streamlit関連の依存関係を自動収集
fastapi_hidden_imports = collect_submodules("fastapi")
uvicorn_hidden_imports = collect_submodules("uvicorn")
streamlit_hidden_imports = collect_submodules("streamlit")

# データファイルの収集
fastapi_data = collect_data_files("fastapi")
uvicorn_data = collect_data_files("uvicorn")
streamlit_data = collect_data_files("streamlit")

# Analysis: アプリケーションの依存関係を分析
a = Analysis(
    ["api_server.py"],  # エントリーポイント
    pathex=[],  # Pythonのインポートパス
    binaries=[],  # 必要なバイナリファイル
    datas=[
        # ソースコードと設定ファイル
        ("src/api", "api"),
        ("src/logic", "logic"),
        ("src/ui", "ui"),
        ("assets", "assets"),
        # ("logs", "logs"),
    ]
    + fastapi_data
    + uvicorn_data
    + streamlit_data,
    hiddenimports=[
        # 明示的にインポートが必要なモジュール
        "fastapi",
        "uvicorn",
        "streamlit",
        "requests",
        "jmespath",
        "httpx",
        "duckduckgo_search",
        "pandas",
        "numpy",
        "yaml",
        "logging",
        "urllib.parse",
        "json",
        "re",
        "argparse",
    ]
    + fastapi_hidden_imports
    + uvicorn_hidden_imports
    + streamlit_hidden_imports,
    hookspath=["./hooks"],  # カスタムフックスクリプトのパス
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# PYZ: Pythonモジュールをzip形式にアーカイブ化
pyz = PYZ(a.pure)

# EXE: 実行ファイルの設定
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="api_server",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# COLLECT: 実行に必要な全ファイルを収集
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="api_server",
)
