interface AnalysisResults {
    transcript: string;
    corrected_transcript: string;
    word_count: number;
    sentence_count: number;
    paragraph_count: number;
    letter_count: number;
    rate_of_speech_points: [number, number][];
    volume_points: Record<string, number>;
    tone_scores?: Record<string, number>;
    parts_of_speech: Record<string, number>;
    grammar_mistakes: [[number, number], string, string][];
    custom_tone_results: [number, string, string][];
    hand_position_results: string;
    gaze_x?: number[];
    gaze_y?: number[];
    aus_sum: number;
    blinks: number;
    active: number;
    passive: number;
    readability_score: string;
    cefr: string;
    ielts: string;
    floss_spans: [number, number][];
}

declare const Chart: any;
declare const html2canvas: any;
declare const jspdf: any;

document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const jobId = urlParams.get('job_id');

    const loadingMessage = document.getElementById('loadingMessage') as HTMLDivElement;
    const errorMessage = document.getElementById('errorMessage') as HTMLDivElement;
    const resultsContent = document.getElementById('resultsContent') as HTMLDivElement;
    const downloadPdfBtn = document.getElementById('downloadPdfBtn') as HTMLButtonElement;

    if (!jobId) {
        showError("No Job ID provided.");
        return;
    }

    // Load User Info
    const userInfoStr = sessionStorage.getItem('userInfo');
    if (userInfoStr) {
        const userInfo = JSON.parse(userInfoStr);
        (document.getElementById('display-name') as HTMLElement).textContent = userInfo.name;
        (document.getElementById('display-age') as HTMLElement).textContent = userInfo.age;
        (document.getElementById('display-org') as HTMLElement).textContent = userInfo.organization;
        (document.getElementById('display-role') as HTMLElement).textContent = userInfo.role;
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

    } catch (err: any) {
        showError(err.message);
    }

    function showError(msg: string) {
        loadingMessage.classList.add('hidden');
        errorMessage.textContent = msg;
        errorMessage.classList.remove('hidden');
    }

    function renderResults(results: AnalysisResults) {
        // Scores
        (document.getElementById('score-cefr') as HTMLElement).textContent = results.cefr || '-';
        (document.getElementById('score-ielts') as HTMLElement).textContent = results.ielts || '-';
        (document.getElementById('score-readability') as HTMLElement).textContent = results.readability_score || '-';

        // Transcript
        const transcriptContainer = document.getElementById('transcript-content') as HTMLDivElement;
        transcriptContainer.innerHTML = results.corrected_transcript; // It already contains <c> tags from backend

        // Add tooltips/interactions for <c> tags
        // Note: The backend returns <c>highlighted</c>. We need to match mistakes to these.
        // The backend logic was:
        // highlighted_text = ... <c>...</c> ...
        // grammar_mistakes = [[start, end], correct, incorrect]
        // Since we are just rendering HTML, we can use the data attributes if we modify backend to include them,
        // OR we can just rely on the visual highlight for now as "Simple TS" implies.
        // To make it better, let's assume the backend could have added data attributes, but it didn't.
        // For now, we just show the highlights.

        // Metrics
        (document.getElementById('metric-blinks') as HTMLElement).textContent = results.blinks.toString();
        (document.getElementById('metric-aus') as HTMLElement).textContent = results.aus_sum.toString();
        (document.getElementById('metric-active') as HTMLElement).textContent = results.active.toString();
        (document.getElementById('metric-passive') as HTMLElement).textContent = results.passive.toString();

        // Charts
        renderRateChart(results.rate_of_speech_points);
        renderVolumeChart(results.volume_points);
        renderToneChart(results.custom_tone_results);
        renderPosChart(results.parts_of_speech);
        renderGazeChart(results.gaze_x, results.gaze_y);
    }

    function renderRateChart(data: [number, number][]) {
        const ctx = (document.getElementById('rateChart') as HTMLCanvasElement).getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d[0].toFixed(1)),
                datasets: [{
                    label: 'Words per Minute',
                    data: data.map(d => d[1]),
                    borderColor: 'rgb(79, 70, 229)',
                    tension: 0.1
                }]
            }
        });
    }

    function renderVolumeChart(data: Record<string, number>) {
        const ctx = (document.getElementById('volumeChart') as HTMLCanvasElement).getContext('2d');
        const labels = Object.keys(data).sort((a, b) => parseFloat(a) - parseFloat(b));
        const values = labels.map(k => data[k]);

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels.map(l => parseFloat(l).toFixed(1)),
                datasets: [{
                    label: 'Volume (RMS)',
                    data: values,
                    borderColor: 'rgb(220, 38, 38)',
                    tension: 0.1
                }]
            }
        });
    }

    function renderToneChart(data: [number, string, string][]) {
        if (!data) return;
        const ctx = (document.getElementById('toneChart') as HTMLCanvasElement).getContext('2d');

        // Count occurrences of each tone
        const toneCounts: Record<string, number> = {};
        data.forEach(item => {
            const tone = item[2]; // Assuming item[2] is the label
            toneCounts[tone] = (toneCounts[tone] || 0) + 1;
        });

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(toneCounts),
                datasets: [{
                    data: Object.values(toneCounts),
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'
                    ]
                }]
            }
        });
    }

    function renderPosChart(data: Record<string, number>) {
        const ctx = (document.getElementById('posChart') as HTMLCanvasElement).getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Count',
                    data: Object.values(data),
                    backgroundColor: 'rgba(75, 192, 192, 0.6)'
                }]
            }
        });
    }

    function renderGazeChart(x?: number[], y?: number[]) {
        if (!x || !y) return;
        const ctx = (document.getElementById('gazeChart') as HTMLCanvasElement).getContext('2d');

        const scatterData = x.map((val, i) => ({ x: val, y: y[i] }));

        new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Gaze Points',
                    data: scatterData,
                    backgroundColor: 'rgba(255, 99, 132, 0.5)'
                }]
            },
            options: {
                scales: {
                    x: { min: -1, max: 1 },
                    y: { min: -1, max: 1 }
                }
            }
        });
    }

    // PDF Download
    downloadPdfBtn.addEventListener('click', async () => {
        const { jsPDF } = jspdf;
        const element = document.getElementById('results-capture');
        if (!element) return;

        try {
            const canvas = await html2canvas(element, {
                scale: 2,
                useCORS: true,
                backgroundColor: '#dbc7fe'
            });

            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF('l', 'mm', 'a4');
            const imgProps = pdf.getImageProperties(imgData);
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;

            pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
            pdf.save('analysis-results.pdf');
        } catch (err) {
            console.error(err);
            alert("Failed to generate PDF");
        }
    });
});
