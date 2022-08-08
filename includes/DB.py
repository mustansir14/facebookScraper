import mariadb
from includes.models import *
from datetime import datetime
import logging

class DB:

    def __init__(self, host, username, password, db_name) -> None:

        self.con = mariadb.connect(host=host, user=username, password=password, db=db_name)
        self.cur = self.con.cursor()

    def insert_or_update_profile(self, profile : Profile):
        
        sql = """INSERT INTO profile (username, about, category, no_of_likes, no_of_followers, 
        email, phone, date_inserted, date_updated, status, log) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 
        %s, %s) ON DUPLICATE KEY UPDATE about=%s, category=%s, no_of_likes=%s, no_of_followers=%s, email=%s,
        phone=%s, date_updated=%s, status=%s, log=%s;"""
        args = (profile.username, profile.about, profile.category, profile.no_of_likes, 
        profile.no_of_followers, profile.email, profile.phone, datetime.now(), datetime.now(), profile.status, 
        profile.log, profile.about, profile.category, profile.no_of_likes, profile.no_of_followers, 
        profile.email, profile.phone, datetime.now(), profile.status, profile.log)
        try:
            self.cur.execute(sql, args)
            logging.info(f"Profile {profile.username} added/updated to DB.")
            self.con.commit()
        except Exception as e:
            logging.error(f"Error saving profile {profile.username} to DB. {str(e)}")

    def insert_or_update_post(self, post: Post):

        sql = """INSERT INTO post (id, username, date_posted, caption, no_of_likes, no_of_views, is_video, 
        media_path, date_inserted, date_updated, status, log) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s) ON DUPLICATE KEY UPDATE username=%s, date_posted=%s, caption=%s, no_of_likes=%s, no_of_views=%s,
        is_video=%s, media_path=%s, date_updated=%s, status=%s, log=%s;"""
        args = (post.id, post.username, post.date_posted, post.caption, post.no_of_likes, post.no_of_views,
        post.is_video, post.media_path, datetime.now(), datetime.now(), post.status, 
        post.log, post.username, post.date_posted, post.caption, post.no_of_likes, post.no_of_views,
        post.is_video, post.media_path, datetime.now(), post.status, post.log, )
        try:
            self.cur.execute(sql, args)
            logging.info(f"Post {post.id} for profile: {post.username} added/updated to DB.")
            self.con.commit()
        except Exception as e:
            logging.error(f"Error saving Post {post.id} for profile: {post.username} to DB. {str(e)}")

    def insert_or_update_product(self, product: Product):

        sql = """INSERT INTO product (id, username, description, price, currency, media_path, status, log,
        date_inserted, date_updated) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE 
        username=%s, description=%s, price=%s, currency=%s, media_path=%s, date_updated=%s, status=%s, log=%s;"""
        args = (product.id, product.username, product.description, product.price, product.currency, 
        product.media_path, product.status, product.log, datetime.now(), datetime.now(), product.username, 
        product.description, product.price, product.currency, product.media_path, datetime.now(), 
        product.status, product.log, )
        try:
            self.cur.execute(sql, args)
            logging.info(f"Product {product.id} for profile: {product.username} added/updated to DB.")
            self.con.commit()
        except Exception as e:
            logging.error(f"Error saving product {product.id} for profile: {product.username} to DB. {str(e)}")

