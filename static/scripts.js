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
        requestAnimation
