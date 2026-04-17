from math import atan2, cos, radians, sin, sqrt

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import HistoricSite


def home(request):
    context = {'subtitle': '<h2>Know Your Surroundings</h2>'}
    return render(request, 'home.html', context)


def serialize_site(site, include_distance=False, distance_miles=None):
    payload = {
        'id': site.id,
        'name': site.name,
        'summary': site.summary,
        'description': site.description,
        'latitude': float(site.latitude),
        'longitude': float(site.longitude),
        'address': site.address,
        'city': site.city,
        'state': site.state,
        'category': site.category,
        'designation': site.designation,
        'era': site.era,
        'source_name': site.source_name,
        'source_id': site.source_id,
        'wikipedia_url': site.wikipedia_url,
        'reference_url': site.reference_url,
        'image_url': site.image_url,
        'is_verified': site.is_verified,
    }
    if include_distance:
        payload['distance_miles'] = distance_miles
    return payload


def haversine_miles(lat1, lon1, lat2, lon2):
    earth_radius_miles = 3958.8
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return earth_radius_miles * c


def api_root(request):
    return JsonResponse({
        'name': 'BeenThere API',
        'version': 'phase-1',
        'endpoints': {
            'sites': '/api/sites/',
            'site_detail': '/api/sites/<id>/',
            'nearby': '/api/sites/nearby/?lat=<lat>&lng=<lng>&radius=<miles>',
        },
    })


def site_list(request):
    sites = HistoricSite.objects.all()
    category = request.GET.get('category')
    state = request.GET.get('state')

    if category:
        sites = sites.filter(category=category)
    if state:
        sites = sites.filter(state__iexact=state)

    return JsonResponse({
        'count': sites.count(),
        'results': [serialize_site(site) for site in sites],
    })


def site_detail(request, site_id):
    site = get_object_or_404(HistoricSite, pk=site_id)
    return JsonResponse(serialize_site(site))


def nearby_sites(request):
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    radius = request.GET.get('radius', '10')

    if lat is None or lng is None:
        return JsonResponse(
            {'error': 'lat and lng query parameters are required'},
            status=400,
        )

    try:
        lat = float(lat)
        lng = float(lng)
        radius = float(radius)
    except ValueError:
        return JsonResponse(
            {'error': 'lat, lng, and radius must be numeric values'},
            status=400,
        )

    results = []
    for site in HistoricSite.objects.all():
        distance = haversine_miles(lat, lng, float(site.latitude), float(site.longitude))
        if distance <= radius:
            results.append((distance, site))

    results.sort(key=lambda item: item[0])
    serialized = [
        serialize_site(site, include_distance=True, distance_miles=round(distance, 2))
        for distance, site in results
    ]

    return JsonResponse({
        'count': len(serialized),
        'results': serialized,
    })
