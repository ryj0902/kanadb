from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
]

urlpatterns += i18n_patterns(
    path("", RedirectView.as_view(pattern_name="card:index"), name="home"),
    path("card/", include("card.urls")),
    path("deck/", include("deck.urls")),
    path("guide/", include("guide.urls")),
    path("npc/", include("npc.urls")),
)
