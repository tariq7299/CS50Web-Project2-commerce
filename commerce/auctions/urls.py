from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create-listing", views.create_listing, name="create_listing"),
    path("listing_page/<int:listing_id>", views.listing_page, name="listing_page"),
    path('listing_page/watchlist', views.add_remove_to_watchlist, name='watchlist'),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.get_categories, name="get_categories"),
    path("categories/<str:category>", views.get_listing_in_a_category, name="listing_in_category"),
]
