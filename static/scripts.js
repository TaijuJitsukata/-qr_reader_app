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
        message.innerHTML = "❌ <span style='color: red;'>カメラを起動できませんでした。</span>";
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
                console.log("🔍 QRコード検出:", qrText); // デバッグ用
                message.innerHTML = `🔍 QRコード検出: <a href="${qrText}" target="_blank">${qrText}</a>`;
                checkURLSafety(qrText);
            } else {
                message.innerHTML = "📷 <span style='color: gray;'>QRコードをスキャン中...</span>";
            }
        }
        requestAnimationFrame(detectQRCode);
    }

    detectQRCode();
}

// URLの安全性をチェック
async function checkURLSafety(url) {
    try {
        console.log("🔍 チェックするURL:", url);  // デバッグ用

        const response = await fetch('/check_url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        if (!response.ok) {
            console.error("🚨 サーバーレスポンスがエラー:", response.status);
            message.innerHTML = `❌ <span style='color: red;'>サーバーエラー: ${response.status}</span>`;
            return;
        }

        const result = await response.json();
        console.log("🔍 サーバーからのレスポンス:", result);  // デバッグ用

        // UIに判別結果を反映
        if (result.is_safe === false) {
            document.body.style.backgroundColor = "rgba(255, 0, 0, 0.2)"; // 背景を赤系に
            message.innerHTML = `⚠️ <span style="color: red; font-size: 20px;">危険なURLです！</span> <br> 
                <strong>理由:</strong> ${result.reasons.join(', ')}<br>
                <a href="${url}" target="_blank">${url}</a>`;
        } else if (result.is_safe === true) {
            document.body.style.backgroundColor = "rgba(0, 255, 0, 0.2)"; // 背景を緑系に
            message.innerHTML = `✅ <span style="color: green; font-size: 20px;">安全なURLです。</span><br> 
                <a href="${url}" target="_blank">${url}</a>`;
        } else {
            document.body.style.backgroundColor = "rgba(255, 255, 0, 0.2)"; // 背景を黄色系に
            message.innerHTML = `❌ <span style="color: orange;">URLの安全性を確認できませんでした。</span> <br> 
                <strong>理由:</strong> ${result.reasons.join(', ')}<br> 
                <a href="${url}" target="_blank">${url}</a>`;
        }
    } catch (error) {
        console.error("🚨 サーバーとの通信エラー:", error);
        message.innerHTML = "❌ <span style='color: red;'>サーバーエラーが発生しました。</span>";
    }
}

// カメラを起動
startCamera();
