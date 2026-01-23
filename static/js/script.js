// Xử lý chọn định dạng đầu ra
const formatBtns = document.querySelectorAll('.format-btn');
const outputFormat = document.getElementById('outputFormat');
const btnText = document.getElementById('btnText');
const modeLocal = document.getElementById('modeLocal');
const modeCloud = document.getElementById('modeCloud');
const modeLocalOption = document.getElementById('modeLocalOption');
const modeCloudOption = document.getElementById('modeCloudOption');
const modeInput = document.getElementById('modeInput');

const formatNames = {
    'word': 'Word',
    'excel': 'Excel',
    'powerpoint': 'PowerPoint'
};

formatBtns.forEach(btn => {
    btn.addEventListener('click', function() {
        // Bỏ active tất cả
        formatBtns.forEach(b => b.classList.remove('active'));
        // Active nút được chọn
        this.classList.add('active');

        const format = this.dataset.format;
        outputFormat.value = format;
        btnText.innerText = 'Chuyển đổi sang ' + formatNames[format];

        // Excel và PowerPoint chỉ hỗ trợ Cloud
        if (format === 'excel' || format === 'powerpoint') {
            modeCloud.checked = true;
            modeLocal.disabled = true;
            modeLocalOption.style.opacity = '0.5';
            modeLocalOption.style.pointerEvents = 'none';
            modeCloudOption.classList.add('selected');
            modeLocalOption.classList.remove('selected');
            modeInput.value = 'cloud';
        } else {
            modeLocal.disabled = false;
            modeLocalOption.style.opacity = '1';
            modeLocalOption.style.pointerEvents = 'auto';
        }
    });
});

// Xử lý chọn chế độ
document.querySelectorAll('.mode-option').forEach(option => {
    option.addEventListener('click', function() {
        if (this.style.pointerEvents === 'none') return;

        document.querySelectorAll('.mode-option').forEach(o => o.classList.remove('selected'));
        this.classList.add('selected');

        const mode = this.dataset.mode;
        document.getElementById('mode' + mode.charAt(0).toUpperCase() + mode.slice(1)).checked = true;
        modeInput.value = mode;
    });
});

// Xử lý drag & drop
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('pdfFile');
const fileName = document.getElementById('fileName');

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragover');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type === 'application/pdf') {
        fileInput.files = files;
        fileName.innerHTML = '<strong class="text-success">' + files[0].name + '</strong>';
    }
});

fileInput.addEventListener('change', function() {
    if (this.files.length > 0) {
        fileName.innerHTML = '<strong class="text-success">' + this.files[0].name + '</strong>';
    }
});

// Xử lý submit
document.getElementById('convertForm').addEventListener('submit', function() {
    var btn = document.getElementById('submitBtn');
    var spinner = document.getElementById('spinner');

    btn.disabled = true;
    spinner.style.display = 'inline-block';
    btnText.innerText = ' Đang xử lý...';
});
