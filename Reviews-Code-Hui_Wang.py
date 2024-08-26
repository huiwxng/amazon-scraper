import requests
from bs4 import BeautifulSoup
import pandas as pd

# using Splash browser (javascript rendering service with an HTTP API) and Docker to host

amazon_url = 'https://www.amazon.com/'

cols = ['product name', 'review text', 'number of helpful votes', 'review date', 
          'reviewer name', 'star rating', 'verified purchase flag']

df = pd.DataFrame(columns=cols)

# function to get data from a url
def get_data(url):
    # Splash browser hosted on port 8050
    r = requests.get('http://localhost:8050/render.html', params={'url': url, 'wait': 2})
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

# function to get the url of the 'see more reviews' page
def get_all_reviews_url(soup):
    page = soup.find('a', {'data-hook': 'see-all-reviews-link-foot'})['href']
    if not page:
        return
    url = amazon_url + str(page)
    return url

# function to go to the next page of reviews
def get_next(soup):
    page = soup.find('ul', {'class': 'a-pagination'})
    if not page:
        return
    if not page.find('li', {'class': 'a-disabled a-last'}):
        href = str(page.find('li', {'class': 'a-last'}).find('a')['href'])
        url = amazon_url + href
        return url
    else:
        return

# function that gets the reviews from the review page
def get_reviews(soup):
    reviews = soup.find_all('div', {'data-hook': 'review'})

    for item in reviews:
        # item name
        item_name = soup.find('a', {'data-hook': 'product-link'}).text
        print(item_name)

        # review text
        try:
            text = item.find('span', {'data-hook': 'review-body'}).text
        except:
            text = "no review text"
        print(text)

        # num of helpful votes
        try:
            votes = item.find('span', {'data-hook': 'helpful-vote-statement'}).text
            votes = votes.split(' ')
        except:
            votes = ['n/a']
        print(f'helpful votes: {votes[0]}')
        votes = votes[0]

        # review date
        date = item.find('span', {'data-hook': 'review-date'}).text.strip()
        date = date.split()
        arr = date[len(date) - 3:]
        date = ''
        for i in arr:
            date += i
            date += ' '
        print(f'date: {date}')

        # reviewer
        reviewer = item.find('span', {'class': 'a-profile-name'}).text
        print(f'reviewer: {reviewer}')

        # verified purchase flag
        try:
            verified = item.find('span', {'data-hook': 'avp-badge-linkless'}).text
            if verified == "Verified Purchase":
                verified = "true"
            else:
                verified = "false"
        except:
            verified = "false"
        print(f'Verified Purchase: {verified}')

        # rating
        try:
            stars = item.find('i', {'data-hook': 'review-star-rating'}).text.strip().replace(' out of 5 stars', '')
        except:
            stars = 'n/a'
        print(f'Stars: {stars}')

        print('\n')

        global df

        new_row = [item_name, text, votes, date, reviewer, stars, verified]
        new_df = pd.DataFrame([new_row], columns=cols)

        df = pd.concat([df, new_df], ignore_index=True)


# function that moves to the 'see more reviews' page and calls to get reviews
def get_all_reviews(url):
    soup = get_data(url)
    url = get_all_reviews_url(soup)
    while True:
        get_reviews(get_data(url))
        soup = get_data(url)
        url = get_next(soup)
        if not url:
            break

# main function that searches through the first 8 results
def main(search_url):
    soup = get_data(search_url)
    for i in range(1, 10):
        div = soup.find('div', {'data-cel-widget': f'search_result_{i}'})
        if not div:
            print(f'search_result_{i}')
            continue
        url = amazon_url + div.find('a')['href']
        get_all_reviews(url)

    df.to_excel('Reviews-Hui_Wang.xlsx')

search_url = 'https://www.amazon.com/s?i=computers&rh=n%3A565108%2Cp_36%3A2421886011&s=exact-aware-popularity-rank&ds=v1%3AFQy9V088cXQ56%2BNygtPl5%2FhTz8psCEVCk5t9EzMs820&content-id=amzn1.sym.4d915fa8-ca05-4073-b385-a93e1e1dd22d&pd_rd_r=a42c9ae5-5a10-4802-8c2f-5f25ef0e364a&pd_rd_w=aoUV0&pd_rd_wg=9r6MB&pf_rd_p=4d915fa8-ca05-4073-b385-a93e1e1dd22d&pf_rd_r=B31SVVTK8X16Q535JREG&qid=1685043013&ref=sr_st_exact-aware-popularity-rank'
main(search_url)