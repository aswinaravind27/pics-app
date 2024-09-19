from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import urlencode
from .models import Customers
from .forms import UsersLoginForm, SignupForm
from django.contrib import messages
from django.shortcuts import render, redirect,HttpResponse,get_object_or_404,HttpResponseRedirect
from django.contrib import messages
from .models import Customers,Albums,Photo
from .forms import UsersLoginForm,AlbumCreations
import uuid,os
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from .forms import UsersLoginForm,ImagesForm
# Create your views here.
def dashboard(request):
    logined,email = verifyLogin(request)
    print(logined)
    if logined:
        # Render the dashboard template if the user is authenticated
        user = Customers.objects.get(email=email)
        albums = Albums.objects.filter(user=user) 
        context ={
            'albums' : albums
        }
    #return render(request, 'dashboard.html', context)
        return render(request, 'dashboard.html',context) 
    else:
        
        return redirect('signup')  

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()
            return redirect('login')  # Redirect to login page
    else:
        form = SignupForm()
    return render(request, 'sign-up.html', {'form': form})

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
                        # Authenticate and log in the user
                        print('logined')
                        if next_url:

                            response = HttpResponseRedirect(next_url)  # Redirect to dashboard view
                            response.set_cookie('logined', [True,email])  # Set the cookie
                            
                            return response
                        else:
                            response = redirect('dashboard') # Redirect to dashboard view
                            response.set_cookie('logined', [True,email])  # Set the cookie
                            
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
                # Generate a unique code for the album
                code = str(uuid.uuid4())
                
                try:
                    # Create and save the album
                    album = Albums.objects.create(
                        name=album_name,
                        path=f'{code}\\',
                        user=Customers.objects.get(email=email),  # Fetch user using email
                        share=album_share,
                        code=code
                    )
                    
                    # Create the media folder
                    media_folder = os.path.join(settings.MEDIA_ROOT, code)
                    os.makedirs(media_folder, exist_ok=True)
                    
                    return redirect('dashboard')  # Redirect to the album view page
                except Exception as e:
                    # Handle any exceptions
                    print(f'Error creating album: {e}')
                    messages.error(request, 'An error occurred while creating the album.')
        else:
            frm = AlbumCreations()
        
        return render(request, 'albumcreate.html', {'form': frm})
    else:
        return redirect('signup')


# def dashboard(request):
    
get_object_or_404


def logout(request):
    
    response = redirect('/')  # Redirect to a home page or login page after logout
    response.delete_cookie('logined')  # Remove the 'logined' cookie
    print('logout')
    return response

def album_view(request, id):
    album = get_object_or_404(Albums, code=id)
    photos = album.photos.all()
    form = ImagesForm()
    logind, email = verifyLogin(request)
    path = request.get_full_path()
    login_url = reverse('login')
    next_url = f"{login_url}?{urlencode({'next': path})}"
    
    def check_ownership(id, email):
        albumid = id
        aldetails = Albums.objects.get(code=albumid)
        ownerid = aldetails.user_id
        ownerdetails = get_object_or_404(Customers, id=ownerid)
        try:
            ownermail = ownerdetails.email
            return ownermail == email
        except:
            return False

    context = {
        'album': album,
        'photos': photos,
        'form': form,
        'logined': logind,
        'owner': check_ownership(id, email),
        'path': next_url  # Pass the correctly constructed URL
    }
    return render(request, 'albumview.html', context)

def upload_photos(request, id):
    album = get_object_or_404(Albums, code=id)
    photos = album.photos.all()

    if request.method == 'POST':
        form = ImagesForm(request.POST, request.FILES)
        print("Form errors:", form.errors)  # Print form errors for debugging
        print("FILES data:", request.FILES)  # Print uploaded files data for debugging
        
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
            return redirect('album', id=id)
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
            album = get_object_or_404(Albums, id=id, user=user)  # Ensure the user owns the album
            
            album.delete()  # Delete the album
            
            # Optionally, delete the media folder
            media_folder = os.path.join(settings.MEDIA_ROOT, album.code)
            if os.path.exists(media_folder):
                os.rmdir(media_folder)  # This will only work if the folder is empty

            messages.success(request, 'Album deleted successfully.')
            return redirect('dashboard')
        except Exception as e:
            print(f'Error deleting albredirectdashboardum: {e}')
            messages.error(request, 'An error occurred while deleting the album.')
            return redirect('dashboard')
    else:
        return redirect('signup')


def delete_photo(request, id, pid):
    # Get the album based on the ID
    album = get_object_or_404(Albums, code=id)
    photo = get_object_or_404(Photo,id=pid)
    filename = photo.images.name.split('/')[-1]
    # Construct the full path of the file
    file_path = os.path.join(settings.MEDIA_ROOT, f'{id}\{filename}')
    
    # Get the photo record
    photo = get_object_or_404(Photo, album=album, images=photo.images.name)
    print('file:',file_path)
    # Remove the file from the filesystem
    if os.path.isfile(file_path):
        print(file_path)
        os.remove(file_path)
        print('Deleted')
    
    # Delete the photo record from the database
    photo.delete()
    
    # Redirect to the album view page
    return redirect('album', id=id)  # Adjust redirection as needed

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
