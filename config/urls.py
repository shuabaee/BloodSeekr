from django.contrib import admin
from django.urls import include, path
from apps.shared.views import location_options

handler403 = "apps.shared.views.permission_denied"
handler404 = "apps.shared.views.page_not_found"
handler500 = "apps.shared.views.server_error"


urlpatterns = [
    path("locations/options/", location_options, name="location_options"),
    path("admin/", admin.site.urls),
    path("login/", include("apps.login.urls")),
    path("register/", include("apps.register.urls")),
    path("profile/", include("apps.profile.urls")),
    path("settings/", include("apps.user_settings.urls")),
    path("requests/", include("apps.blood_requests.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("donations/", include("apps.donations.urls")),
    path("facilities/", include("apps.facilities.urls")),
    path("blood-guide/", include("apps.blood_data.urls")),
    path("", include("apps.home.urls")),
]
