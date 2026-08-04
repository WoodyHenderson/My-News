/*
THIS IS THE BRIDGE BETWEEN THE HTML/JS GENERATED OUTPUT AND THE PYTHON BACKEND
IF YOU WANT THIS STUFF TO WORK, DO NOT GOD DAMN TOUCH THIS FILE, IT IS AUTOMATICALLY
COPIED FROM THE SOURCE CODE TO THE GENERATED OUTPUT FOLDER WHEN THE APP RUNS.
*/

let pyBridge = null;

if (window.qt && window.QWebChannel) {
    new QWebChannel(qt.webChannelTransport, (channel) => {
        pyBridge = channel.objects.pyBridge;
    });
}

async function markSeenInFuturePython(url) {
    return new Promise((resolve) => {
        if (!pyBridge) {
            resolve({ ok: false });
            return;
        }
        pyBridge.markSeen(url, (inserted) => {
            resolve({ ok: Boolean(inserted) });
        });
    });
}

document.addEventListener("click", async (event) => {
    const button = event.target.closest(".mark-seen-button");
    if (!button) return;

    const url = button.dataset.url;
    if (!url) return;

    button.disabled = true;
    button.textContent = "Saving...";

    try {
        const result = await markSeenInFuturePython(url);
        if (result && result.ok) {
        button.textContent = "Seen";
        } else {
        button.disabled = false;
        button.textContent = "Mark as seen";
        }
    } catch (error) {
        button.disabled = false;
        button.textContent = "Mark as seen";
        console.error(error);
    }
});