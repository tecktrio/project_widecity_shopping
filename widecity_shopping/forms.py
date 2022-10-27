from tkinter import Widget
from tkinter.ttk import Style
from django import forms

from widecity_shopping.models import Banners, Category, Products, Subcategory


class add_product_form(forms.ModelForm):
    class Meta:
        model = Products
        fields = [
                    'name', 
                    'description',
                    'specification',
                    'stock_available',
                    'rating',
                    'total_sold', 
                    'is_trusted', 
                    'available_status', 
                    'arrival_date',
                    'end_date',
                    'price',
                    'category', 
                ]

class add_product_images_form(forms.ModelForm):
    class Meta:
        model = Products
        fields = [ 
                    'image_1', 
                    'image_2',
                    'image_3',
                    'image_4',
                ]


class edit_banner(forms.ModelForm):
    class Meta:
        model = Banners
        fields = ['heading', 'description', 'image']


# class company_info(forms.ModelForm):
#     class Meta:
#         model = Company_Info
#         fields = ['company_logo', 'company_name', 'company_description']


class add_category(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','image']



# uiyuiyuiyghug

from django import forms
from .models import Image

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('file',)
