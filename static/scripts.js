async function checkURLSafety(url) {
    try {
        const response = await fetch('/check_url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        const result = await response.json();

        console.log("APIレスポンス:", result); // デバッグ用
        const checkedUrl = result.checked_url || url;

        if (result.is_safe === true) {
            message.innerHTML = `安全なURLです: <a href="${checkedUrl}" target="_blank">${checkedUrl}</a>`;
            message.style.color = "green";
        } else if (result.is_safe === false) {
            const reasons = result.reasons.join(', ');
            message.innerHTML = `危険なURLです: <a href="${checkedUrl}" target="_blank">${checkedUrl}</a><br>理由: ${reasons}`;
            message.style.color = "red";
        } else {
            const reasons = result.reasons.join(', ') || "理由が特定できません。";
            message.innerHTML = `URLの安全性を確認できませんでした。<br>理由: ${reasons}`;
            message.style.color = "orange";
        }
    } catch (error) {
        console.error("フロントエンドAPIエラー:", error);
        message.textContent = "URLの安全性確認中にエラーが発生しました。";
        message.style.color = "red";
    }
}
