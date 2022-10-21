from datetime import datetime
from distutils.command.upload import upload
from email.headerregistry import Address
from email.policy import default
from tkinter import CASCADE
from unicodedata import category
from unittest.util import _MAX_LENGTH
from django.db import models
from django.forms import CharField
import datetime
current_date = datetime.date.today()
# Create your models here.
trust_choices = (
    ('trusted','Trusted'),
    ('not_trusted','Not Trusted'),
    )

available_status_choices = (
        ('availabe','Available'),
    ('not_available','Not Available'),
)
state_choices = (
    ('kerala','KERALA'),
    ('tamil_nadu','TAMIL NADU'),
    ('karnadaka','KARNADAKA'),
)
# this are the models that are accessable by both user and admin

class Users(models.Model):
    
    full_name = models.CharField(max_length = 50 ,)
    email = models.CharField(max_length = 50 ,default = 'buddy')
    password = models.CharField(max_length = 50)
    contact_number = models.CharField(max_length = 50)
    signup_day = models.CharField(max_length = 50,default=current_date.day)
    signup_month = models.CharField(max_length = 50,default=current_date.month)
    signup_year = models.CharField(max_length = 50,default=current_date.year)
    active_status = models.CharField(max_length = 50,default='active')
    is_admin = models.CharField(max_length = 50,default='false')
    profile_image = models.ImageField(upload_to = 'profile_image/')
    reference_id = models.CharField(max_length  =100,default = '0000000000')

class Address(models.Model):
    email = models.CharField(max_length = 50 ,default = 'buddy')
    first_name = models.CharField(max_length =100)
    last_name = models.CharField(max_length =100)
    building_name = models.CharField(max_length =100)
    street = models.CharField(max_length =100)
    city = models.CharField(max_length =100)
    state = models.CharField(
        max_length=20,
        choices=state_choices,
        default='kerala',
    )
    # country = models.CharField(max_length =100)
    pincode = models.CharField(max_length =100)
    contact = models.CharField(max_length =100)
    alt_contact = models.CharField(max_length =100)

# only one single banner is allowed, to change the banner you need to edit the existing banner
class Banners(models.Model):

    heading = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    image = models.ImageField(upload_to = 'banner_images/')

class Category(models.Model):

    name = models.CharField(max_length=100)
    offer_percentage = models.CharField(max_length=100,default = 0)
    image = models.ImageField(upload_to = 'Category_images/')


class Subcategory(models.Model):

    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)

class Products(models.Model):
    
    name = models.CharField(max_length = 100 )
    description = models.CharField(max_length = 200 )
    image_1 = models.ImageField(upload_to='image_2_of_products')
    image_2 = models.ImageField(upload_to ='image_2_of_products')
    image_3 = models.ImageField(upload_to ='image_3_of_products')
    image_4 = models.ImageField(upload_to ='image_4_of_products')
    arrival_date = models.CharField(max_length  = 100)
    end_date = models.CharField(max_length  = 100 )
    price = models.IntegerField(default = 0)
    # category = models.ForeignKey(Category,on_delete = models.CASCADE)
    category = models.CharField(max_length=100)
    specification = models.CharField(max_length = 300)
    stock_available = models.IntegerField()
    rating = models.IntegerField()
    total_sold = models.IntegerField()
    is_trusted = models.CharField(
        max_length=20,
        choices=trust_choices,
        default='trusted',
    )
    available_status = models.CharField(
        max_length=20,
        choices=available_status_choices,
        default='available',
    )
    offer_percentage = models.CharField(max_length= 100,default=0)

class Orders(models.Model):

    # please note that you can only create an order with the fields product,user
    product  = models.ForeignKey(Products,on_delete = models.CASCADE)
    user = models.ForeignKey(Users,on_delete = models.CASCADE)
    Order_day  = models.CharField(max_length = 100,default = current_date.day)
    Order_month  = models.CharField(max_length = 100,default = current_date.month)
    Order_year  = models.CharField(max_length = 100,default = current_date.year)
    quantity = models.IntegerField(default=0)
    status = models.CharField(max_length = 100,default='ordered')
    Address = models.CharField(max_length=20,default=1)
    payment_method = models.CharField(max_length=20,default='cod')
    total_price = models.IntegerField(default=0)
    

class Cart(models.Model):

    product  = models.ForeignKey(Products,on_delete = models.CASCADE)
    user = models.ForeignKey(Users,on_delete = models.CASCADE)
    quantity = models.IntegerField(default = 0)
    total_price = models.CharField(default=0,max_length = 300)
    
    # lets crop
class Image(models.Model):
    file = models.ImageField(upload_to='cropped_images/')
    uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pk)


class Coupon(models.Model):

    coupon = models.CharField(max_length = 100 ,default = 'amal')
    discount_percentage = models.IntegerField(default = 0)

class Coupon_history(models.Model):
    user_id = models.CharField(max_length = 100)
    coupon_code = models.CharField(max_length = 100)

class Return_request(models.Model):
    user = models.ForeignKey(Users,on_delete = models.CASCADE)
    reason = models.CharField(max_length = 500)

class References(models.Model):
    user_id = models.CharField(max_length = 100)
    refered_user_id = models.CharField(max_length = 100)
