document.addEventListener('DOMContentLoaded', () => {
    const logsTableBody = document.getElementById('logsTableBody');
    const filterBtn = document.getElementById('filterBtn');

    const fetchLogs = async () => {
        const studentId = document.getElementById('studentIdFilter').value;
        const startDate = document.getElementById('startDateFilter').value;
        const endDate = document.getElementById('endDateFilter').value;

        let url = '/api/v1/filter/logs?';
        if (studentId) url += `student_id=${studentId}&`;
        if (startDate) url += `start_date=${startDate}&`;
        if (endDate) url += `end_date=${endDate}&`;

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Failed to fetch logs');
            }
            const logs = await response.json();
            renderLogs(logs);
        } catch (error) {
            console.error('Error fetching logs:', error);
            logsTableBody.innerHTML = '<tr><td colspan="6" class="text-center">Failed to load logs.</td></tr>';
        }
    };

    const renderLogs = (logs) => {
        logsTableBody.innerHTML = '';
        if (logs.length === 0) {
            logsTableBody.innerHTML = '<tr><td colspan="6" class="text-center">No logs found.</td></tr>';
            return;
        }

        logs.forEach(log => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${log.log_id}</td>
                <td>${log.submission_id}</td>
                <td>${log.decision}</td>
                <td>${log.reason}</td>
                <td>${new Date(log.created_at).toLocaleString()}</td>
                <td>
                    <button class="btn btn-success btn-sm" onclick="submitFeedback(${log.log_id}, 'GOOD')">👍 Good</button>
                    <button class="btn btn-danger btn-sm" onclick="showFeedbackModal(${log.log_id})">👎 Bad</button>
                </td>
            `;
            logsTableBody.appendChild(row);
        });
    };

    window.submitFeedback = async (logId, feedback, reasonCode = null) => {
        try {
            const response = await fetch('/api/v1/filter/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    log_id: logId.toString(),
                    coach_id: 'coach-007', // Hardcoded for now
                    feedback: feedback,
                    reason_code: reasonCode
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to submit feedback');
            }

            alert('Feedback submitted successfully!');
            fetchLogs(); // Refresh logs
        } catch (error) {
            console.error('Error submitting feedback:', error);
            alert('Failed to submit feedback.');
        }
    };

    window.showFeedbackModal = (logId) => {
        const reason = prompt("Reason for bad feedback (e.g., SIMPLE_MISTAKE, NOT_A_MISTAKE):");
        if (reason) {
            submitFeedback(logId, 'BAD', reason);
        }
    };

    filterBtn.addEventListener('click', fetchLogs);

    // Initial fetch
    fetchLogs();
});
