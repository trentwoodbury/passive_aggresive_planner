document.addEventListener('DOMContentLoaded', () => {
    const taskInput = document.getElementById('taskInput');
    const addTaskBtn = document.getElementById('addTaskBtn');
    const taskList = document.getElementById('taskList');
    const loadingSpinner = document.querySelector('.loading-spinner');
    const btnText = document.querySelector('.btn-text');

    const handleAddTask = async () => {
        const input = taskInput.value.trim();
        if (!input) return;

        // UI Loading State
        setLoading(true);

        try {
            const response = await fetch('/parse-task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ task_description: input }),
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }

            const data = await response.json();

            // Expecting data = { summary: "...", due_date: "...", passive_aggressive_flair: "..." }
            createTaskElement(data.summary, data.due_date, data.passive_aggressive_flair);

            // Clear input
            taskInput.value = '';

        } catch (error) {
            console.error('Failed to add task:', error);
            alert('Failed to process task. Please ensure the backend is running.');
        } finally {
            setLoading(false);
        }
    };

    const setLoading = (isLoading) => {
        if (isLoading) {
            addTaskBtn.disabled = true;
            btnText.classList.add('hidden');
            loadingSpinner.classList.remove('hidden');
        } else {
            addTaskBtn.disabled = false;
            btnText.classList.remove('hidden');
            loadingSpinner.classList.add('hidden');
        }
    };

    const createTaskElement = (summary, dueDate, flair) => {
        const li = document.createElement('li');
        li.className = 'task-item';

        const formattedDate = dueDate ? new Date(dueDate).toLocaleDateString(undefined, {
            weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'
        }) : 'No due date';

        li.innerHTML = `
            <div class="task-content">
                <span class="task-summary">${summary}</span>
                <span class="task-date">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                    ${formattedDate}
                    ${formattedDate}
                </span>
                ${flair ? `<span class="task-flair">${flair}</span>` : ''}
            </div>
            <div class="task-actions">
                <button class="delete-btn" onclick="this.closest('.task-item').remove()">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
            </div>
        `;

        taskList.prepend(li);
    };

    addTaskBtn.addEventListener('click', handleAddTask);

    // Allow pressing Enter to add task
    taskInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleAddTask();
        }
    });
});
