document.addEventListener('DOMContentLoaded',()=>{
 const select=document.getElementById('id_facility');const source=document.getElementById('facility-options');if(!select || !source)return;
 const options=JSON.parse(source.textContent);const preview=document.getElementById('facility-preview');const use=document.getElementById('use-facility-location');
 function render(){const item=options.find(x=>String(x.id)===select.value);preview.replaceChildren();if(!item){preview.hidden=true;use.hidden=true;delete use.dataset.value;return;}preview.hidden=false;
  const title=document.createElement('strong');title.textContent=item.name;preview.append(title);
  const detail=document.createElement('p');detail.textContent=`${item.address} · ${item.verified?'Verified':'Unverified'} facility`;preview.append(detail);
  const link=document.createElement('a');link.href=item.detail_url;link.target='_blank';link.rel='noopener';link.textContent='View facility details';preview.append(link);
  use.hidden=false;use.dataset.value=item.location_value;
 }
 async function apply(){const picker=document.querySelector('.location-picker');if(!picker?._locationPicker){document.getElementById('facility-location-feedback').textContent='The location picker is loading. Try again in a moment.';return;}if(picker?._locationPicker){await picker._locationPicker.setLocation(use.dataset.value);document.getElementById('facility-location-feedback').textContent='Facility collection location selected. Confirm the map point before saving.';}}
 select.addEventListener('change',render);use.addEventListener('click',apply);render();
});
