// --- Глобальные переменные ---
let apiBase = '';          // относительный путь (FastAPI сам проксирует)
let token = null;

// DOM элементы
const authSection = document.getElementById('authSection');
const registerSection = document.getElementById('registerSection');
const appSection = document.getElementById('appSection');
const authError = document.getElementById('authError');
const regError = document.getElementById('regError');

// --- Helper: запросы к API с авторизацией ---
async function apiRequest(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    const response = await fetch(`${apiBase}${url}`, {
        ...options,
        headers
    });
    if (response.status === 401) {
        // Токен просрочен или недействителен
        logout();
        throw new Error('Сессия истекла, войдите заново');
    }
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || 'Ошибка запроса');
    }
    return data;
}

// --- Сохранение токена ---
function setToken(newToken) {
    token = newToken;
    if (token) {
        localStorage.setItem('access_token', token);
    } else {
        localStorage.removeItem('access_token');
    }
}

// --- Выход ---
function logout() {
    setToken(null);
    authSection.classList.remove('hidden');
    registerSection.classList.add('hidden');
    appSection.classList.add('hidden');
}

// --- Проверка авторизации при загрузке ---
async function checkAuth() {
    const savedToken = localStorage.getItem('access_token');
    if (savedToken) {
        token = savedToken;
        try {
            // Проверим токен, запросив список сотрудников (любой защищённый эндпоинт)
            await apiRequest('/employees');
            showApp();
        } catch (e) {
            // Токен невалиден
            logout();
        }
    } else {
        logout();
    }
}

// --- Отображение основного приложения ---
function showApp() {
    authSection.classList.add('hidden');
    registerSection.classList.add('hidden');
    appSection.classList.remove('hidden');
    loadEmployees();
    loadEmployeeSelect();
}

// --- Загрузка списка сотрудников и отрисовка таблицы ---
async function loadEmployees() {
    try {
        const response = await fetch(`${apiBase}/employees/`, {  // добавим слэш в конце
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) {
            const text = await response.text();  // получаем текст ошибки (может быть HTML)
            console.error('Server response:', text);
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const employees = await response.json();
        const tbody = document.querySelector('#employeesTable tbody');
        tbody.innerHTML = '';
        for (const emp of employees) {
            const row = tbody.insertRow();
            row.insertCell(0).innerText = emp.id;
            row.insertCell(1).innerText = emp.name;
            row.insertCell(2).innerText = new Date(emp.created_at).toLocaleString();
            const actions = row.insertCell(3);
            const editBtn = document.createElement('button');
            editBtn.innerText = '✏️';
            editBtn.style.marginRight = '8px';
            editBtn.onclick = () => editEmployee(emp);
            const delBtn = document.createElement('button');
            delBtn.innerText = '🗑️';
            delBtn.onclick = () => deleteEmployee(emp.id);
            actions.appendChild(editBtn);
            actions.appendChild(delBtn);
        }
    } catch (e) {
        console.error('Load error:', e);
        alert('Ошибка загрузки сотрудников: ' + (e.message || 'Неизвестная ошибка'));
        // Дополнительно покажем в консоли детали
        if (e.response) console.log(await e.response.text());
    }
}

// --- Добавление сотрудника ---
async function addEmployee() {
    const name = document.getElementById('empName').value.trim();
    const fileInput = document.getElementById('empPhoto');
    if (!name) {
        alert('Введите имя сотрудника');
        return;
    }
    if (!fileInput.files.length) {
        alert('Выберите фотографию');
        return;
    }
    const formData = new FormData();
    formData.append('name', name);
    formData.append('photo', fileInput.files[0]);
    try {
        const response = await fetch(`${apiBase}/employees`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Ошибка');
        }
        alert('Сотрудник добавлен');
        document.getElementById('empName').value = '';
        fileInput.value = '';
        loadEmployees();
        loadEmployeeSelect();
    } catch (e) {
        alert('Ошибка: ' + e.message);
    }
}

// --- Редактирование сотрудника (имя и/или фото) ---
async function editEmployee(emp) {
    const newName = prompt('Введите новое имя (оставьте пустым, если не менять)', emp.name);
    let newPhoto = null;
    const changePhoto = confirm('Хотите заменить фото?');
    if (changePhoto) {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/jpeg,image/png';
        fileInput.onchange = async () => {
            if (fileInput.files.length) {
                await performUpdate(emp.id, newName, fileInput.files[0]);
            }
        };
        fileInput.click();
    } else {
        await performUpdate(emp.id, newName, null);
    }
}

async function performUpdate(id, name, photoFile) {
    const formData = new FormData();
    if (name && name.trim() !== '') formData.append('name', name.trim());
    if (photoFile) formData.append('photo', photoFile);
    try {
        const response = await fetch(`${apiBase}/employees/${id}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Ошибка');
        }
        alert('Сотрудник обновлён');
        loadEmployees();
        loadEmployeeSelect();
    } catch (e) {
        alert('Ошибка: ' + e.message);
    }
}

// --- Удаление сотрудника ---
async function deleteEmployee(id) {
    if (!confirm('Удалить сотрудника? Все записи посещаемости останутся (без привязки к сотруднику)')) return;
    try {
        await apiRequest(`/employees/${id}`, { method: 'DELETE' });
        alert('Сотрудник удалён');
        loadEmployees();
        loadEmployeeSelect();
    } catch (e) {
        alert('Ошибка удаления: ' + e.message);
    }
}

// --- Заполнение выпадающего списка для посещаемости ---
async function loadEmployeeSelect() {
    try {
        const employees = await apiRequest('/employees');
        const select = document.getElementById('attendanceEmployeeSelect');
        select.innerHTML = '<option value="">-- Выберите сотрудника --</option>';
        for (const emp of employees) {
            const option = document.createElement('option');
            option.value = emp.id;
            option.textContent = `${emp.name} (ID: ${emp.id})`;
            select.appendChild(option);
        }
    } catch (e) {
        console.error('Ошибка загрузки списка сотрудников', e);
    }
}

// --- Загрузка и отображение посещаемости ---
async function loadAttendance() {
    const select = document.getElementById('attendanceEmployeeSelect');
    const empId = select.value;
    if (!empId) {
        alert('Выберите сотрудника');
        return;
    }
    try {
        const records = await apiRequest(`/employees/${empId}/attendance`);
        const container = document.getElementById('attendanceResult');
        if (!records.length) {
            container.innerHTML = '<p>Нет записей о посещаемости.</p>';
            return;
        }
        let html = '<table class="attendance-table"><tr><th>Дата</th><th>Приход</th><th>Уход</th><th>Отработано (ч)</th></tr>';
        for (const rec of records) {
            html += `<tr>
                        <td>${new Date(rec.date).toLocaleDateString()}</td>
                        <td>${rec.check_in ? new Date(rec.check_in).toLocaleTimeString() : '-'}</td>
                        <td>${rec.check_out ? new Date(rec.check_out).toLocaleTimeString() : '-'}</td>
                        <td>${rec.worked_hours !== null ? rec.worked_hours.toFixed(2) : '-'}</td>
                    </tr>`;
        }
        html += '</table>';
        container.innerHTML = html;
    } catch (e) {
        alert('Ошибка загрузки посещаемости: ' + e.message);
    }
}

// --- Авторизация ---
async function login() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    if (!username || !password) {
        authError.innerText = 'Заполните все поля';
        return;
    }
    try {
        const resp = await fetch(`${apiBase}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || 'Ошибка входа');
        setToken(data.access_token);
        authError.innerText = '';
        showApp();
    } catch (e) {
        authError.innerText = e.message;
    }
}

// --- Регистрация ---
async function register() {
    const username = document.getElementById('regUsername').value;
    const password = document.getElementById('regPassword').value;
    if (!username || !password) {
        regError.innerText = 'Заполните все поля';
        return;
    }
    try {
        const resp = await fetch(`${apiBase}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || 'Ошибка регистрации');
        setToken(data.access_token);
        regError.innerText = '';
        showApp();
    } catch (e) {
        regError.innerText = e.message;
    }
}

// --- Переключение между формами авторизации/регистрации ---
document.getElementById('showRegisterBtn').onclick = () => {
    authSection.classList.add('hidden');
    registerSection.classList.remove('hidden');
};
document.getElementById('showLoginBtn').onclick = () => {
    registerSection.classList.add('hidden');
    authSection.classList.remove('hidden');
};
document.getElementById('loginBtn').onclick = login;
document.getElementById('registerBtn').onclick = register;
document.getElementById('logoutBtn').onclick = logout;
document.getElementById('addEmployeeBtn').onclick = addEmployee;
document.getElementById('loadAttendanceBtn').onclick = loadAttendance;

// --- Инициализация ---
checkAuth();