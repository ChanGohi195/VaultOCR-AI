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

### Phase 1: アプリ骨格（現在）
- [x] プロジェクト構造構築
- [ ] Electron + React セットアップ
- [ ] Obsidian風UI実装
- [ ] ファイル管理機能

### Phase 2: OCR統合
- [ ] PaddleOCR統合
- [ ] PDF/画像アップロード
- [ ] OCR結果表示・編集

### Phase 3: OCR精度向上
- [ ] 段落化ロジック
- [ ] レイアウト認識改善
- [ ] 日本語対応強化

### Phase 4: 高度機能
- [ ] 全文検索
- [ ] タグ管理
- [ ] Obsidian/Notionエクスポート
- [ ] ベクトル検索（オプション）

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

**開発状況**: Phase 1 実装中
