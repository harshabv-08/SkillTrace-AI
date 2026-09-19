document.addEventListener("DOMContentLoaded", () => {

    const fileInput = document.getElementById("resumeFile");
    const uploadZone = document.getElementById("uploadZone");
    const fileName = document.getElementById("fileName");
    const analysisForm = document.getElementById("analysisForm");
    const analyzeButton = document.getElementById("analyzeButton");


    // -----------------------------------------
    // File selection
    // -----------------------------------------

    if (fileInput && fileName) {

        fileInput.addEventListener("change", () => {

            if (fileInput.files.length > 0) {

                const file = fileInput.files[0];

                fileName.textContent = `Selected: ${file.name}`;

                if (uploadZone) {
                    uploadZone.classList.add("dragover");
                }
            }

        });

    }


    // -----------------------------------------
    // Drag and drop
    // -----------------------------------------

    if (uploadZone && fileInput) {

        ["dragenter", "dragover"].forEach(eventName => {

            uploadZone.addEventListener(eventName, event => {

                event.preventDefault();
                event.stopPropagation();

                uploadZone.classList.add("dragover");

            });

        });


        ["dragleave", "drop"].forEach(eventName => {

            uploadZone.addEventListener(eventName, event => {

                event.preventDefault();
                event.stopPropagation();

                uploadZone.classList.remove("dragover");

            });

        });


        uploadZone.addEventListener("drop", event => {

            const files = event.dataTransfer.files;

            if (files.length > 0) {

                fileInput.files = files;

                fileName.textContent =
                    `Selected: ${files[0].name}`;

            }

        });

    }


    // -----------------------------------------
    // Form submission
    // -----------------------------------------

    if (analysisForm) {

        analysisForm.addEventListener("submit", event => {

            const hasFile =
                fileInput &&
                fileInput.files &&
                fileInput.files.length > 0;

            const resumeText =
                document.getElementById("resumeText");

            const hasText =
                resumeText &&
                resumeText.value.trim().length > 0;


            if (!hasFile && !hasText) {

                event.preventDefault();

                alert(
                    "Please upload a resume or paste your resume text."
                );

                return;
            }


            if (analyzeButton) {

                analyzeButton.disabled = true;

                analyzeButton.textContent =
                    "Analyzing your resume...";

            }

        });

    }

});