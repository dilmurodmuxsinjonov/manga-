let currentSessionId = null;
let currentWidth = 800;
let currentHeight = 1150;
let originalImageB64 = null;
let cleanedImageB64 = null;
let finalImageB64 = null;
let bubbles = [];
let selectedBubbleId = null;
let currentViewMode = "final"; // 'original', 'cleaned', 'final'

const mangaImage = document.getElementById("manga-image");
const bubbleOverlay = document.getElementById("bubble-overlay");
const bubbleDetailCard = document.getElementById("bubble-detail-card");
const bubbleIdSpan = document.getElementById("bubble-id-span");
const rawTextInput = document.getElementById("raw-text-input");
const uzbekTextInput = document.getElementById("uzbek-text-input");
const isSfxCheckbox = document.getElementById("is-sfx-checkbox");
const globalGenreSelect = document.getElementById("global-genre");
const translateAllBtn = document.getElementById("translate-all-btn");
const rerenderBtn = document.getElementById("rerender-btn");
const downloadBtn = document.getElementById("download-btn");
const fileInput = document.getElementById("file-input");

// Dastlab namunani yuklash
window.addEventListener("DOMContentLoaded", () => {
    loadSample();
});

async function loadSample() {
    try {
        translateAllBtn.innerHTML = '<span class="loading-spinner"></span> Namunani yuklash...';
        const res = await fetch("/api/sample");
        const data = await res.json();
        
        currentSessionId = data.session_id;
        currentWidth = data.width;
        currentHeight = data.height;
        originalImageB64 = data.image_base64;
        bubbles = data.bubbles || [];

        // Boshlang'ich tarjimani ishga tushiramiz
        await runTranslation();
    } catch (e) {
        console.error("Namunani yuklashda xatolik:", e);
    } finally {
        translateAllBtn.innerHTML = '⚡ Mazmunli Tarjima Qilish';
    }
}

async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    translateAllBtn.innerHTML = '<span class="loading-spinner"></span> Yuklanmoqda...';
    try {
        const res = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });
        const data = await res.json();

        currentSessionId = data.session_id;
        currentWidth = data.width;
        currentHeight = data.height;
        originalImageB64 = data.image_base64;
        cleanedImageB64 = null;
        finalImageB64 = null;
        bubbles = data.bubbles || [];
        selectedBubbleId = null;

        renderView("original");
        renderBubbleBoxes();

        // Avtomatik ravishda to'liq tarjima qilish
        await runTranslation();
    } catch (e) {
        alert("Faylni yuklashda xatolik yuz berdi: " + e.message);
    } finally {
        translateAllBtn.innerHTML = '⚡ Mazmunli Tarjima Qilish';
    }
}

async function runTranslation() {
    if (!currentSessionId) return;

    translateAllBtn.disabled = true;
    translateAllBtn.innerHTML = '<span class="loading-spinner"></span> Mazmunli tarjima qilinmoqda...';

    try {
        const payload = {
            session_id: currentSessionId,
            genre: globalGenreSelect.value,
            bubbles: bubbles
        };

        const res = await fetch("/api/translate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        cleanedImageB64 = data.cleaned_image;
        finalImageB64 = data.final_image;
        bubbles = data.bubbles || [];

        renderView("final");
        renderBubbleBoxes();
        
        if (selectedBubbleId) {
            selectBubble(selectedBubbleId);
        }
    } catch (e) {
        alert("Tarjima jarayonida xatolik: " + e.message);
    } finally {
        translateAllBtn.disabled = false;
        translateAllBtn.innerHTML = '⚡ Mazmunli Tarjima Qilish';
    }
}

async function handleRerender() {
    if (!currentSessionId) return;

    // Tanlangan pufakcha qiymatlarini saqlash
    if (selectedBubbleId) {
        const bubble = bubbles.find(b => b.id === selectedBubbleId);
        if (bubble) {
            bubble.text_raw = rawTextInput.value;
            bubble.text_uz = uzbekTextInput.value;
            bubble.is_sfx = isSfxCheckbox.checked;
        }
    }

    rerenderBtn.innerHTML = '<span class="loading-spinner"></span> Shriftlanmoqda...';
    try {
        const payload = {
            session_id: currentSessionId,
            genre: globalGenreSelect.value,
            bubbles: bubbles
        };

        const res = await fetch("/api/re-render", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        finalImageB64 = data.final_image;
        renderView("final");
    } catch (e) {
        console.error("Qayta chizish xatosi:", e);
    } finally {
        rerenderBtn.innerHTML = '🎨 Shriftni Qayta Chizish';
    }
}

function renderView(mode) {
    currentViewMode = mode;
    document.querySelectorAll(".view-btn").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.mode === mode);
    });

    if (mode === "original" && originalImageB64) {
        mangaImage.src = originalImageB64;
    } else if (mode === "cleaned" && cleanedImageB64) {
        mangaImage.src = cleanedImageB64;
    } else if (mode === "final" && finalImageB64) {
        mangaImage.src = finalImageB64;
    } else if (originalImageB64) {
        mangaImage.src = originalImageB64;
    }
}

function renderBubbleBoxes() {
    bubbleOverlay.innerHTML = "";
    if (!bubbles || bubbles.length === 0) return;

    bubbles.forEach(b => {
        const box = document.createElement("div");
        box.className = `bubble-rect ${selectedBubbleId === b.id ? "selected" : ""}`;
        
        // Foizlarda joylashtirish (responsivlik uchun)
        const leftPct = (b.x / currentWidth) * 100;
        const topPct = (b.y / currentHeight) * 100;
        const widthPct = (b.w / currentWidth) * 100;
        const heightPct = (b.h / currentHeight) * 100;

        box.style.left = `${leftPct}%`;
        box.style.top = `${topPct}%`;
        box.style.width = `${widthPct}%`;
        box.style.height = `${heightPct}%`;

        box.innerHTML = `<span class="bubble-num">${b.id}</span>`;
        box.onclick = (e) => {
            e.stopPropagation();
            selectBubble(b.id);
        };

        bubbleOverlay.appendChild(box);
    });
}

function selectBubble(id) {
    selectedBubbleId = id;
    renderBubbleBoxes();

    const bubble = bubbles.find(b => b.id === id);
    if (!bubble) return;

    bubbleDetailCard.style.display = "flex";
    bubbleIdSpan.textContent = `#${bubble.id}`;
    rawTextInput.value = bubble.text_raw || "";
    uzbekTextInput.value = bubble.text_uz || "";
    isSfxCheckbox.checked = !!bubble.is_sfx;
}

function triggerDownload() {
    if (!currentSessionId) return;
    window.location.href = `/api/download/${currentSessionId}`;
}

// Event Listeners
document.querySelectorAll(".view-btn").forEach(btn => {
    btn.onclick = () => renderView(btn.dataset.mode);
});

translateAllBtn.onclick = runTranslation;
rerenderBtn.onclick = handleRerender;
downloadBtn.onclick = triggerDownload;
fileInput.onchange = handleFileUpload;
