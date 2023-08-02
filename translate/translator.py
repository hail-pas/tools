"""通过调用 ``google.com`` | ``google.cn`` web接口进行翻译
"""
import time
import random
import requests
from typing import List, Union, overload, Dict


class Null:
    """
    :param response: 请求失败的 :class:`requests.Response` 对象
    """

    def __init__(self, response: requests.Response):
        self.response = response
        self.msg = f'{self.response.status_code}: {requests.status_codes._codes[self.response.status_code]}\n{self.response.text}'

    def __repr__(self):
        return self.msg


class DetectResponse:
    """DetectResponse"""

    def __init__(self, language: str, isReliable: bool = True, confidence: float = 1.0):
        """

        :param language: 检测到的语言
        """

        self.language = language
        self.isReliable = isReliable
        self.confidence = confidence

    def __repr__(self):
        return self.__class__.__qualname__ + f'(language={repr(self.language)}, isReliable={repr(self.isReliable)}, confidence={repr(self.confidence)})'


class TranslateResponse:
    """TranslateResponse"""

    def __init__(self, translatedText: str, detectedSourceLanguage: str = None, model: str = None):
        """

        :param translatedText: 翻译成目标语言的文本。
        :param model: 翻译模型。
        """
        if isinstance(translatedText, list):
            self.translatedText = translatedText[0]
            if len(translatedText) > 1:
                self.detectedSourceLanguage = translatedText[1]
            else:
                self.detectedSourceLanguage = None
        else:
            self.translatedText = translatedText
            self.detectedSourceLanguage = detectedSourceLanguage

        self.model = model

    def __repr__(self):
        return self.__class__.__qualname__ + f'(translatedText={repr(self.translatedText)}, detectedSourceLanguage={repr(self.detectedSourceLanguage)}, model={repr(self.model)})'


class Translator:
    """
    :param target: str: (可选) 目标语言, 默认: ``zh-CN``, :doc:`查看完整列表 <target>`
    :param source: str: (可选) 源语言, 默认: ``auto`` (自动检测), :doc:`查看完整列表 <source>`
    :param fmt: str: (可选) 文本格式, ``text`` | ``html``, 默认: ``html``
    :param user_agent: str: (可选) 用户代理, 这个参数很重要, 不设置或错误设置非常容易触发 **429 Too Many Requests** 错误,
        默认: ``GoogleTranslate/6.18.0.06.376053713 (Linux; U; Android 11; GM1900)``.
    :param domain: str: (可选) 域名 ``google.com`` 及其可用平行域名 (如: ``google.cn``), 默认: ``google.com``
    :param proxies: (可选) eg: proxies = {'http': 'http://localhost:7890', 'https': 'http://localhost:7890'}
    """

    def __init__(
            self,
            target: str = 'zh-CN',
            source: str = 'auto',
            fmt='html',
            user_agent: str = None,
            domain: str = 'com',
            proxies: Dict = None,
            timeout: int = None
    ):
        self.target = target
        self.source = source
        self.fmt = fmt
        self.timeout = timeout

        if user_agent is None:
            user_agent = (
                f'GoogleTranslate/6.{random.randint(10, 100)}.0.06.{random.randint(111111111, 999999999)}'
                ' (Linux; U; Android {random.randint(5, 11)}; {base64.b64encode(str(random.random())['
                '2:].encode()).decode()}) '
            )

        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': user_agent
        }
        self.BASE_URL: str = 'https://translate.google.' + domain
        self.LANGUAGE_URL: str = f'{self.BASE_URL}/translate_a/l'
        self.DETECT_URL: str = f'{self.BASE_URL}/translate_a/single'
        self.TRANSLATE_URL: str = f'{self.BASE_URL}/translate_a/t'
        self.TTS_URL: str = f'{self.BASE_URL}/translate_tts'

        if proxies is not None:
            self.session.trust_env = False
            self.session.proxies = proxies

    def detect(self, q: str, timeout=...) -> Union[DetectResponse, Null]:
        """语言检测

        :param q: 需要检测的内容.
        :param timeout: 超时时间， int | None
        :return: 成功则返回 :class:`DetectResponse` 对象,
            失败则返回 :class:`Null` 对象
        """
        if timeout is ...:
            timeout = self.timeout
        for i in range(1, 4):
            response = self.session.post(
                self.DETECT_URL,
                params={'dj': 1, 'sl': 'auto', 'ie': 'UTF-8', 'oe': 'UTF-8', 'client': 'at'},
                data={'q': q}, timeout=timeout
            )
            if response.status_code == 429:
                time.sleep(5 * i)
                continue
            break
        # noinspection PyUnboundLocalVariable
        if response.status_code != 200:
            return Null(response)
        rt = response.json()
        return DetectResponse(language=rt['src'], confidence=rt['confidence'])

    @overload
    def translate(self, q: str, target: str = None, source: str = None, fmt: str = None,
                  timeout=...) -> TranslateResponse:
        """..."""

    @overload
    def translate(
            self, q: List[str], target: str = None, source: str = None, fmt: str = None, timeout=...
    ) -> List[TranslateResponse]:
        """..."""

    def translate(
            self, q: Union[str, List[str]], target: str = None, source: str = None, fmt: str = None, timeout=...
    ) -> Union[TranslateResponse, List[TranslateResponse], Null]:
        """翻译文本, 支持批量, 支持 html

        :param q: str: 字符串或字符串列表
        :param target: str: (可选)  目标语言, 默认: ``self.target``
        :param source: str: (可选)  源语言, 默认: ``self.source``
        :param fmt: str: (可选) 文本格式, ``text`` | ``html``, 默认: ``self.format``
        :param timeout: 超时时间， int | None
        :return: 成功则返回: :class:`TranslateResponse` 对象,
            或 :class:`TranslateResponse` 对象列表, 这取决于 `参数: q` 是字符串还是字符串列表.
            失败则返回 :class:`Null` 对象
        """

        if not q:
            return []

        timeout = self.timeout if timeout is ... else timeout

        if isinstance(q, str) and q == '':
            return TranslateResponse('')

        for i in range(1, 4):
            response = self.__translate(q=q, target=target, source=source, fmt=fmt, v='1.0', timeout=timeout)
            if response.status_code == 429:
                time.sleep(5 * i)
                continue
            break

        if response.status_code == 200:
            ll = [TranslateResponse(translatedText=i) for i in response.json()]
            if isinstance(q, str):
                return ll[0]
            return ll

        return Null(response)

    def __translate(
            self, q: Union[str, List[str]], target: str = None, source: str = None, fmt: str = None, v: str = None,
            timeout=...
    ):
        if target is None:
            target = self.target
        if source is None:
            source = self.source
        if fmt is None:
            fmt = self.fmt
        if timeout is ...:
            timeout = self.timeout
        for i in range(1, 4):
            response = self.session.post(
                self.TRANSLATE_URL,
                params={'tl': target, 'sl': source, 'ie': 'UTF-8', 'oe': 'UTF-8', 'client': 'at', 'dj': '1',
                        'format': fmt, 'v': v},
                data={'q': q}, timeout=timeout
            )
            if response.status_code == 429:
                time.sleep(5 * i)
                continue
            break
        return response

    def tts(self, q: str, target: str = None, timeout=...) -> Union[bytes, Null]:
        """语音

        :param q: 只支持短语字符串
        :param target: 目标语言
        :param timeout: 超时时间， int | None
        :return: 返回二进制数据, 需要自行写入文件, MP3
        """
        if target is None:
            target = self.target

        if timeout is ...:
            timeout = self.timeout

        for i in range(1, 4):
            response = self.session.get(
                self.TTS_URL,
                params={
                    'ie': 'UTF-8',
                    'client': 'at',
                    'tl': target,
                    'q': q
                }, timeout=timeout)
            if response.status_code == 429:
                time.sleep(5 * i)
                continue
            break
        # noinspection PyUnboundLocalVariable
        if response.status_code == 200:
            return response.content
        return Null(response)
