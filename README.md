# VaultOCR-AI

**Layout-aware AI OCR Engine with Obsidian-style UI**

複雑なレイアウトのPDF・画像を、人間が読む順番の段落テキストに変換し、Obsidian風UIで編集・管理できるデスクトップアプリケーション。

## 🎯 特徴

- **レイアウト認識OCR**: 多段組、サイドバー、脚注などを正しく認識
- **段落再構成**: 行テキストを自然な段落に変換
- **テーブル検出**: OpenCVによる表の自動検出・構造化
- **Obsidian風UI**: 使い慣れたMarkdownエディタ体験
- **完全無料**: PaddleOCR使用、API課金なし、100%ローカル実行
- **プライバシー保護**: インターネット不要、完全オフライン動作

## 📦 技術スタック（全て無料OSS）

- **Frontend**: React + TypeScript + Tailwind CSS
- **Desktop**: Electron (MIT)
- **Editor**: Monaco Editor (MIT)
- **OCR**: PaddleOCR (Apache 2.0)
- **画像処理**: OpenCV (Apache 2.0)
- **数値計算**: NumPy + SciPy (BSD)

## 🚀 開発ロードマップ

### Phase 1: アプリ骨格 ✅
- [x] プロジェクト構造構築
- [x] Electron + React セットアップ
- [x] Obsidian風UI実装
- [x] ファイル管理機能
- [x] Monaco Editorマークダウン編集

### Phase 2: OCR精度向上 ✅
- [x] PaddleOCR統合
- [x] 多段組レイアウト検出（1/2/3カラム）
- [x] スマート段落化（文途中改行の結合）
- [x] ハイフネーション処理（英語）
- [x] 日本語段落境界判定
- [x] OCR誤認識パターン自動補正
- [x] PDF/画像アップロード
- [x] OCR結果エディタ表示

### Phase 3: 高度機能 ✅ (完了)
- [x] ページ跨ぎ段落連結
- [x] テーブル検出・構造化（OpenCV）
- [x] 読み順最適化アルゴリズム（グラフベース）
- [x] 見出し・章節検出
- [x] Document Stitcher（複数ページ統合）
- [x] 目次（TOC）自動生成
- [x] セクション構造解析
- [x] DocumentInfo UI実装

### Phase 4: エコシステム（次）
- [ ] 全文検索（MeiliSearch/Tantivy）
- [ ] タグ管理
- [ ] Obsidian/Notionエクスポート
- [ ] ベクトル検索（sentence-transformers）
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
│   ├── components/   # UI Components
│   │   ├── DocumentInfo.tsx  # TOC/Sections
│   │   └── ...
├── python/           # Python OCR Backend
│   ├── layout_analyzer.py    # レイアウト検出
│   ├── text_refiner.py       # 段落化
│   ├── document_stitcher.py  # ページ統合
│   ├── table_detector.py     # テーブル検出
│   └── reading_order.py      # 読み順最適化
└── dist/             # ビルド出力
```

## 📝 ライセンス

MIT

## 🤝 コントリビューション

Issue・PRを歓迎します！

---

**開発状況**: Phase 3 完了 🎉🚀

## 🆕 Phase 3 新機能

### ページ跨ぎ段落連結
- 文法的完結性チェック
- 句読点・改行パターン解析
- 英語・日本語対応の統合ロジック

### テーブル検出・構造化（OpenCV）
- Hough変換による罫線検出
- セル領域の自動分割
- Markdownテーブル生成
- 完全無料（API不要）

### 読み順最適化
- グラフベースアルゴリズム（トポロジカルソート）
- 多段組対応
- ヘッダー/フッター優先度制御

### 見出し・章節検出
- 番号付き見出し（1.2.3）
- 全大文字見出し
- 日本語章節（第1章）
- 階層構造の自動解析

### Document Stitcher
- 複数ページの統合
- セクション構造構築
- 目次（TOC）自動生成

### DocumentInfo UI
- リアルタイムTOC表示
- セクション一覧
- メタデータ表示（ページ数・テーブル数）

---

## Phase 2 新機能

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
