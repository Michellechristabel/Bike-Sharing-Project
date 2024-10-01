import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Menambahkan helper function

def create_daily_rentals_df(day_df):
    day_df["dteday"] = pd.to_datetime(day_df["dteday"])
    rentals_df = day_df.resample("D", on="dteday").sum()
    rentals_df['total'] = rentals_df['casual'] + rentals_df['registered']
    return rentals_df

def create_sum_casual_df(day_df):
    sum_casual_df = day_df.groupby("one_of_week").casual.sum().sort_values(ascending=False).reset_index()
    return sum_casual_df

def create_sum_registered_df(day_df):
    sum_registered_df = day_df.groupby("one_of_week").registered.sum().sort_values(ascending=False).reset_index()
    return sum_registered_df

def create_weather_situation_df(day_df):
    weather_situation_df = day_df.groupby("weather_situation").count_rental.sum().reset_index()
    return weather_situation_df

def create_season_df(day_df):
    season_df = day_df.groupby("season").count_rental.sum().reset_index()
    return season_df

def create_rfm_df(day_df):
    rfm_df = day_df.groupby(by="one_of_week", as_index=False).agg({
        "dteday" : "max",
        "instant" : "nunique",
        "count_rental" : "sum"
    })
    rfm_df.columns = ["one_of_week", "max_order_timestamp", "frequency", "monetary"]
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = day_df["dteday"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df

# Prepare Data Frame
day_df = pd.read_csv("dashboard/day_clean.csv")

datetime_columns = ["dteday"]
day_df.sort_values(by="dteday", inplace=True)
day_df.reset_index(inplace=True)
for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])

# Membuat komponen filter
min_date_day = day_df["dteday"].min()
max_date_day = day_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo
    st.image("dashboard/logo.jpg")

    # Mengambil start_date dan end_date dari date_input
    start_date, end_date = st.date_input(
        label = "Rentang Waktu",
        min_value = min_date_day,
        max_value = max_date_day,
        value = [min_date_day, max_date_day]
    )

main_df = day_df[(day_df["dteday"] >= str(start_date)) & (day_df["dteday"] <= str(end_date))]

# Menyiapkan berbagai data frame
rentals_df = create_daily_rentals_df(main_df)
sum_casual_df = create_sum_casual_df(main_df)
sum_registered_df = create_sum_registered_df(main_df)
weather_situation_df = create_weather_situation_df(main_df)
season_df = create_season_df(main_df)
rfm_df = create_rfm_df(main_df)

# Membuat dashboard
st.header('Bike Sharing Dashboard :sparkles:')

st.subheader('Daily Users')
col1, col2, col3 = st.columns(3)

with col1:
    total_casual = rentals_df.casual.sum()
    st.metric("Total Casual User", value=total_casual)

with col2:
    total_registered = rentals_df.registered.sum()
    st.metric("Total Registered User", value=total_registered)

with col3:
    total_users = rentals_df.total.sum()
    st.metric("Total Users", value=total_users)

plt.figure(figsize=(10,6))
plt.plot(rentals_df.index, rentals_df['total'], color='#2596BE')
plt.xlabel(None)
plt.ylabel(None)
plt.title("Number of Users")
#plt.xticks(rotation=45)
#plt.grid(True)
plt.tight_layout()
st.pyplot(plt)

# Number of Casual and Registered User
st.subheader("Jumlah Pengguna Casual dan Pengguna Registered")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#0C6bA1", "#62C6DD", "#62C6DD", "#62C6DD", "#62C6DD", "#62C6DD", "#62C6DD"]
sns.barplot(
    x="casual",
    y="one_of_week",
    data=sum_casual_df,
    palette=colors,
    hue="one_of_week",
    legend=False,
    ax=ax[0]
)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Casual Users", loc="center", fontsize=30)
ax[0].tick_params(axis='y', labelsize=16)
ax[0].tick_params(axis='x', labelsize=16, rotation=-45)

sns.barplot(
    x="registered",
    y="one_of_week",
    data=sum_registered_df,
    palette=colors,
    hue="one_of_week",
    legend=False,
    ax=ax[1]
)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Pengguna Registered", loc="center", fontsize=30)
ax[1].tick_params(axis='y', labelsize=16)
ax[1].tick_params(axis='x', labelsize=12, rotation=-45)

st.pyplot(plt)

st.subheader("Performa Penjualan dalam Beberapa Tahun Terakhir")
plt.figure(figsize=(20,10))

plt.plot(
    day_df["dteday"],
    day_df["count_rental"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
plt.tick_params(axis="y", labelsize=20)
plt.tick_params(axis="x", labelsize=15)
st.pyplot(plt)

st.header("Pengaruh Cuaca Terhadap Penyewaan Sepeda")
colors = ["#62C6DD", "#62C6DD", "#0C6bA1", "#62C6DD"]

plt.subplots(figsize=(20, 15))
sns.barplot(
    x="weather_situation",
    y="count_rental",
    data=day_df.sort_values(by="weather_situation", ascending=False),
    palette=colors
)
plt.title("Grafik Antar Cuaca", loc="center", fontsize=40)
plt.xlabel(None)
plt.ylabel(None)
plt.tick_params(axis="x", labelsize=30)
plt.tick_params(axis="y", labelsize=30)
st.pyplot(plt)

#RFM Analysis
st.subheader("Pelanggan Terbaik Berdasarkan Analisis RFM")
col1, col2, col3 = st.columns(3)

with col1:
    average_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=average_recency)

with col2:
    average_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=average_frequency)

with col3:
    average_frequency = format_currency(rfm_df.monetary.mean(),"AUD", locale="es_CO")
    st.metric("Average Monetary", value=average_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35,15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(
    y="recency",
    x="one_of_week",
    data=rfm_df.sort_values(by="recency", ascending=True).head(5),
    palette=colors,
    hue="one_of_week",
    legend=False,
    ax=ax[0]
)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=25)
ax[0].tick_params(axis='x', labelsize=30, rotation=45)

sns.barplot(
    y="frequency",
    x="one_of_week",
    data=rfm_df.sort_values(by="frequency", ascending=True).head(5),
    palette=colors,
    hue="one_of_week",
    legend=False,
    ax=ax[1]
)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=25)
ax[1].tick_params(axis='x', labelsize=30, rotation=45)


sns.barplot(
    y="monetary",
    x="one_of_week",
    data=rfm_df.sort_values(by="monetary", ascending=True).head(5),
    palette=colors,
    hue="one_of_week",
    legend=False,
    ax=ax[2]
)
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=25)
ax[2].tick_params(axis='x', labelsize=30, rotation=45)

st.pyplot(plt)

