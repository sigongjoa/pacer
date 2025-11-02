document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://127.0.0.1:8001';

    // Kakao SDK 초기화
    if (typeof KAKAO_JS_KEY !== 'undefined' && Kakao && !Kakao.isInitialized()) {
        Kakao.init(KAKAO_JS_KEY);
    }

    // --- Student Management App Logic ---
    const studentManagementApp = document.getElementById('student-management-app');
    if (studentManagementApp) {
        const createStudentForm = document.getElementById('create-student-form');
        const studentList = document.getElementById('student-list').querySelector('tbody');
        const refreshStudentsBtn = document.getElementById('refresh-students-btn');
        const editModal = document.getElementById('edit-student-modal');
        const editForm = document.getElementById('edit-student-form');
        const closeModalBtn = editModal.querySelector('.close-btn');
        let studentsCache = [];

        const openEditModal = (student) => {
            document.getElementById('edit-student-id').value = student.student_id;
            document.getElementById('edit-student-id-display').textContent = student.student_id;
            document.getElementById('edit-student-name-display').textContent = student.name;
            document.getElementById('edit-student-budget').value = student.settings?.anki_budget_per_day || 0;
            editModal.classList.remove('hidden');
        };

        const closeEditModal = () => editModal.classList.add('hidden');

        const handleUpdateStudent = async (event) => {
            event.preventDefault();
            const studentId = document.getElementById('edit-student-id').value;
            const budget = document.getElementById('edit-student-budget').value;
            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/student/${studentId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ settings: { anki_budget_per_day: parseInt(budget, 10) } }),
                });
                if (!response.ok) throw new Error((await response.json()).detail || `HTTP error!`);
                closeEditModal();
                fetchStudents();
            } catch (error) {
                alert(`학생 정보 수정 실패: ${error.message}`);
            }
        };

        const renderStudents = (students) => {
            studentsCache = students;
            studentList.innerHTML = '';
            const studentDropdowns = ['submission-student-id', 'memo-student-id', 'report-student-id'].map(id => document.getElementById(id));
            studentDropdowns.forEach(select => { if(select) select.innerHTML = ''; });

            if (!students || students.length === 0) {
                studentList.innerHTML = '<tr><td colspan="4">등록된 학생이 없습니다.</td></tr>';
                return;
            }

            students.forEach(student => {
                const row = document.createElement('tr');
                row.innerHTML = `<td>${student.student_id}</td><td>${student.name}</td><td>${student.settings?.anki_budget_per_day || 'N/A'}</td><td><button data-student-id="${student.student_id}">수정</button></td>`;
                studentList.appendChild(row);
                studentDropdowns.forEach(select => {
                    if (!select) return;
                    const option = document.createElement('option');
                    option.value = student.student_id;
                    option.textContent = `${student.name} (${student.student_id})`;
                    select.appendChild(option);
                });
            });
        };

        const fetchStudents = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/student/`);
                if (!response.ok) throw new Error(`HTTP error!`);
                renderStudents(await response.json());
            } catch (error) {
                studentList.innerHTML = `<tr><td colspan="4" style="color: red;">학생 목록 로딩 실패: ${error.message}</td></tr>`;
            }
        };

        const createStudent = async (event) => {
            event.preventDefault();
            const studentData = {
                student_id: document.getElementById('student-id').value,
                name: document.getElementById('student-name').value,
                settings: { anki_budget_per_day: parseInt(document.getElementById('student-budget').value, 10) }
            };
            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/student/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(studentData),
                });
                if (!response.ok) throw new Error((await response.json()).detail || `HTTP error!`);
                createStudentForm.reset();
                fetchStudents();
            } catch (error) {
                alert(`학생 생성 실패: ${error.message}`);
            }
        };

        createStudentForm.addEventListener('submit', createStudent);
        refreshStudentsBtn.addEventListener('click', fetchStudents);
        studentList.addEventListener('click', (e) => {
            if (e.target.tagName === 'BUTTON' && e.target.dataset.studentId) {
                const studentToEdit = studentsCache.find(s => s.student_id === e.target.dataset.studentId);
                if (studentToEdit) openEditModal(studentToEdit);
            }
        });
        closeModalBtn.addEventListener('click', closeEditModal);
        window.addEventListener('click', (e) => { if (e.target == editModal) closeEditModal(); });
        editForm.addEventListener('submit', handleUpdateStudent);
        fetchStudents();
    }

    // --- Weekly Report Logic ---
    const weeklyReportApp = document.getElementById('weekly-report-app');
    if (weeklyReportApp) {
        const generateReportForm = document.getElementById('generate-report-form');
        const reportDisplayDiv = document.getElementById('report-display');

        const generateReport = async (e) => {
            e.preventDefault();
            const studentId = document.getElementById('report-student-id').value;
            const startDate = document.getElementById('report-start-date').value;
            const endDate = document.getElementById('report-end-date').value;
            if (!studentId || !startDate || !endDate) {
                reportDisplayDiv.innerHTML = '<p style="color: red;">학생, 시작일, 종료일을 모두 선택해주세요.</p>';
                return;
            }
            reportDisplayDiv.textContent = '리포트 생성 중...';
            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/report/student/${studentId}/period?start_date=${startDate}&end_date=${endDate}`);
                if (!response.ok) throw new Error((await response.json()).detail || `HTTP error!`);
                renderReport(await response.json());
            } catch (error) {
                reportDisplayDiv.innerHTML = `<p style="color: red;">리포트 생성 실패: ${error.message}</p>`;
            }
        };

        const renderReport = (report) => {
            const coachReviewSection = document.getElementById('coach-review-section');
            const finalizeBtn = document.getElementById('finalize-report-btn');
            const shareKakaoBtn = document.getElementById('share-kakao-btn');
            coachReviewSection.dataset.reportId = report.report_id;

            reportDisplayDiv.innerHTML = `<h3>${report.student_name} 학생 주간 리포트 (${report.report_period_start} ~ ${report.report_period_end})</h3><p><strong>리포트 상태:</strong> <span style="font-weight: bold; color: ${report.status === 'draft' ? '#ff9800' : (report.status === 'finalized' ? '#28a745' : '#0056b3')}">${report.status}</span></p><p><strong>AI 생성 전체 요약:</strong></p><p style="background-color: #f9f9f9; padding: 10px; border-radius: 5px;">${report.overall_summary.replace(/\n/g, '<br>')}</p>`;
            if (report.coach_comment) {
                reportDisplayDiv.innerHTML += `<h4>코치 최종 코멘트:</h4><p style="background-color: #e7f3ff; padding: 10px; border-radius: 5px;">${report.coach_comment}</p>`;
            }

            if (report.status === 'draft') {
                coachReviewSection.classList.remove('hidden');
                document.getElementById('coach-comment-input').value = '';
                finalizeBtn.disabled = false;
                shareKakaoBtn.classList.add('hidden');
                document.getElementById('finalize-status').textContent = '';
            } else if (report.status === 'finalized') {
                coachReviewSection.classList.add('hidden');
                shareKakaoBtn.classList.remove('hidden');
                shareKakaoBtn.dataset.report = JSON.stringify(report);
            } else {
                coachReviewSection.classList.add('hidden');
                shareKakaoBtn.classList.add('hidden');
            }
        };

        const finalizeReport = async () => {
            const reportId = document.getElementById('coach-review-section').dataset.reportId;
            const coachComment = document.getElementById('coach-comment-input').value;
            if (!coachComment.trim()) {
                alert('코치 코멘트를 입력해주세요.');
                return;
            }
            document.getElementById('finalize-status').textContent = '최종 승인 처리 중...';
            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/report/${reportId}/finalize`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ coach_comment: coachComment }),
                });
                if (!response.ok) throw new Error((await response.json()).detail || `HTTP error!`);
                renderReport(await response.json());
            } catch (error) {
                document.getElementById('finalize-status').innerHTML = `<p style="color: red;">리포트 승인 실패: ${error.message}</p>`;
            }
        };

        const shareReportViaKakao = (report) => {
            if (!Kakao || !Kakao.isInitialized()) {
                alert('카카오 SDK가 초기화되지 않았습니다. config.js의 키를 확인해주세요.');
                return;
            }
            Kakao.Share.sendDefault({
                objectType: 'list',
                headerTitle: `${report.student_name} 주간 학습 리포트`,
                headerLink: { webUrl: window.location.href, mobileWebUrl: window.location.href },
                contents: [
                    { title: `기간: ${report.report_period_start} ~ ${report.report_period_end}`, description: `AI 분석 및 복습 진행`, link: { webUrl: window.location.href, mobileWebUrl: window.location.href } },
                    { title: '코치 최종 코멘트', description: report.coach_comment || '코멘트가 없습니다.', link: { webUrl: window.location.href, mobileWebUrl: window.location.href } },
                ],
                buttons: [ { title: 'Pacer에서 확인하기', link: { webUrl: window.location.href, mobileWebUrl: window.location.href } } ],
            });
        };

        generateReportForm.addEventListener('submit', generateReport);
        document.getElementById('finalize-report-btn').addEventListener('click', finalizeReport);
        document.getElementById('share-kakao-btn').addEventListener('click', (e) => {
            shareReportViaKakao(JSON.parse(e.target.dataset.report));
        });

        // Set default dates
        const today = new Date();
        document.getElementById('report-end-date').value = today.toISOString().split('T')[0];
        today.setDate(today.getDate() - 7);
        document.getElementById('report-start-date').value = today.toISOString().split('T')[0];
    }

    // --- Navigation Logic ---
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        const navLinks = sidebar.querySelectorAll('.nav-link');
        const pages = document.querySelectorAll('#main-content .app-section');

        const initialTarget = sidebar.querySelector('.nav-link.active').dataset.target;
        pages.forEach(page => {
            if (page.id === initialTarget) page.classList.remove('hidden');
            else page.classList.add('hidden');
        });

        sidebar.addEventListener('click', (e) => {
            if (!e.target.classList.contains('nav-link')) return;
            e.preventDefault();
            const targetId = e.target.dataset.target;
            navLinks.forEach(link => link.classList.remove('active'));
            e.target.classList.add('active');
            pages.forEach(page => {
                if (page.id === targetId) page.classList.remove('hidden');
                else page.classList.add('hidden');
            });
        });
    }
});
