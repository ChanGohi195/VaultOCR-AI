# VaultOCR-AI

**Layout-aware AI OCR Engine with Obsidian-style UI**

複雑なレイアウトのPDF・画像を、人間が読む順番の段落テキストに変換し、Obsidian風UIで編集・管理できるデスクトップアプリケーション。

## 🎯 特徴

- **レイアウト認識OCR**: 多段組、サイドバー、脚注などを正しく認識
- **段落再構成**: 行テキストを自然な段落に変換
- **Obsidian風UI**: 使い慣れたMarkdownエディタ体験
- **完全無料**: PaddleOCR使用、API課金なし
- **ローカル完結**: プライバシー保護

## 📦 技術スタック

- **Frontend**: React + TypeScript + Tailwind CSS
- **Desktop**: Electron
- **Editor**: Monaco Editor (VS Code engine)
- **OCR**: PaddleOCR (Python)

## 🚀 開発ロードマップ

### Phase 1: アプリ骨格 ✅
- [x] プロジェクト構造構築
- [x] Electron + React セットアップ
- [x] Obsidian風UI実装
- [x] ファイル管理機能
- [x] Monaco Editorマークダウン編集

### Phase 2: OCR精度向上 ✅ (完了)
- [x] PaddleOCR統合
- [x] 多段組レイアウト検出（1/2/3カラム）
- [x] スマート段落化（文途中改行の結合）
- [x] ハイフネーション処理（英語）
- [x] 日本語段落境界判定
- [x] OCR誤認識パターン自動補正
- [x] PDF/画像アップロード
- [x] OCR結果エディタ表示

### Phase 3: 高度機能（次）
- [ ] ページ跨ぎ段落連結
- [ ] テーブル検出・構造化
- [ ] 読み順最適化アルゴリズム
- [ ] 複数ページPDF一括処理

### Phase 4: エコシステム
- [ ] 全文検索（MeiliSearch/Tantivy）
- [ ] タグ管理
- [ ] Obsidian/Notionエクスポート
- [ ] ベクトル検索（オプション）
- [ ] プラグインシステム

## 🛠️ セットアップ

### 必要環境

- Node.js 18+
- Python 3.8+
- pnpm (推奨) or npm

### インストール

```bash
# フロントエンド
pnpm install

# Pythonバックエンド
cd python
pip install -r requirements.txt
```

### 開発モード

```bash
pnpm electron:dev
```

### ビルド

```bash
pnpm electron:build
```

## 📁 プロジェクト構造

```
VaultOCR-AI/
├── electron/          # Electron Main Process
├── src/              # React Frontend
├── python/           # Python OCR Backend
└── dist/             # ビルド出力
```

## 📝 ライセンス

MIT

## 🤝 コントリビューション

Issue・PRを歓迎します！

---

**開発状況**: Phase 2 完了 🎉

## 🆕 Phase 2 新機能

### 多段組レイアウト検出
- 1カラム / 2カラム / 3カラム 自動判定
- ヘッダー・フッター分離
- 読み順最適化

### スマート段落化
- 文途中改行の自動結合
- ハイフネーション処理（英語）
- 日本語・英語自動検出
- 段落境界インテリジェント判定

### OCR誤認識補正
- 0/O, 1/l, rn/m などの自動補正
- 文脈ベースの補正パターン

### PDF完全対応
- 複数ページPDF処理
- ページ単位・全ページ一括選択
- pdf2image統合
