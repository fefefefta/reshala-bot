# reshala-bot
Бот для нелегального решальского бизнеса

## Установка
1. Поставить окружение и установить зависимости
```
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```
2. Запустить ботяру
```
python bot.py
```
2*. Запустить в фоне с помощью какой-то умной утилиты. Я заюзаю screen
```
screen
python bot.py
```
Для выхода из сессии скрина (работа бота продолжится в фоне) нажмите Ctrl+a Ctrl+d.
Для возвращения в сессию:
```
screen -r {имя сессии}
```
Чтобы узнать имя сессии:  screen -ls
