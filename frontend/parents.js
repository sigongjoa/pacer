document.addEventListener('DOMContentLoaded', () => {
    const createParentForm = document.getElementById('create-parent-form');
    const parentList = document.getElementById('parent-list');
    const refreshParentsBtn = document.getElementById('refresh-parents-btn');
    const assignParentForm = document.getElementById('assign-parent-form');
    const assignStudentIdSelect = document.getElementById('assign-student-id');
    const assignParentIdSelect = document.getElementById('assign-parent-id');
    const assignStatus = document.getElementById('assign-status');

    // Fetch all parents and render them
    const fetchAndRenderParents = async () => {
        try {
            const response = await fetch('/api/v1/parents/');
            if (!response.ok) throw new Error('Failed to fetch parents');
            const parents = await response.json();
            
            parentList.innerHTML = '';
            assignParentIdSelect.innerHTML = ''; // Clear dropdown

            if (parents.length === 0) {
                parentList.innerHTML = '<li class="list-group-item">No parents found.</li>';
            }

            parents.forEach(parent => {
                // Add to list
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item';
                listItem.textContent = `ID: ${parent.parent_id}, Name: ${parent.name}, Kakao ID: ${parent.kakao_user_id || 'N/A'}`;
                parentList.appendChild(listItem);

                // Add to dropdown
                const option = document.createElement('option');
                option.value = parent.parent_id;
                option.textContent = `${parent.name} (ID: ${parent.parent_id})`;
                assignParentIdSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching parents:', error);
            parentList.innerHTML = '<li class="list-group-item text-danger">Failed to load parents.</li>';
        }
    };

    // Fetch all students and populate the dropdown
    const fetchAndRenderStudents = async () => {
        try {
            const response = await fetch('/api/v1/student/');
            if (!response.ok) throw new Error('Failed to fetch students');
            const students = await response.json();
            
            assignStudentIdSelect.innerHTML = '';
            students.forEach(student => {
                const option = document.createElement('option');
                option.value = student.student_id;
                option.textContent = `${student.name} (ID: ${student.student_id})`;
                assignStudentIdSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching students:', error);
        }
    };

    // Handle Create Parent form submission
    createParentForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('parent-name').value;
        const kakaoId = document.getElementById('kakao-id').value;

        try {
            const response = await fetch('/api/v1/parents/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, kakao_user_id: kakaoId || null })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to create parent');
            }

            createParentForm.reset();
            fetchAndRenderParents(); // Refresh the list
            alert('Parent created successfully!');
        } catch (error) {
            console.error('Error creating parent:', error);
            alert(`Error: ${error.message}`);
        }
    });

    // Handle Assign Parent form submission
    assignParentForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const studentId = assignStudentIdSelect.value;
        const parentId = assignParentIdSelect.value;

        if (!studentId || !parentId) {
            alert('Please select both a student and a parent.');
            return;
        }

        try {
            const response = await fetch(`/api/v1/students/${studentId}/assign-parent/${parentId}` , {
                method: 'POST'
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to assign parent');
            }

            const updatedStudent = await response.json();
            assignStatus.textContent = `Successfully assigned ${updatedStudent.parents.find(p=>p.parent_id == parentId).name} to ${updatedStudent.name}.`;
            assignStatus.className = 'text-success';

        } catch (error) {
            console.error('Error assigning parent:', error);
            assignStatus.textContent = `Error: ${error.message}`;
            assignStatus.className = 'text-danger';
        }
    });

    // Refresh button
    refreshParentsBtn.addEventListener('click', fetchAndRenderParents);

    // Initial data load
    fetchAndRenderParents();
    fetchAndRenderStudents();
});
