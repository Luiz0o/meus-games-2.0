document.addEventListener("DOMContentLoaded", function() {
    // ==================== 1. CONTROLE DAS ESTRELAS DE AVALIAÇÃO ====================
    const stars = document.querySelectorAll('.star');
    const ratingValue = document.getElementById('rating-value');

    stars.forEach(star => {
        star.addEventListener('click', () => {
            const val = star.getAttribute('data-value');
            if (ratingValue) ratingValue.value = val;

            stars.forEach(s => {
                const sVal = s.getAttribute('data-value');
                if (parseInt(sVal) <= parseInt(val)) {
                    s.classList.remove('fa-regular');
                    s.classList.add('fa-solid');
                } else {
                    s.classList.remove('fa-solid');
                    s.classList.add('fa-regular');
                }
            });
        });
    });

    // ==================== 2. ELEMENTOS DO DRAG AND DROP (SUPORTE CADASTRO/EDIÇÃO) ====================
    const dropZone = document.getElementById("drop-zone");
    const coverInput = document.getElementById("cover-input");
    
    // Mapeia os IDs aceitando as variações que usamos nos dois templates HTML
    const prompt = document.getElementById("drop-zone-prompt") || document.getElementById("drop-prompt");
    const previewContainer = document.getElementById("preview-container");
    const previewImage = document.getElementById("cover-preview") || document.getElementById("preview-img");
    const removeBtn = document.getElementById("remove-preview") || document.getElementById("btn-remove-preview");

    // Aborta se os elementos vitais não estiverem na página atual
    if (!dropZone || !coverInput) return;

    // Abrir seleção ao clicar no container da dropzone
    dropZone.addEventListener("click", (e) => {
        // Se clicar no botão remover ou em algo dentro dele, não dispara a seleção de arquivos
        if (e.target.id === 'remove-preview' || e.target.id === 'btn-remove-preview' || e.target.closest("#remove-preview") || e.target.closest("#btn-remove-preview")) return;
        coverInput.click();
    });

    // Eventos visuais do arrasto de arquivos
    ["dragover", "dragleave", "drop"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => e.preventDefault());
    });

    dropZone.addEventListener("dragover", () => dropZone.classList.add("drag-over"));
    ["dragleave", "drop"].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove("drag-over"));
    });

    // Evento ao soltar a imagem na caixa
    dropZone.addEventListener("drop", (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type.startsWith("image/")) {
            coverInput.files = files;
            showPreview(files[0]);
        }
    });

    // Evento ao escolher manualmente pelo seletor do sistema
    coverInput.addEventListener("change", () => {
        if (coverInput.files.length > 0) {
            showPreview(coverInput.files[0]);
        }
    });

    function showPreview(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            if (previewImage) previewImage.src = e.target.result;
            if (prompt) prompt.classList.add("hidden");
            if (previewContainer) previewContainer.classList.remove("hidden");
            dropZone.style.borderStyle = "solid";
        }
        reader.readAsDataURL(file);
    }

    // Ação do Botão remover (se ele existir na tela)
    if (removeBtn) {
        removeBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            coverInput.value = "";
            if (previewImage) previewImage.src = "#";
            if (previewContainer) previewContainer.classList.add("hidden");
            if (prompt) prompt.classList.remove("hidden");
            dropZone.style.borderStyle = "dashed";
        });
    }
});