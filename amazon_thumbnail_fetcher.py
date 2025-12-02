#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazonサムネイル画像自動取得ツール
本のタイトルやISBNからAmazonのサムネイル画像URLを自動取得します。
"""

import requests
import re
from typing import Optional, Dict, List
import logging
import time

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    logging.warning("BeautifulSoup4がインストールされていません。HTMLパースが簡易版になります。")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AmazonThumbnailFetcher:
    """Amazonのサムネイル画像を取得するクラス"""
    
    def __init__(self):
        self.amazon_base_url = "https://www.amazon.co.jp"
        self.amazon_image_base = "https://images-na.ssl-images-amazon.com/images"
        # ブラウザのようなリクエストヘッダー（ボット検出を回避）
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        # セッションを使用してクッキーを保持（より現実的なブラウザセッションをシミュレート）
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def extract_asin_from_url(self, url: str) -> Optional[str]:
        """Amazon URLからASINを抽出"""
        # ASINは10文字の英数字
        asin_pattern = r'/(?:dp|gp/product|exec/obidos/ASIN)/([A-Z0-9]{10})'
        match = re.search(asin_pattern, url)
        if match:
            return match.group(1)
        return None
    
    def isbn_to_asin(self, isbn: str) -> Optional[str]:
        """ISBNからASINを取得（ISBN-10とASINは同じ形式の場合がある）"""
        # ISBN-10は10桁、ISBN-13は13桁
        isbn_clean = isbn.replace('-', '').replace(' ', '')
        
        # ISBN-13の場合、最初の3桁（978または979）と最後のチェックディジットを除いてISBN-10に変換
        if len(isbn_clean) == 13:
            # 978/979で始まる場合は、4桁目から10桁目までがISBN-10の本体部分
            if isbn_clean.startswith('978') or isbn_clean.startswith('979'):
                isbn_10_body = isbn_clean[3:12]  # 9桁
                # チェックディジットを計算（簡易版）
                # 実際にはISBN-10のチェックディジット計算が必要
                return isbn_10_body
        elif len(isbn_clean) == 10:
            return isbn_clean
        
        return None
    
    def search_amazon_by_title(self, title: str, max_results: int = 1) -> List[Dict[str, str]]:
        """タイトルでAmazonを検索して複数の結果を取得（書籍のみ）"""
        # 例外が起きても必ず参照できるように、先に初期化しておく
        results: List[Dict[str, str]] = []
        
        search_url = f"{self.amazon_base_url}/s"
        params = {
            'k': title,
            'i': 'stripbooks',  # 書籍カテゴリに絞り込み
            'rh': 'n:465392',  # 書籍カテゴリID（より確実に書籍のみ）
            'ref': 'sr_pg_1'
        }
        
        # リトライロジック（503エラー対策）
        max_retries = 3
        retry_delay = 5  # 初期待機時間（秒）- ボット検出を回避するため長めに設定
        response = None
        
        for attempt in range(max_retries):
            try:
                # セッションを使用してリクエスト（クッキーを保持）
                response = self.session.get(search_url, params=params, timeout=30)
                
                # 503エラーの場合はリトライ
                if response.status_code == 503:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # 指数バックオフ: 2秒、4秒、8秒
                        logger.warning(f"Amazon 503エラー (試行 {attempt + 1}/{max_retries})。{wait_time}秒後に再試行します...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Amazon 503エラー: 最大リトライ回数に達しました")
                        # 503エラーの場合は空の結果を返す（例外を発生させない）
                        return results
                
                response.raise_for_status()
                break  # 成功したらループを抜ける
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1 and (isinstance(e, requests.exceptions.HTTPError) and e.response and e.response.status_code == 503):
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"リクエストエラー (試行 {attempt + 1}/{max_retries}): {e}。{wait_time}秒後に再試行します...")
                    time.sleep(wait_time)
                    continue
                else:
                    # 503以外のエラー、または最大リトライ回数に達した場合は例外を再発生
                    raise
        
        # リトライがすべて失敗した場合、またはresponseが取得できなかった場合
        if response is None:
            logger.error("Amazon検索: リクエストに失敗しました")
            return results
        
        try:
            
            # BeautifulSoupでHTMLを解析（より確実に商品情報を取得）
            if BS4_AVAILABLE:
                soup = BeautifulSoup(response.text, 'html.parser')
                # data-component-type="s-search-result" の要素を探す
                search_results = soup.find_all('div', {'data-component-type': 's-search-result'})
                logger.info(f"BeautifulSoupで {len(search_results)} 件の検索結果を発見")
                
                # 検索結果から商品情報を抽出
                product_data = []
                for result in search_results[:max_results * 4]:  # 多めに取得
                    try:
                        # ASINを取得
                        asin = result.get('data-asin')
                        if not asin:
                            continue
                        
                        # タイトルを取得（複数の方法を試す）
                        title = None
                        
                        # 方法1: h2タグ内のaタグから（すべてのspanタグのテキストを結合）
                        h2_tag = result.find('h2')
                        if h2_tag:
                            a_tag = h2_tag.find('a')
                            if a_tag:
                                # すべてのspanタグのテキストを結合（タイトルが複数のspanに分割されている場合に対応）
                                span_tags = a_tag.find_all('span')
                                if span_tags:
                                    title_parts = []
                                    for span in span_tags:
                                        text = span.get_text(strip=True)
                                        if text and len(text) > 0:
                                            title_parts.append(text)
                                    if title_parts:
                                        title = ' '.join(title_parts)
                        
                        # 方法2: h2タグ内のすべてのテキストを取得
                        if not title and h2_tag:
                            title = h2_tag.get_text(strip=True)
                            # 長すぎる場合は最初の部分のみ（著者名などが含まれる場合がある）
                            if len(title) > 200:
                                title = title[:200]
                        
                        # 方法3: aタグのs-linkクラスから（すべてのspanタグのテキストを結合）
                        if not title:
                            a_tag = result.find('a', class_=lambda x: x and 's-link' in str(x))
                            if a_tag:
                                span_tags = a_tag.find_all('span')
                                if span_tags:
                                    title_parts = []
                                    for span in span_tags:
                                        text = span.get_text(strip=True)
                                        if text and len(text) > 0:
                                            title_parts.append(text)
                                    if title_parts:
                                        title = ' '.join(title_parts)
                        
                        # 方法4: spanタグのa-text-normalクラスから
                        if not title:
                            span_tags = result.find_all('span', class_=lambda x: x and 'a-text-normal' in str(x))
                            if span_tags:
                                title_parts = []
                                for span in span_tags[:3]:  # 最初の3つまで
                                    text = span.get_text(strip=True)
                                    if text and len(text) > 3:
                                        title_parts.append(text)
                                if title_parts:
                                    title = ' '.join(title_parts)
                        
                        if not title or len(title) < 3:
                            continue
                        
                        # 商品URLを構築
                        product_url = f"{self.amazon_base_url}/dp/{asin}"
                        
                        # 検索結果ページから直接画像URLを抽出
                        thumbnail_url = None
                        
                        # 方法1: imgタグを探す（複数のパターンを試す）
                        img_tag = None
                        # パターン1: s-imageクラスを持つimgタグ
                        img_tag = result.find('img', class_=lambda x: x and 's-image' in str(x))
                        # パターン2: data-image-latency属性を持つimgタグ
                        if not img_tag:
                            img_tag = result.find('img', {'data-image-latency': True})
                        # パターン3: 任意のimgタグ
                        if not img_tag:
                            img_tag = result.find('img')
                        
                        if img_tag:
                            # 複数の属性から画像URLを取得（優先順位順）
                            thumbnail_url = (
                                img_tag.get('src') or 
                                img_tag.get('data-src') or 
                                img_tag.get('data-lazy-src') or 
                                img_tag.get('data-image-src') or
                                img_tag.get('data-old-src')
                            )
                        
                        # 方法2: 正規表現で画像URLを探す（検索結果のHTMLから）
                        if not thumbnail_url:
                            result_html = str(result)
                            # Amazonの画像URLパターン（より柔軟なパターン）
                            img_patterns = [
                                r'https://m\.media-amazon\.com/images/I/[^"\s<>]+\._AC_SL\d+_[^"\s<>]*\.(jpg|png)',
                                r'https://m\.media-amazon\.com/images/I/[^"\s<>]+\._AC_UL\d+_[^"\s<>]*\.(jpg|png)',
                                r'https://m\.media-amazon\.com/images/I/[^"\s<>]+\._AC_SY\d+_[^"\s<>]*\.(jpg|png)',
                                r'https://images-na\.ssl-images-amazon\.com/images/I/[^"\s<>]+\._AC_SL\d+_[^"\s<>]*\.(jpg|png)',
                                r'https://images-na\.ssl-images-amazon\.com/images/I/[^"\s<>]+\._SL\d+_[^"\s<>]*\.(jpg|png)',
                            ]
                            for pattern in img_patterns:
                                match = re.search(pattern, result_html)
                                if match:
                                    thumbnail_url = match.group(0)
                                    break
                        
                        # 画像URLが見つからない場合は、商品ページから取得を試みる（フォールバック）
                        if not thumbnail_url:
                            thumbnail_url = self.get_thumbnail_from_url(product_url)
                        
                        product_data.append({
                            'asin': asin,
                            'url': product_url,
                            'title': title[:200],
                            'thumbnail_url': thumbnail_url,  # 検索結果から取得した画像URL
                            'html_element': result  # デバッグ用
                        })
                        
                        if len(product_data) >= max_results * 3:
                            break
                            
                    except Exception as e:
                        logger.debug(f"検索結果の解析エラー: {e}")
                        continue
                
                logger.info(f"抽出した商品データ: {len(product_data)} 件")
                matches = product_data
            else:
                # BeautifulSoupが使えない場合は正規表現で
                product_pattern = r'href="(/dp/[A-Z0-9]{10}|/gp/product/[A-Z0-9]{10})'
                matches = re.findall(product_pattern, response.text)
                logger.info(f"正規表現で {len(matches)} 件の商品リンクを発見")
                matches = [{'url': f"{self.amazon_base_url}{m}"} for m in matches]
            
            # 書籍以外の商品（Kindle、オーディオブックなど）を除外するための追加フィルタ
            # ただし、まずは書籍カテゴリで絞り込んでいるので、この段階では基本的に書籍のみのはず
            
            seen_asins = set()
            
            # BeautifulSoupで取得したデータを使用
            if BS4_AVAILABLE and isinstance(matches, list) and matches and 'asin' in matches[0]:
                # BeautifulSoupで既にタイトルと画像URLを取得済み
                for product_info in matches:
                    asin = product_info.get('asin')
                    product_url = product_info.get('url')
                    product_title = product_info.get('title')
                    thumbnail_url = product_info.get('thumbnail_url')  # 検索結果から取得済み
                    
                    if not asin or asin in seen_asins:
                        continue
                    
                    seen_asins.add(asin)
                    
                    # 画像URLが取得できた場合のみ追加
                    if thumbnail_url:
                        results.append({
                            'asin': asin,
                            'url': product_url,
                            'title': product_title,
                            'thumbnail_url': thumbnail_url
                        })
                        logger.info(f"候補追加: {product_title[:50]}... (ASIN: {asin})")
                    else:
                        logger.warning(f"画像URLが見つかりませんでした: {product_url}")
                    
                    # 十分な候補が集まったら終了
                    if len(results) >= max_results * 3:
                        break
            else:
                # 正規表現で取得した場合（後方互換性）
                for match_info in matches[:max_results * 4]:
                    if isinstance(match_info, dict):
                        product_url = match_info.get('url')
                    else:
                        product_path = match_info
                        product_url = f"{self.amazon_base_url}{product_path}"
                    
                    asin = self.extract_asin_from_url(product_url)
                    
                    if asin and asin not in seen_asins:
                        seen_asins.add(asin)
                        
                        # 商品タイトルを取得
                        product_title = self._extract_title_from_search_result(response.text, asin, product_url)
                        
                        # サムネイルURLを取得
                        thumbnail_url = self.get_thumbnail_from_url(product_url)
                        
                        if thumbnail_url:
                            results.append({
                                'asin': asin,
                                'url': product_url,
                                'title': product_title[:200],
                                'thumbnail_url': thumbnail_url
                            })
                            logger.info(f"候補追加: {product_title[:50]}... (ASIN: {asin})")
                        
                        if len(results) >= max_results * 3:
                            break
            
            # Amazonの検索結果の順序を保持（関連性ソートは無効化）
            # ユーザーの要望: Amazonで表示される順序をそのまま使用
            if results:
                # max_results件に制限（順序は保持）
                results = results[:max_results]
                
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 503:
                logger.error(f"Amazon検索エラー (503): サーバーが一時的に利用できません。しばらく待ってから再試行してください。")
            else:
                logger.error(f"Amazon検索エラー (HTTP {e.response.status_code if e.response else 'Unknown'}): {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Amazon検索エラー (リクエストエラー): {e}")
        except Exception as e:
            logger.error(f"Amazon検索エラー: {e}")
        
        return results
    
    def _extract_title_from_search_result(self, html_text: str, asin: str, product_url: str) -> str:
        """検索結果ページから商品タイトルを抽出（複数のパターンを試す）"""
        # data-asin属性の周辺からタイトルを取得
        # Amazonの検索結果ページの構造に合わせて複数のパターンを試す
        
        # まず、data-asin属性の位置を特定
        asin_pos = html_text.find(f'data-asin="{asin}"')
        if asin_pos == -1:
            # data-asinが見つからない場合、商品ページから取得
            return self._extract_title_from_product_page(product_url)
        
        # data-asinの周辺（前後2000文字）を抽出して検索
        context_start = max(0, asin_pos - 500)
        context_end = min(len(html_text), asin_pos + 2000)
        context = html_text[context_start:context_end]
        
        patterns = [
            # パターン1: h2タグ内のタイトル（最も一般的なパターン）
            r'<h2[^>]*>.*?<a[^>]*>.*?<span[^>]*>([^<]+)</span>',
            # パターン2: aタグ内のタイトル（s-linkクラス）
            r'<a[^>]*class="[^"]*s-link[^"]*"[^>]*>.*?<span[^>]*>([^<]+)</span>',
            # パターン3: spanタグ内のタイトル（a-text-normalクラス）
            r'<span[^>]*class="[^"]*a-text-normal[^"]*"[^>]*>([^<]+)</span>',
            # パターン4: より広範囲で検索（10文字以上のテキスト）
            r'<span[^>]*>([^<]{10,150})</span>',
        ]
        
        for pattern in patterns:
            try:
                match = re.search(pattern, context, re.DOTALL | re.IGNORECASE)
                if match:
                    title = match.group(1).strip()
                    # HTMLエンティティをデコード
                    title = title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
                    # 余分な空白を削除
                    title = ' '.join(title.split())
                    # 意味のあるタイトルかチェック（3文字以上、かつ「タイトル不明」などの無意味な文字列でない）
                    if title and len(title) > 3 and title.lower() not in ['タイトル不明', 'title', '商品名']:
                        # 著者名やシリーズ名が含まれている可能性があるので、長めに取得
                        return title[:200]
            except Exception as e:
                logger.debug(f"タイトル抽出パターンエラー: {e}")
                continue
        
        # どのパターンでも取得できなかった場合、商品ページから取得を試みる
        return self._extract_title_from_product_page(product_url)
    
    def _extract_title_from_product_page(self, product_url: str) -> str:
        """商品ページからタイトルを取得"""
        try:
            page_response = self.session.get(product_url, timeout=10)
            if page_response.status_code == 200:
                # 商品ページからタイトルを取得
                title_patterns = [
                    r'<span[^>]*id="productTitle"[^>]*>([^<]+)</span>',
                    r'<h1[^>]*id="title"[^>]*>.*?<span[^>]*>([^<]+)</span>',
                    r'<meta\s+property="og:title"\s+content="([^"]+)"',
                ]
                for title_pattern in title_patterns:
                    title_match = re.search(title_pattern, page_response.text, re.DOTALL | re.IGNORECASE)
                    if title_match:
                        title = title_match.group(1).strip()
                        title = title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
                        title = ' '.join(title.split())
                        if title and len(title) > 3:
                            return title[:200]
        except Exception as e:
            logger.debug(f"商品ページからのタイトル取得エラー: {e}")
        
        return "タイトル不明"
    
    def _sort_by_relevance(self, results: List[Dict[str, str]], search_title: str) -> List[Dict[str, str]]:
        """
        検索キーワードとの関連性でソート
        
        ソート基準:
        1. タイトルに検索語が完全一致または部分一致しているか
        2. タイトルが検索語で始まっているか
        3. タイトルに検索語が含まれているか
        4. 元の順番（関連性が同じ場合）
        """
        search_lower = search_title.lower()
        search_words = search_lower.split()
        
        def calculate_score(candidate):
            title_lower = candidate.get('title', '').lower()
            score = 0
            
            # 完全一致（最高点）
            if title_lower == search_lower:
                score += 1000
            
            # タイトルが検索語で始まる（高得点）
            if title_lower.startswith(search_lower):
                score += 500
            
            # 検索語がタイトルに含まれる（中得点）
            if search_lower in title_lower:
                score += 200
            
            # 検索語の各単語がタイトルに含まれる（低得点）
            for word in search_words:
                if word in title_lower:
                    score += 50
            
            # タイトルが短いほど関連性が高い可能性（微調整）
            # ただし、タイトルが短すぎる場合はペナルティ
            title_len = len(title_lower)
            if 10 <= title_len <= 100:
                score += 10
            
            return score
        
        # スコアを計算してソート
        scored_results = [(calculate_score(r), r) for r in results]
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        return [r for _, r in scored_results]
    
    def search_amazon_by_title_single(self, title: str) -> Optional[str]:
        """タイトルでAmazonを検索して最初の結果のURLを取得（後方互換性のため）"""
        results = self.search_amazon_by_title(title, max_results=1)
        if results:
            return results[0]['url']
        return None
    
    def get_thumbnail_url_from_asin(self, asin: str) -> str:
        """ASINからAmazonのサムネイル画像URLを生成"""
        # Amazonの画像URL形式: https://images-na.ssl-images-amazon.com/images/I/[IMAGE_ID]._SL[WIDTH]_.jpg
        # または: https://m.media-amazon.com/images/I/[IMAGE_ID]._SL[WIDTH]_.jpg
        
        # ASINから直接画像URLを構築することはできないため、
        # 商品ページから取得する必要がある
        product_url = f"{self.amazon_base_url}/dp/{asin}"
        return self.get_thumbnail_from_url(product_url)
    
    def get_thumbnail_from_url(self, url: str) -> Optional[str]:
        """Amazon商品URLからサムネイル画像URLを取得"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 画像URLのパターンを探す
            # パターン1: images-na.ssl-images-amazon.com
            pattern1 = r'https://images-na\.ssl-images-amazon\.com/images/I/[^"\s]+\._SL\d+_\.jpg'
            # パターン2: m.media-amazon.com
            pattern2 = r'https://m\.media-amazon\.com/images/I/[^"\s]+\._SL\d+_\.jpg'
            # パターン3: メタタグから取得
            pattern3 = r'<meta\s+property="og:image"\s+content="([^"]+)"'
            
            # メタタグから取得を試みる（最も確実）
            meta_match = re.search(pattern3, response.text)
            if meta_match:
                return meta_match.group(1)
            
            # 直接パターンマッチを試みる
            for pattern in [pattern1, pattern2]:
                matches = re.findall(pattern, response.text)
                if matches:
                    # 最初のマッチを返す（通常はメイン画像）
                    return matches[0]
            
            logger.warning(f"画像URLが見つかりませんでした: {url}")
            
        except Exception as e:
            logger.error(f"画像URL取得エラー: {e}")
        
        return None
    
    def get_thumbnail_by_title(self, title: str) -> Optional[str]:
        """タイトルからサムネイル画像URLを取得（最初の1件のみ）"""
        results = self.search_amazon_by_title(title, max_results=1)
        if results:
            return results[0]['thumbnail_url']
        return None
    
    def get_thumbnails_by_title(self, title: str, max_results: int = 5) -> List[Dict[str, str]]:
        """タイトルから複数のサムネイル画像候補を取得"""
        logger.info(f"タイトルで検索（複数候補）: {title}")
        return self.search_amazon_by_title(title, max_results=max_results)
    
    def get_thumbnail_by_isbn(self, isbn: str) -> Optional[str]:
        """ISBNからサムネイル画像URLを取得"""
        logger.info(f"ISBNで検索: {isbn}")
        
        # ISBNからASINを取得
        asin = self.isbn_to_asin(isbn)
        if not asin:
            logger.warning(f"ASINに変換できませんでした: {isbn}")
            return None
        
        logger.info(f"ASIN: {asin}")
        
        # ASINから画像URLを取得
        thumbnail_url = self.get_thumbnail_url_from_asin(asin)
        return thumbnail_url
    
    def get_thumbnail(self, title: Optional[str] = None, isbn: Optional[str] = None, 
                     amazon_url: Optional[str] = None) -> Optional[str]:
        """
        本の情報からAmazonサムネイル画像URLを取得
        
        Args:
            title: 本のタイトル
            isbn: ISBN（10桁または13桁）
            amazon_url: Amazon商品ページのURL
        
        Returns:
            サムネイル画像のURL、取得できない場合はNone
        """
        # 優先順位: amazon_url > isbn > title
        if amazon_url:
            asin = self.extract_asin_from_url(amazon_url)
            if asin:
                return self.get_thumbnail_url_from_asin(asin)
            else:
                return self.get_thumbnail_from_url(amazon_url)
        
        if isbn:
            result = self.get_thumbnail_by_isbn(isbn)
            if result:
                return result
        
        if title:
            return self.get_thumbnail_by_title(title)
        
        logger.warning("タイトル、ISBN、URLのいずれも指定されていません")
        return None


def main():
    """テスト用のメイン関数"""
    fetcher = AmazonThumbnailFetcher()
    
    # テストケース
    test_cases = [
        {"title": "Python実践入門"},
        {"isbn": "9784798161916"},
        {"title": "リーダブルコード"},
    ]
    
    print("=== Amazonサムネイル取得テスト ===\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"テスト {i}: {test}")
        thumbnail_url = fetcher.get_thumbnail(**test)
        if thumbnail_url:
            print(f"✓ 成功: {thumbnail_url}\n")
        else:
            print(f"✗ 失敗: 画像URLを取得できませんでした\n")


if __name__ == "__main__":
    main()

