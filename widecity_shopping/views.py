# here we write the views file
# importing the neccessary packages and modules
import csv
import time
from tkinter.tix import STATUS
from unittest import result
from django.http import JsonResponse
from .forms import ImageForm, add_product_images_form
from django.shortcuts import render
from django.http import HttpResponse
from asyncio.windows_events import NULL
import email
from itertools import product
from math import fabs
import random

import re
from sre_constants import SUCCESS
from this import d
from unicodedata import category, name
from urllib import response
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse, FileResponse
import io
from pandas import date_range, isnull
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from django.shortcuts import redirect, render
from requests import session
from twilio.rest import Client
from widecity_shopping.forms import add_category, add_product_form, edit_banner
from widecity_shopping.models import Banners, Cart, Category, Coupon, Coupon_history, Image, Orders, Products, References, Return_request, Users, Address
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
import pdfkit
import datetime
from datetime import date, timedelta
# end of importing files

# global variables
current_date = datetime.date.today()
duration = 'Today'
otp = '0'
delivery_charge = 10
# end of global variables

# handling user side


def root(request):
    if 'user' in request.session:
        return redirect('/user_home')
    else:
        return redirect('/user_sign_in')

# controls the content in user home
# start


@never_cache
def user_home(request):
    user = ''

    # gathering neccessary data from the server
    try:
        banner1 = Banners.objects.get(id=1)  # getting the banner data
        banner2 = Banners.objects.get(id=2)  # getting the banner data
        banner3 = Banners.objects.get(id=3)  # getting the banner data
    except:
        banner1 = ''  # assigning null to the banners if there is an issue in getting the banner
        banner2 = ''  # assigning null to the banners if there is an issue in getting the banner
        banner3 = ''  # assigning null to the banners if there is an issue in getting the banner
    try:
        products = Products.objects.all()
        trusted_products = Products.objects.filter(is_trusted = 'trusted')
        best_offer_products = Products.objects.all()
        rated_products = Products.objects.filter(rating = 5)
    except:
        products = ''
    try:
        categories = Category.objects.all()
    except:
        categories = ''
    print(products)
    try:
        if 'user' in request.session:
            user_email = request.session['user']
            user = Users.objects.get(email=user_email)
        else:
            user = 'guest'
    except:
        pass

    return render(request, 'user_home.html', {
        'user': user,
         'banner1': banner1, 
         'banner2': banner2, 
         'banner3': banner3, 
         'products': products, 
         'categories': categories,
         'trusted_products':trusted_products,
         'best_offer_products':best_offer_products,
         'rated_products':rated_products,
         })
# end
#############################################################################################################################

# generating content of user_product_detials
# start


def user_product_detail(request, product_id):
    product = Products.objects.get(id=product_id)
    category = Products.objects.filter(category=product.category)
    return render(request, 'user_product_detail.html', {'product': product, 'category': category})
# end
#############################################################################################################################

# generating content of user invoice downloads
# start


def user_invoice(request):
    if 'user' in request.session:
        user = request.session['user']
    else:
        return redirect('/user_sign_in')
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 10)
    this_user = Users.objects.get(email=user)
    order_details = Orders.objects.filter(
        user=this_user.id, status='Delivered')
    lines = [
        'Sales Report of WideCity Shopping ',
        '',
        '      Date      |       brand       |                       product name                     |  sold   |   stock balance  |   revenue  ',
        '',

    ]
    for orders in order_details:
        lines.append(str(orders.Order_day) +
                     str('/'+str(orders.Order_month)) +
                     str('/'+str(orders.Order_year)) +
                     str('         '+str(orders.product.category)) +
                     str('        '+str(orders.product.name)) +
                     str('       '+str(orders.product.total_sold)) +
                     str('            '+str(orders.product.stock_available)) +
                     str('                 '+str(orders.product.price))

                     )

        lines.append(
            "-----------------------------------------------------------------------------------------------------------------------------------")
    lines.append('')
    lines.append('This report is of the duration of last 7 days')
    for line in lines:
        textob.textLine(line)
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename='widecity_invoice.pdf ')
# end
#############################################################################################################################

# generation contents of user category view
# start


def user_category_view(request, name):
    category = Category.objects.get(name=name)
    category_products = Products.objects.filter(category=category.name)
    categories = Category.objects.all()
    product_count = category_products.count()
    p = Paginator(category_products, 2)
    pages = ''
    page_obj = p.get_page(1)
    if 'page' in request.session:
        page_number = request.session['page']
        page_obj = p.get_page(page_number)
    if request.method == 'POST':
        print('its post')
        page_number = request.POST.get('page')
        try:
            page_obj = p.get_page(page_number)
            request.session['page'] = page_number
            print('page changed')  # returns the desired page object

        except:
            page_obj = p.get_page(1)
    for i in range(0,p.num_pages):
        print(i)
        pages = pages+'.'

    return render(request, 'user_category_view.html',
                  {
                      'category': category,
                      'category_products': page_obj,
                      'categories': categories,
                      'pages':pages,
                  })
# end
#############################################################################################################################

# generating content in the user add to cart
# start


def user_add_to_cart(request):
    response = 'failed'
    if 'user' in request.session:
        user = request.session['user']
    else:
        response = 'user_not_found'
        return JsonResponse({'response': response})
    if request.method == 'POST':
        product_id = int(request.POST.get('product_id'))
        user = Users.objects.get(email=user)
        user_id = int(user.id)
        product = Products.objects.get(id=product_id)
        product_offer = product.offer_percentage
        discount = int(product.price) * (int(product_offer) / 100)
        total_price = product.price - discount
        print('offer applied ', total_price)
        new_cart_product = Cart.objects.create(
            product_id=product_id,
            user_id=user_id,
            quantity=1,
            total_price=int(total_price),
        )
        new_cart_product.save()
        response = 'product_added'
        print(response)
    return JsonResponse({'response': response})
# end
#############################################################################################################################

# genereating content of user view cart
# start


@never_cache
def user_view_cart(request):
    sub_total = 0
    # trying to add the order to the cart
    if 'user' in request.session:
        user = request.session['user']
    else:
        return redirect('/user_sign_in')
    try:
        user = Users.objects.get(email=user)
    except:
        user = ''
    try:
        products = Cart.objects.filter(user=user.id)
    except:
        products = ''
    if len(products) == 0:
        return render(request, 'user_cart_empty.html')
    product_offer = 0
    for price in products:
        # price.total_price = Products.objects.get(id = price.product.id).price
        print('product with discount', price.total_price)
        sub_total = int(sub_total) + int(price.total_price)
    # total = sub_total+delivery_charge
    special_offer = product_offer
    request.session['sub_total'] = sub_total
    request.session['checkout_status'] = 'True'
    # for data in products:
    #     temp_data = model_to_dict(data)
    #     discount = int(data.product.price) * (int(data.product.offer_percentage)/100)
    #     temp_data['total'] = int(data.product.price) - discount
    #     print(temp_data)
    #     total = int(data.product.price) * (int(data.product.offer_percentage)/100)
    #     # data.insert(total)
    #     data['total']=total
    return render(request, 'user_cart_view.html', {'user': user, 'products': products, 'sub_total': sub_total, 'special_offer': special_offer, 'delivery_charge': delivery_charge})
# end
#############################################################################################################################

# generating content of user invoice per item
# start


def user_invoice_per_item(request, id):
    if 'user' in request.session:
        user = request.session['user']
    else:
        return redirect('/user_sign_in')
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 10)
    this_user = Users.objects.get(email=user)
    order_details = Orders.objects.get(id=id)
    lines = [
        'INVOICE ',
        '',
        '',
        '',
        'Customer Name : {username}'.format(username=this_user.full_name),
        '',
        'Contact : {contact}'.format(contact=this_user.contact_number),
        '',
        '----------------------------------------------------------------------------------------------------------------------------------------------',
        '',
        'Product Name: {product_name}'.format(
            product_name=order_details.product.name),
        '',
        'Order Status : {order_status}'.format(
            order_status=order_details.status),
        '',
        '',
        '',
        'Provided Discount : {discount} %'.format(
            discount=int(order_details.product.offer_percentage)),
        '',
        'Total Price : Rs {product_price}'.format(
            product_price=order_details.total_price),
        '',
    ]
    lines.append('')
    lines.append('Thank you for visiting widecity shopping.')
    for line in lines:
        textob.textLine(line)
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)
    print(buf)
    return FileResponse(buf, as_attachment=True, filename='widecity_invoice.pdf ')
# end
#############################################################################################################################


def search_engine(request):
    keyword = request.GET.get('keyword')

    available_product = Products.objects.all()
    result = []
    for product in available_product:
        keyword = str(str(keyword).upper())
        all_products = str(str(product.name).upper())
        if keyword in all_products:
            print('found in product')
            search_result = Products.objects.get(id=product.id)
            result.append(search_result)

    return render(request, 'user_search_results.html',
                  {
                      'category_products': result
                  })
# generation content of user export my orders in csv
# start


def user_export_myorders_in_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    if 'user' in request.session:
        user = request.session['user']
    else:
        return redirect('/user_sign_in')
    this_user = Users.objects.get(email=user)
    # output filename handling
    filename = str(this_user.full_name)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(
        filename)
    writer = csv.writer(response)
    ordered_products = Orders.objects.filter(user=this_user.id)
    for product in ordered_products:
        print(product.product.name)
        print(product.Order_day, product.Order_month, product.Order_year)
        print(product.quantity)
        print(product.total_price)
        row = [product.product.name, product.Order_day, product.Order_month,
               product.Order_year, product.quantity, product.total_price]
        writer.writerow(row)
    return response
# end
#############################################################################################################################

# generation the contents of the user update cart
# start


def user_update_cart(request):
    if 'user' in request.session:
        user = request.session['user']
    else:
        return redirect('/user_sign_in')
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        cart_id = request.POST.get('cart_id')
        task = request.POST.get('task')
        print(task)
        user = Users.objects.get(email=user)
        product = Cart.objects.get(id=cart_id)
        stock = Products.objects.get(id=product.product.id)
        discount = int(stock.price) * (int(stock.offer_percentage)/100)
        orginal_price_with_discount = stock.price - discount
        stock_balance = stock.stock_available
        print('got quantity', quantity)
        if task == 'plus':
            updated_quantity = int(quantity) + 1
            if stock_balance > 1:
                product.quantity = updated_quantity
                print('updated quantity', updated_quantity)
                # stock manage
                stock.stock_available = stock.stock_available - 1
            else:
                updated_quantity = quantity
        else:
            updated_quantity = int(quantity) - 1
            if updated_quantity >= 1:
                product.quantity = updated_quantity
                print('updated quantity', updated_quantity)
                # stock manage
                stock.stock_available = stock.stock_available + 1
            else:
                updated_quantity = quantity
        print('orginal_price_with_discount', orginal_price_with_discount)
        total_prize = int(int(orginal_price_with_discount)
                          * int(updated_quantity))
        product.total_price = int(total_prize)
        stock.save()
        print('stock balance ', stock.stock_available)
        product.save()
        all_cart_products = Cart.objects.filter(user=user.id)
        sub_total = 0
        for product in all_cart_products:
            sub_total = int(sub_total) + int(product.total_price)
        # print(sub_total)
        request.session['sub_total'] = sub_total
        print('saved the changes in database')
        return JsonResponse({
            'updated_quantity': updated_quantity,
            'stock_available': stock.stock_available,
            'total_price': product.total_price,
            'sub_total': int(sub_total),
            'delivery_charge': delivery_charge,
        })
    return JsonResponse({'user': 'user_info'})
# end
#############################################################################################################################

# ganerating the contents of the user delete cart item
# start


def user_delete_cart_item(request):
    if request.method == 'POST':
        cart_id = request.POST.get('id')
        delete_product = Cart.objects.get(id=cart_id).delete()
        print('one item from the cart is deleted')
        return JsonResponse({'deleted': 'deleted'})
# end
#############################################################################################################################

# generating the contents of the user check cart or shop
# start


def user_check_cart_or_shop(request):
    return render(request, 'user_check_cart_or_shop.html')
# end
#############################################################################################################################

# generating the contents of the user checkout
# start


def user_checkout(request):
    if 'user' in request.session:
        user = request.session['user']
    else:
        return redirect('/user_sign_in')

    # if 'checkout_status' in request.session:
    #     print('checkout status while loading the checkout page',request.session['checkout_status'])
    #     if request.session['checkout_status'] == 'False':
    #         return redirect(user_home)

    sub_total = request.session['sub_total']
    address = Address.objects.filter(email=user)
    user = Users.objects.get(email=user)
    return render(request, 'user_checkout.html',
                  {
                      'sub_total': sub_total,
                      'address': address,
                      'user': user,
                      'default_address_id': 1,
                  })
# end
#############################################################################################################################

# generating the contents of the user return order
# start


def user_return_order(request, order_id):
    if 'user' in request.session:
        user = request.session['user']
    else:
        return redirect('/user_sign_in')
    this_user = Users.objects.get(email=user)
    product = Orders.objects.get(id=order_id)
    if request.method == 'POST':
        user = this_user.id
        reason = request.POST.get('reason')
        return_request = Return_request.objects.create(
            user=this_user, reason=reason)
        return_request.save()
        product.status = 'return requested'
        product.save()
        print('return request applied ')
        return redirect('/user_account')
    return render(request, 'user_return_order_form.html', {'product': product})
# end
#############################################################################################################################


def user_update_user(request, user_id):
    user_full_name = request.POST.get('user_full_name')
    user_contact_number = request.POST.get('user_contact_number')
    profile_image = request.FILES.get('profile_image')

    print(user_full_name)
    print(user_contact_number)
    user = Users.objects.get(id=user_id)
    user.full_name = user_full_name
    user.contact_number = user_contact_number
    user.profile_image = profile_image
    user.save()
    return redirect(user_account)
# generating the contents of the user razorpay place order
# start


@csrf_exempt
def user_razorpay_place_order(request):
    request.session['checkout_status'] = 'False'
    status = ''
    # sub_total = request.session['sub_total']
    sub_total = 234
    print(sub_total)
    if request.method == 'POST':
        user = request.POST.get('user')
        payment_method = request.POST.get('payment_method')
        this_user = Users.objects.get(email=user)
        cart_products = Cart.objects.filter(user=this_user.id)

        for product in cart_products:
            this_product = Products.objects.get(id=product.product_id)
            new_order = Orders.objects.create(product=this_product, user=this_user, quantity=product.quantity,
                                              Address=1, total_price=product.total_price, payment_method=payment_method)
            print('adding : ', this_product.name)
            new_order.save()
            cart_products = Cart.objects.filter(user=this_user.id).delete()
            status = 'success'
    return redirect('/user_thankyou_for_order')
# end
#############################################################################################################################

# generating the contents of the uesr validate coupon
# start


def user_validate_coupon(request):
    request.session['checkout_status'] = 'False'
    discount = 0
    if 'user' in request.session:
        user = request.session['user']
    else:
        return redirect('/user_sign_in')
    this_user = Users.objects.get(email=user)
    if request.method == 'POST':
        entered_coupon = request.POST.get('coupon')
        discount_percentage = 0
        available_coupons = Coupon.objects.all()
        status = 'failed'
        for coupon in available_coupons:
            if coupon.coupon == entered_coupon:
                coupon_history = Coupon_history.objects.all()
                for coupon_detail in coupon_history:
                    if int(this_user.id) == int(coupon_detail.user_id):
                        if entered_coupon == coupon_detail.coupon_code:
                            status = 'used'
                            return JsonResponse({'status': status})
                used_coupon = Coupon_history.objects.create(
                    user_id=this_user.id, coupon_code=entered_coupon)
                used_coupon.save()
                print('Coupon Applied')
                discount_percentage = coupon.discount_percentage
                status = 'success'
        prize = int(request.session['sub_total'])
        print(prize)
        discount = int(prize)*(discount_percentage / 100)
        discount_price = int(
            request.session['sub_total'] - discount)
        request.session['sub_total'] = discount_price
    return JsonResponse({'discount': discount_price, 'status': status})
# end
#############################################################################################################################

# generating the contents of the user paypal place order
# start


@csrf_exempt
def user_paypal_place_order(request):
    request.session['checkout_status'] = 'False'
    status = ''
    if 'user' in request.session:
        user = request.session['user']
    else:
        return redirect('/user_sign_in')
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        address_id = request.POST.get('address_id')
        this_user = Users.objects.get(email=user)
        cart_products = Cart.objects.filter(user=this_user.id)
        for product in cart_products:
            this_product = Products.objects.get(id=product.product_id)
            new_order = Orders.objects.create(product=this_product, user=this_user, quantity=product.quantity,
                                              Address=address_id, total_price=product.total_price, payment_method=payment_method)
            print('adding : ', this_product.name)
            new_order.save()
            cart_products = Cart.objects.filter(user=this_user.id).delete()
        status = 'success'
        return JsonResponse({'status': status})
# end
#############################################################################################################################

# generaing the contents of the user thankyou for order
# start


@never_cache
def user_thankyou_for_order(request):
    # thankyou(request)
    request.session['checkout_status'] = 'False'
    print(request.session['checkout_status'])
    return render(request, 'user_thankyou_for_order.html')

    # time.sleep(1000)
    # home(request)

# end
#############################################################################################################################

# generatinng the content for the user add address
# start


def user_add_address(request):
    if 'user' in request.session:
        user = request.session['user']
    else:
        return redirect('/user_sign_in')
    if request.method == 'POST':
        this_user = Users.objects.get(email=user)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        building_name = request.POST.get('building_name')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        contact = request.POST.get('contact')
        alt_contact = request.POST.get('alt_contact')
        user_new_address = Address.objects.create(
            email=user,
            first_name=first_name,
            last_name=last_name,
            building_name=building_name,
            street=street,
            city=city,
            state=state,
            pincode=pincode,
            contact=contact,
            alt_contact=alt_contact,
        )
        user_new_address.save()
        print('new address of the user  is saved')
        return redirect('/user_checkout')
    return render(request, 'user_add_address.html')
# end
###############################################################################################

# generating the contents for the user delete address


def user_delete_address(request):
    address_id = request.POST.get('address_id')
    print(address_id)
    delete_address = Address.objects.get(id=address_id).delete()
    return JsonResponse({'status': 'done'})
# end
###############################################################################################

# generating the contents for the user edit address


def user_edit_address(request, address_id):
    address_prefill = Address.objects.get(id=address_id)
    if request.method == 'POST':
        address_prefill.first_name = request.POST.get('first_name')
        address_prefill.last_name = request.POST.get('last_name')
        address_prefill.building_name = request.POST.get('building_name')
        address_prefill.street = request.POST.get('street')
        address_prefill.city = request.POST.get('city')
        address_prefill.state = request.POST.get('state')
        address_prefill.pincode = request.POST.get('pincode')
        address_prefill.contact = request.POST.get('contact')
        address_prefill.alt_contact = request.POST.get('alt_contact')
        address_prefill.save()
        print('address has been updated')
        return redirect('/user_account')
    return render(request, 'user_edit_address.html', {'address_prefill': address_prefill})
# end
###############################################################################################

# generating the content for the user sign in


@never_cache
def user_sign_in(request):
    if 'user' in request.session:
        return redirect(user_home)
    if request.method == 'POST':
        # collecting the data from the ajax request in user_sign_in.html
        user_email = request.POST.get('user_email')
        user_password = request.POST.get('user_password')
        print('got the user input data')
        # getting all the available users
        users = Users.objects.all()
        if len(users) > 0:
            for user in users:
                if user_email == user.email:
                    if user_password == user.password:
                        if user.active_status == 'active':
                            request.session['user'] = user_email
                            user_authentication_status = 'success'
                            break
                        user_authentication_status = 'user_not_active'
                        break
                    user_authentication_status = 'wrong_password'
                    break
                user_authentication_status = 'user_not_found'
            return JsonResponse({'user_authentication_status': user_authentication_status})
        else:
            return JsonResponse({'user_authentication_status': 'user_not_found'})
    return render(request, 'user_sign_in.html')
# end
###############################################################################################

# generating the content for the user update oder status


def user_update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order_status = request.POST.get('order_status')
        product = Orders.objects.get(id=order_id)
        print(product.status)
        product.status = 'canceled'
        product.save()
    return JsonResponse({'status': 'canceled'})
# end
###############################################################################################

# generating the user sign up


def user_sign_up(request):
    if request.method == 'POST':
        # collecting the data from the ajax request in user_sign_in.html
        user_full_name = request.POST.get('user_full_name')
        user_email = request.POST.get('user_email')
        user_password = request.POST.get('user_password')
        user_contact_number = request.POST.get('user_contact_number')
        profile_image = request.FILES.get('profile_image')
        # getting all the available users
        try:
            new_user = Users.objects.create(
                full_name=user_full_name,
                email=user_email,
                password=user_password,
                contact_number=user_contact_number,
                profile_image=profile_image
            )
            new_user.save()
            user_sign_up_status = 'user_created'
            return redirect(welcome_new_user)
        except:
            user_sign_up_status = 'failed'
        return redirect(user_home)
    return render(request, 'user_sign_up.html')
# end
###############################################################################################

# generating the contents in the welcome new user


def welcome_new_user(request):
    return render(request, 'welcome_new_user.html')
# end
###############################################################################################

# generating the user sign out


def user_sign_out(request):
    del request.session['user']
    return redirect('/user_home')
# end
###############################################################################################

# generating the contents of user reset password


def user_reset_password(request):
    if 'user' in request.session:
        user = request.session['user']
    else:
        return redirect('/user_sign_in')
    this_user = Users.objects.get(email=user)
    if request.method == 'POST':
        password = request.POST.get('new_pass')
        this_user.password = password
        this_user.save()
    return redirect(user_account)
# end
###############################################################################################

# generating the contents of the user reset pass success


def user_reset_pass_successs(request):
    return render(request, 'user_reset_pass_successs.html')
# end
###############################################################################################

# generating the contents of the user account


def user_account(request):
    refered_people = ''
    if 'user' in request.session:
        user = request.session['user']
    else:
        return redirect('/user_sign_in')
    this_user = Users.objects.get(email=user)
    orders = Orders.objects.filter(user_id=this_user.id).order_by('-id')
    address = Address.objects.filter(email=this_user.email)
    refered_people_details = References.objects.filter(user_id=this_user.id)
    delivered_orders = Orders.objects.filter(
        user_id=this_user.id, status='delivered')
    for order in delivered_orders:
        if int(current_date.day) >= int(order.Order_day)+7:
            order.status = 'delivered_no_return'
            order.save()
    print(refered_people_details)
    peoples = []
    for people in refered_people_details:
        print(people.refered_user_id)
        user = Users.objects.get(id=(people.refered_user_id))
        peoples.append(user.full_name)
    return render(
        request, 'user_account.html', {'user': this_user, 'orders': orders, 'address': address, 'refered_people_details': peoples})
# end

# generating the contents of the user otp sign in


def user_otp_sign_in(request):
    if request.method == 'POST':
        user_contact_number = request.POST.get('user_contact_number')
        try:
            print(user_contact_number)
            user = Users.objects.get(contact_number=123456789)
            print(user.contact_number)
            if user is not None:
                print('found the user')
                # generate otp and send otp
                # setting up the variables with the data that we get from the message api ( twilio )
                account_sid = 'ACd9fe7f948f2b0de94a1502c2998c884e'
                auth_token = '59a1424f9a3f2f933da5811c92d52fdd'
                # verifying the client usig the above details
                print('trying to connect with twilio.......')
                client = Client(account_sid, auth_token)
                print('connection established successfully')
                # generating 4 digit random otp
                print('generating 4 digit random otp....')
                global otp
                otp = str(random.randrange(1000, 9000))
                # setting up the message to send
                print('getting your otp (message) ready to send....')
                try:
                    client.api.account.messages.create(
                        to="+919946658045",
                        from_="+18304980732",
                        body="welcome to widecity shopping, enjoy shopping with us. This is your otp : {}".format(
                            otp)
                    )
                    print(f'otp has been send to +91  successfully')
                    otp_sign_in_user_status = 'success'
                    request.session['user'] = user.email
                except:
                    print('sry, failed to send the otp')
                    otp_sign_in_user_status = 'failed_to_send_otp'
                # end
        except:
            otp_sign_in_user_status = 'user_not_found'
        return JsonResponse({'otp_sign_in_user_status': otp_sign_in_user_status})
    return render(request, 'user_otp_sign_in.html')
# end
###############################################################################################

#


def user_otp_sign_in_validation(request):
    if request.method == 'POST':
        otp_1 = request.POST.get('otp_1')
        otp_2 = request.POST.get('otp_2')
        otp_3 = request.POST.get('otp_3')
        otp_4 = request.POST.get('otp_4')
        user_otp = str(otp_1+otp_2+otp_3+otp_4)
        print(otp)
        print(user_otp)
        user_authentication_status = 'wrong_otp'
        if str(user_otp) == str(otp):
            user_authentication_status = 'otp_verified'
        return JsonResponse({'user_authentication_status': user_authentication_status})

    return render(request, 'user_otp_sign_in_validation.html')


def forget_password(request):
    return render(request, 'forget_password.html')

    # admin side


@never_cache
def admin_sign_in(request):

    if request.session['admin'] != False:
        return redirect(admin_panel)
    if request.method == 'POST':
        # collecting the data from the ajax request in user_sign_in.html
        user_email = request.POST.get('user_email')
        user_password = request.POST.get('user_password')

        # getting all the available users
        users = Users.objects.all()

        if len(users) > 0:
            for user in users:
                if user_email == user.email:
                    if user_password == user.password:
                        user = Users.objects.get(email=user_email)
                        if user.active_status == 'active':
                            if user.is_admin == 'true':
                                request.session['admin'] = user_email
                                user_authentication_status = 'success'
                                break
                            user_authentication_status = 'user_not_admin'
                            break
                        user_authentication_status = 'admin_not_active'
                        break
                    user_authentication_status = 'wrong_password'
                    break
                user_authentication_status = 'admin_not_found'
            return JsonResponse({'user_authentication_status': user_authentication_status})
        else:
            return JsonResponse({'user_authentication_status': 'admin_not_found'})
    return render(request, 'admin_sign_in.html')


def admin_category_delete(request):
    admin = ''
    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')
    this_admin = Users.objects.get(email=admin)

    delete_category = Category.objects.get(
        id=request.POST.get('category_id')).delete()

    return JsonResponse({'status': 'done'})


def admin_sign_out(request):
    request.session['admin'] = False
    return render(request, 'admin_sign_in.html')


@never_cache
def admin_panel(request):
    admin = ''
    if request.session['admin'] == False:
        return redirect('/admin_sign_in')
    else:
        admin_email = request.session['admin']

    this_admin = Users.objects.get(email=admin_email)

    user_count = Users.objects.all().count()
    sales = Orders.objects.filter(status='Delivered')

    revenue = 0
    for sale in sales:
        revenue = revenue + sale.total_price

    return render(request, 'admin_panel.html', {'admin': this_admin, 'duration': '', 'sales': sales.count, 'customer_count': user_count, 'revenue': revenue})


def admin_list_customer(request):
    admin = ''
    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')
    this_admin = Users.objects.get(email=admin)

    try:
        users = Users.objects.all()

    except:
        pass

    return render(request, 'admin_list_customer.html', {'users': users, 'admin': this_admin})


def admin_thankyou_for_adding_product(request):
    return render(request, 'admin_thankyou_for_adding_product.html')

# generating the contents for the admin change order status
# start


def admin_change_order_status(request):

    order_status = request.POST.get('status')
    order_id = request.POST.get('order_id')
    print(order_id)
    change_order_status = Orders.objects.get(id=order_id)
    change_order_status.status = order_status
    change_order_status.save()
    return JsonResponse({'status': 'success'})


def admin_add_product(request):
    admin = ''
    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')
    this_admin = Users.objects.get(email=admin)

    if request.method == 'POST':
        category = request.POST.get('category')
        # getting datas from the specific fields from the frontend
        form = add_product_form(request.POST, request.FILES)
        category = request.POST.get('category')
        specification = request.POST.get('specification')

        # checking whether all the input fields are filled,not empty and are filled with proper inputs

        if form.is_valid():
            obj = form.save(commit=False)
            obj.category = category
            obj.specification = specification
            obj.save()
            return redirect(admin_thankyou_for_adding_product)

            #
        return HttpResponse('failed')
        # handling get request

        # trying to creating new product
    form = add_product_form()
    form_categories = Category.objects.all()
    return render(request, 'admin_add_product.html', {'form': form, 'form_categories': form_categories, 'admin': this_admin})


def admin_update_user_status(request):

    admin = ''
    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')
    this_admin = Users.objects.get(email=admin)

    if request.method == 'POST':
        status = request.POST.get('status')
        email = request.POST.get('email')
        # print(status)
        if status == 'true':
            status = 'block'
        else:
            status = 'active'
        # print(email)
        #     getting the user details for update
        customer = Users.objects.get(email=email)
        customer.active_status = status
        customer.save()
        print(customer.email)
        print(customer.active_status)
        return JsonResponse({'status': status})
    customers = Users.objects.all()
    return render(request, 'edit_customer.html', {'users': customers, 'admin': this_admin})


def admin_list_product(request):
    admin = ''
    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')
    this_admin = Users.objects.get(email=admin)

    products = Products.objects.all()
    return render(request, 'admin_list_product.html', {'admin': admin, 'products': products, 'admin': this_admin})


def admin_list_category(request):
    admin = ''
    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')
    this_admin = Users.objects.get(email=admin)

    categories = Category.objects.all()
    return render(request, 'admin_list_category.html', {'admin': admin, 'categories': categories, 'admin': this_admin})


def admin_add_category(request):
    admin = ''
    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')
    this_admin = Users.objects.get(email=admin)
    if request.method == 'POST':
        # getting datas from the specific fields from the frontend
        form = add_category(request.POST, request.FILES)
        # checking whether all the input fields are filled,not empty and are filled with proper inputs
        if form.is_valid():
            name = form.cleaned_data['name']
            try:
                category_id = Category.objects.get(name=str(name))
                if category_id is not None:
                    print('category already exist')
                    return render(request, 'admin_add_category.html', {'form': form, 'message': 'category already exist', 'admin': admin})

            except:
                # adding new details to the company_info table/model
                # form.cleaned_data['name'] = category_id
                form.save()
                return render(request, 'admin_add_category_success.html')

        return HttpResponse('failed')
        # handling get request

        # trying to creating new product
    form = add_category()
    return render(request, 'admin_add_category.html', {'form': form})


@never_cache
def admin_list_orders(request):
    admin = ''
    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')
    this_admin = Users.objects.get(email=admin)

    orders = Orders.objects.all()
    return render(request, 'admin_list_orders.html', {'admin': this_admin, 'orders': orders})


def admin_order_details(request, order_id):

    admin = ''
    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')
    this_admin = Users.objects.get(email=admin)

    order = Orders.objects.get(id=order_id)
    address = Address.objects.get(id=order.Address)

    if order.status == 'ordered':
        next_status = 'shipped'
    elif order.status == 'shipped':
        next_status = 'delivered'
    elif order.status == 'return requested':
        next_status = 'Returned'
    elif order.status == 'Returned':
        next_status = 'Refunded'
    else:
        next_status = ''

    return render(request, 'admin_order_details.html', {'order': order, 'address': address, 'next_status': next_status, 'admin': this_admin})


def admin_get_graph_data(request):

    sales_graph_data = []
    sales_graph_category = []
    user_graph_data = []
    user_graph_category = []

    if request.method == 'POST':

        duration = request.POST.get('duration')
        print('Getting Graph details of ', duration)
        orders = Orders.objects.all()
        users = Users.objects.all()

        # today
        # x axis - ordered products
        # y axis - delivered products
        if duration == 'today':

            sales_graph_data = []
            sales_graph_category = []
            user_graph_data = []
            user_graph_category = []

            count = 0
            # finding the number of sales on today based on orders
            cycle = 0
            for sale in orders:
                cycle = cycle + 1
                # filtering sales based on year
                if str(sale.Order_year) == str(current_date.year):
                    # filtering sales based on month
                    if str(sale.Order_month) == str(current_date.month):
                        # filtering sales based on day
                        if str(sale.Order_day) == str(current_date.day):
                            # filterin sales which has the status as delivered based on orders
                            print(sale.status)
                            if str(sale.status == 'delivered'):
                                count = count+1
                            sales_graph_data.append(count)
                            sales_graph_category.append(cycle)
            # printing the number of sales on today
            print('Number of sales In Today Is ', count)

            for user in users:
                # filtering sales based on year
                if str(user.signup_year) == str(current_date.year):
                    # filtering sales based on month
                    if str(user.signup_month) == str(current_date.month):
                        # filtering sales based on day
                        if str(user.signup_day) == str(current_date.day):
                            count = count+1
                            user_graph_data.append(4)
                            user_graph_category.append(1)

        # last 7 days
        # x axis - last 7 days
        # y axis - sales
        elif duration == 'last_7_days':

            sales_graph_data = []
            sales_graph_category = []
            user_graph_data = []
            user_graph_category = []

            count = 0
            # getting the sales of last  days
            # value of day is from 1 to 7
            for day in range(0, 7):
                count = 0
                for sale in orders:
                    if str(sale.Order_year) == str(current_date.year):
                        # print(sale.Order_day,current_date.day-timedelta(days=day).days)
                        if str(sale.Order_day) == str(current_date.day - (timedelta(days=day).days)):
                            # print('count+',count)
                            count = count+1
                sales_graph_data.append(count)
                sales_graph_category.append(
                    current_date.day - (timedelta(days=day).days))

            print('Number of sales in the last 7 days is ', sales_graph_data)

            # getting the new users
            for day in range(0, 7):
                count = 0
                for user in users:
                    if str(user.signup_year) == str(current_date.year):
                        if str(user.signup_month) == str(current_date.month):
                            # print(sale.Order_day,current_date.day-timedelta(days=day).days)
                            if str(user.signup_day) == str(current_date.day - (timedelta(days=day).days)):
                                # print('count+',count)
                                count = count+1
                user_graph_data.append(count)
                user_graph_category.append(
                    current_date.day - (timedelta(days=day).days))

            print('Number of revenue in the last 7 days is ', user_graph_data)

        # this month
        elif duration == 'last_month':
            sales_graph_data = []
            sales_graph_category = []
            user_graph_data = []
            user_graph_category = []
            count = 0

            for day in range(1, 32):
                count = 0
                for sale in orders:
                    if str(sale.Order_year) == str(current_date.year):
                        if str(sale.Order_month) == str(current_date.month):
                            if str(sale.Order_day) == str(day):
                                count = count+1
                sales_graph_data.append(count)
                sales_graph_category.append(day)

            for day in range(1, 32):
                count = 0
                for user in users:
                    if str(user.signup_year) == str(current_date.year):
                        if str(user.signup_month) == str(current_date.month):
                            if str(user.signup_day) == str(day):
                                count = count+1
                user_graph_data.append(count)
                user_graph_category.append(day)

        # this year
        else:

            sales_graph_data = []
            sales_graph_category = []
            user_graph_data = []
            user_graph_category = []
            count = 0

            for month in range(1, 13):
                count = 0
                for sale in orders:
                    if str(sale.Order_year) == str(current_date.year):
                        if str(sale.Order_month) == str(month):
                            count = count+1
                sales_graph_data.append(count)
                sales_graph_category.append(month)

            for month in range(1, 13):
                count = 0
                for user in users:
                    if str(user.signup_year) == str(current_date.year):
                        if str(user.signup_month) == str(month):
                            count = count+1
                user_graph_data.append(count)
                user_graph_category.append(month)

    user_count = Users.objects.all().count()
    sales = Orders.objects.filter(status='Delivered')
    cod = Orders.objects.filter(payment_method='cod').count()
    paypal = Orders.objects.filter(payment_method='paypal').count()
    razorpay = Orders.objects.filter(payment_method='razorpay').count()
    paypal_payment_method_graph_data = paypal
    razorpay_payment_method_graph_data = razorpay
    cod_payment_method_graph_data = cod

    revenue = 0
    for sale in sales:
        revenue = revenue + sale.total_price

    return render(request, 'admin_panel.html', {
        'duration': duration,
        'customer_count': user_count,
        'sales': sales.count(),
        'revenue': revenue,

        'sales_graph_data': sales_graph_data,
        'sales_graph_category': sales_graph_category,

        'user_graph_data': user_graph_data,
        'user_graph_category': [user_graph_category],

        'paypal_payment_method_graph_data': paypal_payment_method_graph_data,
        'razorpay_payment_method_graph_data': razorpay_payment_method_graph_data,
        'cod_payment_method_graph_data': cod_payment_method_graph_data,
    })


# @never_cache
def admin_edit_Product(request):
    admin = ''
    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')
    this_admin = Users.objects.get(email=admin)
    products = Products.objects.all()

    if request.method == 'POST':
        global current_product
        id = request.POST.get('id')
        print(id)
        product = Products.objects.get(id=id)
        product.name = request.POST.get('product_name')
        product.price = request.POST.get('product_price')
        product.category = request.POST.get('product_category')
        product.description = request.POST.get('product_description')
        product.specification = request.POST.get('product_specification')
        product.stock_available = request.POST.get('product_stock_available')
        product.rating = request.POST.get('product_rating')
        product.available_status = request.POST.get('product_status')

        if request.FILES.get('image_1') == None:
            product.image_1 = product.image_1
            print('product image 1 not found')
        else:
            product.image_1 = request.FILES.get('image_1')

        if request.FILES.get('image_2') == None:
            product.image_2 = product.image_2
            print('product image 2 not found')
        else:
            product.image_2 = request.FILES.get('image_2')
        if request.FILES.get('image_3') == None:
            product.image_3 = product.image_3
            print('product image 3 not found')
        else:
            product.image_3 = request.FILES.get('image_3')
        if request.FILES.get('image_4') == None:
            product.image_4 = product.image_4
            print('product image 4 not found')
        else:
            product.image_4 = request.FILES.get('image_4')
        product.offer_percentage = request.POST.get('offer_percentage')
        product.save()
        return render(request, 'admin_edit_product_success.html')

    action = request.GET['action']
    product_id = request.GET['product_id']
    print(action)
    product = Products.objects.get(id=product_id)

    if action == 'edit':
        return render(request, 'admin_edit_product.html', {'product': product, 'admin': this_admin})
    elif action == 'delete':
        product.delete()
        return redirect(admin_list_product)

    return redirect('/admin_panel')


def admin_edit_category(request, cat_id):
    category = Category.objects.get(id=cat_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        offer_percentage = request.POST.get('offer_percentage')

        if image is None:
            category.image = Category.objects.get(id=cat_id).image
        else:
            category.image = image

        category.offer_percentage = offer_percentage
        category.name = name
        category.save()

    return render(request, 'admin_edit_category.html', {'category': category})


def admin_edit_banner(request):
    admin = ''
    try:
        banner1 = Banners.objects.get(id=1)
        banner2 = Banners.objects.get(id=2)
        banner3 = Banners.objects.get(id=3)
    except:
        banner1 = ''
        banner2 = ''
        banner3 = ''

    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')

    if request.method == 'POST':

        if request.POST.get('banner') == '1':

            banner_1_image = request.FILES.get('banner_1_image')
        # banner_2_image = request.FILES('banner_2_image')
        # banner_3_image = request.FILES('banner_3_image')

            banner_1_heading = request.POST.get('banner_1_heading')
            banner_1_description = request.POST.get('banner_1_description')
            banner_1 = Banners.objects.get(id=1)
            banner_1.heading = banner_1_heading
            banner_1.description = banner_1_description
            banner_1.image = banner_1_image
            banner_1.save()

        if request.POST.get('banner') == '2':

            # banner_1_image = request.FILES('banner_1_image')
            banner_2_image = request.FILES.get('banner_2_image')
        # banner_3_image = request.FILES('banner_3_image')

            banner_2_heading = request.POST.get('banner_2_heading')
            banner_2_description = request.POST.get('banner_2_description')
            banner_2 = Banners.objects.get(id=2)
            banner_2.heading = banner_2_heading
            banner_2.description = banner_2_description
            banner_2.image = banner_2_image
            banner_2.save()

        if request.POST.get('banner') == '3':

            # banner_1_image = request.FILES('banner_1_image')
            # banner_2_image = request.FILES('banner_2_image')
            banner_3_image = request.FILES.get('banner_3_image')

            banner_3_heading = request.POST.get('banner_3_heading')
            banner_3_description = request.POST.get('banner_3_description')
            banner_3 = Banners.objects.get(id=3)
            banner_3.heading = banner_3_heading
            banner_3.description = banner_3_description
            banner_3.image = banner_3_image
            banner_3.save()

    return render(request, 'admin_edit_banner.html', {'banner1': banner1, 'banner2': banner2, 'banner3': banner3})


def admin_category_offers(request):
    admin = ''
    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')
    if request.method == 'POST':

        new_offer_percentage = request.POST.get('new_offer_percentage')
        category_id = request.POST.get('category_id')
        print(new_offer_percentage, category_id)
        category = Category.objects.get(id=category_id)
        category.offer_percentage = new_offer_percentage
        category.save()

    this_admin = Users.objects.get(email=admin)
    categories = Category.objects.all()
    return render(request, 'admin_category_offers.html', {'categories': categories})


def admin_product_offers(request):
    admin = ''
    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')
    if request.method == 'POST':

        new_offer_percentage = request.POST.get('new_offer_percentage')
        product_id = request.POST.get('product_id')
        print(new_offer_percentage, product_id)
        product = Products.objects.get(id=product_id)
        product.offer_percentage = new_offer_percentage
        product.save()

    this_admin = Users.objects.get(email=admin)
    products = Products.objects.all()

    return render(request, 'admin_product_offers.html', {'products': products})


def admin_edit_company_info(request):
    admin = ''
    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')

    this_admin = Users.objects.get(email=admin)
    return render(request, 'admin_edit_company_info.html', {'admin': this_admin})


def admin_sales_report(request):
    ppp = 4  # product per page in sales report
    admin = ''
    global duration
    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')

    # if request.method == 'GET':
    #     page = request.GET['page']

    if request.method == 'POST':

        if 'export' in request.POST.keys():
            filetype = request.POST.get('filetype')
            if filetype == 'pdf':
                buf = io.BytesIO()
                c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
                textob = c.beginText()
                textob.setTextOrigin(inch, inch)
                textob.setFont("Helvetica", 10)

                if duration == 'Today':
                    ordered_products = Orders.objects.filter(
                        Order_day=current_date.day)
                if duration == 'Month':
                    ordered_products = Orders.objects.filter(
                        Order_month=current_date.month)
                if duration == 'Year':
                    ordered_products = Orders.objects.filter(
                        Order_year=current_date.year)

                lines = [
                    'Sales Report of WideCity Shopping ',
                    '',
                    '      Date      |       brand       |                       product name                     |  sold   |   stock balance  |   revenue  ',
                    '',

                ]
                for orders in ordered_products:

                    lines.append(str(orders.Order_day) +
                                 str('/'+str(orders.Order_month)) +
                                 str('/'+str(orders.Order_year)) +
                                 str('         '+str(orders.product.category)) +
                                 str('        '+str(orders.product.name)) +
                                 str('       '+str(orders.product.total_sold)) +
                                 str('            '+str(orders.product.stock_available)) +
                                 str('                 ' +
                                     str(orders.product.price))

                                 )

                    lines.append(
                        "-----------------------------------------------------------------------------------------------------------------------------------")

                lines.append('')
                lines.append('This report is of the duration of last 7 days')

                for line in lines:
                    textob.textLine(line)

                c.drawText(textob)
                c.showPage()
                c.save()
                buf.seek(0)

                return FileResponse(buf, as_attachment=True, filename='output.pdf ')

            elif filetype == 'csv':

                # output filename handling
                filename = 'Widecity Report'
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename={}.csv'.format(
                    filename)
                writer = csv.writer(response)
                writer.writerow(['Product Name', 'Ordered Day', 'Ordered Month',
                                'Ordered Year', 'Quantity', 'Total Price'])
                if duration == 'Today':
                    ordered_products = Orders.objects.filter(
                        Order_day=current_date.day)
                if duration == 'Month':
                    ordered_products = Orders.objects.filter(
                        Order_month=current_date.month)
                if duration == 'Year':
                    ordered_products = Orders.objects.filter(
                        Order_year=current_date.year)

                for product in ordered_products:

                    print(product.product.name)
                    print(product.Order_day, product.Order_month,
                          product.Order_year)
                    print(product.quantity)
                    print(product.total_price)

                    row = [product.product.name, product.Order_day, product.Order_month,
                           product.Order_year, product.quantity, product.total_price]

                    writer.writerow(row)

                return response

        elif 'duration' in request.POST.keys():
            orders = Orders.objects.all()
            current_page = 1
            if 'page_number' in request.POST.keys():
                current_page = request.POST.get('page_number')
                print('got page_number', current_page)

            duration = request.POST.get('duration')
            print(duration)
            if duration == 'custom_search':
                from_date = request.POST.get('from')
                to_date = request.POST.get('to')

                from_date = from_date.split('-')
                to_date = to_date.split('-')

                from_day = from_date[2]
                from_month = from_date[1]
                from_year = from_date[0]
                to_day = to_date[2]
                to_month = to_date[1]
                to_year = to_date[0]
                for order in orders:
                    orders = Orders.objects.filter(
                        Order_day__gte=from_day, Order_day__lte=to_day,
                        Order_month__gte=from_month, Order_month__lte=to_month,
                        Order_year__gte=from_year, Order_year__lte=to_year
                    )

                p = Paginator(orders, ppp)
                page_obj = p.get_page(current_page)
                available_pages = []
                pages = int(orders.count()/ppp)
                for i in range(pages):
                    available_pages.append(i)
                return render(request, 'admin_sales_report.html', {'admin': admin, 'orders': page_obj, 'duration': duration, 'available_pages': available_pages})

            else:
                if duration == 'Today':
                    print(duration)
                    orders = Orders.objects.filter(Order_day=current_date.day)
                elif duration == 'Month':
                    print(duration)
                    orders = Orders.objects.filter(
                        Order_month=current_date.month)
                elif duration == 'Year':
                    print(duration)
                    orders = Orders.objects.filter(
                        Order_year=current_date.year)

                p = Paginator(orders, ppp)
                page_obj = p.get_page(current_page)
                available_pages = []
                pages = int(orders.count()/ppp)
                for i in range(pages):
                    available_pages.append(i)
                return render(request, 'admin_sales_report.html', {'admin': admin, 'orders': page_obj, 'duration': duration, 'available_pages': available_pages})

    orders = Orders.objects.all()
    p = Paginator(orders, ppp)
    page_obj = p.get_page(1)
    available_pages = []
    pages = int(orders.count()/ppp)
    for i in range(pages):
        available_pages.append(i)
    return render(request, 'admin_sales_report.html', {'admin': admin, 'orders': page_obj, 'current_date': current_date, 'duration': duration, 'available_pages': available_pages})


def admin_remove_coupon(request):
    if request.method == 'POST':

        print('trying to remove')
        coupon_id = request.POST.get('coupon_id')
        coupon = Coupon.objects.get(id=coupon_id).delete()
        print('coupon deleted')
        return JsonResponse({'status': 'done'})

    coupons = Coupon.objects.all()
    return render(request, 'admin_manage_coupons.html', {'coupons': coupons})


def admin_add_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('new_coupon')
        coupon_discount = request.POST.get('new_coupon_discount')
        print('trying to add a new coupon')
        new_coupon = Coupon.objects.create(
            coupon=coupon_code, discount_percentage=coupon_discount)
        new_coupon.save()
        print(' coupon added ')
        return JsonResponse({'status': 'success'})

    #  payments


def pay_with_paypal(request):
    admin = ''
    if 'user' in request.session:
        user = request.session['user']
    else:
        return redirect('/user_sign_in')

    # user = Users.objects.get(email = user)
    return render(request, 'payment_paypal.html', {'user': 'user'})


def pay_with_razorpay(request):
    import razorpay
    client = razorpay.Client(
        auth=("rzp_test_oRDO7oXd5GwL0O", "rrdO67DEimkHGWBihfZvO6iW"))

    DATA = {
        "amount": 100,
        "currency": "INR",
        "receipt": "receipt#1",
        "notes": {
            "key1": "value3",
            "key2": "value2"
        }
    }
    client.order.create(data=DATA)
    admin = ''
    if 'user' in request.session:
        user = request.session['user']
    else:
        return redirect('/user_sign_in')

    return render(request, 'payment_razorpay.html', {'user': user})


@csrf_exempt
def razorpay_success(request):
    return render(request, 'success.html')


# hhjhb


# 33   test #################################3

def test(request):
    return render(request, 'tesing.html')
