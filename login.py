import mechanize
from http.cookiejar import CookieJar
cj =CookieJar()
br = mechanize.Browser()
br.set_cookiejar(cj)
br.open("https://jobinja.ir/login/user?redirect_url=https%3A%2F%2Fjobinja.ir%2Fjobs%3Ffilters%255Bjob_categories%255D%2"
        "55B0%255D%3D%25D9%2588%25D8%25A8%25D8%258C%25E2%2580%258C%2520%25D8%25A8%25D8%25B1%25D9%2586%25D8%25A7%25D9%258"
        "5%25D9%2587%25E2%2580%258C%25D9%2586%25D9%2588%25DB%258C%25D8%25B3%25DB%258C%2520%25D9%2588%2520%25D9%2586%25D8"
        "%25B1%25D9%2585%25E2%2580%258C%25D8%25A7%25D9%2581%25D8%25B2%25D8%25A7%25D8%25B1%26filters%255Bkeywords%255D%25"
        "5B0%255D%3D%26filters%255Blocations%255D%255B0%255D%3D%25D8%25AA%25D9%2587%25D8%25B1%25D8%25A7%25D9%2586%26page"
        "%3D2%26sort_by%3Dpublished_at_desc&return_url=https%3A%2F%2Fjobinja.ir%2Fjobs%3Ffilters%255Bjob_categories%255D"
        "%255B0%255D%3D%25D9%2588%25D8%25A8%25D8%258C%25E2%2580%258C%2520%25D8%25A8%25D8%25B1%25D9%2586%25D8%25A7%25D9%2"
        "585%25D9%2587%25E2%2580%258C%25D9%2586%25D9%2588%25DB%258C%25D8%25B3%25DB%258C%2520%25D9%2588%2520%25D9%2586%25"
        "D8%25B1%25D9%2585%25E2%2580%258C%25D8%25A7%25D9%2581%25D8%25B2%25D8%25A7%25D8%25B1%26filters%255Bkeywords%255D%"
        "255B0%255D%3D%26filters%255Blocations%255D%255B0%255D%3D%25D8%25AA%25D9%2587%25D8%25B1%25D8%25A7%25D9%2586%26"
        "page%3D2%26sort_by%3Dpublished_at_desc")
br.select_form(nr=0)
br.form['identifier'] = 'sh.mohammad66@yahoo.com'
br.form['password'] = '123456sH'
br.submit()

# print(br.response().read().decode('utf-8'))