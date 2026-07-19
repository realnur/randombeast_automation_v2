import sys
import os
from twocaptcha import TwoCaptcha

from dotenv import load_dotenv
load_dotenv()
#api_key_2captcha = os.getenv("API_KEY")
api_key_2captcha = "eb21cc898e9d23f0aec37aa71785abd3"

api_key = os.getenv('APIKEY_2CAPTCHA', api_key_2captcha)
solver = TwoCaptcha(api_key)
def solve_by_color_extraction(image_path):
    try:
        result = solver.normal(image_path)['code']
        print(result)
        text = "".join(result.split())
        print(text)
        if len(text) == 5:
            return text
        else:
            return False
    except Exception as e:
        return False


if __name__ == '__main__':
    print(solve_by_color_extraction('entrance.png'))
