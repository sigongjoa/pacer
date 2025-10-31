document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://127.0.0.1:8000';

    // --- Student Management App Logic ---
    const studentManagementApp = document.getElementById('student-management-app');
    if (studentManagementApp) {
        const createStudentForm = document.getElementById('create-student-form');
        const studentList = document.getElementById('student-list').querySelector('tbody');
        const refreshStudentsBtn = document.getElementById('refresh-students-btn');
        const editModal = document.getElementById('edit-student-modal');
        const editForm = document.getElementById('edit-student-form');
        const closeModalBtn = editModal.querySelector('.close-btn');

        let studentsCache = []; // Cache to hold student data for editing

        const openEditModal = (student) => {
            document.getElementById('edit-student-id').value = student.student_id;
            document.getElementById('edit-student-id-display').textContent = student.student_id;
            document.getElementById('edit-student-name-display').textContent = student.name;
            const budget = student.settings?.anki_budget_per_day || 0;
            document.getElementById('edit-student-budget').value = budget;
            editModal.classList.remove('hidden');
        };

        const closeEditModal = () => {
            editModal.classList.add('hidden');
        };

        const handleUpdateStudent = async (event) => {
            event.preventDefault();
            const studentId = document.getElementById('edit-student-id').value;
            const budget = document.getElementById('edit-student-budget').value;
            const payload = {
                settings: { anki_budget_per_day: parseInt(budget, 10) }
            };

            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/student/${studentId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
                }
                closeEditModal();
                fetchStudents(); // Refresh the list
            } catch (error) {
                alert(`학생 정보 수정에 실패했습니다: ${error.message}`);
            }
        };

        const renderStudents = (students) => {
            studentsCache = students; // Update cache
            studentList.innerHTML = '';
            if (!students || students.length === 0) {
                studentList.innerHTML = '<tr><td colspan="4">등록된 학생이 없습니다.</td></tr>';
                return;
            }
            students.forEach(student => {
                const row = document.createElement('tr');
                const settings = student.settings || {};
                const budget = settings.anki_budget_per_day || 'N/A';
                row.innerHTML = `
                    <td>${student.student_id}</td>
                    <td>${student.name}</td>
                    <td>${budget}</td>
                    <td><button data-student-id="${student.student_id}">수정</button></td>
                `;
                studentList.appendChild(row);
            });
        };

        const fetchStudents = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/student/`);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const students = await response.json();
                renderStudents(students);
            } catch (error) {
                studentList.innerHTML = `<tr><td colspan="4" style="color: red;">학생 목록을 불러오는 데 실패했습니다: ${error.message}</td></tr>`;
            }
        };

        const createStudent = async (event) => {
            event.preventDefault();
            const id = document.getElementById('student-id').value;
            const name = document.getElementById('student-name').value;
            const budget = document.getElementById('student-budget').value;

            const studentData = {
                student_id: id,
                name: name,
                settings: { anki_budget_per_day: parseInt(budget, 10) }
            };

            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/student/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(studentData),
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
                }
                createStudentForm.reset();
                fetchStudents();
            } catch (error) {
                alert(`학생 생성에 실패했습니다: ${error.message}`);
            }
        };

        createStudentForm.addEventListener('submit', createStudent);
        refreshStudentsBtn.addEventListener('click', fetchStudents);

        // Event delegation for edit buttons
        studentList.addEventListener('click', (event) => {
            if (event.target.tagName === 'BUTTON' && event.target.dataset.studentId) {
                const studentId = event.target.dataset.studentId;
                const studentToEdit = studentsCache.find(s => s.student_id === studentId);
                if (studentToEdit) {
                    openEditModal(studentToEdit);
                }
            }
        });

        // Listeners for closing the modal
        closeModalBtn.addEventListener('click', closeEditModal);
        window.addEventListener('click', (event) => {
            if (event.target == editModal) {
                closeEditModal();
            }
        });

        // Listener for the edit form submission
        editForm.addEventListener('submit', handleUpdateStudent);

                const refreshStudentsBtn = document.getElementById('refresh-students-btn');

                const editModal = document.getElementById('edit-student-modal');

                const editForm = document.getElementById('edit-student-form');

                const closeModalBtn = editModal.querySelector('.close-btn');

        

                let studentsCache = []; // Cache to hold student data for editing

        

                const openEditModal = (student) => {

                    document.getElementById('edit-student-id').value = student.student_id;

                    document.getElementById('edit-student-id-display').textContent = student.student_id;

                    document.getElementById('edit-student-name-display').textContent = student.name;

                    const budget = student.settings?.anki_budget_per_day || 0;

                    document.getElementById('edit-student-budget').value = budget;

                    editModal.classList.remove('hidden');

                };

        

                const closeEditModal = () => {

                    editModal.classList.add('hidden');

                };

        

                const handleUpdateStudent = async (event) => {

                    event.preventDefault();

                    const studentId = document.getElementById('edit-student-id').value;

                    const budget = document.getElementById('edit-student-budget').value;

                    const payload = {

                        settings: { anki_budget_per_day: parseInt(budget, 10) }

                    };

        

                    try {

                        const response = await fetch(`${API_BASE_URL}/api/v1/student/${studentId}`, {

                            method: 'PUT',

                            headers: { 'Content-Type': 'application/json' },

                            body: JSON.stringify(payload),

                        });

                        if (!response.ok) {

                            const errorData = await response.json();

                            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);

                        }

                        closeEditModal();

                        fetchStudents(); // Refresh the list

                    } catch (error) {

                        alert(`학생 정보 수정에 실패했습니다: ${error.message}`);

                    }

                };

        

                const renderStudents = (students) => {

                    studentsCache = students; // Update cache

                    studentList.innerHTML = '';

                    if (!students || students.length === 0) {

                        studentList.innerHTML = '<tr><td colspan="4">등록된 학생이 없습니다.</td></tr>';

                        return;

                    }

                    students.forEach(student => {

                        const row = document.createElement('tr');

                        const settings = student.settings || {};

                        const budget = settings.anki_budget_per_day || 'N/A';

                        row.innerHTML = `

                            <td>${student.student_id}</td>

                            <td>${student.name}</td>

                            <td>${budget}</td>

                            <td><button data-student-id="${student.student_id}">수정</button></td>

                        `;

                        studentList.appendChild(row);

                    });

        

                    // Populate student dropdown for assignment submission

                    const submissionStudentSelect = document.getElementById('submission-student-id');

                    submissionStudentSelect.innerHTML = '';

                    students.forEach(student => {

                        const option = document.createElement('option');

                        option.value = student.student_id;

                        option.textContent = `${student.name} (${student.student_id})`;

                        submissionStudentSelect.appendChild(option);

                    });

                };

        

                const fetchStudents = async () => {

                    try {

                        const response = await fetch(`${API_BASE_URL}/api/v1/student/`);

                        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

                        const students = await response.json();

                        renderStudents(students);

                    } catch (error) {

                        studentList.innerHTML = `<tr><td colspan="4" style="color: red;">학생 목록을 불러오는 데 실패했습니다: ${error.message}</td></tr>`;

                    }

                };

        

                createStudentForm.addEventListener('submit', createStudent);

                refreshStudentsBtn.addEventListener('click', fetchStudents);

        

                // Event delegation for edit buttons

                studentList.addEventListener('click', (event) => {

                    if (event.target.tagName === 'BUTTON' && event.target.dataset.studentId) {

                        const studentId = event.target.dataset.studentId;

                        const studentToEdit = studentsCache.find(s => s.student_id === studentId);

                        if (studentToEdit) {

                            openEditModal(studentToEdit);

                        }

                    }

                });

        

                // Listeners for closing the modal

                closeModalBtn.addEventListener('click', closeEditModal);

                window.addEventListener('click', (event) => {

                    if (event.target == editModal) {

                        closeEditModal();

                    }

                });

        

                // Listener for the edit form submission

                editForm.addEventListener('submit', handleUpdateStudent);

        

                fetchStudents(); // Initial load

            }

        

                // --- Assignment Submission Logic ---

        

                const assignmentSubmissionApp = document.getElementById('assignment-submission-app');

        

                if (assignmentSubmissionApp) {

        

                    const submitAssignmentForm = document.getElementById('submit-assignment-form');

        

                    const submissionStudentSelect = document.getElementById('submission-student-id');

        

                    const submissionAssignmentIdInput = document.getElementById('submission-assignment-id');

        

                    const submissionAnswerTextarea = document.getElementById('submission-answer');

        

                    const submissionStatusDiv = document.getElementById('submission-status');

        

            

        

                    const submitAssignment = async (event) => {

        

                        event.preventDefault();

        

                        const studentId = submissionStudentSelect.value;

        

                        const assignmentId = submissionAssignmentIdInput.value;

        

                        const answer = submissionAnswerTextarea.value;

        

            

        

                        const submissionData = {

        

                            student_id: studentId,

        

                            assignment_id: assignmentId,

        

                            answer: answer

        

                        };

        

            

        

                        submissionStatusDiv.textContent = '과제 제출 중...';

        

                        try {

        

                            const response = await fetch(`${API_BASE_URL}/api/v1/submission/`, {

        

                                method: 'POST',

        

                                headers: { 'Content-Type': 'application/json' },

        

                                body: JSON.stringify(submissionData),

        

                            });

        

                            if (!response.ok) {

        

                                const errorData = await response.json();

        

                                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);

        

                            }

        

                            const result = await response.json();

        

                            submissionStatusDiv.innerHTML = `<p style="color: green;">제출 완료: ${result.message}</p>`;

        

                            if (result.judge_decision) {

        

                                submissionStatusDiv.innerHTML += `<p>LLM 판단: ${result.judge_decision}</p>`;

        

                            }

        

                            submitAssignmentForm.reset();

        

                        } catch (error) {

        

                            submissionStatusDiv.innerHTML = `<p style="color: red;">과제 제출 실패: ${error.message}</p>`;

        

                        }

        

                    };

        

            

        

                    submitAssignmentForm.addEventListener('submit', submitAssignment);

        

                }

        

            

        

                    // --- Coach Memos Logic ---

        

            

        

                    const coachMemosApp = document.getElementById('coach-memos-app');

        

            

        

                    if (coachMemosApp) {

        

            

        

                        const createMemoForm = document.getElementById('create-memo-form');

        

            

        

                        const memoStudentSelect = document.getElementById('memo-student-id');

        

            

        

                        const memoCoachIdInput = document.getElementById('memo-coach-id');

        

            

        

                        const memoTextarea = document.getElementById('memo-text');

        

            

        

                        const memosListDiv = document.getElementById('memos-list');

        

            

        

                        const refreshMemosBtn = document.getElementById('refresh-memos-btn');

        

            

        

                

        

            

        

                        const createMemo = async (event) => {

        

            

        

                            event.preventDefault();

        

            

        

                            const studentId = memoStudentSelect.value;

        

            

        

                            const coachId = memoCoachIdInput.value;

        

            

        

                            const memoText = memoTextarea.value;

        

            

        

                

        

            

        

                            const memoData = {

        

            

        

                                coach_id: coachId,

        

            

        

                                student_id: studentId,

        

            

        

                                memo_text: memoText

        

            

        

                            };

        

            

        

                

        

            

        

                            try {

        

            

        

                                const response = await fetch(`${API_BASE_URL}/api/v1/coach/memo`, {

        

            

        

                                    method: 'POST',

        

            

        

                                    headers: { 'Content-Type': 'application/json' },

        

            

        

                                    body: JSON.stringify(memoData),

        

            

        

                                });

        

            

        

                                if (!response.ok) {

        

            

        

                                    const errorData = await response.json();

        

            

        

                                    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);

        

            

        

                                }

        

            

        

                                createMemoForm.reset();

        

            

        

                                fetchMemosForStudent(studentId); // Refresh memos for the selected student

        

            

        

                            } catch (error) {

        

            

        

                                alert(`메모 작성 실패: ${error.message}`);

        

            

        

                            }

        

            

        

                        };

        

            

        

                

        

            

        

                        const renderMemos = (memos) => {

        

            

        

                            memosListDiv.innerHTML = '';

        

            

        

                            if (!memos || memos.length === 0) {

        

            

        

                                memosListDiv.innerHTML = '<p>등록된 메모가 없습니다.</p>';

        

            

        

                                return;

        

            

        

                            }

        

            

        

                            memos.forEach(memo => {

        

            

        

                                const memoElement = document.createElement('div');

        

            

        

                                memoElement.className = 'log-item'; // Reusing log-item style

        

            

        

                                memoElement.innerHTML = `

        

            

        

                                    <p><strong>메모 ID:</strong> ${memo.memo_id}</p>

        

            

        

                                    <p><strong>코치 ID:</strong> ${memo.coach_id}</p>

        

            

        

                                    <p><strong>학생 ID:</strong> ${memo.student_id}</p>

        

            

        

                                    <p><strong>내용:</strong> ${memo.memo_text}</p>

        

            

        

                                    <p><strong>작성일:</strong> ${new Date(memo.created_at).toLocaleString()}</p>

        

            

        

                                `;

        

            

        

                                memosListDiv.appendChild(memoElement);

        

            

        

                            });

        

            

        

                        };

        

            

        

                

        

            

        

                        const fetchMemosForStudent = async (studentId) => {

        

            

        

                            if (!studentId) {

        

            

        

                                memosListDiv.innerHTML = '<p>학생을 선택해주세요.</p>';

        

            

        

                                return;

        

            

        

                            }

        

            

        

                            try {

        

            

        

                                const response = await fetch(`${API_BASE_URL}/api/v1/coach/student/${studentId}/memos`);

        

            

        

                                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        

            

        

                                const memos = await response.json();

        

            

        

                                renderMemos(memos);

        

            

        

                            } catch (error) {

        

            

        

                                memosListDiv.innerHTML = `<p style="color: red;">메모를 불러오는 데 실패했습니다: ${error.message}</p>`;

        

            

        

                            }

        

            

        

                        };

        

            

        

                

        

            

        

                        createMemoForm.addEventListener('submit', createMemo);

        

            

        

                        memoStudentSelect.addEventListener('change', (event) => fetchMemosForStudent(event.target.value));

        

            

        

                        refreshMemosBtn.addEventListener('click', () => fetchMemosForStudent(memoStudentSelect.value));

        

            

        

                

        

            

        

                        // Initial load of memos if a student is pre-selected

        

            

        

                        if (memoStudentSelect.value) {

        

            

        

                            fetchMemosForStudent(memoStudentSelect.value);

        

            

        

                        }

        

            

        

                    }

        

            

        

                

        

            

        

                    // --- Weekly Report Logic ---

        

            

        

                    const weeklyReportApp = document.getElementById('weekly-report-app');

        

            

        

                    if (weeklyReportApp) {

        

            

        

                        const generateReportForm = document.getElementById('generate-report-form');

        

            

        

                        const reportStudentSelect = document.getElementById('report-student-id');

        

            

        

                        const reportStartDateInput = document.getElementById('report-start-date');

        

            

        

                        const reportEndDateInput = document.getElementById('report-end-date');

        

            

        

                        const reportDisplayDiv = document.getElementById('report-display');

        

            

        

                

        

            

        

                        const generateReport = async (event) => {

        

            

        

                            event.preventDefault();

        

            

        

                            const studentId = reportStudentSelect.value;

        

            

        

                            const startDate = reportStartDateInput.value;

        

            

        

                            const endDate = reportEndDateInput.value;

        

            

        

                

        

            

        

                            if (!studentId || !startDate || !endDate) {

        

            

        

                                reportDisplayDiv.innerHTML = '<p style="color: red;">학생, 시작일, 종료일을 모두 선택해주세요.</p>';

        

            

        

                                return;

        

            

        

                            }

        

            

        

                

        

            

        

                            reportDisplayDiv.textContent = '리포트 생성 중...';

        

            

        

                            try {

        

            

        

                                const response = await fetch(`${API_BASE_URL}/api/v1/report/student/${studentId}/period?start_date=${startDate}&end_date=${endDate}`);

        

            

        

                                if (!response.ok) {

        

            

        

                                    const errorData = await response.json();

        

            

        

                                    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);

        

            

        

                                }

        

            

        

                                const report = await response.json();

        

            

        

                                renderReport(report);

        

            

        

                            } catch (error) {

        

            

        

                                reportDisplayDiv.innerHTML = `<p style="color: red;">리포트 생성 실패: ${error.message}</p>`;

        

            

        

                            }

        

            

        

                        };

        

            

        

                

        

            

        

                        const renderReport = (report) => {

        

            

        

                            reportDisplayDiv.innerHTML = `

        

            

        

                                <h3>${report.student_name} 학생 주간 리포트 (${report.report_period_start} ~ ${report.report_period_end})</h3>

        

            

        

                                <p><strong>총 제출 과제 수:</strong> ${report.total_submissions}</p>

        

            

        

                                <p><strong>LLM 판단 건수:</strong> ${report.llm_judgments_count}</p>

        

            

        

                                <p><strong>복습한 Anki 카드 수:</strong> ${report.anki_cards_reviewed_count}</p>

        

            

        

                                <p><strong>새로 생성된 Anki 카드 수:</strong> ${report.new_anki_cards_created_count}</p>

        

            

        

                                <h4>전체 요약:</h4>

        

            

        

                                <p>${report.overall_summary}</p>

        

            

        

                                

        

            

        

                                <h4>Anki 카드 요약:</h4>

        

            

        

                                <ul>

        

            

        

                                    ${report.anki_card_summaries.map(card => `

        

            

        

                                        <li>ID: ${card.card_id}, 질문: ${card.question}, 다음 복습일: ${card.next_review_date}, 반복: ${card.repetitions}회</li>

        

            

        

                                    `).join('')}

        

            

        

                                </ul>

        

            

        

                

        

            

        

                                <h4>LLM 판단 로그 요약:</h4>

        

            

        

                                <ul>

        

            

        

                                    ${report.llm_log_summaries.map(log => `

        

            

        

                                        <li>ID: ${log.log_id}, 제출물: ${log.submission_id}, 결정: ${log.decision}, 이유: ${log.reason}</li>

        

            

        

                                    `).join('')}

        

            

        

                                </ul>

        

            

        

                

        

            

        

                                <h4>코치 메모 요약:</h4>

        

            

        

                                <ul>

        

            

        

                                    ${report.coach_memo_summaries.map(memo => `

        

            

        

                                        <li>ID: ${memo.memo_id}, 코치: ${memo.coach_id}, 내용: ${memo.memo_text}</li>

        

            

        

                                    `).join('')}

        

            

        

                                </ul>

        

            

        

                            `;

        

            

        

                        };

        

            

        

                

        

            

        

                        generateReportForm.addEventListener('submit', generateReport);

        

            

        

                

        

            

        

                        // Set default dates for convenience

        

            

        

                        const today = new Date();

        

            

        

                        const sevenDaysAgo = new Date(today);

        

            

        

                        sevenDaysAgo.setDate(today.getDate() - 7);

        

            

        

                        reportStartDateInput.value = sevenDaysAgo.toISOString().split('T')[0];

        

            

        

                        reportEndDateInput.value = today.toISOString().split('T')[0];

        

            

        

                    }

        

            

        

                

        

            

        

                

        

            

        

                    // --- Coach App Logic ---
    const coachApp = document.getElementById('coach-app');
    if (coachApp) {
        const logsContainer = document.getElementById('logs-container');
        const refreshBtn = document.getElementById('refresh-btn');

        const fetchLogs = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/filter/logs`);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const logs = await response.json();
                renderLogs(logs);
            } catch (error) {
                logsContainer.innerHTML = `<p style="color: red;">로그를 불러오는 데 실패했습니다: ${error.message}</p>`;
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
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ log_id: logId, coach_id: 'coach-001', feedback: feedback }),
                });
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                await response.json();
                fetchLogs();
            } catch (error) {
                alert(`피드백 제출에 실패했습니다: ${error.message}`);
                console.error('Error submitting feedback:', error);
            }
        };

        logsContainer.addEventListener('click', (event) => {
            if (event.target.tagName === 'BUTTON' && event.target.dataset.logId) {
                submitFeedback(event.target.dataset.logId, event.target.dataset.feedback);
            }
        });

        refreshBtn.addEventListener('click', fetchLogs);
        fetchLogs(); // Initial load
    }

    // --- Student App Logic ---
    const studentApp = document.getElementById('student-app');
    if (studentApp) {
        const startBtn = document.getElementById('start-review-btn');
        const cardContainer = document.getElementById('card-container');
        const cardQuestion = document.getElementById('card-question');
        const showAnswerBtn = document.getElementById('show-answer-btn');
        const cardAnswer = document.getElementById('card-answer');
        const feedbackControls = document.getElementById('feedback-controls');
        const reviewStatus = document.getElementById('review-status');

        let currentDeck = [];
        let currentCardIndex = 0;
        const STUDENT_ID = 'student-budget-001'; // 테스트용 학생 ID

        const startReview = async () => {
            startBtn.disabled = true;
            reviewStatus.textContent = '오늘의 복습 카드를 불러오는 중...';
            try {
                let response = await fetch(`${API_BASE_URL}/api/v1/student/${STUDENT_ID}/daily_review_deck`);
                
                // 학생이 존재하지 않으면 (404), 새로 생성하고 다시 시도
                if (response.status === 404) {
                    reviewStatus.textContent = '학생 정보를 생성하는 중...';
                    const createStudentResponse = await fetch(`${API_BASE_URL}/api/v1/student/`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            student_id: STUDENT_ID, 
                            name: '테스트 학생', 
                            settings: { anki_budget_per_day: 5 }
                        }),
                    });
                    if (!createStudentResponse.ok) throw new Error('학생 생성에 실패했습니다.');
                    
                    reviewStatus.textContent = '학생 정보를 생성했습니다. 다시 카드를 불러옵니다...';
                    response = await fetch(`${API_BASE_URL}/api/v1/student/${STUDENT_ID}/daily_review_deck`);
                }

                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                
                const deckData = await response.json();
                currentDeck = deckData.due_cards;
                currentCardIndex = 0;
                startBtn.classList.add('hidden');

                if (currentDeck.length > 0) {
                    showNextCard();
                } else {
                    reviewStatus.textContent = '🎉 오늘은 복습할 카드가 없습니다!';
                    cardContainer.classList.add('hidden');
                }
            } catch (error) {
                reviewStatus.innerHTML = `<p style="color: red;">복습 카드를 불러오는 데 실패했습니다: ${error.message}</p>`;
                startBtn.disabled = false;
            }
        };

        const showNextCard = () => {
            if (currentCardIndex < currentDeck.length) {
                const card = currentDeck[currentCardIndex];
                cardContainer.classList.remove('hidden');
                cardQuestion.textContent = card.question;
                cardAnswer.textContent = card.answer;
                cardAnswer.classList.add('hidden');
                showAnswerBtn.classList.remove('hidden');
                feedbackControls.classList.add('hidden');
                reviewStatus.textContent = `카드 ${currentCardIndex + 1} / ${currentDeck.length}`;
            } else {
                cardContainer.classList.add('hidden');
                reviewStatus.innerHTML = '<h2>✨ 오늘의 복습 완료! 수고하셨습니다! ✨</h2>';
            }
        };

        const showAnswer = () => {
            cardAnswer.classList.remove('hidden');
            showAnswerBtn.classList.add('hidden');
            feedbackControls.classList.remove('hidden');
        };

        const submitReview = async (quality) => {
            const card = currentDeck[currentCardIndex];
            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/cards/${card.card_id}/review`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ quality: quality }),
                });
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                currentCardIndex++;
                showNextCard();
            } catch (error) {
                alert(`리뷰 제출에 실패했습니다: ${error.message}`);
            }
        };

        startBtn.addEventListener('click', startReview);
        showAnswerBtn.addEventListener('click', showAnswer);
        feedbackControls.addEventListener('click', (event) => {
            if (event.target.tagName === 'BUTTON') {
                submitReview(parseInt(event.target.dataset.quality, 10));
            }
        });
    }
});
