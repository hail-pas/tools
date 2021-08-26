"""
HPV 预约脚本
"""
from datetime import datetime
from json.decoder import JSONDecodeError
from urllib.parse import quote

from requests import sessions

HEADERS = {
    "host": "cloud.cn2030.com",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.11(0x18000b26) NetType/WIFI Language/zh_CN",
    "Referer": "https://servicewechat.com/wx2c7f0f3c30d99445/79/page-frame.html",
    "Content-Type": "application/json",
    "Accept-Encoding": "gzip,compress,br,deflate",
    "Cache-Control": "no-cache",
    # 需要手动更新
    "zftsl": "e2b890b71bf6991774173388bf1ba938",
}
COOKIES = {
    "ASP.NET_SessionId": "ouu2zxxiyzx0xibwu1khciuu"
}
URL = "https://cloud.cn2030.com/sc/wx/HandlerSubscribe.ashx"


def get_response(params: dict = None, url: str = None):
    with sessions.Session() as session:
        session.cookies.update(COOKIES)
        session.headers = HEADERS
        if params:
            session.params = params
        res = session.get(url=URL if not url else url)

    if res.status_code == 200:
        try:
            res = res.json()
            if res.get("status") == 200:
                return res.get("list")
        except JSONDecodeError:
            pass
    print("\n\nAbnormal Response: \n", res.text if getattr(res, "text", None) else res, "\n\n")


def get_appointment_category():
    params = {
        "act": "GetCat1"
    }
    return get_response(params)


def get_hospitals(product: int = 0):
    """
    customer list
    :return:
    """
    return get_response(
        url="https://cloud.cn2030.com/sc/wx/HandlerSubscribe.ashx?act=CustomerList&city=%5B%22%22%2C%22%22%2C%22%22%5D&lat=29.717979431152344&lng=106.63043212890625&cityCode=0&product=0&id=0")


def get_product_of_hospital(hospital_id):
    params = {
        "act": "CustomerProduct",
        "id": hospital_id,
        "lat": "29.717979431152344",
        "lng": "106.63043212890625"
    }
    return get_response(params=params)


def get_product_appointment_date(hospital_id, product_id):
    params = {
        "act": "GetCustSubscribeDateAll",
        "id": hospital_id,
        "pid": product_id,
        "month": f"{datetime.now().year}{f'0{datetime.now().month}' if datetime.now().month < 10 else datetime.now().month}"
    }
    return get_response(params=params)


def get_product_appointment_date_detail(hospital_id, product_id, date):
    """
    {
        "status": 200,
        "id": 1824,
        "customer": "惠州市仲恺区陈江社区卫生服务中心",
        "list": [{
            "customer": "惠州市仲恺区陈江社区卫生服务中心",
            "customerid": 1824,
            "StartTime": "08:10:00",
            "EndTime": "11:00:00",
            "mxid": "TzrAAB1QAACLZDQB",
            "qty": 38 // 余量
            }, {
            "customer": "惠州市仲恺区陈江社区卫生服务中心",
            "customerid": 1824,
            "StartTime": "14:40:00",
            "EndTime": "16:40:00",
            "mxid": "TzrAAB9QAACLZDQB",
            "qty": 20
            }],
        "ver": "2.0"
    }
    :param hospital_id:
    :param product_id:
    :param date:
    :return:
    """

    params = {
        "act": "GetCustSubscribeDateDetail",
        "id": hospital_id,
        "pid": product_id,
        "scdate": date
    }
    return get_response(params=params)


def get_captcha(mxid):
    """

    :return:
    """
    params = {
        "act": "GetCaptcha",
        "mxid": mxid,
    }
    return get_response(params=params)


def verify_captcha(x, y, mxid):
    """
    {
        "guid": "",
        "status": 200,
        "msg": "验证成功"
    }
    :return:
    """
    "act=CaptchaVerify&token=&x=197&y=5&mxid=TzrAAB9QAACPZDQB"
    params = {
        "act": "CaptchaVerify",
        "token": "",
        "x": x,
        "y": y,
        "mxid": mxid
    }


def appointment_apply(name, birthday, tel, idcard, mxid, date, pid, guid, Ftime=1):
    """
    {
        "status": 200,
        "message": "提交成功"
    :return:
    """
    url = f"https://cloud.cn2030.com/sc/wx/HandlerSubscribe.ashx?act=Save20&birthday={birthday}&tel={tel}&sex=2&cname={quote(name)}&doctype=1&idcard={idcard}&mxid={mxid}&date={date}&pid={pid}&Ftime={Ftime}&guid={guid}"
    "guid=e0dd512f-a648-4a63-bb11-5dac974b7a3a"
    params = {
        "act": "Save",
        "birthday": birthday,
        "tel": tel,
        "sex": 2,  # 女
        "cname": name,
        "doctype": 1,  # 证件类型
        "idcard": idcard,
        "mxid": mxid,
        "date": date,
        "pid": pid,
        "Ftime": Ftime,  # 接种针次
        "guid": guid
    }
    return get_response(params=params)


if __name__ == "__main__":
    # print(get_appointment_category())
    # print(get_hospitals())
    # print(get_product_of_hospital(71))
    # print(get_product_appointment_date(1885, 64))
    # print(get_product_appointment_date_detail(1824, 54, "2021-08-26"))
    # print(appointment_apply())
    print(get_captcha("TzrAAB9QAACPZDQB"))
