
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

REQUEST_TIMEOUT = 10
OUTPUT_FILE = "news_articles.json"


def scrape_kathmandu_post():
    base_url = "https://kathmandupost.com/"
    url = "https://kathmandupost.com/politics"
    news_articles = []

    def scrape_kathmandu_post_content(post_obj):
        try:
            post_url = base_url + post_obj.get('url', '') 
            response = requests.get(post_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_content = soup.find('section', class_='story-section')
            post_obj['content'] = news_content.get_text(strip=True) if news_content else ""
        
        except (requests.RequestException, requests.Timeout) as e:
            print(f"Error scraping Kathmandu Post Politics Page: {e}")
        except (AttributeError, TypeError) as e:
            print(f"Error parsing Kathmandu Post titles: {e}")
        
        return post_obj

    def scrape_kathmandu_post_titles():
        news_titles = []
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # find the politis tag just above the articles
            politics_title = soup.find('h4', class_='title--line__red')
            if not politics_title:
                print("No titles found in Kathmandu Post politics section.")
                return news_titles
            
            # articles are the siblings of the politics title
            articles = politics_title.find_next_siblings('article', class_='article-image')
            for article in articles:
                news = dict()
                
                # this is to skip the first anchor tag which is only the image link
                # this selects the first anchor tag that is a direct child of the article
                title_tag = article.select_one(":scope > a")
                
                if title_tag and title_tag.get_text(strip=True):
                    news['title'] = title_tag.get_text(strip=True)
                    news['url'] = title_tag['href'] if title_tag.has_attr('href') else None
                    news_titles.append(news)
        
        except (requests.RequestException, requests.Timeout) as e:
            print(f"Error scraping Kathmandu Post Politics Page: {e}")
        except (AttributeError, TypeError) as e:
            print(f"Error parsing Kathmandu Post titles: {e}")

        return news_titles
    
    news_titles = scrape_kathmandu_post_titles()
    print(f"\tFound {len(news_titles)} articles from Kathmandu Post")
    
    for i, news in enumerate(news_titles):
        print(f"\tProcessing article {i+1}/{len(news_titles)}: {news['title']}")
        if news.get('url'):
            news_with_content = scrape_kathmandu_post_content(news)
            news_articles.append(news_with_content)

    return news_articles


def scrape_online_khabar():
    url = "https://english.onlinekhabar.com/category/political"
    news_articles = []
    
    def scrape_online_khabar_content(post_obj):
        try:
            response = requests.get(post_obj['url'], timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_content = soup.find('div', class_='post-content-wrap')
            post_obj['content'] = news_content.get_text(strip=True) if news_content else ""
        
        except (requests.RequestException, requests.Timeout) as e:
            print(f"Error scraping Online Khabar Politics Page: {e}")
        except (AttributeError, TypeError) as e:
            print(f"Error parsing Online Khabar titles: {e}")
        
        return post_obj

    def scrape_online_khabar_titles():
        news_titles = []
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            

            articles_countainer = soup.find('div', class_='listical-news-big')
            if not articles_countainer:
                print("No articles found in Online Khabar politics section.")
                return []

            articles = articles_countainer.find_all('div', class_='ok-news-post')

            for article in articles:
                title_countainer = article.find('div', class_='ok-post-contents')
                title_tag = title_countainer.find('a') if title_countainer else None
                
                if title_tag and title_tag.get_text(strip=True):
                    news = dict()
                
                    news['title'] = title_tag.get_text(strip=True)
                    news['url'] = title_tag['href'] if title_tag.has_attr('href') else None
                    news_titles.append(news)

        except (requests.RequestException, requests.Timeout) as e:
            print(f"Error scraping Online Khabar Politics Page: {e}")
        except (AttributeError, TypeError) as e:
            print(f"Error parsing Online Khabar titles: {e}")
        
        return news_titles

    news_titles = scrape_online_khabar_titles()
    print(f"\tFound {len(news_titles)} articles from Online Khabar")

    for i, news in enumerate(news_titles):
        print(f"\tProcessing article {i+1}/{len(news_titles)}: {news['title']}")

        if news.get('url'):
            news_with_content = scrape_online_khabar_content(news)
            news_articles.append(news_with_content)

    return news_articles


def scrape_setopati():
    """Scrape news from Setopati Politics section"""
    url = "https://en.setopati.com/political"
    news_articles = []

    def scrape_setopati_content(post_obj):
        try:
            response = requests.get(post_obj['url'], timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_content = soup.find('div', class_='editor-box')
            post_obj['content'] = news_content.get_text(strip=True) if news_content else ""
        
        except (requests.RequestException, requests.Timeout) as e:
            print(f"Error scraping Setopati Politics Page: {e}")
        except (AttributeError, TypeError) as e:
            print(f"Error parsing Setopati titles: {e}")
        
        return post_obj
    
    def scrape_setopati_titles():
        news_titles = []
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # this website does not have a clear container for all articles.
            title_elements = soup.select("a span.main-title")

            for title_elem in title_elements:
                news = dict()
                
                news['title'] = title_elem.get_text(strip=True)
                parent_a_tag = title_elem.find_parent('a')
                
                # All articles have an image inside a figure tag, so we can use that to filter out non-article links
                if not parent_a_tag.find("figure"):
                    continue

                news['url'] = parent_a_tag['href'] if parent_a_tag and parent_a_tag.has_attr('href') else None
                news_titles.append(news)
        
        except (requests.RequestException, requests.Timeout) as e:
            print(f"Error scraping Setopati Politics Page: {e}")
        except (AttributeError, TypeError) as e:
            print(f"Error parsing Setopati titles: {e}")
        
        return news_titles
    
    news_titles = scrape_setopati_titles()
    print(f"\tFound {len(news_titles)} articles from Setopati")
    
    for i, news in enumerate(news_titles):
        print(f"\tProcessing article {i+1}/{len(news_titles)}: {news['title']}")
        if news.get('url'):
            news_with_content = scrape_setopati_content(news)
            news_articles.append(news_with_content)

    return news_articles


def scrape_nepalpress():

    url = "https://english.nepalpress.com/category/political/"
    news_articles = []

    def scrape_nepalpress_content(post_obj):
        try:
            response = requests.get(post_obj['url'], timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_content = soup.find('div', class_='news-content-area')
            post_obj['content'] = news_content.get_text(strip=True) if news_content else ""
        
        except (requests.RequestException, requests.Timeout) as e:
            print(f"Error scraping Nepal Press Politics Page: {e}")
        except (AttributeError, TypeError) as e:
            print(f"Error parsing Nepal Press titles: {e}")
        
        return post_obj
    
    def scrape_nepalpress_titles():
        news_titles = []
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_card_titles = soup.find_all('div', class_='news-title')
            featured_title = soup.find('h3', class_='title title-large')

            if featured_title:
                news_card_titles.append(featured_title)
        
            for title in news_card_titles:
                title_tag = title.find('a') if title else None
                if title_tag and title_tag.get_text(strip=True):
                    news = dict()
                    news['title'] = title_tag.get_text(strip=True)
                    news['url'] = title_tag['href'] if title_tag.has_attr('href') else None
                    news_titles.append(news)
    
        except (requests.RequestException, requests.Timeout) as e:
            print(f"Error scraping Nepal Press Politics Page: {e}")
        except (AttributeError, TypeError) as e:
            print(f"Error parsing Nepal Press titles: {e}")
        
        return news_titles

    news_titles = scrape_nepalpress_titles()
    print(f"\tFound {len(news_titles)} articles from Nepal Press")
    
    for i, news in enumerate(news_titles):
        print(f"\tProcessing article {i+1}/{len(news_titles)}: {news['title']}")
        if news.get('url'):
            news_with_content = scrape_nepalpress_content(news)
            news_articles.append(news_with_content)

    return news_articles


def scrape_all_portals():
    print("\nStarting to scrape Nepali news portals...")
    
    # scrape each portal
    print("\nScraping Kathmandu Post...")
    kathmandu_post_articles = scrape_kathmandu_post()
    print(f"Found {len(kathmandu_post_articles)} articles from Kathmandu Post")

    print("\nScraping Online Khabar...")
    online_khabar_articles = scrape_online_khabar()
    print(f"Found {len(online_khabar_articles)} articles from Online Khabar")
    
    print("\nScraping Setopati...")
    setopati_articles = scrape_setopati()
    print(f"Found {len(setopati_articles)} articles from Setopati")

    print("\nScraping Nepal Press...")
    nepal_press_articles = scrape_nepalpress()
    print(f"Found {len(nepal_press_articles)} articles from Nepal Press")


    # format the data
    data = {
        "scrape_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_articles": len(kathmandu_post_articles) + len(online_khabar_articles) + len(setopati_articles) + len(nepal_press_articles),
        "portals": [
            {
                "name": "Kathmandu Post",
                "url": "https://kathmandupost.com/politics",
                "articles_count": len(kathmandu_post_articles),
                "articles": kathmandu_post_articles
            },
            {
                "name": "Online Khabar",
                "url": "https://english.onlinekhabar.com/political",
                "articles_count": len(online_khabar_articles),
                "articles": online_khabar_articles
            },
            {
                "name": "Setopati",
                "url": "https://en.setopati.com/political",
                "articles_count": len(setopati_articles),
                "articles": setopati_articles
            },
            {
                "name": "Nepal Press",
                "url": "https://english.nepalpress.com/category/political/",
                "articles_count": len(nepal_press_articles),
                "articles": nepal_press_articles
            }
        ]
    }
    
    return data


def read_from_json(filename=OUTPUT_FILE):
    try:
        with open (filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        print(f"\nError decoding JSON file: {e}")
        return []
    except Exception as e:
        print(f"\nError reading JSON file: {e}")
        return []


def save_to_json(data, filename=OUTPUT_FILE):

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\nData successfully saved to {filename}")
    except TypeError as e:
        print(f"\nError serializing data to JSON: {e}")
    except Exception as e:
        print(f"\nError writing to JSON file: {e}")


def filter_old_news(new_data, existing_data):
    if not existing_data:
        return new_data


    existing_urls = set()
    for portal in existing_data.get('portals', []):
        for article in portal.get('articles', []):
            if article.get('url'):
                existing_urls.add(article['url'])
    
    filtered_articles = []
    for portal in new_data.get('portals', []):
        new_portal = {
            "name": portal['name'],
            "url": portal['url'],
            "articles_count": 0,
            "articles": []
        }
        for article in portal.get('articles', []):
            if article.get('url') and article['url'] not in existing_urls:
                new_portal['articles'].append(article)
                new_portal['articles_count'] += 1
        if new_portal['articles_count'] > 0:
            filtered_articles.append(new_portal)
    
    resp = {
        "scrape_date": new_data['scrape_date'],
        "total_articles": sum(portal['articles_count'] for portal in filtered_articles),
        "portals": filtered_articles
    }
    return resp


def combine_news_data(existing_data, new_data):
    if not existing_data:
        return new_data

    combined_portals = {p['name']: p for p in existing_data.get('portals', [])}
    for portal in new_data.get('portals', []):
        if portal['name'] in combined_portals:
            combined_portals[portal['name']]['articles'].extend(portal['articles'])
            combined_portals[portal['name']]['articles_count'] += portal['articles_count']
        else:
            combined_portals[portal['name']] = portal
    
    combined_data = {
        "scrape_date": new_data['scrape_date'],
        "total_articles": sum(p['articles_count'] for p in combined_portals.values()),
        "portals": list(combined_portals.values())
    }
    return combined_data


def main():
    # Read existing data from JSON file
    saved_news = read_from_json()

    # Scrape all portals
    current_news = scrape_all_portals()
    
    # Filter out old news articles that are already in the saved data
    new_news = filter_old_news(current_news, saved_news)

    # Combine new news with existing news for saving
    combined_data = combine_news_data(saved_news, new_news)

    # Save to JSON file
    save_to_json(combined_data)
    
    # Print summary
    print(f"\nSummary:")
    print(f"Total news articles scraped (this run): {current_news['total_articles']}")
    print(f"New articles fetched: {new_news['total_articles']}")
    
    print("\nPer portal:")
    # Build a mapping of portal name to new articles count
    new_articles_by_portal = {p['name']: p['articles_count'] for p in new_news['portals']}
    for portal in current_news['portals']:
        name = portal['name']
        total = portal['articles_count']
        new_count = new_articles_by_portal.get(name, 0)
        print(f"  - {name}: {total} scraped, {new_count} new")


if __name__ == "__main__":
    main()
