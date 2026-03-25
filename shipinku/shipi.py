import os
import sqlite3
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import webview

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

if __name__ == '__main__':
    init_db()
    
    # 启动 Flask 应用
    import threading
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=False))
    flask_thread.daemon = True  # 设置为守护线程，这样主程序退出时Flask也会退出
    flask_thread.start()
    
    # 创建webview窗口
    webview.create_window('My Application', 'http://127.0.0.1:5002', width=1200, height=680)
    webview.start()