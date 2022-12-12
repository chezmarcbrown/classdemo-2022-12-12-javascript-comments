from django.urls import path
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("", views.ListingListView.as_view(), name="index"),
    #path("", views.index, name="index"),

    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("my_listings", views.my_listings, name="my-listings"),
    path("my_watchlist", views.my_watchlist, name="my-watchlist"),

    path("create_listing", views.ListingCreateView.as_view(), name="create-listing"),
    #path("create_listing", views.create_listing, name="create-listing"),

    path("categories", views.CategoryListView.as_view(), name="categories"),
    #path("categories", views.categories, name="categories"),

    path("category/<int:category_id>", views.CategoryListingsView.as_view(), name="category"),
    #path("category/<int:category_id>", views.category, name="category"),

    path("create_category", views.CategoryCreateView.as_view(), name="create-category"),
    path("category/delete/<int:pk>", views.CategoryDeleteView.as_view(), name="delete-category"),
    path("category/update/<int:pk>", views.CategoryUpdateView.as_view(), name="update-category"),


    path("comment/<int:listing_id>", views.add_comment, name="add-comment"),

    path("api/counters", views.api_counters, name="api-counters"),
    path("api/toggle", views.api_toggle, name="api-toggle"),
    path("api/watching", views.api_watching, name="api-watching"),
    path("api/comment/<int:listing_id>", views.api_comment, name="api-add-comment"),

]
