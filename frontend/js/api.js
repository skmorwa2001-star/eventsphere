/* ===========================================================
   api.js — shared by the home page and the app
   Backend URL, tiny DOM helpers, fetch wrapper, status pill
   =========================================================== */
let API = localStorage.getItem("es_api") || "http://127.0.0.1:8000";
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];

function toast(m, bad){const t=$("#toast");t.textContent=m;t.style.color=bad?"var(--err)":"var(--ok)";t.classList.add("show");clearTimeout(t._t);t._t=setTimeout(()=>t.classList.remove("show"),3200)}
async function api(path, method="GET", body){
  let r;
  try{ r = await fetch(API+path,{method,headers:body?{"Content-Type":"application/json"}:{},body:body?JSON.stringify(body):undefined}); }
  catch(e){ throw new Error("Cannot reach the server at "+API); }
  const d = await r.json().catch(()=>({}));
  if(!r.ok){
    let m = d.detail;
    if(Array.isArray(m)) m = m.map(x=>(x.loc?.slice(-1)[0]||"")+": "+x.msg).join("; ");
    throw new Error(m || "Request failed");
  }
  return d;
}
// Format an ISO date from the API for display, e.g. "Thu, Nov 5, 2026, 6:30 PM"
function fmtDate(iso){
  if(!iso)return "Date to be announced";
  return new Date(iso).toLocaleString([],{weekday:"short",year:"numeric",month:"short",day:"numeric",hour:"numeric",minute:"2-digit"});
}
const esc = s => String(s ?? "").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const open_ = id => $(id).classList.add("show");
$$(".close").forEach(b=>b.onclick=()=>b.closest(".modal").classList.remove("show"));
$$(".modal").forEach(m=>m.addEventListener("mousedown",e=>{if(e.target===m)m.classList.remove("show")}));

/* ---------- backend status pill (GET /) ---------- */
async function ping(){const s=$("#st");try{const d=await(await fetch(API+"/")).json();s.textContent="● "+(d.status||"online");s.className="chip on"}catch{s.textContent="● offline";s.className="chip off"}}
$("#st").onclick=()=>{const u=prompt("Backend URL",API);if(u){API=u.trim().replace(/\/$/,"");localStorage.setItem("es_api",API);ping();if(user)show("events")}};
ping();setInterval(ping,15000);
