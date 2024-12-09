const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
const message = document.getElementById('message');

// カメラの起動を非同期関数で行う
async function startCamera() {
    try {
        // ユーザーのカメラにアクセスをリクエスト
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' }  // 背面カメラを指定
        });
        
        // カメラのストリームをvideoタグに設定
        video.srcObject = stream;
        video.play();

        // カメラのメタデータ（幅・高さ）を取得してcanvasのサイズを設定
        video.addEventListener('loadedmetadata', () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
        });

        // QRコードのスキャン開始
        scanQRCode();
    } catch (err) {
        // エラー発生時の処理
        message.textContent = "カメラへのアクセスが拒否されました。";
        message.style.color = "red";
        console.error("カメラへのアクセスエラー:", err);
    }
}

// QRコードスキャン処理
function scanQRCode() {
    // videoタグの映像をcanvasに描画
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    const qrCode = jsQR(imageData.data, imageData.width, imageData.height);

    if (qrCode) {
        const qrText = qrCode.data;
        message.textContent = `QRコード検出: ${qrText}`;
        if (qrText.startsWith("http://") || qrText.startsWith("https://")) {
            checkURLSafety(qrText);
        }
    } else {
        message.textContent = "QRコードが検出されませんでした。";
    }

    // 再帰的にQRコードスキャンを続ける
    requestAnimationFrame(scanQRCode);
}

// URLの安全性をチェックするAPI
async function checkURLSafety(url) {
    const response = await fetch('/check_url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
    });
    const result = await response.json();
    if (result.is_safe) {
        message.textContent = `安全なURLです: ${url}`;
        message.style.color = "green";
    } else {
        message.textContent = `危険なURLです: ${url}`;
        message.style.color = "red";
    }
}

// カメラ起動を開始
startCamera();
