const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
const message = document.getElementById('message');

async function startCamera() {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
    video.srcObject = stream;
    video.play();
    scanQRCode();
}

function scanQRCode() {
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

    requestAnimationFrame(scanQRCode);
}

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

startCamera();
