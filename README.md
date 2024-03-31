
The provided script is designed to scrape top posts from a specified subreddit using the Reddit API, extract details from these posts and their comments, and save the data to a JSON file.

**Usage**:
1. Ensure Python 3.x is installed.
2. Install required packages: `praw`, `python-dotenv`
3. Set up an `.env` file with Reddit API credentials (`REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `USER_AGENT`, `REDDIT_USERNAME`, `REDDIT_PASSWORD`).
4. Run the script, modifying the `subreddit_name` and `limit` variables to target a specific subreddit and number of top posts.

