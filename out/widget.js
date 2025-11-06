(()=>{
  const DATA = {"lastUpdated": "2025-11-06T06:53:35Z", "sections": {"infotech": [{"title": "New PIC/S Chairperson and Executive Bureau", "url": "http://www.picscheme.org/en/news/136/new-pics-chairperson-and-executive-bureau-136", "source": "Picscheme", "summary": "Geneva, 4 November 2025:\nA new PIC/S Chairperson and Executive Bureau were elected as from 1 January 2026 by the PIC/S Committee at its meeting in Hong Kong SAR, China, on 3 November 2025.At this occasion, the PIC/S Committee unanimously elected Ms Kathleen Sinninger (US FDA) as Chairperson for the period 2026-2027. Ms Sinninger will be assisted by Mr Gwylim Janssens (Netherlands / IGJ), PIC/S Deputy Chairperson. The full Executive Bureau for the period 2026-2027 consists of:Ms Kathleen Sinninger (US FDA), PIC/S Chairperson;Mr Gwylim Janssens (Netherlands / IGJ), PIC/S Deputy Chairperson and Chair of the Sub-Committee on Training (SCT);Mr Jacques Morénas (France / ANSM), immediate past PIC/S Chairperson;Ms Virginie Waysbaum (France / ANSM), Chair of the Sub-Committee on Compliance (SCC);Mr Roel Op den Camp (Switzerland / Swissmedic), Chair of the Sub-Committe on Strategic Development (SCSD);Mr Marco Paolo Fulfaro (Italy / AIFA), Chair of the Sub-Committee on GM(D)P Harmonisation (SCH);Ms Ana Carolina Moreira Araujo (Brazil / ANVISA), Chair of the Sub-Committee on Communication (SC COM);Ms Ying-Hua (Ellen) Chen (Chinese Taipei / TFDA), Chair of the Sub-Committee on Budget, Risk and Audit (SCB); andMs Nicole Proctor (Canada / ROEB), Chair of the Sub-Committee on Expert Circles (SCEC).\nThe PIC/S Committee elected the Members, Deputy Chairs and Chairs of the PIC/S Sub-Committee structure for the period 2026-2027. Office holders were elected for the following seven Sub-Committees: Training (SCT); Expert Circles (SCEC); Strategic Development (SCSD); Compliance (SCC); GM(D)P Harmonisation (SCH); Budget, Risk and Audit (SCB) and Communication (SC COM). All Sub-Committee Chairs will be Members of the PIC/S Executive Bureau as listed above.", "published": "2025-11-04T05:10:00Z"}]}};
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