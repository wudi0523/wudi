import os
import sys
import time
import sqlite3
import webbrowser
import signal
from threading import Timer, Thread
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import tkinter as tk
from tkinter import messagebox

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# 数据库路径
DB_PATH = os.path.join(os.getcwd(), "WuDiSocialData", "tool", "videos.db")

def init_db():
    # 确保目录存在
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
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

# 获取所有视频
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

# 添加新视频
@app.route('/api/videos', methods=['POST'])
def add_video():
    data = request.get_json()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO videos (title, url, thumbnail_url) VALUES (?, ?, ?)',
        (data['title'], data['url'], data.get('thumbnail_url', ''))
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Video added successfully'}), 201

# 删除视频
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
    return send_file('index.html')

def run_server():
    app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=False)

def create_close_window():
    # 创建主窗口
    window = tk.Tk()
    window.title("服务器控制")
    window.geometry("200x100")  # 窗口大小
    
    # 关闭服务器的函数
    def close_server():
        if messagebox.askyesno("确认", "确定要关闭服务器吗？"):
            # 发送终止信号
            os.kill(os.getpid(), signal.SIGINT)
            window.destroy()
    
    # 创建关闭按钮
    close_btn = tk.Button(window, text="关闭服务器", command=close_server, width=15, height=2)
    close_btn.pack(pady=30)  # 放置按钮并设置边距
    
    # 运行窗口主循环
    window.mainloop()

if __name__ == '__main__':
    init_db()
    
    # 启动Flask服务器在新线程
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # 打开浏览器
    Timer(0.5, lambda: webbrowser.open('http://127.0.0.1:5002')).start()
    
    # 创建并显示关闭窗口
    create_close_window()
    
    # 等待服务器线程结束
    server_thread.join()
    sys.exit(0)