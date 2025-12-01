# Gitプッシュ手順（トラブルシューティング）

リポジトリが空と表示される場合の対処法です。

## 手動でプッシュする手順

PowerShellで以下のコマンドを順番に実行してください：

```powershell
# 1. ディレクトリに移動
cd "C:\Users\1024i\Documents\python code\Notion\読書管理\amazon_thumbnail_widget"

# 2. 現在の状態を確認
git status

# 3. すべてのファイルを追加
git add .

# 4. コミット（まだコミットしていない場合）
git commit -m "Initial commit: Amazon thumbnail widget"

# 5. リモートリポジトリを確認
git remote -v

# 6. リモートが正しく設定されていない場合、削除して再追加
git remote remove origin
git remote add origin https://github.com/SOU-Notion/amazon-thumbnail-widget.git

# 7. プッシュ
git push -u origin main
```

## 認証が必要な場合

GitHubにプッシュする際、認証情報が求められる場合があります。

### Personal Access Tokenを使用する方法（推奨）

1. GitHubにログイン
2. Settings → Developer settings → Personal access tokens → Tokens (classic)
3. "Generate new token" をクリック
4. スコープで `repo` にチェック
5. トークンを生成してコピー
6. プッシュ時にパスワードの代わりにトークンを入力

### または、GitHub CLIを使用

```powershell
# GitHub CLIをインストール（まだの場合）
winget install --id GitHub.cli

# 認証
gh auth login

# その後、通常通りプッシュ
git push -u origin main
```

## ファイルが表示されない場合

以下のファイルがすべて含まれているか確認：

- `app.py`
- `amazon_thumbnail_fetcher.py` ← 重要！
- `index.html`
- `style.css`
- `script.js`
- `requirements.txt`
- `Procfile`
- `.gitignore`

`amazon_thumbnail_fetcher.py` がない場合：

```powershell
copy ..\amazon_thumbnail_fetcher.py .
git add amazon_thumbnail_fetcher.py
git commit -m "Add amazon_thumbnail_fetcher.py"
git push
```

## 確認方法

GitHubのリポジトリページ（https://github.com/SOU-Notion/amazon-thumbnail-widget）にアクセスして、ファイルが表示されているか確認してください。

