
# Pixora

**Pixora** is a Django-based photo-sharing web application that allows users to create, manage, and share photo albums. It includes user authentication, album management, and features like marking albums as favorites.
![Logo](static/images/logo.png)
## Features
- **User Authentication**: Signup, login, and logout functionalities.
- **Album Management**: Create, edit, delete albums.
- **Photo Upload**: Upload photos to specific albums.
- **Favorite Albums**: Users can mark albums as favorites for quick access.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AaronShenny/pixora.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Start the development server:
   ```bash
   python manage.py runserver
   ```
# NOTE : In pixora/settings.py, change your database according to your preference.
## Usage

- Visit `http://127.0.0.1:8000/` to access the app.
- Sign up and create new albums.
- Upload photos to your albums.
- Share albums using a unique code or link.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request.

## License

This project is licensed under the MIT License.

---

### Breakdown of MAIN Functions:
---
### pics/views.py
---
#### 1. **`index()`**
   - **Purpose**: Renders the home page and displays user albums if they are logged in.
   - **Details**:
     - `verifyLogin(request)`: Verifies if a user is logged in.
     - If `logined` is `True`, fetches the user’s albums and favorite albums.
     - Context dictionary is used to pass data (like `albums`, `fav`) to the `index.html` template.

#### 2. **`dashboard()`**
   - **Purpose**: Displays the user dashboard with their albums and favorited albums.
   - **Details**:
     - Uses `verifyLogin()` to check login status.
     - Fetches user-specific albums and favorites, then renders `dashboard.html`.
     - Redirects to the login page if not logged in.

#### 3. **`signup()`**
   - **Purpose**: Handles new user registration.
   - **Details**:
     - On `POST`, validates the `SignupForm` and creates a new user.
     - Uses `set_password()` to hash the password before saving.
     - Redirects users to the login page upon successful signup.

#### 4. **`login()`**
   - **Purpose**: Manages user login.
   - **Details**:
     - Retrieves `next_url` for post-login redirection.
     - Validates login form and checks user credentials (`email` and `password`).
     - Sets a cookie with login status (`logined`) upon successful login.
     - Provides user feedback using Django messages for incorrect credentials.

#### 5. **`verifyLogin()`**
   - **Purpose**: Checks if a user is logged in using cookies.
   - **Details**:
     - Extracts and evaluates the `logined` cookie.
     - Returns a tuple (`logined`, `email`).
     - Handles cases where the cookie is not set.

#### 6. **`albumcreation()`**
   - **Purpose**: Allows logged-in users to create a new album.
   - **Details**:
     - Validates the form for album creation.
     - Generates a unique `uuid` for each album.
     - Saves the album details and creates a directory for media uploads.
     - Uses `os.makedirs` to create a folder for storing album photos.

#### 7. **`logout()`**
   - **Purpose**: Logs out the user.
   - **Details**:
     - Redirects to the homepage and deletes the `logined` cookie.

#### 8. **`album_view()`**
   - **Purpose**: Displays the contents of a specific album.
   - **Details**:
     - Fetches the album by its `code` using `get_object_or_404`.
     - Retrieves all photos associated with the album.
     - Uses `check_ownership()` to determine if the current user is the album owner.
     - Passes data to `albumview.html` including ownership status and favorited status.

#### 9. **`upload_photos()`**
   - **Purpose**: Handles photo uploads to a specific album.
   - **Details**:
     - Uses `ImagesForm` to accept image uploads.
     - Processes uploaded images in a loop and associates them with the specified album.
     - Redirects back to the album view after uploading.

#### 10. **`delete_album()`**
   - **Purpose**: Deletes a specific album and its associated media.
   - **Details**:
     - Verifies login status and user ownership of the album.
     - Uses `shutil.rmtree` to delete the album folder from the filesystem.
     - Displays success or error messages and redirects to the dashboard.

#### 11. **`delete_photo()`**
   - **Purpose**: Removes a specific photo from an album.
   - **Details**:
     - Retrieves the photo by its `id` and deletes it from the album.
     - Deletes the physical image file from the server using `os.remove`.

#### 12. **`imageupload()`**
   - **Purpose**: Allows batch upload of images to an album.
   - **Details**:
     - Iterates over uploaded images and saves them to the specified album.
     - Redirects to the album view page after completion.

#### 13. **`Fav_albums()`**
   - **Purpose**: Toggles the favorite status of an album for a user.
   - **Details**:
     - Checks if the album is already favorited by the user.
     - Adds or removes the album from `FavAlbums` accordingly.
     - Redirects back to the album view.

#### 14. **`EditAlbum()`**
   - **Purpose**: Edits the details of an existing album.
   - **Details**:
     - Allows changing the album’s name and share status.
     - Saves the updated details and redirects back to the album view.
---
### pics/forms.py
---

### Explanation of `forms.py`:

#### 1. **Imports**:
   - `ModelForm`: A Django form class that automatically connects a form to a model, making it easier to create and update database entries.
   - `Customers`, `Albums`, `Photo`: Models from your app, used for form validation and input handling.
   - `forms`: Provides various form fields like `CharField`, `EmailField`, and `FileField`.
   - `ValidationError`: Used to raise custom validation errors for input.

#### 2. **`UsersLoginForm`**:
   - **Purpose**: Handles user login.
   - **Fields**:
     - `password`: A `CharField` using `PasswordInput` to mask input.
       - Attributes include `class` for CSS styling, `placeholder` for input hints, and `required` to enforce input.
     - `email`: An `EmailField` with similar attributes.
   - **Meta**:
     - Specifies the `Customers` model and includes `email` and `password` as fields.
     - Automatically links form validation to the `Customers` model.

#### 3. **`SignupForm`**:
   - **Purpose**: Manages new user registration.
   - **Fields**:
     - `name`: A `CharField` for the user’s name.
   - **Meta**:
     - Uses the `Customers` model and includes all fields (`__all__`).
   - **Method**: `clean_email()`
     - Custom validation to check if the email already exists in the database.
     - Raises a `ValidationError` if the email is already registered.

#### 4. **`AlbumCreations`**:
   - **Purpose**: Handles album creation input.
   - **Meta**:
     - Uses the `Albums` model.
     - Specifies `name` and `share` as fields to manage album details.

#### 5. **`ImagesForm`**:
   - **Purpose**: Manages image uploads to albums.
   - **Fields**:
     - `images`: Uses `FileField` to allow users to upload image files.
     - Uses `ClearableFileInput` widget to allow users to manage uploaded files.
     - Set as `required=False` to make image uploads optional.

---

These forms streamline user interactions by handling input validation, displaying form fields, and connecting user inputs to the database models. If you need a deeper dive into any part of this file, let me know!
