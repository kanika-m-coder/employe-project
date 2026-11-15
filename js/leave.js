const admin = user.role === "ADMIN";

// Configure form and headers according to Role
if (admin) {
  fillEmployees("emp");
  if ($("formTitleText")) $("formTitleText").textContent = "Record Leave / Absence Entry";
  if ($("formSubtitleText")) $("formSubtitleText").textContent = "Submit approved absence or administrative leave directly";
  if ($("btnSubmitLeave")) $("btnSubmitLeave").textContent = "Save Leave Record";
  if ($("tableTitleText")) $("tableTitleText").textContent = "Organization Leave Logs & Requests";
  if ($("tableSubtitleText")) $("tableSubtitleText").textContent = "Review, approve, reject or delete workforce leave records";
} else {
  // Employee View: Apply for Leave
  if ($("formTitleText")) $("formTitleText").textContent = "Apply for Leave Request";
  if ($("formSubtitleText")) $("formSubtitleText").textContent = "Submit a new leave application for administrator review and approval";
  if ($("btnSubmitLeave")) $("btnSubmitLeave").textContent = "Submit Leave Request";
  if ($("tableTitleText")) $("tableTitleText").textContent = "My Leave Requests & History";
  if ($("tableSubtitleText")) $("tableSubtitleText").textContent = "Track the approval status of your submitted leave applications";

  // Pre-select and lock Employee selector to current employee
  const empEl = $("emp");
  if (empEl) {
    empEl.innerHTML = `<option value="${user.empId}" selected>#${user.empId} – ${esc(user.name || user.username)}</option>`;
    empEl.disabled = true;
  }

  // Hide admin status selector (employees always submit as Pending)
  if ($("sttGroup")) $("sttGroup").style.display = "none";
  if ($("scard")) $("scard").style.display = "none";
}

async function load() {
  try {
    const r = await api("/leave?emp=" + (admin ? "" : user.empId));
    
    table("tb", [
      ["Employee", x => `
        <div style="display:flex;align-items:center;gap:8px">
          <span style="font-weight:700;color:var(--secondary-navy);font-size:12px;background:var(--bg-primary);padding:2px 6px;border-radius:4px;border:1px solid var(--border)">#${x.empId}</span>
          <span style="font-weight:600;color:var(--text-primary)">${esc(x.name)}</span>
        </div>
      `],
      ["Leave Type", r => `<span style="font-weight:600;color:var(--secondary-navy)">${esc(r.type)}</span>`],
      ["Start Date", "startDate"],
      ["End Date", "endDate"],
      ["Working Days", r => `<b>${r.days}</b> days`],
      ["Reason", r => `<span style="color:var(--text-secondary)">${esc(r.reason || "–")}</span>`],
      ["Status", x => badge(x.status)],
      ["Actions", x => {
        if (admin) {
          if (x.status === "Pending") {
            return `
              <div style="display:flex;align-items:center;gap:6px">
                <button type="button" class="btn-sm" style="background:#059669;color:#fff;border:none;display:inline-flex;align-items:center;gap:4px;padding:4px 8px;border-radius:4px;cursor:pointer;font-weight:600;font-size:11.5px" onclick="updateStatus(${x.id}, 'Approved')" title="Approve Leave and Update Attendance">
                  <svg viewBox="0 0 24 24" width="13" height="13" stroke="currentColor" fill="none" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                  Approve
                </button>
                <button type="button" class="btn-sm" style="background:#DC2626;color:#fff;border:none;display:inline-flex;align-items:center;gap:4px;padding:4px 8px;border-radius:4px;cursor:pointer;font-weight:600;font-size:11.5px" onclick="updateStatus(${x.id}, 'Rejected')" title="Reject Leave Request">
                  <svg viewBox="0 0 24 24" width="13" height="13" stroke="currentColor" fill="none" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  Reject
                </button>
                <button type="button" class="btn-sm del-btn" onclick="del(${x.id})" title="Delete Record">
                  <svg viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                </button>
              </div>
            `;
          }
          return `
            <button type="button" class="btn-sm del-btn" onclick="del(${x.id})" title="Delete Leave Record">
              <svg viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
              Delete
            </button>
          `;
        } else {
          // Employee mode: can withdraw pending requests
          if (x.status === "Pending") {
            return `
              <button type="button" class="btn-sm del-btn" onclick="cancelRequest(${x.id})" title="Cancel this Pending Request">
                <svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                Cancel
              </button>
            `;
          }
          return `<span style="color:var(--text-muted);font-size:12px;font-style:italic">Processed</span>`;
        }
      }]
    ], r);

    if (admin) {
      const summaryData = await api("/leave/summary");
      table("sm", [
        ["Employee", x => `
          <div style="display:flex;align-items:center;gap:8px">
            <span style="font-weight:700;color:var(--secondary-navy);font-size:12px;background:var(--bg-primary);padding:2px 6px;border-radius:4px;border:1px solid var(--border)">#${x.empId}</span>
            <span style="font-weight:600;color:var(--text-primary)">${esc(x.name)}</span>
          </div>
        `],
        ["Absent Days", x => `<span style="color:var(--status-absent);font-weight:700">${x.absent}</span>`],
        ["Half Days", x => `<span style="color:var(--status-pending);font-weight:600">${x.halfDays}</span>`],
        ["On Leave Days", x => `<span style="color:var(--primary-accent);font-weight:600">${x.onLeave}</span>`]
      ], summaryData);
    }
  } catch (e) {
    showError(e.message);
  }
}

async function updateStatus(id, newStatus) {
  const actionText = newStatus === "Approved" ? "approve this leave request and mark attendance" : "reject this leave request";
  if (!confirm(`Are you sure you want to ${actionText}?`)) return;
  try {
    await api("/leave/" + id, {
      method: "PUT",
      body: JSON.stringify({ status: newStatus })
    });
    toast(`Leave request has been ${newStatus.toLowerCase()}!`);
    load();
    if (typeof initNotifications === "function") initNotifications();
  } catch (e) {
    toast(e.message, "bad");
  }
}

async function cancelRequest(id) {
  if (!confirm("Are you sure you want to cancel and withdraw this pending leave request?")) return;
  try {
    await api("/leave/" + id, { method: "DELETE" });
    toast("Leave request cancelled successfully");
    load();
    if (typeof initNotifications === "function") initNotifications();
  } catch (e) {
    toast(e.message, "bad");
  }
}

async function del(id) {
  if (!confirm("⚠️ Delete this leave record? Attendance already marked is not changed.")) return;
  try {
    await api("/leave/" + id, { method: "DELETE" });
    toast("Leave record removed");
    load();
    if (typeof initNotifications === "function") initNotifications();
  } catch (e) {
    toast(e.message, "bad");
  }
}

$("f").onsubmit = async e => {
  e.preventDefault();
  const empVal = admin ? $("emp").value : user.empId;
  const statusVal = admin ? $("stt").value : "Pending";

  if (!empVal) {
    toast("Please select an employee", "bad");
    return;
  }

  try {
    await api("/leave", {
      method: "POST",
      body: JSON.stringify({
        empId: empVal,
        type: $("type").value,
        startDate: $("sd").value,
        endDate: $("ed").value,
        status: statusVal,
        reason: $("rs").value
      })
    });
    toast(admin ? "Leave record saved successfully" : "Leave request submitted for admin review!");
    $("f").reset();
    if (!admin && $("emp")) {
      $("emp").innerHTML = `<option value="${user.empId}" selected>#${user.empId} – ${esc(user.name || user.username)}</option>`;
      $("emp").disabled = true;
    }
    load();
    if (typeof initNotifications === "function") initNotifications();
  } catch (x) {
    toast(x.message, "bad");
  }
};

load();
