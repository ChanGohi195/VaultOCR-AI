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
- レイアウト検出
- チャンク生成

#### text_refiner.py
- 行→段落変換
- テキスト整形
- Markdown生成

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

### Phase 3: 高度化（次）
- ページ跨ぎ処理
- テーブル検出・構造化
- 読み順最適化アルゴリズム
- 複数ページPDF一括処理
- Vision AI fallback（複雑レイアウト）

### Phase 4: エコシステム
- 全文検索
- タグ管理
- Obsidian/Notionエクスポート
- プラグインシステム

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
