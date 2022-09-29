from email.message import MIMEPart
from email.mime import image
import requests
import json
import schedule
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from urllib import parse, request
from bs4 import BeautifulSoup


def call_url():
    auth_token = "NTJkYzEzZjQtMGI5Mi00M2Y0LThmYWQtYjlmN2U3ZDIyY2Zh"
    data = {"days": "1", "location": "Streetsboro, OH"}
    url = "https://api.m3o.com/v1/weather/Forecast"
    headers = {
        "Content-Type": "application/json",
        'Authorization': 'Bearer ' + auth_token,
    }
    resp = requests.get(url, headers=headers, params=data).content
    readable = json.loads(resp)

    return readable


# def get_weather():
def get_weather():
    url = "https://www.wunderground.com/weather/us/oh/streetsboro"
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    current_temp = soup.find("span",  attrs={
                             'class': "wu-value wu-value-to"}).text
    hi_temp = soup.find("span",  attrs={'class': "hi"}).text

    resp = call_url()
    location = resp['location']
    for result in resp['forecast']:
        date = result['date']
        high = result['max_temp_f']
        low = result['min_temp_f']
        condition = result['condition']
        conditions = condition.strip('{}')
        will_it_rain = result['will_it_rain']
        if will_it_rain == True:
            chance_of_rain = result['chance_of_rain']
        else:
            will_it_rain = "None"
            chance_of_rain = result['chance_of_rain']
        sun_rise = result['sunrise']
        sun_set = result['sunset']

        # use string formatting to print the results
        # print(f"Date: {date}, High: {high}, Low: {low}, {conditions}, Will it rain: {will_it_rain}, Chance of rain: {chance_of_rain}, Sun Rise: {sun_rise}, Sun Set: {sun_set}")
    return location, date, high, low, conditions, will_it_rain, chance_of_rain, sun_rise, sun_set, current_temp, hi_temp


get_weather()


def get_daily_gif():
    url = "http://api.giphy.com/v1/gifs/trending"

    params = parse.urlencode({
        "api_key": "GZ6Wdvdb9V8ZoH6EdtN3tsiLbb1n8FsI",
        "limit": "2"
    })

    with request.urlopen("".join((url, "?", params))) as response:
        data = json.loads(response.read())

    image_cid = data['data'][0]['id']
    image_url = data['data'][1]['images']['original']['url']
    return image_url


get_daily_gif()


def get_quote():
   # url = 'https://api.quotable.io/random'
    url = 'https://zenquotes.io/api/today'
    resp = requests.get(url).content
    readable = json.loads(resp)
    # quote = readable['content']
    # author = readable['author']
    quote = readable[0]['q']
    author = readable[0]['a']
    return quote, author


def send_email():
    location, date, high, low, conditions, will_it_rain, chance_of_rain, sun_rise, sun_set, current_temp, hi_temp = get_weather()
    quote, author = get_quote()

    sender_email = 'csdj92@gmail.com'
    sender_name = 'Daily Report'

    receiver_email = 'micheleann1017@gmail.com'
    receiver_name = 'Michele'

    image_cid = get_daily_gif()

    subject = "Daily Report"
    body = '''Here is your Daily Report.<br><br>The Weather conditions for {date} are, {conditions}<br>The current tempature is {current_temp}°F<br>The high temperature is {hi_temp}F and the low temperature is {low}°F. <br>Precipitation: {will_it_rain} and there is a {chance_of_rain} chance of rain.<br>Sunrise is at {sun_rise} and sunset is at {sun_set}.<br><br><br>Love,<br>Your Husband <br><br>Quote Of The Day: {quote}<br>~{author}<br><br>
         <img src="{image_cid}">'''.format(image_cid=image_cid, date=date, conditions=conditions, high=high, low=low, will_it_rain=will_it_rain, chance_of_rain=chance_of_rain, sun_rise=sun_rise, sun_set=sun_set, current_temp=current_temp, quote=quote, author=author, hi_temp=hi_temp)

    msg = MIMEText(body, 'html')
    msg['To'] = formataddr((receiver_name, receiver_email))
    msg['From'] = formataddr((sender_name, sender_email))
    msg['Subject'] = subject
    try:
        # sending the mail
        smtp_object = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_object.starttls()
        smtp_object.login("csdj92@gmail.com", "yolnbkemalggjcez")
        smtp_object.sendmail(sender_email, receiver_email, msg.as_string())

        # terminating the session
        smtp_object.quit()
        print("Email Sent!")
    except Exception as e:
        print("Error: unable to send email", e)


def main():
    schedule.every().day.at("07:00").do(send_email)
    while True:
        schedule.run_pending()


if __name__ == "__main__":
    main()
