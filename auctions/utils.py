from django.core.paginator import Paginator
from django.db.models import Q

from auctions.models import Bid
import pickle
import shelve


def last_bid_amount():  # это для всех то есть неправильно.
    last_bid_amount = Bid.objects.order_by('-id').first()
    return last_bid_amount


def load_winners_from_file():
    print('load_winners_from_file')
    try:
        with open('data.pickle', 'rb') as file:
            data_new = pickle.load(file)  # загружаем объект из файла
            print(f'data_new - {data_new}')
        return data_new
    except (EOFError, FileNotFoundError):
        return {}


def save_winners_to_file(winners):
    my_data = load_winners_from_file()
    print(f'my_data - {my_data}')
    my_data.update(winners)
    print(f'save_winners_to_file() - {winners}')
    print(f'update my data - {my_data}')
    with open('data.pickle', 'wb') as file:
        pickle.dump(my_data, file)  # записываем


def get_paginator_and_page(request, ):
    auctions = Auction.objects.filter(Q(pk__in=watchlist) & Q(is_active=True)).order_by(
        'pk')  # возможно можно сделать все одной строкой
    paginator = Paginator(auctions, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)



