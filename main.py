from imports import AutomationDisposableUrlWithPlaywright, GetDisposableUrlWithTelegram, solve_by_color_extraction
import asyncio
from loguru import logger
import re
import json
import threading
import sys
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    enqueue=True
)
logger.add(
    "logs/logs.log",
    rotation="10 MB",
    enqueue=True,
    retention=5,
    encoding="utf-8"
)
def load_gift_links():
    with open('data/gift_links.txt', encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]

def load_sessions():
    with open('data/accounts.json', encoding="utf-8") as f:
        accounts = json.load(f)
    for session in accounts:
        session['name'] = f"sessions/{session['name']}"
    return accounts

async def main(acc, gift_links):
    try:
        session_name = acc['name']
        #заранее поднимаем браузер
        playwright = AutomationDisposableUrlWithPlaywright()
        await playwright.start()
        logger.success(f"[{session_name}] Успешно запустился браузер для сессии")
        #запускаем телезон
        print(acc['api_id'],acc['api_hash'],acc['name'])
        telethon = (GetDisposableUrlWithTelegram
            (
            api_id=acc['api_id'],
            api_hash=acc['api_hash'],
            session_name=acc['name'],
        ))
        status_client = await telethon.connect_and_auth()

        if not status_client:
            return False

        for gift_link in gift_links:
            gift_url = await telethon.get_disposable_url_with_telegram(gift_link)
            if not gift_url:
                logger.error(f"[{session_name}] Не смог получит однорозовую ссылку, Проблема со сессии")
                return False
            #await asyncio.sleep(999)
            #плайврайгхт
            await playwright.single_threaded_context(gift_url)
            logger.success(f"[{session_name}] Переходил к ссылку однорозовую в браузере")
            
            captcha_is = await playwright.open_captcha()
            if not captcha_is:
                continue
            logger.success(f"[{session_name}] открыл капчу")
            await playwright.screenshot_captcha()
            logger.success(f"[{session_name}] скриншотил капчу")
            captcha_passed = False
            for i in range(3):
                if i == 2:
                    logger.error(f"[{session_name}] оба попытка провален завершаем цикл")
                    break  # лиш 2 попыток
                logger.success(f"[{session_name}] передал скриншот к 2капчу")
                captcha_code = solve_by_color_extraction('captcha_png/entrance.png')
                if captcha_code:  # если 5 символов
                    logger.success(f"[{session_name}] получен код {captcha_code}")
                    await playwright.bypass_captcha(captcha_code)  # введем капчу код
                    logger.success(f"[{session_name}] ввёл код {captcha_code}")
                    status_true_captcha = await playwright.check_true_captcha()  # проверяем статус капчи
                    logger.success(f"[{session_name}] статус капчи = {status_true_captcha}")
                    if status_true_captcha:
                        logger.success(f"[{session_name}] капча решено")
                        captcha_passed = True
                        break  # если все ок решался тогда завершаем цикл
                    else:
                        logger.error(f"[{session_name}] капча не решено и перезагрузаем капчу {i + 1}/2")
                        await playwright.reload_captcha()  # капча нерешался перезагружаем капчу
                        continue  # начинаем следущий этап цикла
                else:  # ответ false тогда просто перезагружаем капчу
                    logger.error(
                        f"[{session_name}] получен неверный код меньше 5ых символов перезапускаем капчу попытка {i + 1}/2")
                    await playwright.reload_captcha()
                    continue


            if captcha_passed:
                logger.success(f"[{session_name}] Решил капчу {gift_link}")
            else:
                logger.critical(f"[{session_name}] Не смог решит капчу. Переходим к другую ссылку. Не получилось: {gift_link}")
                continue
            await asyncio.sleep(7)
            max = await playwright.max()
            if max:
                logger.success(f"[{session_name}] обрабатывал MAX {gift_link}")
            else:
                logger.success(f"[{session_name}] у {gift_link} нет MAX")
            await asyncio.sleep(1)
            logger.success(f"[{session_name}] Успешно обрабатывал ссылку {gift_link}")
        logger.success(f"[ВСЕ] успешно обрабатывал все ссылки завершаем сессию")
        return True
    except Exception as e:
        logger.error(f"[{acc}] Ошибка: {e}")
        return False
    finally:
        await playwright.close_context()
        await telethon.disconnect()

def run_therad(sessions_sheet: list[dict[str, any]], gift_links: list[str]):
    for session_sheet in sessions_sheet:
        asyncio.run(main(session_sheet, gift_links))
        # мейн принимает только сессию СТРИНГ и список ссылки

if __name__ == "__main__":
    count_threadings=int(input('Количество потоков -> '))
    gift_links=load_gift_links()  #ссылки 
    sessions = load_sessions() #список сессии
    whole_sessions = len(sessions) //  count_threadings   # длина сессии делём на потока   заберем -> весь    қазақша бүтінін аламыз тек
    remainder_sessions = len(sessions) % count_threadings # длина сессии заберем остаток
    threads = []
    for count_threading in range(count_threadings):
        future_number_of_sessions_transferred_to_the_list=0
        future_number_of_sessions_transferred_to_the_list+=whole_sessions     # добавляем весь
        if remainder_sessions >= 1: # если остаток больше 1 или равен
            future_number_of_sessions_transferred_to_the_list += remainder_sessions #добавляем один из остатков
            remainder_sessions-=1   # и уберем один остаток чтоб не мешал к другим
        future_sessions_transferred_to_the_list = sessions[:future_number_of_sessions_transferred_to_the_list] #добавляем настоящий сессии используя нужные готовыеколичество
        del sessions[:future_number_of_sessions_transferred_to_the_list] #удаляем взятые сессии из основного списка sessions
        thread = threading.Thread(target=run_therad,
            args=(future_sessions_transferred_to_the_list, gift_links),
            daemon=True)   #даемон труе не ждем запускаем все потоки сразу
        threads.append(thread)
        thread.start()
        # run thread требует СПИСОК настоящих сессии 
    for thread in threads:
        thread.join()
