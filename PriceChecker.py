import requests, app, sqlite3, Scraper, Joke, Twilio


# Get items from DB
def get_items():
    items = app.Items.query.all()
    return items

# Run only when adding new item
def create_item(link, buy_price):

    # Take in data from website
    url = link
    buy_price = float(buy_price)

    # Determine site for data scraping
    scraper = site_check(url)

    # Scrape data into variables
    title = scraper.title()
    selling_price = scraper.price_finder()
    image_url = scraper.image_url()

    # Add completed item to db
    item = app.Items(title=title, selling_price=selling_price, imageurl=image_url, buy_price=buy_price, link=url)
    app.db.session.add(item)
    app.db.session.commit()

# Determine correct 'scraper' to use
def site_check(url):

    if 'bhphotovideo.com' in url:
        return Scraper.BHPhoto(url)
    elif 'bestbuy.com' in url:
        return Scraper.BestBuy(url)
    elif 'amazon.com' in url:
        return Scraper.Amazon(url)
    elif 'walmart.com' in url:
        return Scraper.Walmart(url)
    elif 'target.com' in url:
        return Scraper.Target(url)
    elif 'ulta.com' in url:
        return Scraper.Ulta(url)
    else:
        print('we no support you silly site.')

def price_check():
    items = get_items()
    
    for item in items:

        current_price = float(item.selling_price)

        # Determine site for data scraping
        scraper = site_check(item.link)

        # Scrape correct site for new selling price
        selling_price = scraper.price_finder()

        # If price changed save new price to db
        if selling_price != current_price:
            update_price(selling_price, item.id)
            print(f"{ item.title } is now { selling_price }")

            # If new price is less than buy price text user
            text_user(selling_price, float(item.buy_price), item.link)

        else:
            print(f"No Change in price for { item.title }")

    # Print joke for happiness
    joke = Joke.get_joke()
    
def update_price(selling_price, id):
    item = app.Items.query.get(id)
    item.selling_price = selling_price
    app.db.session.commit()

def text_user(selling_price, buy_price, url):
    if selling_price <= buy_price:
        print("texted user")
        #Twilio.send_text(url, selling_price)
    else:
        print("still not cheap enough")