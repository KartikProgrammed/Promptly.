// Create the Context Menu item
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "promptly-rewrite",
        title: "⚡ Promptly Rewrite",
        contexts: ["selection"]
    });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    if (info.menuItemId === "promptly-rewrite" && info.selectionText) {
        
        // 1. Tell content script to show "Loading..."
        chrome.tabs.sendMessage(tab.id, { action: "loading" });

        try {
            // 2. Call your Flask API
            const response = await fetch("https://promptly-orcin.vercel.app/rewrite", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: info.selectionText })
            });

            if (!response.ok) throw new Error("API Error");

            const data = await response.json();
            const improvedText = data.improved_prompt;

            // 3. Send result to content script
            if (improvedText) {
                chrome.tabs.sendMessage(tab.id, {
                    action: "replace_text",
                    text: improvedText
                });
            }

        } catch (error) {
            console.error("Promptly Error:", error);
            chrome.tabs.sendMessage(tab.id, {
                action: "error",
                message: "Could not refine prompt. Check server."
            });
        }
    }
});     