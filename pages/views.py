from math import atan2, cos, radians, sin, sqrt

from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from .models import HistoricSite
from .serializers import HistoricSiteSerializer


def home(request):
    context = {'subtitle': '<h2>Know Your Surroundings</h2>'}
    return render(request, 'home.html', context)


def haversine_miles(lat1, lon1, lat2, lon2):
    earth_radius_miles = 3958.8
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return earth_radius_miles * c


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def api_root(request):
    return Response({
        'name': 'BeenThere API',
        'version': 'phase-1',
        'endpoints': {
            'sites': '/api/sites/',
            'site_detail': '/api/sites/<id>/',
            'nearby': '/api/sites/nearby/?lat=<lat>&lng=<lng>&radius=<miles>',
        },
    })


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def site_list(request):
    sites = HistoricSite.objects.all()
    category = request.query_params.get('category')
    state = request.query_params.get('state')

    if category:
        sites = sites.filter(category=category)
    if state:
        sites = sites.filter(state__iexact=state)

    serializer = HistoricSiteSerializer(sites, many=True)
    return Response({
        'count': sites.count(),
        'results': serializer.data,
    })


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def site_detail(request, site_id):
    site = get_object_or_404(HistoricSite, pk=site_id)
    serializer = HistoricSiteSerializer(site)
    return Response(serializer.data)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def nearby_sites(request):
    lat = request.query_params.get('lat')
    lng = request.query_params.get('lng')
    radius = request.query_params.get('radius', '10')
    category = request.query_params.get('category')

    if lat is None or lng is None:
        return Response(
            {'error': 'lat and lng query parameters are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        lat = float(lat)
        lng = float(lng)
        radius = float(radius)
    except ValueError:
        return Response(
            {'error': 'lat, lng, and radius must be numeric values'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    sites = HistoricSite.objects.all()
    if category:
        sites = sites.filter(category=category)

    results = []
    for site in sites:
        distance = haversine_miles(lat, lng, float(site.latitude), float(site.longitude))
        if distance <= radius:
            site.distance_miles = round(distance, 2)
            results.append((distance, site))

    results.sort(key=lambda item: item[0])
    ordered_sites = [site for _, site in results]
    serializer = HistoricSiteSerializer(ordered_sites, many=True)

    return Response({
        'count': len(ordered_sites),
        'results': serializer.data,
    })
