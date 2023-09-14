from decimal import Decimal

from django.contrib import messages
from django.contrib.admin import models
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, EmailMessage, send_mass_mail, BadHeaderError
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Max, Q
from django.db.models.functions import Lower
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
import pickle

# from mixin import mixin_watchlist
from .forms import AuctionForm, BidForm, CommentForm, SearchForm
from .models import User, Auction, Bid, Comment, WatchListStorage, Category
from django.utils import timezone

# def index(request):
#     return render(request, "auctions/index.html")
# from .utils import save_winners_to_file, load_winners_from_file
from .utils import save_winners_to_file, load_winners_from_file


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('auction_list'))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('auction_list'))


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
        return HttpResponseRedirect(reverse('auction_list'))
    else:
        return render(request, "auctions/register.html")


class AuctionListView(ListView):
    paginate_by = 5
    model = Auction
    template_name = 'auctions/index.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        form = SearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # queryset = queryset.filter(Q(product_name__icontains=query) & Q(is_active=True))
            queryset = queryset.annotate(similarity=TrigramSimilarity('product_name', query),
                                                ).filter(Q(similarity__gt=0.1) & Q(is_active=True)).order_by('-similarity')
            return queryset
        queryset = queryset.filter(is_active=True)
        # queryset = queryset.filter(is_active=True).order_by('-is_closed')
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        return context


class AuctionDetailView(DetailView):
    model = Auction
    template_name = 'auctions/auctions_detail.html'
    # context_object_name = 'auction'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return super().get_queryset().select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_auction = self.object
        bid_amount = Bid.objects.filter(auction=current_auction).aggregate(Max('bid_amount'))
        print(f'bid_amou - {bid_amount}')
        context['bid_form'] = BidForm(initial={'bid_amount': bid_amount['bid_amount__max']})
        context['comment_form'] = CommentForm()
        context['comments'] = Comment.objects.filter(auction=current_auction).select_related('commenter')

        if current_auction.winner:
            context['success_message'] = f'User {current_auction.winner} ' \
                                         f'have won this auction for {bid_amount["bid_amount__max"]}!'

        return context


@login_required
def create_auction(request):
    if request.method == 'POST':
        auction_form = AuctionForm(request.POST, request.FILES)
        bid_form = BidForm(request.POST)
        if auction_form.is_valid() and bid_form.is_valid():
            auction = auction_form.save(commit=False)
            bid = bid_form.save(commit=False)
            auction.bid = bid
            auction.author = request.user
            bid.bidder = request.user
            category_name = auction.category.lower() if auction.category else ''
            auction.category = category_name
            bid.save()
            auction.save()
            if category_name:  # Чтобы нельзя было создать аукцион  с пустой категорией
                category_object, created = Category.objects.get_or_create(name=category_name)  # чтобы создать обьект мне нужно auction=auction
                category_object.auction.add(auction)
            return redirect('auction_list')
    else:
        auction_form = AuctionForm()
        bid_form = BidForm()
    return render(request, 'auctions/create_auction.html', {'auction_form': auction_form, 'bid_form': bid_form})


winners = dict()


@login_required
def close_auction(request, slug):
    auction = get_object_or_404(Auction, slug=slug)
    auction.is_closed = True
    winner = auction.bid.bidder
    auction.winner = winner
    auction.save()

    subject = f'Auction {auction}'
    message = f'Congratulations, you have won the auction {auction}!!!'  # надо еще указать за сколько денег
    from_email = 'geleyroman941@gmail.com'
    recipient_list = [winner.email]
    # print(f'recipient_list - {subject, message, from_email, recipient_list}')
    print(f'winner - {winner.email}')
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    except BadHeaderError:
        return HttpResponse('Incorrect email titles.')
    except Exception as e:
        # Общая обработка других исключений, если возникнет ошибка, которую не удалось предвидеть
        print(str(e))
        return HttpResponse('There was an error when sending an email to the winner ')
    return HttpResponse('The email was successfully sent to the winner.')
    # redirect_url = reverse('auction_detail', kwargs={'slug': slug})
    # return redirect(redirect_url)


# min_value = 0


@require_POST
@login_required
def make_bid(request, slug):
    # if request.method == 'POST':
    bid_form = BidForm(request.POST)
    if bid_form.is_valid():
        current_bid_amount = bid_form.cleaned_data['bid_amount']
        auction = Auction.objects.select_related('author').get(slug=slug)
        max_bid_amount = Bid.objects.filter(auction=auction).aggregate(Max('bid_amount'))  # максимальная сумма ставки для данного аукциона
        context = {'bid_form': BidForm(initial={'bid_amount': current_bid_amount}),
                   'comment_form': CommentForm(),
                   'comments': Comment.objects.filter(auction=auction).select_related('commenter'),
                   'auction': auction}
        if max_bid_amount['bid_amount__max']: # если максимальная сумма ставки None то нам нужно избежать сравнения
            if max_bid_amount['bid_amount__max'] >= current_bid_amount:
                context['error_message'] = 'The bid should be greater than last one.'
                return render(request, 'auctions/auctions_detail.html', context)
        bid = bid_form.save(commit=False)
        bid.bidder = request.user
        bid.auction = auction
        bid.save()
        auction.bid = bid
        auction.save()
        return render(request, 'auctions/auctions_detail.html', context)
    # else:
    #     redirect_url = reverse('auction_detail', kwargs={'slug': slug})
    #     return redirect(redirect_url)


def get_paginator_and_page_and_auctions(request, watchlist):
    auctions = Auction.objects.filter(Q(pk__in=watchlist) & Q(is_active=True))
    paginator = Paginator(auctions, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(paginator, page_obj)
    return page_obj, paginator


@require_POST
@login_required
def add_watchlist(request, slug):
    watchlist_pk = WatchListStorage.objects.filter(user=request.user).values_list('auction__pk', flat=True)
    # if request.method == 'POST':
    auction = get_object_or_404(Auction, slug=slug)
    if auction.pk not in watchlist_pk:
        watchlist, created = WatchListStorage.objects.get_or_create(user=request.user)
        watchlist.auction.add(auction)
    page_obj, paginator = get_paginator_and_page_and_auctions(request, watchlist_pk)
    return render(request, 'auctions/watchlist.html',
                      {'page_obj': page_obj, 'paginator': paginator})


@login_required
def auction_watchlist(request):
    watchlist = WatchListStorage.objects.filter(user=request.user).values_list('auction__pk', flat=True)
    page_obj, paginator = get_paginator_and_page_and_auctions(request, watchlist)
    return render(request, 'auctions/watchlist.html', {'page_obj': page_obj, 'paginator': paginator})


@require_POST
@login_required
def delete_watchlist(request, slug):
    watchlist_pk = WatchListStorage.objects.filter(user=request.user).values_list('auction__pk', flat=True)
    # if request.method == 'POST':
    auction = get_object_or_404(Auction, slug=slug)
    if auction.pk in watchlist_pk:
        watchlist = get_object_or_404(WatchListStorage, user=request.user)
        watchlist.auction.remove(auction)
    page_obj, paginator = get_paginator_and_page_and_auctions(request, watchlist_pk)
    return render(request, 'auctions/watchlist.html', {'page_obj': page_obj, 'paginator': paginator})


@login_required
def add_comment(request, slug):
    if request.method == 'POST':
        auction = get_object_or_404(Auction, slug=slug)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.commenter = request.user
            comment.auction = auction
            comment.save()
            redirect_url = reverse('auction_detail', kwargs={'slug': slug})
            return redirect(redirect_url)
    else:
        comment_form = CommentForm()
    return render(request, 'auctions/auctions_detail.html', {'comment_form': comment_form})


def categories(request):
    current_categories = Category.objects.all()
    return render(request, 'auctions/categories.html', {'current_categories': current_categories})


def detail_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    auctions = Auction.objects.filter(Q(category=category) & Q(is_active=True))\
        .only('product_name', 'slug', 'image_url', 'category', 'is_active')
    return render(request, 'auctions/categories_list.html', {'auction_list': auctions})
