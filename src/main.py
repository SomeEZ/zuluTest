import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                            QHBoxLayout, QLabel, QPushButton, QComboBox, QFrame,
                            QLineEdit, QCheckBox, QStackedWidget, QListWidget)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation


class LoginWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        # 优化边距自适应逻辑
        base_margin = max(15, min(50, int(self.width() * 0.04)))  # 限制在15-50px之间
        v_margin = int(base_margin * 0.8)  # 垂直边距稍小
        layout.setContentsMargins(base_margin, v_margin, base_margin, v_margin)
        layout.setSpacing(max(10, int(base_margin * 0.6)))  # 间距最小值10px

        # 标题
        title = QLabel("EZMC启动器")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # 登录方式选择
        self.login_method = QComboBox()
        self.login_method.addItems(["正版登录", "离线版", "第三方登录"])
        self.login_method.currentTextChanged.connect(self.update_login_fields)
        layout.addWidget(self.login_method)

        # 用户名/游戏ID输入
        self.username = QLineEdit()
        self.username.setPlaceholderText("用户名/邮箱")
        layout.addWidget(self.username)

        # 密码输入
        self.password = QLineEdit()
        self.password.setPlaceholderText("密码")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        # 记住密码选项
        self.remember = QCheckBox("记住密码")
        layout.addWidget(self.remember)

        # 登录按钮
        self.login_btn = QPushButton("登录")
        self.login_btn.setStyleSheet("padding: 10px;")
        layout.addWidget(self.login_btn)

        # 版本信息
        version = QLabel("版本 1.0.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color: gray;")
        layout.addWidget(version)

        self.setLayout(layout)
        self.update_login_fields()

    def update_login_fields(self):
        """根据登录方式更新输入字段"""
        method = self.login_method.currentText()
        if method == "离线版":
            self.username.setPlaceholderText("游戏ID")
            self.password.hide()
            self.remember.hide()
        else:
            self.username.setPlaceholderText("用户名/邮箱")
            self.password.show()
            self.remember.show()

class VersionSelectPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # 版本选择标题
        title = QLabel("选择游戏版本")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 版本列表
        self.version_list = QListWidget()
        self.version_list.addItems(["1.20.4", "1.19.2", "1.18.1", "1.17.1"])
        self.version_list.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.version_list, stretch=1)

        # 确认按钮
        btn_layout = QHBoxLayout()
        self.confirm_btn = QPushButton("确认")
        self.confirm_btn.setStyleSheet("font-size: 16px; padding: 8px;")
        btn_layout.addWidget(self.confirm_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

class MinecraftLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EZMC启动器")

        # 优化窗口大小以更好显示头像
        screen = QApplication.primaryScreen().availableGeometry()
        base_width = min(900, int(screen.width() * 0.7))  # 增大到40%屏幕宽度
        width = max(700, base_width)  # 最小700px
        height = int(width * 0.6)  # 调整为90%高度比例，增加窗口长度
        self.setFixedSize(width, height)  # 固定窗口大小

        # 同步调整头像大小限制
        self.avatar_max_size = int(width * 0.18)  # 增大头像最大尺寸
        self.avatar_min_size = 80  # 添加最小头像尺寸
        self.avatar_container = None  # 初始化头像容器
        self.login_info = None  # 初始化登录信息

        # 更精细的字体自适应
        font = self.font()
        base_size = max(10, int(width * 0.012))  # 更平滑的字体缩放
        font.setPixelSize(base_size)
        self.setFont(font)

        # 使用堆叠窗口管理登录/主界面
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 登录界面
        self.login_window = LoginWindow()
        self.login_window.login_btn.clicked.connect(self.handle_login)
        self.stacked_widget.addWidget(self.login_window)

        # 主界面容器
        self.main_container = None

        # 设置蓝白灰主题样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 10px;
            }
            QWidget {
                background-color: white;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QComboBox, QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #dddddd;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            /* 左侧栏样式 */
            QFrame#left_panel {
                background-color: #f5f5f5;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            /* 右侧栏样式 */
            QFrame#right_panel {
                background-color: #f5f5f5;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            /* 启动按钮特殊样式 */
            QPushButton#launch_btn {
                font-size: 16px;
                padding: 10px;
            }
        """)

    def init_ui(self):
        """初始化主界面"""
        # 确保main_container只创建一次
        if self.main_container is None:
            self.main_container = QWidget()
            self.stacked_widget.addWidget(self.main_container)

        # 初始化版本选择面板
        self.version_select_panel = VersionSelectPanel()
        self.version_select_panel.confirm_btn.clicked.connect(self.on_version_selected)

        # 确保版本选择按钮存在并连接信号
        if hasattr(self, 'version_select_btn'):
            try:
                self.version_select_btn.clicked.disconnect()
            except:
                pass
            self.version_select_btn.clicked.connect(self.show_version_select)

        # 清除现有布局
        if hasattr(self, 'main_layout') and self.main_layout is not None:
            QWidget().setLayout(self.main_layout)

        # 创建新的主布局
        self.main_layout = QVBoxLayout(self.main_container)

        # 创建主水平布局(左右分栏)
        self.horizontal_layout = QHBoxLayout()
        self.main_layout.addLayout(self.horizontal_layout)

        # 左侧区域 (账号和版本管理)
        self.left_panel = QFrame()
        self.left_panel.setObjectName("left_panel")  # 设置对象名用于样式表
        self.left_panel.setFrameShape(QFrame.Shape.StyledPanel)
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(10, 10, 10, 10)

        # 初始化头像区域
        self._setup_avatar_section()

        # 头像容器置顶
        self.left_layout.addWidget(self.avatar_container)

    def show_default_avatar(self):
        """显示默认头像"""
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.green)
        self.avatar_label.setPixmap(pixmap)

        # 切换账号按钮
        self.switch_account_btn = QPushButton("切换账号")
        self.switch_account_btn.setStyleSheet("text-align: center;")
        self.switch_account_btn.clicked.connect(self.show_login)
        self.left_layout.addWidget(self.switch_account_btn)

        # 移除登录方式选择
        self.left_layout.setSpacing(15)

        # 版本显示(只读文本框)
        if not hasattr(self, 'version_display'):
            self.version_display = QLineEdit("1.20.4")
            self.version_display.setReadOnly(True)
            self.version_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.left_layout.addWidget(self.version_display)

        # 版本操作按钮
        if not hasattr(self, 'version_select_btn'):
            version_btn_layout = QHBoxLayout()
            self.version_select_btn = QPushButton("版本选择")
            self.version_config_btn = QPushButton("版本设置")
            version_btn_layout.addWidget(self.version_select_btn)
            version_btn_layout.addWidget(self.version_config_btn)
            self.left_layout.addLayout(version_btn_layout)
            self.version_select_btn.clicked.connect(self.show_version_select)

        # 右侧区域 (游戏信息显示)
        self.right_panel = QFrame()
        self.right_panel.setObjectName("right_panel")  # 设置对象名用于样式表
        self.right_panel.setFrameShape(QFrame.Shape.StyledPanel)
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(15, 15, 15, 15)
        self.right_layout.setSpacing(10)

        # 游戏新闻标题 - 固定在左上角
        news_title = QLabel("游戏新闻")
        news_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        news_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.right_layout.addWidget(news_title)

        # 游戏新闻内容 - 占据剩余空间
        news_content = QLabel("最新版本1.20.4已发布！\n\n新增内容：\n- 新生物骆驼\n- 竹木系列方块\n- 悬挂式告示牌")
        news_content.setStyleSheet("font-size: 14px;")
        news_content.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        news_content.setWordWrap(True)
        self.right_layout.addWidget(news_content, stretch=1)  # 使用stretch使内容区域可扩展

        # 启动按钮容器
        self.btn_container = QWidget()
        self.btn_layout = QVBoxLayout(self.btn_container)
        self.btn_layout.setContentsMargins(0, 20, 0, 0)

        # 启动按钮
        self.launch_btn = QPushButton("启动游戏")
        self.launch_btn.setObjectName("launch_btn")  # 设置对象名用于样式表
        self.launch_btn.setFixedHeight(50)
        self.launch_btn.clicked.connect(self.launch_game)
        self.btn_layout.addWidget(self.launch_btn)

        # 添加左右面板到主布局
        self.horizontal_layout.addWidget(self.left_panel, stretch=3)  # 账号管理区域宽度占比1/3
        self.horizontal_layout.addWidget(self.right_panel, stretch=12)  # 新闻区域宽度占比2/3
        self.main_layout.addWidget(self.btn_container)

        # 增加内容区域高度
        self.left_layout.setSpacing(10)  # 增加组件间距
        self.right_layout.setSpacing(10)  # 增加组件间距

        # 调整左右面板的内边距
        self.left_layout.setContentsMargins(10, 10, 10, 10)  # 增加内边距
        self.right_layout.setContentsMargins(30, 30, 30, 30)  # 增加内边距

        # 强制更新布局
        self.main_container.updateGeometry()
        self.update()

    def launch_game(self):
        """启动游戏按钮点击事件"""
        selected_version = self.version_combo.currentText()
        self.statusBar().showMessage(f"正在启动Minecraft {selected_version}...")
        # TODO: 实现实际启动逻辑

    def handle_login(self):
        """处理登录逻辑"""
        method = self.login_window.login_method.currentText()
        username = self.login_window.username.text()

        if method == "离线版":
            if not username:
                self.statusBar().showMessage("请输入游戏ID")
                return
            self.statusBar().showMessage("正在登录...")
            QTimer.singleShot(1500, self.login_success)
        else:
            password = self.login_window.password.text()
            if not username or not password:
                self.statusBar().showMessage("请输入用户名和密码")
                return
            self.statusBar().showMessage("正在登录...")
            QTimer.singleShot(1500, self.login_success)

    def _setup_avatar_section(self):
        """设置头像区域"""
        # 先创建头像容器（严格居中）
        self.avatar_container = QWidget()
        self.avatar_layout = QVBoxLayout(self.avatar_container)
        self.avatar_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.avatar_layout.setContentsMargins(0, 10, 0, 10)
        self.avatar_layout.setSpacing(10)

        # 创建头像标签
        self.avatar_label = QLabel()
        # 优化头像自适应显示
        self.avatar_label.setMinimumSize(self.avatar_min_size, self.avatar_min_size)
        self.avatar_label.setScaledContents(True)  # 确保图片缩放适应标签
        self.avatar_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                padding: 2px;
            }
            QLabel:hover {
                background-color: rgba(76, 175, 80, 0.1);
            }
        """)

        # 添加水平居中容器
        self.avatar_hbox = QHBoxLayout()
        self.avatar_hbox.addStretch(1)
        self.avatar_hbox.addWidget(self.avatar_label)
        self.avatar_hbox.addStretch(1)
        self.avatar_layout.addLayout(self.avatar_hbox)

        # 添加登录信息（保持居中）
        self.login_info = QLabel("登录方式：正版登录\n游戏ID: SomeEZ")
        self.login_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_info.setStyleSheet("font-size: 15px;")
        self.avatar_layout.addWidget(self.login_info)

        # 加载头像
        self._load_avatar()

    def _load_avatar(self):
        """异步加载用户头像"""
        def load_avatar_async():
            try:
                # 获取当前文件绝对路径
                current_dir = os.path.dirname(os.path.abspath(__file__))
                avatar_path = os.path.join(current_dir, "resources", "default_avatar.png")

                # 检查文件是否存在
                if not os.path.exists(avatar_path):
                    self.show_default_avatar()
                    return

                # 异步加载图片
                pixmap = QPixmap()
                if pixmap.load(avatar_path):
                    # 在主线程更新UI
                    def update_avatar():
                        self.avatar_label.setPixmap(pixmap.scaled(
                            100, 100,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        ))
                    QTimer.singleShot(0, update_avatar)
                else:
                    self.show_default_avatar()
            except Exception as e:
                print(f"加载头像失败: {e}")
                self.show_default_avatar()

        # 启动异步加载
        QTimer.singleShot(0, load_avatar_async)

    def login_success(self):
        """登录成功处理"""
        try:
            # 确保主界面已初始化
            if self.main_container is None:
                self.main_container = QWidget()
                self.stacked_widget.addWidget(self.main_container)
                # 完整初始化主界面
                self.init_ui()
                # 初始化默认UI状态
                self.show_default_avatar()
                self._load_avatar()

            # 更新登录信息
            method = self.login_window.login_method.currentText()
            username = self.login_window.username.text()
            self.login_info.setText(f"登录方式：{method}\n游戏ID: {username}")

            # 刷新主界面布局
            self.main_container.layout().update()
            self.main_container.updateGeometry()

            # 切换到主界面
            self.stacked_widget.setCurrentIndex(1)
            self.statusBar().showMessage("登录成功", 3000)

            # 强制完整重绘
            self.main_container.show()
            self.repaint()
            QApplication.processEvents()

            # 延迟额外刷新确保界面稳定
            QTimer.singleShot(100, lambda: [
                self.main_container.update(),
                self.repaint(),
                QApplication.processEvents()
            ])
        except Exception as e:
            print(f"初始化主界面时出错: {e}")
            self.statusBar().showMessage(f"登录失败: {str(e)}", 5000)

    def show_version_select(self):
        """显示版本选择面板"""
        # 保存当前右侧面板内容
        self.saved_right_panel = self.right_panel

        # 替换为版本选择面板
        self.horizontal_layout.replaceWidget(self.right_panel, self.version_select_panel)
        self.right_panel = self.version_select_panel
        self.right_panel.show()

        # 添加淡入动画
        self.fade_in(self.version_select_panel)

    def on_version_selected(self):
        """版本选择确认处理"""
        selected = self.version_select_panel.version_list.currentItem()
        if selected:
            self.version_display.setText(selected.text())

        # 恢复原始右侧面板
        self.horizontal_layout.replaceWidget(self.version_select_panel, self.saved_right_panel)
        self.right_panel = self.saved_right_panel
        self.right_panel.show()

        # 添加淡出动画
        self.fade_out(self.version_select_panel)

    def fade_in(self, widget):
        """淡入动画效果"""
        if widget is None or not widget.isWidgetType():
            return

        try:
            self._current_animation = QPropertyAnimation(widget, b"windowOpacity")
            self._current_animation.setDuration(300)
            self._current_animation.setStartValue(0)
            self._current_animation.setEndValue(1)
            self._current_animation.finished.connect(lambda: self._cleanup_animation())
            self._current_animation.start()
        except Exception as e:
            print(f"淡入动画错误: {e}")

    def fade_out(self, widget):
        """淡出动画效果"""
        if widget is None or not widget.isWidgetType():
            return

        try:
            self._current_animation = QPropertyAnimation(widget, b"windowOpacity")
            self._current_animation.setDuration(300)
            self._current_animation.setStartValue(1)
            self._current_animation.setEndValue(0)
            self._current_animation.finished.connect(lambda: self._cleanup_animation())
            self._current_animation.start()
        except Exception as e:
            print(f"淡出动画错误: {e}")

    def _cleanup_animation(self):
        """清理动画资源"""
        if hasattr(self, '_current_animation'):
            try:
                self._current_animation.stop()
                self._current_animation.deleteLater()
            except:
                pass
            finally:
                del self._current_animation

    def show_login(self):
        """显示登录界面"""
        self.stacked_widget.setCurrentIndex(0)
        self.login_window.username.clear()
        self.login_window.password.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = MinecraftLauncher()
    launcher.show()
    sys.exit(app.exec())
