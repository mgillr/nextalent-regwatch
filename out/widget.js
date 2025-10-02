(()=>{
  const DATA = {"lastUpdated": "2025-10-02T06:58:17Z", "sections": {"pharma": [{"title": "IMDRF 28th MC Meeting Sapporo, Japan September 2025 - Outcome Statement", "url": "https://www.imdrf.org/documents/imdrf-28th-mc-meeting-sapporo-japan-september-2025-outcome-statement", "source": "IMDRF - Documents", "summary": "IMDRF 28th MC Meeting Sapporo, Japan September 2025 - Outcome Statement", "published": "2025-09-30T12:00:00Z"}]}};
  function esc(s){return (s||"").replace(/[&<>"]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'})[c]||c);}
  function titleMap(k){return ({aviation:"Aviation",space:"Space",pharma:"Pharma & MedTech",automotive:"Automotive / EV / Clean energy",infotech:"InfoSec & InfoTech",deeptech:"Deep Tech & Advanced Engineering",crossIndustry:"Cross‑industry"})[k]||k;}
  function render(id) {
    const root = document.getElementById(id||"regwatch-root"); if(!root) return;
    const wrap = document.createElement("div"); wrap.className="regwatch";
    const h1 = document.createElement("h1"); h1.textContent="Daily Regulatory Brief"; wrap.appendChild(h1);
    const meta = document.createElement("div"); meta.style.opacity=".7"; meta.style.margin="0 0 1rem";
    meta.textContent="Updated " + new Date(DATA.lastUpdated).toUTCString(); wrap.appendChild(meta);
    const order = ["crossIndustry","deeptech","infotech","automotive","pharma","aviation","space"];
    for(const k of order){
      const arr = (DATA.sections||{})[k]; if(!arr||!arr.length) continue;
      const h2=document.createElement("h2"); h2.textContent=titleMap(k); wrap.appendChild(h2);
      const ul=document.createElement("ul"); ul.style.margin=".2rem 0 1rem 1.2rem";
      for(const it of arr){
        const li=document.createElement("li"); li.style.margin=".4rem 0"; li.style.lineHeight="1.3";
        const dateStr = it.published ? new Date(it.published).toLocaleDateString() : '';
        li.innerHTML = "<strong>"+esc(it.title)+"</strong> — "+(dateStr ? esc(dateStr)+" — " : "")+esc(it.source)+"<br><a href='"+esc(it.url)+"' target='_blank' rel='noopener'>"+esc(it.url)+"</a>";
        ul.appendChild(li);
      }
      wrap.appendChild(ul);
    }
    root.innerHTML=""; root.appendChild(wrap);
    // JSON-LD
    try {
      const items = Object.values(DATA.sections||{}).flat().map((it,i)=>({"@type":"ListItem","position":i+1,"url":it.url,"name":it.title}));
      const ld = {"@context":"https://schema.org","@type":"ItemList","name":"Nextalent Daily Regulatory Brief","dateCreated":DATA.lastUpdated,"itemListElement":items};
      const tag=document.createElement("script"); tag.type="application/ld+json"; tag.textContent=JSON.stringify(ld); document.head.appendChild(tag);
    } catch(_e){}
  }
  window.NextalentRegwatch={data:DATA,render};
  if(!document.currentScript || document.currentScript.dataset.autorender!=="false"){
    if(document.readyState!=="loading") render(); else document.addEventListener("DOMContentLoaded",()=>render());
  }
})();