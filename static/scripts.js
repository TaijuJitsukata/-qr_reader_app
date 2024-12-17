const video = document.getElementById('video');
const canvas = document.createElement('canvas'); // 非表示のcanvasを作成
const context = canvas.getContext('2d', { willReadFrequently: true }); // パフォーマンス改善
const message = document.getElementById('message');

// カメラの起動
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' }  // 背面カメラ
        });
        video.srcObject = stream;
        video.play();

        video.addEventListener('loadedmetadata', () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            scanQRCode(); // QRコードスキャン開始
        });
    } catch (err) {
        message.textContent = "カメラのアクセスが拒否されました。";
        message.style.color = "red";
        console.error("カメラエラー:", err);
    }
}

// QRコードスキャン処理
function scanQRCode() {
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    const qrCode = jsQR(imageData.data, imageData.width, imageData.height);

    if (qrCode) {
        const qrText = qrCode.data;
        message.textContent = `QRコード検出: ${qrText}`;
        message.style.color = "blue";
        checkURLSafety(qrText);
    } else {
        message.textContent = "QRコードをスキャン中...";
        message.style.color = "#333";
    }

    requestAnimationFrame(scanQRCode); // スキャンを継続
}

// URLの安全性を確認する
async function checkURLSafety(url) {
    try {
        const response = await fetch('/check_url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        const result = await response.json();

        if (result.is_safe === true) {
            message.textContent = `安全なURLです: ${url}`;
            message.style.color = "green";
        } else if (result.is_safe === false) {
            message.textContent = `危険なURLです: ${url}`;
            message.style.color = "red";
        } else {
            message.textContent = "URLの安全性を確認できませんでした。";
            message.style.color = "orange";
        }
    } catch (error) {
        console.error("APIエラー:", error);
        message.textContent = "URLの安全性確認中にエラーが発生しました。";
        message.style.color = "red";
    }
}

// カメラ起動を開始
startCamera();
