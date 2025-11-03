document.addEventListener('DOMContentLoaded', () => {
    const summaryTableBody = document.getElementById('summary-table-body');

    const fetchSummary = async () => {
        try {
            const response = await fetch('/api/v1/analysis/feedback-summary');
            if (!response.ok) {
                throw new Error('Failed to fetch analysis summary');
            }
            const summaryData = await response.json();
            renderSummary(summaryData);
        } catch (error) {
            console.error('Error fetching summary:', error);
            summaryTableBody.innerHTML = '<tr><td colspan="3" class="text-center text-danger">Failed to load summary.</td></tr>';
        }
    };

    const renderSummary = (summary) => {
        summaryTableBody.innerHTML = '';
        if (!summary || summary.length === 0) {
            summaryTableBody.innerHTML = '<tr><td colspan="3" class="text-center">No bad feedback data found.</td></tr>';
            return;
        }

        summary.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.reason_code || 'N/A'}</td>
                <td>${item.concept_name || 'N/A'}</td>
                <td>${item.count}</td>
            `;
            summaryTableBody.appendChild(row);
        });
    };

    // Initial fetch
    fetchSummary();
});
