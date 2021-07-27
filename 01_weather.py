# -*- coding: utf-8 -*-

# В очередной спешке, проверив приложение с прогнозом погоды, вы выбежали
# навстречу ревью вашего кода, которое ожидало вас в офисе.
# И тут же день стал хуже - вместо обещанной облачности вас встретил ливень.

# Вы промокли, настроение было испорчено, и на ревью вы уже пришли не в духе.
# В итоге такого сокрушительного дня вы решили написать свою программу для прогноза погоды
# из источника, которому вы доверяете.

# Для этого вам нужно:

# Создать модуль-движок с классом WeatherMaker, необходимым для получения и формирования предсказаний.
# В нём должен быть метод, получающий прогноз с выбранного вами сайта (парсинг + re) за некоторый диапазон дат,
# а затем, получив данные, сформировать их в словарь {погода: Облачная, температура: 10, дата:datetime...}
import os
import time
import cv2
import peewee
import requests
from termcolor import cprint
from PIL import Image
from bs4 import BeautifulSoup

# Создал три константы. Список с погодой, Весь список с погодой, Месяца
# TODO поменял все "\\" на "/"
WEATHER_DESCRIPTION = []
ALL_WEATHER = []
MONTHS = ['january', 'february', 'march', 'april', 'may', 'june ',
          'july', 'august', 'september', 'october', 'november', 'december']

# Создаём базу.
database = peewee.SqliteDatabase('Weather_db.db')


class Weather(peewee.Model):
    date = peewee.DateTimeField()
    temperature = peewee.CharField()
    weather_description = peewee.CharField()

    class Meta:
        database = database


Weather.create_table([Weather])


def get_month():
    while True:
        try:
            month = int(input('За какой месяц вывести погоду: '))
            return MONTHS[month - 1]
        except Exception:
            cprint('Вы указали неверно месяц, указали ничего или вписали буквы. '
                   'Введите месяц ввиде цифр от 1-12', color='red')
            continue


def get_year():
    while True:
        year = int(input('За какой год вывести погоду: '))
        if 2009 <= year <= int(time.strftime("%Y")):
            return year
        else:
            cprint(f'За указанный вами год, нет акутальной информации. Информация есть с 2009 по '
                   f'{time.strftime("%Y")} год и {time.strftime("%m")} месяц.', color='red')
            continue


class WeatherMaker:

    def __init__(self):
        self.dict_data = {'погода': '', 'температура': '', 'дата': ''}

    def weather(self):
        # Отправляем get запрос
        get_the_response = requests.get(f'https://pogoda.mail.ru/prognoz/moskva/{get_month()}-{get_year()}/')
        # print(get_the_response)
        html_doc = BeautifulSoup(get_the_response.text, features='html.parser')
        # Вытягиваем данные по тегу div
        list_of_date = html_doc.find_all('div', {'class': 'day__date'})
        list_of_temperature = html_doc.find_all('div', {'class': 'day__temperature'})
        list_of_description = html_doc.find_all('div', {'class': 'day__description'})
        # Делам проход циклом for по темп., дате и погоде и заносим инфо. в базу.
        for temperature, date, description in zip(list_of_temperature, list_of_date, list_of_description):
            self.dict_data['температура'] = temperature.text.split()[0]
            self.dict_data['погода'] = description.text.split()[0]
            if "Сегодня" in date.text:
                self.dict_data['дата'] = (date.text[8:])
                # Вносим данные в БД
                Weather.create(
                    date=self.dict_data['дата'],
                    temperature=self.dict_data['температура'],
                    weather_description=self.dict_data['погода'])
                continue
            self.dict_data['дата'] = date.text
            # Вносим данные в БД
            Weather.create(
                date=self.dict_data['дата'],
                temperature=self.dict_data['температура'],
                weather_description=self.dict_data['погода'])
        if self.dict_data['дата'][:2] == '':
            cprint('В выбранном диапазоне нет информации о погоде! Укажите текущий месяц', color='red')
            WeatherMaker().weather()

    # Делаем перезапись.
    Weather.delete().where(Weather.id).execute()


# Добавить класс ImageMaker.
# Снабдить его методом рисования открытки
# (использовать OpenCV, в качестве заготовки брать lesson_016/python_snippets/external_data/probe.jpg):
#   С текстом, состоящим из полученных данных (пригодится cv2.putText)
#   С изображением, соответствующим типу погоды
# (хранятся в lesson_016/python_snippets/external_data/weather_img ,но можно нарисовать/добавить свои)
#   В качестве фона добавить градиент цвета, отражающего тип погоды
# Солнечно - от желтого к белому
# Дождь - от синего к белому
# Снег - от голубого к белому
# Облачно - от серого к белому
class ImageMaker:

    def __init__(self):
        self.gradient_x1 = -500
        self.gradient_x2 = 0
        self.gradient_y1 = 0
        self.gradient_y2 = 300
        self.r, self.g, self.b = 0, 0, 0
        self.image = cv2.imread('python_snippets/external_data/probe.jpg')
        self.font = cv2.FONT_HERSHEY_COMPLEX

    def draw_postcard(self, weather_for_postcard):
        # Задём изначальные цвета
        if weather_for_postcard == 'ясно':
            self.g += 255
            self.r += 255
        elif weather_for_postcard == 'осадки' or weather_for_postcard == 'дождь' \
                or weather_for_postcard == 'дождь/гроза':
            self.b += 125
        elif weather_for_postcard == 'снег':
            self.b += 255
        elif weather_for_postcard == 'облачно':
            self.b, self.g, self.r = 80, 80, 80
        else:
            self.b, self.g, self.r = 255, 255, 255
        # Делаем 70 итерации циклом for
        for _ in range(70):
            cv2.line(self.image, (self.gradient_x1, self.gradient_y1), (self.gradient_x2, self.gradient_y2),
                     (self.b, self.g, self.r), 10)
            if weather_for_postcard == 'ясно':
                self.b += 6
            elif weather_for_postcard == 'осадки' or weather_for_postcard == 'дождь' \
                    or weather_for_postcard == 'дождь/гроза':
                self.r += 5
                self.g += 5
                self.b += 3
            elif weather_for_postcard == 'снег':
                self.r += 5
                self.g += 5
            elif weather_for_postcard == 'облачно':
                self.r += 3
                self.g += 3
                self.b += 3
            self.gradient_x1 += 15
            self.gradient_x2 += 15
        # Теперь создаём открытку и закидываем готовый вариант в текущую папку (откуда запускали программу)
        if weather_for_postcard == 'ясно':
            cv2.imwrite('sun_background.jpg', self.image)
            # Вставляем текст на фон
            output = cv2.imread('sun_background.jpg')
            cv2.putText(output, "Погода:", (180, 40), self.font, 1, (0, 0, 0), 1)
            cv2.putText(output, f'{WEATHER_DESCRIPTION[day - 1].weather_description}',
                        (220, 80), self.font, 0.60, (0, 0, 0), 1)
            cv2.putText(output, f'{WEATHER_DESCRIPTION[day - 1].temperature[:-1]}',
                        (130, 180), self.font, 3, (0, 0, 0), 1)
            cv2.putText(output, f'{WEATHER_DESCRIPTION[day - 1].date}',
                        (180, 230), self.font, 0.60, (0, 0, 0), 1)
            cv2.imwrite('sun_background_with_txt.jpg', output)
            # Открываем солнышко и фон
            foreground = Image.open("icons_for_postcards/sun.jpg")
            background = Image.open('sun_background_with_txt.jpg')
            # Задаём координаты
            background_width, background_height = background.size[0], background.size[1]
            foreground_width, foreground_height = foreground.size[0], foreground.size[1]
            x, y = background_width - foreground_width, 0
            # Вставляем солнышко в правый верхний угол на фон
            background.paste(foreground, (x, y))
            # Сохраняем итог
            background.save(f'{WEATHER_DESCRIPTION[day - 1].date}_sun_postcard.jpg', 'JPEG')
            # удаляем ненужные нам файлы
            os.remove(os.path.abspath('sun_background.jpg'))
            os.remove(os.path.abspath('sun_background_with_txt.jpg'))
        elif weather_for_postcard == 'осадки' or weather_for_postcard == 'дождь' \
                or weather_for_postcard == 'дождь/гроза':
            cv2.imwrite('precipitation_background.jpg', self.image)
            # Вставляем текст на фон
            output = cv2.imread('precipitation_background.jpg')
            cv2.putText(output, "Погода:", (180, 40), self.font, 1, (0, 0, 0), 1)
            cv2.putText(output, f'{WEATHER_DESCRIPTION[day - 1].weather_description}',
                        (180, 80), self.font, 0.60, (0, 0, 0), 1)
            cv2.putText(output, f'{WEATHER_DESCRIPTION[day - 1].temperature[:-1]}',
                        (130, 180), self.font, 3, (0, 0, 0), 1)
            cv2.putText(output, f'{WEATHER_DESCRIPTION[day - 1].date}',
                        (180, 230), self.font, 0.60, (0, 0, 0), 1)
            cv2.imwrite('precipitation_background_with_txt.jpg', output)
            # Открываем солнышко и фон
            foreground = Image.open("icons_for_postcards/rain.jpg")
            background = Image.open('precipitation_background_with_txt.jpg')
            # Задаём координаты
            background_width, background_height = background.size[0], background.size[1]
            foreground_width, foreground_height = foreground.size[0], foreground.size[1]
            x, y = background_width - foreground_width, 0
            # Вставляем солнышко в правый верхний угол на фон
            background.paste(foreground, (x, y))
            # Сохраняем итог
            background.save(f'{WEATHER_DESCRIPTION[day - 1].date}_precipitation_postcard.jpg', 'JPEG')
            # удаляем ненужные нам файлы
            os.remove(os.path.abspath('precipitation_background.jpg'))
            os.remove(os.path.abspath('precipitation_background_with_txt.jpg'))
        elif weather_for_postcard == 'снег':
            cv2.imwrite('snow_background.jpg', self.image)
            # Вставляем текст на фон
            output = cv2.imread('snow_background.jpg')
            cv2.putText(output, "Погода:", (180, 40), self.font, 1, (0, 0, 0), 1)
            cv2.putText(output, f'{WEATHER_DESCRIPTION[day - 1].weather_description}',
                        (220, 80), self.font, 0.60, (0, 0, 0), 1)
            cv2.putText(output, f'{WEATHER_DESCRIPTION[day - 1].temperature[:-1]}',
                        (130, 180), self.font, 3, (0, 0, 0), 1)
            cv2.putText(output, f'{WEATHER_DESCRIPTION[day - 1].date}',
                        (180, 230), self.font, 0.60, (0, 0, 0), 1)
            cv2.imwrite('snow_background_with_txt.jpg', output)
            # Открываем солнышко и фон
            foreground = Image.open("icons_for_postcards/snow.jpg")
            background = Image.open('snow_background_with_txt.jpg')
            # Задаём координаты
            background_width, background_height = background.size[0], background.size[1]
            foreground_width, foreground_height = foreground.size[0], foreground.size[1]
            x, y = background_width - foreground_width, 0
            # Вставляем солнышко в правый верхний угол на фон
            background.paste(foreground, (x, y))
            # Сохраняем итог
            background.save(f'{WEATHER_DESCRIPTION[day - 1].date}_snow_postcard.jpg', 'JPEG')
            # удаляем ненужные нам файлы
            os.remove(os.path.abspath('snow_background.jpg'))
            os.remove(os.path.abspath('snow_background_with_txt.jpg'))
        elif weather_for_postcard == 'облачно':
            cv2.imwrite('cloudy_background.jpg', self.image)
            # Вставляем текст на фон
            output = cv2.imread('cloudy_background.jpg')
            cv2.putText(output, "Погода:", (180, 40), self.font, 1, (0, 0, 0), 1)
            cv2.putText(output, f'{WEATHER_DESCRIPTION[day - 1].weather_description}',
                        (200, 80), self.font, 0.60, (0, 0, 0), 1)
            cv2.putText(output, f'{WEATHER_DESCRIPTION[day - 1].temperature[:-1]}',
                        (130, 180), self.font, 3, (0, 0, 0), 1)
            cv2.putText(output, f'{WEATHER_DESCRIPTION[day - 1].date}',
                        (180, 230), self.font, 0.60, (0, 0, 0), 1)
            cv2.imwrite('cloudy_background_with_txt.jpg', output)
            # Открываем солнышко и фон
            foreground = Image.open("icons_for_postcards/cloud.jpg")
            background = Image.open('cloudy_background_with_txt.jpg')
            # Задаём координаты
            background_width, background_height = background.size[0], background.size[1]
            foreground_width, foreground_height = foreground.size[0], foreground.size[1]
            x, y = background_width - foreground_width, 0
            # Вставляем солнышко в правый верхний угол на фон
            background.paste(foreground, (x, y))
            # Сохраняем итог
            background.save(f'{WEATHER_DESCRIPTION[day - 1].date}_cloudy_postcard.jpg', 'JPEG')
            # удаляем ненужные нам файлы
            os.remove(os.path.abspath('cloudy_background.jpg'))
            os.remove(os.path.abspath('cloudy_background_with_txt.jpg'))


# Добавить класс DatabaseUpdater с методами:
#   Получающим данные из базы данных за указанный диапазон дат.
#   Сохраняющим прогнозы в базу данных (использовать peewee)
class DatabaseUpdater:

    def __init__(self):
        self.forecasts = Weather.select()

    def weather_description(self):
        for forecast in self.forecasts:
            WEATHER_DESCRIPTION.append(forecast)

    def show_weather_description(self):
        start_num = int(input('\nС какого числа вывести прогноз погоды: '))
        end_num = int(input('По какое число вывести прогноз погоды: '))
        cprint(f'Показываю погоду за указанный вами диапазон дат', color='green')
        for _weather in self.forecasts[start_num - 1:end_num]:
            cprint(f"'погода': {_weather.weather_description}, 'температура': {_weather.temperature}, "
                   f"'дата': {_weather.date}", color='yellow')
            ALL_WEATHER.append(f"'погода': {_weather.weather_description}, 'температура': {_weather.temperature}, "
                               f"'дата': {_weather.date}")


# Запускаем программу
# WeatherMaker().weather()
# ImageMaker().draw_postcard('осадки')
# DatabaseUpdater().get_data_of_database()

# Сделать программу с консольным интерфейсом, постаравшись все выполняемые действия вынести в отдельные функции.
# Среди действий, доступных пользователю, должны быть:
#   Добавление прогнозов за диапазон дат в базу данных
#   Получение прогнозов за диапазон дат из базы
#   Создание открыток из полученных прогнозов
#   Выведение полученных прогнозов на консоль
# При старте консольная утилита должна загружать прогнозы за прошедшую неделю.
WeatherMaker().weather()
run = True
image_maker = ImageMaker()
weather_dt = Weather()
weather = WeatherMaker()
db_updater = DatabaseUpdater()
cprint('Погода добавлена за весь указанный вами месяц в базу данных', color='green')
while run:
    cprint('\nВы можете: \n'
           '1. Получить прогнозы за диапазон дат из базы данных \n'
           '2. Создать открытки из полученных прогнозов \n'
           '3. Вывести полученные прогнозы на консоль \n'
           '4. Закончить работу с приложением \n', color='blue')
    choice = input('Пожалуйста введите номер желаемого действия: ')
    if choice == '1':
        db_updater.show_weather_description()
    elif choice == '2':
        day = int(input('\nЗа какое число сделать открытку: '))
        db_updater.weather_description()
        image_maker.draw_postcard(WEATHER_DESCRIPTION[day - 1].weather_description)
        cprint('Открытка будет создана в корневой папке "lesson_016" после завершения программы', color='green')
    elif choice == '3':
        cprint(f'\nВот вся история запрошенных дат', color='green')
        cprint('\n'.join(ALL_WEATHER), color='yellow')
    elif choice == '4':
        cprint('\nПрощай, надеюсь я помог :)', color='green')
        run = False
    else:
        cprint('\nИзвините, я не могу распознать вашу команду, попробуйте еще раз', color='red')

# Рекомендации:
# Можно создать отдельный модуль для инициализирования базы данных.
# Как далее использовать эту базу данных в движке:
# Передавать DatabaseUpdater url-путь
# https://peewee.readthedocs.io/en/latest/peewee/playhouse.html#db-url
# Приконнектится по полученному url-пути к базе данных
# Инициализировать её через DatabaseProxy()
# https://peewee.readthedocs.io/en/latest/peewee/database.html#dynamically-defining-a-database


# Отлично!

# зачет!
