# アーキテクチャ設計

## システム構成

```
┌─────────────────────────────────────────┐
│         Electron Main Process           │
│  - Window管理                           │
│  - IPC通信                              │
│  - Pythonプロセス管理                   │
└─────────────────────────────────────────┘
         ↓ IPC                    ↓ spawn
┌──────────────────┐      ┌──────────────────┐
│  React Frontend  │      │  Python Backend  │
│  - Obsidian UI   │      │  - PaddleOCR     │
│  - Monaco Editor │      │  - Layout分析    │
│  - Markdown      │      │  - 段落化        │
└──────────────────┘      └──────────────────┘
```

## データフロー

### OCR処理フロー

```
1. ユーザーがPDF/画像をアップロード
   ↓
2. Electron Main: ファイルパスを取得
   ↓
3. Python spawn: JSON request送信
   {"command": "ocr", "image_path": "/path/to/image.jpg"}
   ↓
4. Python OCR Server:
   - PaddleOCRで画像解析
   - レイアウト検出
   - テキスト抽出
   - 段落化
   ↓
5. JSON response返却
   {
     "status": "ok",
     "result": {
       "text": "...",
       "chunks": [...]
     }
   }
   ↓
6. React: 結果をEditorに表示
   ↓
7. ユーザーが編集・保存
```

## モジュール詳細

### Electron Layer

#### main.ts
- ウィンドウ作成・管理
- IPCハンドラー登録
- ファイルシステムアクセス
- Pythonプロセス起動

#### preload.ts
- セキュアなAPI公開
- Renderer ↔ Main間の橋渡し

### React Layer

#### App.tsx
- アプリケーション全体の状態管理
- コンポーネント間の連携

#### components/
- **Sidebar**: ファイルツリー表示
- **Editor**: Monacoエディタ統合
- **Preview**: Markdownプレビュー
- **Toolbar**: 操作ボタン群

### Python Layer

#### ocr_server.py
- stdin/stdoutでJSON通信
- リクエストルーティング
- エラーハンドリング

#### layout_analyzer.py
- PaddleOCR統合
- レイアウト検出（1/2/3カラム）
- チャンク生成

#### text_refiner.py
- 行→段落変換
- テキスト整形
- Markdown生成
- 言語検出（日本語・英語）

#### document_stitcher.py
- 複数ページ統合
- ページ跨ぎ段落検出
- セクション構造構築

#### table_detector.py
- OpenCVテーブル検出
- Hough変換罫線検出
- Markdownテーブル生成

#### reading_order.py
- グラフベース読み順最適化
- トポロジカルソート
- 多段組対応

#### search_engine.py (Phase 4)
- Whoosh全文検索
- インデックス管理
- ハイライト機能

#### document_manager.py (Phase 4)
- SQLiteデータベース
- ドキュメントCRUD
- タグ管理

#### export_manager.py (Phase 4)
- 各種フォーマットエクスポート
- Obsidian/Markdown/JSON/Notion対応

## Phase別実装計画

### Phase 1: MVP ✅ (完了)
- Electronアプリ骨格
- Obsidian風UI
- 基本OCR機能
- ファイル読み書き

### Phase 2: OCR精度向上 ✅ (完了)
- 多段組検出（1/2/3カラム）
- スマート段落化
- ハイフネーション処理
- 日本語・英語対応
- OCR誤認識自動補正
- PDF完全対応
- Electron ↔ Python IPC通信

**Phase 2 アルゴリズム詳細:**
1. **レイアウト検出**: X座標ヒストグラムでカラム境界検出
2. **段落化**: 句読点・改行パターン解析で文境界判定
3. **言語検出**: Unicode範囲でCJK文字判定
4. **誤認識補正**: 正規表現パターンマッチング

### Phase 3: 高度化 ✅ (完了)
- ページ跨ぎ処理
- テーブル検出・構造化
- 読み順最適化アルゴリズム
- 複数ページPDF一括処理
- 見出し・章節検出
- TOC自動生成

### Phase 4: エコシステム ✅ (完了)
- 全文検索（Whoosh）
- ドキュメント管理（SQLite）
- タグ管理
- Markdown/Obsidian/JSON/Notionエクスポート
- 検索インデックス自動更新

**Phase 4 アルゴリズム詳細:**

#### 1. 全文検索エンジン（search_engine.py）
- **Whoosh**: 純粋Python全文検索ライブラリ（BSD License）
- **スキーマ設計**:
  - `doc_id`: ユニークID
  - `title`: タイトル（ステミング解析）
  - `content`: 本文（ステミング解析）
  - `tags`: タグ（キーワード検索）
  - `path`: ファイルパス
  - `metadata`: JSON形式メタデータ
- **検索機能**:
  - マルチフィールド検索（タイトル・本文同時検索）
  - ハイライト機能（検索結果スニペット生成）
  - 日付範囲検索
- **インデックス管理**:
  - ドキュメント追加時に自動インデックス更新
  - 増分更新対応

#### 2. ドキュメント管理（document_manager.py）
- **SQLiteデータベース**:
  ```sql
  CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    file_path TEXT,
    content TEXT,
    created_at TIMESTAMP,
    page_count INTEGER,
    tags TEXT,  -- JSON array
    metadata TEXT  -- JSON object
  );

  CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
  );

  CREATE TABLE document_tags (
    document_id TEXT,
    tag_id INTEGER,
    FOREIGN KEY (document_id) REFERENCES documents(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
  );
  ```
- **機能**:
  - ドキュメントCRUD操作
  - タグの多対多リレーション
  - 統計情報集計（ドキュメント数、ページ数、タグ数）
  - ページネーション対応

#### 3. エクスポートマネージャ（export_manager.py）
- **Markdownエクスポート**: 標準Markdown + メタデータコメント
- **Obsidianエクスポート**:
  - YAML frontmatter（タイトル・作成日・タグ）
  - Wiki Links形式TOC
  - バックリンク対応
- **JSONエクスポート**: 構造化データ（paragraphs, sections, toc, metadata）
- **Notionエクスポート**: Notionインポート互換フォーマット

#### 4. OCR Server統合
新規APIエンドポイント:
- `{"command": "search", "query": "...", "limit": 20}` → 検索実行
- `{"command": "save_document", "title": "...", "content": "...", "tags": [...]}` → ドキュメント保存
- `{"command": "export", "format": "obsidian", "content": "...", "vault_path": "..."}` → エクスポート
- `{"command": "list_documents", "limit": 100, "offset": 0}` → ドキュメント一覧
- `{"command": "get_tags"}` → タグ一覧

## セキュリティ

- `contextIsolation: true` でRenderer隔離
- IPCで明示的にAPIを公開
- ファイルパスのバリデーション
- Pythonプロセスのサンドボックス化

## パフォーマンス最適化

- Lazy loading (Monaco, PaddleOCR)
- 仮想スクロール (大量ファイル)
- Web Workers (重い処理)
- Python非同期処理 (Phase 2+)

---

**このアーキテクチャは段階的に進化させます**
