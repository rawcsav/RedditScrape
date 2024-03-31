import os
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import praw
from praw import models
from praw.exceptions import RedditAPIException, ClientException, PRAWException
from dotenv import load_dotenv

load_dotenv()

def setup_reddit_client():
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("USER_AGENT")
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("REDDIT_PASSWORD")
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        username=username,
        password=password
    )


def extract_comments(comment_forest, indent_level=0):
    comments = []
    for comment in comment_forest:
        if isinstance(comment, praw.models.MoreComments):
            continue
        comment_body = comment.body.replace('\n', ' ')
        comments.append({
            "author": str(comment.author) if comment.author else '[deleted]',
            "body": comment_body,
            "score": comment.score,
            "replies": extract_comments(comment.replies,
                                        indent_level + 1) if comment.replies else []
        })
    return comments


def extract_post_details(post):
    post_details = {
        'title': post.title,
        'author': str(post.author) if post.author else '[deleted]',
        'date': datetime.utcfromtimestamp(post.created_utc).strftime(
            '%Y-%m-%d %H:%M:%S'),
        'content_type': 'text' if post.is_self else 'link',
        'content_url': post.url,
        'post_text': post.selftext if post.is_self else '',
        'score': post.score,
        'comments': []
    }
    post.comments.replace_more(limit=0)
    post_details['comments'] = extract_comments(post.comments)
    return post_details


def read_existing_data(filename):
    try:
        with open(filename, "r", encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []  # Return an empty list if the file does not exist


def write_updated_data(data, filename):
    with open(filename, "w", encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def scrape_top_posts(subreddit_name, limit=10):
    reddit = setup_reddit_client()
    subreddit = reddit.subreddit(subreddit_name)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{subreddit_name}_top_posts_{timestamp}.json"

    existing_data = read_existing_data(filename)

    posts = list(subreddit.top(limit=limit))
    with ThreadPoolExecutor() as executor:
        future_to_post = {executor.submit(extract_post_details, post): post for post in
                          posts}
        try:
            for future in as_completed(future_to_post):
                post_details = future.result()
                if post_details:
                    existing_data.append(post_details)
        except (RedditAPIException, ClientException, PRAWException) as e:
            print(f"Reddit API error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    write_updated_data(existing_data, filename)


if __name__ == "__main__":
    subreddit_name = "python"  # Example subreddit
    limit = 10  # Example limit
    scrape_top_posts(subreddit_name, limit)

