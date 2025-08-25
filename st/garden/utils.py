
# import requests
#
# def get_nbrb_rates():
#     url = "https://www.nbrb.by/api/exrates/rates?periodicity=0"
#     try:
#         resp = requests.get(url, timeout=5)
#         resp.raise_for_status()
#         data = resp.json()
#         rates = {}
#         wanted_codes = {'USD', 'EUR', 'RUB'}  # Коды валют, которые хотим получить
#         for item in data:
#             code = item['Cur_Abbreviation']
#             if code in wanted_codes:
#                 # учитываем, что курс даётся для Cur_Scale единиц валюты
#                 rate = item['Cur_OfficialRate'] / item['Cur_Scale']
#                 rates[code] = rate
#         return rates
#     except Exception:
#         return {}
