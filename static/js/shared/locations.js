(() => {
  const cache=new Map();
  async function load(url,country){const key=url+country;if(!cache.has(key))cache.set(key,fetch(url+'?country='+encodeURIComponent(country)).then(r=>{if(!r.ok)throw Error('Location list unavailable.');return r.json();}).catch(e=>{cache.delete(key);throw e;}));return cache.get(key);}
  function options(select,rows,selected,placeholder,custom=false){select.replaceChildren(new Option(placeholder,''));for(const row of rows)select.add(new Option(row.name,row.id));if(custom)select.add(new Option('My city is not listed','__custom__'));select.value=selected || '';}
  async function setup(root){
    const controls=Array.from({length:8},(_,i)=>root.querySelector(`[data-part="${i}"] input,[data-part="${i}"] select`));
    const [country,province,city,address,lat,lng,precision,custom]=controls;
    const feedback=root.querySelector('.location-feedback');let data=null,marker=null,sequence=0,map=null;
    const message=(text,error=false)=>{feedback.textContent=text;feedback.classList.toggle('error',error);};
    const coords=()=>lat.value!=='' && lng.value!=='' && Number.isFinite(Number(lat.value)) && Number.isFinite(Number(lng.value)) ? [Number(lat.value),Number(lng.value)] : null;
    function customVisibility(){root.querySelector('[data-part="7"]').classList.toggle('is-visible',city.value==='__custom__');custom.required=city.value==='__custom__';}
    function place(point,source='pin',pan=true){if(!point)return;lat.value=point[0].toFixed(5);lng.value=point[1].toFixed(5);precision.value=source;
      if(map){if(!marker)marker=map.add({lat:point[0],lng:point[1],title:'Selected location'},{draggable:true,onMove:p=>place(p,'pin',false)});else marker.move(point);if(pan)map.pan(point,source==='city'?12:16);}
      message(source==='city'?'Approximate city center selected. Move the pin for a more accurate point.':`Location pin saved at ${lat.value}, ${lng.value}.`);
    }
    function clearPin(){lat.value='';lng.value='';precision.value='legacy';if(marker){marker.remove();marker=null;}message('Choose a city to position the pin.');}
    async function refresh(keep=false){const token=++sequence;if(!country.value){data=null;if(keep){customVisibility();return;}options(province,[],'','Select province / state');options(city,[],'','Select city');return;}
      try{const value=await load(root.dataset.catalog,country.value);if(token!==sequence)return;data=value;const oldProvince=keep?province.value:'';const oldCity=keep?city.value:'';options(province,data.regions,oldProvince,'All areas / select province');options(city,data.cities.filter(x=>!province.value || x.region===province.value),oldCity,'Select city / municipality',true);customVisibility();}
      catch(e){message('Could not load localities. Refresh or keep your existing selection.',true);}
    }
    country.addEventListener('change',()=>{clearPin();custom.value='';refresh();});
    province.addEventListener('change',()=>{clearPin();options(city,(data?.cities || []).filter(x=>!province.value || x.region===province.value),'','Select city / municipality',true);customVisibility();});
    city.addEventListener('change',()=>{customVisibility();const entry=data?.cities.find(x=>x.id===city.value);if(entry){province.value=entry.region;if(entry.lat!=null)place([entry.lat,entry.lng],'city');else clearPin();}else clearPin();});
    lat.addEventListener('change',()=>{if(coords())place(coords(),'pin',false);});lng.addEventListener('change',()=>{if(coords())place(coords(),'pin',false);});
    root.querySelector('.use-location').addEventListener('click',()=>{
      if(!navigator.geolocation){message('Your browser does not support location access.',true);return;}
      message('Waiting for your location…');navigator.geolocation.getCurrentPosition(async position=>{
        const point=[position.coords.latitude,position.coords.longitude];
        if(!country.value){country.value='PH';await refresh();}
        if(!city.value && data?.cities.length){const nearest=data.cities.reduce((best,item)=>{const distance=(item.lat-point[0])**2+(item.lng-point[1])**2;return !best || distance<best.distance?{item,distance}:best;},null);if(nearest){province.value=nearest.item.region;options(city,data.cities.filter(x=>x.region===province.value),nearest.item.id,'Select city',true);}}
        place(point,'gps');customVisibility();
      },()=>message('Location access was unavailable. Choose a city and click the map instead.',true),{enableHighAccuracy:true,timeout:10000,maximumAge:60000});
    });
    await refresh(true);
    map=await window.BloodSeekrMaps.create(root.querySelector('.picker-map'),{center:coords() || undefined,zoom:coords()?14:7,googleKey:root.dataset.googleKey,mapId:root.dataset.mapId,onSelect:p=>place(p,'pin',false),onWarning:t=>message(t,true)});
    if(coords())place(coords(),precision.value || 'pin',false);
    root._locationPicker={async setLocation(value){
      if(value.startsWith('BS1:')){const row=JSON.parse(value.slice(4));country.value=row[0];province.value=row[1];city.value=row[2];address.value=row[5] || '';custom.value=row[2].startsWith('~')?row[2].slice(1):'';await refresh(true);province.value=row[1];options(city,data.cities.filter(x=>!province.value || x.region===province.value),custom.value?'__custom__':row[2],'Select city',true);place([row[3],row[4]],'facility');}
      else{const match=(data?.cities || []).find(x=>x.name.toLowerCase()===value.toLowerCase());if(match){province.value=match.region;options(city,data.cities.filter(x=>x.region===match.region),match.id,'Select city',true);place([match.lat,match.lng],'city');}}
      customVisibility();
    },get map(){return map;}};
    root.dispatchEvent(new Event('location-ready'));
  }
  document.addEventListener('DOMContentLoaded',()=>document.querySelectorAll('.location-picker').forEach(root=>setup(root).catch(()=>{root.querySelector('.location-feedback').textContent='Map unavailable. Select a locality or enter coordinates to continue.';})));
})();
