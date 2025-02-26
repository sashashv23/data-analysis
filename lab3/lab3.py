import pandas as pd
import datetime
import os
import urllib
import glob
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.colors import LinearSegmentedColormap

class VHIAnalysis:
    def __init__(self, base_folder='vhi_data'):
        # Ініціалізація класу, створення словників та колірної карти
        self.base_folder = base_folder
        self.lavender_malina_cmap = LinearSegmentedColormap.from_list(
            "lavender_malina", ["#E6E6FA", "#D5006D"], N=256)
        self.regions_true_id = {
            1: 'Вінницька',  2: 'Волинська',  3: 'Дніпропетровська',  4: 'Донецька',  5: 'Житомирська',
            6: 'Закарпатська',  7: 'Запорізька',  8: 'Івано-Франківська',  9: 'Київська',  10: 'Кіровоградська',
            11: 'Луганська',  12: 'Львівська',  13: 'Миколаївська',  14: 'Одеська',  15: 'Полтавська',
            16: 'Рівненська',  17: 'Сумська',  18: 'Тернопільська',  19: 'Харківська',  20: 'Херсонська',
            21: 'Хмельницька',  22: 'Черкаська',  23: 'Чернівецька',  24: 'Чернігівська',  25: 'Республіка Крим'
        }
        self.columns = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']
    
    def load_data(self, province_code):
        # Завантаження VHI-даних для заданого регіону
        if not os.path.isdir(self.base_folder):
            os.makedirs(self.base_folder)

        current_date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
        file_name = f'vhi_id__{province_code}__{current_date}.csv'
        file_path = os.path.join(self.base_folder, file_name)

        url = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={province_code}&year1=1981&year2=2025&type=Mean"

        files_in_folder = [f for f in os.listdir(self.base_folder) if f.startswith(f'vhi_id__{province_code}__')]
        if files_in_folder:
            print(f"Data for province {province_code} already downloaded. Skipping download.")
            return

        try:
            response = urllib.request.urlopen(url)
            data = response.read()
            with open(file_path, 'wb') as file:
                file.write(data)
            print(f"VHI data successfully downloaded to file: {file_path}")
        except Exception as e:
            print(f"Failed to download data for province {province_code}: {e}")
    
    def data_frame(self):
        # Обробка CSV-файлів та формування єдиного DataFrame
        def process_csv(file_path):
            region_num = int(file_path.split('__')[1])
            data = pd.read_csv(file_path, header=1, names=self.columns)
            data.at[0, 'Year'] = data.at[0, 'Year'][9:]
            data = data.drop(data.index[-1])
            data = data[data['VHI'] != -1]
            data = data.drop(columns=['empty'])
            data.insert(0, 'region_num', region_num, True)
            data['Week'] = data['Week'].astype(int)
            return data

        csv_files = glob.glob(f"{self.base_folder}/*.csv")
        data_frames = [process_csv(file) for file in csv_files]

        combined_data = pd.concat(data_frames).drop_duplicates().reset_index(drop=True)
        combined_data = combined_data[~combined_data.region_num.isin([12, 20])]

        region_translation = {
            1: 22, 2: 24, 3: 23, 4: 25, 5: 3, 6: 4, 7: 8, 8: 19, 9: 20, 10: 21,
            11: 9, 13: 10, 14: 11, 15: 12, 16: 13, 17: 14, 18: 15, 19: 16, 21: 17,
            22: 18, 23: 6, 24: 1, 25: 2, 26: 6, 27: 5
        }
        combined_data['region_num'] = combined_data['region_num'].replace(region_translation)

        return combined_data

    def filter_data(self, df, years_interval, weeks_interval, region, sort_asc, sort_desc, parameter):
        # Фільтрація даних за вибраними параметрами
        region_num_selected = [key for key, value in self.regions_true_id.items() if value == region][0]
        filtered_data = df[(df["Year"].between(years_interval[0], years_interval[1])) & 
                           (df['Week'].between(weeks_interval[0], weeks_interval[1])) & 
                           (df['region_num'] == region_num_selected)]

        if sort_asc and not sort_desc:
            filtered_data = filtered_data.sort_values(by=parameter, ascending=True)
        elif sort_desc and not sort_asc:
            filtered_data = filtered_data.sort_values(by=parameter, ascending=False)

        return filtered_data

    def plot_line_chart(self, filtered_data, parameter):
        # Побудова лінійного графіка для вибраного параметра
        fig, ax = plt.subplots(figsize=(16, 8))
        sns.lineplot(data=filtered_data, x="Year", y=parameter, ax=ax, linewidth=2, ci=None, color="#D5006D")
        ax.set_xlabel("Рік")
        ax.set_ylabel(parameter)
        return fig

    def plot_heatmap(self, df, parameter, years_interval):
        # Побудова теплової карти за вибраним параметром
        df_filtered = df[df['Year'].between(years_interval[0], years_interval[1])]
        pivot_data = df_filtered.pivot_table(values=parameter, index="region_num", columns="Year", aggfunc='mean')
        pivot_data = pivot_data.rename(index=self.regions_true_id)
        fig, ax = plt.subplots(figsize=(16, 10))
        sns.heatmap(pivot_data, cmap=self.lavender_malina_cmap, annot=False, linewidths=0.5, ax=ax)
        ax.set_xlabel("Рік")
        ax.set_ylabel("Регіон")
        return fig

    def run_analysis(self):
        # Головна функція запуску аналізу через Streamlit
        st.set_page_config(layout="wide")
        df = self.data_frame()
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        st.title("Аналіз даних")

        view_option = st.sidebar.radio("Оберіть вид відображення", ["Таблиця", "Лінійний графік", "Теплова карта"])

        parameter = st.sidebar.selectbox("Оберіть параметр", ["VCI", "TCI", "VHI"])
        region = st.sidebar.selectbox("Оберіть регіон", list(self.regions_true_id.values()))

        years_interval = st.sidebar.slider("Інтервал років", 1981, 2025, (1981, 2025))
        weeks_interval = st.sidebar.slider("Інтервал тижнів", 1, 52, (1, 52))

        sort_asc = st.sidebar.checkbox('Sort Ascending')
        sort_desc = st.sidebar.checkbox('Sort Descending')

        filtered_data = self.filter_data(df, years_interval, weeks_interval, region, sort_asc, sort_desc, parameter)

        if view_option == "Таблиця":
            st.dataframe(filtered_data, use_container_width=True)

        elif view_option == "Лінійний графік":
            fig = self.plot_line_chart(filtered_data, parameter)
            st.pyplot(fig)

        elif view_option == "Теплова карта":
            fig = self.plot_heatmap(df, parameter, years_interval)
            st.pyplot(fig)

            
if __name__ == "__main__":
    analysis = VHIAnalysis()
    analysis.run_analysis()
