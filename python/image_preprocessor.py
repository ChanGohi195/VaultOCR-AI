"""
Image Preprocessor
OCR精度向上のための画像前処理

Features:
- グレースケール変換
- ノイズ除去
- 二値化（Otsu's method）
- 傾き補正
- コントラスト調整
"""

import cv2
import numpy as np
from typing import Tuple, Optional


class ImagePreprocessor:
    """画像前処理クラス"""

    def __init__(self):
        self.processed_image = None
        self.original_image = None

    def preprocess(
        self,
        image: np.ndarray,
        denoise: bool = True,
        deskew: bool = True,
        enhance_contrast: bool = True,
        binarize: bool = True
    ) -> np.ndarray:
        """
        画像の前処理を実行

        Args:
            image: 入力画像（BGR or グレースケール）
            denoise: ノイズ除去を実行するか
            deskew: 傾き補正を実行するか
            enhance_contrast: コントラスト調整を実行するか
            binarize: 二値化を実行するか

        Returns:
            前処理済み画像
        """
        self.original_image = image.copy()
        processed = image.copy()

        # グレースケール変換
        if len(processed.shape) == 3:
            processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)

        # ノイズ除去
        if denoise:
            processed = self._denoise(processed)

        # 傾き補正
        if deskew:
            processed = self._deskew(processed)

        # コントラスト調整
        if enhance_contrast:
            processed = self._enhance_contrast(processed)

        # 二値化
        if binarize:
            processed = self._binarize(processed)

        self.processed_image = processed
        return processed

    def _denoise(self, image: np.ndarray) -> np.ndarray:
        """
        ノイズ除去（Non-local Means Denoising）

        Args:
            image: グレースケール画像

        Returns:
            ノイズ除去済み画像
        """
        # fastNlMeansDenoisingを使用
        denoised = cv2.fastNlMeansDenoising(
            image,
            None,
            h=10,  # フィルタ強度
            templateWindowSize=7,
            searchWindowSize=21
        )
        return denoised

    def _deskew(self, image: np.ndarray) -> np.ndarray:
        """
        傾き補正（Hough変換による角度検出）

        Args:
            image: グレースケール画像

        Returns:
            傾き補正済み画像
        """
        # エッジ検出
        edges = cv2.Canny(image, 50, 150, apertureSize=3)

        # Hough変換で直線検出
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=100,
            minLineLength=100,
            maxLineGap=10
        )

        if lines is None or len(lines) == 0:
            return image

        # 検出された直線の角度を計算
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 - x1 == 0:  # 垂直線は無視
                continue
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            angles.append(angle)

        if not angles:
            return image

        # 中央値を取得（外れ値の影響を軽減）
        median_angle = np.median(angles)

        # 角度が小さい場合のみ補正（大きな傾きは誤検出の可能性）
        if abs(median_angle) < 5:
            # 画像を回転
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
            rotated = cv2.warpAffine(
                image,
                M,
                (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            return rotated

        return image

    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """
        コントラスト調整（CLAHE: Contrast Limited Adaptive Histogram Equalization）

        Args:
            image: グレースケール画像

        Returns:
            コントラスト調整済み画像
        """
        # CLAHEオブジェクト作成
        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )
        enhanced = clahe.apply(image)
        return enhanced

    def _binarize(self, image: np.ndarray) -> np.ndarray:
        """
        二値化（Otsu's method）

        Args:
            image: グレースケール画像

        Returns:
            二値化済み画像
        """
        # Otsuの二値化
        _, binary = cv2.threshold(
            image,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        return binary

    def get_quality_metrics(self) -> dict:
        """
        画像品質メトリクスを取得

        Returns:
            品質メトリクス
        """
        if self.processed_image is None:
            return {}

        # ブラー検出（Laplacianの分散）
        blur_score = cv2.Laplacian(self.processed_image, cv2.CV_64F).var()

        # コントラスト（標準偏差）
        contrast = np.std(self.processed_image)

        return {
            'blur_score': float(blur_score),
            'contrast': float(contrast),
            'mean_brightness': float(np.mean(self.processed_image)),
            'is_preprocessed': True
        }
