import os
import pandas as pd
import io  # 【新】导入 io 库，用于内存操作
from flask import (
    Flask, render_template, request, redirect, url_for, 
    session, send_from_directory, flash, Response  # 【新】导入 Response
)
import random
from flask_session import Session

# --- Vercel 适配配置 ---
# 【重要】Vercel 唯一可写的目录是 /tmp
# 我们将所有临时文件都指向那里
TEMP_DIR = '/tmp'
SESSION_FILE_DIR = os.path.join(TEMP_DIR, 'flask_session')
UPLOAD_FOLDER = os.path.join(TEMP_DIR, 'uploads')
DOWNLOAD_FOLDER = os.path.join(TEMP_DIR, 'downloads') # 虽然不用了，但保持一致

SECRET_KEY = 'a_very_secret_key_for_session' 

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = SESSION_FILE_DIR
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = SECRET_KEY

Session(app)

# 确保 Vercel 上的 /tmp 目录存在
os.makedirs(SESSION_FILE_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- 核心功能：解析词汇表 ---
def load_words(filepath):
    """
    解析用户上传的特定格式的CSV/XLSX文件。
    返回一个字典，键为 "Word List XX"，值为单词字典列表。
    """
    try:
        df = pd.read_csv(filepath, header=None, keep_default_na=False)
    except Exception:
        try:
            df = pd.read_excel(filepath, header=None, keep_default_na=False)
        except Exception as e:
            flash(f"文件读取错误: {e}")
            return None

    word_lists = {}
    current_list_name = None
    
    for _, row in df.iterrows():
        if row.isnull().all() or all(cell == '' for cell in row):
            continue

        if str(row[0]).startswith("Word List"):
            current_list_name = str(row[0]).strip()
            word_lists[current_list_name] = []
        
        elif current_list_name and str(row[1]): 
            if not str(row[1]) and not str(row[3]):
                continue
                
            word_data = {
                'id': str(row[0]),
                'word': str(row[1]),
                'pos': str(row[2]), 
                'def': str(row[3]), 
                'syn': str(row[4]), 
                'original_row': list(row)
            }
            word_lists[current_list_name].append(word_data)
            
    return word_lists

# --- 路由：首页 (上传和选择模式) ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('没有文件部分')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('未选择文件')
            return redirect(request.url)
        
        if file:
            # 【重要】文件被保存在 /tmp/uploads/ 目录下
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            word_lists = load_words(filepath)
            if word_lists:
                session['word_lists'] = word_lists
                flash('词汇表上传成功！')
            else:
                flash('文件格式错误，无法解析')
            
            # 解析完成后，可以删除临时文件（可选）
            if os.path.exists(filepath):
                os.remove(filepath)

            return redirect(url_for('index'))

    list_names = session.get('word_lists', {}).keys()
    return render_template('index.html', list_names=list_names)

# --- 路由：开始复习 (准备数据) ---
@app.route('/start_review', methods=['POST'])
def start_review():
    word_lists = session.get('word_lists')
    if not word_lists:
        flash('请先上传词汇表')
        return redirect(url_for('index'))

    review_mode = request.form.get('review_mode')
    review_deck = []

    if review_mode == 'list':
        selected_list = request.form.get('selected_list', '').strip()
        review_deck = word_lists.get(selected_list, [])
    elif review_mode == 'random':
        for list_name in word_lists:
            review_deck.extend(word_lists[list_name])
    
    if not review_deck:
        flash('选择的列表为空或模式错误')
        return redirect(url_for('index'))

    random.shuffle(review_deck)
    
    session['review_deck'] = review_deck
    session['current_index'] = 0
    session['forgotten_deck'] = [] 
    session['forgotten_words_raw'] = []

    return redirect(url_for('review'))

# --- 路由：复习页面 (闪卡) ---
@app.route('/review')
def review():
    review_deck = session.get('review_deck')
    current_index = session.get('current_index', 0)

    if not review_deck or not isinstance(review_deck, list):
        flash('复习列表为空，请重新开始')
        return redirect(url_for('index'))
        
    if not isinstance(current_index, int) or current_index >= len(review_deck):
        return redirect(url_for('results'))

    word = review_deck[current_index]
    progress = {
        'current': current_index + 1,
        'total': len(review_deck)
    }
    
    return render_template('review.html', word=word, progress=progress)

# --- 路由：记录答案 (处理 "记住" / "没记住") ---
@app.route('/record_answer', methods=['POST'])
def record_answer():
    review_deck = session.get('review_deck', [])
    current_index = session.get('current_index', 0)

    if not review_deck or current_index >= len(review_deck):
        flash('复习进程丢失，请重新开始')
        return redirect(url_for('index'))

    answer = request.form.get('answer')

    if answer == 'forgot':
        word_data = review_deck[current_index]
        
        forgotten_list_deck = session.get('forgotten_deck', [])
        forgotten_list_deck.append(word_data)
        session['forgotten_deck'] = forgotten_list_deck
        
        forgotten_list_raw = session.get('forgotten_words_raw', [])
        forgotten_list_raw.append(word_data['original_row'])
        session['forgotten_words_raw'] = forgotten_list_raw

    session['current_index'] = current_index + 1
    return redirect(url_for('review'))

# --- 路由：结果页面 ---
@app.route('/results')
def results():
    total_reviewed = len(session.get('review_deck', []))
    total_forgotten = len(session.get('forgotten_deck', []))
    
    session.pop('review_deck', None)
    session.pop('current_index', None)
    
    return render_template('results.html', total_reviewed=total_reviewed, total_forgotten=total_forgotten)

# --- 路由：重新复习 ---
@app.route('/rereview')
def rereview():
    forgotten_deck = session.get('forgotten_deck', [])
    if not forgotten_deck:
        flash('没有“没记住”的单词可供复习')
        return redirect(url_for('index'))

    random.shuffle(forgotten_deck)
    
    session['review_deck'] = forgotten_deck
    session['current_index'] = 0
    
    session['forgotten_deck'] = []
    session['forgotten_words_raw'] = []
    
    return redirect(url_for('review'))

# --- 路由：下载 "没记住" 的单词 ---
# 【!! 重大修改 !!】
@app.route('/download_forgotten')
def download_forgotten():
    forgotten_words_raw = session.get('forgotten_words_raw', [])
    if not forgotten_words_raw:
        flash('没有“没记住”的单词可供下载')
        return redirect(url_for('results'))

    # 1. 在内存中创建 DataFrame
    df = pd.DataFrame(forgotten_words_raw)
    
    # 2. 创建一个内存中的“文件” (BytesIO)
    output = io.BytesIO()
    
    # 3. 将 Excel 文件写入这个内存“文件”
    df.to_excel(output, index=False, header=False)
    # 4. 将“指针”移到“文件”的开头
    output.seek(0)
    
    # 5. 清理 session
    session.pop('forgotten_deck', None)
    session.pop('forgotten_words_raw', None)
    
    # 6. 直接返回内存中的文件作为响应
    return Response(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment;filename=forgotten_words.xlsx"}
    )

# --- 启动 ---
# 【注意】部署时，Vercel 会自动处理启动，
# 但为了本地测试，我们保留这部分 (Vercel 会忽略它)
if __name__ == '__main__':
    # 你本地测试时，仍然需要创建这些目录
    os.makedirs(SESSION_FILE_DIR, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, host='0.0.0.0')