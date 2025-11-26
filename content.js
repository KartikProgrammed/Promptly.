let loadingBadge = null;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "loading") {
        showLoadingIndicator();
    } 
    else if (request.action === "replace_text") {
        removeLoadingIndicator();
        replaceSelectedText(request.text);
    } 
    else if (request.action === "error") {
        removeLoadingIndicator();
        alert(request.message);
    }
});

// --- UI Functions ---

function showLoadingIndicator() {
    // Prevent duplicate badges
    if (loadingBadge) return;

    loadingBadge = document.createElement("div");
    loadingBadge.innerText = "Promptly: Rewriting... ⏳";
    
    // Style the badge to float in the bottom-right corner
    Object.assign(loadingBadge.style, {
        position: "fixed",
        bottom: "20px",
        right: "20px",
        padding: "10px 20px",
        backgroundColor: "#0078d7",
        color: "#ffffff",
        borderRadius: "8px",
        fontFamily: "Segoe UI, sans-serif",
        fontSize: "14px",
        boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
        zIndex: "10000",
        opacity: "0",
        transition: "opacity 0.3s ease",
        pointerEvents: "none" // Click-through so it doesn't block UI
    });

    document.body.appendChild(loadingBadge);
    
    // Trigger fade in
    setTimeout(() => {
        if(loadingBadge) loadingBadge.style.opacity = "1";
    }, 10);
}

function removeLoadingIndicator() {
    if (loadingBadge) {
        loadingBadge.style.opacity = "0";
        setTimeout(() => {
            if (loadingBadge && loadingBadge.parentNode) {
                loadingBadge.parentNode.removeChild(loadingBadge);
            }
            loadingBadge = null;
        }, 300); // Wait for fade out
    }
}

// --- Text Replacement Logic ---

function replaceSelectedText(replacementText) {
    const activeElement = document.activeElement;

    // Check if we are in a standard Input or Textarea
    const isInput = activeElement && (activeElement.tagName === "INPUT" || activeElement.tagName === "TEXTAREA");

    if (isInput) {
        // Handle Standard Inputs
        const start = activeElement.selectionStart;
        const end = activeElement.selectionEnd;
        const text = activeElement.value;

        activeElement.value = text.slice(0, start) + replacementText + text.slice(end);
        activeElement.selectionStart = activeElement.selectionEnd = start + replacementText.length;
    } else {
        // Handle ContentEditable (Divs like ChatGPT) using Modern Range API
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            
            // 1. Delete selected text
            range.deleteContents();
            
            // 2. Create a text node and insert it
            const textNode = document.createTextNode(replacementText);
            range.insertNode(textNode);

            // 3. Move cursor to the end of the inserted text
            range.setStartAfter(textNode);
            range.setEndAfter(textNode);
            selection.removeAllRanges();
            selection.addRange(range);
        }
    }

    // CRITICAL: Fire the 'input' event immediately.
    // Without this, ChatGPT won't know the text changed and the "Send" button might stay gray.
    activeElement.dispatchEvent(new Event('input', { bubbles: true }));
}