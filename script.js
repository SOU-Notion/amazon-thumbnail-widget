// Amazonサムネイル取得ウィジェット

// バックエンドAPIのURL（デプロイ後はここを変更）
// ローカル開発: 'http://localhost:5000/api/get-thumbnail'
// クラウドデプロイ後: 'https://your-app-name.onrender.com/api/get-thumbnail'
// ※ Render 本番環境では必ず /api/get-thumbnail まで含める
const API_ENDPOINT = 'https://amazon-thumbnail-widget.onrender.com/api/get-thumbnail';
// DOM要素
const bookTitleInput = document.getElementById('book-title');
const searchBtn = document.getElementById('search-btn');
const clearBtn = document.getElementById('clear-btn');
const resultSection = document.getElementById('result-section');
const thumbnailImg = document.getElementById('thumbnail-img');
const thumbnailUrlInput = document.getElementById('thumbnail-url');
const copyBtn = document.getElementById('copy-btn');
const errorMessage = document.getElementById('error-message');

// 検索ボタンのクリックイベント
searchBtn.addEventListener('click', handleSearch);
bookTitleInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSearch();
    }
});

// クリアボタンのクリックイベント
clearBtn.addEventListener('click', handleClear);

// URLコピーボタン
copyBtn.addEventListener('click', copyUrl);

async function handleSearch() {
    const title = bookTitleInput.value.trim();
    
    // バリデーション
    if (!title) {
        showError('タイトルを入力してください');
        return;
    }
    
    // UI更新
    setLoading(true);
    hideError();
    hideResult();
    
    try {
        console.log('検索開始:', { title });
        
        // バックエンドAPIを呼び出す（複数候補対応）
        const candidates = await fetchThumbnail(title);
        
        console.log('検索結果:', candidates);
        
        if (candidates && candidates.length > 0) {
            if (candidates.length === 1) {
                // 1件のみの場合は直接表示
                showResult(candidates[0]);
            } else {
                // 複数候補の場合は選択UIを表示
                showCandidates(candidates);
            }
        } else {
            showError('サムネイル画像が見つかりませんでした');
        }
    } catch (error) {
        console.error('エラー詳細:', error);
        showError('エラーが発生しました: ' + (error.message || '不明なエラー'));
    } finally {
        setLoading(false);
    }
}

function handleClear() {
    // 入力フィールドをクリア
    bookTitleInput.value = '';
    
    // 結果を非表示
    hideResult();
    
    // エラーメッセージを非表示
    hideError();
    
    // 候補コンテナを削除
    const candidatesContainer = document.getElementById('candidates-container');
    if (candidatesContainer) {
        candidatesContainer.remove();
    }
    
    // 入力フィールドにフォーカス
    bookTitleInput.focus();
}

async function fetchThumbnail(title) {
    return await fetchThumbnailFromBackend(title);
}

async function fetchThumbnailFromBackend(title) {
    // バックエンドAPIのエンドポイント（複数候補対応）
    try {
        const requestBody = { 
            title: title || null,
            isbn: null,
            max_results: 5  // 最大5件の候補を取得
        };
        
        console.log('APIリクエスト送信:', requestBody);
        
        // タイムアウトを60秒に設定
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 60000);
        
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        console.log('APIレスポンスステータス:', response.status);
        
        if (!response.ok) {
            let errorMessage = `HTTP error! status: ${response.status}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                const errorText = await response.text();
                errorMessage = errorText || errorMessage;
            }
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        console.log('APIレスポンスデータ:', data);
        
        if (data.candidates) {
            return data.candidates;
        } else if (data.thumbnail_url) {
            // 後方互換性: 単一のthumbnail_urlが返された場合
            return [{
                thumbnail_url: data.thumbnail_url,
                title: data.title || 'タイトル不明',
                url: null,
                asin: null
            }];
        } else {
            throw new Error('予期しないレスポンス形式です');
        }
    } catch (error) {
        console.error('バックエンドAPIエラー詳細:', error);
        if (error.name === 'AbortError') {
            throw new Error('リクエストがタイムアウトしました。時間がかかりすぎている可能性があります。');
        } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            throw new Error('バックエンドAPIに接続できません。バックエンドサーバー（app.py）が起動しているか確認してください。');
        }
        throw error;
    }
}

function showResult(candidate) {
    // 候補コンテナを削除
    const candidatesContainer = document.getElementById('candidates-container');
    if (candidatesContainer) {
        candidatesContainer.remove();
    }
    
    // サムネイルプレビューとURL表示を表示
    const thumbnailPreview = document.getElementById('thumbnail-preview');
    const urlDisplay = document.querySelector('.url-display');
    if (thumbnailPreview) thumbnailPreview.style.display = 'block';
    if (urlDisplay) urlDisplay.style.display = 'block';
    
    thumbnailUrlInput.value = candidate.thumbnail_url;
    thumbnailImg.src = candidate.thumbnail_url;
    thumbnailImg.onerror = () => {
        showError('画像の読み込みに失敗しました');
    };
    resultSection.style.display = 'block';
}

function showCandidates(candidates) {
    // 候補選択UIを表示
    // 既存の候補コンテナを削除
    const existingContainer = document.getElementById('candidates-container');
    if (existingContainer) {
        existingContainer.remove();
    }
    
    // 既存の結果表示を非表示（サムネイルプレビューとURL表示）
    const thumbnailPreview = document.getElementById('thumbnail-preview');
    const urlDisplay = document.querySelector('.url-display');
    if (thumbnailPreview) thumbnailPreview.style.display = 'none';
    if (urlDisplay) urlDisplay.style.display = 'none';
    
    // 候補コンテナを作成
    const container = document.createElement('div');
    container.id = 'candidates-container';
    container.className = 'candidates-container';
    
    // 結果セクションの最初に挿入
    resultSection.insertBefore(container, resultSection.firstChild);
    
    container.innerHTML = '<h3>検索結果（選択してください）</h3>';
    
    candidates.forEach((candidate, index) => {
        const candidateCard = document.createElement('div');
        candidateCard.className = 'candidate-card';
        
        // タイトルをエスケープ（XSS対策）
        const safeTitle = candidate.title.replace(/</g, '&lt;').replace(/>/g, '&gt;');
        const safeUrl = candidate.thumbnail_url.replace(/"/g, '&quot;');
        
        candidateCard.innerHTML = `
            <div class="candidate-image">
                <img src="${safeUrl}" alt="${safeTitle}" 
                     onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'200\' height=\'200\'%3E%3Crect fill=\'%23ddd\' width=\'200\' height=\'200\'/%3E%3Ctext x=\'50%25\' y=\'50%25\' text-anchor=\'middle\' dy=\'.3em\' fill=\'%23999\'%3E画像なし%3C/text%3E%3C/svg%3E'">
            </div>
            <div class="candidate-info">
                <div class="candidate-title">${safeTitle}</div>
                <button class="select-button" data-index="${index}">この画像を選択</button>
            </div>
        `;
        
        // 選択ボタンのイベント
        const selectBtn = candidateCard.querySelector('.select-button');
        selectBtn.addEventListener('click', () => {
            selectCandidate(candidate);
        });
        
        container.appendChild(candidateCard);
    });
    
    // 結果セクションを表示
    resultSection.style.display = 'block';
}

function selectCandidate(candidate) {
    // 候補を選択したら、通常の結果表示に切り替え
    const candidatesContainer = document.getElementById('candidates-container');
    if (candidatesContainer) {
        candidatesContainer.remove();
    }
    showResult(candidate);
}

function hideResult() {
    // 候補コンテナを削除
    const candidatesContainer = document.getElementById('candidates-container');
    if (candidatesContainer) {
        candidatesContainer.remove();
    }
    
    // サムネイルプレビューとURL表示を非表示
    const thumbnailPreview = document.getElementById('thumbnail-preview');
    const urlDisplay = document.querySelector('.url-display');
    if (thumbnailPreview) thumbnailPreview.style.display = 'none';
    if (urlDisplay) urlDisplay.style.display = 'none';
    
    // 結果セクションを非表示
    resultSection.style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}

function setLoading(loading) {
    searchBtn.disabled = loading;
    const btnText = searchBtn.querySelector('.btn-text');
    const btnLoading = searchBtn.querySelector('.btn-loading');
    
    if (loading) {
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline';
    } else {
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
}

function copyUrl() {
    thumbnailUrlInput.select();
    document.execCommand('copy');
    
    // コピー成功のフィードバック
    const originalText = copyBtn.textContent;
    copyBtn.textContent = 'コピーしました！';
    copyBtn.style.background = '#4caf50';
    
    setTimeout(() => {
        copyBtn.textContent = originalText;
        copyBtn.style.background = '#4caf50';
    }, 2000);
}

