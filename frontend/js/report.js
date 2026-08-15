/**
 * ==============================================================================
 * CIVICFIX — Resident Issue Reporting Controller (js/report.js)
 * ==============================================================================
 * Connects the issue report form with:
 * - Photo Preview (FileReader)
 * - Interactive Leaflet OpenStreetMap
 * - Generative AI Analysis (Step 8: analyzeIssue)
 * - Issue Submission (Step 9: createIssue & redirect to issue-details.html?id=ID)
 */

let reportMap = null;
let reportMarker = null;

const DEFAULT_LAT = 12.9716;
const DEFAULT_LNG = 77.5946;

document.addEventListener('DOMContentLoaded', () => {
  initReportForm();
  initPhotoUpload();
  initReportMap();
  initCurrentLocationButton();
  initAiAnalysis();
});

/**
 * ============================================================================
 * 1. Form Validation & Submission Controller (STEP 9)
 * ============================================================================
 */
function initReportForm() {
  const form = document.getElementById('issue-report-form');
  const alertBanner = document.getElementById('form-alert');
  const alertMessage = document.getElementById('form-alert-message');
  const formCard = document.getElementById('report-form-card');
  const successCard = document.getElementById('submission-success-card');
  const idBadge = document.getElementById('submission-id-badge');
  const btnViewDetails = document.getElementById('btn-view-details');
  const btnReportAnother = document.getElementById('btn-report-another');
  const btnReset = document.getElementById('btn-reset-form');

  if (!form) return;

  // Real-time error clearing on input
  ['title', 'category', 'description', 'latitude', 'longitude'].forEach((fieldId) => {
    const input = document.getElementById(fieldId);
    if (input) {
      input.addEventListener('input', () => clearFieldError(fieldId));
      input.addEventListener('change', () => clearFieldError(fieldId));
    }
  });

  // Submit Handler -> Calls createIssue(issue)
  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const validationResult = validateIssueForm();

    if (!validationResult.isValid) {
      if (alertBanner && alertMessage) {
        alertMessage.textContent = 'Please fix the errors highlighted below before submitting.';
        alertBanner.classList.add('show');
        alertBanner.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      return;
    }

    if (alertBanner) alertBanner.classList.remove('show');

    // Collect all fields corresponding to backend Issue model
    const submitBtn = document.getElementById('btn-submit-issue');
    if (submitBtn) {
      submitBtn.textContent = '⏳ Submitting Issue...';
      submitBtn.disabled = true;
    }

    try {
      // Step 9: Call api.createIssue(issue)
      const createdIssue = await window.api.createIssue(validationResult.data);
      console.log('✅ Issue created successfully:', createdIssue);

      // Hide form card and display success card
      if (formCard) formCard.style.display = 'none';
      if (successCard) {
        successCard.style.display = 'block';
        if (idBadge) idBadge.textContent = `Issue #${createdIssue.id}`;
        if (btnViewDetails) btnViewDetails.href = `issue-details.html?id=${createdIssue.id}`;
        successCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    } catch (error) {
      console.error('Submission error:', error);
      if (alertBanner && alertMessage) {
        alertMessage.textContent = `Submission failed: ${error.message || 'Server error'}. Please try again.`;
        alertBanner.classList.add('show');
      }
    } finally {
      if (submitBtn) {
        submitBtn.textContent = '📢 Submit Issue';
        submitBtn.disabled = false;
      }
    }
  });

  // Reset form
  if (btnReset) {
    btnReset.addEventListener('click', () => {
      resetReportForm();
    });
  }

  // Report another issue
  if (btnReportAnother) {
    btnReportAnother.addEventListener('click', () => {
      resetReportForm();
      if (formCard) formCard.style.display = 'block';
      if (successCard) successCard.style.display = 'none';
      const titleInput = document.getElementById('title');
      if (titleInput) titleInput.focus();
    });
  }
}

/**
 * Validate all required fields against backend schema constraints
 */
function validateIssueForm() {
  let isValid = true;

  // Title
  const titleInput = document.getElementById('title');
  const titleVal = titleInput ? titleInput.value.trim() : '';
  if (!titleVal || titleVal.length < 3) {
    showFieldError('title', 'Title must be at least 3 characters long.');
    isValid = false;
  } else {
    setFieldValid('title');
  }

  // Category
  const categoryInput = document.getElementById('category');
  const categoryVal = categoryInput ? categoryInput.value : '';
  if (!categoryVal) {
    showFieldError('category', 'Please select an issue category from the dropdown.');
    isValid = false;
  } else {
    setFieldValid('category');
  }

  // Description
  const descInput = document.getElementById('description');
  const descVal = descInput ? descInput.value.trim() : '';
  if (!descVal || descVal.length < 5) {
    showFieldError('description', 'Description must be at least 5 characters long.');
    isValid = false;
  } else {
    setFieldValid('description');
  }

  // Latitude
  const latInput = document.getElementById('latitude');
  const latVal = latInput ? parseFloat(latInput.value) : NaN;
  if (isNaN(latVal) || latVal < -90 || latVal > 90) {
    showFieldError('latitude', 'Please enter a valid latitude (-90.0 to 90.0).');
    isValid = false;
  } else {
    setFieldValid('latitude');
  }

  // Longitude
  const lngInput = document.getElementById('longitude');
  const lngVal = lngInput ? parseFloat(lngInput.value) : NaN;
  if (isNaN(lngVal) || lngVal < -180 || lngVal > 180) {
    showFieldError('longitude', 'Please enter a valid longitude (-180.0 to 180.0).');
    isValid = false;
  } else {
    setFieldValid('longitude');
  }

  // Optional / AI fields
  const addressInput = document.getElementById('address');
  const addressVal = addressInput ? addressInput.value.trim() : '';

  const imagePathInput = document.getElementById('image_path');
  const imagePathVal = imagePathInput ? imagePathInput.value : null;

  const aiSummary = document.getElementById('ai_summary')?.value || null;
  const aiCategory = document.getElementById('ai_category')?.value || null;
  const aiPriority = document.getElementById('ai_priority')?.value || null;
  const aiAction = document.getElementById('ai_suggested_action')?.value || null;

  // Complete payload matching backend Issue model
  const payload = {
    title: titleVal,
    category: categoryVal,
    description: descVal,
    latitude: latVal,
    longitude: lngVal,
    address: addressVal || null,
    image_path: imagePathVal || null,
    priority: aiPriority || "MEDIUM",
    ai_summary: aiSummary,
    ai_category: aiCategory,
    ai_priority: aiPriority,
    ai_suggested_action: aiAction,
    created_by: 1
  };

  return { isValid, data: payload };
}

/**
 * ============================================================================
 * 2. Generative AI Issue Analysis Controller (STEP 8)
 * ============================================================================
 */
function initAiAnalysis() {
  const btnAiAnalyze = document.getElementById('btn-ai-analyze');
  const loadingBox = document.getElementById('ai-loading-box');
  const failureBox = document.getElementById('ai-failure-box');
  const analysisCard = document.getElementById('ai-analysis-card');

  const displaySummary = document.getElementById('ai-display-summary');
  const displayCategory = document.getElementById('ai-display-category');
  const displayPriority = document.getElementById('ai-display-priority');
  const displayAction = document.getElementById('ai-display-action');

  const inputSummary = document.getElementById('ai_summary');
  const inputCategory = document.getElementById('ai_category');
  const inputPriority = document.getElementById('ai_priority');
  const inputAction = document.getElementById('ai_suggested_action');
  const categorySelect = document.getElementById('category');

  if (!btnAiAnalyze) return;

  btnAiAnalyze.addEventListener('click', async () => {
    const titleVal = document.getElementById('title')?.value.trim() || '';
    const descVal = document.getElementById('description')?.value.trim() || '';
    const categoryVal = document.getElementById('category')?.value || '';
    const imageVal = document.getElementById('image_path')?.value || null;

    if (!titleVal && !descVal) {
      alert('Please enter at least an issue title or description before running AI analysis.');
      document.getElementById('title')?.focus();
      return;
    }

    // 1. Loading State
    btnAiAnalyze.disabled = true;
    if (loadingBox) loadingBox.style.display = 'flex';
    if (failureBox) failureBox.style.display = 'none';
    if (analysisCard) analysisCard.style.display = 'none';

    try {
      // Step 8: Call analyzeIssue(issue) from api.js
      const aiResult = await window.api.analyzeIssue({
        title: titleVal,
        description: descVal,
        category: categoryVal,
        image_path: imageVal
      });

      // 2. Success State: Populate card and hidden fields
      if (displaySummary) displaySummary.textContent = `"${aiResult.ai_summary}"`;
      if (displayCategory) displayCategory.textContent = aiResult.ai_category;
      if (displayPriority) displayPriority.textContent = `${aiResult.ai_priority} Priority`;
      if (displayAction) displayAction.textContent = aiResult.ai_suggested_action;

      if (inputSummary) inputSummary.value = aiResult.ai_summary;
      if (inputCategory) inputCategory.value = aiResult.ai_category;
      if (inputPriority) inputPriority.value = aiResult.ai_priority;
      if (inputAction) inputAction.value = aiResult.ai_suggested_action;

      // Auto-sync category dropdown if none was selected
      if (categorySelect && !categorySelect.value && aiResult.ai_category) {
        for (let opt of categorySelect.options) {
          if (opt.value.toLowerCase() === aiResult.ai_category.toLowerCase()) {
            categorySelect.value = opt.value;
            clearFieldError('category');
            setFieldValid('category');
            break;
          }
        }
      }

      if (analysisCard) analysisCard.style.display = 'block';
    } catch (error) {
      console.warn('AI analysis error:', error);
      // 3. Failure State Fallback
      if (failureBox) failureBox.style.display = 'flex';
    } finally {
      if (loadingBox) loadingBox.style.display = 'none';
      btnAiAnalyze.disabled = false;
    }
  });
}

/**
 * ============================================================================
 * 3. Interactive Leaflet Map Controller
 * ============================================================================
 */
function initReportMap() {
  const mapContainer = document.getElementById('report-map');
  const latInput = document.getElementById('latitude');
  const lngInput = document.getElementById('longitude');

  if (!mapContainer) return;

  if (typeof L === 'undefined') {
    console.warn('Leaflet.js not loaded. Falling back to manual coordinates entry.');
    return;
  }

  try {
    const initialLat = (latInput && latInput.value) ? parseFloat(latInput.value) : DEFAULT_LAT;
    const initialLng = (lngInput && lngInput.value) ? parseFloat(lngInput.value) : DEFAULT_LNG;

    reportMap = L.map('report-map', {
      center: [initialLat, initialLng],
      zoom: 14,
      scrollWheelZoom: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>'
    }).addTo(reportMap);

    reportMarker = L.marker([initialLat, initialLng], {
      draggable: true,
      title: 'Drag to adjust exact location'
    }).addTo(reportMap);

    reportMarker.bindPopup('<b>Selected Issue Location</b><br>Drag pin or click map to adjust.').openPopup();

    updateCoordinatesInputs(initialLat, initialLng);

    reportMarker.on('dragend', () => {
      const position = reportMarker.getLatLng();
      updateCoordinatesInputs(position.lat, position.lng);
      clearFieldError('latitude');
      clearFieldError('longitude');
      setFieldValid('latitude');
      setFieldValid('longitude');
    });

    reportMap.on('click', (event) => {
      const clickedLat = event.latlng.lat;
      const clickedLng = event.latlng.lng;
      
      reportMarker.setLatLng([clickedLat, clickedLng]);
      updateCoordinatesInputs(clickedLat, clickedLng);
      clearFieldError('latitude');
      clearFieldError('longitude');
      setFieldValid('latitude');
      setFieldValid('longitude');
    });

    if (latInput && lngInput) {
      const syncInputsToMap = () => {
        const parsedLat = parseFloat(latInput.value);
        const parsedLng = parseFloat(lngInput.value);

        if (!isNaN(parsedLat) && !isNaN(parsedLng) &&
            parsedLat >= -90 && parsedLat <= 90 &&
            parsedLng >= -180 && parsedLng <= 180) {
          reportMarker.setLatLng([parsedLat, parsedLng]);
          reportMap.panTo([parsedLat, parsedLng]);
        }
      };

      latInput.addEventListener('change', syncInputsToMap);
      lngInput.addEventListener('change', syncInputsToMap);
    }
  } catch (error) {
    console.error('Error initializing Leaflet map:', error);
  }
}

function updateCoordinatesInputs(lat, lng) {
  const latInput = document.getElementById('latitude');
  const lngInput = document.getElementById('longitude');

  if (latInput) latInput.value = parseFloat(lat).toFixed(6);
  if (lngInput) lngInput.value = parseFloat(lng).toFixed(6);
}

/**
 * ============================================================================
 * 4. Current Location Button Controller
 * ============================================================================
 */
function initCurrentLocationButton() {
  const btnCurrentLocation = document.getElementById('btn-current-location');
  const noticeEl = document.getElementById('location-notice');
  const addressInput = document.getElementById('address');

  if (!btnCurrentLocation) return;

  btnCurrentLocation.addEventListener('click', () => {
    btnCurrentLocation.textContent = '⏳ Locating...';
    btnCurrentLocation.disabled = true;
    hideLocationNotice();

    if (!navigator.geolocation) {
      showLocationNotice(
        'Unable to access your current location. Please select your location manually.',
        'warning'
      );
      restoreButton();
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const userLat = position.coords.latitude;
        const userLng = position.coords.longitude;

        updateCoordinatesInputs(userLat, userLng);
        clearFieldError('latitude');
        clearFieldError('longitude');
        setFieldValid('latitude');
        setFieldValid('longitude');

        if (reportMap && reportMarker) {
          reportMarker.setLatLng([userLat, userLng]);
          reportMap.setView([userLat, userLng], 16);
          reportMarker.bindPopup('<b>Your Current Location</b>').openPopup();
        }

        if (addressInput && !addressInput.value) {
          addressInput.value = `Near GPS (${userLat.toFixed(4)}, ${userLng.toFixed(4)})`;
        }

        showLocationNotice('Location detected successfully!', 'success');
        restoreButton();
      },
      (error) => {
        console.warn('Geolocation failed or denied:', error.message);
        showLocationNotice(
          'Unable to access your current location. Please select your location manually.',
          'warning'
        );

        const latInput = document.getElementById('latitude');
        const lngInput = document.getElementById('longitude');
        if (latInput && !latInput.value) latInput.value = DEFAULT_LAT.toFixed(6);
        if (lngInput && !lngInput.value) lngInput.value = DEFAULT_LNG.toFixed(6);

        restoreButton();
      },
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
    );

    function restoreButton() {
      btnCurrentLocation.textContent = '📍 Use My Current Location';
      btnCurrentLocation.disabled = false;
    }
  });

  function showLocationNotice(message, type) {
    if (noticeEl) {
      noticeEl.textContent = message;
      noticeEl.className = `location-notice notice-${type}`;
    }
  }

  function hideLocationNotice() {
    if (noticeEl) {
      noticeEl.style.display = 'none';
      noticeEl.textContent = '';
      noticeEl.className = 'location-notice';
    }
  }
}

/**
 * ============================================================================
 * 5. Photo Upload & FileReader Preview Controller
 * ============================================================================
 */
function initPhotoUpload() {
  const dropzone = document.getElementById('upload-dropzone');
  const fileInput = document.getElementById('photo-input');
  const previewContainer = document.getElementById('photo-preview-container');
  const previewImg = document.getElementById('photo-preview-img');
  const filenameEl = document.getElementById('photo-filename');
  const filesizeEl = document.getElementById('photo-filesize');
  const btnRemove = document.getElementById('btn-remove-photo');
  const btnChange = document.getElementById('btn-change-photo');
  const photoError = document.getElementById('photo-error');
  const imagePathInput = document.getElementById('image_path');

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener('click', () => fileInput.click());

  if (btnChange) {
    btnChange.addEventListener('click', (e) => {
      e.stopPropagation();
      fileInput.click();
    });
  }

  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      handleImageSelection(e.target.files[0]);
    }
  });

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.style.borderColor = 'var(--color-primary)';
    dropzone.style.backgroundColor = 'var(--color-primary-subtle)';
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.style.borderColor = 'var(--color-border)';
    dropzone.style.backgroundColor = 'var(--color-bg)';
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.style.borderColor = 'var(--color-border)';
    dropzone.style.backgroundColor = 'var(--color-bg)';
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleImageSelection(e.dataTransfer.files[0]);
    }
  });

  if (btnRemove) {
    btnRemove.addEventListener('click', (e) => {
      e.stopPropagation();
      removeSelectedImage();
    });
  }

  function handleImageSelection(file) {
    if (!file || !file.type.startsWith('image/')) {
      showPhotoError('Invalid file: The selected file is not an image. Please choose a PNG, JPG, or JPEG file.');
      fileInput.value = '';
      return;
    }

    clearPhotoError();
    const reader = new FileReader();

    reader.onload = (event) => {
      const dataUrl = event.target.result;
      if (previewImg) previewImg.src = dataUrl;
      if (filenameEl) filenameEl.textContent = file.name;
      if (filesizeEl) filesizeEl.textContent = formatBytes(file.size);
      if (imagePathInput) imagePathInput.value = dataUrl;

      dropzone.style.display = 'none';
      if (previewContainer) previewContainer.style.display = 'block';
    };

    reader.onerror = () => {
      showPhotoError('Failed to read image file. Please try selecting the photo again.');
    };

    reader.readAsDataURL(file);
  }

  function removeSelectedImage() {
    fileInput.value = '';
    if (previewImg) previewImg.src = '';
    if (filenameEl) filenameEl.textContent = '';
    if (filesizeEl) filesizeEl.textContent = '';
    if (imagePathInput) imagePathInput.value = '';

    if (previewContainer) previewContainer.style.display = 'none';
    if (dropzone) dropzone.style.display = 'block';
    clearPhotoError();
  }

  function showPhotoError(message) {
    if (photoError) {
      photoError.textContent = message;
      photoError.classList.add('show');
    }
  }

  function clearPhotoError() {
    if (photoError) {
      photoError.textContent = '';
      photoError.classList.remove('show');
    }
  }

  function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }
}

/**
 * ============================================================================
 * 6. UI Helpers & Reset
 * ============================================================================
 */
function showFieldError(fieldId, message) {
  const input = document.getElementById(fieldId);
  const errorElement = document.getElementById(`${fieldId}-error`);

  if (input) {
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');
  }

  if (errorElement) {
    errorElement.textContent = message;
    errorElement.classList.add('show');
  }
}

function setFieldValid(fieldId) {
  const input = document.getElementById(fieldId);
  const errorElement = document.getElementById(`${fieldId}-error`);

  if (input) {
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
  }

  if (errorElement) {
    errorElement.classList.remove('show');
  }
}

function clearFieldError(fieldId) {
  const input = document.getElementById(fieldId);
  const errorElement = document.getElementById(`${fieldId}-error`);

  if (input) {
    input.classList.remove('is-invalid');
  }

  if (errorElement) {
    errorElement.classList.remove('show');
  }
}

function resetReportForm() {
  const form = document.getElementById('issue-report-form');
  const alertBanner = document.getElementById('form-alert');
  
  if (form) form.reset();
  if (alertBanner) alertBanner.classList.remove('show');

  ['title', 'category', 'description', 'latitude', 'longitude'].forEach((fieldId) => {
    clearFieldError(fieldId);
    const input = document.getElementById(fieldId);
    if (input) input.classList.remove('is-valid');
  });

  // Reset photo
  const dropzone = document.getElementById('upload-dropzone');
  const previewContainer = document.getElementById('photo-preview-container');
  const previewImg = document.getElementById('photo-preview-img');
  const imagePathInput = document.getElementById('image_path');
  const photoInput = document.getElementById('photo-input');
  const photoError = document.getElementById('photo-error');

  if (photoInput) photoInput.value = '';
  if (dropzone) dropzone.style.display = 'block';
  if (previewContainer) previewContainer.style.display = 'none';
  if (previewImg) previewImg.src = '';
  if (imagePathInput) imagePathInput.value = '';
  if (photoError) {
    photoError.textContent = '';
    photoError.classList.remove('show');
  }

  // Reset AI fields and card
  const analysisCard = document.getElementById('ai-analysis-card');
  const loadingBox = document.getElementById('ai-loading-box');
  const failureBox = document.getElementById('ai-failure-box');
  if (analysisCard) analysisCard.style.display = 'none';
  if (loadingBox) loadingBox.style.display = 'none';
  if (failureBox) failureBox.style.display = 'none';

  ['ai_summary', 'ai_category', 'ai_priority', 'ai_suggested_action'].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });

  // Reset map position
  if (reportMap && reportMarker) {
    reportMarker.setLatLng([DEFAULT_LAT, DEFAULT_LNG]);
    reportMap.setView([DEFAULT_LAT, DEFAULT_LNG], 14);
    updateCoordinatesInputs(DEFAULT_LAT, DEFAULT_LNG);
  }
}
