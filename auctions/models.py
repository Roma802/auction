import random

from PIL import Image
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify


class User(AbstractUser):
    email = models.EmailField(blank=True, null=True)


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=100, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f'{self.bidder} make bid on sum {self.bid_amount}'



class Auction(models.Model):
    slug = models.SlugField(unique=True, blank=True, null=True)
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(default=False)
    image_url = models.ImageField(blank=True, null=True, upload_to='media/')
    # category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    bid = models.ForeignKey(Bid, on_delete=models.SET_NULL, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='auctions_as_winner')

    def __str__(self):
        return self.product_name

    def save(self, *args, **kwargs):
        auction_slugs = Auction.objects.values_list('slug', flat=True)
        # print(f'{auction_slugs}, slug - {slugify(self.product_name)}')
        if not self.slug and slugify(self.product_name) not in auction_slugs:
            print('OK')
            self.slug = slugify(self.product_name)
        super().save(*args, **kwargs)
        # if self.image_url:
        #     image = Image.open(self.image_url.path)
        #     if image.height > 200 or image.width > 200:
        #         max_size = (200, 200)
        #         # width, height = image.size
        #         image.thumbnail(max_size)
        #         image.save(self.image_url.path)

    def get_absolute_url(self):
        return reverse('auction_detail', kwargs={'slug': self.slug})

    class Meta:
        ordering = ['-id']


class Comment(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment of {self.commenter}'


class WatchListStorage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    auction = models.ManyToManyField(Auction)

    def __str__(self):
        return str(self.user)


class Category(models.Model):
    slug = models.SlugField(unique=True, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    auction = models.ManyToManyField(Auction, related_name='categories')  # удалится ауцкион - удалится и категория.

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
