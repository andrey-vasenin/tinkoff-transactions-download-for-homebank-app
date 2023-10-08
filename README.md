# Автоматическая загрузка транзакции из аккаунта Tinkoff для использования в программе HomeBank

Этот скрипт написан для автоматической загрузки файла ofx с транзакциями по личным счетам банка Tinkoff за текущий месяц. Скачанные транзакции на русском дополнительно транслителируются латинским алфавитом, чтобы потом загрузить их в программу [HomeBank](http://homebank.free.fr/ru/index.php) ( бесплатное программное обеспечение, которое помогает вести свой личный бухгалтерский учет).

## Предварительные установки

* **selenium** — python-модуль для управления движком chrome). Установить можно через `pip install selenium`
* **ChromeDriver** — движок браузера Google Chrome. Его нужно скачать здесь [https://googlechromelabs.github.io/chrome-for-testing/](https://googlechromelabs.github.io/chrome-for-testing/). Версия скачанного движка обязана совпадать с версией установленного браузера Google Chrome, иначе не заработает. Скачанный .zip-архив распаковать и поместить .exe-файл в корневой каталог, где находится скрипт `update_my_transactions.py`

## Как пользоваться

* Запустить с помощью `python update_my_transactions.py`
* Откроется новое окно браузера Google Chrome, в котором будет открыта страница для входа в личный кабинет банка Тинькофф. При этом будет создан новый профиль для браузера. Необходимо залогиниться
* Остальные действия по скачиванию .ofx файла выполнит скрипт. Их можно наблюдать в окне браузера, но переключения могут быть слишком быстрыми
* В результате в папке `downloads`, которая находится в том же каталоге, где скрипт, будут лежать минимум два файла (больше если там были предыдущие загрузки). Один файл &mdash; загруженный ofx файл, а второй &mdash; транслителированый, который можно отдавать программе HomeBank

## Логика работы скрипта
1. Создание необходимых папок для профиля, кукис и загрузок в корневом каталоге
1. Запуск нового окна браузера
1. Открытие страницы для входа 
1. Дожидание пока пользователь не залогинится
1. Перейти на страницу с транзакциями
1. Нажимение на кнопку экспорта
1. Наживание на кнопку для выгрузки OFX
1. Загрузка файла в папку `download_dir`, которая по умолчанию `downloads`
1. Сохранение кукис и закрытие браузера
1. Транслитерация скачанного OFX файла