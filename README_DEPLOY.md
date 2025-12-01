# デプロイ手順（簡易版）

## 🚀 クイックスタート（Render.com推奨）

### 1. GitHubにリポジトリを作成

1. GitHubで新しいリポジトリを作成（例: `amazon-thumbnail-widget`）
2. 以下のコマンドでファイルをプッシュ：

```bash
cd "C:\Users\1024i\Documents\python code\Notion\読書管理\amazon_thumbnail_widget"
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/amazon-thumbnail-widget.git
git push -u origin main
```

### 2. Render.comでデプロイ

1. [Render.com](https://render.com) にアクセス
2. 「Get Started for Free」→ GitHubでログイン
3. 「New +」→「Web Service」
4. GitHubリポジトリを選択
5. 設定：
   - **Name**: `amazon-thumbnail-widget`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. 「Create Web Service」をクリック
7. デプロイ完了後、URLをコピー（例: `https://amazon-thumbnail-widget.onrender.com`）

### 3. フロントエンドのAPIエンドポイントを更新

`script.js` の3行目を変更：

```javascript
const API_ENDPOINT = 'https://amazon-thumbnail-widget.onrender.com/api/get-thumbnail';
```

### 4. フロントエンドをGitHub Pagesで公開（オプション）

1. GitHubリポジトリの Settings → Pages
2. Source を `main` ブランチ、`/amazon_thumbnail_widget` フォルダに設定
3. 公開URLが生成されます（例: `https://your-username.github.io/amazon-thumbnail-widget/`）

## 📝 注意事項

- Render.comの無料プランでは、15分間アクセスがないとスリープします
- 初回アクセス時に起動するため、少し時間がかかることがあります
- 本番環境では `script.js` の `API_ENDPOINT` を本番URLに変更してください

## 🔧 ローカル開発

```bash
# バックエンド起動
python app.py

# ブラウザで http://localhost:5000 にアクセス
```

## 🌐 その他のホスティングサービス

- **Railway.app**: GitHub連携で自動デプロイ
- **Fly.io**: 無料プランあり
- **Vercel**: サーバーレス関数としてデプロイ可能

詳細は `DEPLOY.md` を参照してください。

