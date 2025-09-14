// MDitD Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadSpinner = document.getElementById('uploadSpinner');
    const results = document.getElementById('results');
    const resultsContent = document.getElementById('resultsContent');

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const filesInput = document.getElementById('files');
        const outputDirInput = document.getElementById('output_dir');
        
        if (!filesInput.files.length) {
            alert('Please select at least one file to convert.');
            return;
        }

        // Show loading state
        setLoadingState(true);
        hideResults();

        try {
            const formData = new FormData();
            
            // Add files
            for (let file of filesInput.files) {
                formData.append('files', file);
            }
            
            // Add output directory
            formData.append('output_dir', outputDirInput.value || 'vystup');

            // Upload and convert
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

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
        result.results.forEach(file => {
            const statusIcon = file.success ? '✅' : '❌';
            const statusClass = file.success ? 'success' : 'danger';
            
            html += `
                <div class="alert alert-${statusClass} alert-dismissible">
                    <strong>${statusIcon} ${file.filename}</strong>
                    <br>
                    ${file.success ? 
                        `<small class="text-muted">Saved to: ${file.output_path}</small>` : 
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
});