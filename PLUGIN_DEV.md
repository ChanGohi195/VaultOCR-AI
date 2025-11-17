# VaultOCR-AI Plugin Development Guide

**Phase 10: Plugin System for Extensibility**

プラグインシステムにより、VaultOCR-AIの機能をPythonコードで自由に拡張できます。

## 📦 プラグインタイプ

### 1. PreprocessorPlugin (前処理)
画像をOCR処理前に加工します。

**用途:**
- 画像の超解像度化
- ノイズ除去
- 適応的二値化
- 傾き補正
- コントラスト強化

**入力:** PIL Image または numpy array
**出力:** 処理済み画像

### 2. OCREnginePlugin (OCRエンジン)
カスタムOCRエンジンを統合します。

**用途:**
- Google Cloud Vision API統合
- Amazon Textract統合
- カスタムMLモデル

**入力:** PIL Image または numpy array
**出力:** OCR結果 (text, boxes, confidence)

### 3. PostprocessorPlugin (後処理)
OCR抽出テキストを加工します。

**用途:**
- スペル補正
- 文法修正
- フォーマット整形
- 言語固有の補正

**入力:** OCRテキスト (string)
**出力:** 処理済みテキスト (string)

### 4. ExporterPlugin (エクスポート)
カスタムエクスポート形式を追加します。

**用途:**
- DOCX出力
- LaTeX出力
- カスタムJSON形式

**入力:** ドキュメントデータ
**出力:** エクスポートファイル

### 5. AnalyzerPlugin (分析)
カスタム分析・抽出を実行します。

**用途:**
- キーワード抽出
- センチメント分析
- エンティティ認識

**入力:** テキストまたはドキュメント
**出力:** 分析結果

## 🛠️ プラグイン作成方法

### ステップ1: プラグインクラスを作成

```python
from plugin_interface import PreprocessorPlugin, PluginPriority
from typing import Dict, Any
import numpy as np
from PIL import Image

class MyCustomPlugin(PreprocessorPlugin):
    """カスタムプラグインの説明"""

    @property
    def name(self) -> str:
        return "my_custom_plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "カスタムプラグインの詳細説明"

    @property
    def author(self) -> str:
        return "あなたの名前"

    @property
    def priority(self) -> PluginPriority:
        return PluginPriority.NORMAL  # LOWEST, LOW, NORMAL, HIGH, HIGHEST

    @property
    def dependencies(self) -> list:
        return ['opencv-python>=4.8.0']  # 必要なPythonパッケージ

    @property
    def config_schema(self) -> Dict[str, Any]:
        """設定スキーマ定義"""
        return {
            'threshold': {
                'type': 'int',
                'default': 127,
                'description': '二値化の閾値',
                'required': False
            },
            'enable_denoise': {
                'type': 'bool',
                'default': True,
                'description': 'ノイズ除去を有効化',
                'required': False
            }
        }

    def process_image(self, image: Any, context: Dict[str, Any]) -> Any:
        """画像処理のメインロジック"""
        # 設定を取得
        threshold = self._config.get('threshold', 127)
        enable_denoise = self._config.get('enable_denoise', True)

        # PIL ImageをNumPy配列に変換
        if isinstance(image, Image.Image):
            img_array = np.array(image)
            is_pil = True
        else:
            img_array = image
            is_pil = False

        # カスタム処理を実行
        processed = self._custom_processing(img_array, threshold)

        # PIL Imageに戻す（必要な場合）
        if is_pil:
            return Image.fromarray(processed)
        else:
            return processed

    def _custom_processing(self, image, threshold):
        """カスタム処理ロジック"""
        # ここに独自の画像処理を実装
        return image
```

### ステップ2: プラグインファイルを配置

```bash
# プラグインを配置
cp my_custom_plugin.py python/plugins/
```

### ステップ3: アプリケーションを再起動

プラグインは起動時に自動的にロードされます。

## 📚 組み込みプラグイン例

### 1. SuperResolutionPlugin
**ファイル:** `python/plugins/super_resolution_plugin.py`
**機能:** AI超解像度化で低解像度画像を2-4倍にアップスケール

**設定:**
```json
{
  "scale_factor": 2,
  "min_resolution": 300,
  "max_resolution": 4000
}
```

### 2. AdaptiveBinarizationPlugin
**ファイル:** `python/plugins/adaptive_binarization_plugin.py`
**機能:** 適応的二値化で不均一な照明条件に対応

**設定:**
```json
{
  "method": "adaptive_gaussian",
  "block_size": 11,
  "c_value": 2,
  "denoise_first": true
}
```

### 3. SpellCorrectionPlugin
**ファイル:** `python/plugins/spell_correction_plugin.py`
**機能:** OCR誤認識の自動スペル補正

**設定:**
```json
{
  "language": "en",
  "aggressive": false,
  "preserve_case": true,
  "custom_replacements": {
    "teh": "the"
  }
}
```

## 🔧 プラグインAPI使用方法

### Python API

```python
from plugin_manager import PluginManager
from plugin_interface import PluginType

# プラグインマネージャー初期化
pm = PluginManager()

# プラグインをロード
pm.load_plugin_from_file('path/to/my_plugin.py')

# プラグインを設定
pm.configure_plugin('my_custom_plugin', {
    'threshold': 150,
    'enable_denoise': True
})

# プラグインを有効化/無効化
pm.enable_plugin('my_custom_plugin')
pm.disable_plugin('my_custom_plugin')

# プラグインパイプラインを実行
from PIL import Image
image = Image.open('test.png')
processed = pm.execute_pipeline(
    PluginType.PREPROCESSOR,
    image,
    context={}
)
```

### Electron API

```typescript
// プラグイン一覧取得
const response = await window.electronAPI.listPlugins('preprocessor', true)
console.log(response.result.plugins)

// プラグイン詳細取得
const info = await window.electronAPI.getPluginInfo('super_resolution')
console.log(info.result.plugin)

// プラグイン設定
await window.electronAPI.configurePlugin('super_resolution', {
  scale_factor: 3,
  min_resolution: 200
})

// プラグイン有効化/無効化
await window.electronAPI.enablePlugin('super_resolution')
await window.electronAPI.disablePlugin('spell_correction')
```

## 📋 ベストプラクティス

### 1. エラーハンドリング
```python
def process_image(self, image, context):
    try:
        # 処理ロジック
        return processed_image
    except Exception as e:
        # エラー時は元の画像を返す
        logger.error(f"Processing failed: {e}")
        return image
```

### 2. 設定のバリデーション
設定スキーマを正しく定義すると、自動的にバリデーションされます。

### 3. パフォーマンス
- 重い処理は遅延初期化（lazy loading）
- 不要なメモリコピーを避ける
- NumPy配列を直接操作

### 4. ドキュメント
- プラグインの説明を明確に
- 設定パラメータに説明を追加
- サンプルコードを提供

## 🧪 プラグインテスト

```python
import unittest
from my_custom_plugin import MyCustomPlugin
from PIL import Image
import numpy as np

class TestMyCustomPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = MyCustomPlugin()
        self.plugin.configure({'threshold': 128})

    def test_process_image(self):
        # テスト画像作成
        test_image = Image.new('RGB', (100, 100), color='white')

        # プラグイン実行
        result = self.plugin.process_image(test_image, {})

        # 検証
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (100, 100))

if __name__ == '__main__':
    unittest.main()
```

## 🚀 高度な機能

### プラグインパイプライン

複数のプラグインは優先度順に実行されます：

```
Image → [HIGH] SuperResolution
      → [NORMAL] AdaptiveBinarization
      → [LOW] NoiseReduction
      → OCR Engine
```

### コンテキスト共有

プラグイン間でデータを共有できます：

```python
def process_image(self, image, context):
    # 前のプラグインの結果を取得
    prev_results = context.get('plugin_results', {})

    # 自分の結果を保存
    context['my_plugin_data'] = {'processed': True}

    return processed_image
```

### 動的設定更新

実行時に設定を変更できます：

```python
pm.configure_plugin('my_plugin', {'threshold': 200})
```

## 📦 プラグイン配布

### プラグインパッケージング

```bash
# ディレクトリ構造
my-plugin-package/
├── my_plugin.py
├── requirements.txt
├── README.md
└── examples/
    └── sample_config.json
```

### requirements.txt
```
opencv-python>=4.8.0
numpy>=1.24.0
pillow>=10.0.0
```

## 🔒 セキュリティ

- プラグインは信頼できるソースからのみインストール
- コード review before deployment
- サンドボックス実行（将来の実装）

## 🐛 トラブルシューティング

### プラグインがロードされない
1. ファイル名が`_`で始まっていないか確認
2. `BasePlugin`を継承しているか確認
3. 必要なメソッドが実装されているか確認

### 設定エラー
1. `config_schema`が正しく定義されているか確認
2. 型が一致しているか確認

### パフォーマンス問題
1. 不要な画像コピーを削減
2. NumPy配列で直接操作
3. プロファイリングツールを使用

## 📞 サポート

質問やバグ報告は GitHub Issues へ:
https://github.com/YOUR_REPO/VaultOCR-AI/issues

---

**Happy Plugin Development!** 🎉
