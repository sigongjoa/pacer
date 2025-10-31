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

        fetchStudents(); // Initial load
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
