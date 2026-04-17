from django.urls import path


from .views import (
    api_root,
    current_user,
    filter_options,
    home,
    import_run_list,
    login_user,
    logout_user,
    nearby_sites,
    register_user,
    site_browser,
    site_detail,
    site_list,
    source_feed_list,
    visit_site,
    visit_summary,
)


urlpatterns= [
    path('', home, name='home'),
    path('sites/', site_browser, name='site-browser'),
    path('api/', api_root, name='api-root'),
    path('api/auth/register/', register_user, name='register-user'),
    path('api/auth/login/', login_user, name='login-user'),
    path('api/auth/logout/', logout_user, name='logout-user'),
    path('api/auth/me/', current_user, name='current-user'),
    path('api/sites/', site_list, name='site-list'),
    path('api/sites/nearby/', nearby_sites, name='site-nearby'),
    path('api/sites/<int:site_id>/', site_detail, name='site-detail'),
    path('api/sites/<int:site_id>/visit/', visit_site, name='visit-site'),
    path('api/visits/summary/', visit_summary, name='visit-summary'),
    path('api/filter-options/', filter_options, name='filter-options'),
    path('api/sources/', source_feed_list, name='source-feed-list'),
    path('api/import-runs/', import_run_list, name='import-run-list'),
]
