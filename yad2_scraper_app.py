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
st.caption("הדבק קישור לעמוד תוצאות ביד2 (למשל: קיה נירו, מאזדה 3)")

url = st.text_input("🔗 קישור לדף:", "")

if url:
    with st.spinner("🚗 טוען מודעות מהאתר..."):
        # הגדרות לדפדפן כרום (פתוח רגיל כדי למנוע קריסה)
        options = Options()
        # options.add_argument("--headless")  # ⛔ שורה זו מושבתת כדי לא לקרוס
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver_path = r"C:\Users\malachi\.wdm\drivers\chromedriver\win64\138.0.7204.94\chromedriver-win32\chromedriver.exe" driver = webdriver.Chrome(executable_path=driver_path, options=options)
        driver.get(url)

        time.sleep(5)  # המתנה שהדף ייטען

        html = driver.page_source
        driver.quit()

        # ✅ שמירת HTML לבדיקה
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        # ניתוח HTML עם BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        listings = soup.find_all("div", class_="feeditem table")  # סלקטור זמני

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
            st.error("❌ לא נמצאו מודעות — ייתכן שצריך לעדכן class לפי HTML בפועל.")
