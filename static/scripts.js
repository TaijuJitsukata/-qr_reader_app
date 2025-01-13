const video = document.getElementById('video');
const canvas = document.createElement('canvas');
const context = canvas.getContext('2d', { willReadFrequently: true });
const message = document.getElementById('message');

// カメラの起動
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' }
        });
        video.srcObject = stream;
        video.play();

        video.addEventListener('loadedmetadata', () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            scanQRCode();
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
        checkURLSafety(qrText); // URLの安全性を確認
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
            message.style.color = "green"; // 安全なURLは緑色
        } else if (result.is_safe === false) {
            // 危険なURLの理由を表示
            const reasons = result.reasons.join(', ');
            message.innerHTML = `危険なURLです: ${url}<br>理由: ${reasons}`;
            message.style.color = "red"; // 危険なURLは赤色
        } else {
            message.textContent = result.message;
            message.style.color = "orange"; // エラー時はオレンジ色
        }
    } catch (error) {
        console.error("APIエラー:", error);
        message.textContent = "URLの安全性確認中にエラーが発生しました。";
        message.style.color = "red";
    }
}

// カメラ起動を開始
startCamera();
