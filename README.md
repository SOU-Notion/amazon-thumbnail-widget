# Amazonサムネイル取得ウィジェット

Notionに埋め込めるウィジェットです。本のタイトルを入力すると、Amazonのサムネイル画像URLを取得します。

## 機能

- 📚 本のタイトルからAmazonサムネイル画像URLを取得
- 🔢 ISBNからも検索可能
- 📋 取得したURLをワンクリックでコピー
- 🖼️ 画像のプレビュー表示

## セットアップ

### 1. バックエンドAPIサーバーの起動

```bash
cd "C:\Users\1024i\Documents\python code\Notion\読書管理\amazon_thumbnail_widget"
pip install flask flask-cors requests
python app.py
```

サーバーが起動すると、`http://localhost:5000` でAPIが利用可能になります。

### 2. ウィジェットのデプロイ

#### 方法A: ローカル開発サーバーでホスト

```bash
# 簡単なHTTPサーバーを起動
python -m http.server 8000
```

ブラウザで `http://localhost:8000` にアクセスして動作確認。

#### 方法B: オンラインホスティング（推奨）

以下のサービスにデプロイして、Notionからアクセスできるようにします：

- **Vercel** (推奨)
- **Netlify**
- **GitHub Pages**
- **Glitch**

### 3. Notionに埋め込む

1. Notionでページを開く
2. `/embed` または「埋め込み」を入力
3. ウィジェットのURLを入力
   - 例: `https://your-widget-url.com/index.html`

## ファイル構成

```
amazon_thumbnail_widget/
├── index.html      # メインのHTMLファイル
├── style.css       # スタイルシート
├── script.js       # フロントエンドのJavaScript
├── app.py          # バックエンドAPIサーバー（Flask）
└── README.md       # このファイル
```

## 使用方法

1. バックエンドAPIサーバーを起動（`python app.py`）
2. ウィジェットページを開く
3. 本のタイトル（またはISBN）を入力
4. 「検索」ボタンをクリック
5. 取得したURLをコピーしてNotionに貼り付け

## 注意事項

- バックエンドAPIサーバーが起動している必要があります
- CORSの問題を避けるため、バックエンドAPIが必要です
- 本番環境では、適切なホスティングサービスを使用してください

## トラブルシューティング

### バックエンドAPIに接続できない

- `app.py` が起動しているか確認
- `http://localhost:5000/health` にアクセスして動作確認
- ファイアウォールの設定を確認

### CORSエラーが発生する

- `flask-cors` がインストールされているか確認
- バックエンドAPIのCORS設定を確認

