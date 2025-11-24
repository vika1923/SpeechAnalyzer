// Results page TypeScript - recreating legacy ResultsDisplay.tsx functionality
document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const jobId = urlParams.get('job_id');

    const loadingMessage = document.getElementById('loadingMessage');
    const errorMessage = document.getElementById('errorMessage');
    const resultsContent = document.getElementById('resultsContent');
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    const currentYearSpan = document.getElementById('currentYear');

    if (currentYearSpan) {
        currentYearSpan.textContent = new Date().getFullYear().toString();
    }

    if (!jobId) {
        showError("No Job ID provided.");
        return;
    }

    // Load User Info
    const userInfoStr = sessionStorage.getItem('userInfo');
    if (userInfoStr) {
        try {
            const userInfo = JSON.parse(userInfoStr);
            const userInfoSection = document.getElementById('userInfoSection');
            if (userInfoSection) {
                document.getElementById('display-user-name').textContent = userInfo.name || '-';
                document.getElementById('display-user-age').textContent = userInfo.age || '-';
                document.getElementById('display-user-org').textContent = userInfo.organization || '-';
                document.getElementById('display-user-role').textContent = userInfo.role || '-';
                userInfoSection.classList.remove('hidden');
            }
        } catch (e) {
            console.error('Failed to parse user info', e);
        }
    }

    try {
        const res = await fetch(`/api/job/${jobId}`);
        if (!res.ok) throw new Error("Failed to fetch results");

        const data = await res.json();
        if (data.status !== 'completed' || !data.results) {
            showError("Results not ready or failed.");
            return;
        }

        renderResults(data.results);
        loadingMessage.classList.add('hidden');
        resultsContent.classList.remove('hidden');

    } catch (err) {
        showError(err.message);
    }

    function showError(msg) {
        loadingMessage.classList.add('hidden');
        errorMessage.textContent = msg;
        errorMessage.classList.remove('hidden');
    }

    function renderResults(results) {
        // Linguistic counts
        document.getElementById('metric-letters').textContent = results.letter_count || '-';
        document.getElementById('metric-words').textContent = results.word_count || '-';
        document.getElementById('metric-sentences').textContent = results.sentence_count || '-';
        document.getElementById('metric-paragraphs').textContent = results.paragraph_count || '-';

        // Proficiency scores
        document.getElementById('metric-cefr').textContent = results.cefr || '-';
        document.getElementById('metric-ielts').textContent = results.ielts || '-';
        document.getElementById('metric-readability').textContent = results.readability_score || '-';

        // Sentiment Analysis
        if (results.custom_tone_results && results.custom_tone_results.length > 0) {
            const sentimentList = document.getElementById('sentiment-list');
            sentimentList.innerHTML = results.custom_tone_results.map(([score, label, emoji]) =>
                `<li class="flex items-center space-x-2">
                    <span class="text-2xl">${emoji}</span>
                    <span class="font-medium text-gray-800">${label}</span>
                    <span class="ml-auto font-semibold text-red-600">${(score * 100).toFixed(1)}%</span>
                </li>`
            ).join('');
        }

        if (results.extra_tone_results && results.extra_tone_results.length > 0) {
            const extraSection = document.getElementById('extra-sentiment-section');
            const extraList = document.getElementById('extra-sentiment-list');
            extraList.innerHTML = results.extra_tone_results.map(([score, label, emoji], idx) =>
                `<li class="flex items-center space-x-2">
                    <span class="font-bold text-gray-500 mr-2">${idx + 1}.</span>
                    <span class="text-2xl">${emoji}</span>
                    <span class="font-medium text-gray-800">${label}</span>
                </li>`
            ).join('');
            extraSection.classList.remove('hidden');
        }

        // Parts of Speech Chart
        if (results.parts_of_speech) {
            const posCtx = document.getElementById('posChart');
            const posData = Object.entries(results.parts_of_speech).map(([part, count]) => ({
                name: part.replace(/_/g, ' '),
                value: count
            }));

            new Chart(posCtx, {
                type: 'pie',
                data: {
                    labels: posData.map(d => d.name),
                    datasets: [{
                        data: posData.map(d => d.value),
                        backgroundColor: posData.map((_, i) => `hsl(${i * 60}, 70%, 50%)`)
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'right' }
                    }
                }
            });
        }

        // Active/Passive Chart
        const activePassiveCtx = document.getElementById('activePassiveChart');
        new Chart(activePassiveCtx, {
            type: 'bar',
            data: {
                labels: ['Active', 'Passive'],
                datasets: [{
                    label: 'Sentences',
                    data: [results.active || 0, results.passive || 0],
                    backgroundColor: ['#34d399', '#f87171']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, ticks: { precision: 0 } }
                }
            }
        });

        // Rate of Speech Chart
        if (results.rate_of_speech_points && results.rate_of_speech_points.length > 0) {
            const rateCtx = document.getElementById('rateChart');
            new Chart(rateCtx, {
                type: 'line',
                data: {
                    labels: results.rate_of_speech_points.map(([time]) => time.toFixed(1)),
                    datasets: [{
                        label: 'Words/Min',
                        data: results.rate_of_speech_points.map(([_, rate]) => (rate * 60).toFixed(1)),
                        borderColor: '#009688',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true }
                    },
                    plugins: { legend: { display: true } }
                }
            });
        }

        // Volume Chart
        if (results.volume_points) {
            const volumeCtx = document.getElementById('volumeChart');
            const volumeData = Object.entries(results.volume_points)
                .sort(([a], [b]) => parseFloat(a) - parseFloat(b));

            new Chart(volumeCtx, {
                type: 'bar',
                data: {
                    labels: volumeData.map(([time]) => `${Math.round(parseFloat(time))}s`),
                    datasets: [{
                        label: 'Volume',
                        data: volumeData.map(([_, vol]) => vol),
                        backgroundColor: '#fb923c'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }

        // Hand & Eye Activity
        if (results.hand_eye_activity_results) {
            const handActivity = results.hand_eye_activity_results.hand_activity;
            if (handActivity) {
                document.getElementById('hand-left').textContent = handActivity.left_hand_avg_activity;
                document.getElementById('hand-right').textContent = handActivity.right_hand_avg_activity;
                document.getElementById('hand-combined').textContent = handActivity.avg_combined_activity;
                document.getElementById('hand-distance').textContent = handActivity.total_distance_changes;
                document.getElementById('hand-avg-distance').textContent = handActivity.avg_distance_change_per_frame;
                document.getElementById('hand-activity-section').classList.remove('hidden');
            }

            const eyeActivity = results.hand_eye_activity_results.eye_activity;
            if (eyeActivity) {
                document.getElementById('eye-left').textContent = eyeActivity.left_eye_avg_activity;
                document.getElementById('eye-right').textContent = eyeActivity.right_eye_avg_activity;
                document.getElementById('eye-combined').textContent = eyeActivity.avg_combined_eye_activity;
                document.getElementById('eye-activity-section').classList.remove('hidden');
            }
        }

        // Stickman Visualization
        if (results.hand_position_results) {
            renderStickman(results.hand_position_results);
        }

        // Gaze Analysis
        renderGazePlot(results.gaze_x || [], results.gaze_y || []);

        // Transcripts
        const originalTranscript = document.getElementById('original-transcript');
        if (results.floss_spans && results.floss_spans.length > 0) {
            originalTranscript.innerHTML = applyUnderlines(results.transcript, results.floss_spans);
        } else {
            originalTranscript.textContent = results.transcript;
        }

        const correctedTranscript = document.getElementById('corrected-transcript');
        if (results.corrected_transcript) {
            correctedTranscript.innerHTML = results.corrected_transcript
                .replace(/\<c\>/g, '<span class="bg-yellow-300 px-1 rounded font-semibold underline decoration-wavy decoration-orange-500">')
                .replace(/\<\/c\>/g, '</span>');
        }

        // Copy button
        document.getElementById('copyBtn').addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(results.corrected_transcript || results.transcript);
                const alert = document.getElementById('copyAlert');
                alert.classList.remove('hidden');
                setTimeout(() => alert.classList.add('hidden'), 1000);
            } catch (e) {
                console.error('Failed to copy', e);
            }
        });

        // Grammar Suggestions
        if (results.grammar_mistakes && results.grammar_mistakes.length > 0) {
            const grammarList = document.getElementById('grammar-list');
            grammarList.innerHTML = results.grammar_mistakes.map(([range, suggestion, original]) =>
                `<li>"${original}" should be "${suggestion}"</li>`
            ).join('');
            document.getElementById('grammar-section').classList.remove('hidden');
        }
    }

    function applyUnderlines(text, spans) {
        if (!spans || spans.length === 0) return text;
        const sortedSpans = [...spans].sort((a, b) => b[0] - a[0]);
        let result = text;
        for (const [start, end] of sortedSpans) {
            if (start >= 0 && end <= text.length && start < end) {
                const before = result.slice(0, start);
                const underlined = result.slice(start, end);
                const after = result.slice(end);
                result = before + `<u class="text-red-600 decoration-2">${underlined}</u>` + after;
            }
        }
        return result;
    }

    function renderStickman(handPositionData) {
        const container = document.getElementById('stickman-container');
        const percentages = parseHandPositionData(handPositionData);

        const stickmanHTML = `
            <div class="relative inline-block group">
                <img src="/static/analysis/images/stickman.png" alt="Stickman" class="w-64 h-64 object-contain block" />
                ${createOverlay('uul', percentages.uul, 0, 0, '50%', '24%')}
                ${createOverlay('uur', percentages.uur, 0, '50%', '50%', '24%')}
                ${createOverlay('ul', percentages.ul, '24%', 0, '50%', '18%')}
                ${createOverlay('ur', percentages.ur, '24%', '50%', '50%', '18%')}
                ${createOverlay('dl', percentages.dl, '42%', 0, '50%', '15%')}
                ${createOverlay('dr', percentages.dr, '42%', '50%', '50%', '15%')}
                ${createOverlay('ddl', percentages.ddl, '57%', 0, '50%', '43%')}
                ${createOverlay('ddr', percentages.ddr, '57%', '50%', '50%', '43%')}
            </div>
        `;
        container.innerHTML = stickmanHTML;
    }

    function createOverlay(key, percentage, top, left, width, height) {
        const alpha = Math.max(0.1, Math.min(0.9, (percentage * 1.6) / 100));
        return `
            <div class="absolute flex items-center justify-center text-white text-xs font-semibold group"
                 style="top:${top};left:${left};width:${width};height:${height};background-color:rgba(59,130,246,${alpha})">
                <span class="px-2 py-1 rounded bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
                    ${(percentage || 0).toFixed(1)}%
                </span>
            </div>
        `;
    }

    function parseHandPositionData(data) {
        try {
            const boxesMatch = data.match(/'boxes_percentages':\s*{([^}]+)}/);
            if (!boxesMatch) return {};

            const percentages = {};
            const pairs = boxesMatch[1].split(',');
            pairs.forEach(pair => {
                const match = pair.match(/'([^']+)':\s*([\d.]+)/);
                if (match) percentages[match[1]] = parseFloat(match[2]);
            });
            return percentages;
        } catch (error) {
            console.error('Error parsing hand position data:', error);
            return {};
        }
    }

    function renderGazePlot(gazeX, gazeY) {
        const container = document.getElementById('gaze-container');
        if (!gazeX || !gazeY || gazeX.length === 0) {
            container.innerHTML = '<p class="text-yellow-700">No gaze data available.</p>';
            return;
        }

        const length = Math.min(gazeX.length, gazeY.length);
        const xs = gazeX.slice(0, length).map(v => Math.max(Math.min(v, 0.4), -0.4));
        const ys = gazeY.slice(0, length).map(v => Math.max(Math.min(v, 0.4), -0.4));

        const svg = `
            <div class="text-sm text-gray-600 mb-2">Samples: ${length}</div>
            <svg viewBox="0 0 100 100" class="w-full h-64 bg-white rounded-md border border-yellow-200">
                <rect x="10" y="6" width="85" height="82" fill="#fff" stroke="#ddd" stroke-width="0.5"/>
                <line x1="52.5" y1="6" x2="52.5" y2="88" stroke="#bbb" stroke-width="0.6"/>
                <line x1="10" y1="47" x2="95" y2="47" stroke="#bbb" stroke-width="0.6"/>
                <circle cx="52.5" cy="47" r="3" stroke="#f87171" stroke-width="0.7" fill="none"/>
                <circle cx="52.5" cy="47" r="6" stroke="#52a447" stroke-width="0.7" fill="none"/>
                ${xs.map((x, i) => {
            const cx = 52.5 + (x / 0.4) * 42.5;
            const cy = 47 - (ys[i] / 0.4) * 41;
            return `<circle cx="${cx}" cy="${cy}" r="1.5" fill="#eab308" fill-opacity="0.85"/>`;
        }).join('')}
                <text x="10" y="96" font-size="3" fill="#666" text-anchor="start">-0.4</text>
                <text x="52.5" y="96" font-size="3" fill="#666" text-anchor="middle">0</text>
                <text x="95" y="96" font-size="3" fill="#666" text-anchor="end">0.4</text>
                <text x="8" y="90" font-size="3" fill="#666" text-anchor="end">-0.4</text>
                <text x="8" y="48" font-size="3" fill="#666" text-anchor="end">0</text>
                <text x="8" y="9" font-size="3" fill="#666" text-anchor="end">0.4</text>
            </svg>
            <div class="flex justify-between text-xs text-gray-600 mt-1">
                <span>Left (neg)</span>
                <span>Right (pos)</span>
            </div>
        `;
        container.innerHTML = svg;
    }

    // PDF Download
    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener('click', async () => {
            const element = document.getElementById('results-capture');
            if (!element) return;

            try {
                const canvas = await html2canvas(element, {
                    scale: 2,
                    useCORS: true,
                    backgroundColor: '#dbc7fe'
                });

                const imgData = canvas.toDataURL('image/png');
                const { jsPDF } = window.jspdf;
                const pdf = new jsPDF('l', 'mm', 'a4');
                const pdfWidth = pdf.internal.pageSize.getWidth();
                const pdfHeight = pdf.internal.pageSize.getHeight();
                const imgWidth = pdfWidth;
                const imgHeight = (canvas.height * imgWidth) / canvas.width;

                if (imgHeight <= pdfHeight) {
                    pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
                } else {
                    // Paginate
                    const pxPerMm = canvas.width / imgWidth;
                    const pageHeightPx = pdfHeight * pxPerMm;
                    let positionPx = 0;
                    const pageCanvas = document.createElement('canvas');
                    pageCanvas.width = canvas.width;
                    pageCanvas.height = Math.floor(pageHeightPx);
                    const pageCtx = pageCanvas.getContext('2d');

                    while (positionPx < canvas.height) {
                        pageCtx.clearRect(0, 0, pageCanvas.width, pageCanvas.height);
                        pageCtx.drawImage(canvas, 0, positionPx, canvas.width, Math.min(pageHeightPx, canvas.height - positionPx), 0, 0, pageCanvas.width, Math.min(pageHeightPx, canvas.height - positionPx));
                        const pageData = pageCanvas.toDataURL('image/png');
                        pdf.addImage(pageData, 'PNG', 0, 0, imgWidth, pdfHeight);
                        positionPx += pageHeightPx;
                        if (positionPx < canvas.height) pdf.addPage('l');
                    }
                }

                pdf.save('analysis-results.pdf');
            } catch (e) {
                console.error('PDF generation failed', e);
                alert('Failed to generate PDF');
            }
        });
    }
});
