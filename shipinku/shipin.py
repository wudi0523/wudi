import os
import sys
import sqlite3
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import wx
import wx.html2
import threading

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# --- 资源路径处理函数 ---
def resource_path(relative_path):
    """获取打包后的正确资源路径"""
    if getattr(sys, 'frozen', False):  # 判断是否打包
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 数据库路径
DB_PATH = resource_path(os.path.join("WuDiSocialData", "tool", "videos.db"))

# --- 初始化数据库 ---
def init_db():
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)  # 递归创建目录
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        thumbnail_url TEXT
    )
    ''')
    conn.commit()
    conn.close()

# --- Flask API路由 ---
@app.route('/api/videos', methods=['GET'])
def get_videos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, url, thumbnail_url FROM videos')
    videos = cursor.fetchall()
    conn.close()
    
    result = []
    for video in videos:
        result.append({
            'id': video[0],
            'title': video[1],
            'url': video[2],
            'thumbnail_url': video[3]
        })
    return jsonify(result)

@app.route('/api/videos', methods=['POST'])
def add_video():
    data = request.get_json()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO videos (title, url, thumbnail_url) VALUES (?, ?, ?)',
        (data['title'], data['url'], data.get('thumbnail_url', ''))
    )  # 修复括号闭合问题
    conn.commit()
    conn.close()
    return jsonify({'message': 'Video added successfully'}), 201

@app.route('/api/videos/<int:id>', methods=['DELETE'])
def delete_video(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM videos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Video deleted successfully'}), 200

@app.route('/')
def index():
    return send_file(resource_path('index.html'))

# --- wxPython窗口类 ---
class BrowserFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(BrowserFrame, self).__init__(*args, **kwargs)
        
        self.webview = wx.html2.WebView.New(self)
        self.webview.Bind(wx.html2.EVT_WEBVIEW_LOADED, self.on_page_loaded)
        self.webview.LoadURL("http://127.0.0.1:5002")
        self.webview.SetBackgroundColour(wx.TransparentColour)
        
        # 设置窗口属性
        self.SetSize((1200, 680))
        self.SetTitle("吴迪视频库")
        icon_path = resource_path(os.path.join("WuDiSocialData", "app_icon.ico"))
        icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.Centre()
        self.Show()
    
    def on_page_loaded(self, event):
        """页面加载完成后延迟执行缩放"""
        self.webview.RunScript("setTimeout(() => { document.body.style.zoom = '100%'; }, 300);")

# --- 主程序入口 ---
if __name__ == '__main__':
    init_db()
    
    # 启动Flask线程（关闭调试模式）
    flask_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=5002, debug=False, use_reloader=False)
    )
    flask_thread.daemon = True
    flask_thread.start()
    
    # 启动wxPython应用
    app_wx = wx.App()
    frame = BrowserFrame(None)
    app_wx.MainLoop()