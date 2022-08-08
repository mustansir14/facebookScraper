##########################################
# Coded by Mustansir Muzaffar
# mustansir2001@gmail.com
# +923333487952
##########################################

from datetime import datetime, timedelta, date
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import urllib.request
import os, logging, sys, argparse
from sys import platform
from multiprocessing import Process, Queue
from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER, FILES_DIR, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS
from includes.DB import DB
from includes.models import *
from includes.Reporter import Reporter

class FacebookScraper:

    def __init__(self, use_db=True) -> None:
        
        options = Options()
        options.headless = True
        options.add_argument("window-size=1920,1080")
        options.add_argument("--log-level=3")
        options.add_argument("--no-sandbox")
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--renderer-process-limit=1'); # do not allow take more resources
        options.add_argument('--disable-crash-reporter'); # disable crash reporter process
        options.add_argument('--no-zygote'); # disable zygote process
        options.add_argument('--disable-crashpad')
        options.add_argument('--grabber-facebook-mustansir')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36")
        self.driver = webdriver.Chrome(options=options, executable_path=ChromeDriverManager().install())
        os.makedirs("file/post/image", exist_ok=True)
        os.makedirs("file/post/video", exist_ok=True)
        os.makedirs("file/product/image", exist_ok=True)
        self.use_db = use_db
        if use_db:
            self.db = DB(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        self.reporter = Reporter(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS)

    def scrape_profile(self, url, photos=True, videos=True, products=True) -> Profile:

        logging.info("Scraping Profile: " + url)
        self.driver.get(url)
        profile = Profile()
        try:
            subline = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.lr9zc1uh.a5q79mjw.g1cxx5fr.b1v8xokw.m9osqain"))).text.split("·")
        except Exception as e:
            profile.status = "error"
            profile.log = "Error for " + url + ": " + str(e)
            logging.error(profile.log)
            self.reporter.error(profile.log)
            return profile
        profile.username = subline[0].strip().lstrip("@")
        if len(subline) > 1:
            profile.category = subline[1].strip()
        try:
            see_more_button = self.driver.find_element_by_class_name('oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.gpro0wi8.oo9gr5id.lrazzd5p')
            if see_more_button.text.strip().lower() == "see more":
                see_more_button.click()
        except:
            pass
        lines = self.driver.find_elements_by_class_name("rq0escxv.l9j0dhe7.du4w35lb.j83agx80.cbu4d94t.d2edcug0.hpfvmrgz.rj1gh0hx.buofh1pr.g5gj957u.o8rfisnq.p8fzw8mz.pcp91wgn.iuny7tx3.ipjc6fyt")
        for line in lines:
            line_text = line.text.strip()
            if profile.about is None:
                try:
                    profile.about = line.find_element_by_class_name("kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.c1et5uql").text.rstrip("See less").strip()
                except:
                    pass
            if "people like this" in line_text:
                profile.no_of_likes = int(line_text.rstrip("people like this").strip().replace(",", ""))
            elif "people follow this" in line_text:
                profile.no_of_followers = int(line_text.rstrip("people follow this").strip().replace(",", ""))
            elif "@" in line_text and "." in line_text and "\n" not in line_text and len(line_text) < 50:
                profile.email = line_text
            elif line_text and line_text[0] == "+" and line_text[1:].replace(" ", "").replace("-", "").isnumeric():
                profile.phone = line_text.replace(" ", "").replace("-", "")

        if not profile.status:
            profile.status = "success"

        if self.use_db:
            self.db.insert_or_update_profile(profile)


        if photos:
            profile.posts = self.scrape_photos(url, profile.username)
        if videos:
            profile.posts += self.scrape_videos(url, profile.username)
        if products:
            profile.products = self.scrape_products(url, profile.username)
        return profile

    
    def scrape_photos(self, url, username=None, scrape_specific_photo=None):

        photos_url = url.rstrip("/") + "/photos/?ref=page_internal"
        self.driver.get(photos_url)
        images = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "aodizinl.hv4rvrfc.ihqw7lf3.dati1w0a"))).find_elements_by_tag_name("a")
        image_posts = []
        for image in images:
            post = Post()
            post.id = image.get_attribute("href").rstrip("/").split("/")[-1]
            if scrape_specific_photo and post.id != scrape_specific_photo:
                continue
            self.driver.execute_script("arguments[0].click();", image)
            img = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ji94ytn4.d2edcug0.r9f5tntg.r0294ipz")))
            if not username:
                post.username = self.driver.current_url.split("/photos")[0].split("/")[-1]
            else:
                post.username = username
            try:
                logging.info("Scraping Photo %s for %s" % (post.id, username))
                post.is_video=False
                image_source = img.get_attribute("src")
                post.media_path = FILES_DIR.rstrip("/") + "/post/image/" + str(post.id) + ".jpg"
                res = requests.get(image_source)
                with open(post.media_path, "wb") as f:
                    f.write(res.content)
                post.caption = self.driver.find_element_by_class_name("a8nywdso.j7796vcc.rz4wbd8a.l29c1vbm").text
                post.caption = " ".join(filter(lambda x:x[0]!='#' or x[0] != '@', post.caption.split()))
                post.no_of_likes = 0
                likes_string = None
                try:
                    likes_string = self.driver.find_element_by_class_name("bzsjyuwj.ni8dbmo4.stjgntxs.ltmttdrg.gjzvkazv").text.replace(",", "")
                    post.no_of_likes = int(likes_string)
                except:
                    if likes_string:
                        number = likes_string[:-1]
                        if "." in number:
                            point_index = number.index(".")
                            number = number[:point_index]
                        if likes_string[-1] == "K":
                            post.no_of_likes = int(number)*1000
                            if "." in likes_string:
                                post.no_of_likes += int(likes_string[point_index+1:-1])*100
                        elif likes_string[-1] == "M":
                            post.no_of_likes = int(number)*1000000
                            if "." in likes_string:
                                post.no_of_likes += int(likes_string[point_index+1:-1])*100000
                date_text = self.driver.find_element_by_class_name("oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.gmql0nx0.gpro0wi8.b1v8xokw").text
                date_text_split = date_text.split()
                if len(date_text_split) == 4 and "at" in date_text and ":" in date_text:
                    post.date_posted = datetime.strptime(" ".join(date_text_split[:2]) + " " + str(datetime.now().year) + " " + date_text_split[3], "%d %B %Y %H:%M")
                elif len(date_text_split) == 3 and date_text_split[0].lower() == "yesterday":
                    post.date_posted = datetime.strptime(str((date.today() - timedelta(days=1))) + " " + date_text_split[2], "%Y-%m-%d %H:%M")
                elif len(date_text_split) > 3:
                    post.date_posted = datetime.strptime(" ".join(date_text_split[:2]) + " " + str(datetime.now().year), "%B %d %Y")
                elif len(date_text_split) == 3:
                    try:
                        post.date_posted = datetime.strptime(date_text, "%d %B %Y")
                    except:
                        post.date_posted = datetime.strptime(date_text, "%B %d %Y")
                elif len(date_text_split) == 2:
                    if date_text.lower() == "just now":
                        post.date_posted = datetime.now()
                    elif date_text_split[1] == "hrs":
                        post.date_posted = datetime.now() - timedelta(hours=int(date_text_split[0]))
                    else:
                        try:
                            post.date_posted = datetime.strptime(date_text + " " + str(datetime.now().year), "%d %B %Y")
                        except:
                            post.date_posted = datetime.strptime(date_text + " " + str(datetime.now().year), "%B %d %Y")
                elif len(date_text_split) == 1:
                    if date_text[-1] == "m":
                        minutes = int(date_text[:-1])
                        post.date_posted = datetime.now() - timedelta(minutes=minutes)
                    elif date_text[-1] == "h":
                        hours = int(date_text[:-1])
                        post.date_posted = datetime.now() - timedelta(hours=hours)
                    elif date_text[-1] == 's':
                        seconds = int(date_text[:-1])
                        post.date_posted = datetime.now() - timedelta(seconds=seconds)
                post.status = "success"
            except Exception as e:
                post.status = "error"
                post.log = str(e)
                logging.error(str(e))
                self.reporter.error(f"Error scraping photo {post.id} for {username}: {str(e)}")
            image_posts.append(post)
            if self.use_db:
                self.db.insert_or_update_post(post)
            if self.driver.current_url != photos_url:
                self.driver.back()
            if scrape_specific_photo:
                return post
        return image_posts

    
    def scrape_videos(self, url, username=None, scrape_specific_video=None):

        videos_url = url.rstrip("/") + "/videos/?ref=page_internal"
        self.driver.get(videos_url)
        videos = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "j83agx80.l9j0dhe7.k4urcfbm"))).find_elements_by_tag_name("a")
        video_urls = []
        for video in videos:
            url = video.get_attribute("href")
            if url not in video_urls:
                video_urls.append(url)
        video_posts = []
        for video_url in video_urls:
            post = Post()
            post.id = video_url.rstrip("/").split("/")[-1]
            if scrape_specific_video and post.id != scrape_specific_video:
                continue
            self.driver.get(video_url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "hv4rvrfc.dati1w0a.discj3wi")))
            try:
                buttons = self.driver.find_elements_by_class_name("oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.gpro0wi8.oo9gr5id.lrazzd5p")
                for button in buttons:
                    if button.text.strip().lower() == "see more":
                        self.driver.execute_script("arguments[0].click();", button)
                        break
            except:
                pass
            if not username:
                post.username = self.driver.current_url.split("/videos")[0].split("/")[-1]
            else:
                post.username = username
            try:
                logging.info("Scraping Video %s for %s" % (post.id, username))
                post.is_video=True
                try:
                    video_source = self.driver.find_element_by_xpath('//meta[@property="og:video:url"]').get_attribute("content")
                except:
                    logging.info("Video not available. Skipping...")
                    continue
                post.media_path = FILES_DIR.rstrip("/") + "/post/video/" + str(post.id) + ".mp4"
                if not os.path.isfile(post.media_path):
                    urllib.request.urlretrieve(video_source, post.media_path)
                try:
                    post.caption = self.driver.find_element_by_class_name("e5nlhep0.nu4hu5il.eg9m0zos").text
                    post.caption = " ".join(filter(lambda x:x[0]!='#' or x[0] != '@', post.caption.split()))
                except:
                    pass

                post.no_of_likes = 0
                likes_string = None
                try:
                    likes_string = self.driver.find_element_by_class_name("gpro0wi8.g5ia77u1.bzsjyuwj.hcukyx3x.ni8dbmo4.stjgntxs.ltmttdrg.g0qnabr5").text.replace(",", "")
                    post.no_of_likes = int(likes_string)
                except:
                    if likes_string:
                        number = likes_string[:-1]
                        if "." in number:
                            point_index = number.index(".")
                            number = number[:point_index]
                        if likes_string[-1] == "K":
                            post.no_of_likes = int(number)*1000
                            if "." in likes_string:
                                post.no_of_likes += int(likes_string[point_index+1:-1])*100
                        elif likes_string[-1] == "M":
                            post.no_of_likes = int(number)*1000000
                            if "." in likes_string:
                                post.no_of_likes += int(likes_string[point_index+1:-1])*100000
                
                post.no_of_views = 0
                view_string = None
                for element in self.driver.find_elements_by_class_name("d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.lr9zc1uh.a8c37x1j.fe6kdd0r.mau55g9w.c8b282yb.keod5gw0.nxhoafnm.aigsh9s9.d9wwppkn.mdeji52x.e9vueds3.j5wam9gi.b1v8xokw.m9osqain"):
                    view_string = element.text
                    if "view" in view_string:
                        view_string = view_string.replace(",", "").split()[0]
                        try:
                            post.no_of_views = int(view_string)
                        except:
                            if view_string:
                                number = view_string[:-1]
                                if "." in number:
                                    point_index = number.index(".")
                                    number = number[:point_index]
                                if view_string[-1] == "K":
                                    post.no_of_views = int(number)*1000
                                    if "." in view_string:
                                        post.no_of_views += int(view_string[point_index+1:-1])*100
                                elif view_string[-1] == "M":
                                    post.no_of_views = int(number)*1000000
                                    if "." in view_string:
                                        post.no_of_views += int(view_string[point_index+1:-1])*100000
                        break

                date_text = self.driver.find_element_by_class_name("oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.gmql0nx0.gpro0wi8.b1v8xokw").text
                date_text_split = date_text.split()
                if len(date_text_split) == 4 and "at" in date_text and ":" in date_text:
                    post.date_posted = datetime.strptime(" ".join(date_text_split[:2]) + " " + str(datetime.now().year) + " " + date_text_split[3], "%d %B %Y %H:%M")
                elif len(date_text_split) == 3 and date_text_split[0].lower() == "yesterday":
                    post.date_posted = datetime.strptime(str((date.today() - timedelta(days=1))) + " " + date_text_split[2], "%Y-%m-%d %H:%M")
                elif len(date_text_split) > 3:
                    post.date_posted = datetime.strptime(" ".join(date_text_split[:2]) + " " + str(datetime.now().year), "%B %d %Y")
                elif len(date_text_split) == 3:
                    try:
                        post.date_posted = datetime.strptime(date_text, "%d %B %Y")
                    except:
                        post.date_posted = datetime.strptime(date_text, "%B %d %Y")
                elif len(date_text_split) == 2:
                    if date_text.lower() == "just now":
                        post.date_posted = datetime.now()
                    elif date_text_split[1] == "hrs":
                        post.date_posted = datetime.now() - timedelta(hours=int(date_text_split[0]))
                    else:
                        try:
                            post.date_posted = datetime.strptime(date_text + " " + str(datetime.now().year), "%d %B %Y")
                        except:
                            post.date_posted = datetime.strptime(date_text + " " + str(datetime.now().year), "%B %d %Y")
                elif len(date_text_split) == 1:
                    if date_text[-1] == "m":
                        minutes = int(date_text[:-1])
                        post.date_posted = datetime.now() - timedelta(minutes=minutes)
                    elif date_text[-1] == "h":
                        hours = int(date_text[:-1])
                        post.date_posted = datetime.now() - timedelta(hours=hours)
                    elif date_text[-1] == 's':
                        seconds = int(date_text[:-1])
                        post.date_posted = datetime.now() - timedelta(seconds=seconds)
                post.status = "success"
            except Exception as e:
                post.status = "error"
                post.log = str(e)
                logging.error(str(e))
                self.reporter.error(f"Error scraping video {post.id} for {username}: {str(e)}")
            video_posts.append(post)
            if self.use_db:
                self.db.insert_or_update_post(post)
            if scrape_specific_video:
                return post
        return video_posts

    
    def scrape_products(self, url, username=None, scrape_specific_product=None):
        self.driver.get(url.rstrip("/") + "/shop")
        if not username:
            username = url.rstrip("/").split("/")[-1]
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.gmql0nx0.p8dawk7l")))
        except:
            return []
        products_tags = self.driver.find_elements_by_class_name("oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.gmql0nx0.p8dawk7l")
        products = []
        for product_tag in products_tags:
            product = Product()
            try:
                product.id = product_tag.get_attribute("href").split("?")[0].strip("/").split("/")[-1]
            except Exception as e:
                logging.error("Error locating ID: " + str(e))
                continue
            if scrape_specific_product and product.id != scrape_specific_product:
                continue
            logging.info("Scraping Product %s for %s" % (product.id, username))
            product.username = username
            try:
                product.description = product_tag.find_element_by_class_name("a8c37x1j.ni8dbmo4.stjgntxs.l9j0dhe7").text.strip()
                price_text = product_tag.find_element_by_class_name("d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.lr9zc1uh.a8c37x1j.fe6kdd0r.mau55g9w.c8b282yb.keod5gw0.nxhoafnm.aigsh9s9.d3f4x2em.iv3no6db.jq4qci2q.a3bd9o3v.b1v8xokw.m9osqain").text
                for i, c in enumerate(price_text):
                    if c.isnumeric():
                        break
                product.currency = price_text[:i]
                product.price = float(price_text[i:].replace(",", ""))
                product.media_path = FILES_DIR.rstrip("/") + "/product/image/" + str(product.id) + ".jpg"
                res = requests.get(product_tag.find_element_by_tag_name("img").get_attribute("src"))
                with open(product.media_path, "wb") as f:
                    f.write(res.content)
                product.status = "success"
            except Exception as e:
                logging.error(str(e))
                product.status = "error"
                product.log = str(e)
                self.reporter.error(f"Error scraping product {product.id} for {username}: {str(e)}")
            if self.use_db:
                self.db.insert_or_update_product(product)
            products.append(product)
            if scrape_specific_product:
                return product
        return products

    def bulk_scrape(self, urls, num_threads):

        if platform == "linux" or platform == "linux2":
            urls_to_scrape = Queue()
            for url in urls:
                urls_to_scrape.put(url)
            processes = []
            for i in range(num_threads):
                processes.append(Process(target=self.scrape_urls_from_queue, args=(urls_to_scrape, )))
                processes[i].start()

            for i in range(num_threads):
                processes[i].join()
        else:
            for url in urls:
                self.scrape_profile(url)
    
    
    def scrape_urls_from_queue(self, q):

        try:
            scraper = FacebookScraper()
            
            while q.qsize():
                company_url = q.get()
                scraper.scrape_profile(company_url)   
        except:
            pass

        try:
            scraper.kill_chrome()
        except:
            pass


    def kill_chrome(self):
        try:
            self.driver.quit()
        except:
            pass

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="FacebookScraper CLI to grab company profiles, posts and products from URL")
    parser.add_argument("--bulk_scrape_urls_file", nargs='?', type=str, default=False, help="File to read urls for bulk scrape, one url per line.")
    parser.add_argument("--urls", nargs='*', help="url(s) for scraping. Separate by spaces")
    parser.add_argument("--no_of_threads", nargs='?', type=int, default=1, help="No of threads to run. Default 1")
    parser.add_argument("--log_file", nargs='?', type=str, default=None, help="Path for log file. If not given, output will be printed on stdout.")
    parser.add_argument("--grabber-facebook-mustansir", nargs='?', type=bool, default=False, help="Only mark to kill all")
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    # setup logging based on arguments
    if args.log_file and platform == "linux" or platform == "linux2":
        logging.basicConfig(filename=args.log_file, filemode='a',format='%(asctime)s Process ID %(process)d: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    elif platform == "linux" or platform == "linux2":
        logging.basicConfig(format='%(asctime)s Process ID %(process)d: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    elif args.log_file:
        logging.basicConfig(filename=args.log_file, filemode='a',format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    else:
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)

    scraper = FacebookScraper()
    if args.bulk_scrape_urls_file:
        with open(args.bulk_scrape_urls_file, "r") as f:
            urls = f.read()
            urls = [x.strip() for x in urls.split("\n") if x.strip()]
        scraper.bulk_scrape(urls, num_threads=args.no_of_threads)
    else:
        for url in args.urls:
            profile = scraper.scrape_profile(url)
            logging.info("Profile for %s scraped successfully.\n" % profile.username)
            try:
                print(profile)
            except Exception as e:
                print(e)
            print("\n")
            for i, post in enumerate(profile.posts, start=1):
                print("Post# " + str(i))
                try:
                    print(post)
                except Exception as e:
                    print(e)
                print("\n")
            for i, product in enumerate(profile.products, start=1):
                print("Product# " + str(i))
                try:
                    print(product)
                except Exception as e:
                    print(e)
                print("\n")
   
    scraper.kill_chrome()

        