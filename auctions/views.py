import re
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy

from .models import User, Listing, Category, Comment
from .forms import ListingForm, BidForm, CommentForm

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            next_url = request.POST.get("next", "index")
            return redirect(next_url)
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        next_url = request.GET.get("next", "index")
        return render(request, "auctions/login.html", {"next": next_url })


def logout_view(request):
    logout(request)
    return redirect("index")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return redirect("index")
    else:
        return render(request, "auctions/register.html")


def index(request):
    return render(request, "auctions/index.html", {
        'listings': Listing.objects.all().filter(active=True).order_by('-created_at'),
        'banner': 'Active Listings'
    })

class ListingListView(ListView):
    model = Listing
    template_name = "auctions/index.html"
    context_object_name = "listings"

    def get_queryset(self):
        return Listing.objects.all().filter(active=True).order_by('-created_at')

    def get_context_data(self):
        context = super().get_context_data()
        context['banner'] = "Active Listings"
        return context


def listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    if request.method == 'POST':
        clicked = request.POST["doit"]
        if clicked == "toggle-watcher":
            listing.toggle_watcher(request.user)
            return redirect('listing', listing_id=listing.id)
        elif clicked == "bid":
            return redirect('bid', listing_id=listing.id)
            return HttpResponse("make a bid")
        elif clicked == "close-auction":
            listing.active = False
            listing.save()
            return redirect('my-listings')
        elif clicked == "add-comment":
            return redirect('add-comment', listing_id=listing_id)
        else:
            return HttpResponseServerError(f'Unknown button clicked')
    else:
        being_watched = listing.watchers.filter(id=request.user.id).exists()
        return render(request, "auctions/listing.html", {
            'listing': listing,
            'being_watched': being_watched,
        })

@login_required(login_url='login')
def my_listings(request):
    return render(request, "auctions/index.html", {
        'listings': request.user.my_listings.order_by('-created_at'),
        'banner': 'My Listings'
    })

@login_required(login_url='login')
def my_watchlist(request):
    return render(request, "auctions/index.html", {
        'listings': request.user.watched_listings.order_by('-created_at'),
        'banner': 'My Watchlist'
    })

def categories(request):
    return render(request, "auctions/categories.html", {
        'categories': Category.objects.all().order_by('name'),
    })

class CategoryListView(ListView):
   model = Category
   template_name = "auctions/categories.html"
   context_object_name = "categories"


def category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    listings = Listing.objects.filter(categories = category, active=True)
    return render(request, "auctions/index.html", {
        'listings': listings,
        'banner': f'{category.name} Listings',
    })

class CategoryListingsView(ListView):
   model = Listing
   template_name = "auctions/category_listings.html"
   context_object_name = "listings"
 
   def get_queryset(self):
       return Listing.objects.filter(categories=self.kwargs["category_id"], active=True)
 
   def get_context_data(self):
       context = super().get_context_data()
       category_id = self.kwargs["category_id"]
       category = Category.objects.get(id=category_id)
       context['category'] = category
       context['banner'] = f'{category.name} Category ({self.get_queryset().count()} listings)'
       return context

class CategoryCreateView(CreateView):
    model = Category
    fields = ('name', 'image')
    success_url = reverse_lazy('categories')

class CategoryDeleteView(DeleteView):
    model = Category
    success_url = reverse_lazy('categories')

class CategoryUpdateView(UpdateView):
   model = Category
   fields = ("name", "image")
   success_url = reverse_lazy("categories")

@login_required(login_url='login')
def create_listing(request):
    if request.method == "POST":
        if "cancel" in request.POST: 
            return redirect('index')
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.creator = request.user
            listing.save()
            form.save_m2m()
            messages.success(request, f'Listing created successfully!')
            return redirect("index")
        else:
            messages.error(request, 'Problem creating the listing. Details below.')	
    else: 
        form = ListingForm(initial={'starting_bid': 1})
    return render(request, "auctions/new_listing.html", {'form':form})

#class ListingCreateView(LoginRequiredMixin, CreateView):
class ListingCreateView(CreateView):
    model = Listing
    template_name = "auctions/new_listing.html"
    fields = ('title', 'description', 'starting_bid', 'categories', 'image')
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

@login_required(login_url='login')
# possible todo: prevent user to bid on his own listing
def bid(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    if request.method == 'POST':
        form = BidForm(request.POST)
        form.set_minimum_bid(listing.minimum_bid())
        if form.is_valid():
            bid = form.save(commit=False)
            bid.bidder = request.user
            bid.listing = listing
            bid.save()
            return redirect('listing', listing_id=listing_id)
        else:
            messages.error(request, "Problem with the bid")
    else:
        form = BidForm(initial={'amount':listing.minimum_bid})
    return render(request, "auctions/bid.html", {
            'form': form,
            'listing': listing,
        }) 

@login_required(login_url='login')
def add_comment(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    if request.method == "POST":
        if "cancel" in request.POST: 
            return redirect('listing', listing_id=listing_id)
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.commentor = request.user
            comment.listing = listing
            comment.save()
            return redirect('listing', listing_id=listing_id)
        else:
            messages.error(request, 'Problem creating the comment. Details below.')	
    else: 
        form = CommentForm()
    # return render(request, "auctions/listing.html", {
    #     'form':form, 'listing':listing, 'show_CommentForm':'yes'})
    return render(request, "auctions/new_comment.html", {
        'form':form, 'listing':listing, 'show_CommentForm':'yes'})

from django.http import JsonResponse
def api_counters(request):
    user = request.user
    counts = {'active_listings': Listing.objects.filter(active=True).count()}
    if user.is_authenticated:
        counts['my_listings'] = user.my_listings.all().count()
        counts['my_watches'] = user.watched_listings.all().count()
    print(f'api_counters called. returning {counts}')
    return JsonResponse(counts)

def api_toggle(request):
    if not request.user.is_authenticated:
        return JsonResponse({})
    listing_id = request.GET['listing_id']
    listing = Listing.objects.get(id=listing_id)
    on_watchlist = listing.watchers.filter(id=request.user.id).exists()
    if on_watchlist:
        listing.watchers.remove(request.user)
    else:
        listing.watchers.add(request.user)
    on_watchlist = not on_watchlist
    status = {
        'user': request.user.username,
        'on_watchlist': on_watchlist,
        'my_watches': request.user.watched_listings.all().count()
    }
    print(f'api_toggle called. returning {status}')
    return JsonResponse(status)

def api_watching(request):
    # should check of user is_authenticated and listing_id is valid
    if not request.user.is_authenticated:
        return JsonResponse({})
    listing_id = request.GET['listing_id']
    listing = Listing.objects.get(id=listing_id)
    status = {
        'on_watchlist': listing.watchers.filter(id=request.user.id).exists()
    }
    print(f'api_onwatchlist called. returning {status}')
    return JsonResponse(status)

import json
def api_comment(request, listing_id):
    print(f'api_comment called. id={listing_id}')
    # should check of user is_authenticated and listing_id is valid
    listing = Listing.objects.get(id=listing_id)
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        comment = Comment.objects.create(comment=body['comment'], commentor = request.user, listing = listing)
        reponse = {
            'comment': comment.comment,
            'commentor': f'{comment.commentor}',
            'created_at': comment.created_at
        }
        print(f'api_comment returning: {reponse}')
        return JsonResponse(reponse)
    return JsonResponse({'api_comment error':'something went wrong'})
