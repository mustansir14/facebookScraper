class Profile:

    def __init__(self):

        self.username = None
        self.about = None
        self.no_of_followers = None
        self.no_of_likes = None
        self.category = None
        self.email = None
        self.phone = None
        self.status = None
        self.log = None
        self.posts = []
        self.products = []

    def __str__(self):

        return_string = ""
        if self.username:
            return_string += "Username: " + self.username + "\n"
        if self.about:
            return_string += "About: " + self.about + "\n"
        if self.no_of_likes:
            return_string += "Likes: " + str(self.no_of_likes) + "\n"
        if self.no_of_followers:
            return_string += "Followers: " + str(self.no_of_followers) + "\n"
        if self.category:
            return_string += "Category: " + self.category + "\n"
        if self.email:
            return_string += "Email: " + self.email + "\n"
        if self.phone:
            return_string += "Phone: " + self.phone + "\n"

        return return_string

class Post:

    def __init__(self) -> None:
        
        self.id = None
        self.username = None
        self.date_posted = None
        self.caption = None
        self.no_of_likes = None
        self.is_video = None
        self.no_of_views = None
        self.media_path = None
        self.status = None
        self.log = None

    def __str__(self) -> str:
        
        return_string = ""
        if self.id:
            return_string += "ID: " + str(self.id) + "\n"
        if self.username:
            return_string += "Username: " + self.username + "\n"
        if self.date_posted:
            return_string += "Date Posted: " + str(self.date_posted) + "\n"
        if self.caption:
            return_string += "Caption: " + self.caption + "\n"
        if self.no_of_likes:
            return_string += "Likes: " + str(self.no_of_likes) + "\n"
        if self.is_video is not None:
            return_string += "Is Video: " + str(self.is_video) + "\n"
        if self.no_of_views:
            return_string += "Views: " + str(self.no_of_views) + "\n"
        if self.media_path:
            return_string += "Media Path: " + str(self.media_path) + "\n"

        return return_string


class Product:

    def __init__(self) -> None:

        self.id = None
        self.username = None
        self.description = None
        self.price = None
        self.currency = None
        self.media_path = None
        self.status = None
        self.log = None

    def __str__(self) -> str:
        
        return_string = ""
        if self.id:
            return_string += "ID: " + str(self.id) + "\n"
        if self.username:
            return_string += "Username: " + self.username + "\n"
        if self.description:
            return_string += "Description: " + self.description + "\n"
        if self.price:
            return_string += "Price: " + str(self.price) + "\n"
        if self.currency:
            return_string += "Currency: " + self.currency + "\n"
        if self.media_path:
            return_string += "Media Path: " + self.media_path + "\n"

        return return_string