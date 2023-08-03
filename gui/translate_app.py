import os
import csv
import sys
from pathlib import Path

import requests

sys.path.append("..")
sys.path.append(".")
from parser.csv import csv_loader

from PyQt6 import QtGui
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
    QComboBox,
    QLineEdit,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QApplication,
    QProgressDialog,
)

from translate.translator import Translator

BASEDIR = Path(__file__).parent.parent

target_languages = {
    "中文(简体)": "zh-CN",
    "英语": "en",
    "中文(繁体)": "zh-TW",
    "阿尔巴尼亚语": "sq",
    "阿拉伯语": "ar",
    "阿姆哈拉语": "am",
    "阿塞拜疆语": "az",
    "爱尔兰语": "ga",
    "爱沙尼亚语": "et",
    "奥利亚语": "or",
    "巴斯克语": "eu",
    "白俄罗斯语": "be",
    "保加利亚语": "bg",
    "冰岛语": "is",
    "波兰语": "pl",
    "波斯尼亚语": "bs",
    "波斯语": "fa",
    "布尔语(南非荷兰语)": "af",
    "鞑靼语": "tt",
    "丹麦语": "da",
    "德语": "de",
    "俄语": "ru",
    "法语": "fr",
    "菲律宾语": "tl",
    "芬兰语": "fi",
    "弗里西语": "fy",
    "高棉语": "km",
    "格鲁吉亚语": "ka",
    "古吉拉特语": "gu",
    "哈萨克语": "kk",
    "海地克里奥尔语": "ht",
    "韩语": "ko",
    "豪萨语": "ha",
    "荷兰语": "nl",
    "吉尔吉斯语": "ky",
    "加利西亚语": "gl",
    "加泰罗尼亚语": "ca",
    "捷克语": "cs",
    "卡纳达语": "kn",
    "科西嘉语": "co",
    "克罗地亚语": "hr",
    "库尔德语": "ku",
    "拉丁语": "la",
    "拉脱维亚语": "lv",
    "老挝语": "lo",
    "立陶宛语": "lt",
    "卢森堡语": "lb",
    "卢旺达语": "rw",
    "罗马尼亚语": "ro",
    "马尔加什语": "mg",
    "马耳他语": "mt",
    "马拉地语": "mr",
    "马拉雅拉姆语": "ml",
    "马来语": "ms",
    "马其顿语": "mk",
    "毛利语": "mi",
    "蒙古语": "mn",
    "孟加拉语": "bn",
    "缅甸语": "my",
    "苗语": "hmn",
    "南非科萨语": "xh",
    "南非祖鲁语": "zu",
    "尼泊尔语": "ne",
    "挪威语": "no",
    "旁遮普语": "pa",
    "葡萄牙语": "pt",
    "普什图语": "ps",
    "齐切瓦语": "ny",
    "日语": "ja",
    "瑞典语": "sv",
    "萨摩亚语": "sm",
    "塞尔维亚语": "sr",
    "塞索托语": "st",
    "僧伽罗语": "si",
    "世界语": "eo",
    "斯洛伐克语": "sk",
    "斯洛文尼亚语": "sl",
    "斯瓦希里语": "sw",
    "苏格兰盖尔语": "gd",
    "宿务语": "ceb",
    "索马里语": "so",
    "塔吉克语": "tg",
    "泰卢固语": "te",
    "泰米尔语": "ta",
    "泰语": "th",
    "土耳其语": "tr",
    "土库曼语": "tk",
    "威尔士语": "cy",
    "维吾尔语": "ug",
    "乌尔都语": "ur",
    "乌克兰语": "uk",
    "乌兹别克语": "uz",
    "西班牙语": "es",
    "希伯来语": "iw",
    "希腊语": "el",
    "夏威夷语": "haw",
    "信德语": "sd",
    "匈牙利语": "hu",
    "修纳语": "sn",
    "亚美尼亚语": "hy",
    "伊博语": "ig",
    "意大利语": "it",
    "意第绪语": "yi",
    "印地语": "hi",
    "印尼巽他语": "su",
    "印尼语": "id",
    "印尼爪哇语": "jw",
    "约鲁巴语": "yo",
    "越南语": "vi",
}


class TranslateThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str)

    def __init__(self, source_file, dest_file, target_language, proxy=None):
        super().__init__()
        self.source_file = source_file
        self.dest_file = dest_file
        self.target_language = target_language
        self.proxy = proxy
        self.is_running = True  # 添加标志来跟踪线程是否正在运行

    def run(self):
        assert Path(self.source_file).exists(), "源文件不存在"

        translate_client = Translator(
            target=self.target_language,
            # source="en",
            proxies=self.proxy,
            timeout=10,
        )

        values = csv_loader(self.source_file)

        headers = next(values)
        column_count = len(headers)

        writer = csv.writer(
            Path(self.dest_file).open(mode="w", encoding="utf-8-sig", newline="")
        )
        target_headers = []
        for h in headers:
            target_headers.extend([h, h])
        writer.writerows([target_headers])

        row_number = 0

        try:
            def translate_and_write(_rows):
                trans_responses = translate_client.translate(q=_rows)
                translated = [response.translatedText for response in trans_responses]
                nonlocal row_number
                for i in range(0, len(translated), column_count):
                    _origin_row = [rows[i + bias] for bias in range(column_count)]
                    _translated_row = [translated[i + bias] for bias in range(column_count)]
                    _temp = []
                    for _index, _r in enumerate(_origin_row):
                        _temp.extend([_r, _translated_row[_index]])
                    writer.writerow(_temp)
                    # writer.writerow([rows[i + bias] for bias in range(column_count)])
                    # writer.writerow([translated[i + bias] for bias in range(column_count)])

                    row_number += 1
                    # print([rows[i + bias] for bias in range(column_count)])
                    self.progress_signal.emit(row_number)

            rows = []
            for row in values:
                rows.extend(row)

                if len(rows) >= 5000:
                    translate_and_write(_rows=rows)
                    rows = []

                if self.isInterruptionRequested():
                    break

            if rows:
                translate_and_write(_rows=rows)
            self.finished_signal.emit("Success")
        except requests.exceptions.ConnectTimeout:
            self.finished_signal.emit("网络请求超时, 请检查代理配置!")
        except Exception as e:
            self.finished_signal.emit(f"发生错误: {e}")


    def stop(self):
        self.is_running = False  # 设置标志为False，以便线程结束


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CSV文件翻译")
        self.setGeometry(200, 200, 600, 300)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.com_box = QComboBox()
        self.com_box.addItems(target_languages.keys())
        self.com_box.setCurrentText("中文(简体)")
        self.com_box_label = QLabel("目标语种选择")
        self.layout.addWidget(self.com_box_label)
        self.layout.addWidget(self.com_box)
        self.setLayout(self.layout)
        self.com_box.currentIndexChanged.connect(self.target_language_selection_change)
        self.target_language_code = "zh-CN"

        self.proxy = None
        self.input_proxy = QLineEdit(self)
        self.input_proxy.setPlaceholderText("请设置代理(eg. http://loclhost:7890), 无需则置空")
        self.proxy_input_label = QLabel("配置代理地址")
        self.layout.addWidget(self.proxy_input_label)
        self.layout.addWidget(self.input_proxy)
        self.input_proxy.textChanged.connect(self.input_proxy_change)

        self.file_label = QLabel("未选择文件")
        self.layout.addWidget(self.file_label)
        self.upload_button = QPushButton("上传CSV文件")
        self.upload_button.clicked.connect(self.upload_csv)
        self.layout.addWidget(self.upload_button)

        self.save_button = QPushButton("保存解析结果到CSV")
        self.save_button.clicked.connect(self.save_data)
        self.layout.addWidget(self.save_button)
        self.source_file_path = None

    def target_language_selection_change(self, i):
        self.target_language_code = target_languages[self.com_box.currentText()]

    def input_proxy_change(self, text):
        if text:
            self.proxy = {"http": text}

    def upload_csv(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "选择CSV文件", "", "CSV Files (*.csv)"
        )
        if file_path:
            self.file_label.setText(file_path)
            self.source_file_path = file_path

    def save_data(self):
        if self.source_file_path is None:
            QMessageBox.warning(self, "警告", "请先上传CSV文件!")
            return
        if self.source_file_path is not None:
            file_dialog = QFileDialog()
            save_path, _ = file_dialog.getSaveFileName(
                self, "保存解析结果", "", "CSV Files (*.csv)"
            )

            if not save_path:
                QMessageBox.information(self, "提示", "未选择保存路径!")
                return

            total_row_count = sum(1 for _ in Path(self.source_file_path).open())
            self.progress_dialog = QProgressDialog(
                "处理中...", "取消", 0, total_row_count, self
            )
            self.progress_dialog.setWindowTitle("请稍候")
            self.progress_dialog.show()
            # self.translate(self.source_file_path, save_path, self.target_language_code)
            translate_thread = TranslateThread(
                self.source_file_path,
                save_path,
                self.target_language_code,
                self.proxy,
            )
            translate_thread.progress_signal.connect(self.progress_dialog.setValue)

            def finished_recever(result):
                if result == "Success":
                    QMessageBox.information(self, "成功", "解析结果已保存")
                    self.source_file_path = None
                    self.file_label.setText("解析结果已保存")
                else:
                    QMessageBox.information(self, "错误", result)
                self.progress_dialog.hide()
                translate_thread.stop()

            translate_thread.finished_signal.connect(finished_recever)
            translate_thread.start()

            while translate_thread.is_running:  # 等待翻译线程完成
                if self.progress_dialog.wasCanceled():  # 检查是否点击了取消按钮
                    translate_thread.terminate()
                    break
                QApplication.processEvents()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setWindowIcon(QtGui.QIcon(os.path.join(BASEDIR, "gui/window_icon.ico")))
    window = MainWindow()
    window.setWindowIcon(QtGui.QIcon(os.path.join(BASEDIR, "gui/window_icon.ico")))
    window.show()
    sys.exit(app.exec())
