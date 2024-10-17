from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import urlencode
from .models import Customers
from .forms import UsersLoginForm, SignupForm
from django.contrib import messages
from django.shortcuts import render, redirect,HttpResponse,get_object_or_404,HttpResponseRedirect
from django.contrib import messages
from .models import Customers,Albums,Photo,FavAlbums
from .forms import UsersLoginForm,AlbumCreations
import uuid,os
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from .forms import UsersLoginForm,ImagesForm
import shutil

def index(request):
    logined,email = verifyLogin(request)
    if logined:
       
        user = Customers.objects.get(email=email)
        albums = Albums.objects.filter(user=user)
        favorited_albums = FavAlbums.objects.filter(user=user)
        context ={
            'albums' : albums,
            'fav':favorited_albums,
            'logined': logined,
            'user':user
        }
    else:
        context ={
            
            
            'logined': False,
            
        }
        
    return render(request,'index.html',context)

def dashboard(request):
    logined,email = verifyLogin(request)

    print(logined)
    if logined:
       
        user = Customers.objects.get(email=email)
        albums = Albums.objects.filter(user=user)
        favorited_albums = FavAlbums.objects.filter(user=user)
        context ={
            'albums' : albums,
            'fav':favorited_albums,
            'logined': logined,
            'user':user
        }
    
        return render(request, 'dashboard.html',context) 
    else:
        
        return redirect('login')  

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            print('else21')
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password']) 
            user.save()
            return redirect('login') 
        else:
            print('else')
            return redirect('login')
    else:
        return redirect('login')
    

def login(request):
    next_url = request.POST.get('next','/dashboard')
    if request.method == 'POST':
        frm = UsersLoginForm(request.POST)
        if frm.is_valid():
            email = frm.cleaned_data.get('email')
            password = frm.cleaned_data.get('password')
            
            if email and password:
                try:
                    user = Customers.objects.get(email=email)
                    if user.check_password(password):
                        
                        print('logined')
                        if next_url:

                            response = HttpResponseRedirect(next_url) 
                            response.set_cookie('logined', [True,email]) 
                            
                            return response
                        else:
                            response = redirect('dashboard') 
                            response.set_cookie('logined', [True,email]) 
                            
                            return response


                    else:
                        messages.error(request, 'Incorrect password.')
                except Customers.DoesNotExist:
                    messages.error(request, 'User does not exist.')
                except Customers.MultipleObjectsReturned:
                    messages.error(request, 'Multiple users found with this email.')
            else:
                messages.error(request, 'Email or password not provided.')
        else:
            messages.error(request, 'Invalid form submission.')
    else:
        frm = UsersLoginForm()
        next_url = request.GET.get('next', '/dashboard')

    return render(request, "login.html", {'form': frm,'next':next_url})

def verifyLogin(request):

    try:
        response = eval(request.COOKIES.get('logined'))
        logined = response[0]
        if logined:
            email = response[1]
        else:
            email = None
        return logined ,email
    except TypeError:
        return False,None
    
def albumcreation(request):
    logined, email = verifyLogin(request)
    if logined:
        if request.method == 'POST':
            frm = AlbumCreations(request.POST)
            if frm.is_valid():
                album_name = request.POST.get('name')
                album_share = request.POST.get('share')
                if album_share == 'on' : album_share = True
                else: album_share = False
               
                code = str(uuid.uuid4())
                
                try:
                    
                    album = Albums.objects.create(
                        name=album_name,
                        path=f'{code}\\',
                        user=Customers.objects.get(email=email),  
                        share=album_share,
                        code=code
                    )
                    
                    
                    media_folder = os.path.join(settings.MEDIA_ROOT, code)
                    os.makedirs(media_folder, exist_ok=True)
                    
                    return redirect('dashboard') 
                except Exception as e:
                    
                    print(f'Error creating album: {e}')
                    messages.error(request, 'An error occurred while creating the album.')
        else:
            frm = AlbumCreations()
        
        return render(request, 'albumcreate.html', {'form': frm})
    else:
        return redirect('signup')



get_object_or_404


def logout(request):
    
    response = redirect('/')  # 
    response.delete_cookie('logined')
    print('logout')
    return response

def album_view(request, id):
    album = get_object_or_404(Albums, code=id)
    photos = album.photos.all()
    form = ImagesForm()
    logind, email = verifyLogin(request)
    print('hi')
    
    path = request.get_full_path()
    login_url = reverse('login')
    next_url = f"{login_url}?{urlencode({'next': path})}"
    

    def check_ownership(album_code, user_email):
        album_details = get_object_or_404(Albums, code=album_code)
        return album_details.user.email == user_email,album_details.user.name

    
    try:
        user = Customers.objects.get(email=email)
        is_favorited = FavAlbums.objects.filter(user=user, album=album).exists()
    except:
        user = None
        is_favorited = False
    print(f'is_favorited {is_favorited}')
    owner , oemail = check_ownership(id, email)
    context = {
        'album': album,
        'photos': photos,
        'form': form,
        'logined': logind,
        'owner': owner,
        'ownername' :oemail,
        'user': user,
        'is_favorited': is_favorited,  
        'path': next_url
    }
    print(check_ownership(id,email))
    return render(request, 'albumview.html', context)


def upload_photos(request, id):
    album = get_object_or_404(Albums, code=id)
    photos = album.photos.all()

    if request.method == 'POST':
        form = ImagesForm(request.POST, request.FILES)
        print("Form errors:", form.errors)  
        print("FILES data:", request.FILES)  
        
        if form.is_valid():
            images = request.FILES.getlist('images')
            email = verifyLogin(request)[1]
            user = Customers.objects.get(email=email)

            for image in images:
                Photo.objects.create(
                    album=album,
                    images=image,
                    uploaded_by=user
                )
            return redirect('album_view', id=id)
    else:
        form = ImagesForm()

    context = {
        'album': album,
        'photos': photos,
        'form': form
    }
    return render(request, 'albumview.html', context)

from django.shortcuts import get_object_or_404, redirect
from .models import Albums, Photo


def delete_album(request, id):
    logined, email = verifyLogin(request)
    if logined:
        try:
            user = Customers.objects.get(email=email)
            album = get_object_or_404(Albums, id=id, user=user)  
            
            album.delete() 
            
           
            media_folder = os.path.join(settings.MEDIA_ROOT, album.code)
            print(media_folder)
            if os.path.exists(media_folder):
                shutil.rmtree(media_folder)  

            messages.success(request, 'Album deleted successfully.')
            return redirect('dashboard')
        except Exception as e:
            print(f'Error deleting albredirectdashboardum: {e}')
            messages.error(request, 'An error occurred while deleting the album.')
            return redirect('dashboard')
    else:
        return redirect('signup')


def delete_photo(request, id, pid):
  
    album = get_object_or_404(Albums, code=id)
    photo = get_object_or_404(Photo,id=pid)
    filename = photo.images.name.split('/')[-1]
   
    file_path = os.path.join(settings.MEDIA_ROOT, f'{id}\{filename}')
    
    
    photo = get_object_or_404(Photo, album=album, images=photo.images.name)
    print('file:',file_path)
   
    if os.path.isfile(file_path):
        print(file_path)
        os.remove(file_path)
        print('Deleted')
    
    
    photo.delete()
    
    
    return redirect('album_view', id=id) 

def imageupload(request,id):
    form = ImagesForm(request.POST, request.FILES)
    if request.method == 'POST':
        album = Albums.objects.get(code=id)
        
        user = album.user
        images = request.FILES.getlist('images')
        for image in images:

            image_ins = Photo.objects.create(
                album = album,
                uploaded_by = user
            )
            image_ins.save()
        return redirect(f'album/{id}')
    context = {'form': form}
    return render(request, "upload.html", context)


def Fav_albums(request, id):
    logined, email = verifyLogin(request)

    user = get_object_or_404(Customers, email=email)  
    album = get_object_or_404(Albums, code=id)  
   
    if FavAlbums.objects.filter(user=user, album=album).exists():
        FavAlbums.objects.filter(user=user, album=album).delete()  
    else:
        FavAlbums.objects.create(user=user, album=album)  

    return redirect('album_view', id=id)  

    
def EditAlbum(request,id):
    album = Albums.objects.get(code=id)
    if request.POST:
        name = request.POST.get('name')
        share = request.POST.get('share')
        if share == 'on':
            share = True
        else:
            share = False
        Album = Albums.objects.get(code=id)
        Album.name = name
        Album.share = share
        Album.save()
        return redirect('album_view',id=id)
    context = {
        'album' : album
    }
    return render(request, 'albumedit.html', context)