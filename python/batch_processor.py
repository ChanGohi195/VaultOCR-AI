"""
Batch OCR Processor
複数ファイルの一括OCR処理を管理

Features:
- 複数ファイル/フォルダの一括処理
- 進捗トラッキング
- エラーハンドリング
- 結果の自動保存
"""

import os
from typing import List, Dict, Any, Callable
from pathlib import Path
import threading
import queue


class BatchProcessor:
    """バッチOCR処理マネージャー"""

    def __init__(self, ocr_handler, document_manager=None, search_engine=None):
        """
        Args:
            ocr_handler: OCRハンドラ関数
            document_manager: ドキュメント管理インスタンス（任意）
            search_engine: 検索エンジンインスタンス（任意）
        """
        self.ocr_handler = ocr_handler
        self.document_manager = document_manager
        self.search_engine = search_engine
        self.is_processing = False
        self.current_progress = 0
        self.total_files = 0

    def collect_files(self, paths: List[str], recursive: bool = False) -> List[str]:
        """
        パスリストからOCR対象ファイルを収集

        Args:
            paths: ファイル/ディレクトリパスのリスト
            recursive: サブディレクトリも含めるか

        Returns:
            OCR対象ファイルパスのリスト
        """
        supported_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        files = []

        for path_str in paths:
            path = Path(path_str)

            if path.is_file():
                if path.suffix.lower() in supported_extensions:
                    files.append(str(path))
            elif path.is_dir():
                if recursive:
                    # 再帰的にファイル収集
                    for ext in supported_extensions:
                        files.extend([str(f) for f in path.rglob(f'*{ext}')])
                else:
                    # 直下のファイルのみ
                    for ext in supported_extensions:
                        files.extend([str(f) for f in path.glob(f'*{ext}')])

        return sorted(set(files))  # 重複除去してソート

    def process_batch(
        self,
        file_paths: List[str],
        auto_save: bool = True,
        tags: List[str] = None,
        progress_callback: Callable[[int, int, str], None] = None
    ) -> Dict[str, Any]:
        """
        バッチOCR処理を実行

        Args:
            file_paths: 処理するファイルパスのリスト
            auto_save: 処理結果を自動保存するか
            tags: 保存時に付与するタグ
            progress_callback: 進捗コールバック(current, total, filename)

        Returns:
            処理結果サマリー
        """
        self.is_processing = True
        self.current_progress = 0
        self.total_files = len(file_paths)

        results = {
            'total': self.total_files,
            'success': 0,
            'failed': 0,
            'files': []
        }

        for i, file_path in enumerate(file_paths):
            self.current_progress = i + 1
            filename = os.path.basename(file_path)

            # 進捗コールバック
            if progress_callback:
                progress_callback(self.current_progress, self.total_files, filename)

            try:
                # OCR処理実行
                ocr_result = self.ocr_handler(file_path)

                file_result = {
                    'path': file_path,
                    'filename': filename,
                    'status': 'success',
                    'metadata': ocr_result.get('metadata', {}),
                    'doc_id': None
                }

                # 自動保存
                if auto_save and self.document_manager:
                    try:
                        # タイトルをファイル名から生成
                        title = Path(filename).stem

                        # ドキュメント保存
                        doc_id = self.document_manager.add_document(
                            title=title,
                            content=ocr_result.get('text', ''),
                            file_path=file_path,
                            tags=tags or [],
                            metadata=ocr_result.get('metadata', {}),
                            page_count=ocr_result.get('metadata', {}).get('page_count', 1)
                        )

                        file_result['doc_id'] = doc_id

                        # 検索インデックスに追加
                        if self.search_engine:
                            self.search_engine.add_document(
                                doc_id=doc_id,
                                title=title,
                                content=ocr_result.get('text', ''),
                                tags=tags or [],
                                path=file_path,
                                metadata=ocr_result.get('metadata', {})
                            )
                    except Exception as save_error:
                        file_result['save_error'] = str(save_error)

                results['success'] += 1
                results['files'].append(file_result)

            except Exception as e:
                results['failed'] += 1
                results['files'].append({
                    'path': file_path,
                    'filename': filename,
                    'status': 'failed',
                    'error': str(e)
                })

        self.is_processing = False
        return results

    def get_progress(self) -> Dict[str, Any]:
        """
        現在の処理進捗を取得

        Returns:
            進捗情報
        """
        return {
            'is_processing': self.is_processing,
            'current': self.current_progress,
            'total': self.total_files,
            'percentage': int((self.current_progress / self.total_files * 100) if self.total_files > 0 else 0)
        }
