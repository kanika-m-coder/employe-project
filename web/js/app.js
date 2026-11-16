// AttendPay Frontend Core
const user = JSON.parse(sessionStorage.getItem("user") || "null");
if (!user && !location.pathname.endsWith("login.html") && !location.pathname.endsWith("register.html")) {
  location.href = "login.html";
}

// Lucide SVG Icons Library (Linear 24x24 Clean Geometry)
const ic = p => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${p}</svg>`;

const ICONS = {
  dashboard: '<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>',
  employees: '<path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>',
  attendance: '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><path d="M9 16l2 2 4-4"/>',
  leave: '<path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/><line x1="12" y1="6" x2="16" y2="6"/><line x1="12" y1="10" x2="16" y2="10"/>',
  payroll: '<rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/><circle cx="7" cy="15" r="1"/>',
  reports: '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>',
  analytics: '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/>',
  logout: '<path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>',
  calendar: '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
  search: '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
  bell: '<path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/>',
  menu: '<line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>'
};

const NAV_MAIN = [
  ["index.html", "Dashboard", ICONS.dashboard],
  ["employees.html", "Employees", ICONS.employees],
  ["attendance.html", "Attendance", ICONS.attendance],
  ["leave.html", "Leave Management", ICONS.leave]
];

const NAV_ANALYTICS = [
  ["payroll.html", "Payroll", ICONS.payroll],
  ["reports.html", "Reports", ICONS.reports],
  ["analytics.html", "Analytics", ICONS.analytics]
];

const here = location.pathname.split("/").pop() || "index.html";

document.addEventListener("DOMContentLoaded", () => {
  if (!user) return;

  // Build Premium Sidebar
  const sidebarEl = document.querySelector(".sidebar");
  if (sidebarEl) {
    sidebarEl.innerHTML = `
      <div class="sidebar-header">
        <a href="index.html" class="brand">
          <div class="brand-icon-box">A</div>
          <div class="brand-text">Attend<span>Pay</span></div>
        </a>
      </div>
      
      <div class="sidebar-nav-container">
        <div class="nav-section-title">Main Menu</div>
        <nav class="nav" id="navMain"></nav>
        
        ${user.role === "ADMIN" ? `
          <div class="nav-section-title" style="margin-top:10px">Finance & Intelligence</div>
          <nav class="nav" id="navAnalytics"></nav>
        ` : ''}

        <div class="nav-section-title" style="margin-top:10px">System</div>
        <nav class="nav">
          <button type="button" class="nav-btn" onclick="openSettingsModal()">
            ${ic(ICONS.settings)}
            <span>Settings</span>
          </button>
        </nav>
      </div>

      <div class="sidebar-footer">
        <div class="user-profile-card">
          <div class="avatar-container">
            <div class="avatar" id="sidebarAv">${(user.name || user.username || "U")[0].toUpperCase()}</div>
            <div class="user-status-dot"></div>
          </div>
          <div class="user-details">
            <span class="user-name" title="${user.name || user.username}">${user.name || user.username}</span>
            <span class="user-role">${user.role === "ADMIN" ? "Admin" : "Employee"}</span>
          </div>
          <button type="button" class="btn-sidebar-logout" onclick="logout()" title="Sign Out">
            ${ic(ICONS.logout)}
          </button>
        </div>
      </div>
    `;

    // Populate Main Navigation
    const navMainEl = document.getElementById("navMain");
    const mainItems = user.role === "ADMIN" 
      ? NAV_MAIN 
      : NAV_MAIN.filter(n => n[0] === "attendance.html" || n[0] === "leave.html");

    if (navMainEl) {
      navMainEl.innerHTML = mainItems.map(n => `
        <a href="${n[0]}" class="${n[0] === here ? 'active' : ''}">
          ${ic(n[2])}
          <span>${n[1]}</span>
        </a>
      `).join("");
    }

    // Populate Analytics Navigation
    const navAnalyticsEl = document.getElementById("navAnalytics");
    if (navAnalyticsEl && user.role === "ADMIN") {
      navAnalyticsEl.innerHTML = NAV_ANALYTICS.map(n => `
        <a href="${n[0]}" class="${n[0] === here ? 'active' : ''}">
          ${ic(n[2])}
          <span>${n[1]}</span>
        </a>
      `).join("");
    }
  }

  // Setup Mobile Backdrop
  if (!document.querySelector(".sidebar-backdrop")) {
    const backdrop = document.createElement("div");
    backdrop.className = "sidebar-backdrop";
    backdrop.onclick = toggleSidebar;
    document.body.appendChild(backdrop);
  }

  // Enhance Top Header
  const topEl = document.querySelector(".top");
  if (topEl) {
    const existingTitle = document.getElementById("title");
    const currentTitleText = existingTitle ? existingTitle.textContent : "AttendPay";

    // Format current date
    const dateFormatted = new Date().toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: "numeric"
    });

    topEl.innerHTML = `
      <div class="header-left">
        <button type="button" class="btn-mobile-menu" onclick="toggleSidebar()" aria-label="Toggle navigation">
          ${ic(ICONS.menu)}
        </button>
        <div class="header-greeting-block">
          <h1 id="title">${currentTitleText}</h1>
          <div class="header-date-badge">
            ${ic(ICONS.calendar)}
            <span>${dateFormatted}</span>
          </div>
        </div>
      </div>

      <div class="header-center">
        <div class="global-search-bar">
          ${ic(ICONS.search)}
          <input type="text" placeholder="Search employees, records, departments..." aria-label="Quick search" onkeydown="if(event.key==='Enter'&&window.handleGlobalSearch)handleGlobalSearch(this.value)">
        </div>
      </div>

      <div class="header-right">
        <!-- Notification Dropdown -->
        <div class="notification-dropdown-wrapper">
          <button type="button" class="header-icon-btn" id="btnNotification" onclick="toggleNotifications(event)" title="Notifications" aria-expanded="false" aria-label="Notifications">
            ${ic(ICONS.bell)}
            <span class="notification-indicator" id="notifDot" style="display:none"></span>
          </button>
          <div class="notification-dropdown" id="notifDropdown">
            <div class="notif-header">
              <h4>
                <span>Notifications</span>
                <span class="notif-badge-count" id="notifCount">0</span>
              </h4>
              <button type="button" class="notif-mark-read" onclick="markAllNotificationsRead(event)">Mark all read</button>
            </div>
            <div class="notif-list" id="notifList"></div>
            <div class="notif-footer">
              <a href="reports.html">View System Audit & Reports →</a>
            </div>
          </div>
        </div>

        <button type="button" class="header-icon-btn" onclick="openSettingsModal()" title="System Settings">
          ${ic(ICONS.settings)}
        </button>
        <div class="user" style="margin-left: 6px;">
          <div class="avatar" id="av">${(user.name || user.username || "U")[0].toUpperCase()}</div>
          <span id="uname" style="font-weight:600;font-size:13.5px;color:var(--text-primary);">${user.name || user.username}</span>
          <button class="btn ghost" style="padding:6px 14px;font-size:12.5px;margin-left:8px" onclick="logout()">Sign out</button>
        </div>
      </div>
    `;

    // Initialize Notification Feed
    initNotifications();
  }
});

// Global Search Handler
window.handleGlobalSearch = query => {
  if (!query || !query.trim()) return;
  const q = encodeURIComponent(query.trim());
  if (location.pathname.endsWith("employees.html")) {
    const qEl = document.getElementById("q");
    if (qEl) {
      qEl.value = query.trim();
      if (typeof load === "function") load();
    }
  } else {
    location.href = `employees.html?q=${q}`;
  }
};

// Notification System Core
let appNotifications = [];

async function initNotifications() {
  appNotifications = [];
  try {
    if (user.role === "ADMIN") {
      // 1. Pending Leaves Notice
      const leaves = await api("/leave").catch(() => []);
      const pending = leaves.filter(l => l.status === "Pending");
      pending.forEach(l => {
        appNotifications.push({
          id: "leave-" + l.id,
          type: "leave",
          title: "Pending Leave Approval",
          desc: `${l.name} (#${l.empId}) requested ${l.type} leave (${l.days} day${l.days === 1 ? '' : 's'}).`,
          time: l.startDate || "Recent",
          link: "leave.html",
          unread: true
        });
      });

      // 2. Absences Alert from Dashboard
      const dash = await api("/dashboard").catch(() => null);
      if (dash && dash.absent > 0) {
        appNotifications.push({
          id: "att-absent",
          type: "attendance",
          title: "Attendance Notice",
          desc: `${dash.absent} employee(s) marked absent as of ${dash.date}.`,
          time: "Today",
          link: "attendance.html",
          unread: true
        });
      }

      // 3. Monthly Payroll Engine Status
      if (dash) {
        appNotifications.push({
          id: "payroll-engine",
          type: "payroll",
          title: "Payroll Register Status",
          desc: `Active period payroll net total: ₹${Number(dash.monthlyPayroll || 0).toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}.`,
          time: dash.date || "Active",
          link: "payroll.html",
          unread: false
        });
      }

      // 4. System Rule Engine Active
      appNotifications.push({
        id: "sys-rules",
        type: "system",
        title: "Statutory Rules Active",
        desc: "HRA 20%, DA 10%, PF 12% deduction formulas in effect.",
        time: "Verified",
        link: "payroll.html",
        unread: false
      });
    } else {
      // Employee notifications
      const myLeaves = await api(`/leave?emp=${user.empId}`).catch(() => []);
      myLeaves.slice(0, 3).forEach(l => {
        appNotifications.push({
          id: "myleave-" + l.id,
          type: "leave",
          title: `Leave Status: ${l.status}`,
          desc: `Your ${l.type} leave (${l.startDate} to ${l.endDate}) is marked ${l.status}.`,
          time: l.startDate || "Recent",
          link: "leave.html",
          unread: l.status === "Pending"
        });
      });

      appNotifications.push({
        id: "emp-welcome",
        type: "system",
        title: "Employee Portal Active",
        desc: "You can track your duty attendance and submit leave requests.",
        time: "Active",
        link: "attendance.html",
        unread: false
      });
    }
  } catch (err) {
    console.warn("Could not load notifications:", err);
  }

  renderNotifications();
}

function renderNotifications() {
  const notifDot = document.getElementById("notifDot");
  const notifCount = document.getElementById("notifCount");
  const notifList = document.getElementById("notifList");
  if (!notifList) return;

  const unreadCount = appNotifications.filter(n => n.unread).length;
  if (notifDot) {
    notifDot.style.display = unreadCount > 0 ? "block" : "none";
  }
  if (notifCount) {
    notifCount.textContent = unreadCount > 0 ? `${unreadCount} new` : "0";
  }

  if (appNotifications.length === 0) {
    notifList.innerHTML = `<div class="notif-empty">No notifications. All systems up to date.</div>`;
    return;
  }

  const icons = {
    leave: '<path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/><line x1="12" y1="6" x2="16" y2="6"/><line x1="12" y1="10" x2="16" y2="10"/>',
    attendance: '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    payroll: '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="3"/><line x1="6" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="18" y2="12"/>',
    system: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/>'
  };

  notifList.innerHTML = appNotifications.map(n => `
    <a href="${n.link}" class="notif-item ${n.unread ? 'unread' : ''}" onclick="onNotificationClick('${n.id}')">
      <div class="notif-icon-box ${n.type}">
        ${ic(icons[n.type] || icons.system)}
      </div>
      <div class="notif-content">
        <div class="notif-title-row">
          <span class="notif-title">${esc(n.title)}</span>
          <span class="notif-time">${esc(n.time)}</span>
        </div>
        <p class="notif-desc">${esc(n.desc)}</p>
      </div>
      ${n.unread ? '<div class="notif-unread-dot"></div>' : ''}
    </a>
  `).join("");
}

function toggleNotifications(e) {
  if (e) e.stopPropagation();
  const dropdown = document.getElementById("notifDropdown");
  const btn = document.getElementById("btnNotification");
  if (!dropdown) return;
  const isExpanded = dropdown.classList.toggle("active");
  if (btn) btn.setAttribute("aria-expanded", isExpanded ? "true" : "false");
}

function markAllNotificationsRead(e) {
  if (e) e.stopPropagation();
  appNotifications.forEach(n => n.unread = false);
  renderNotifications();
  toast("All notifications marked as read");
}

function onNotificationClick(id) {
  const item = appNotifications.find(n => n.id === id);
  if (item) item.unread = false;
  renderNotifications();
}

// Close notifications when clicking anywhere outside
document.addEventListener("click", e => {
  const wrapper = document.querySelector(".notification-dropdown-wrapper");
  const dropdown = document.getElementById("notifDropdown");
  const btn = document.getElementById("btnNotification");
  if (dropdown && dropdown.classList.contains("active") && wrapper && !wrapper.contains(e.target)) {
    dropdown.classList.remove("active");
    if (btn) btn.setAttribute("aria-expanded", "false");
  }
});

function toggleSidebar() {
  const sb = document.querySelector(".sidebar");
  const bd = document.querySelector(".sidebar-backdrop");
  if (sb) sb.classList.toggle("open");
  if (bd) bd.classList.toggle("active");
}

// Settings Modal Component
function openSettingsModal() {
  const existingModal = document.getElementById("settingsModal");
  if (existingModal) existingModal.remove();

  const modal = document.createElement("div");
  modal.id = "settingsModal";
  modal.className = "modal-overlay";
  modal.innerHTML = `
    <div class="modal-card">
      <div class="modal-header">
        <h3>AttendPay Settings & Configuration</h3>
        <button type="button" class="modal-close-btn" onclick="document.getElementById('settingsModal').remove()">✕</button>
      </div>

      <div style="display:flex;flex-direction:column;gap:18px;">
        <!-- Statutory Salary Engine Rules -->
        <div style="background:#F8FAFC;border:1px solid #E5EAF1;border-radius:12px;padding:16px;">
          <h4 style="font-size:13.5px;font-weight:700;color:var(--secondary-navy);margin-bottom:8px;">
            Statutory Payroll Rules (Scenario 13)
          </h4>
          <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:10px;text-align:center;">
            <div style="background:#FFFFFF;border:1px solid #E5EAF1;border-radius:8px;padding:10px;">
              <small style="color:var(--text-secondary);font-size:11px;font-weight:600;display:block;">HRA</small>
              <b style="font-size:16px;color:var(--status-present);">20%</b>
            </div>
            <div style="background:#FFFFFF;border:1px solid #E5EAF1;border-radius:8px;padding:10px;">
              <small style="color:var(--text-secondary);font-size:11px;font-weight:600;display:block;">DA</small>
              <b style="font-size:16px;color:var(--status-present);">10%</b>
            </div>
            <div style="background:#FFFFFF;border:1px solid #E5EAF1;border-radius:8px;padding:10px;">
              <small style="color:var(--text-secondary);font-size:11px;font-weight:600;display:block;">PF DEDUCTION</small>
              <b style="font-size:16px;color:var(--status-absent);">12%</b>
            </div>
          </div>
          <p style="font-size:12px;color:var(--text-secondary);margin-top:10px;line-height:1.5;">
            * Daily Rate = Basic ÷ Weekdays (Mon–Fri). Full day absent = 1.0 day rate deduction; Half day = 0.5 deduction.
          </p>
        </div>

        <!-- System Information -->
        <div style="background:#F8FAFC;border:1px solid #E5EAF1;border-radius:12px;padding:16px;">
          <h4 style="font-size:13.5px;font-weight:700;color:var(--secondary-navy);margin-bottom:8px;">
            System & Environment
          </h4>
          <div style="font-size:12.5px;color:var(--text-secondary);display:flex;flex-direction:column;gap:6px;">
            <div><strong>Active User:</strong> ${user.name || user.username} (${user.role})</div>
            <div><strong>Database:</strong> MySQL / MariaDB (payroll_db) on Port 3306</div>
            <div><strong>Analytics Engine:</strong> Python 3 (pandas, matplotlib)</div>
            <div><strong>Web Engine:</strong> Java 17 Built-in HttpServer (Port 8080)</div>
          </div>
        </div>

        <!-- Admin Account Management -->
        ${user.role === "ADMIN" ? `
          <div style="border-top:1px solid #E5EAF1;padding-top:16px;display:flex;justify-content:space-between;align-items:center;">
            <div>
              <div style="font-weight:600;font-size:13px;color:var(--status-absent);">Delete Administrator Account</div>
              <div style="font-size:11.5px;color:var(--text-secondary);">Allows re-registration of a new administrator</div>
            </div>
            <button type="button" class="btn btn-danger-ghost" style="padding:6px 12px;font-size:12px;" onclick="deleteAdminAccount()">
              Delete Account
            </button>
          </div>
        ` : ''}

        <div style="display:flex;justify-content:flex-end;margin-top:6px;">
          <button type="button" class="btn ghost" onclick="document.getElementById('settingsModal').remove()">Close</button>
        </div>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
}

async function deleteAdminAccount() {
  const ok = confirm("⚠️ Are you sure you want to delete this administrator account?\n\nOnce deleted, you will be logged out, and a new administrator can create an account using the registration page.");
  if (!ok) return;
  try {
    await api("/delete-admin", {
      method: "POST",
      body: JSON.stringify({ username: user.username })
    });
    sessionStorage.clear();
    alert("Administrator account has been deleted.\nA new administrator can now register.");
    location.href = "register.html";
  } catch (err) {
    toast(err.message, "bad");
  }
}

function logout() {
  sessionStorage.clear();
  location.href = "login.html";
}

async function api(path, opts = {}) {
  const r = await fetch("/api" + path, {
    headers: { "Content-Type": "application/json" },
    ...opts
  });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.error || "Request failed");
  return d;
}

function showError(m) {
  const e = document.getElementById("err");
  if (e) {
    e.textContent = m;
    e.style.display = "block";
  }
}

const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const fmt = n => "₹" + Number(n || 0).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

function toast(m, t) {
  const existing = document.querySelector(".toast");
  if (existing) existing.remove();
  const e = document.createElement("div");
  e.className = "toast " + (t || "");
  e.innerHTML = `
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
      ${t === "bad" ? '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>' : '<path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>'}
    </svg>
    <span>${esc(m)}</span>
  `;
  document.body.appendChild(e);
  setTimeout(() => e.remove(), 3200);
}

function table(id, cols, rows, empty) {
  const container = $(id);
  if (!container) return;
  if (!rows || !rows.length) {
    container.innerHTML = `<p class="empty">${empty || "No records found."}</p>`;
    return;
  }
  container.innerHTML = `
    <table>
      <thead>
        <tr>${cols.map(c => `<th>${c[0]}</th>`).join("")}</tr>
      </thead>
      <tbody>
        ${rows.map(r => `<tr>${cols.map(c => `<td>${typeof c[1] === "function" ? c[1](r) : esc(r[c[1]])}</td>`).join("")}</tr>`).join("")}
      </tbody>
    </table>
  `;
}

const badge = s => `<span class="badge ${String(s).replace(/\s+/g, "")}">${esc(s)}</span>`;

async function fillEmployees(id, all) {
  const el = $(id);
  if (!el) return;
  const e = await api("/employees");
  el.innerHTML = (all ? `<option value="">${all}</option>` : "") + e.map(x => `<option value="${x.id}">${x.id} – ${esc(x.name)}</option>`).join("");
}

const today = () => new Date().toISOString().slice(0, 10);
