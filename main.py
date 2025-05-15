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
    live_id = '970345816745'  # 替换为你想监控的直播间ID
    
    app = QApplication(sys.argv)
    
    # 创建直播抓取器
    fetcher = DouyinLiveWebFetcher(live_id)
    
    # 创建GUI窗口
    gui = DouyinLiveGUI(fetcher)
    gui.show()
    
    # 检查房间状态
    fetcher.get_room_status()
    
    # 在单独的线程中启动抓取器
    import threading
    fetch_thread = threading.Thread(target=fetcher.start)
    fetch_thread.daemon = True
    fetch_thread.start()
    
    
    sys.exit(app.exec_())
