document.addEventListener('DOMContentLoaded',()=>{
 const element=document.getElementById('requests-map');if(!element)return;
 const status=document.getElementById('request-map-status');let map,loading;
 async function load(){
  if(loading)return loading;
  loading=(async()=>{
   try{
    const response=await fetch(element.dataset.endpoint+window.location.search);
    if(!response.ok)throw Error('Could not load requests.');
    const data=await response.json();const points=data.points;
    const radius=data.mode==='matching'&&data.my_location ? {radiusCenter:data.my_location,radiusKm:data.radius_km} : {};
    map=await window.BloodSeekrMaps.create(element,{center:data.my_location||undefined,...radius,onWarning:t=>status.textContent=t});
    if(map){points.forEach(p=>map.add(p));map.fit(points);map.resize();}
    status.textContent=points.length?`${points.length} request pin(s)${data.unmapped_count ? ` · ${data.unmapped_count} older request(s) need a saved pin` : ''}.`:`No mapped requests in this view${data.unmapped_count ? `; ${data.unmapped_count} older request(s) need a saved pin` : ''}.`;
    if(radius.radiusKm)status.textContent+=` Your matching radius is ${radius.radiusKm} km.`;
    element.dataset.loaded='true';element.dataset.pinCount=points.length;
   }catch(error){status.textContent='Request pins could not load. The request list is still available.';loading=null;}
  })();return loading;
 }
 document.querySelectorAll('[data-request-view]').forEach(button=>button.addEventListener('click',()=>{
  const mode=button.dataset.requestView;
  document.querySelectorAll('[data-request-view]').forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button));});
  document.getElementById('request-results').hidden=mode==='map';
  document.getElementById('map-panel').hidden=mode==='list';
  if(mode==='map'){if(map)requestAnimationFrame(()=>map.resize());else load();}
 }));
});
