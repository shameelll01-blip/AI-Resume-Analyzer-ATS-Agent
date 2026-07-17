document.addEventListener('DOMContentLoaded', () => {
    
    // --- Elements ---
    const homeView = document.getElementById('home-view');
    const loadingView = document.getElementById('loading-view');
    const reportView = document.getElementById('report-view');
    
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('resume-file');
    const selectFileBtn = document.querySelector('.select-file-btn');
    const removeFileBtn = document.querySelector('.remove-file-btn');
    const dropzoneContent = document.querySelector('.dropzone-content');
    const dropzoneFileInfo = document.querySelector('.dropzone-file-info');
    const selectedFileName = document.getElementById('selected-file-name');
    const selectedFileSize = document.getElementById('selected-file-size');
    
    const jobTemplatesSelect = document.getElementById('job-templates');
    const jobDescTextarea = document.getElementById('job-desc');
    const apiKeyInput = document.getElementById('api-key');
    const analyzeBtn = document.getElementById('analyze-btn');
    
    const loadingTitle = document.getElementById('loading-title');
    const loadingMessage = document.getElementById('loading-message');
    const progressBarFill = document.querySelector('.progress-bar-fill');
    
    const backHomeBtn = document.getElementById('back-home-btn');
    
    // Report fields
    const overallScoreText = document.getElementById('overall-score-text');
    const gaugeArc = document.getElementById('gauge-arc');
    
    const badgeTone = document.getElementById('badge-tone');
    const scoreTone = document.getElementById('score-tone');
    const badgeContent = document.getElementById('badge-content');
    const scoreContent = document.getElementById('score-content');
    const badgeStructure = document.getElementById('badge-structure');
    const scoreStructure = document.getElementById('score-structure');
    const badgeSkills = document.getElementById('badge-skills');
    const scoreSkills = document.getElementById('score-skills');
    
    const atsCardContainer = document.getElementById('ats-card-container');
    const atsScoreTitle = document.getElementById('ats-score-title');
    const atsStatusText = document.getElementById('ats-status-text');
    const atsWarningsUl = document.getElementById('ats-warnings-ul');
    const atsWarningIcon = document.getElementById('ats-warning-icon');
    
    const accBadgeTone = document.getElementById('acc-badge-tone');
    const accBadgeContent = document.getElementById('acc-badge-content');
    const accBadgeStructure = document.getElementById('acc-badge-structure');
    const accBadgeSkills = document.getElementById('acc-badge-skills');
    
    const panelToneText = document.getElementById('panel-tone-text');
    const panelContentText = document.getElementById('panel-content-text');
    const panelStructureText = document.getElementById('panel-structure-text');
    
    const matchedSkillsChips = document.getElementById('matched-skills-chips');
    const missingSkillsChips = document.getElementById('missing-skills-chips');
    
    // Resume preview fields
    const resName = document.getElementById('res-name');
    const resContacts = document.getElementById('res-contacts');
    const resEmail = document.getElementById('res-email');
    const resPhone = document.getElementById('res-phone');
    const resAddress = document.getElementById('res-address');
    const resSummary = document.getElementById('res-summary');
    const resExperience = document.getElementById('res-experience');
    const resProjects = document.getElementById('res-projects');
    const resEducation = document.getElementById('res-education');
    
    // --- State Variables ---
    let selectedFile = null;
    let jobTemplates = {};
    
    // --- Initialize Templates ---
    fetch('/api/templates')
        .then(res => res.json())
        .then(data => {
            jobTemplates = data;
            Object.keys(data).forEach(role => {
                const option = document.createElement('option');
                option.value = role;
                option.textContent = role;
                jobTemplatesSelect.appendChild(option);
            });
        })
        .catch(err => console.error('Error fetching job templates:', err));
        
    // --- Drag and Drop Handlers ---
    const highlight = (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    };
    
    const unhighlight = (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
    };
    
    dropzone.addEventListener('dragenter', highlight, false);
    dropzone.addEventListener('dragover', highlight, false);
    dropzone.addEventListener('dragleave', unhighlight, false);
    dropzone.addEventListener('drop', (e) => {
        unhighlight(e);
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleSelectedFile(files[0]);
        }
    }, false);
    
    selectFileBtn.addEventListener('click', () => {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleSelectedFile(e.target.files[0]);
        }
    });
    
    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetFileInput();
    });
    
    const handleSelectedFile = (file) => {
        if (file.type !== 'application/pdf') {
            alert('Please select a valid PDF resume file.');
            return;
        }
        selectedFile = file;
        selectedFileName.textContent = file.name;
        selectedFileSize.textContent = formatBytes(file.size);
        
        dropzoneContent.classList.add('hidden');
        dropzoneFileInfo.classList.remove('hidden');
        
        validateForm();
    };
    
    const resetFileInput = () => {
        selectedFile = null;
        fileInput.value = '';
        dropzoneContent.classList.remove('hidden');
        dropzoneFileInfo.classList.add('hidden');
        validateForm();
    };
    
    const formatBytes = (bytes, decimals = 2) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    };
    
    // --- JD Template Handler ---
    jobTemplatesSelect.addEventListener('change', (e) => {
        const role = e.target.value;
        if (jobTemplates[role]) {
            jobDescTextarea.value = jobTemplates[role];
            validateForm();
        }
    });
    
    jobDescTextarea.addEventListener('input', validateForm);
    
    // --- Validate Form ---
    function validateForm() {
        const hasFile = selectedFile !== null;
        const hasJd = jobDescTextarea.value.trim().length > 0;
        analyzeBtn.disabled = !(hasFile && hasJd);
    }
    
    // --- Accordions logic ---
    const toggles = document.querySelectorAll('.accordion-toggle');
    toggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            const panel = toggle.parentElement;
            const content = panel.querySelector('.accordion-content');
            
            // Check if this panel is already open
            const isOpen = panel.classList.contains('expanded');
            
            // Close all panels
            document.querySelectorAll('.accordion-panel').forEach(p => {
                p.classList.remove('expanded');
                p.querySelector('.accordion-content').style.maxHeight = '0px';
            });
            
            // If it wasn't open, open it
            if (!isOpen) {
                panel.classList.add('expanded');
                content.style.maxHeight = content.scrollHeight + 'px';
            }
        });
    });
    
    // --- Form Submission / Analysis ---
    analyzeBtn.addEventListener('click', () => {
        if (!selectedFile || !jobDescTextarea.value.trim()) return;
        
        // Form Data
        const formData = new FormData();
        formData.append('resume', selectedFile);
        formData.append('job_desc', jobDescTextarea.value);
        formData.append('api_key', apiKeyInput.value);
        
        // Show Loading Screen
        homeView.classList.add('hidden');
        loadingView.classList.remove('hidden');
        
        // Loading animation progress variables
        let progress = 0;
        let analysisDone = false;
        let responseData = null;
        let responseError = null;
        
        const updateProgressBar = () => {
            if (responseError) {
                progressBarFill.style.width = '0%';
                alert(responseError);
                // Return to home view
                loadingView.classList.add('hidden');
                homeView.classList.remove('hidden');
                return;
            }
            
            if (progress >= 100) {
                // Done loading
                setTimeout(() => {
                    renderReport(responseData);
                    loadingView.classList.add('hidden');
                    reportView.classList.remove('hidden');
                }, 400);
                return;
            }
            
            // Stagger loading messages based on progress
            if (progress < 25) {
                loadingTitle.textContent = "Extracting Resume Content";
                loadingMessage.textContent = "Parsing layout elements and character layers from PDF document...";
                document.getElementById('step-1').className = "step-msg active";
            } else if (progress < 50) {
                loadingTitle.textContent = "Analyzing Role Requirements";
                loadingMessage.textContent = "Structuring target qualifications and key skills from job description...";
                document.getElementById('step-1').className = "step-msg done";
                document.getElementById('step-2').className = "step-msg active";
            } else if (progress < 75) {
                loadingTitle.textContent = "Computing Semantic Alignment";
                loadingMessage.textContent = "Comparing resume achievements using sentence embedding similarity...";
                document.getElementById('step-2').className = "step-msg done";
                document.getElementById('step-3').className = "step-msg active";
            } else if (progress < 95) {
                loadingTitle.textContent = "Synthesizing ATS Readability Matrix";
                loadingMessage.textContent = "Checking grammar styles, heading hierarchy, and token accessibility...";
                document.getElementById('step-3').className = "step-msg done";
                document.getElementById('step-4').className = "step-msg active";
            } else {
                loadingTitle.textContent = "Completing Agent Report";
                loadingMessage.textContent = "Finalizing JSON evaluation and compiling actionable bullet points...";
            }
            
            // Increment progress
            if (analysisDone) {
                progress += 5; // Fast completion
            } else {
                if (progress < 95) {
                    progress += 1; // Slow ticks while waiting
                }
            }
            
            progressBarFill.style.width = progress + '%';
            setTimeout(updateProgressBar, progress < 95 ? 100 : 50);
        };
        
        // Start Progress Ticks
        updateProgressBar();
        
        // Execute API Request
        fetch('/api/analyze', {
            method: 'POST',
            body: formData
        })
        .then(async (res) => {
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.error || "Failed to analyze resume.");
            }
            return data;
        })
        .then(data => {
            responseData = data;
            analysisDone = true;
            document.getElementById('step-4').className = "step-msg done";
        })
        .catch(err => {
            responseError = err.message || "An unexpected error occurred.";
        });
    });
    
    // --- Render Analysis Results to DOM ---
    const renderReport = (data) => {
        try {
            if (!data) return;
            
            // 1. Overall Resume Score & Gauge Sweep
            const score = data.resume_score || 0;
        overallScoreText.textContent = `${score}/100`;
        
        // Gauge Dashoffset Calculation
        // SVG circumference of semi-circle = 251.2
        // offset = 251.2 - (score / 100) * 251.2
        const strokeOffset = 251.2 - (score / 100) * 251.2;
        
        // Reset path first
        gaugeArc.style.strokeDashoffset = '251.2';
        
        // Trigger repaint to animate
        setTimeout(() => {
            gaugeArc.style.strokeDashoffset = strokeOffset;
        }, 150);
        
        // Adjust gauge fill color based on score
        if (score < 50) {
            gaugeArc.style.stroke = '#ef4444'; // Red
        } else if (score < 80) {
            gaugeArc.style.stroke = '#f59e0b'; // Yellow/Orange
        } else {
            gaugeArc.style.stroke = '#10b981'; // Green
        }
        
        // 2. Score Breakdown items
        const renderBadge = (element, status) => {
            element.textContent = status;
            element.className = 'badge'; // Reset
            
            const normalizedStatus = status.toLowerCase();
            if (normalizedStatus.includes('excellent') || normalizedStatus.includes('strong') || normalizedStatus.includes('good match')) {
                element.classList.add('badge-excellent');
            } else if (normalizedStatus.includes('needs work') || normalizedStatus.includes('improve')) {
                element.classList.add('badge-needs-work');
            } else {
                element.classList.add('badge-good-start'); // Fallback to orange "Good Start"
            }
        };
        
        const toneStyleData = data.categories.tone_style;
        scoreTone.textContent = `${toneStyleData.score}/100`;
        renderBadge(badgeTone, toneStyleData.status);
        accBadgeTone.textContent = `${toneStyleData.score}/100`;
        panelToneText.textContent = toneStyleData.details;
        
        const contentData = data.categories.content;
        scoreContent.textContent = `${contentData.score}/100`;
        renderBadge(badgeContent, contentData.status);
        accBadgeContent.textContent = `${contentData.score}/100`;
        panelContentText.textContent = contentData.details;
        
        const structureData = data.categories.structure;
        scoreStructure.textContent = `${structureData.score}/100`;
        renderBadge(badgeStructure, structureData.status);
        accBadgeStructure.textContent = `${structureData.score}/100`;
        panelStructureText.textContent = structureData.details;
        
        const skillsData = data.categories.skills;
        scoreSkills.textContent = `${skillsData.score}/100`;
        renderBadge(badgeSkills, skillsData.status);
        accBadgeSkills.textContent = `${skillsData.score}/100`;
        
        // 3. ATS Score Card Alert container
        const atsScore = data.ats_score || 0;
        atsScoreTitle.textContent = `ATS Score - ${atsScore}/100`;
        atsStatusText.textContent = data.ats_status;
        
        // Clean previous status styling classes
        atsCardContainer.className = 'metric-card ats-score-card';
        const warningIcon = atsWarningIcon.querySelector('i');
        
        if (atsScore < 50) {
            atsCardContainer.classList.add('border-needs-work');
            warningIcon.className = 'fa-solid fa-circle-exclamation';
        } else if (atsScore < 80) {
            atsCardContainer.classList.add('border-good-start');
            warningIcon.className = 'fa-solid fa-triangle-exclamation';
        } else {
            atsCardContainer.classList.add('border-excellent');
            warningIcon.className = 'fa-solid fa-circle-check';
        }
        
        // Render warning items in ATS card
        atsWarningsUl.innerHTML = '';
        if (data.ats_warnings && data.ats_warnings.length > 0) {
            data.ats_warnings.forEach(warning => {
                const li = document.createElement('li');
                li.className = 'ats-warning-item';
                
                let iconClass = 'fa-solid fa-triangle-exclamation';
                if (atsScore >= 80) {
                    iconClass = 'fa-solid fa-check';
                }
                
                li.innerHTML = `<i class="${iconClass}"></i> <span>${warning}</span>`;
                atsWarningsUl.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.className = 'ats-warning-item';
            li.innerHTML = `<i class="fa-solid fa-check"></i> <span>No critical ATS parsing warnings. The document layout is well optimized.</span>`;
            atsWarningsUl.appendChild(li);
        }
        
        // 4. Detailed Skills chips
        matchedSkillsChips.innerHTML = '';
        if (data.matched_skills && data.matched_skills.length > 0) {
            data.matched_skills.forEach(skill => {
                const span = document.createElement('span');
                span.className = 'chip chip-matched';
                span.textContent = skill;
                matchedSkillsChips.appendChild(span);
            });
        } else {
            matchedSkillsChips.innerHTML = '<span class="resume-body-text">No matched keywords found.</span>';
        }
        
        missingSkillsChips.innerHTML = '';
        if (data.missing_skills && data.missing_skills.length > 0) {
            data.missing_skills.forEach(skill => {
                const span = document.createElement('span');
                span.className = 'chip chip-missing';
                span.textContent = skill;
                missingSkillsChips.appendChild(span);
            });
        } else {
            missingSkillsChips.innerHTML = '<span class="resume-body-text" style="color: #047857;">Excellent! No missing requirements.</span>';
        }
        
        // 5. Styled Resume preview document
        const parsed = data.parsed_resume || {};
        resName.textContent = parsed.name || "Candidate Name";
        
        // Clear contacts row
        let contactsHtml = '';
        if (parsed.email && parsed.email !== "Email not found") {
            contactsHtml += `<span>${parsed.email}</span>`;
        }
        if (parsed.phone && parsed.phone !== "Phone not found") {
            if (contactsHtml) contactsHtml += ' • ';
            contactsHtml += `<span>${parsed.phone}</span>`;
        }
        if (parsed.address && parsed.address !== "Address not found") {
            if (contactsHtml) contactsHtml += ' • ';
            contactsHtml += `<span>${parsed.address}</span>`;
        }
        resContacts.innerHTML = contactsHtml || 'No contact credentials detected';
        
        resSummary.textContent = parsed.summary || 'Professional profile not found.';
        
        // Map lists
        const populateList = (element, items) => {
            element.innerHTML = '';
            if (items && items.length > 0) {
                items.forEach(item => {
                    // Check if it looks like empty/placeholder fallback
                    if (item && !item.toLowerCase().includes('no work experience') && !item.toLowerCase().includes('no education') && !item.toLowerCase().includes('no project')) {
                        const li = document.createElement('li');
                        li.className = 'resume-body-text';
                        li.textContent = item;
                        element.appendChild(li);
                    }
                });
            }
            
            // If empty, show fallback
            if (element.children.length === 0) {
                element.innerHTML = '<li class="resume-body-text" style="list-style: none; color: #64748b; font-style: italic;">No specific details reported under this section.</li>';
            }
        };
        
        populateList(resExperience, parsed.experience);
        populateList(resProjects, parsed.projects);
        populateList(resEducation, parsed.education);
        
            // Apply staggering animations to list items on render
            const warningItems = document.querySelectorAll('.ats-warning-item');
            warningItems.forEach((item, index) => {
                item.style.opacity = '0';
                item.style.animation = `fadeInUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) ${0.2 + (index * 0.08)}s forwards`;
            });
        } catch (error) {
            console.error('Error rendering report:', error);
            loadingView.classList.add('hidden');
            homeView.classList.remove('hidden');
            alert('The report could not be rendered. Please try again.');
        }
    };
    
    // --- Navigation back home ---
    backHomeBtn.addEventListener('click', () => {
        reportView.classList.add('hidden');
        homeView.classList.remove('hidden');
        
        // Reset file input
        resetFileInput();
    });
});
