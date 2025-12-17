"""
PyInstallerを使用してKivyアプリを実行ファイルにビルドするスクリプト
"""
import os
import subprocess
import sys

def build_exe():
    """実行ファイルをビルド"""

    # PyInstallerのインストール確認
    try:
        import PyInstaller
    except ImportError:
        print("PyInstallerがインストールされていません。インストール中...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # japanize_kivyのフォントパスを取得
    try:
        import japanize_kivy
        japanize_path = os.path.dirname(japanize_kivy.__file__)
        font_path = os.path.join(japanize_path, 'resources', 'ipaexg00401', 'ipaexg.ttf')
        font_data = f"{font_path};japanize_kivy/resources/ipaexg00401"
    except ImportError:
        print("警告: japanize_kivyが見つかりません")
        font_data = None

    # ビルドコマンド
    build_command = [
        "pyinstaller",
        "--name=DOIO_Layout_Viewer",  # 実行ファイル名
        "--onefile",                   # 単一の実行ファイルにまとめる
        "--windowed",                  # コンソールウィンドウを表示しない
        "--add-data=DOIO.png;.",       # 画像ファイルを含める
        "--add-data=my.kv;.",          # kvファイルを含める
        "--add-data=layout.json;.",    # レイアウトファイルを含める
        "--hidden-import=kivy",
        "--hidden-import=japanize_kivy",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.PngImagePlugin",
        "main.pyw"
    ]

    # フォントデータを追加
    if font_data:
        build_command.insert(-1, f"--add-data={font_data}")

    print("ビルドを開始します...")
    print(" ".join(build_command))

    try:
        subprocess.check_call(build_command)
        print("\n✓ ビルドが完了しました！")
        print("実行ファイルは dist/DOIO_Layout_Viewer.exe にあります")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ ビルドに失敗しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
