from flask import Flask, render_template, request, send_file, redirect, url_for
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import linkedin
import os

app = Flask(__name__)

# Configure WebDriver options for Chrome
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")
browser = webdriver.Chrome(options=options)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        if keyword:
            linkedin.login(browser)
            profiles = linkedin.scrape_multiple_profiles(browser, keyword)
            filename = f"{keyword.replace(' ', '_')}_profiles.xlsx"
            linkedin.profiles_to_excel(profiles, filename)
            return send_file(filename, as_attachment=True, download_name=filename)
    return render_template("search.html")

if __name__ == "__main__":
    app.run(debug=True)
