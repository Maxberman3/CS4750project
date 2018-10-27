import requests
import json
import secrets

from django import forms
from decimal import Decimal
from django.shortcuts import render,reverse,redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.conf import settings

from urllib.parse import urlencode
from django.core.mail import send_mail
from .forms import SignUpForm, PaymentForm
from festivalpickr.utils import songkickcall

from django_coinpayments.models import Payment
from django_coinpayments.exceptions import CoinPaymentsProviderError
from django.views.generic import FormView, ListView, DetailView
from django.shortcuts import render, get_object_or_404

spot_client_id=settings.SPOT_CLIENT_ID
spot_secret_id=settings.SPOT_SECRET_ID
spot_uri=settings.SPOT_CALLBACK

def index(request):
    return render(request,'festivalpickr/index.html')

def about(request):
    return render(request, 'festivalpickr/about.html')

def contact(request):
    return render(request,'festivalpickr/contact.html')

def login(request):
    return render(request,'registration/login.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save();
            user.refresh_from_db()
            user.profile.address = form.cleaned_data.get('address')
            user.profile.city = form.cleaned_data.get('city')
            user.profile.state = form.cleaned_data.get('state')
            user.profile.zip = form.cleaned_data.get('zip')
            user.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            django_login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'festivalpickr/signup.html', {'form': form})

def toemail(request):
    if request.method != 'POST':
        return render('festivalpicr/error.html',{'problem':'unable to handle the message due to bad request','message':'This url should only be accessed through a post request'})
    name=request.POST['name']
    theirmail=request.POST['email']
    contents=request.POST['message']
    send_mail(
    name,
    contents,
    theirmail,
    ['festivalpickr@gmail.com'],
    fail_silently=False,
    )
    return redirect('index')

def getspotify(request):
    if "refresh_token" in request.session:
        return redirect(reverse('refreshlanding'))
    state=secrets.token_urlsafe(20)
    request.session['state_token']=state
    scope='user-library-read'
    payload={'client_id':spot_client_id,'response_type':'code','redirect_uri':spot_uri,'scope':scope,'state':state}
    url_args=urlencode(payload)
    auth_url = "{}/?{}".format('https://accounts.spotify.com/authorize', url_args)
    return redirect(auth_url)

def landing(request):
    if 'error' in request.GET:
        return render('festivalpickr/error.html',{'problem':'spotify authorization failed','message':'Either you failed to give permission to the app or there was a faulty connection'})
    if request.GET['state'] != request.session['state_token']:
        return render('festivalpickr/error.html',{'problem':'Are you trying to hack me?','message':'Get that weak shit outta here'})
    spotcode=request.GET['code']
    payload={
    'grant_type':'authorization_code',
    'code':str(spotcode),
    'redirect_uri':spot_uri,
    'client_id':spot_client_id,
    'client_secret':spot_secret_id
    }
    post_request=requests.post('https://accounts.spotify.com/api/token',data=payload)
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    request.session['refresh_token']=refresh_token
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}
    lib_request_url='https://api.spotify.com/v1/me/tracks'
    lib_request=requests.get(lib_request_url,headers=authorization_header)
    lib_data=json.loads(lib_request.text)
    artist_set=set()
    if items not in lib_data:
        print(lib_data)
        return render('festivalpickr/error.html',{'problem':'Some sort of issue with the returned spotify library','message':'Check the console to see what was returned'})
    while True:
        for item in lib_data['items']:
            track=item['track']
            artist_set.add(track['artists'][0]['name'])
        if lib_data['next'] is None:
            break
        else:
            lib_request_url=lib_data['next']
            lib_request=requests.get(lib_request_url,headers=authorization_header)
            lib_data=json.loads(lib_request.text)
    context={
    'festivals':songkickcall(artist_set),
    }
    return render(request,'festivalpickr/festivals.html',context)

def refreshlanding(request):
    if 'refresh_token' not in request.session:
        return render('festivalpickr/error.html',{'problem':'you have not yet been authorized through spotify','message':'Im not even sure how you got here'})
    refresh_token=request.session['refresh_token']
    payload={'grant_type':'refresh_token','refresh_token':refresh_token,'client_id':spot_client_id,'client_secret':spot_secret_id}
    refresh_request=requests.post('https://accounts.spotify.com/api/token',data=payload)
    response_data = json.loads(refresh_request.text)
    access_token = response_data["access_token"]
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}
    lib_request_url='https://api.spotify.com/v1/me/tracks'
    lib_request=requests.get(lib_request_url,headers=authorization_header)
    lib_data=json.loads(lib_request.text)
    artist_set=set()
    while True:
        for item in lib_data['items']:
            track=item['track']
            artist_set.add(track['artists'][0]['name'])
        if lib_data['next'] is None:
            break
        else:
            lib_request_url=lib_data['next']
            lib_request=requests.get(lib_request_url,headers=authorization_header)
            lib_data=json.loads(lib_request.text)
    festivals=songkickcall(artist_set)
    festivals_order=sorted(festivals,key=lambda k:festivals[k]['score'],reverse=True)
    context={
    'festivals':festivals,
    'festivals_order':festivals_order,
    }
    return render(request,'festivalpickr/festivals.html',context)

def create_tx(request, payment):
    context = {}
    try:
        tx = payment.create_tx()
        payment.status = Payment.PAYMENT_STATUS_PENDING
        payment.save()
        context['object'] = payment
    except CoinPaymentsProviderError as e:
        context['error'] = e
    return render(request, 'festivalpickr/payment_result.html', context)

class PaymentDetail(DetailView):
    model = Payment
    template_name = 'festivalpickr/payment_result.html'
    context_object_name = 'object'

class PaymentSetupView(FormView):
    template_name = 'festivalpickr/payment_setup.html'
    form_class = PaymentForm

    def form_valid(self, form):
        cl = form.cleaned_data
        payment = Payment(currency_original=cl['currency_paid'],
                          currency_paid=cl['currency_paid'],
                          amount=Decimal(0.05),
                          amount_paid=Decimal(0),
                          status=Payment.PAYMENT_STATUS_PROVIDER_PENDING)
        return create_tx(self.request, payment)

def create_new_payment(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if payment.status in [Payment.PAYMENT_STATUS_PROVIDER_PENDING, Payment.PAYMENT_STATUS_TIMEOUT]:
        pass
    elif payment.status in [Payment.PAYMENT_STATUS_PENDING]:
        payment.provider_tx.delete()
    else:
        error = "Invalid status - {}".format(payment.get_status_display())
        return render(request, 'festivalpickrs/payment_result.html', {'error': error})
    return create_tx(request, payment)
