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
            scanQRCode(); // QRコードのスキャンを開始
        });

        message.textContent = "カメラが起動しました。QRコードを読み取ってください。";
        message.style.color = "green";
    } catch (err) {
        console.error("カメラエラー:", err);
        message.textContent = "カメラの起動中にエラーが発生しました。";
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
            checkURLSafety(qrText);
        } else {
            message.textContent = "QRコードをスキャン中...";
            message.style.color = "#333";
        }

        requestAnimationFrame(scanQRCode);
    } catch (err) {
        console.error("QRコードスキャンエラー:", err);
        message.textContent = "QRコードのスキャン中にエラーが発生しました。";
        message.style.color = "red";
    }
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
            message.innerHTML = `安全なURLです: <a href="${url}" target="_blank">${url}</a>`;
            message.style.color = "green";
        } else if (result.is_safe === false) {
            const reasons = result.reasons.join(', ');
            message.innerHTML = `危険なURLです: ${url}<br>理由: ${reasons}`;
            message.style.color = "red";
        } else {
            const reasons = result.reasons.join(', ') || "理由が特定できません。";
            message.innerHTML = `URLの安全性を確認できませんでした。<br>理由: ${reasons}`;
            message.style.color = "orange";
        }
    } catch (err) {
        console.error("APIエラー:", err);
        message.textContent = "URLの安全性確認中にエラーが発生しました。";
        message.style.color = "red";
    }
}

// カメラ起動を開始
startCamera();
