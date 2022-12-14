# this program perform the backend logical operations in widecity shopping 
# Author: widecity Developers

# starting importing the neccessary modules and packages
import csv
from django.http import JsonResponse
from .forms import ImageForm
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
from pandas import isnull
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from django.shortcuts import redirect, render
from requests import session
from twilio.rest import Client
from widecity_shopping.forms import add_category, add_product_form, edit_banner
from widecity_shopping.models import Banners, Cart, Category, Coupon, Coupon_history, Orders, Products, References, Return_request, Users, Address
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
import pdfkit
import datetime
from datetime import timedelta
# end 


# declaring or initializing the global variables
current_date = datetime.date.today()
duration = 'Today'
otp = '0'
delivery_charge = 10
# end

# starting the functions to handle our app backend
def handler404(request,data):
    return redirect(root)
def handler500(request):
    return render(request,'handler500.html')


def root(request):
    if 'user' in request.session:return redirect('/user_home')
    else: return redirect('/user_sign_in')

def user_home(request):
    user = ''
    # gathering neccessary data from the server
    try:banner = Banners.objects.get(id=1)  # getting the banner data
    except:banner = ''  # assigning null to the banners if there is an issue in getting the banner
    try: products = Products.objects.all()
    except: products = ''
    try:categories = Category.objects.all()
    except: categories = ''
    print(products)
    try:
        if 'user' in request.session:
            user_email = request.session['user']
            user = Users.objects.get(email=user_email)
        else:user = 'guest'
    except: pass
    return render(request, 'user_home.html', {'user': user, 'banner': banner, 'products': products, 'categories': categories})


def user_product_detail(request, product_id):
    product = Products.objects.get(id=product_id)
    category = Products.objects.filter(category=product.category)
    return render(request, 'user_product_detail.html', {'product': product, 'category': category})


def user_invoice(request):
    if 'user' in request.session:user = request.session['user']
    else:return redirect('/user_sign_in')
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


def user_category_view(request, name):
    category = Category.objects.get(name=name)
    category_products = Products.objects.filter(category=category.name)
    categories = Category.objects.all()
    product_count = category_products.count()
    p = Paginator(category_products, 2)
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
            for i in page_obj:
                print(i)
            JsonResponse({'category_products': page_obj})
    return render(request, 'user_category_view.html',
                  {
                      'category': category,
                      'category_products': page_obj,
                      'categories': categories,
                  })


def user_add_to_cart(request):
    response = 'failed'
    if 'user' in request.session:user = request.session['user']
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

def user_view_cart(request):
    sub_total = 0
    # trying to add the order to the cart
    if 'user' in request.session:
        user = request.session['user']
    else: return redirect('/user_sign_in')
    try: user = Users.objects.get(email=user)
    except:user = ''
    try:products = Cart.objects.filter(user=user.id)
    except: products = ''
    if len(products) == 0:return render(request, 'user_cart_empty.html')
    product_offer = 0
    for price in products:
        # price.total_price = Products.objects.get(id = price.product.id).price
        print('product with discount', price.total_price)
        sub_total = int(sub_total) + int(price.total_price)
    # total = sub_total+delivery_charge
    special_offer = product_offer
    request.session['sub_total'] = sub_total
    # for data in products:
    #     temp_data = model_to_dict(data)
    #     discount = int(data.product.price) * (int(data.product.offer_percentage)/100)
    #     temp_data['total'] = int(data.product.price) - discount
    #     print(temp_data)
    #     total = int(data.product.price) * (int(data.product.offer_percentage)/100)
    #     # data.insert(total)

    #     data['total']=total

    return render(request, 'user_cart_view.html', {'user': user, 'products': products, 'sub_total': sub_total, 'special_offer': special_offer, 'delivery_charge': delivery_charge})


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
# 3


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

#####################################################


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


def user_delete_cart_item(request):
    if request.method == 'POST':
        cart_id = request.POST.get('id')
        delete_product = Cart.objects.get(id=cart_id).delete()
        print('one item from the cart is deleted')
        return JsonResponse({'deleted': 'deleted'})


def user_check_cart_or_shop(request):
    return render(request, 'user_check_cart_or_shop.html')


def user_checkout(request):
    if 'user' in request.session:
        user = request.session['user']
    else:
        return redirect('/user_sign_in')

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


@csrf_exempt
def user_razorpay_place_order(request):

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


def user_validate_coupon(request):
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
                discount_percentage = coupon.discount_percentage
                status = 'success'

        prize = int(request.session['sub_total'])
        print(prize)
        discount = int(prize)*(discount_percentage / 100)
        request.session['sub_total'] = int(
            request.session['sub_total'] - discount)
        print(coupon)
    return JsonResponse({'discount': discount, 'status': status})


@csrf_exempt
def user_paypal_place_order(request):
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


def user_thankyou_for_order(request):
    return render(request, 'user_thankyou_for_order.html')


def admin_change_order_status(request):

    order_status = request.POST.get('status')
    order_id = request.POST.get('order_id')
    print(order_id)
    change_order_status = Orders.objects.get(id=order_id)
    change_order_status.status = order_status
    change_order_status.save()
    return JsonResponse({'status': 'success'})


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


def user_delete_address(request):
    address_id = request.POST.get('address_id')
    print(address_id)
    delete_address = Address.objects.get(id=address_id).delete()
    return JsonResponse({'status': 'done'})


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


def user_sign_in(request):
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


def user_update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order_status = request.POST.get('order_status')

        product = Orders.objects.get(id=order_id)
        print(product.status)
        product.status = 'canceled'
        product.save()
    return JsonResponse({'status': 'canceled'})


def user_sign_up(request):

    if request.method == 'POST':
        reference_id_status = 'referal_owner_not_found'
        user_entered_reference_id = ''
        # collecting the data from the ajax request in user_sign_in.html
        user_full_name = request.POST.get('user_full_name')
        user_email = request.POST.get('user_email')
        user_password = request.POST.get('user_password')
        user_contact_number = request.POST.get('user_contact_number')
        user_entered_reference_id = request.POST.get('user_reference_id')

        users = Users.objects.all()
        for user in users:
            if user.email == user_email:
                user_sign_up_status = 'user_exist'
                return JsonResponse({'user_sign_up_status': user_sign_up_status,'reference_id_status':reference_id_status})

        
        try:
            print('trying to create the new user account...')

            new_user = Users.objects.create(
                full_name=user_full_name,
                email=user_email,
                password=user_password,
                contact_number=user_contact_number,
                reference_id = random.randrange(1000000000,9999999999)
            )
            new_user.save()
            print('user created')
            user_sign_up_status = 'user_created'

            users = Users.objects.all()
            print('getting the user details of the new user with email ',user_email)
            this_user = Users.objects.get(email = user_email)
            print('got the user id the new user as ',this_user.id)
            # searching the user to whom this referal id belongs too.
            for referal_owner in users:
                if referal_owner.reference_id ==  user_entered_reference_id:
                    # adding the user id of the new user as the refered user 
                    new_refered_user = References.objects.create(user_id = referal_owner.id,refered_user_id = this_user.id)
                    new_refered_user.save()
                    reference_id_status = 'refered'
                    print('found the referal id. Adding the new user as the refered user.')
                else:
                    reference_id_status = 'referal_owner_not_found'

        # getting all the available users
        except:
            user_sign_up_status = 'failed'

        return JsonResponse({'user_sign_up_status': user_sign_up_status,'reference_id_status':reference_id_status})

    return render(request, 'user_sign_up.html')


def welcome_new_user(request):
    return render(request, 'welcome_new_user.html')


def user_sign_out(request):
    request.session.flush()
    return redirect('/user_home')


def user_account(request):
    if 'user' in request.session:
        user = request.session['user']
    else:
        return redirect('/user_sign_in')
    this_user = Users.objects.get(email=user)
    orders = Orders.objects.filter(user_id=this_user.id)
    address = Address.objects.filter(email=this_user.email)

    return render(request, 'user_account.html', {'user': this_user, 'orders': orders, 'address': address})


def user_otp_sign_in(request):
    if request.method == 'POST':
        user_contact_number = request.POST.get('user_contact_number')
        try:
            user = Users.objects.get(email='amalpullan4@gmail.com')
            if user is not None:
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


def admin_sign_in(request):

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
    return render(request, 'admin_sign_out.html')


def admin_panel(request):
    admin = ''
    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')
    this_admin = Users.objects.get(email=admin)

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
            return redirect('/admin_thankyou_for_adding_product')
            #
        return HttpResponse('failed')
        # handling get request

        # trying to creating new product
    form = add_product_form()
    form_categories = Category.objects.all()

    return render(request, 'admin_add_product.html', {'form': form, 'form_categories': form_categories, 'admin': this_admin})

    # admin = ''
    # if 'admin' in request.session:
    #     admin = request.session['admin']
    # else:
    #     return redirect('/admin_sign_in')
    # return render(request,'admin_add_product.html',{'admin':admin})


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
        next_status = 'Accept Return Request'
    elif order.status == 'Accept Return Request':
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
        banner = Banners.objects.get(id=1)
    except:
        banner = ''

    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')

    if request.method == 'POST':

        form = edit_banner(request.POST, request.FILES)
        print('got values')

        if form.is_valid():
            form = edit_banner(request.POST, request.FILES, instance=banner)
            form.save()
            return HttpResponse('banner saved')
        return HttpResponse('form not valid')

    form = edit_banner()
    return render(request, 'admin_edit_banner.html', {'form': form, 'banner': banner})


def admin_edit_company_info(request):
    admin = ''
    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')
    this_admin = Users.objects.get(email=admin)
    return render(request, 'admin_edit_company_info.html', {'admin': this_admin})


def admin_sales_report(request):
    admin = ''
    global duration
    if 'admin' in request.session:
        admin = request.session['admin']
    else:
        return redirect('/admin_sign_in')

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

            duration = request.POST.get('duration')
            print(duration)
            orders = Orders.objects.all()
            if duration == 'Today':
                print(duration)
                orders = Orders.objects.filter(Order_day=current_date.day)
            elif duration == 'Month':
                print(duration)
                orders = Orders.objects.filter(Order_month=current_date.month)
            elif duration == 'Year':
                print(duration)
                orders = Orders.objects.filter(Order_year=current_date.year)

        return render(request, 'admin_sales_report.html', {'admin': admin, 'orders': orders, 'duration': duration})

    orders = Orders.objects.all()
    return render(request, 'admin_sales_report.html', {'admin': admin, 'orders': orders, 'current_date': current_date, 'duration': duration})


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


def main_view(request):
    form = ImageForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return JsonResponse({'message': 'works'})
    context = {'form': form}
    return render(request, 'admin_image_upload.html', context)


# 33   testing purpous #################################3

def test(request):
    return render(request, 'tesing.html')


##################################################################################################################################

# thank you 
# last update on 21-10-2022