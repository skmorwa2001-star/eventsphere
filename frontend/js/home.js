/* ===========================================================
   home.js — landing page behaviour (needs api.js first)
   Pulls live data from GET /events (+ analytics) to fill the
   stats, the event preview cards and the "View details" modal
   =========================================================== */

let homeEvents = [];

async function loadHome() {
  const grid = $("#liveEvents");
  try {
    const data = await api("/events");
    $("#statEvents").textContent = data.total;
    $("#statSeats").textContent = data.events.reduce((n, e) => n + e.capacity, 0);

    if (!data.events.length) {
      grid.innerHTML = '<div class="empty glass" style="grid-column:1/-1">No events yet — organizers can create the first one!</div>';
      return;
    }

    // Show the first 3 events; fetch registrations so we can show seats left
    homeEvents = await Promise.all(data.events.slice(0, 3).map(async e => {
      try {
        const a = await api(`/events/${e.id}/analytics`);
        return { ...e, taken: a.total_registrations };
      } catch { return { ...e, taken: 0 }; }
    }));

    grid.innerHTML = homeEvents.map(e => `
      <article class="glass card">
        <h3>${esc(e.title)}</h3>
        <div class="when">📅 ${fmtDate(e.event_date)}</div>
        <div class="loc">📍 ${esc(e.location)}</div>
        <p>${esc(e.description || "No description provided.")}</p>
        <div class="small">${Math.max(e.capacity - e.taken, 0)} of ${e.capacity} seats left</div>
        <div class="row">
          <button class="btn ghost sm" onclick="showDetails(${e.id})">View details</button>
          <a class="btn sm" href="app.html" style="text-decoration:none">Register</a>
        </div>
      </article>`).join("");
  } catch (err) {
    $("#statEvents").textContent = "–";
    $("#statSeats").textContent = "–";
    grid.innerHTML = `<div class="empty glass" style="grid-column:1/-1">${esc(err.message)}</div>`;
  }
}

/* ---------- event details modal ---------- */
function showDetails(id) {
  const e = homeEvents.find(x => x.id === id);
  const left = Math.max(e.capacity - e.taken, 0);
  const pct = Math.min(100, (e.taken / e.capacity) * 100);

  $("#dTitle").textContent = e.title;
  $("#dBody").innerHTML = `
    <div class="when">📅 ${fmtDate(e.event_date)}</div>
    <div class="loc" style="margin:6px 0 14px">📍 ${esc(e.location)}</div>
    <p class="detail-desc">${esc(e.description || "No description provided.")}</p>
    <div class="stats">
      <div class="stat"><b>${e.capacity}</b><span class="small">Capacity</span></div>
      <div class="stat"><b>${e.taken}</b><span class="small">Registered</span></div>
      <div class="stat"><b>${left}</b><span class="small">Seats left</span></div>
    </div>
    <div class="meter"><i style="width:${pct}%"></i></div>`;
  $("#dActions").innerHTML = `
    <button class="btn ghost close">Close</button>
    <a class="btn" href="app.html" style="text-decoration:none">${left ? "Log in to register" : "Sold out"}</a>`;
  // buttons are created dynamically, so wire up Close here
  $("#dActions .close").onclick = () => $("#mDet").classList.remove("show");
  $("#mDet").classList.add("show");
}

loadHome();
