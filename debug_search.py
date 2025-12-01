#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon検索結果のデバッグ用スクリプト
実際のHTML構造を確認して、タイトル取得方法を改善する
"""

import requests
import re
from bs4 import BeautifulSoup

def debug_amazon_search(title: str):
    """Amazon検索結果のHTML構造をデバッグ"""
    amazon_base_url = "https://www.amazon.co.jp"
    
    search_url = f"{amazon_base_url}/s"
    params = {
        'k': title,
        'i': 'stripbooks',  # 書籍カテゴリ
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"検索キーワード: {title}")
    print(f"検索URL: {search_url}")
    print(f"パラメータ: {params}\n")
    
    response = requests.get(search_url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    
    print("=" * 60)
    print("HTML構造の解析")
    print("=" * 60)
    
    # BeautifulSoupで解析
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 検索結果を取得
    search_results = soup.find_all('div', {'data-component-type': 's-search-result'})
    print(f"\n検索結果数: {len(search_results)}件\n")
    
    # 最初の5件を詳しく表示
    for i, result in enumerate(search_results[:5], 1):
        print(f"\n【検索結果 {i}】")
        print("-" * 60)
        
        # ASIN
        asin = result.get('data-asin')
        print(f"ASIN: {asin}")
        
        # タイトルを複数の方法で取得
        print("\nタイトル取得の試行:")
        
        # 方法1: h2タグ
        h2_tag = result.find('h2')
        if h2_tag:
            print(f"  h2タグ: {h2_tag}")
            a_tag = h2_tag.find('a')
            if a_tag:
                print(f"    aタグ: {a_tag.get('href', 'N/A')}")
                span_tags = a_tag.find_all('span')
                for j, span in enumerate(span_tags[:3], 1):
                    text = span.get_text(strip=True)
                    if text and len(text) > 3:
                        print(f"      span {j}: {text[:100]}")
        
        # 方法2: aタグ（s-linkクラス）
        a_tags = result.find_all('a', class_=lambda x: x and 's-link' in str(x))
        for a_tag in a_tags[:2]:
            text = a_tag.get_text(strip=True)
            if text and len(text) > 3:
                print(f"  aタグ（s-link）: {text[:100]}")
        
        # 方法3: spanタグ（a-text-normalクラス）
        span_tags = result.find_all('span', class_=lambda x: x and 'a-text-normal' in str(x))
        for span_tag in span_tags[:2]:
            text = span_tag.get_text(strip=True)
            if text and len(text) > 3:
                print(f"  spanタグ（a-text-normal）: {text[:100]}")
        
        # HTMLの一部を表示（デバッグ用）
        print(f"\n  HTML構造（最初の500文字）:")
        html_str = str(result)[:500]
        print(f"    {html_str}...")
    
    print("\n" + "=" * 60)
    print("デバッグ完了")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    search_title = sys.argv[1] if len(sys.argv) > 1 else "いけない"
    debug_amazon_search(search_title)

