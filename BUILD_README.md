# DOIO Layout Viewer - 実行ファイルビルド手順

## 必要な依存パッケージのインストール

```powershell
pip install pyinstaller kivy-deps.sdl2 kivy-deps.glew
```

## ビルド方法

### 方法1: ビルドスクリプトを使用（推奨）

```powershell
python build_exe.py
```

### 方法2: specファイルを使用

```powershell
pyinstaller DOIO_Layout_Viewer.spec
```

### 方法3: コマンドラインから直接

```powershell
pyinstaller --name=DOIO_Layout_Viewer --onefile --windowed --add-data="DOIO.png;." --add-data="my.kv;." --add-data="layout.json;." --hidden-import=kivy --hidden-import=japanize_kivy --hidden-import=PIL main.pyw
```

## ビルド後

実行ファイルは `dist` フォルダに生成されます：
- `dist/DOIO_Layout_Viewer.exe`

## 配布方法

1. `dist/DOIO_Layout_Viewer.exe` を配布
2. `layout.json`と`DOIO.png` を同じフォルダに配置
3. JSONファイルはドラッグ&ドロップで読み込み可能

## トラブルシューティング

### Kivyの依存関係エラーが出る場合

```powershell
pip install kivy[base] kivy-deps.sdl2 kivy-deps.glew kivy-deps.angle
```

### サイズを小さくしたい場合

UPXを使用してファイルサイズを圧縮：
```powershell
pip install pyinstaller[encryption]
```

### デバッグモード

コンソールウィンドウを表示してエラーを確認：
- `--windowed` を `--console` に変更
