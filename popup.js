const promptInput = document.getElementById("promptInput");
const modeSelect = document.getElementById("modeSelect");
const sendBtn = document.getElementById("sendBtn");
const responseBox = document.getElementById("responseContainer");
const imageArea = document.getElementById("imageArea");
const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("preview");

let selectedImage = null;

// Allow clicking the image area to choose file
imageArea.addEventListener("click", () => imageInput.click());

// Handle manual file selection
imageInput.addEventListener("change", (e) => {
  if (e.target.files && e.target.files[0]) {
    selectedImage = e.target.files[0];
    showPreview(selectedImage);
  }
});

// Handle image paste (Ctrl+V)
document.addEventListener("paste", (e) => {
  const items = e.clipboardData?.items;
  if (!items) return;

  for (const item of items) {
    if (item.type.indexOf("image") !== -1) {
      const file = item.getAsFile();
      selectedImage = file;
      showPreview(file);
      break;
    }
  }
});

// Show preview image
function showPreview(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    preview.src = e.target.result;
    preview.style.display = "block";
    document.getElementById("imageText").innerText = "✅ Image ready to send";
  };
  reader.readAsDataURL(file);
}

// Handle prompt submission
sendBtn.addEventListener("click", async () => {
  const prompt = promptInput.value.trim();
  const mode = modeSelect.value;

  if (!prompt) {
    responseBox.innerText = "Please enter a prompt first.";
    return;
  }

  responseBox.innerText = "Processing... ⏳";

  try {
    let res;
    if (selectedImage) {
      // If an image is selected, send as multipart/form-data
      const formData = new FormData();
      formData.append("prompt", prompt);
      formData.append("image", selectedImage);

      res = await fetch(`https://promptly-orcin.vercel.app/${mode}`, {
        method: "POST",
        body: formData
      });
    } else {
      // Text-only prompt
      res = await fetch(`https://promptly-orcin.vercel.app/${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
      });
    }

    const data = await res.json();
    const keyName = Object.keys(data)[0];
    responseBox.innerText = data[keyName] || "No response received.";
  } catch (error) {
    responseBox.innerText = "Error: " + error.message;
  }
});
