
from translate.translator import Translator

if __name__ == "__main__":
    translate_client = Translator(target="zh-CN", source="en", proxies={"http": "http://127.0.0.1:7890"})

    trans_response = translate_client.translate(q="Time is flying by")

    assert trans_response.translatedText == "时间飞逝"

    trans_responses = translate_client.translate(q=["Time is flying by", "Remembrance of Things Past"])

    assert [response.translatedText for response in trans_responses] == [
        "时间飞逝",
        "追忆逝水年华"
    ]
