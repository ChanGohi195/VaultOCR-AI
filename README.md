# VaultOCR-AI

**Layout-aware AI OCR Engine with Obsidian-style UI**

複雑なレイアウトのPDF・画像を、人間が読む順番の段落テキストに変換し、Obsidian風UIで編集・管理できるデスクトップアプリケーション。

## 🎯 特徴

- **レイアウト認識OCR**: 多段組、サイドバー、脚注などを正しく認識
- **多言語対応**: 20言語OCR + 自動言語検出
- **段落再構成**: 行テキストを自然な段落に変換
- **テーブル検出**: OpenCVによる表の自動検出・構造化
- **AI検索**:
  - **セマンティック検索**: 意味ベースの賢い検索（50言語対応）
  - **ハイブリッド検索**: キーワード + AIの融合
  - **類似文書発見**: 1文書から関連文書を自動推薦
- **AI機能**:
  - **AI要約**: 45言語対応の自動要約（mT5/BART）
  - **自動翻訳**: 20言語ペア対応翻訳（Helsinki-NLP Opus）
  - **テンプレート抽出**: 領収書・名刺・契約書・請求書の自動構造化
- **バッチ処理**: 複数ファイル一括OCR処理
- **Searchable PDF**: OCR結果から検索可能PDF生成
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
- **検索エンジン**:
  - Whoosh (BSD) - キーワード検索
  - sentence-transformers (Apache 2.0) - セマンティック検索
  - FAISS (MIT) - 高速ベクトル検索
- **AI機能**:
  - transformers (Apache 2.0) - 要約・翻訳
  - PyTorch (BSD) - 機械学習フレームワーク
- **PDF生成**: reportlab (BSD) - Searchable PDF生成
- **言語検出**: langdetect (Apache 2.0)
- **データベース**: SQLite (内蔵) - ドキュメント管理

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

### Phase 4: エコシステム ✅ (完了)
- [x] 全文検索（Whoosh - 純粋Python）
- [x] ドキュメント管理（SQLite）
- [x] タグ管理システム
- [x] Markdown/Obsidian/JSON/Notionエクスポート
- [x] 検索インデックス自動更新
- [x] ドキュメント統計情報

### Phase 5: 実用機能 ✅ (完了)
- [x] バッチOCR処理（複数ファイル一括処理）
- [x] OCR結果自動保存
- [x] ドキュメント取得API
- [x] 進捗表示UI
- [x] バッチ処理統計情報

### Phase 6: UX改善・OCR品質向上 ✅ (完了)
- [x] キーボードショートカット（Cmd/Ctrl + S/K/B/E/P/D）
- [x] ドラッグ&ドロップ対応（PDF・画像の直接投入）
- [x] 画像前処理パイプライン（デノイズ・傾き補正・コントラスト強化・二値化）
- [x] OCR信頼度表示（品質メトリクス可視化）
- [x] デスクトップショートカット（インストール時自動作成）
- [x] ビルド設定最適化（electron-builder完全対応）

### Phase 7: 多言語OCR対応 ✅ (完了)
- [x] 自動言語検出（langdetect）
- [x] 多言語OCR実行（日本語・英語・中国語・韓国語・フランス語・ドイツ語・スペイン語等20言語対応）
- [x] 混在言語対応（1文書内で複数言語検出・分離）
- [x] UI: 言語選択ドロップダウン
- [x] 言語別信頼度表示（検出言語・混在言語可視化）
- [x] PaddleOCR多言語モデル統合

### Phase 8: ベクトル検索・セマンティック検索 ✅ (完了)
- [x] ベクトル検索エンジン実装（sentence-transformers + FAISS）
- [x] セマンティック検索（意味ベース検索・50言語対応）
- [x] ハイブリッド検索（キーワード + ベクトル融合）
- [x] 類似文書検索（ドキュメント間類似度）
- [x] UI: 検索モード切り替え（Keyword/Semantic/Hybrid）
- [x] FAISSインデックス永続化

### Phase 9: AI機能・PDF生成 ✅ (完了)
- [x] AI要約エンジン（mT5/BART - 45言語対応）
- [x] 自動翻訳（Helsinki-NLP Opus - 20言語ペア）
- [x] カスタムテンプレート抽出（領収書・名刺・契約書・請求書・汎用フォーム）
- [x] Searchable PDF生成（OCR結果からテキスト埋め込みPDF作成）
- [x] テンプレート自動検出（文書種別AI判定）
- [x] API統合（summarize/translate/extractTemplate/generateSearchablePDF）

### Phase 10: プラグインシステム ✅ (完了)
- [x] プラグインインターフェース定義（5種類のプラグインタイプ）
- [x] プラグインマネージャー（動的ロード・設定・実行）
- [x] 組み込みプラグイン実装:
  - [x] 超解像度化プラグイン（AI画像アップスケール）
  - [x] 適応的二値化プラグイン（不均一照明対応）
  - [x] スペル補正プラグイン（OCR誤認識修正）
- [x] プラグインAPI統合（list/configure/enable/disable）
- [x] プラグイン開発ドキュメント（PLUGIN_DEV.md）

### Phase 11: 次世代拡張（次）
- [ ] Webアプリ版（ブラウザで動作）
- [ ] クラウド同期（オプション）
- [ ] OCR精度向上（カスタムモデル学習）
- [ ] リアルタイムコラボレーション

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
│   ├── ocr_server.py            # メインサーバー
│   ├── layout_analyzer.py       # レイアウト検出
│   ├── text_refiner.py          # 段落化
│   ├── document_stitcher.py     # ページ統合
│   ├── table_detector.py        # テーブル検出
│   ├── reading_order.py         # 読み順最適化
│   ├── search_engine.py         # 全文検索（Whoosh）
│   ├── document_manager.py      # ドキュメント管理
│   ├── export_manager.py        # エクスポート機能
│   ├── batch_processor.py       # バッチ処理（Phase 5）
│   ├── language_detector.py     # 言語検出（Phase 7）
│   ├── vector_search.py         # ベクトル検索（Phase 8）
│   ├── summarization_engine.py  # AI要約（Phase 9）
│   ├── translation_engine.py    # 翻訳（Phase 9）
│   ├── template_engine.py       # テンプレート抽出（Phase 9）
│   ├── pdf_generator.py         # Searchable PDF生成（Phase 9）
│   ├── plugin_interface.py      # プラグインAPI（Phase 10）
│   ├── plugin_manager.py        # プラグインマネージャー（Phase 10）
│   └── plugins/                 # プラグインディレクトリ（Phase 10）
│       ├── super_resolution_plugin.py
│       ├── adaptive_binarization_plugin.py
│       └── spell_correction_plugin.py
└── dist/             # ビルド出力
```

## 📝 ライセンス

MIT

## 🤝 コントリビューション

Issue・PRを歓迎します！

---

**開発状況**: Phase 10 完了 🎉🚀

## 🆕 Phase 10 新機能

### プラグインシステム - 無限の拡張性

#### 1. プラグインアーキテクチャ
- **5種類のプラグインタイプ**:
  1. **Preprocessor**: 画像前処理（OCR前の画像強化）
  2. **OCR Engine**: カスタムOCRエンジン統合
  3. **Postprocessor**: テキスト後処理（スペル補正等）
  4. **Exporter**: カスタムエクスポート形式
  5. **Analyzer**: 独自分析・抽出ロジック

#### 2. プラグインマネージャー
- **動的ロード**: 実行時にプラグインを発見・ロード
- **優先度制御**: プラグイン実行順序を制御（HIGHEST → LOWEST）
- **設定管理**: JSON設定スキーマで自動バリデーション
- **パイプライン実行**: 複数プラグインを連鎖実行

#### 3. 組み込みプラグイン
**SuperResolutionPlugin** - AI画像超解像度化
- 低解像度スキャンを2-4倍にアップスケール
- Bicubic補間 + シャープニング
- 最小/最大解像度の自動判定

**AdaptiveBinarizationPlugin** - 適応的二値化
- 4種類の二値化アルゴリズム:
  - Adaptive Gaussian （デフォルト）
  - Adaptive Mean
  - Otsu
  - Sauvola
- 不均一な照明条件に対応
- デノイジング統合

**SpellCorrectionPlugin** - OCRスペル補正
- 一般的なOCR誤認識パターンの自動修正
- 複数言語対応（英語・日本語等）
- カスタム置換辞書対応
- 大文字小文字保持

#### 4. プラグイン開発
```python
from plugin_interface import PreprocessorPlugin

class MyPlugin(PreprocessorPlugin):
    @property
    def name(self) -> str:
        return "my_plugin"

    def process_image(self, image, context):
        # カスタム処理
        return processed_image
```

詳細は [PLUGIN_DEV.md](PLUGIN_DEV.md) を参照

#### 5. プラグインAPI
```python
# プラグイン一覧
pm.list_plugins(plugin_type='preprocessor', enabled_only=True)

# プラグイン設定
pm.configure_plugin('super_resolution', {'scale_factor': 3})

# プラグイン有効化/無効化
pm.enable_plugin('spell_correction')
pm.disable_plugin('adaptive_binarization')

# パイプライン実行
result = pm.execute_pipeline(PluginType.PREPROCESSOR, image, context)
```

#### 拡張性の未来
プラグインシステムにより、ユーザーは以下を自由に追加可能：
- Google Cloud Vision API統合
- Amazon Textract統合
- カスタムMLモデル
- 業界固有のテンプレート抽出
- エンタープライズエクスポート形式

---

## 🆕 Phase 9 新機能

### AI要約・翻訳・テンプレート抽出・Searchable PDF

#### 1. AI要約エンジン
- **多言語対応要約**: 45言語対応（mT5-multilingual）
- **英語専用高精度要約**: facebook/bart-large-cnn
- **日本語専用要約**: sonoisa/t5-base-japanese
- **圧縮率指定**: ratio パラメータで要約率を制御
- **セクション別要約**: 文書の各セクションを個別に要約
- **自動長さ調整**: 入力テキスト量に応じた最適な要約長

#### 2. 自動翻訳エンジン
- **20言語ペア対応**: Helsinki-NLP Opus-MT モデル
- **主要言語ペア**:
  - 日本語 ⇔ 英語
  - 中国語 ⇔ 英語
  - 韓国語 ⇔ 英語
  - フランス語・ドイツ語・スペイン語・ロシア語・アラビア語等 ⇔ 英語
- **バッチ翻訳**: 複数テキストの一括翻訳
- **セクション別翻訳**: 文書構造を保持した翻訳

#### 3. カスタムテンプレート抽出
- **5種類の組み込みテンプレート**:
  1. **領収書**: 店名・日付・合計・小計・税・支払方法・明細抽出
  2. **名刺**: 氏名・会社・役職・電話・メール・住所・Web抽出
  3. **契約書**: 契約名・当事者・有効期限・重要条項・署名抽出
  4. **請求書**: 請求番号・請求先・支払期限・明細・金額抽出
  5. **汎用フォーム**: ラベル-値ペアの自動抽出
- **自動文書種別判定**: テキストから文書タイプを自動検出
- **正規表現ベース抽出**: 柔軟なパターンマッチング

#### 4. Searchable PDF生成
- **OCR結果からPDF作成**: 画像+テキストレイヤー埋め込み
- **完全検索可能**: PDFビューアで全文検索可能
- **テキストのみPDF**: マークダウンテキストから通常PDF生成
- **メタデータ埋め込み**: タイトル・著者・キーワード等
- **PDF結合**: 複数PDFの統合機能

#### API統合
```python
# 要約API
electronAPI.summarize(text, { language: 'ja', ratio: 0.3 })

# 翻訳API
electronAPI.translate(text, 'ja', 'en')

# テンプレート抽出API
electronAPI.extractTemplate(text, 'receipt')

# Searchable PDF生成API
electronAPI.generateSearchablePDF({
  mode: 'text',
  text: content,
  outputPath: '/path/to/output.pdf',
  metadata: { title: 'Document', author: 'User' }
})
```

---

## 🆕 Phase 8 新機能

### ベクトル検索・セマンティック検索
- **ベクトル検索エンジン**: sentence-transformers + FAISS統合
  - 768次元ベクトル埋め込み
  - コサイン類似度ベース検索
  - FAISSインデックス永続化（自動保存・読み込み）
- **セマンティック検索**: AIによる意味ベース検索
  - `paraphrase-multilingual-mpnet-base-v2` モデル採用
  - 50言語以上対応
  - クロスリンガル検索（日本語クエリ→英語文書も発見）
  - 例：「契約書」で「Agreement」「Contract」も検索
- **ハイブリッド検索**: キーワード + ベクトル融合
  - キーワード検索とセマンティック検索の重み付け統合
  - スコア分解表示（K: 50 S: 45）
  - 最適なバランスで高精度検索
- **類似文書検索**: ドキュメント間類似度計算
  - 1つの文書から関連文書を自動発見
  - 類似度スコア付き推薦
- **検索モードUI**: SearchBarに3モード切り替え実装
  - **Keyword**: 従来のキーワード検索（Whoosh）
  - **Semantic**: AI意味ベース検索（sentence-transformers）
  - **Hybrid**: 両方の長所を組み合わせ（デフォルト）
- **自動インデックス**: 文書保存時に自動ベクトル化

---

## 🆕 Phase 7 新機能

### 多言語OCR対応
- **自動言語検出**: langdetectによる100言語対応
  - ヒューリスティックフォールバック（langdetect未インストール時）
  - 日本語・韓国語・中国語・アラビア語・キリル文字等の自動判別
  - 信頼度スコア付き
- **20言語対応OCR**: PaddleOCR多言語モデル統合
  - 🇯🇵 日本語, 🇬🇧 英語, 🇨🇳 中国語簡体字/繁体字
  - 🇰🇷 韓国語, 🇫🇷 フランス語, 🇩🇪 ドイツ語, 🇪🇸 スペイン語
  - 🇷🇺 ロシア語, 🇦🇪 アラビア語, 🇮🇳 ヒンディー語
  - 🇵🇹 ポルトガル語, 🇮🇹 イタリア語, 🇳🇱 オランダ語
  - 🇵🇱 ポーランド語, 🇹🇷 トルコ語, 🇻🇳 ベトナム語
  - 🇹🇭 タイ語, 🇮🇩 インドネシア語, 🇸🇪 スウェーデン語
- **言語選択UI**: Toolbarに言語ドロップダウン追加
  - Auto Detect モード（デフォルト）
  - 手動言語選択（20言語から選択）
  - 選択した言語でOCR実行
- **混在言語検出**: 1文書内で複数言語を自動検出
  - ドキュメント全体の言語分布解析
  - 行ごとの言語検出（混在度15%以上で有効化）
  - パーセンテージ・文字数統計
- **言語情報表示**: DocumentInfoパネルに追加
  - 検出言語表示（ISO 639-1コード）
  - 言語検出信頼度プログレスバー
  - 混在言語可視化（言語別比率）

---

## 🆕 Phase 6 新機能

### UX改善
- **キーボードショートカット**: 6つのショートカット実装
  - `Cmd/Ctrl + S`: ファイル保存
  - `Cmd/Ctrl + K`: 検索フォーカス
  - `Cmd/Ctrl + B`: バッチ処理ダイアログ
  - `Cmd/Ctrl + E`: エクスポートダイアログ
  - `Cmd/Ctrl + P`: プレビュー切り替え
  - `Cmd/Ctrl + D`: サイドバーモード切り替え
- **ドラッグ&ドロップ**: PDF・画像ファイルの直接投入
  - 単一ファイル: 即座にOCR実行
  - 複数ファイル: バッチ処理ダイアログ表示
  - 視覚的フィードバック付き

### OCR品質向上
- **画像前処理パイプライン**: OpenCVベースの5段階処理
  - グレースケール変換
  - Non-local Means デノイジング
  - Hough変換による傾き補正
  - CLAHE コントラスト強化
  - Otsu二値化
- **OCR信頼度表示**: 品質メトリクス可視化
  - 平均信頼度スコア
  - 最小/最大信頼度
  - 低信頼度テキスト比率
  - カラーコード付きプログレスバー

### インストール最適化
- **デスクトップショートカット**: インストール時自動作成
  - Windows: NSIS インストーラー + デスクトップ/スタートメニュー
  - macOS: DMG パッケージ
  - Linux: .desktop ファイル + AppImage/deb/rpm対応
- **クロスプラットフォームビルド**: electron-builder完全対応

---

## 🆕 Phase 5 新機能

### バッチOCR処理
- **複数ファイル一括処理**: PDF・画像を一度に処理
- **自動保存**: OCR結果を自動的にデータベース保存
- **進捗トラッキング**: リアルタイム処理状況表示
- **エラーハンドリング**: ファイル単位のエラー管理
- **統計情報**: 成功/失敗件数の即時フィードバック

### ドキュメント取得機能
- **保存済みドキュメントロード**: データベースから即座に読み込み
- **シームレスな編集**: ドキュメント一覧から選択して即編集

### バッチ処理UI
- **ファイル管理**: 複数ファイル選択・削除
- **タグ一括設定**: バッチ処理時の自動タグ付け
- **進捗バー**: 視覚的な処理状況表示
- **ステータス表示**: 各ファイルの処理結果

### OCR Server API拡張
- `get_document`: ドキュメント取得
- `batch_ocr`: バッチOCR処理実行

---

## 🆕 Phase 4 新機能

### 全文検索エンジン（Whoosh）
- 純粋Python実装、完全無料
- マルチフィールド検索（タイトル・内容・タグ）
- ハイライト機能付き検索結果
- 自動インデックス更新

### ドキュメント管理（SQLite）
- ドキュメントメタデータ保存
- タグシステム（多対多リレーション）
- 統計情報自動集計
- 完全オフライン動作

### エクスポート機能
- **Markdown**: 標準フォーマット
- **Obsidian**: フロントマター + Wiki Links対応
- **JSON**: 構造化データ保存
- **Notion**: Notionフォーマット互換

### OCR Server API拡張
- `search`: 全文検索クエリ実行
- `save_document`: ドキュメント保存＋自動インデックス
- `export`: 各種フォーマットエクスポート
- `list_documents`: ドキュメント一覧取得
- `get_tags`: タグ一覧取得

---

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
