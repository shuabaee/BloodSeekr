from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from .locations import catalog,city_index,locate_legacy,pack,unpack

class LocationWidget(forms.MultiWidget):
    template_name='shared/location_widget.html'
    def __init__(self,attrs=None):
        countries=[('', 'Select country')]+sorted([(code,d['name']) for code,d in catalog().items()],key=lambda x:x[1])
        widgets=[forms.Select(choices=countries),forms.Select(),forms.Select(),forms.TextInput(attrs={'placeholder':'Street, barangay or collection point (optional)'}),forms.NumberInput(attrs={'step':'any','min':-90,'max':90}),forms.NumberInput(attrs={'step':'any','min':-180,'max':180}),forms.HiddenInput(),forms.TextInput(attrs={'placeholder':'Type your city or municipality'})]
        super().__init__(widgets,attrs)
    def decompress(self,value):
        item=locate_legacy(value)
        country=item['country'] or ('PH' if not value else '')
        city=item['city'];custom=city[1:] if city.startswith('~') else ''
        if item['legacy'] and not city and not item['point']:
            city='__custom__';custom=item['legacy']
        point=item['point'] or ('','')
        return [country,item['province'],'__custom__' if custom else city,item['address'],*point,item['precision'],custom]
    def value_from_datadict(self,data,files,name):
        if name in data and not any(name+'_'+str(i) in data for i in range(8)):
            return data.get(name)
        return super().value_from_datadict(data,files,name)
    def get_context(self,name,value,attrs):
        values=self.decompress(value) if not isinstance(value,(list,tuple)) else value
        values=list(values or ['']*8)+['']*8
        country,province,city=values[:3]
        data=catalog().get(country,{})
        self.widgets[1].choices=[('','Select province / state')]+sorted(data.get('regions',{}).items(),key=lambda x:x[1])
        cities=[x for x in data.get('cities',[]) if not province or x['region']==province]
        self.widgets[2].choices=[('','Select city / municipality')]+[(x['id'],x['name']) for x in cities]+[('__custom__','My city is not listed')]
        context=super().get_context(name,values[:8],attrs)
        for i, subwidget in enumerate(context['widget']['subwidgets']):
            subwidget['rendered']=self.widgets[i].render(subwidget['name'],values[i],attrs=subwidget['attrs'])
        context['widget']['maps_key']=getattr(settings,'GOOGLE_MAPS_BROWSER_KEY','')
        context['widget']['map_id']=getattr(settings,'GOOGLE_MAPS_MAP_ID','DEMO_MAP_ID')
        context['widget']['catalog_url']='/locations/options/'
        return context
    def render(self,name,value,attrs=None,renderer=None):
        return mark_safe(render_to_string(self.template_name,self.get_context(name,value,attrs)))
    class Media:
        css={'all':('vendor/leaflet/leaflet.css','css/shared/location.css')}
        js=('vendor/leaflet/leaflet.js','js/shared/maps.js','js/shared/locations.js')

class LocationField(forms.MultiValueField):
    def __init__(self,*args,max_length=255,**kwargs):
        self.max_length=max_length
        fields=[forms.ChoiceField(choices=[('', '')]+[(code,d['name']) for code,d in catalog().items()],required=False),forms.CharField(required=False),forms.CharField(required=False),forms.CharField(required=False),forms.FloatField(min_value=-90,max_value=90,required=False),forms.FloatField(min_value=-180,max_value=180,required=False),forms.ChoiceField(choices=[('legacy','Legacy'),('city','City center'),('pin','Selected pin'),('gps','GPS'),('facility','Facility')],required=False),forms.CharField(max_length=100,required=False)]
        super().__init__(fields=fields,widget=LocationWidget(),require_all_fields=False,*args,**kwargs)
    def clean(self,value):
        old=getattr(self,'legacy_initial','')
        if old and not old.startswith('BS1:') and isinstance(value,(list,tuple)) and len(value)==8:
            initial=self.widget.decompress(old)
            def canonical(values):
                values=list(values)
                for i in (4,5):
                    try:values[i]=round(float(values[i]),5) if values[i] not in (None,'') else ''
                    except (TypeError,ValueError):return None
                return [str(x) if x is not None else '' for x in values]
            if canonical(value)==canonical(initial):
                return self.clean(old)
        if isinstance(value,str):
            # Preserve old form/API submissions and existing rows. Validate tagged inputs.
            if len(value)>self.max_length:raise forms.ValidationError('Location is too long.')
            if value.startswith('BS1:'):
                item=unpack(value)
                if item['legacy']:raise forms.ValidationError('Invalid location data.')
                return self.clean(self.widget.decompress(value))
            if self.required and not value.strip():raise forms.ValidationError('Select a location.')
            return value.strip()
        return super().clean(value)
    def compress(self,values):
        if not values:return ''
        country,province,city,address,lat,lng,precision,custom=values
        if not city:
            if self.required:raise forms.ValidationError('Choose a city or municipality.')
            return ''
        if not country:raise forms.ValidationError('Choose a country.')
        data=catalog()[country]
        if province and province not in data['regions']:
            raise forms.ValidationError('Choose a valid province or state.')
        if city=='__custom__':
            if not custom.strip():raise forms.ValidationError('Enter your city name.')
            city='~'+custom.strip()
        else:
            entry=city_index().get(city)
            if not entry or entry['country']!=country or (province and entry['region']!=province):
                raise forms.ValidationError('The selected city does not belong to this country/province.')
            province=entry['region']
            if lat is None and lng is None and entry.get('lat') is not None:
                lat,lng=entry['lat'],entry['lng'];precision='city'
        if (lat is None)!=(lng is None):raise forms.ValidationError('Both latitude and longitude are required for a map pin.')
        if city.startswith('~') and lat is None:raise forms.ValidationError('Choose a map point for an unlisted city.')
        if not precision or precision=='legacy':precision='pin' if lat is not None else 'legacy'
        value=pack(country,province,city,lat,lng,address.strip(),precision)
        if len(value)>self.max_length:
            raise forms.ValidationError('Shorten the street/collection-point description to fit this location.')
        return value


class LegacyLocationMixin:
    """Leave old text values intact when only other model fields are edited."""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if self.instance.pk:
            for name,field in self.fields.items():
                if isinstance(field,LocationField):
                    field.legacy_initial=getattr(self.instance,name,'') or ''
