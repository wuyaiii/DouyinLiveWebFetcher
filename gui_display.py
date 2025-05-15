from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                            QWidget, QTabWidget, QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QObject

class DouyinLiveGUI(QMainWindow):
    def __init__(self, live_fetcher):
        super().__init__()
        self.live_fetcher = live_fetcher
        self.setWindowTitle("抖音直播")
        self.resize(400, 300)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # 创建主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # 添加置顶按钮到窗口右上角
        self.topmost_btn = QPushButton("取消置顶")
        self.topmost_btn.setCheckable(True)
        self.topmost_btn.setChecked(True)
        self.topmost_btn.clicked.connect(self.toggle_topmost)
        
        # 创建一个工具栏来放置置顶按钮
        toolbar = self.addToolBar('Topmost')
        toolbar.addWidget(self.topmost_btn)
        
        # 创建选项卡
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # 创建不同消息类型的显示区域
        self.create_chat_tab()
        self.create_gift_tab()
        self.create_like_tab()
        self.create_member_tab()
        self.create_stats_tab()
        
        # 连接信号
        self.connect_signals()
    
    def create_chat_tab(self):
        """创建聊天消息标签页"""
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.tabs.addTab(self.chat_area, "聊天")
    
    def create_gift_tab(self):
        """创建礼物消息标签页"""
        self.gift_area = QTextEdit()
        self.gift_area.setReadOnly(True)
        self.tabs.addTab(self.gift_area, "礼物")
    
    def create_like_tab(self):
        """创建点赞消息标签页"""
        self.like_area = QTextEdit()
        self.like_area.setReadOnly(True)
        self.tabs.addTab(self.like_area, "点赞")
    
    def create_member_tab(self):
        """创建进场消息标签页"""
        self.member_area = QTextEdit()
        self.member_area.setReadOnly(True)
        self.tabs.addTab(self.member_area, "进场")
    
    def create_stats_tab(self):
        """创建统计信息标签页"""
        self.stats_area = QTextEdit()
        self.stats_area.setReadOnly(True)
        self.tabs.addTab(self.stats_area, "统计")
    
    def connect_signals(self):
        """连接所有信号"""
        try:
            self.live_fetcher.signals.chat_msg.connect(
                self.display_chat_message, Qt.QueuedConnection)
            self.live_fetcher.signals.gift_msg.connect(
                self.display_gift_message, Qt.QueuedConnection)
            self.live_fetcher.signals.like_msg.connect(
                self.display_like_message, Qt.QueuedConnection)
            self.live_fetcher.signals.member_msg.connect(
                self.display_member_message, Qt.QueuedConnection)
            self.live_fetcher.signals.social_msg.connect(
                self.display_social_message, Qt.QueuedConnection)
            self.live_fetcher.signals.stats_msg.connect(
                self.display_stats_message, Qt.QueuedConnection)
            self.live_fetcher.signals.control_msg.connect(
                self.display_control_message, Qt.QueuedConnection)
            self.live_fetcher.signals.room_status_msg.connect(
                self.display_room_status, Qt.QueuedConnection)
        except Exception as e:
            print(f"信号连接错误: {e}")
            
    def display_chat_message(self, user_id, user_name, content):
        self.chat_area.append(f"[{user_id}]{user_name}: {content}")
    
    def display_gift_message(self, user_name, gift_name, count):
        self.gift_area.append(f"{user_name} 送出了 {gift_name}x{count}")
    
    def display_like_message(self, user_name, count):
        self.like_area.append(f"{user_name} 点了{count}个赞")
    
    def display_member_message(self, user_id, gender, user_name):
        self.member_area.append(f"[{user_id}][{gender}]{user_name} 进入了直播间")
    
    def display_social_message(self, user_id, user_name):
        self.member_area.append(f"[{user_id}]{user_name} 关注了主播")
    
    def display_stats_message(self, current, total):
        self.stats_area.append(f"当前观看人数: {current}, 累计观看人数: {total}")
    
    def display_control_message(self, status):
        if status == 3:
            self.stats_area.append("直播间已结束")
    
    def display_room_status(self, nickname, user_id, status):
        self.stats_area.append(f"【{nickname}】[{user_id}]直播间：{status}")
    
    def toggle_topmost(self, checked):
        """切换窗口置顶状态"""
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.topmost_btn.setText("取消置顶")
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.topmost_btn.setText("置顶")
        self.show()
    
    def close_app(self):
        """关闭应用"""
        self.live_fetcher.stop()
        QApplication.quit()