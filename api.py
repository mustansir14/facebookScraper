from flask import Flask, json, request
from FacebookScraper import FacebookScraper
from includes.DB import DB
from config import *
from multiprocessing import Process
import logging
from sys import platform
import requests
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)

api = Flask(__name__)

@api.route('/api/v1/scrape/profile', methods=['GET'])
def grab_company():

    def scrape_company(company_id, webhook_url, is_sync):

        try:
            scraper = FacebookScraper()
            profile = scraper.scrape_profile(company_id)
            
            status = profile.status
            log = profile.log
            if profile.status == "success":
                for post in profile.posts:
                    if post.status == "error":
                        status = "error"
                        log = "Error in scraping some of the posts"
                for product in profile.products:
                    if product.status == "error":
                        status = "error"
                        log = "Error in scraping some of the products"
            
            scraper.kill_chrome()
                        
            if is_sync == False:
                if status == "success":
                    requests.post(webhook_url, json={"url": company_id, "status" : "success"})
                else:
                    requests.post(webhook_url, json={"url": company_id, "status" : status, "log": log})
            else:
                if status == "success":
                    return {"status": "success", "data": f"{profile.username} profile with {len(profile.posts)} posts and {len(profile.products)} products."}
                else:
                    return {"status": status, "log": log}

        except Exception as e:
            try:
                scraper.kill_chrome()
            except:
                pass
            return {"status": "error", "log": str(e)}

    if "url" not in request.args:
        return {"status": "error", "message": "missing url argument"}
    if "sync" not in request.args and "webhookUrl" not in request.args:
        return {"status": "error", "message": "missing webhookUrl or sync=1"}
    if "webhookUrl" not in request.args:
        webhook = None
    else:
        webhook = request.args["webhookUrl"]
    
    try:
        if "sync" not in request.args and ( platform == "linux" or platform == "linux2" ):
            p = Process(target=scrape_company, args=(request.args["id"], webhook, False, ))
            p.start()
            return {"status": "pending", "message": f"Request recieved to scrape profile with url {request.args['url']}"}
        else:
            return scrape_company(request.args["id"], webhook, "sync" in request.args )
    except Exception as e:
        logging.error(str(e))
        return {"status": "error", "message": str(e)}


@api.route('/api/v1/scrape/photo', methods=['GET'])
def grab_photo():

    def scrape_photo(photo_id, username, webhook_url, is_sync):

        try:
            scraper = FacebookScraper()
            post = scraper.scrape_photos(f"https://www.facebook.com/{username}", username=username, scrape_specific_photo=photo_id)
            status = post.status
            log = post.log
            scraper.kill_chrome()
                        
            if is_sync == False:
                if status == "success":
                    requests.post(webhook_url, json={"id": photo_id, "status" : "success"})
                else:
                    requests.post(webhook_url, json={"id": photo_id, "status" : status, "log": log})
            else:
                if status == "success":
                    return {"id": photo_id, "status": "success"}
                else:
                    return {"id": photo_id, "status": status, "log": log}

        except Exception as e:
            try:
                scraper.kill_chrome()
            except:
                pass
            return {"id": photo_id, "status": "error", "log": str(e)}

    if "id" not in request.args:
        return {"status": "error", "message": "missing id argument"}
    if "sync" not in request.args and "webhookUrl" not in request.args:
        return {"status": "error", "message": "missing webhookUrl or sync=1"}
    if "webhookUrl" not in request.args:
        webhook = None
    else:
        webhook = request.args["webhookUrl"]
 
    db = DB(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    db.cur.execute("SELECT username from post where id = %s;", (request.args["id"], ))
    results = db.cur.fetchall()
    if not results:
        return {"status": "error", "message": "No post found with given id"}
    username = results[0][0]
    
    try:
        if "sync" not in request.args and ( platform == "linux" or platform == "linux2" ):
            p = Process(target=scrape_photo, args=(request.args["id"], username, webhook, False, ))
            p.start()
            return {"status": "pending", "message": f"Request recieved to scrape photo with id {request.args['id']}"}
        else:
            return scrape_photo(request.args["id"], username, webhook, "sync" in request.args )
    except Exception as e:
        logging.error(str(e))
        return {"id": request.args["id"], "status": "error", "message": str(e)}


@api.route('/api/v1/scrape/video', methods=['GET'])
def grab_video():

    def scrape_video(video_id, username, webhook_url, is_sync):

        try:
            scraper = FacebookScraper()
            post = scraper.scrape_videos(f"https://www.facebook.com/{username}", username=username, scrape_specific_video=video_id)
            status = post.status
            log = post.log
            scraper.kill_chrome()
                        
            if is_sync == False:
                if status == "success":
                    requests.post(webhook_url, json={"id": video_id, "status" : "success"})
                else:
                    requests.post(webhook_url, json={"id": video_id, "status" : status, "log": log})
            else:
                if status == "success":
                    return {"id": video_id, "status": "success"}
                else:
                    return {"id": video_id, "status": status, "log": log}

        except Exception as e:
            try:
                scraper.kill_chrome()
            except:
                pass
            return {"id": video_id, "status": "error", "log": str(e)}

    if "id" not in request.args:
        return {"status": "error", "message": "missing id argument"}
    if "sync" not in request.args and "webhookUrl" not in request.args:
        return {"status": "error", "message": "missing webhookUrl or sync=1"}
    if "webhookUrl" not in request.args:
        webhook = None
    else:
        webhook = request.args["webhookUrl"]
 
    db = DB(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    db.cur.execute("SELECT username from post where id = %s;", (request.args["id"], ))
    results = db.cur.fetchall()
    if not results:
        return {"status": "error", "message": "No post found with given id"}
    username = results[0][0]
    
    try:
        if "sync" not in request.args and ( platform == "linux" or platform == "linux2" ):
            p = Process(target=scrape_video, args=(request.args["id"], username, webhook, False, ))
            p.start()
            return {"status": "pending", "message": f"Request recieved to scrape video with id {request.args['id']}"}
        else:
            return scrape_video(request.args["id"], username, webhook, "sync" in request.args )
    except Exception as e:
        logging.error(str(e))
        return {"id": request.args["id"], "status": "error", "message": str(e)}


@api.route('/api/v1/scrape/product', methods=['GET'])
def grab_product():

    def scrape_product(product_id, username, webhook_url, is_sync):

        try:
            scraper = FacebookScraper()
            post = scraper.scrape_products(f"https://www.facebook.com/{username}", username=username, scrape_specific_product=product_id)
            status = post.status
            log = post.log
            scraper.kill_chrome()
                        
            if is_sync == False:
                if status == "success":
                    requests.post(webhook_url, json={"id": product_id, "status" : "success"})
                else:
                    requests.post(webhook_url, json={"id": product_id, "status" : status, "log": log})
            else:
                if status == "success":
                    return {"id": product_id, "status": "success"}
                else:
                    return {"id": product_id, "status": status, "log": log}

        except Exception as e:
            try:
                scraper.kill_chrome()
            except:
                pass
            return {"id": product_id, "status": "error", "log": str(e)}

    if "id" not in request.args:
        return {"status": "error", "message": "missing id argument"}
    if "sync" not in request.args and "webhookUrl" not in request.args:
        return {"status": "error", "message": "missing webhookUrl or sync=1"}
    if "webhookUrl" not in request.args:
        webhook = None
    else:
        webhook = request.args["webhookUrl"]
 
    db = DB(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    db.cur.execute("SELECT username from product where id = %s;", (request.args["id"], ))
    results = db.cur.fetchall()
    if not results:
        return {"status": "error", "message": "No product found with given id"}
    username = results[0][0]
    
    try:
        if "sync" not in request.args and ( platform == "linux" or platform == "linux2" ):
            p = Process(target=scrape_product, args=(request.args["id"], username, webhook, False, ))
            p.start()
            return {"status": "pending", "message": f"Request recieved to scrape product with id {request.args['id']}"}
        else:
            return scrape_product(request.args["id"], username, webhook, "sync" in request.args )
    except Exception as e:
        logging.error(str(e))
        return {"id": request.args["id"], "status": "error", "message": str(e)}
    
if __name__ == "__main__":
    api.run()