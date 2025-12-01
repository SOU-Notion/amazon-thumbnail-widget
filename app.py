#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazonサムネイル取得APIサーバー
Notionウィジェット用のバックエンドAPI
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os

# amazon_thumbnail_fetcherをインポート（同じディレクトリまたは親ディレクトリから）
try:
    # 同じディレクトリからインポートを試みる
    from amazon_thumbnail_fetcher import AmazonThumbnailFetcher
except ImportError:
    # 親ディレクトリからインポートを試みる
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from amazon_thumbnail_fetcher import AmazonThumbnailFetcher

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # CORSを有効化（Notionウィジェットからアクセス可能にする）

# Amazonサムネイル取得クラスのインスタンス
thumbnail_fetcher = AmazonThumbnailFetcher()


@app.route('/api/get-thumbnail', methods=['POST'])
def get_thumbnail():
    """サムネイル画像URLを取得するAPIエンドポイント（複数候補対応）"""
    try:
        data = request.get_json()
        print(f"受信したリクエスト: {data}")
        
        title = data.get('title')
        isbn = data.get('isbn')
        max_results = data.get('max_results', 5)  # デフォルトで5件
        
        if not title and not isbn:
            return jsonify({
                'error': 'タイトルまたはISBNが必要です'
            }), 400
        
        # ISBNの場合は1件のみ、タイトルの場合は複数候補を返す
        if isbn:
            print(f"ISBNで検索: {isbn}")
            # ISBNの場合は1件のみ
            thumbnail_url = thumbnail_fetcher.get_thumbnail(
                title=None,
                isbn=isbn
            )
            if thumbnail_url:
                result = {
                    'candidates': [{
                        'thumbnail_url': thumbnail_url,
                        'title': f'ISBN: {isbn}',
                        'url': None,
                        'asin': None
                    }]
                }
                print(f"ISBN検索結果: {result}")
                return jsonify(result)
            else:
                print(f"ISBN検索: 見つかりませんでした")
                return jsonify({
                    'error': 'サムネイル画像が見つかりませんでした'
                }), 404
        else:
            print(f"タイトルで検索: {title}, max_results: {max_results}")
            # タイトルの場合は複数候補を返す
            candidates = thumbnail_fetcher.get_thumbnails_by_title(title, max_results=max_results)
            print(f"タイトル検索結果: {len(candidates)}件見つかりました")
            
            if candidates:
                result = {
                    'candidates': candidates
                }
                print(f"返すデータ: {result}")
                return jsonify(result)
            else:
                print(f"タイトル検索: 見つかりませんでした")
                return jsonify({
                    'error': 'サムネイル画像が見つかりませんでした'
                }), 404
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"エラー発生: {str(e)}")
        print(f"トレースバック: {error_trace}")
        return jsonify({
            'error': f'エラーが発生しました: {str(e)}'
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """ヘルスチェックエンドポイント"""
    return jsonify({'status': 'ok'})

@app.route('/')
def index():
    """フロントエンドのHTMLを返す"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """静的ファイル（CSS、JS）を配信"""
    return send_from_directory('.', path)


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("=" * 60)
    print("Amazonサムネイル取得APIサーバー")
    print("=" * 60)
    print("\nサーバーを起動しています...")
    print("Notionウィジェットから以下のURLでアクセスできます:")
    print(f"  http://localhost:{port}/api/get-thumbnail")
    print("\nサーバーを停止するには Ctrl+C を押してください\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)

