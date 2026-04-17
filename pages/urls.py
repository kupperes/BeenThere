from django.urls import path


from .views import api_root, home, nearby_sites, site_detail, site_list


urlpatterns= [
    path('', home, name='home'),
    path('api/', api_root, name='api-root'),
    path('api/sites/', site_list, name='site-list'),
    path('api/sites/nearby/', nearby_sites, name='site-nearby'),
    path('api/sites/<int:site_id>/', site_detail, name='site-detail'),
]
