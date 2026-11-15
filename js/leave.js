const admin = user.role === "ADMIN";

// UI Layout configuration based on Role
if (admin) {
  // Admin View: Display Leave Approving Option Card, hide Employee Apply form
  if ($("approvalCard")) $("approvalCard").style.display = "block";
  if ($("fcard")) $("fcard").style.display = "none";
  if ($("scard")) $("scard").style.display = "block";
  if ($("tableTitleText")) $("tableTitleText").textContent = "Organization Leave Logs & Requests";
  if ($("tableSubtitleText")) $("tableSubtitleText").textContent = "Review, track and manage workforce leave history";
} else {
  // Employee View: Display Apply for Leave Request Card, hide Admin Approvals
  if ($("approvalCard")) $("approvalCard").style.display = "none";
  if ($("fcard")) $("fcard").style.display = "block";
  if ($("scard")) $("scard").style.display = "none";
  if ($("tableTitleText")) $("tableTitleText").textContent = "My Leave Requests & History";
  if ($("tableSubtitleText")) $("tableSubtitleText").textContent = "Track the approval status of your submitted leave applications";

  // Pre-fill and lock Employee select to current logged-in employee
  const empEl = $("emp");
  if (empEl) {
    empEl.innerHTML = `<option value="${user.empId}" selected>#${user.empId} – ${esc(user.name || user.username)}</option>`;
    empEl.disabled = true;
  }
}

async function load() {
  try {
    const r = await api("/leave?emp=" + (admin ? "" : user.empId));

    if (admin) {
      // Filter pending leave requests for approval
      const pendingList = r.filter(x => x.status === "Pending");

      // Update Pending Badge in Approval Card Header
      if ($("pendingBadge")) {
        $("pendingBadge").textContent = `${pendingList.length} Pending`;
        $("pendingBadge").className = pendingList.length > 0 ? "badge Pending" : "badge Approved";
      }

      // Render Pending Leave Approvals Table
      if (pendingList.length === 0) {
        $("approvalTable").innerHTML = `
          <div style="padding:28px 20px;text-align:center;background:var(--bg-primary);border-radius:var(--radius-md);border:1px dashed var(--border)">
            <div style="width:38px;height:38px;margin:0 auto 10px;border-radius:50%;background:rgba(5,150,105,0.1);display:grid;place-items:center;color:#059669">
              <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" fill="none" stroke-width="2.2"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
            <div style="font-weight:600;color:var(--text-primary);font-size:13.5px">No Pending Leave Requests</div>
            <p style="font-size:12px;color:var(--text-secondary);margin-top:3px">All employee leave requests have been reviewed and approved or rejected.</p>
          </div>
        `;
      } else {
        table("approvalTable", [
          ["Employee Name", x => `
            <div style="display:flex;align-items:center;gap:8px">
              <span style="font-weight:700;color:var(--secondary-navy);font-size:12px;background:var(--bg-primary);padding:2px 6px;border-radius:4px;border:1px solid var(--border)">#${x.empId}</span>
              <span style="font-weight:600;color:var(--text-primary)">${esc(x.name)}</span>
            </div>
          `],
          ["Department", x => `<span style="font-weight:600;color:var(--secondary-navy)">${esc(x.department || "–")}</span>`],
          ["Designation", x => `<span style="color:var(--text-secondary);font-size:13px">${esc(x.designation || "–")}</span>`],
          ["Leave Period", x => `
            <div>
              <span style="font-weight:600;color:var(--text-primary)">${esc(x.type)}</span>
              <div style="font-size:11.5px;color:var(--text-muted);margin-top:2px">${x.startDate} to ${x.endDate} (<b>${x.days}</b> day${x.days === 1 ? '' : 's'})</div>
            </div>
          `],
          ["Reason", x => `<span style="color:var(--text-primary);font-weight:500;font-size:13px">${esc(x.reason || "–")}</span>`],
          ["Approval Decision", x => `
            <div style="display:flex;align-items:center;gap:8px">
              <button type="button" class="btn-sm" style="background:#059669;color:#ffffff;border:none;display:inline-flex;align-items:center;gap:5px;padding:6px 12px;border-radius:6px;cursor:pointer;font-weight:600;font-size:12px;box-shadow:0 1px 2px rgba(5,150,105,0.2)" onclick="updateStatus(${x.id}, 'Approved', '${esc(x.name)}')" title="Approve Request & Mark Attendance">
                <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" fill="none" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                Approve
              </button>
              <button type="button" class="btn-sm" style="background:#DC2626;color:#ffffff;border:none;display:inline-flex;align-items:center;gap:5px;padding:6px 12px;border-radius:6px;cursor:pointer;font-weight:600;font-size:12px;box-shadow:0 1px 2px rgba(220,38,38,0.2)" onclick="updateStatus(${x.id}, 'Rejected', '${esc(x.name)}')" title="Reject Leave Request">
                <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" fill="none" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                Reject
              </button>
            </div>
          `]
        ], pendingList);
      }
    }

    // Render Organization Leave Logs & Requests Table
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

    // Cumulative summary for Admin
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

async function updateStatus(id, newStatus, empName) {
  const actionText = newStatus === "Approved" ? "approve this leave request and mark attendance" : "reject this leave request";
  if (!confirm(`Are you sure you want to ${actionText} for ${empName || 'the employee'}?`)) return;
  try {
    await api("/leave/" + id, {
      method: "PUT",
      body: JSON.stringify({ status: newStatus })
    });
    toast(`Leave request for ${empName || 'employee'} has been ${newStatus.toLowerCase()}!`);
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
  const empVal = user.empId;
  if (!empVal) {
    toast("Please log in as an employee to submit leave requests", "bad");
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
        status: "Pending",
        reason: $("rs").value
      })
    });
    toast("Leave request submitted for admin review!");
    $("f").reset();
    if ($("emp")) {
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
