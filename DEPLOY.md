# デプロイ手順

このウィジェットをクラウドで公開する方法を説明します。

## 方法1: Render.com（推奨・無料プランあり）

### 1. GitHubにリポジトリを作成

1. GitHubで新しいリポジトリを作成
2. 以下のファイルをコミット・プッシュ：
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `index.html`
   - `style.css`
   - `script.js`
   - 親ディレクトリの `amazon_thumbnail_fetcher.py` も必要

### 2. Render.comでデプロイ

1. [Render.com](https://render.com) にアカウント作成（GitHub連携）
2. 「New Web Service」を選択
3. GitHubリポジトリを選択
4. 設定：
   - **Name**: `amazon-thumbnail-widget`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. 「Create Web Service」をクリック

### 3. フロントエンドの設定

`script.js` の `API_ENDPOINT` を Render.com のURLに変更：

```javascript
const API_ENDPOINT = 'https://your-app-name.onrender.com/api/get-thumbnail';
```

## 方法2: Railway.app（無料プランあり）

### 1. Railwayでデプロイ

1. [Railway.app](https://railway.app) にアカウント作成
2. 「New Project」→「Deploy from GitHub repo」
3. リポジトリを選択
4. Railwayが自動的に検出してデプロイ

### 2. 環境変数の設定

通常は不要ですが、必要に応じて設定できます。

## 方法3: Vercel（サーバーレス関数）

### 1. Vercelでデプロイ

1. [Vercel](https://vercel.com) にアカウント作成
2. GitHubリポジトリをインポート
3. 設定：
   - **Framework Preset**: Other
   - **Build Command**: `pip install -r requirements.txt`
   - **Output Directory**: `.`

### 2. `vercel.json` の作成

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "app.py"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ]
}
```

## フロントエンドのホスティング

フロントエンド（HTML/CSS/JS）は以下の方法でホスティングできます：

### GitHub Pages

1. リポジトリの Settings → Pages
2. Source を選択
3. `index.html` があるディレクトリを選択

### Netlify

1. [Netlify](https://netlify.com) にアカウント作成
2. 「Add new site」→「Import an existing project」
3. GitHubリポジトリを選択
4. デプロイ設定：
   - **Base directory**: `amazon_thumbnail_widget`
   - **Publish directory**: `amazon_thumbnail_widget`

## 注意事項

1. **CORS設定**: バックエンドの `app.py` で `CORS(app)` が設定されていることを確認
2. **APIエンドポイント**: フロントエンドの `script.js` でバックエンドのURLを正しく設定
3. **タイムアウト**: Render.comの無料プランでは15分でスリープする可能性があります

## ローカル開発

ローカルで開発する場合：

```bash
# バックエンド起動
cd amazon_thumbnail_widget
python app.py

# フロントエンド（別ターミナル）
python -m http.server 8000
```

ブラウザで `http://localhost:8000` にアクセス

