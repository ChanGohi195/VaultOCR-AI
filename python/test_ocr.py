#!/usr/bin/env python3
"""
Test script for OCR functionality
Run this to verify Python setup is correct
"""
import json
from ocr_server import OCRServer


def test_ping():
    """Test basic server communication"""
    server = OCRServer()
    request = {'command': 'ping'}
    response = server.process_request(request)

    print("Ping test:")
    print(json.dumps(response, indent=2))
    assert response['status'] == 'ok'
    print("✓ Ping test passed\n")


def test_ocr_mock():
    """Test OCR with mock (no actual image needed)"""
    server = OCRServer()

    # This will fail gracefully since we don't have an image
    request = {
        'command': 'ocr',
        'image_path': '/nonexistent/test.jpg'
    }
    response = server.process_request(request)

    print("OCR test (expected to fail gracefully):")
    print(json.dumps(response, indent=2))
    assert response['status'] == 'error'
    print("✓ Error handling works\n")


if __name__ == '__main__':
    print("=" * 50)
    print("VaultOCR-AI Python Backend Test")
    print("=" * 50 + "\n")

    try:
        test_ping()
        test_ocr_mock()

        print("=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
        print("\nNote: To test actual OCR, you need:")
        print("1. A sample image/PDF")
        print("2. PaddleOCR models downloaded (happens on first run)")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
