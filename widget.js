(()=>{
  const DATA = {"lastUpdated": "2025-12-22T06:55:42Z", "sections": {"space": [{"title": "USG Seeks Private Sector Participation in a “Discussion Group on Space Situational Awareness”", "url": "https://space.commerce.gov/usg-seeks-private-sector-participation-in-a-discussion-group-on-space-situational-awareness/", "source": "Office of Space Commerce", "summary": "The U.S. Department of State’s Office of Space Affairs has posted a solicitation seeking private sector participation in a “Discussion Group on the topic of Space Situational Awareness (SSA).” Background: The growing number of satellites in orbit has afforded increased … USG Seeks Private Sector Participation in a “Discussion Group on Space Situational Awareness” Read More »", "published": "2025-12-15T15:03:40Z"}], "pharma": [{"title": "IMDRF Strategic Plan 2026-2030", "url": "https://www.imdrf.org/documents/imdrf-strategic-plan-2026-2030", "source": "IMDRF - Documents", "summary": "The strategic plan outlines the mission, objectives and priorities of the International Medical Device Regulators Forum (IMDRF).", "published": "2025-12-19T12:00:00Z"}], "infotech": [{"title": "OSC Seeks Stakeholder Feedback on Draft “Mission Authorization” Concept", "url": "https://space.commerce.gov/osc-seeks-stakeholder-feedback-on-draft-mission-authorization-concept/", "source": "Office of Space Commerce", "summary": "Section 5 of Executive Order 14335, “Enabling Competition in the Commercial Space Industry,” directs the U.S. Secretary of Commerce to develop and “propose a process for individualized mission authorizations for activities that are […] not clearly or straightforwardly governed by existing … OSC Seeks Stakeholder Feedback on Draft “Mission Authorization” Concept Read More »", "published": "2025-12-17T14:44:33Z"}]}};
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