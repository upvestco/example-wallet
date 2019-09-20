from django.urls import path

from .views import SinglePage

app_name = "core"
urlpatterns = [path("", SinglePage.as_view(), name="singlepage")]
