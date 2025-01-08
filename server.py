from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/get_scraping_task', methods=['GET'])
def get_scraping_task():
    # This is an example response from your central system
    return jsonify({
        "url": "https://www.aajtak.in/rssfeeds/sitemap.xml",
        "scrape_type": "sitemap"
    })

if __name__ == '__main__':
    app.run(debug=True)
