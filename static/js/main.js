let video = document.getElementById("video");
let canvas = document.getElementById("canvas");
let previewImage = document.getElementById("preview-image");
let imageUpload = document.getElementById("image-upload");
let uploadLabel = document.getElementById("upload-label");
let historyTableBody = document.getElementById("history-table-body");

let capturedBlob = null;

/* ================================
   FILE UPLOAD PREVIEW
================================ */
if (imageUpload) {
    imageUpload.addEventListener("change", function (event) {
        let file = event.target.files[0];
        if (file) {
            uploadLabel.innerText = "📁 " + file.name;
            let reader = new FileReader();
            reader.onload = function (e) {
                video.style.display = "none";
                previewImage.src = e.target.result;
                previewImage.style.display = "block";
            };
            reader.readAsDataURL(file);
            capturedBlob = null;
        }
    });
}

/* ================================
   START WEBCAM (DROIDCAM PRIORITY)
================================ */
function startCamera() {
    previewImage.style.display = "none";
    video.style.display = "block";

    navigator.mediaDevices.enumerateDevices()
    .then(function(devices) {

        let droidCam = devices.find(device =>
            device.kind === "videoinput" &&
            device.label.toLowerCase().includes("droid")
        );

        let constraints;

        if (droidCam) {
            console.log("Using DroidCam:", droidCam.label);

            constraints = {
                video: {
                    deviceId: { exact: droidCam.deviceId },
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            };
        } else {
            console.log("DroidCam not found, using default webcam");

            constraints = {
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: "environment"
                }
            };
        }

        return navigator.mediaDevices.getUserMedia(constraints);
    })
    .then(function (stream) {
        video.srcObject = stream;
    })
    .catch(function (error) {
        alert("Cannot access webcam device peripheral tool.");
        console.log(error);
    });
}

/* ================================
   CAPTURE IMAGE FROM WEBCAM
================================ */
function captureImage() {
    if (!video.srcObject) {
        alert("Please boot active live video feed window first.");
        return;
    }

    let context = canvas.getContext("2d");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);

    video.style.display = "none";
    previewImage.src = canvas.toDataURL("image/png");
    previewImage.style.display = "block";

    canvas.toBlob(function (blob) {
        capturedBlob = blob;
    }, "image/png");
}

/* ================================
   SEND IMAGE TO BACKEND
================================ */
function detectCurrency() {
    let formData = new FormData();
    let uploadedFile = imageUpload.files[0];

    if (uploadedFile) {
        formData.append("image", uploadedFile);
    }
    else if (capturedBlob) {
        formData.append("image", capturedBlob, "captured.png");
    }
    else {
        alert("Please upload an image file asset or record a live camera scene snapshot.");
        return;
    }

    let resultBox = document.getElementById("result-box");
    let resultText = document.getElementById("result-text");
    let confidence = document.getElementById("confidence-score");
    let resultImage = document.getElementById("result-image");

    resultBox.style.display = "block";
    resultText.innerText = "Analyzing security markers and pattern maps...";
    resultText.className = "";
    confidence.innerText = "--%";
    resultImage.src = previewImage.src;

    fetch("/predict", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        confidence.innerText = data.confidence + "%";

        let isReal = (data.result === "Real" || data.result === "Real_500");

        if (isReal) {
            resultText.innerText = "REAL BANKNOTE";
            resultText.className = "real-text";
            resultBox.style.borderLeftColor = "#16a34a";
        } else {
            resultText.innerText = "COUNTERFEIT (FAKE) DETECTED";
            resultText.className = "fake-text";
            resultBox.style.borderLeftColor = "#dc2626";
        }

        resultBox.scrollIntoView({ behavior: 'smooth' });

        let rowId = data.id || Math.floor(Math.random() * 10000);
        let statusColor = isReal ? "#16a34a" : "#dc2626";

        let dynamicRowHTML = `
            <tr id="history-row-${rowId}">
                <td>${rowId}</td>
                <td style="color: #6b7280;">Just Now</td>
                <td><img src="${previewImage.src}" width="110" style="border-radius: 6px; border: 1px solid #cbd5e1; display: block; object-fit: contain; background: #f8fafc; max-height: 60px;"></td>
                <td><span style="font-weight: bold; color: ${statusColor};">${data.result}</span></td>
                <td><strong>${data.confidence}%</strong></td>
                <td><button style="background: #ef4444; color: white; border: none; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 13px;" onclick="deleteHistory(${rowId})">Delete</button></td>
            </tr>`;

        historyTableBody.insertAdjacentHTML('afterbegin', dynamicRowHTML);
    })
    .catch(error => {
        console.log(error);
        alert("Verification pipe failed to parse asset file.");
    });
}

/* ================================
   DELETE HISTORY ROW
================================ */
function deleteHistory(historyId) {
    fetch("/delete_history/" + historyId, {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            let row = document.getElementById("history-row-" + historyId);
            if (row) {
                row.remove();
            }
        }
        else {
            alert("Delete execution failure tracking target array item.");
        }
    })
    .catch(error => {
        console.log(error);
    });
}