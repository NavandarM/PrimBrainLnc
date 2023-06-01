from django.urls import path
from . import views

app_name='Application'

urlpatterns=[
    path('home/', views.IndexView.as_view(), name="home"),
    path('search/', views.search, name="search"),
    path('downloads/', views.downloads, name="downloads"),
    path('contact/', views.contact, name="contact"),
    path('statistics/', views.statistics, name="statistics"),
    path('userArea/', views.userArea, name="user-area"),
    path('Explore/', views.Explore, name="explore-db"),
    path('faqs/', views.faqs, name="faqs"),
    path('results_from_ids/<str:lncIDs>/<str:OrgS>', views.Results_from_ids, name="results-from-ids")
    ]