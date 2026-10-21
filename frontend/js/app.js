/* ===========================================================
   app.js — EventSphere dashboard logic (needs api.js first)
   Sections: state · auth · shell · events · tickets · organizer
   =========================================================== */

/* ---------- state ---------- */
let user = JSON.parse(localStorage.getItem("es_user") || "null");
let role = "participant", mode = "login", editId = null, regEvent = null, mgEvent = null, events = [];

/* ---------- auth ---------- */
$$("#roleSeg button").forEach(b=>b.onclick=()=>{role=b.dataset.r;$$("#roleSeg button").forEach(x=>x.classList.toggle("on",x===b))});
$("#swBtn").onclick=e=>{e.preventDefault();mode=mode==="login"?"signup":"login";
  $("#nameWrap").classList.toggle("hide",mode==="login");
  $("#authT").textContent=mode==="login"?"Welcome back":"Create account";
  $("#authBtn").textContent=mode==="login"?"Log in":"Sign up";
  $("#swTxt").textContent=mode==="login"?"No account?":"Have an account?";
  $("#swBtn").textContent=mode==="login"?"Sign up":"Log in"};
$("#authBtn").onclick=async()=>{
  const email=$("#aEmail").value.trim(), password=$("#aPass").value;
  try{
    let d;
    if(mode==="signup"){
      await api("/auth/signup","POST",{name:$("#aName").value.trim(),email,password,role});
      toast("Account created!");
    }
    d = await api("/auth/login","POST",{email,password,role});
    user=d.user; localStorage.setItem("es_user",JSON.stringify(user)); boot();
  }catch(e){toast(e.message,true)}
};
$("#out").onclick=()=>{user=null;localStorage.removeItem("es_user");boot()};

/* ---------- shell ---------- */
function boot(){
  const li=!!user;
  $("#auth").classList.toggle("hide",li);
  ["#nav","#who","#out"].forEach(s=>$(s).classList.toggle("hide",!li));
  if(!li){$$("section[id^=v-]").forEach(s=>s.classList.add("hide"));return}
  const org=user.role==="organizer";
  $$(".org").forEach(e=>e.classList.toggle("hide",!org));
  $$(".par").forEach(e=>e.classList.toggle("hide",org));
  $("#who").textContent=user.name+" · "+user.role;
  show("events");
}
function show(v){
  if(v!=="checkin")stopScan(); // turn the camera off when leaving Check-in
  $$(".tab").forEach(t=>t.classList.toggle("on",t.dataset.v===v));
  $$("section[id^=v-]").forEach(s=>s.classList.toggle("hide",s.id!=="v-"+v));
  if(v==="events")loadEvents(); if(v==="tickets")renderTickets();
}
$$(".tab").forEach(t=>t.onclick=()=>show(t.dataset.v));

/* ---------- events ---------- */
async function loadEvents(){
  const g=$("#evGrid"); g.innerHTML='<div class="empty">Loading…</div>';
  try{
    const d=await api("/events");
    events=await Promise.all(d.events.map(async e=>{
      try{const a=await api(`/events/${e.id}/analytics`);return{...e,taken:a.total_registrations}}catch{return{...e,taken:0}}
    }));
    if(!events.length){g.innerHTML='<div class="empty glass" style="grid-column:1/-1">No events yet.</div>';return}
    const org=user.role==="organizer";
    g.innerHTML=events.map(e=>{
      const left=Math.max(e.capacity-e.taken,0), pct=Math.min(100,e.taken/e.capacity*100);
      return `<article class="glass card">
        <h3>${esc(e.title)}</h3><div class="when">📅 ${fmtDate(e.event_date)}</div><div class="loc">📍 ${esc(e.location)}</div>
        <p>${esc(e.description||"No description provided.")}</p>
        <div class="meter"><i style="width:${pct}%"></i></div>
        <div class="small">${left} of ${e.capacity} seats left</div>
        <div class="row"><button class="btn ghost sm" onclick="showDetails(${e.id})">View details</button>${org
          ?`<button class="btn sm" onclick="manage(${e.id})">Manage</button><button class="btn ghost sm" onclick="editEv(${e.id})">Edit</button><button class="btn del sm" onclick="delEv(${e.id})">Delete</button>`
          :`<button class="btn sm" ${left?"":"disabled"} onclick="regOpen(${e.id})">${left?"Register":"Sold out"}</button>`}</div>
      </article>`}).join("");
  }catch(e){g.innerHTML=`<div class="empty glass" style="grid-column:1/-1">${esc(e.message)}</div>`}
}
$("#newEv").onclick=()=>{editId=null;$("#evT").textContent="New Event";["#eTitle","#eDesc","#eDate","#eLoc","#eCap"].forEach(s=>$(s).value="");open_("#mEv")};
window.editEv=id=>{const e=events.find(x=>x.id===id);editId=id;$("#evT").textContent="Edit Event";
  $("#eTitle").value=e.title;$("#eDesc").value=e.description||"";$("#eDate").value=e.event_date?e.event_date.slice(0,16):"";$("#eLoc").value=e.location;$("#eCap").value=e.capacity;open_("#mEv")};
$("#evSave").onclick=async()=>{
  const b={title:$("#eTitle").value.trim(),description:$("#eDesc").value.trim()||null,event_date:$("#eDate").value||null,location:$("#eLoc").value.trim(),capacity:+$("#eCap").value};
  if(!b.event_date){toast("Please pick a date and time",true);return}
  try{
    await (editId?api("/events/"+editId,"PUT",b):api("/events","POST",b));
    $("#mEv").classList.remove("show");toast(editId?"Event updated":"Event created");loadEvents();
  }catch(e){toast(e.message,true)}
};
/* ---------- event details ---------- */
window.showDetails=id=>{
  const e=events.find(x=>x.id===id),left=Math.max(e.capacity-e.taken,0),pct=Math.min(100,e.taken/e.capacity*100);
  $("#dTitle").textContent=e.title;
  $("#dBody").innerHTML=`<div class="when">📅 ${fmtDate(e.event_date)}</div>
    <div class="loc" style="margin:6px 0 14px">📍 ${esc(e.location)}</div>
    <p class="detail-desc">${esc(e.description||"No description provided.")}</p>
    <div class="stats"><div class="stat"><b>${e.capacity}</b><span class="small">Capacity</span></div>
    <div class="stat"><b>${e.taken}</b><span class="small">Registered</span></div>
    <div class="stat"><b>${left}</b><span class="small">Seats left</span></div></div>
    <div class="meter"><i style="width:${pct}%"></i></div>`;
  const org=user.role==="organizer";
  $("#dActions").innerHTML=`<button class="btn ghost" onclick="$('#mDet').classList.remove('show')">Close</button>`+
    (org?`<button class="btn ghost" onclick="$('#mDet').classList.remove('show');editEv(${id})">Edit</button><button class="btn" onclick="$('#mDet').classList.remove('show');manage(${id})">Manage</button>`
        :`<button class="btn" ${left?"":"disabled"} onclick="$('#mDet').classList.remove('show');regOpen(${id})">${left?"Register":"Sold out"}</button>`);
  open_("#mDet");
};
window.delEv=async id=>{if(!confirm("Delete this event and its registrations?"))return;
  try{await api("/events/"+id,"DELETE");toast("Event deleted");loadEvents()}catch(e){toast(e.message,true)}};

/* ---------- registration & tickets ---------- */
const getTk=()=>JSON.parse(localStorage.getItem("es_tickets_"+user.email)||"[]");
window.regOpen=id=>{regEvent=events.find(e=>e.id===id);$("#rT").textContent="Register · "+regEvent.title;
  $("#rName").value=user.name;$("#rEmail").value=user.email;open_("#mReg")};
$("#rSave").onclick=async()=>{
  try{
    const d=await api(`/events/${regEvent.id}/register`,"POST",{attendee_name:$("#rName").value.trim(),attendee_email:$("#rEmail").value.trim()});
    const t={...d.registration,event_title:regEvent.title};
    localStorage.setItem("es_tickets_"+user.email,JSON.stringify([t,...getTk()]));
    $("#mReg").classList.remove("show");toast("Registered!");showTicket(t);loadEvents();
  }catch(e){toast(e.message,true)}
};
function showTicket(t){$("#tkSub").textContent=t.event_title+" · "+t.attendee_name;$("#tkQr").src=API+t.qr_code_url;$("#tkCode").textContent=t.ticket_code;open_("#mTk")}
function renderTickets(){
  const t=getTk(),g=$("#tkGrid");
  if(!t.length){g.innerHTML='<div class="empty glass" style="grid-column:1/-1">No tickets yet. Register for an event to get one.</div>';return}
  g.innerHTML=t.map((x,i)=>`<article class="glass card"><h3>${esc(x.event_title)}</h3><p>${esc(x.attendee_name)}<br>${esc(x.attendee_email)}</p>
    <div class="row"><button class="btn sm" onclick="showTicket(getTk()[${i}])">View QR</button>
    <button class="btn del sm" onclick="cancelTk(${i})">Cancel</button></div></article>`).join("");
}
$("#tkDl").onclick=async()=>{ // saves the QR image so it can be tested with "Upload QR image"
  try{const b=await(await fetch($("#tkQr").src)).blob();const a=document.createElement("a");
    a.href=URL.createObjectURL(b);a.download="ticket-qr.png";a.click()}catch{toast("Could not download the QR",true)}
};
window.cancelTk=async i=>{const t=getTk();if(!confirm("Cancel this registration?"))return;
  try{await api("/registrations/"+t[i].id,"DELETE");t.splice(i,1);localStorage.setItem("es_tickets_"+user.email,JSON.stringify(t));toast("Registration cancelled");renderTickets()}
  catch(e){toast(e.message,true)}};
window.getTk=getTk;window.showTicket=showTicket;

/* ---------- organizer: manage & check-in ---------- */
window.manage=async id=>{
  mgEvent=id;
  try{
    const [a,r]=await Promise.all([api(`/events/${id}/analytics`),api(`/events/${id}/registrations`)]);
    $("#mgT").textContent=a.event_title;
    $("#mgStats").innerHTML=[["Capacity",a.capacity],["Registered",a.total_registrations],["Checked in",a.checked_in],["Pending",a.pending_count_in],["Seats left",a.available_seats]]
      .map(([k,v])=>`<div class="stat"><b>${v}</b><span class="small">${k}</span></div>`).join("");
    $("#mgBody").innerHTML=r.attendees.length?r.attendees.map(x=>`<tr><td>${esc(x.attendee_name)}</td><td>${esc(x.attendee_email)}</td>
      <td><span class="tag ${x.checked_in?"ok":""}">${x.checked_in?"Checked in":"Pending"}</span></td>
      <td><button class="btn del sm" onclick="rmReg(${x.id})">Remove</button></td></tr>`).join("")
      :'<tr><td colspan="4" class="empty">No registrations yet.</td></tr>';
    open_("#mMg");
  }catch(e){toast(e.message,true)}
};
window.rmReg=async rid=>{if(!confirm("Remove this attendee?"))return;
  try{await api("/registrations/"+rid,"DELETE");toast("Attendee removed");manage(mgEvent);loadEvents()}catch(e){toast(e.message,true)}};
/* ---------- check-in (manual + QR scanner) ---------- */
// Calls POST /registrations/check-in/{code} and shows the result.
async function doCheckIn(code){
  const out=$("#ciRes");
  code=(code||"").trim(); if(!code)return;
  try{
    const d=await api("/registrations/check-in/"+encodeURIComponent(code),"POST");
    out.className="ci-res ok";out.textContent="✓ "+d.attendee_name+" checked in (event #"+d.event_id+")";
    toast("Checked in: "+d.attendee_name);$("#ciCode").value="";
  }catch(e){out.className="ci-res bad";out.textContent="✕ "+e.message;toast(e.message,true)}
}
$("#ciBtn").onclick=()=>doCheckIn($("#ciCode").value);
$("#ciCode").addEventListener("keydown",e=>{if(e.key==="Enter")$("#ciBtn").click()});

/* ---------- QR scanner ---------- */
let stream=null, scanning=false, lastCode="", lastTime=0;
// Native detector where available (Chrome/Edge/Android); jsQR otherwise.
const detector=("BarcodeDetector" in window)?new BarcodeDetector({formats:["qr_code"]}):null;

// Decode a QR from a <video> or <img>. Tries the browser's native detector first,
// then jsQR at several scales (helps with big screenshots and small images).
// quick=true (used for live video) only tries the original size, to stay fast.
async function decodeQR(source,quick){
  if(detector){try{const r=await detector.detect(source);if(r[0])return r[0].rawValue}catch{}}
  if(!window.jsQR)throw new Error("QR library not loaded");
  const w=source.videoWidth||source.naturalWidth,h=source.videoHeight||source.naturalHeight;
  if(!w||!h)return null;
  const c=$("#scanCanvas"),ctx=c.getContext("2d",{willReadFrequently:true});
  for(const scale of(quick?[1]:[1,.5,.25,2])){
    const cw=Math.round(w*scale),ch=Math.round(h*scale);
    if(cw<60||ch<60||cw>3000)continue;
    const pad=Math.round(Math.min(cw,ch)*.1);          // white margin: QR codes need a "quiet zone"
    c.width=cw+pad*2;c.height=ch+pad*2;
    ctx.fillStyle="#fff";ctx.fillRect(0,0,c.width,c.height); // also fixes transparent PNGs
    ctx.drawImage(source,pad,pad,cw,ch);
    const d=ctx.getImageData(0,0,c.width,c.height);
    const r=jsQR(d.data,d.width,d.height,{inversionAttempts:"attemptBoth"});
    if(r&&r.data)return r.data;
  }
  return null;
}
async function startScan(){
  try{stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:"environment"}})}
  catch(e){toast("Camera unavailable: "+e.message,true);$("#scanHint").textContent="Allow camera access, or use the image upload / manual entry.";return}
  const v=$("#scanVideo");v.srcObject=stream;await v.play();
  $("#scanBox").classList.remove("hide");$("#scanBtn").textContent="⏹ Stop scanner";
  $("#scanHint").textContent="Point the camera at the attendee's QR code.";
  scanning=true;scanLoop();
}
function stopScan(){
  scanning=false;
  if(stream){stream.getTracks().forEach(t=>t.stop());stream=null}
  $("#scanBox").classList.add("hide");$("#scanBtn").textContent="📷 Start scanner";
}
async function scanLoop(){
  if(!scanning)return;
  const v=$("#scanVideo");
  if(v.readyState>=2){
    let code=null;try{code=await decodeQR(v,true)}catch{}
    // ignore the same code for 4s so one scan doesn't fire repeatedly
    if(code&&(code!==lastCode||Date.now()-lastTime>4000)){
      lastCode=code;lastTime=Date.now();await doCheckIn(code);
    }
  }
  requestAnimationFrame(scanLoop);
}
$("#scanBtn").onclick=()=>scanning?stopScan():startScan();
// Fallback: decode a saved QR image (e.g. screenshot of the ticket)
$("#scanFile").onchange=async e=>{
  const f=e.target.files[0];if(!f)return;
  const img=new Image();img.src=URL.createObjectURL(f);
  try{await img.decode()}catch{toast("Could not read that image file",true);e.target.value="";return}
  let code=null;
  try{code=await decodeQR(img)}catch(err){toast(err.message,true);e.target.value="";return}
  code?doCheckIn(code):toast("No QR found. Use a clear, full image of the ticket QR.",true);
  e.target.value="";
};

boot();
