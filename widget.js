(()=>{
  const DATA = {"lastUpdated": "2025-11-25T06:52:49Z", "sections": {"infotech": [{"title": "Office of Space Commerce Stakeholder Briefing on “Mission Authorization” – December 3", "url": "https://space.commerce.gov/office-of-space-commerce-stakeholder-briefing-on-mission-authorization-december-3/", "source": "Office of Space Commerce", "summary": "On Wednesday, December 3rd, from 10:00 am – 12:00 pm (ET), the U.S. Department of Commerce’s Office of Space Commerce will host a public (in-person and livestreamed) event to discuss concepts for the eventual U.S. regulatory authorization of “novel” commercial space activities.  … Office of Space Commerce Stakeholder Briefing on “Mission Authorization” – December 3 Read More »", "published": "2025-11-24T18:17:38Z"}], "deeptech": [{"title": "The ETSI Railway Communication Plugtests™ Report is Out", "url": "http://www.etsi.org/newsroom/news/2609-the-etsi-railway-communication-plugtests-report-is-out", "source": "RSS ETSI News & Press", "summary": "Published in: News Sophia Antipolis, France, 24 November 2025 ETSI is pleased to publish the Report of the interoperability event on the Future Railway Mobile Communication System (FRMCS), held from 27 to 31 October 2025. Organised by ETSI with the support of the European Union, EFTA, TCCA-Critical Communications and UIC - International union of railways, these Plugtests™ play a key role in accelerating the global adoption of future railway communications. They enable stakeholders across the value chain to test their solutions against each other, ensuring interoperability when deploying FRMCS over 5G networks and guaranteeing interworking with the legacy GSM-R system.", "published": "2025-11-24T13:00:00Z"}], "crossIndustry": [{"title": "Join DARPA for an office-wide industry day in Orlando in January", "url": "https://www.darpa.mil/news/2025/discover-dso-2026", "source": "DARPA - Defense Advanced Research Projects Agency", "summary": "D3 connects innovators with the agency on Jan. 13, 2026, to discuss game-changing capabilities.", "published": "2025-11-19T21:22:50Z"}]}};
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