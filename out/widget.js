(()=>{
  const DATA = {"lastUpdated": "2025-09-03T00:49:07Z", "sections": {"space": [{"title": "NASA 2026 Human Lander Challenge", "url": "https://www.nasa.gov/directorates/stmd/prizes-challenges-crowdsourcing-program/center-of-excellence-for-collaborative-innovation-coeci/nasa-2026-human-lander-challenge/", "source": "NASA", "date": "2025-09-02", "summary": "NASA’s Human Lander Challenge (HuLC) is an initiative supporting its Exploration Systems Development Mission Directorate’s (ESDMD’s) efforts to explore innovative solutions for a variety of known technology development areas for human landing systems (HLS). Landers are used to safely ferry astronauts to and from the lunar surface as part of the mission architecture for NASA’s Artemis […]"}, {"title": "Lydia Rodriguez Builds a Career of Service and Support at NASA", "url": "https://www.nasa.gov/centers-and-facilities/johnson/lydia-rodriguez-builds-a-career-of-service-and-support-at-nasa/", "source": "NASA", "date": "2025-09-02", "summary": "Lydia Rodriguez is an office administrator in the Flight Operations Directorate’s Operations Division and Operations Tools and Procedures Branch at NASA’s Johnson Space Center in Houston.  Over nearly two decades, she has supported nine organizations, helping enable NASA’s missions and forming lasting relationships along the way.  “I’ve had the opportunity to meet many different people […]"}, {"title": "What’s Up: September 2025 Skywatching Tips from NASA", "url": "https://science.nasa.gov/centers-and-facilities/jpl/whats-up-september-2025-skywatching-tips-from-nasa/", "source": "NASA", "date": "2025-09-02", "summary": "Saturn’s spectacle, a Conjunction, and the Autumnal Equinox Saturn shines throughout the month, a conjunction sparkles in the sky, and we welcome the autumnal equinox.  Skywatching Highlights Transcript What’s Up for September? Saturn puts on a spectacular show, a sunrise conjunction shines bright, and we ring in the autumnal equinox. Saturn at Opposition Saturn will […]"}, {"title": "Circular Star Trails", "url": "https://www.nasa.gov/image-article/circular-star-trails/", "source": "NASA", "date": "2025-09-02", "summary": "On July 26, 2025, NASA astronaut Nichole Ayers took this long-exposure photograph – taken over 31 minutes from a window inside the International Space Station’s Kibo laboratory module – capturing the circular arcs of star trails. In its third decade of continuous human presence, the space station has a far-reaching impact as a microgravity lab […]"}, {"title": "Advancing Single-Photon Sensing Image Sensors to Enable the Search for Life Beyond Earth", "url": "https://science.nasa.gov/directorates/stmd/advancing-single-photon-sensing-image-sensors-to-enable-the-search-for-life-beyond-earth/", "source": "NASA", "date": "2025-09-02", "summary": "Advancing Single-Photon Sensing Image Sensors to Enable the Search for Life Beyond Earth A NASA-sponsored team is advancing single-photon sensing Complementary Metal-Oxide-Semiconductor (CMOS) detector technology that will enable future NASA astrophysics space missions to search for life on other planets. As part of their detector maturation program, the team is characterizing sensors before, during, and […]"}, {"title": "Tech From NASA’s Hurricane-hunting TROPICS Flies on Commercial Satellites", "url": "https://www.nasa.gov/earth/tech-from-nasas-hurricane-hunting-tropics-flies-on-commercial-satellites/", "source": "NASA", "date": "2025-09-02", "summary": "NASA science and American industry have worked hand-in-hand for more than 60 years, transforming novel technologies created with NASA research into commercial products like cochlear implants, memory-foam mattresses, and more. Now, a NASA-funded device for probing the interior of storm systems has been made a key component of commercial weather satellites. The novel atmospheric sounder […]"}]}};
  function esc(s){return (s||"").replace(/[&<>"]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'})[c]||c);}
  function titleMap(k){return ({aviation:"Aviation",space:"Space",pharma:"Pharma & MedTech",automotive:"Automotive / EV / Clean energy",crossIndustry:"Cross‑industry"})[k]||k;}
  function render(id) {
    const root = document.getElementById(id||"regwatch-root"); if(!root) return;
    const wrap = document.createElement("div"); wrap.className="regwatch";
    const h1 = document.createElement("h1"); h1.textContent="Daily Regulatory Brief"; wrap.appendChild(h1);
    const meta = document.createElement("div"); meta.style.opacity=".7"; meta.style.margin="0 0 1rem";
    meta.textContent="Updated " + new Date(DATA.lastUpdated).toUTCString(); wrap.appendChild(meta);
    const order = ["crossIndustry","automotive","pharma","aviation","space"];
    for(const k of order){
      const arr = (DATA.sections||{})[k]; if(!arr||!arr.length) continue;
      const h2=document.createElement("h2"); h2.textContent=titleMap(k); wrap.appendChild(h2);
      const ul=document.createElement("ul"); ul.style.margin=".2rem 0 1rem 1.2rem";
      for(const it of arr){
        const li=document.createElement("li"); li.style.margin=".4rem 0"; li.style.lineHeight="1.3";
        li.innerHTML = "<strong>"+esc(it.title)+"</strong> — "+esc(it.date)+" — "+esc(it.source)+"<br><a href='"+esc(it.url)+"' target='_blank' rel='noopener'>"+esc(it.url)+"</a>";
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