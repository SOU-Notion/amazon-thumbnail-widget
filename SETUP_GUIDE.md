# 🚀 デプロイ完全ガイド

このガイドでは、Amazonサムネイル取得ウィジェットをクラウドにデプロイする手順を詳しく説明します。

## 📋 事前準備

- GitHubアカウント（[github.com](https://github.com)で作成）
- Render.comアカウント（GitHub連携で作成可能）

---

## ステップ1: GitHubリポジトリを作成

### 1-1. GitHubでリポジトリを作成

1. [GitHub](https://github.com) にログイン
2. 右上の「+」ボタン → 「New repository」をクリック
3. リポジトリ情報を入力：
   - **Repository name**: `amazon-thumbnail-widget`（任意の名前）
   - **Description**: `Amazon book thumbnail fetcher for Notion`
   - **Public** または **Private** を選択
   - **Initialize this repository with** のチェックは外す
4. 「Create repository」をクリック

### 1-2. リポジトリのURLをコピー

作成後、表示されるURLをコピーします（例: `https://github.com/your-username/amazon-thumbnail-widget.git`）

---

## ステップ2: ファイルをGitHubにプッシュ

### 2-1. Gitを初期化（初回のみ）

PowerShellまたはコマンドプロンプトで、以下のコマンドを実行：

```powershell
# ウィジェットのディレクトリに移動
cd "C:\Users\1024i\Documents\python code\Notion\読書管理\amazon_thumbnail_widget"

# Gitを初期化
git init

# すべてのファイルを追加
git add .

# 初回コミット
git commit -m "Initial commit: Amazon thumbnail widget"
```

### 2-2. GitHubリポジトリと接続

```powershell
# リモートリポジトリを追加（your-usernameとリポジトリ名を実際のものに置き換え）
git remote add origin https://github.com/your-username/amazon-thumbnail-widget.git

# メインブランチを設定
git branch -M main

# GitHubにプッシュ
git push -u origin main
```

**注意**: 初回プッシュ時、GitHubの認証情報（ユーザー名とパスワード/トークン）を求められます。

---

## ステップ3: Render.comでデプロイ

### 3-1. Render.comにアカウント作成

1. [Render.com](https://render.com) にアクセス
2. 「Get Started for Free」をクリック
3. 「Sign up with GitHub」を選択してGitHubアカウントでログイン
4. 必要に応じて、Render.comへのアクセス許可を承認

### 3-2. 新しいWebサービスを作成

1. Render.comのダッシュボードで「New +」ボタンをクリック
2. 「Web Service」を選択
3. 「Connect account」でGitHubアカウントを選択（まだ接続していない場合）
4. リポジトリ一覧から `amazon-thumbnail-widget` を選択
5. 「Connect」をクリック

### 3-3. サービス設定

以下の設定を入力：

- **Name**: `amazon-thumbnail-widget`（任意の名前）
- **Environment**: `Python 3` を選択
- **Region**: 最寄りのリージョン（例: `Oregon (US West)`）
- **Branch**: `main`（デフォルト）
- **Root Directory**: 空白のまま（デフォルト）
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  gunicorn app:app
  ```
- **Instance Type**: `Free`（無料プラン）

### 3-4. 環境変数（オプション）

通常は不要ですが、必要に応じて環境変数を追加できます。

### 3-5. デプロイ開始

1. 設定を確認
2. 「Create Web Service」をクリック
3. デプロイが開始されます（数分かかります）

### 3-6. デプロイ完了を待つ

- ビルドログが表示されます
- 「Live」と表示されればデプロイ完了
- サービスURLが表示されます（例: `https://amazon-thumbnail-widget.onrender.com`）

---

## ステップ4: APIエンドポイントを更新

### 4-1. デプロイされたURLを確認

Render.comのダッシュボードで、デプロイされたサービスのURLをコピーします。
例: `https://amazon-thumbnail-widget.onrender.com`

### 4-2. script.jsを更新

1. `script.js` ファイルを開く
2. 3行目の `API_ENDPOINT` を更新：

```javascript
// 変更前
const API_ENDPOINT = 'http://localhost:5000/api/get-thumbnail';

// 変更後（Render.comのURLに置き換え）
const API_ENDPOINT = 'https://amazon-thumbnail-widget.onrender.com/api/get-thumbnail';
```

### 4-3. 変更をGitHubにプッシュ

```powershell
# 変更をコミット
git add script.js
git commit -m "Update API endpoint to production URL"

# GitHubにプッシュ
git push
```

### 4-4. Render.comで再デプロイ（自動）

GitHubにプッシュすると、Render.comが自動的に再デプロイを開始します。

---

## ✅ 動作確認

### ローカルでテスト

1. ブラウザで `https://amazon-thumbnail-widget.onrender.com` にアクセス
2. 本のタイトルを入力して検索
3. サムネイル画像が表示されれば成功

### Notionで使用

1. Notionで新しいページを作成
2. 「/embed」と入力
3. URLに `https://amazon-thumbnail-widget.onrender.com` を入力
4. ウィジェットが表示されます

---

## 🔧 トラブルシューティング

### デプロイが失敗する場合

1. **ビルドログを確認**
   - Render.comのダッシュボードで「Logs」タブを確認
   - エラーメッセージを確認

2. **よくあるエラー**
   - `ModuleNotFoundError`: `requirements.txt` に必要なパッケージが記載されているか確認
   - `ImportError`: `amazon_thumbnail_fetcher.py` が同じディレクトリにあるか確認

### APIに接続できない場合

1. **CORSエラー**
   - `app.py` で `CORS(app)` が設定されているか確認

2. **タイムアウト**
   - Render.comの無料プランでは、15分間アクセスがないとスリープします
   - 初回アクセス時に起動するため、少し時間がかかることがあります

### ファイルが見つからない場合

1. **amazon_thumbnail_fetcher.py の配置**
   - `amazon_thumbnail_widget` ディレクトリに `amazon_thumbnail_fetcher.py` があるか確認
   - ない場合は、親ディレクトリからコピー

---

## 📝 補足情報

### Render.comの無料プランの制限

- 15分間アクセスがないとスリープ
- 初回アクセス時に起動（数秒〜数十秒かかる場合あり）
- 月間750時間まで無料

### カスタムドメインの設定（オプション）

1. Render.comのダッシュボードで「Settings」→「Custom Domain」
2. ドメインを追加
3. DNS設定を更新

### 環境変数の設定

必要に応じて、Render.comの「Environment」タブで環境変数を設定できます。

---

## 🎉 完了！

これで、PCでサーバーを起動せずに、どこからでもウィジェットを使用できます！

質問や問題があれば、GitHubのIssuesで報告してください。

