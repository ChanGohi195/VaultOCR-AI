# セットアップガイド

## 必要環境

- Node.js 18+ (推奨: 20+)
- Python 3.8+ (推奨: 3.10+)
- pnpm (推奨) または npm

## インストール手順

### 1. Node.js依存関係のインストール

```bash
# pnpm推奨
pnpm install

# または npm
npm install
```

### 2. Python環境のセットアップ

```bash
# 仮想環境作成（推奨）
cd python
python -m venv .venv

# 仮想環境の有効化
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt
```

**注意**: PaddleOCRの初回実行時、学習済みモデルが自動ダウンロードされます（数百MB）

### 3. 開発モード起動

```bash
# ルートディレクトリで
pnpm electron:dev
```

ブラウザが自動的に開かない場合は、手動で http://localhost:5173 にアクセスしてください。

## トラブルシューティング

### Pythonモジュールが見つからない

```bash
cd python
pip install -r requirements.txt --upgrade
```

### Electronが起動しない

```bash
# キャッシュクリア
rm -rf node_modules dist dist-electron
pnpm install
```

### PaddleOCRのGPU版を使いたい

```bash
# requirements.txtを編集
# paddlepaddle → paddlepaddle-gpu に変更
pip uninstall paddlepaddle
pip install paddlepaddle-gpu

# layout_analyzer.py でuse_gpu=Trueに設定
```

## 次のステップ

1. サンプルPDF/画像を準備
2. OCRボタンをクリックして動作確認
3. Phase 2の機能開発へ

---

**問題が発生した場合は、Issueを立ててください！**
