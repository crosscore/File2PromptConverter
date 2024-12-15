// File2PromptConverter/src/templates/scripts.js

// DOM Elements
const elements = {
  form: document.getElementById('upload-form'),
  fileInput: document.getElementById('fileInput'),
  uploadedFiles: document.getElementById('uploaded-files'),
  resultContainer: document.getElementById('result-container'),
  resultText: document.getElementById('resultText')
};

// File Display Handler
function displayFileNames() {
  elements.uploadedFiles.innerHTML = '';

  if (elements.fileInput.files.length > 0) {
      const fileNames = Array.from(elements.fileInput.files)
          .map(file => file.name)
          .join(', ');
      elements.uploadedFiles.textContent = 'Selected files: ' + fileNames;
  }
}

// File Upload Handler
async function handleFileUpload(event) {
  event.preventDefault();

  const formData = new FormData();

  for (const file of elements.fileInput.files) {
      formData.append('files', file);
  }

  try {
      const response = await fetch('/upload', {
          method: 'POST',
          body: formData
      });

      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }

      const resultText = await response.text();
      elements.resultText.value = resultText;
      elements.resultContainer.style.display = 'block';
  } catch (error) {
      console.error('Error:', error);
      alert('Error uploading files: ' + error.message);
  }
}

// Clipboard Handler
function copyToClipboard() {
  elements.resultText.select();
  document.execCommand("copy");
  alert("Copied to clipboard!");
}

// Form Reset Handler
function resetForm() {
  elements.fileInput.value = '';
  elements.uploadedFiles.innerHTML = '';
  elements.resultText.value = '';
  elements.resultContainer.style.display = 'none';
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
  elements.form.addEventListener('submit', handleFileUpload);
  elements.fileInput.addEventListener('change', displayFileNames);
});
