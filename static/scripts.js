const video = document.getElementById('video');
const message = document.getElementById('message');

// カメラの起動
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
        video.srcObject = stream;
        video.play();
        scanQRCode();
    } catch (error) {
        console.error("🚨 カメラのアクセスに失敗しました:", error);
        message.textContent = "❌ カメラを起動できませんでした。";
        message.style.color = "red";
    }
}

// QRコードのスキャン
function scanQRCode() {
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");

    function detectQRCode() {
        if (video.readyState === video.HAVE_ENOUGH_DATA) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
            const qrCode = jsQR(imageData.data, imageData.width, imageData.height);

            if (qrCode) {
                const qrText = qrCode.data;
                message.innerHTML = `🔍 QRコード検出: <a href="${qrText}" target="_blank">${qrText}</a>`;
                checkURLSafety(qrText);
            }
        }
        requestAnimationFrame(detectQRCode);
    }

    detectQRCode();
}

// URLの安全性をチェック
async function checkURLSafety(url) {
    try {
        const response = await fetch('/check_url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        const result = await response.json();

        console.log("🔍 サーバーからのレスポンス:", result); // デバッグ用

        // 結果に応じてUIを変更
        if (result.is_safe === false) {
            message.innerHTML = `⚠️ <span style="color: red;">危険なURLです！</span> <br> 理由: ${result.reasons.join(', ')}<br>
                <a href="${url}" target="_blank">${url}</a>`;
        } else if (result.is_safe === true) {
            message.innerHTML = `✅ <span style="color: green;">安全なURLです。</span><br> 
                <a href="${url}" target="_blank">${url}</a>`;
        } else {
            message.innerHTML = `❌ <span style="color: orange;">URLの安全性を確認できませんでした。</span> 理由: ${result.reasons.join(', ')}<br> 
                <a href="${url}" target="_blank">${url}</a>`;
        }
    } catch (error) {
        console.error("🚨 サーバーとの通信エラー:", error);
        message.innerHTML = "❌ <span style='color: red;'>サーバーエラーが発生しました。</span>";
    }
}

// カメラを起動
startCamera();
