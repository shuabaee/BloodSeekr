/* Shared map adapter. Google Maps when configured; Leaflet/OSM otherwise. */
(() => {
  let googlePromise;
  const config = () => {
    const el = document.getElementById('maps-config');
    return el ? JSON.parse(el.textContent) : {};
  };
  const point = value => Array.isArray(value) && value.length === 2 && value.every(Number.isFinite);
  function loadGoogle(key) {
    if (googlePromise) return googlePromise;
    googlePromise = new Promise((resolve, reject) => {
      let timer;
      window.bloodSeekrGoogleReady = () => { clearTimeout(timer); resolve(window.google); };
      window.gm_authFailure = () => { clearTimeout(timer); reject(new Error('Google Maps authorization failed.')); window.dispatchEvent(new Event('bloodseekr-google-error')); };
      const script = document.createElement('script');
      const params = new URLSearchParams({key, callback:'bloodSeekrGoogleReady', loading:'async', v:'weekly', libraries:'maps,marker'});
      script.src = 'https://maps.googleapis.com/maps/api/js?' + params;
      script.async = true;
      script.onerror = () => {clearTimeout(timer);reject(new Error('Google Maps could not load.'));};
      timer = setTimeout(() => reject(new Error('Google Maps timed out.')), 15000);
      document.head.append(script);
    });
    return googlePromise;
  }
  function iconNode(data) {
    const node = document.createElement('div');
    node.className = 'blood-map-pin ' + (data.type === 'facility' ? 'facility' : (['urgent','emergency'].includes(data.urgency) ? data.urgency : ''));
    const span = document.createElement('span'); span.textContent = data.blood_type || (data.type === 'facility' ? '+' : '•'); node.append(span);
    return node;
  }
  function popup(data) {
    const node = document.createElement('div'); node.className='map-popup';
    const title=document.createElement('strong');title.textContent=data.title || 'Collection point';node.append(title);
    for (const value of [data.subtitle, data.units ? `${data.units} unit(s) · Needed ${data.needed_date}` : '', data.approximate ? 'Approximate city center' : '', data.distance_km != null ? `${data.distance_km} km straight-line distance` : '']) {
      if (!value) continue;const p=document.createElement('p');p.textContent=value;node.append(p);
    }
    if (data.url && data.url.startsWith('/')) {const a=document.createElement('a');a.href=data.url;a.textContent='View request →';node.append(a);}
    else if (data.id) {const p=document.createElement('p');p.textContent='Complete your donor profile to respond to matching requests.';node.append(p);}
    return node;
  }
  async function create(element, opts={}) {
    const center=point(opts.center) ? opts.center : [10.3157,123.8854];
    const key=opts.googleKey ?? config().google_key;
    if (key) {
      try {
        const g=await loadGoogle(key);
        const [{Map,InfoWindow},{AdvancedMarkerElement}]=await Promise.all([g.maps.importLibrary('maps'),g.maps.importLibrary('marker')]);
        const map=new Map(element,{center:{lat:center[0],lng:center[1]},zoom:opts.zoom || 12,mapId:opts.mapId || config().map_id || 'DEMO_MAP_ID',mapTypeControl:false,streetViewControl:false,fullscreenControl:true,gestureHandling:'cooperative'});
        const markers=[];const info=new InfoWindow();
        const radiusCircle=point(opts.radiusCenter) && opts.radiusKm ? new g.maps.Circle({map,center:{lat:opts.radiusCenter[0],lng:opts.radiusCenter[1]},radius:opts.radiusKm*1000,strokeColor:'#941d31',strokeWeight:1,fillColor:'#941d31',fillOpacity:.05}) : null;
        if(opts.onSelect) map.addListener('click',e=>opts.onSelect([e.latLng.lat(),e.latLng.lng()]));
        const api={kind:'google',raw:map,markers,pan(p,zoom=15){map.setCenter({lat:p[0],lng:p[1]});map.setZoom(zoom);},resize(){g.maps.event.trigger(map,'resize');},clear(){markers.splice(0).forEach(m=>m.map=null);},add(data,options={}) {
          const marker=new AdvancedMarkerElement({map,position:{lat:data.lat,lng:data.lng},content:iconNode(data),title:data.title || 'Location',gmpDraggable:!!options.draggable});
          marker.addListener('click',()=>{info.setContent(popup(data));info.open({map,anchor:marker});});
          if(options.onMove)marker.addListener('dragend',e=>options.onMove([e.latLng.lat(),e.latLng.lng()]));
          markers.push(marker);
          return {move(p){marker.position={lat:p[0],lng:p[1]};},remove(){marker.map=null;}};
        },fit(points){if(radiusCircle){map.fitBounds(radiusCircle.getBounds(),35);return;}if(!points.length)return; if(points.length===1){this.pan([points[0].lat,points[0].lng],14);return;} const bounds=new g.maps.LatLngBounds();points.forEach(p=>bounds.extend({lat:p.lat,lng:p.lng}));map.fitBounds(bounds,35);}};
        element._bloodseekrMap=api;return api;
      } catch(error) {element.textContent=''; if(opts.onWarning) opts.onWarning('Google Maps is unavailable; using the standard map.');}
    }
    if (!window.L) {element.textContent='Map could not load. Your location fields are still available.';return null;}
    const map=L.map(element,{scrollWheelZoom:false}).setView(center,opts.zoom || 12);
    const tiles=L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
    let warned=false;tiles.on('tileerror',()=>{if(!warned && opts.onWarning){warned=true;opts.onWarning('Map background could not load. Pins and coordinates remain available.');}});
    const group=L.layerGroup().addTo(map);
    if(opts.onSelect)map.on('click',e=>opts.onSelect([e.latlng.lat,e.latlng.lng]));
    const radiusCircle=point(opts.radiusCenter) && opts.radiusKm ? L.circle(opts.radiusCenter,{radius:opts.radiusKm*1000,color:'#941d31',weight:1,fillOpacity:.05}).addTo(map) : null;
    const api={kind:'leaflet',raw:map,pan(p,zoom=15){map.setView(p,zoom);},resize(){map.invalidateSize();},clear(){group.clearLayers();},add(data,options={}){
      const node=iconNode(data);const marker=L.marker([data.lat,data.lng],{icon:L.divIcon({className:'',html:node.outerHTML,iconSize:[42,42],iconAnchor:[21,42],popupAnchor:[0,-38]}),draggable:!!options.draggable}).addTo(group);
      marker.bindPopup(popup(data));if(options.onMove)marker.on('dragend',()=>{const p=marker.getLatLng();options.onMove([p.lat,p.lng]);});
      return {move(p){marker.setLatLng(p);},remove(){group.removeLayer(marker);}};
    },fit(points){if(radiusCircle){map.fitBounds(radiusCircle.getBounds(),{padding:[25,25],maxZoom:14});return;}if(!points.length)return;if(points.length===1){this.pan([points[0].lat,points[0].lng],14);return;}map.fitBounds(points.map(p=>[p.lat,p.lng]),{padding:[35,35],maxZoom:15});}};
    element._bloodseekrMap=api;return api;
  }
  window.BloodSeekrMaps={create,popup,config};
  document.addEventListener('DOMContentLoaded',async()=>{
    for(const element of document.querySelectorAll('[data-map-points]')){
      const source=document.getElementById(element.dataset.mapPoints);if(!source)continue;
      const points=JSON.parse(source.textContent);const map=await create(element,{center:points.length ? [points[0].lat,points[0].lng] : undefined});
      if(map){points.forEach(p=>map.add(p));map.fit(points);}
    }
  });
})();
