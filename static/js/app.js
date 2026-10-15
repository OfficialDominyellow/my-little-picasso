document.addEventListener("DOMContentLoaded", () => {
    // DOM 요소 참조
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const uploadPlaceholder = document.getElementById("uploadPlaceholder");
    const previewWrapper = document.getElementById("previewWrapper");
    const photoPreview = document.getElementById("photoPreview");
    const btnChangePhoto = document.getElementById("btnChangePhoto");

    const selectLang = document.getElementById("selectLang");
    const selectLength = document.getElementById("selectLength");
    const inputNotes = document.getElementById("inputNotes");
    const btnGenerate = document.getElementById("btnGenerate");
    const loadingState = document.getElementById("loadingState");

    const editSection = document.getElementById("editSection");
    const editDate = document.getElementById("editDate");
    const editWeather = document.getElementById("editWeather");
    const editTitle = document.getElementById("editTitle");
    const editContent = document.getElementById("editContent");
    const charCount = document.getElementById("charCount");
    const btnUpdatePreview = document.getElementById("btnUpdatePreview");

    const emptyState = document.getElementById("emptyState");
    const renderedImageBox = document.getElementById("renderedImageBox");
    const renderedImage = document.getElementById("renderedImage");
    const renderLoading = document.getElementById("renderLoading");
    const btnDownload = document.getElementById("btnDownload");
    const btnReset = document.getElementById("btnReset");
    const toast = document.getElementById("toast");

    let currentFile = null;
    let currentRenderBlobUrl = null;

    // 1. 오늘 날짜 기본값 설정 (한국어 형식)
    function getTodayFormatted() {
        const now = new Date();
        const year = now.getFullYear();
        const month = now.getMonth() + 1;
        const date = now.getDate();
        const days = ["일", "월", "화", "수", "목", "금", "토"];
        const day = days[now.getDay()];
        return `${year}년 ${month}월 ${date}일 ${day}요일`;
    }
    editDate.value = getTodayFormatted();

    // 2. 토스트 메시지 함수
    function showToast(message, isError = false) {
        toast.textContent = message;
        toast.className = isError ? "toast show error" : "toast show";
        setTimeout(() => {
            toast.className = "toast";
        }, 3500);
    }

    // 3. 파일 선택 및 드래그 앤 드롭 핸들링
    dropZone.addEventListener("click", (e) => {
        if (e.target !== btnChangePhoto) {
            fileInput.click();
        }
    });

    btnChangePhoto.addEventListener("click", (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            handleSelectedFile(e.target.files[0]);
        }
    });

    ["dragenter", "dragover"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add("dragover");
        });
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove("dragover");
        });
    });

    dropZone.addEventListener("drop", (e) => {
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleSelectedFile(e.dataTransfer.files[0]);
        }
    });

    function handleSelectedFile(file) {
        if (!file.type.startsWith("image/")) {
            showToast("이미지 파일(JPG, PNG, WEBP)만 업로드할 수 있습니다.", true);
            return;
        }

        if (file.size > 15 * 1024 * 1024) {
            showToast("파일 크기가 15MB를 초과할 수 없습니다.", true);
            return;
        }

        currentFile = file;

        const reader = new FileReader();
        reader.onload = (e) => {
            photoPreview.src = e.target.result;
            uploadPlaceholder.style.display = "none";
            previewWrapper.style.display = "block";
            btnGenerate.disabled = false;
        };
        reader.readAsDataURL(file);
    }

    // 4. 글자 수 카운터
    editContent.addEventListener("input", () => {
        const len = editContent.value.length;
        charCount.textContent = `${len} / 84자 권장 (원고지 규격)`;
        if (len > 84) {
            charCount.style.color = "#e63946";
        } else {
            charCount.style.color = "#94a3b8";
        }
    });

    // 5. AI 그림일기 생성 요청
    btnGenerate.addEventListener("click", async () => {
        if (!currentFile) {
            showToast("먼저 사진을 등록해주세요.", true);
            return;
        }

        btnGenerate.disabled = true;
        loadingState.style.display = "block";
        emptyState.style.display = "none";
        renderLoading.style.display = "block";

        const formData = new FormData();
        formData.append("file", currentFile);
        formData.append("language", selectLang.value);
        formData.append("length", selectLength.value);
        if (inputNotes.value.trim()) {
            formData.append("notes", inputNotes.value.trim());
        }

        try {
            const response = await fetch("/api/generate-diary", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "일기 생성 중 오류가 발생했습니다.");
            }

            const data = await response.json();

            // 편집 영역에 값 세팅
            editTitle.value = data.title;
            editContent.value = data.diary_text;
            editSection.style.display = "block";
            charCount.textContent = `${data.diary_text.length} / 84자 권장 (원고지 규격)`;

            // 템플릿 합성 렌더링 호출
            await requestRenderTemplate();
            showToast("🎉 귀여운 그림일기가 완성되었습니다!");

        } catch (err) {
            console.error("AI 생성 실패:", err);
            showToast(err.message, true);
            renderLoading.style.display = "none";
            if (!currentRenderBlobUrl) {
                emptyState.style.display = "block";
            }
        } finally {
            btnGenerate.disabled = false;
            loadingState.style.display = "none";
        }
    });

    // 6. 템플릿 렌더링 API 요청 함수
    async function requestRenderTemplate() {
        renderLoading.style.display = "block";
        renderedImageBox.style.display = "none";
        emptyState.style.display = "none";

        const renderForm = new FormData();
        renderForm.append("title", editTitle.value.trim() || "오늘의 일기");
        renderForm.append("date_str", editDate.value.trim() || getTodayFormatted());
        renderForm.append("weather", editWeather.value);
        renderForm.append("content", editContent.value);

        if (currentFile) {
            renderForm.append("file", currentFile);
        }

        try {
            const resp = await fetch("/api/render-template", {
                method: "POST",
                body: renderForm,
            });

            if (!resp.ok) {
                const errData = await resp.json();
                throw new Error(errData.detail || "템플릿 합성 중 오류가 발생했습니다.");
            }

            const blob = await resp.blob();
            if (currentRenderBlobUrl) {
                URL.revokeObjectURL(currentRenderBlobUrl);
            }
            currentRenderBlobUrl = URL.createObjectURL(blob);

            renderedImage.src = currentRenderBlobUrl;
            renderedImageBox.style.display = "block";
            btnDownload.disabled = false;

        } catch (err) {
            console.error("렌더링 실패:", err);
            showToast("템플릿 렌더링 실패: " + err.message, true);
        } finally {
            renderLoading.style.display = "none";
        }
    }

    // 7. 템플릿에 수정사항 반영하기 버튼 클릭
    btnUpdatePreview.addEventListener("click", async () => {
        btnUpdatePreview.disabled = true;
        try {
            await requestRenderTemplate();
            showToast("수정된 내용이 템플릿에 반영되었습니다.");
        } finally {
            btnUpdatePreview.disabled = false;
        }
    });

    // 8. PNG 다운로드 핸들링
    btnDownload.addEventListener("click", () => {
        if (!currentRenderBlobUrl) {
            showToast("다운로드할 이미지가 없습니다.", true);
            return;
        }

        const now = new Date();
        const pad = (n) => String(n).padStart(2, "0");
        const filename = `그림일기_${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}.png`;

        const a = document.createElement("a");
        a.href = currentRenderBlobUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        showToast("그림일기 PNG 다운로드를 시작했습니다!");
    });

    // 9. 다시 만들기 (초기화)
    btnReset.addEventListener("click", () => {
        if (!confirm("지금까지 작업한 내용을 초기화하고 다시 시작할까요?")) {
            return;
        }

        currentFile = null;
        if (currentRenderBlobUrl) {
            URL.revokeObjectURL(currentRenderBlobUrl);
            currentRenderBlobUrl = null;
        }

        fileInput.value = "";
        photoPreview.src = "";
        uploadPlaceholder.style.display = "flex";
        previewWrapper.style.display = "none";
        btnGenerate.disabled = true;

        inputNotes.value = "";
        selectLang.value = "ko";
        selectLength.value = "short";

        editSection.style.display = "none";
        editTitle.value = "";
        editContent.value = "";
        editDate.value = getTodayFormatted();
        editWeather.value = "맑음";

        renderedImage.src = "";
        renderedImageBox.style.display = "none";
        renderLoading.style.display = "none";
        emptyState.style.display = "block";
        btnDownload.disabled = true;

        showToast("초기화되었습니다. 새로운 사진을 등록해주세요.");
    });
});

