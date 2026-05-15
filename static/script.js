// static/script.js - 前端交互逻辑

const API_BASE = 'http://localhost:5000/api';

// 等待页面加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 页面切换
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;

            document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
            link.classList.add('active');

            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById(`${page}-page`).classList.add('active');

            if (page === 'my-bookings') {
                // 清空并等待用户查询
                document.getElementById('bookingsList').innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-search"></i>
                        <p>请输入姓名查询您的预约记录</p>
                    </div>
                `;
            }
        });
    });

    // 加载课程
    loadCourses();

    // 绑定查询按钮
    const queryBtn = document.getElementById('queryBookingsBtn');
    if (queryBtn) {
        queryBtn.addEventListener('click', queryBookings);
    }

    // 绑定搜索框
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', filterCourses);
    }

    // 绑定分类按钮
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterCourses();
        });
    });

    // 绑定弹窗按钮
    const submitBtn = document.getElementById('submitBookingBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', submitBooking);
    }

    const cancelModalBtn = document.getElementById('cancelModalBtn');
    if (cancelModalBtn) {
        cancelModalBtn.addEventListener('click', closeBookingModal);
    }

    const closeBtn = document.querySelector('.close-btn');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeBookingModal);
    }

    // 点击弹窗外部关闭
    const modal = document.getElementById('bookingModal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeBookingModal();
            }
        });
    }
});

// 加载课程
async function loadCourses() {
    try {
        const response = await fetch(`${API_BASE}/courses`);
        const result = await response.json();

        if (result.success) {
            renderCourses(result.data);
        } else {
            console.error('加载课程失败:', result);
            showError('加载课程失败');
        }
    } catch (error) {
        console.error('加载课程失败:', error);
        document.getElementById('coursesGrid').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>加载失败，请确保后端服务已启动</p>
                <p style="font-size:12px; margin-top:10px;">错误: ${error.message}</p>
            </div>
        `;
    }
}

// 渲染课程
function renderCourses(courses) {
    const container = document.getElementById('coursesGrid');

    if (!courses || courses.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-book-open"></i><p>暂无课程</p></div>';
        return;
    }

    container.innerHTML = courses.map(course => `
        <div class="course-card" data-course-id="${course.id}">
            <div class="course-cover" style="background-image: url('${course.cover || 'https://picsum.photos/id/20/300/200'}')">
                <span class="course-badge">${course.category || '精品课程'}</span>
            </div>
            <div class="course-info">
                <h3 class="course-title">${escapeHtml(course.name)}</h3>
                <div class="course-teacher">
                    <img src="${course.teacher_avatar || 'https://picsum.photos/id/64/28/28'}" class="teacher-avatar">
                    <span>${escapeHtml(course.teacher_name)} · ${course.teacher_title || '讲师'}</span>
                </div>
                <p class="course-desc">${escapeHtml(course.description || '暂无简介')}</p>
                <div class="course-meta">
                    <span class="price">¥${course.price}<small>${course.original_price ? '¥' + course.original_price : ''}</small></span>
                    <span class="seats ${course.remaining_seats <= 5 ? (course.remaining_seats <= 0 ? 'full' : 'warning') : ''}">
                        ${course.remaining_seats > 0 ? `剩余 ${course.remaining_seats} 席` : '已满员'}
                    </span>
                </div>
                <button class="book-btn" onclick="openBookingModal(${course.id})" ${course.remaining_seats <= 0 ? 'disabled' : ''}>
                    ${course.remaining_seats > 0 ? '立即预约' : '暂无名额'}
                </button>
            </div>
        </div>
    `).join('');
}

// 弹窗相关
let currentCourseId = null;

function openBookingModal(courseId) {
    currentCourseId = courseId;

    // 获取课程详情
    fetch(`${API_BASE}/courses/${courseId}`)
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                const course = result.data;
                const modalCourseInfo = document.getElementById('modalCourseInfo');
                if (modalCourseInfo) {
                    modalCourseInfo.innerHTML = `
                        <h4>${escapeHtml(course.name)}</h4>
                        <p>讲师：${escapeHtml(course.teacher_name)} | 剩余${course.remaining_seats}席</p>
                    `;
                }
            }
        })
        .catch(err => console.error('获取课程详情失败:', err));

    const modal = document.getElementById('bookingModal');
    if (modal) {
        modal.classList.add('active');
    }
    const form = document.getElementById('bookingForm');
    if (form) {
        form.reset();
    }
}

function closeBookingModal() {
    const modal = document.getElementById('bookingModal');
    if (modal) {
        modal.classList.remove('active');
    }
    currentCourseId = null;
}

// 提交预约
async function submitBooking() {
    const name = document.getElementById('bookingName')?.value.trim();
    const phone = document.getElementById('bookingPhone')?.value.trim();
    const remark = document.getElementById('bookingRemark')?.value || '';

    if (!name) {
        alert('请填写姓名');
        return;
    }
    if (!phone) {
        alert('请填写手机号');
        return;
    }
    if (!currentCourseId) {
        alert('课程信息错误');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/bookings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_name: name,
                student_phone: phone,
                course_id: currentCourseId,
                remark: remark
            })
        });

        const result = await response.json();

        if (result.success) {
            alert(result.message);
            closeBookingModal();
            loadCourses(); // 刷新课程列表
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('预约失败:', error);
        alert('预约失败，请稍后重试');
    }
}

// 查询预约记录
async function queryBookings() {
    const name = document.getElementById('queryName')?.value.trim();
    const phone = document.getElementById('queryPhone')?.value.trim();

    if (!name) {
        alert('请输入姓名');
        return;
    }

    try {
        let url = `${API_BASE}/bookings?student_name=${encodeURIComponent(name)}`;
        if (phone) {
            url += `&student_phone=${encodeURIComponent(phone)}`;
        }

        const response = await fetch(url);
        const result = await response.json();

        if (result.success) {
            renderBookings(result.data);
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('查询失败:', error);
        alert('查询失败');
    }
}

// 渲染预约列表
function renderBookings(bookings) {
    const container = document.getElementById('bookingsList');

    if (!bookings || bookings.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-calendar-times"></i>
                <p>暂无预约记录</p>
            </div>
        `;
        return;
    }

    const statusMap = {
        'pending': { text: '待确认', class: 'pending' },
        'confirmed': { text: '已确认', class: 'confirmed' },
        'cancelled': { text: '已取消', class: 'cancelled' },
        'completed': { text: '已完成', class: 'completed' }
    };

    container.innerHTML = bookings.map(booking => {
        const status = statusMap[booking.status] || { text: booking.status, class: 'pending' };
        return `
            <div class="booking-card ${status.class}">
                <div class="booking-info">
                    <h4>${escapeHtml(booking.course_name)}</h4>
                    <p>预约时间：${new Date(booking.booking_date).toLocaleString()}</p>
                    ${booking.schedule ? `<p>上课时间：${escapeHtml(booking.schedule)} ${booking.location ? '@ ' + escapeHtml(booking.location) : ''}</p>` : ''}
                    ${booking.remark ? `<p>备注：${escapeHtml(booking.remark)}</p>` : ''}
                </div>
                <div>
                    <span class="booking-status status-${booking.status}">${status.text}</span>
                    ${booking.status === 'pending' || booking.status === 'confirmed' ?
                        `<button class="cancel-booking-btn" onclick="cancelBooking(${booking.id}, '${escapeHtml(booking.student_name)}')">取消预约</button>` :
                        ''}
                </div>
            </div>
        `;
    }).join('');
}

// 取消预约
async function cancelBooking(bookingId, studentName) {
    if (!confirm('确定要取消这个预约吗？')) return;

    try {
        const response = await fetch(`${API_BASE}/bookings/${bookingId}/cancel`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_name: studentName })
        });

        const result = await response.json();

        if (result.success) {
            alert('取消成功');
            queryBookings(); // 刷新列表
            loadCourses();   // 刷新课程名额
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('取消失败:', error);
        alert('取消失败');
    }
}

// 筛选功能
let allCourses = [];

function filterCourses() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const activeCategory = document.querySelector('.filter-btn.active')?.dataset.category || 'all';

    fetch(`${API_BASE}/courses`)
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                let filtered = result.data;
                allCourses = result.data;

                if (activeCategory !== 'all') {
                    filtered = filtered.filter(c => c.category === activeCategory);
                }
                if (searchTerm) {
                    filtered = filtered.filter(c => c.name && c.name.toLowerCase().includes(searchTerm));
                }
                renderCourses(filtered);
            }
        })
        .catch(err => console.error('筛选失败:', err));
}

// 显示错误
function showError(message) {
    const container = document.getElementById('coursesGrid');
    if (container) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
            </div>
        `;
    }
}

// 工具函数
function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}