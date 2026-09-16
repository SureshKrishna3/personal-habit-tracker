/**
 * HabitPulse - Personal Habit Tracker Frontend Logic
 * Interacts with Flask API endpoints using Fetch API
 */

document.addEventListener('DOMContentLoaded', () => {
    // State management
    let habitsList = [];
    let currentStatusFilter = 'all';
    let currentCategoryFilter = 'all';

    // DOM Elements
    const habitsContainer = document.getElementById('habits-container');
    const emptyState = document.getElementById('empty-state');
    const todayDateText = document.getElementById('today-date-text');
    
    // Stats Elements
    const statTotal = document.getElementById('stat-total');
    const statCompleted = document.getElementById('stat-completed');
    const statPending = document.getElementById('stat-pending');
    const statStreaks = document.getElementById('stat-streaks');
    const progressPercentage = document.getElementById('progress-percentage');
    const progressCircle = document.getElementById('progress-circle');
    const progressBarFill = document.getElementById('progress-bar-fill');
    const progressSubtitle = document.getElementById('progress-subtitle');

    // Filter Controls
    const statusFilterTabs = document.getElementById('status-filter');
    const categoryFilterSelect = document.getElementById('category-filter');

    // Modal & Form Elements
    const addModal = document.getElementById('add-modal');
    const openAddBtn = document.getElementById('open-add-modal-btn');
    const emptyAddBtn = document.getElementById('empty-add-btn');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const cancelModalBtn = document.getElementById('cancel-modal-btn');
    const addHabitForm = document.getElementById('add-habit-form');
    const toast = document.getElementById('toast-notification');

    // Initialize Page
    initDateDisplay();
    loadDashboardData();

    // Event Listeners
    openAddBtn.addEventListener('click', () => openModal());
    emptyAddBtn.addEventListener('click', () => openModal());
    closeModalBtn.addEventListener('click', () => closeModal());
    cancelModalBtn.addEventListener('click', () => closeModal());
    
    // Close modal on outside overlay click
    addModal.addEventListener('click', (e) => {
        if (e.target === addModal) closeModal();
    });

    // Form Submit
    addHabitForm.addEventListener('submit', handleAddHabit);

    // Status Filter Tabs
    statusFilterTabs.addEventListener('click', (e) => {
        if (e.target.classList.contains('tab-btn')) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            currentStatusFilter = e.target.dataset.filter;
            renderHabits();
        }
    });

    // Category Filter Select
    categoryFilterSelect.addEventListener('change', (e) => {
        currentCategoryFilter = e.target.value;
        renderHabits();
    });

    /**
     * Display current formatted date in header
     */
    function initDateDisplay() {
        const options = { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' };
        const todayStr = new Date().toLocaleDateString('en-US', options);
        todayDateText.textContent = todayStr;
    }

    /**
     * Fetch habits and stats from backend API
     */
    async function loadDashboardData() {
        try {
            await Promise.all([fetchHabits(), fetchStats()]);
        } catch (error) {
            showToast('Failed to load dashboard data', 'error');
            console.error(error);
        }
    }

    /**
     * Fetch list of habits
     */
    async function fetchHabits() {
        const response = await fetch('/api/habits');
        if (!response.ok) throw new Error('Failed to fetch habits');
        habitsList = await response.json();
        renderHabits();
    }

    /**
     * Fetch overall stats & update progress indicators
     */
    async function fetchStats() {
        const response = await fetch('/api/stats');
        if (!response.ok) throw new Error('Failed to fetch stats');
        const stats = await response.json();

        statTotal.textContent = stats.total;
        statCompleted.textContent = stats.completed;
        statPending.textContent = stats.pending;

        // Calculate total active streaks across all habits
        const activeStreaksCount = habitsList.filter(h => h.streak > 0).length;
        statStreaks.textContent = activeStreaksCount;

        // Update progress indicators
        const pct = stats.percentage || 0;
        progressPercentage.textContent = `${pct}%`;
        progressCircle.style.setProperty('--progress', pct);
        progressBarFill.style.width = `${pct}%`;

        progressSubtitle.textContent = `You have completed ${stats.completed} of ${stats.total} habits today.`;
    }

    /**
     * Filter and render habits list
     */
    function renderHabits() {
        habitsContainer.innerHTML = '';

        const filtered = habitsList.filter(habit => {
            const matchesStatus = 
                currentStatusFilter === 'all' ||
                (currentStatusFilter === 'completed' && habit.completed_today) ||
                (currentStatusFilter === 'pending' && !habit.completed_today);

            const matchesCategory = 
                currentCategoryFilter === 'all' || 
                habit.category.toLowerCase() === currentCategoryFilter.toLowerCase();

            return matchesStatus && matchesCategory;
        });

        if (filtered.length === 0) {
            emptyState.classList.remove('hidden');
        } else {
            emptyState.classList.add('hidden');
            filtered.forEach(habit => {
                const card = createHabitCard(habit);
                habitsContainer.appendChild(card);
            });
        }
    }

    /**
     * Create DOM element for a single habit card
     */
    function createHabitCard(habit) {
        const card = document.createElement('div');
        card.className = `habit-card ${habit.completed_today ? 'completed-card' : ''}`;
        
        card.innerHTML = `
            <div class="habit-header">
                <div class="habit-title-area">
                    <h3 class="habit-name">${escapeHTML(habit.name)}</h3>
                    ${habit.description ? `<p class="habit-desc">${escapeHTML(habit.description)}</p>` : ''}
                    <span class="category-badge ${escapeHTML(habit.category)}">${escapeHTML(habit.category)}</span>
                </div>
            </div>

            <div class="habit-footer">
                <div class="streak-pill">
                    <i class="ri-fire-fill"></i> ${habit.streak} ${habit.streak === 1 ? 'day' : 'days'} streak
                </div>

                <div class="actions-group">
                    <button class="toggle-btn ${habit.completed_today ? 'completed' : ''}" 
                            title="${habit.completed_today ? 'Mark as Incomplete' : 'Mark as Completed'}"
                            onclick="window.toggleHabit(${habit.id})">
                        <i class="ri-check-line"></i>
                    </button>
                    
                    <button class="delete-btn" 
                            title="Delete Habit" 
                            onclick="window.deleteHabit(${habit.id}, '${escapeHTML(habit.name)}')">
                        <i class="ri-delete-bin-line"></i>
                    </button>
                </div>
            </div>
        `;
        return card;
    }

    /**
     * Toggle completion status of habit
     */
    window.toggleHabit = async function(habitId) {
        try {
            const response = await fetch(`/api/habits/${habitId}/toggle`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            
            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.error || `HTTP ${response.status}: Failed to update status`);
            }
            
            const data = await response.json();
            
            showToast(data.completed ? 'Habit completed! 🎉' : 'Habit marked pending', 'success');
            await loadDashboardData();
        } catch (error) {
            showToast('Failed to update habit status', 'error');
            console.error('Error toggling habit:', error);
        }
    };

    /**
     * Delete a habit with confirmation
     */
    window.deleteHabit = async function(habitId, habitName) {
        if (!confirm(`Are you sure you want to delete "${habitName}"?`)) return;

        try {
            const response = await fetch(`/api/habits/${habitId}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Delete request failed');

            showToast('Habit deleted successfully', 'info');
            await loadDashboardData();
        } catch (error) {
            showToast('Failed to delete habit', 'error');
            console.error(error);
        }
    };

    /**
     * Handle Add Habit Form submission
     */
    async function handleAddHabit(e) {
        e.preventDefault();
        
        const nameInput = document.getElementById('habit-name');
        const categoryInput = document.getElementById('habit-category');
        const descInput = document.getElementById('habit-desc');

        const payload = {
            name: nameInput.value.trim(),
            category: categoryInput.value,
            description: descInput.value.trim()
        };

        if (!payload.name) {
            showToast('Please enter a habit name', 'error');
            return;
        }

        try {
            const response = await fetch('/api/habits', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error('Failed to create habit');

            showToast('New habit added successfully! 🚀', 'success');
            closeModal();
            addHabitForm.reset();
            await loadDashboardData();
        } catch (error) {
            showToast('Failed to create habit', 'error');
            console.error(error);
        }
    }

    /**
     * Modal Helpers
     */
    function openModal() {
        addModal.classList.remove('hidden');
        document.getElementById('habit-name').focus();
    }

    function closeModal() {
        addModal.classList.add('hidden');
    }

    /**
     * Toast Notifications Helper
     */
    function showToast(message) {
        toast.textContent = message;
        toast.classList.remove('hidden');
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }

    /**
     * HTML Escaping utility to prevent XSS
     */
    function escapeHTML(str) {
        if (!str) return '';
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }
});
