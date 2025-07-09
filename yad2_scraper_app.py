import time
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def scrape_yad2(url, max_pages=3):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    cars = []

    for _ in range(max_pages):
        time.sleep(3)
        items = driver.find_elements("css selector", ".feeditem")

        for item in items:
            try:
                title = item.find_element("css selector", ".title").text
                price = item.find_element("css selector", ".price").text.replace(",", "").replace("₪", "").strip()
                subtitle = item.find_element("css selector", ".subtitle").text
                year = [int(s) for s in subtitle.split() if s.isdigit()]
                year = year[0] if year else None
                if year and price.isdigit():
                    cars.append({
                        "title": title,
                        "year": year,
                        "price": int(price)
                    })
            except:
                continue

        # נסה לעבור לעמוד הבא
        try:
            next_button = driver.find_element("css selector", '[aria-label="לעמוד הבא"]')
            next_button.click()
        except:
            break

    driver.quit()
    return pd.DataFrame(cars)

def plot_prices(df):
    fig, ax = plt.subplots()
    ax.scatter(df["year"], df["price"], alpha=0.6, label="מודעות")
    
    # קו מגמה
    z = np.polyfit(df["year"], df["price"], 1)
    p = np.poly1d(z)
    df_sorted = df.sort_values("year")
    ax.plot(df_sorted["year"], p(df_sorted["year"]), "r--", label="קו מגמה")

    ax.set_xlabel("שנת ייצור")
    ax.set_ylabel("מחיר (₪)")
    ax.set_title("ירידת ערך לפי מודעות Yad2")
    ax.legend()
    st.pyplot(fig)

# Streamlit UI
st.title("ניתוח ירידת ערך מרכבים ביד2")
url = st.text_input("הדבק קישור לדף חיפוש ביד2 (למשל: מאזדה 3)", "")

if url:
    with st.spinner("שואב נתונים..."):
        df = scrape_yad2(url)
    st.success(f"נמצאו {len(df)} מודעות")
    st.dataframe(df)

    if not df.empty:
        plot_prices(df)
