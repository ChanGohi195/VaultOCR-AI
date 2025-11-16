# Contributing to VaultOCR-AI

VaultOCR-AIへのコントリビューションを歓迎します！

## 開発の流れ

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Requestを作成

## コーディング規約

### TypeScript/React
- ESLintルールに従う
- コンポーネントは関数コンポーネントで
- Tailwind CSSを使用

### Python
- PEP 8に従う
- 型ヒントを使用
- docstringを書く

## テスト

```bash
# Pythonバックエンド
cd python
python test_ocr.py

# フロントエンド（Phase 2以降）
pnpm test
```

## コミットメッセージ

わかりやすいコミットメッセージを心がけてください：

- `feat:` 新機能
- `fix:` バグ修正
- `docs:` ドキュメント
- `refactor:` リファクタリング
- `test:` テスト追加

例: `feat: Add multi-column layout detection`

## 質問・相談

Issueで気軽に質問してください！

---

**Thank you for contributing! 🎉**
