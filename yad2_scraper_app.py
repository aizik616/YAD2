import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

st.set_page_config(page_title="ירידת ערך ביד2", layout="wide")
st.title("📉 ניתוח ירידת ערך מרכבים ביד2")
st.caption("הדבק קישור לעמוד תוצאות ביד2 (למשל: מאזדה 3, יונדאי איוניק)")

url = st.text_input("🔗 קישור לחיפוש:", "")

if url:
    with st.spinner("🚗 טוען מודעות מדף יד2..."):
        # הגדרות לדפדפן כרום ללא GUI
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)

        time.sleep(5)  # אפשר להחליף ל־WebDriverWait בהמשך

        html = driver.page_source
        driver.quit()

        # שמירת ה-HTML לבדיקה
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        soup = BeautifulSoup(html, "html.parser")
        listings = soup.find_all("div", class_="feeditem table")  # class שצריך לוודא שהוא עדכני

        data = []
        for item in listings:
            title = item.find("h3")
            price = item.find("div", class_="price")
            year_km = item.find("ul", class_="data")

            if title and price and year_km:
                data.append({
                    "רכב": title.get_text(strip=True),
                    "מחיר": price.get_text(strip=True).replace("₪", "").replace(",", ""),
                    "פרטים": year_km.get_text(" | ", strip=True)
                })

        if data:
            df = pd.DataFrame(data)
            st.success(f"נמצאו {len(df)} מודעות")
            st.dataframe(df)
        else:
            st.error("לא נמצאו מודעות. ייתכן שה־class השתנה או שהעמוד נטען חלקית.")
