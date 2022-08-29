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
            subline = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "gvxzyvdx.aeinzg81.t7p7dqev.gh25dzvf.exr7barw.b6ax4al1.gem102v4.ncib64c9.mrvwc6qr.sx8pxkcf.f597kf1v.cpcgwwas.m2nijcs8.szxhu1pg.hpj0pwwo.sggt6rq5.tes86rjd.rtxb060y.ztn2w49o"))).text.split("·")
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
            see_more_button = self.driver.find_element_by_class_name('qi72231t.nu7423ey.n3hqoq4p.r86q59rh.b3qcqh3k.fq87ekyn.bdao358l.fsf7x5fv.rse6dlih.s5oniofx.m8h3af8h.l7ghb35v.kjdc1dyq.kmwttqpk.srn514ro.oxkhqvkx.rl78xhln.nch0832m.cr00lzj9.rn8ck1ys.s3jn8y49.icdlwmnq.cxfqmxzd.pbevjfx6.innypi6y')
            if see_more_button.text.strip().lower() == "see more":
                see_more_button.click()
        except:
            pass
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "qgrdou9d.nu7423ey.frfouenu.bonavkto.djs4p424.r7bn319e.bdao358l.aglvbi8b.m8h3af8h.l7ghb35v.kjdc1dyq.kmwttqpk.srn514ro.oxkhqvkx.rl78xhln.nch0832m.om3e55n1.cr00lzj9.mfclru0v")))
        except Exception as e:
            profile.status = "error"
            profile.log = "Error for " + url + ": Error loading about block"
            logging.error(profile.log)
            self.reporter.error(profile.log)
        lines = self.driver.find_elements_by_class_name("qgrdou9d.nu7423ey.frfouenu.bonavkto.djs4p424.r7bn319e.bdao358l.aglvbi8b.m8h3af8h.l7ghb35v.kjdc1dyq.kmwttqpk.srn514ro.oxkhqvkx.rl78xhln.nch0832m.om3e55n1.cr00lzj9.mfclru0v")
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
        try:
            images = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "h6ft4zvz.r227ecj6.ez8dtbzv.gt60zsk1"))).find_elements_by_tag_name("a")
        except Exception as e:
            logging.error("Error scraping images: " + str(e))
            self.reporter.error(str(e))
            return []
        image_posts = []
        for image in images:
            post = Post()
            post.id = image.get_attribute("href").rstrip("/").split("/")[-1]
            if scrape_specific_photo and post.id != scrape_specific_photo:
                continue
            self.driver.execute_script("arguments[0].click();", image)
            img = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "d65gybhy.gvxzyvdx.b84q63wn.lxj2zdis")))
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
                post.caption = self.driver.find_element_by_class_name("nch0832m.sglrnj1k.oxkhqvkx.jpugfq45").text
                post.caption = " ".join(filter(lambda x:x[0]!='#' or x[0] != '@', post.caption.split()))
                post.no_of_likes = 0
                likes_string = None
                try:
                    likes_string = self.driver.find_element_by_class_name("o3hwc0lp.lq84ybu9.hf30pyar.oshhggmv.lwqmdtw6").text.replace(",", "")
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
                date_text = self.driver.find_element_by_class_name("qi72231t.nu7423ey.n3hqoq4p.r86q59rh.b3qcqh3k.fq87ekyn.bdao358l.fsf7x5fv.rse6dlih.s5oniofx.m8h3af8h.l7ghb35v.kjdc1dyq.kmwttqpk.srn514ro.oxkhqvkx.rl78xhln.nch0832m.cr00lzj9.rn8ck1ys.s3jn8y49.icdlwmnq.jxuftiz4.cxfqmxzd.tes86rjd").text
                date_text_split = date_text.split()
                if len(date_text_split) == 4 and "at" in date_text and ":" in date_text:
                    post.date_posted = datetime.strptime(" ".join(date_text_split[:2]) + " " + str(datetime.now().year) + " " + date_text_split[3], "%d %B %Y %H:%M")
                elif len(date_text_split) == 3 and date_text_split[0].lower() == "yesterday":
                    post.date_posted = datetime.strptime(str((date.today() - timedelta(days=1))) + " " + date_text_split[2], "%Y-%m-%d %H:%M")
                elif len(date_text_split) > 3:
                    post.date_posted = datetime.strptime(" ".join(date_text_split[:2]) + " " + str(datetime.now().year), "%B %d %Y")
                elif len(date_text_split) == 3:
                    if "," in date_text:
                        comma = ","
                    else:
                        comma = ""
                    try:
                        post.date_posted = datetime.strptime(date_text, f"%d %B{comma} %Y")
                    except:
                        post.date_posted = datetime.strptime(date_text, f"%B %d{comma} %Y")
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
        try:
            videos = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "alzwoclg.om3e55n1.mfclru0v"))).find_elements_by_tag_name("a")
        except Exception as e:
            logging.error("Error scraping videos: " + str(e))
            self.reporter.error(str(e))
            return []
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
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "r227ecj6.gt60zsk1.g4qalytl")))
            try:
                buttons = self.driver.find_elements_by_class_name("qi72231t.nu7423ey.n3hqoq4p.r86q59rh.b3qcqh3k.fq87ekyn.bdao358l.fsf7x5fv.rse6dlih.s5oniofx.m8h3af8h.l7ghb35v.kjdc1dyq.kmwttqpk.srn514ro.oxkhqvkx.rl78xhln.nch0832m.cr00lzj9.rn8ck1ys.s3jn8y49.icdlwmnq.cxfqmxzd.pbevjfx6.innypi6y")
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
                    post.caption = self.driver.find_element_by_class_name("o9wcebwi.bsavta2s.mm05nxu8").text
                    post.caption = " ".join(filter(lambda x:x[0]!='#' or x[0] != '@', post.caption.split()))
                except:
                    pass

                post.no_of_likes = 0
                likes_string = None
                try:
                    likes_string = self.driver.find_element_by_class_name("cxfqmxzd.nu7423ey.o3hwc0lp.kmwttqpk.lq84ybu9.hf30pyar.oshhggmv.qm54mken").text.replace(",", "")
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
                for element in self.driver.find_elements_by_class_name("gvxzyvdx.aeinzg81.t7p7dqev.gh25dzvf.exr7barw.b6ax4al1.gem102v4.ncib64c9.mrvwc6qr.sx8pxkcf.f597kf1v.cpcgwwas.f5mw3jnl.szxhu1pg.nfkogyam.kkmhubc1.tes86rjd.rtxb060y"):
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

                date_text = self.driver.find_element_by_class_name("qi72231t.nu7423ey.n3hqoq4p.r86q59rh.b3qcqh3k.fq87ekyn.bdao358l.fsf7x5fv.rse6dlih.s5oniofx.m8h3af8h.l7ghb35v.kjdc1dyq.kmwttqpk.srn514ro.oxkhqvkx.rl78xhln.nch0832m.cr00lzj9.rn8ck1ys.s3jn8y49.icdlwmnq.jxuftiz4.cxfqmxzd.tes86rjd").text
                date_text_split = date_text.split()
                if len(date_text_split) == 4 and "at" in date_text and ":" in date_text:
                    post.date_posted = datetime.strptime(" ".join(date_text_split[:2]) + " " + str(datetime.now().year) + " " + date_text_split[3], "%d %B %Y %H:%M")
                elif len(date_text_split) == 3 and date_text_split[0].lower() == "yesterday":
                    post.date_posted = datetime.strptime(str((date.today() - timedelta(days=1))) + " " + date_text_split[2], "%Y-%m-%d %H:%M")
                elif len(date_text_split) > 3:
                    post.date_posted = datetime.strptime(" ".join(date_text_split[:2]) + " " + str(datetime.now().year), "%B %d %Y")
                elif len(date_text_split) == 3:
                    if "," in date_text:
                        comma = ","
                    else:
                        comma = ""
                    try:
                        post.date_posted = datetime.strptime(date_text, f"%d %B{comma} %Y")
                    except:
                        post.date_posted = datetime.strptime(date_text, f"%B %d{comma} %Y")
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
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "qi72231t.nu7423ey.n3hqoq4p.r86q59rh.b3qcqh3k.fq87ekyn.bdao358l.fsf7x5fv.rse6dlih.s5oniofx.m8h3af8h.l7ghb35v.kjdc1dyq.kmwttqpk.srn514ro.oxkhqvkx.rl78xhln.nch0832m.cr00lzj9.rn8ck1ys.s3jn8y49.icdlwmnq.jxuftiz4.l3ldwz01")))
        except:
            return []
        products_tags = self.driver.find_elements_by_class_name("qi72231t.nu7423ey.n3hqoq4p.r86q59rh.b3qcqh3k.fq87ekyn.bdao358l.fsf7x5fv.rse6dlih.s5oniofx.m8h3af8h.l7ghb35v.kjdc1dyq.kmwttqpk.srn514ro.oxkhqvkx.rl78xhln.nch0832m.cr00lzj9.rn8ck1ys.s3jn8y49.icdlwmnq.jxuftiz4.l3ldwz01")
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
                product.description = product_tag.find_element_by_class_name("b6ax4al1.lq84ybu9.hf30pyar.om3e55n1").text.strip()
                price_text = product_tag.find_element_by_class_name("mfclru0v.d2hqwtrz.i0rxk2l3.t5n4vrf6.sr926ui1.alzwoclg").text
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

        