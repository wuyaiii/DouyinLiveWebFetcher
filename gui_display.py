import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                            QWidget, QTabWidget, QPushButton, QHBoxLayout, QLineEdit,
                            QComboBox, QMenu, QAction)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from liveMan import FavoritesManager
import time

class DouyinLiveGUI(QMainWindow):
    def __init__(self, live_fetcher):
        super().__init__()
        self.live_fetcher = live_fetcher
        self.favorites_manager = FavoritesManager()
        self.setWindowTitle("抖音直播")
        self.resize(400, 350)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # 创建主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # 添加房间号输入框和连接按钮
        input_layout = QHBoxLayout()
        self.room_id_input = QLineEdit()
        self.room_id_input.setPlaceholderText("请输入房间号")
        self.connect_btn = QPushButton("连接房间")
        self.connect_btn.clicked.connect(self.connect_room)
        input_layout.addWidget(self.room_id_input)
        input_layout.addWidget(self.connect_btn)
        main_layout.addLayout(input_layout)
        
        # 添加收藏功能
        self._setup_favorites(main_layout)
        
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
        
        # 初始化收藏列表
        self._update_favorites_list()
        # 确保收藏下拉框初始时处于未选择状态
        self.favorites_combo.setCurrentIndex(-1)
        
    def _setup_favorites(self, layout):
        """设置收藏区域"""
        # 添加收藏下拉框
        favorites_layout = QHBoxLayout()
        
        # 收藏下拉框
        self.favorites_combo = QComboBox()
        self.favorites_combo.setFixedWidth(200)
        
        # 连接当前选择变化信号
        self.favorites_combo.currentIndexChanged.connect(self._on_favorite_selected)
        
        
        # 添加收藏按钮
        self.add_favorite_btn = QPushButton("添加收藏")
        self.add_favorite_btn.clicked.connect(self._add_favorite)
        
        
        # 删除收藏按钮
        self.remove_favorite_btn = QPushButton("删除收藏")
        self.remove_favorite_btn.clicked.connect(self._remove_favorite)
        
        # 将收藏下拉框和按钮添加到布局
        favorites_layout.addWidget(self.favorites_combo)
        favorites_layout.addWidget(self.add_favorite_btn)
        favorites_layout.addWidget(self.remove_favorite_btn)
        
        # 添加到主布局
        layout.addLayout(favorites_layout)
        
    
    def _update_favorites_list(self):
        """更新收藏列表"""
        self.favorites_combo.clear()
        self.favorites_combo.addItem("- 请选择直播间 -", "")  # 添加空选项
        favorites = self.favorites_manager.get_favorites()
        for room_id, info in favorites.items():
            nickname = info.get('nickname', '')
            self.favorites_combo.addItem(f"{room_id} - {nickname}", room_id)

    def _add_favorite(self):
        """添加收藏"""
        room_id = self.room_id_input.text().strip()
        if not room_id:
            self.chat_area.append("请输入房间号!")
            return
            
        try:
            # 更新直播抓取器的房间号
            self.live_fetcher.set_room_id(room_id)
            # 获取房间状态信息
            room_info = self.live_fetcher.get_room_status()
            if not room_info:
                self.chat_area.append("无效的房间号或无法获取房间信息")
                return
                
            # 添加到收藏
            if self.favorites_manager.add_favorite(room_id, room_info.get('nickname', '')):
                self._update_favorites_list()
                self.chat_area.append(f"已添加收藏: {room_id}")
            else:
                self.chat_area.append(f"已存在收藏: {room_id}")
            # 清除收藏选择
            self.favorites_combo.setCurrentIndex(-1)
                
        except Exception as e:
            self.chat_area.append(f"添加收藏失败: {str(e)}")

    def _remove_favorite(self):
        """删除收藏"""
        current_index = self.favorites_combo.currentIndex()
        if current_index >= 0:
            room_id = self.favorites_combo.currentData()
            if self.favorites_manager.remove_favorite(room_id):
                self._update_favorites_list()
                self.chat_area.append(f"已删除收藏: {room_id}")
                
                
    def _on_favorite_selected(self, index):
        """收藏下拉框当前选择变化处理函数"""
        if index > 0:  # 只有选择了实际的直播间才更新输入框
            room_id = self.favorites_combo.currentData()
            self.room_id_input.setText(room_id)
        else:
            self.room_id_input.clear()  # 选择空选项时清空输入框
            
    def create_chat_tab(self):
        """创建聊天消息标签页"""
        from PyQt5.QtWidgets import QTextBrowser
        self.chat_area = QTextBrowser()
        self.chat_area.setOpenExternalLinks(True)  # 允许打开外部链接
        # 设置样式表，去除段落间距和行高
        self.chat_area.setStyleSheet("""
            QTextBrowser {
                font-size: 12px;
            }
            QTextBrowser p {
                margin: 0;
                padding: 0;
                line-height: 1;
            }
        """)
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
    
    def connect_room(self):
        """连接指定房间"""
            
        room_id = self.room_id_input.text().strip()
        if not room_id:
            self.chat_area.append("请输入房间号!")
            return
            
        try:
            # 如果正在连接其他房间，先停止
            if hasattr(self.live_fetcher, 'ws') and self.live_fetcher.ws:
                self.live_fetcher.stop()
                time.sleep(0.1)  # 短暂等待
                
            # 更新直播抓取器的房间号
            self.live_fetcher.set_room_id(room_id)
            
            # 获取房间状态信息
            room_info = self.live_fetcher.get_room_status()
            if not room_info:
                self.chat_area.append("无法获取房间信息")
                return
            nickname = room_info.get('nickname', '')
            
            room_status = room_info.get('status')
            if room_status == 2:
                self.chat_area.append(f"{room_id} - {nickname}直播已结束")
                return
            
            # 更新窗口标题为主播名称
            self.setWindowTitle(f"抖音直播 - {nickname}")
            
            # 在单独的线程中启动抓取器
            import threading
            fetch_thread = threading.Thread(target=self.live_fetcher.start)
            fetch_thread.daemon = True
            fetch_thread.start()
            self.chat_area.append(f"正在连接房间 {room_id} - {nickname}...")
            
            
            if room_status == 0:
                # 构建直播间的URL
                live_url = f"https://www.douyin.com/live/{room_id}"
                # 添加直播链接到消息中
                self.chat_area.append(f"{room_id} - {nickname}直播正在直播！")
                self.chat_area.append(f"<a href='{live_url}' style='color: blue;'>点击这里查看直播间</a>")
            elif room_status == 2:
                self.chat_area.append(f"{room_id} - {nickname}直播已结束")
                return
            
            # 清除收藏选择
            self.favorites_combo.setCurrentIndex(-1)
                
        except Exception as e:
            self.chat_area.append(f"连接失败: {str(e)}")
            # 如果连接失败，确保清理WebSocket连接
            if hasattr(self.live_fetcher, 'ws'):
                self.live_fetcher.ws = None
                    
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
            self.chat_area.append("直播已结束")
            self.stats_area.append("直播已结束")
    
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