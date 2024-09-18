from django.shortcuts import render, redirect
from .models import Customers
from .forms import UsersLoginForm, SignupForm
from django.contrib import messages
from django.shortcuts import render, redirect,HttpResponse,get_object_or_404
from django.contrib import messages
from .models import Customers,Albums,Photo
from django.contrib.auth.decorators import login_required
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
                        response = redirect('dashboard')  # Redirect to dashboard view
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
    return render(request, "login.html", {'form': frm})

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

@login_required
def albumcreation(request):
    logined, email = verifyLogin(request)
    if logined:
        if request.method == 'POST':
            frm = AlbumCreations(request.POST)
            if frm.is_valid():
                album_name = request.POST.get('name')
                album_share = request.POST.get('share')
                if album_share == 'on' : album_share = True
                else: album_share = True
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
                    
                    return redirect('album/', id=code)  # Redirect to the album view page
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
    
@login_required
def album_view(request, id):

    # Fetch the album and its photos
    album = get_object_or_404(Albums, code=id)
    photos = album.photos.all()  # Get all photos related to the album
    form = ImagesForm()
    context = {
        'album': album,
        'photos': photos,
        #r'imagename':photos.images.split('/')[-1],
        'form':form
    }
    for photo in photos:
        print(photo.images)
        
        
    return render(request, 'albumview.html', context)

@login_required
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

@login_required
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

@login_required
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
