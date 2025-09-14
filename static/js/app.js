// MDitD Frontend JavaScript

// Configuration
const CONFIG = {
    supportedExtensions: ['.pdf', '.docx', '.pptx', '.xlsx',
                         '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
                         '.mp3', '.wav', '.m4a', '.flac',
                         '.html', '.htm', '.csv', '.json', '.xml',
                         '.zip', '.txt', '.md'],
    maxFileSize: 50 * 1024 * 1024, // 50MB
    maxFiles: 20
};

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadSpinner = document.getElementById('uploadSpinner');
    const results = document.getElementById('results');
    const resultsContent = document.getElementById('resultsContent');
    const filesInput = document.getElementById('files');

    // Initialize features
    initializeFileValidation();
    initializeDragAndDrop();
    initializeProgressTracking();

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const outputDirInput = document.getElementById('output_dir');

        // Validate files before upload
        const validationResult = validateFiles(filesInput.files);
        if (!validationResult.isValid) {
            displayValidationError(validationResult.errors);
            return;
        }

        // Show loading state with progress
        setLoadingState(true);
        hideResults();
        showProgressBar(0);

        try {
            const formData = new FormData();

            // Add files
            for (let file of filesInput.files) {
                formData.append('files', file);
            }

            // Add output directory
            formData.append('output_dir', outputDirInput.value || 'vystup');

            // Upload with progress tracking
            const response = await uploadWithProgress('/upload', formData);
            const result = await response.json();

            if (response.ok) {
                displayResults(result);
            } else {
                throw new Error(result.detail || 'Upload failed');
            }

        } catch (error) {
            console.error('Upload error:', error);
            displayError('Error: ' + error.message);
        } finally {
            setLoadingState(false);
            hideProgressBar();
        }
    });

    function setLoadingState(loading) {
        if (loading) {
            uploadBtn.disabled = true;
            uploadSpinner.classList.remove('d-none');
            uploadBtn.innerHTML = '<span id="uploadSpinner" class="spinner-border spinner-border-sm" role="status"></span> Converting...';
        } else {
            uploadBtn.disabled = false;
            uploadSpinner.classList.add('d-none');
            uploadBtn.innerHTML = 'Convert to Markdown';
        }
    }

    function displayResults(result) {
        let html = `
            <div class="row mb-3">
                <div class="col-md-4">
                    <div class="text-center">
                        <h5 class="text-primary">${result.total_files}</h5>
                        <small class="text-muted">Total Files</small>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="text-center">
                        <h5 class="text-success">${result.successful}</h5>
                        <small class="text-muted">Successful</small>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="text-center">
                        <h5 class="text-danger">${result.failed}</h5>
                        <small class="text-muted">Failed</small>
                    </div>
                </div>
            </div>
            <hr>
        `;

        // Individual file results
        result.results.forEach((file, index) => {
            const statusIcon = file.success ? '✅' : '❌';
            const statusClass = file.success ? 'success' : 'danger';

            html += `
                <div class="alert alert-${statusClass} alert-dismissible">
                    <strong>${statusIcon} ${file.filename}</strong>
                    <br>
                    ${file.success ?
                        `<small class="text-muted">Saved to: ${file.output_path}</small>
                         ${file.content ? `<button class="btn btn-sm btn-outline-primary mt-2" onclick="showPreview('${file.filename}', \`${escapeHtml(file.content)}\`)">
                            <i class="fas fa-eye"></i> Preview
                         </button>` : ''}` :
                        `<small>Error: ${file.error}</small>`
                    }
                </div>
            `;
        });

        resultsContent.innerHTML = html;
        showResults();
    }

    function displayError(message) {
        resultsContent.innerHTML = `
            <div class="alert alert-danger">
                <strong>Error!</strong> ${message}
            </div>
        `;
        showResults();
    }

    function showResults() {
        results.classList.remove('d-none');
        results.scrollIntoView({ behavior: 'smooth' });
    }

    function hideResults() {
        results.classList.add('d-none');
    }

    // ====== NEW ENHANCEMENT FUNCTIONS ======

    function initializeFileValidation() {
        filesInput.addEventListener('change', function() {
            const files = this.files;
            updateFilePreview(files);

            // Real-time validation feedback
            const validationResult = validateFiles(files);
            if (!validationResult.isValid && files.length > 0) {
                displayValidationWarning(validationResult.errors);
            } else {
                hideValidationWarning();
            }
        });
    }

    function initializeDragAndDrop() {
        const uploadArea = document.querySelector('.upload-area') || uploadForm;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Highlight drop area when dragging over it
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });

        // Handle dropped files
        uploadArea.addEventListener('drop', handleDrop, false);

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        function highlight(e) {
            uploadArea.classList.add('drag-over');
        }

        function unhighlight(e) {
            uploadArea.classList.remove('drag-over');
        }

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            filesInput.files = files;

            // Trigger change event for validation
            const event = new Event('change');
            filesInput.dispatchEvent(event);
        }
    }

    function initializeProgressTracking() {
        // Create progress bar HTML if it doesn't exist
        if (!document.getElementById('progressContainer')) {
            const progressHTML = `
                <div id="progressContainer" class="progress-container d-none mb-3">
                    <div class="progress" style="height: 20px;">
                        <div id="progressBar" class="progress-bar progress-bar-striped progress-bar-animated"
                             role="progressbar" style="width: 0%">
                            <span id="progressText">0%</span>
                        </div>
                    </div>
                </div>
            `;
            uploadForm.insertAdjacentHTML('afterend', progressHTML);
        }
    }

    function validateFiles(files) {
        const errors = [];

        if (!files || files.length === 0) {
            return { isValid: false, errors: ['Please select at least one file to convert.'] };
        }

        if (files.length > CONFIG.maxFiles) {
            errors.push(`Maximum ${CONFIG.maxFiles} files allowed. You selected ${files.length} files.`);
        }

        let totalSize = 0;
        for (let file of files) {
            // Check file extension
            const extension = '.' + file.name.split('.').pop().toLowerCase();
            if (!CONFIG.supportedExtensions.includes(extension)) {
                errors.push(`Unsupported file type: ${file.name} (${extension})`);
            }

            // Check file size
            if (file.size > CONFIG.maxFileSize) {
                const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
                const maxSizeMB = (CONFIG.maxFileSize / (1024 * 1024)).toFixed(0);
                errors.push(`File too large: ${file.name} (${sizeMB}MB). Maximum size: ${maxSizeMB}MB`);
            }

            totalSize += file.size;
        }

        // Check total size (optional additional limit)
        const maxTotalSize = CONFIG.maxFileSize * 3; // 150MB total
        if (totalSize > maxTotalSize) {
            const totalSizeMB = (totalSize / (1024 * 1024)).toFixed(1);
            const maxTotalSizeMB = (maxTotalSize / (1024 * 1024)).toFixed(0);
            errors.push(`Total file size too large: ${totalSizeMB}MB. Maximum total: ${maxTotalSizeMB}MB`);
        }

        return {
            isValid: errors.length === 0,
            errors: errors,
            fileCount: files.length,
            totalSize: totalSize
        };
    }

    function updateFilePreview(files) {
        const preview = document.getElementById('filePreview') || createFilePreview();

        if (!files || files.length === 0) {
            preview.classList.add('d-none');
            return;
        }

        let html = '<h6>Selected Files:</h6><ul class="list-group list-group-flush">';

        for (let file of files) {
            const sizeKB = (file.size / 1024).toFixed(1);
            const extension = '.' + file.name.split('.').pop().toLowerCase();
            const isSupported = CONFIG.supportedExtensions.includes(extension);
            const statusIcon = isSupported ? '✅' : '❌';
            const statusClass = isSupported ? 'text-success' : 'text-danger';

            html += `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <span class="${statusClass}">${statusIcon}</span>
                        <strong>${file.name}</strong>
                        <small class="text-muted d-block">${extension.toUpperCase()} • ${sizeKB} KB</small>
                    </div>
                </li>
            `;
        }

        html += '</ul>';
        preview.innerHTML = html;
        preview.classList.remove('d-none');
    }

    function createFilePreview() {
        const preview = document.createElement('div');
        preview.id = 'filePreview';
        preview.className = 'file-preview mt-3 d-none';
        filesInput.parentNode.insertBefore(preview, filesInput.nextSibling);
        return preview;
    }

    function displayValidationError(errors) {
        let html = '<div class="alert alert-danger alert-dismissible"><strong>Validation Error:</strong><ul class="mb-0 mt-2">';
        errors.forEach(error => {
            html += `<li>${error}</li>`;
        });
        html += '</ul></div>';

        showValidationMessage(html);
    }

    function displayValidationWarning(errors) {
        let html = '<div class="alert alert-warning alert-dismissible"><strong>Warning:</strong><ul class="mb-0 mt-2">';
        errors.forEach(error => {
            html += `<li>${error}</li>`;
        });
        html += '</ul><small class="d-block mt-1">Please fix these issues before uploading.</small></div>';

        showValidationMessage(html);
    }

    function showValidationMessage(html) {
        let validationDiv = document.getElementById('validationMessage');
        if (!validationDiv) {
            validationDiv = document.createElement('div');
            validationDiv.id = 'validationMessage';
            uploadForm.parentNode.insertBefore(validationDiv, uploadForm);
        }
        validationDiv.innerHTML = html;
    }

    function hideValidationWarning() {
        const validationDiv = document.getElementById('validationMessage');
        if (validationDiv) {
            validationDiv.innerHTML = '';
        }
    }

    function uploadWithProgress(url, formData) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            // Progress tracking
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    updateProgressBar(percentComplete);
                }
            });

            // State change handling
            xhr.addEventListener('readystatechange', () => {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        resolve({
                            ok: true,
                            json: () => Promise.resolve(JSON.parse(xhr.responseText))
                        });
                    } else {
                        reject(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`));
                    }
                }
            });

            // Error handling
            xhr.addEventListener('error', () => {
                reject(new Error('Network error occurred'));
            });

            // Start upload
            xhr.open('POST', url);
            xhr.send(formData);
        });
    }

    function showProgressBar(progress = 0) {
        const progressContainer = document.getElementById('progressContainer');
        if (progressContainer) {
            progressContainer.classList.remove('d-none');
            updateProgressBar(progress);
        }
    }

    function updateProgressBar(progress) {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');

        if (progressBar && progressText) {
            const rounded = Math.round(progress);
            progressBar.style.width = `${rounded}%`;
            progressText.textContent = `${rounded}%`;

            // Change color based on progress
            progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated';
            if (progress < 50) {
                progressBar.classList.add('bg-info');
            } else if (progress < 80) {
                progressBar.classList.add('bg-warning');
            } else {
                progressBar.classList.add('bg-success');
            }
        }
    }

    function hideProgressBar() {
        const progressContainer = document.getElementById('progressContainer');
        if (progressContainer) {
            setTimeout(() => {
                progressContainer.classList.add('d-none');
            }, 1000); // Keep visible for 1 second after completion
        }
    }

    // Initialize preview functionality
    initializePreview();
});

// ====== MARKDOWN PREVIEW FUNCTIONS ======

function initializePreview() {
    const renderedViewBtn = document.getElementById('renderedViewBtn');
    const rawViewBtn = document.getElementById('rawViewBtn');

    if (renderedViewBtn && rawViewBtn) {
        renderedViewBtn.addEventListener('change', () => {
            if (renderedViewBtn.checked) {
                showRenderedPreview();
            }
        });

        rawViewBtn.addEventListener('change', () => {
            if (rawViewBtn.checked) {
                showRawPreview();
            }
        });
    }
}

function showPreview(filename, content) {
    const previewSection = document.getElementById('previewSection');
    const renderedPreview = document.getElementById('renderedPreview');
    const rawContent = document.getElementById('rawContent');
    const renderedViewBtn = document.getElementById('renderedViewBtn');

    if (!content || content.trim() === '') {
        content = 'No content available for preview.';
    }

    // Update content
    rawContent.textContent = content;

    // Render markdown using marked.js if available
    if (typeof marked !== 'undefined') {
        try {
            marked.setOptions({
                highlight: function(code, lang) {
                    if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
                        return hljs.highlight(code, {language: lang}).value;
                    }
                    return code;
                },
                breaks: true,
                gfm: true
            });

            renderedPreview.innerHTML = marked.parse(content);

            // Highlight code blocks
            if (typeof hljs !== 'undefined') {
                renderedPreview.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });
            }
        } catch (error) {
            console.warn('Error rendering markdown:', error);
            renderedPreview.innerHTML = `<pre>${escapeHtml(content)}</pre>`;
        }
    } else {
        // Fallback if marked.js is not available
        renderedPreview.innerHTML = `<pre>${escapeHtml(content)}</pre>`;
    }

    // Update preview title
    const previewTitle = previewSection.querySelector('.card-header h6');
    if (previewTitle) {
        previewTitle.innerHTML = `<i class="fas fa-eye text-primary me-2"></i>Markdown Preview - ${filename}`;
    }

    // Show rendered view by default
    renderedViewBtn.checked = true;
    showRenderedPreview();

    // Show and scroll to preview
    previewSection.classList.remove('d-none');
    previewSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function showRenderedPreview() {
    const renderedPreview = document.getElementById('renderedPreview');
    const rawPreview = document.getElementById('rawPreview');

    if (renderedPreview && rawPreview) {
        renderedPreview.classList.remove('d-none');
        rawPreview.classList.add('d-none');
    }
}

function showRawPreview() {
    const renderedPreview = document.getElementById('renderedPreview');
    const rawPreview = document.getElementById('rawPreview');

    if (renderedPreview && rawPreview) {
        renderedPreview.classList.add('d-none');
        rawPreview.classList.remove('d-none');
    }
}

function hidePreview() {
    const previewSection = document.getElementById('previewSection');
    if (previewSection) {
        previewSection.classList.add('d-none');
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}