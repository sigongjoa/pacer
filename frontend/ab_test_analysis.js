document.addEventListener('DOMContentLoaded', () => {
    const abTestSummaryTableBody = document.getElementById('ab-test-summary-table-body');

    const fetchAbTestSummary = async () => {
        try {
            const response = await fetch('/api/v1/analysis/ab-test-summary');
            if (!response.ok) {
                throw new Error('Failed to fetch A/B test summary');
            }
            const summaryData = await response.json();
            renderAbTestSummary(summaryData);
        } catch (error) {
            console.error('Error fetching A/B test summary:', error);
            abTestSummaryTableBody.innerHTML = '<tr><td colspan="7" class="text-center text-danger">Failed to load A/B test summary.</td></tr>';
        }
    };

    const renderAbTestSummary = (summary) => {
        abTestSummaryTableBody.innerHTML = '';
        if (!summary || summary.length === 0) {
            abTestSummaryTableBody.innerHTML = '<tr><td colspan="7" class="text-center">No A/B test data found.</td></tr>';
            return;
        }

        summary.forEach(item => {
            const row = document.createElement('tr');
            const goodFeedbackRate = (item.good_feedback_rate * 100).toFixed(2);
            const badFeedbackRate = (item.bad_feedback_rate * 100).toFixed(2);
            
            let significanceClass = '';
            if (item.statistical_significance.includes("Significant")) {
                significanceClass = item.statistical_significance.includes("Not") ? 'text-warning' : 'text-success';
            }

            row.innerHTML = `
                <td>${item.model_version || 'N/A'}</td>
                <td>${item.total_requests}</td>
                <td>${item.good_feedback_count}</td>
                <td>${item.bad_feedback_count}</td>
                <td>${goodFeedbackRate}%</td>
                <td>${badFeedbackRate}%</td>
                <td class="${significanceClass}">${item.statistical_significance}</td>
            `;
            abTestSummaryTableBody.appendChild(row);
        });
    };

    // Initial fetch
    fetchAbTestSummary();
});