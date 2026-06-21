import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# =====================================================================
# 1. ЗАВАНТАЖЕННЯ ТА ПІДГОТОВКА ДАНИХ (Автовизначення шляху)
# =====================================================================
# Отримуємо точний шлях до папки, де лежить цей скрипт .py
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "alerts_data.csv")

try:
    # Завантажуємо файл за абсолютною адресою
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
except FileNotFoundError:
    print(f"Помилка! Скрипт шукав файл тут: {csv_path}")
    print("Переконайся, що назва файлу саме 'alerts_data.csv'")
    exit()

# Очищаємо назви колонок від випадкових пробілів
df.columns = df.columns.str.strip()

# Перетворюємо колонки з часом у формат datetime
df["start_alert"] = pd.to_datetime(df["start_alert"])
df["end_alert"] = pd.to_datetime(df["end_alert"])

# Очищуємо тривалість (перетворюємо "120 хв" на чисте число 120)
df["duration_min"] = (
    df["time_alert"].astype(str).str.replace(" хв", "").astype(int)
)

# Витягуємо дату та часовий слот (ГГ:ХХ)
df["date"] = df["start_alert"].dt.date
df["time_slot"] = df["start_alert"].dt.strftime("%H:%M")

# =====================================================================
# 2. РОЗРАХУНОК СТАТИСТИКИ (ПІДСУМКІВ)
# =====================================================================
total_alerts = len(df)
total_duration_hours = df["duration_min"].sum() / 60
mean_duration = df["duration_min"].mean()

max_duration = df["duration_min"].max()
max_alert_row = df.loc[df["duration_min"].idxmax()]
max_alert_date = max_alert_row["date"].strftime("%d.%m")

daily_counts = df.groupby("date").size()
busiest_day = daily_counts.idxmax()
max_alerts_in_day = daily_counts.max()

# =====================================================================
# 3. ВІЗУАЛІЗАЦІЯ ДАНИХ
# =====================================================================
sns.set_theme(style="darkgrid")
fig = plt.figure(figsize=(15, 12))
fig.suptitle(
    "Аналіз часових рядів повітряних тривог у Києві (01.06.2026 - 20.06.2026)",
    fontsize=18,
    fontweight="bold",
    color="#2c3e50",
)

# --- ДІАГРАМА 1: Розподіл по півгодинах ---
plt.subplot(2, 1, 1)

all_slots = []
for hour in range(24):
    all_slots.append(f"{hour:02d}:00")
    all_slots.append(f"{hour:02d}:30")

slot_counts = df["time_slot"].value_counts()
full_slots_df = pd.DataFrame(index=all_slots)
full_slots_df["counts"] = slot_counts
full_slots_df["counts"] = full_slots_df["counts"].fillna(0).astype(int)

sns.barplot(
    x=full_slots_df.index,
    y=full_slots_df["counts"],
    palette="YlOrRd",
    hue=full_slots_df["counts"],
    legend=False,
)
plt.title(
    "1. Кількість тривог з розподілом по півгодинах доби (час початку)",
    fontsize=14,
    fontweight="bold",
)
plt.xlabel("Півгодинні інтервали початку тривоги", fontsize=12)
plt.ylabel("Кількість тривог", fontsize=12)
plt.xticks(rotation=90, fontsize=9)

# --- ДІАГРАМА 2: Динаміка по днях (Часовий ряд) ---
plt.subplot(2, 1, 2)

full_dates = pd.date_range(start="2026-06-01", end="2026-06-20").date
full_dates_df = pd.DataFrame(index=full_dates)
full_dates_df["counts"] = daily_counts
full_dates_df["counts"] = full_dates_df["counts"].fillna(0).astype(int)
full_dates_df.index = pd.to_datetime(full_dates_df.index).strftime("%d.%m")

plt.plot(
    full_dates_df.index,
    full_dates_df["counts"],
    marker="o",
    color="#c0392b",
    linewidth=2.5,
)
plt.fill_between(
    full_dates_df.index, full_dates_df["counts"], color="#e74c3c", alpha=0.15
)

plt.title(
    "2. Хронологічна динаміка тривог за днями (01-20 червня)",
    fontsize=14,
    fontweight="bold",
)
plt.xlabel("Дата", fontsize=12)
plt.ylabel("Кількість тривог за добу", fontsize=12)
plt.ylim(0, full_dates_df["counts"].max() + 1)
plt.xticks(rotation=45)

# --- ДОДАВАННЯ АНАЛІТИЧНОГО ПІДСУМКУ НА ГРАФІК ---
summary_text = (
    f"📊 АНАЛІТИЧНИЙ ПІДСУМОК ПЕРІОДУ:\n"
    f"• Всього зафіксовано тривог: {total_alerts}\n"
    f"• Сумарна тривалість небезпеки: {total_duration_hours:.1f} год.\n"
    f"• Середня тривалість однієї тривоги: {mean_duration:.0f} хв.\n"
    f"• Найважчий день: {busiest_day.strftime('%d.%m')} ({max_alerts_in_day} тривоги)\n"
    f"• Найдовша тривога: {max_duration} хв ({max_alert_date})"
)

plt.gcf().text(
    0.15,
    0.38,
    summary_text,
    fontsize=12,
    fontweight="bold",
    color="#2c3e50",
    bbox=dict(
        boxstyle="round,pad=0.8",
        facecolor="#fcf3cf",
        edgecolor="#f39c12",
        alpha=0.9,
    ),
)

plt.tight_layout()
plt.subplots_adjust(top=0.91, hspace=0.4)

plt.show()
