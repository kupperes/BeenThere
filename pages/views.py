from math import atan2, cos, radians, sin, sqrt

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from django.db.models import Count

from .models import HistoricSite, ImportRun, SourceFeed, UserVisit
from .serializers import (
    HistoricSiteSerializer,
    ImportRunSerializer,
    SourceFeedSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserVisitSerializer,
)


DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200


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


def normalize_page_params(request):
    params = getattr(request, 'query_params', request.GET)
    page = params.get('page', '1')
    page_size = params.get('page_size', str(DEFAULT_PAGE_SIZE))

    try:
        page = int(page)
        page_size = int(page_size)
    except ValueError:
        raise ValueError('page and page_size must be integers')

    if page < 1:
        raise ValueError('page must be greater than or equal to 1')
    if page_size < 1:
        raise ValueError('page_size must be greater than or equal to 1')

    return page, min(page_size, MAX_PAGE_SIZE)


def paginate_results(queryset_or_list, request, serializer_class):
    page, page_size = normalize_page_params(request)
    total_count = len(queryset_or_list) if isinstance(queryset_or_list, list) else queryset_or_list.count()
    start = (page - 1) * page_size
    end = start + page_size
    page_items = queryset_or_list[start:end]
    serializer = serializer_class(page_items, many=True, context={'request': request})

    return {
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size if total_count else 0,
        'results': serializer.data,
    }


def apply_site_filters(sites, request):
    params = getattr(request, 'query_params', request.GET)
    category = params.get('category')
    state = params.get('state')
    site_type = params.get('type')

    if category:
        sites = sites.filter(category=category)
    if state:
        sites = sites.filter(state__iexact=state)
    if site_type:
        sites = sites.filter(designation__icontains=site_type)

    return sites


def build_site_browser_context(request):
    sites = apply_site_filters(HistoricSite.objects.all(), request)
    pagination = paginate_results(sites, request, HistoricSiteSerializer)
    params = getattr(request, 'query_params', request.GET)
    page = pagination['page']
    total_pages = pagination['total_pages']

    return {
        'sites': pagination['results'],
        'count': pagination['count'],
        'page': page,
        'page_size': pagination['page_size'],
        'total_pages': total_pages,
        'selected_state': params.get('state', ''),
        'selected_type': params.get('type', ''),
        'selected_category': params.get('category', ''),
        'state_options': HistoricSite.objects.exclude(state='').values_list('state', flat=True).distinct().order_by('state'),
        'type_options': HistoricSite.objects.exclude(designation='').values_list('designation', flat=True).distinct().order_by('designation'),
        'category_options': HistoricSite.objects.exclude(category='').values_list('category', flat=True).distinct().order_by('category'),
        'has_previous': page > 1,
        'has_next': total_pages > page,
        'previous_page': page - 1,
        'next_page': page + 1,
    }


def annotate_visited_state(sites, request):
    if not request.user.is_authenticated:
        return sites

    if isinstance(sites, list):
        visited_ids = set(
            UserVisit.objects.filter(user=request.user, historic_site__in=sites).values_list('historic_site_id', flat=True)
        )
        for site in sites:
            site.visited = site.id in visited_ids
        return sites

    return sites


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
            'sources': '/api/sources/',
            'import_runs': '/api/import-runs/',
            'filter_options': '/api/filter-options/',
        },
    })


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def site_list(request):
    try:
        sites = apply_site_filters(HistoricSite.objects.all(), request)
        sites = annotate_visited_state(sites, request)
        return Response(paginate_results(sites, request, HistoricSiteSerializer))
    except ValueError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


def site_browser(request):
    try:
        context = build_site_browser_context(request)
        return render(request, 'site_browser.html', context)
    except ValueError as exc:
        return render(request, 'site_browser.html', {'error': str(exc), 'sites': []}, status=400)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def site_detail(request, site_id):
    site = get_object_or_404(HistoricSite, pk=site_id)
    if request.user.is_authenticated:
        site.visited = site.user_visits.filter(user=request.user).exists()
    serializer = HistoricSiteSerializer(site, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def source_feed_list(request):
    feeds = SourceFeed.objects.all()
    jurisdiction_level = request.query_params.get('jurisdiction_level')

    if jurisdiction_level:
        feeds = feeds.filter(jurisdiction_level=jurisdiction_level)

    try:
        return Response(paginate_results(feeds, request, SourceFeedSerializer))
    except ValueError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def import_run_list(request):
    runs = ImportRun.objects.select_related('source_feed').all()
    source_slug = request.query_params.get('source')

    if source_slug:
        runs = runs.filter(source_feed__slug=source_slug)

    try:
        return Response(paginate_results(runs, request, ImportRunSerializer))
    except ValueError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def filter_options(request):
    states = list(
        HistoricSite.objects.exclude(state='')
        .values('state')
        .annotate(count=Count('id'))
        .order_by('state')
    )
    designations = list(
        HistoricSite.objects.exclude(designation='')
        .values('designation')
        .annotate(count=Count('id'))
        .order_by('designation')
    )
    categories = list(
        HistoricSite.objects.exclude(category='')
        .values('category')
        .annotate(count=Count('id'))
        .order_by('category')
    )

    return Response({
        'states': states,
        'types': designations,
        'categories': categories,
    })


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def nearby_sites(request):
    lat = request.query_params.get('lat')
    lng = request.query_params.get('lng')
    radius = request.query_params.get('radius', '10')
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

    sites = HistoricSite.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    sites = apply_site_filters(sites, request)

    results = []
    for site in sites:
        distance = haversine_miles(lat, lng, float(site.latitude), float(site.longitude))
        if distance <= radius:
            site.distance_miles = round(distance, 2)
            results.append((distance, site))

    results.sort(key=lambda item: item[0])
    ordered_sites = [site for _, site in results]
    ordered_sites = annotate_visited_state(ordered_sites, request)
    try:
        return Response(paginate_results(ordered_sites, request, HistoricSiteSerializer))
    except ValueError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)
        return Response({'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)

    if user is None:
        return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)

    login(request, user)
    return Response({'user': UserSerializer(user).data})


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def logout_user(request):
    logout(request)
    return Response({'success': True})


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def current_user(request):
    if not request.user.is_authenticated:
        return Response({'user': None})
    return Response({'user': UserSerializer(request.user).data})


@api_view(['POST', 'DELETE'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def visit_site(request, site_id):
    site = get_object_or_404(HistoricSite, pk=site_id)

    if request.method == 'POST':
        visit, created = UserVisit.objects.get_or_create(user=request.user, historic_site=site)
        site.visited = True
        return Response(
            {
                'created': created,
                'visit': UserVisitSerializer(visit, context={'request': request}).data,
                'site': HistoricSiteSerializer(site, context={'request': request}).data,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    deleted_count, _ = UserVisit.objects.filter(user=request.user, historic_site=site).delete()
    site.visited = False
    return Response(
        {
            'deleted': deleted_count > 0,
            'site': HistoricSiteSerializer(site, context={'request': request}).data,
        }
    )


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def visit_summary(request):
    visits = UserVisit.objects.filter(user=request.user).select_related('historic_site')
    return Response(
        {
            'visit_count': visits.count(),
            'recent_visits': UserVisitSerializer(visits[:10], many=True, context={'request': request}).data,
        }
    )
