import csv

import requests
from bs4 import BeautifulSoup

headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                   " Chrome/98.0.4758.109 Safari/537.36 OPR/84.0.4316.42"
}

field_names = ['Num of kernels', 'Base frequency', 'RAM', 'SSD', 'Card', 'HDD', 'Price', 'Name', 'Diagonal']


def scrap_laptop_details_from_hot_line(url="https://hotline.ua/computer/noutbuki-netbuki/",
                                       csv_file_name="Data Import/items.csv",
                                       is_new_file=True):
    """ Scrap laptop characteristics to .csv file

        Keyword arguments:
        url -- link to laptops on HotLine. Can include filters that will be used while scrapping.
        csv_file_name -- name of the file where data will be stored.
        is_additional_data -- flag, when True file will be recreated, when False - data will be added in the end

        Doesn't return anything

    """

    source_code = requests.get(url, headers=headers)
    soup = BeautifulSoup(source_code.text, "lxml")
    page_count = int(soup.find_all("a", class_="pages")[-1].text.strip()) - 1

    if is_new_file:
        with open(csv_file_name, 'w', encoding='UTF-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=field_names)
            writer.writeheader()

    for page in range(1, page_count + 1):

        url = f"{url}?p={page}"
        source_code = requests.get(url, headers=headers)
        soup = BeautifulSoup(source_code.text, "lxml")

        items = []

        all_items = soup.find("ul", class_="products-list cell-list").find_all("li", class_="product-item")

        for item in all_items:
            item_characteristic = dict.fromkeys(field_names, None)
            try:
                url = "https://hotline.ua" + item.find("a", class_="item-img-link").get("href") + "?tab=about"

                source_code = requests.get(url, headers=headers)
                soup = BeautifulSoup(source_code.text, "lxml")

                item_characteristic["Price"] = item.find("div", class_="price-md").text.strip()
                item_characteristic["Name"] = item.find("div", class_="item-info").find("p",class_="h4").text.strip()

                all_characteristics = soup.find("table", class_="specifications__table").find_all("td")
                for i_characteristic in range(len(all_characteristics)):
                    characteristic = all_characteristics[i_characteristic].text.strip().split(":")[0]
                    if characteristic == "Діагональ, дюймів":
                        item_characteristic["Diagonal"] = all_characteristics[i_characteristic + 1].text.strip()
                    elif characteristic == "Базова тактова частота, ГГц":
                        item_characteristic["Base frequency"] = all_characteristics[i_characteristic + 1].text.strip()
                    elif characteristic == "Кількість ядер процесора":
                        item_characteristic["Num of kernels"] = all_characteristics[i_characteristic + 1].text.strip()
                    elif characteristic == "Оперативна пам'ять, ГБ":
                        item_characteristic["RAM"] = all_characteristics[i_characteristic + 1].text.strip()
                    elif characteristic == "Жорсткий диск, ГБ":
                        item_characteristic["HDD"] = all_characteristics[i_characteristic + 1].text.strip()
                    elif characteristic == "SSD, ГБ":
                        item_characteristic["SSD"] = all_characteristics[i_characteristic + 1].text.strip()
                    elif characteristic == "Графічний адаптер, об'єм пам'яті":
                        item_characteristic["Card"] = all_characteristics[i_characteristic + 1].text.strip()

                print(f"On page {page}/{page_count} looking for {item_characteristic['Name']}")

                items.append(item_characteristic)
            except:
                continue

        with open(csv_file_name, 'a', encoding='UTF-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writerows(items)


if __name__ == "__main__":
    scrap_laptop_details_from_hot_line()
