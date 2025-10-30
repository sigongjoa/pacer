document.addEventListener('DOMContentLoaded', () => {
    const logsContainer = document.getElementById('logs-container');
    const refreshBtn = document.getElementById('refresh-btn');

    const API_BASE_URL = 'http://127.0.0.1:8000';

    const fetchLogs = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/filter/logs`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const logs = await response.json();
            renderLogs(logs);
        } catch (error) {
            logsContainer.innerHTML = `<p style="color: red;">로그를 불러오는 데 실패했습니다: ${error.message}</p><p>백엔드 서버가 실행 중인지, CORS 설정이 올바른지 확인하세요.</p>`;
            console.error('Error fetching logs:', error);
        }
    };

    const renderLogs = (logs) => {
        logsContainer.innerHTML = '';
        if (logs.length === 0) {
            logsContainer.innerHTML = '<p>표시할 로그가 없습니다.</p>';
            return;
        }

        logs.forEach(log => {
            const logElement = document.createElement('div');
            logElement.className = 'log-item';
            logElement.innerHTML = `
                <p><strong>Log ID:</strong> ${log.log_id}</p>
                <p><strong>LLM 결정:</strong> ${log.decision}</p>
                <p class="reason"><strong>판단 근거:</strong> ${log.reason}</p>
                <p><strong>코치 피드백:</strong> ${log.coach_feedback || '아직 없음'}</p>
                <div class="feedback-buttons">
                    <button class="btn-good" data-log-id="${log.log_id}" data-feedback="GOOD">👍 좋음</button>
                    <button class="btn-bad" data-log-id="${log.log_id}" data-feedback="BAD">👎 나쁨</button>
                </div>
            `;
            logsContainer.appendChild(logElement);
        });
    };

    const submitFeedback = async (logId, feedback) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/filter/feedback`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    log_id: logId,
                    coach_id: 'coach-001', // 하드코딩된 코치 ID
                    feedback: feedback,
                }),
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            await response.json();
            fetchLogs(); // 피드백 제출 후 목록 새로고침
        } catch (error) {
            alert(`피드백 제출에 실패했습니다: ${error.message}`);
            console.error('Error submitting feedback:', error);
        }
    };

    logsContainer.addEventListener('click', (event) => {
        if (event.target.tagName === 'BUTTON' && event.target.dataset.logId) {
            const logId = event.target.dataset.logId;
            const feedback = event.target.dataset.feedback;
            submitFeedback(logId, feedback);
        }
    });

    refreshBtn.addEventListener('click', fetchLogs);

    // 초기 로드
    fetchLogs();
});
