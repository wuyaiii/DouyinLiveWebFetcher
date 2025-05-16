#!/usr/bin/python
# coding:utf-8

# @FileName:    main.py
# @Time:        2024/1/2 22:27
# @Author:      bubu
# @Project:     douyinLiveWebFetcher
import sys

from PyQt5.QtWidgets import QApplication
from liveMan import DouyinLiveWebFetcher
from gui_display import DouyinLiveGUI

if __name__ == '__main__':
    fetcher = DouyinLiveWebFetcher("")
    
    app = QApplication(sys.argv)
    
    # 创建GUI窗口
    gui = DouyinLiveGUI(fetcher)
    gui.show()
    
    sys.exit(app.exec_())