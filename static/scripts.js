const video = document.getElementById('video');
const canvas = document.createElement('canvas');
const context = canvas.getContext('2d', { willReadFrequently: true });
const message = document.getElementById('message');

// カメラの起動
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' } // 背面カメラを優先
        });
        video.srcObject = stream;
        video.play();

        video.addEventListener('loadedmetadata', () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            scanQRCode(); // QRコードのスキャンを開始
        });
    } catch (err) {
        console.error("カメラエラー:", err);
        if (err.name === 'NotAllowedError') {
            message.textContent = "カメラのアクセスが拒否されました。ブラウザの設定を確認してください。";
        } else if (err.name === 'NotFoundError') {
            message.textContent = "カメラが見つかりませんでした。デバイスにカメラが接続されているか確認してください。";
        } else {
            message.textContent = "カメラの起動中にエラーが発生しました。";
        }
        message.style.color = "red";
    }
}

// QRコードスキャン処理
function scanQRCode() {
    try {
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
    } catch (err) {
        console.error("QRコードスキャンエラー:", err);
        message.textContent = "QRコードのスキャン中にエラーが発生しました。";
        message.style.color = "red";
    }
}

// カメラ起動を開始
startCamera();
