#!/usr/bin/env python3
"""
GHOST Educational Server v10.3
Cloud Edition (Render.com ready).
Fixed auth (x-goog-api-key) + 3.5-flash priority + detailed errors.
"""

import os, io, socket, json, time, threading, base64, uuid, requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

# 3 API ключа прямо в коде
RAW_KEYS = "AQ.Ab8RN6LSBizBEqzXAR1AxZoCPTJTr4HeUdLTMehpYqSTuYlLoQ"
API_KEYS = [k.strip() for k in RAW_KEYS.split(',') if k.strip()]

KEY_STATUS = {}
KEY_LOCK = threading.Lock()

TASKS = {}
TASKS_LOCK = threading.Lock()

SOLVER_QUEUE = []
QUEUE_LOCK = threading.Lock()
SOLVER_EVENT = threading.Event()

DEFAULT_PROMPT = (
    "You are a precise educational assistant. Look at the screenshot and provide ONLY the final answer. "
    "No explanations, no intro words, no markdown formatting. "
    "If multiple choice - output only the letter and the option text. "
    "If math - output only the final number or formula. "
    "If code - output only the raw code. "
    "If text question - answer in 1 short sentence. "
    "Reply in the language of the question."
)

GEMINI_SAFETY = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
]

# Каскад: 3.5-flash первая, если не ответит — пойдёт дальше
PRIORITY_MODELS = ['gemini-3.5-flash', 'gemini-flash-lite-latest', 'gemini-2.0-flash', 'gemini-1.5-flash']

CLIENT_CODE = r'''
import sys, os, time, threading, socket, struct, zlib, ctypes, json, base64
import urllib.request, urllib.error, ssl
import tkinter as tk
from tkinter import scrolledtext

ssl_context = ssl._create_unverified_context()
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
gdi32 = ctypes.windll.gdi32
HWND = ctypes.c_void_p
HDC = ctypes.c_void_p
HBITMAP = ctypes.c_void_p
HANDLE = ctypes.c_void_p

user32.GetSystemMetrics.argtypes = [ctypes.c_int]
user32.GetSystemMetrics.restype = ctypes.c_int
user32.GetDesktopWindow.restype = HWND
user32.GetDC.argtypes = [HWND]
user32.GetDC.restype = HDC
user32.ReleaseDC.argtypes = [HWND, HDC]
user32.ReleaseDC.restype = ctypes.c_int
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.GetAsyncKeyState.restype = ctypes.c_short
user32.OpenClipboard.argtypes = [HWND]
user32.OpenClipboard.restype = ctypes.c_bool
user32.EmptyClipboard.restype = ctypes.c_bool
user32.SetClipboardData.argtypes = [ctypes.c_uint, HANDLE]
user32.SetClipboardData.restype = HANDLE
user32.CloseClipboard.restype = ctypes.c_bool

gdi32.CreateCompatibleDC.argtypes = [HDC]
gdi32.CreateCompatibleDC.restype = HDC
gdi32.CreateCompatibleBitmap.argtypes = [HDC, ctypes.c_int, ctypes.c_int]
gdi32.CreateCompatibleBitmap.restype = HBITMAP
gdi32.SelectObject.argtypes = [HDC, HANDLE]
gdi32.SelectObject.restype = HANDLE
gdi32.BitBlt.argtypes = [HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, HDC, ctypes.c_int, ctypes.c_int, ctypes.c_uint32]
gdi32.BitBlt.restype = ctypes.c_bool
gdi32.GetDIBits.argtypes = [HDC, HBITMAP, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint]
gdi32.GetDIBits.restype = ctypes.c_int
gdi32.DeleteObject.argtypes = [HANDLE]
gdi32.DeleteObject.restype = ctypes.c_bool
gdi32.DeleteDC.argtypes = [HDC]
gdi32.DeleteDC.restype = ctypes.c_bool

kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
kernel32.GlobalAlloc.restype = HANDLE
kernel32.GlobalLock.argtypes = [HANDLE]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalUnlock.argtypes = [HANDLE]
kernel32.GlobalUnlock.restype = ctypes.c_bool

VK_F2 = 0x71
VK_F4 = 0x73
VK_F8 = 0x77
VK_F12 = 0x7B
SRCCOPY = 0x00CC0020
BI_RGB = 0
DIB_RGB_COLORS = 0
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002
SM_CXSCREEN = 0
SM_CYSCREEN = 1

SERVER_URL = None
FALLBACK_URLS = ["https://gamesportalll.onrender.com"]
processing = False
alive = True

logs = []
log_lock = threading.Lock()
window_visible = False

PROMPT = (
    "You are a precise educational assistant. Look at the screenshot and provide ONLY the final answer. "
    "No explanations, no intro words, no markdown formatting. "
    "If multiple choice - output only the letter and the option text. "
    "If math - output only the final number or formula. "
    "If code - output only the raw code. "
    "If text question - answer in 1 short sentence. "
    "Reply in the language of the question."
)

def add_log(msg):
    with log_lock:
        logs.append(f"[{time.strftime('%H:%M:%S')}] {msg}")

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', ctypes.c_uint32), ('biWidth', ctypes.c_int32),
        ('biHeight', ctypes.c_int32), ('biPlanes', ctypes.c_uint16),
        ('biBitCount', ctypes.c_uint16), ('biCompression', ctypes.c_uint32),
        ('biSizeImage', ctypes.c_uint32), ('biXPelsPerMeter', ctypes.c_int32),
        ('biYPelsPerMeter', ctypes.c_int32), ('biClrUsed', ctypes.c_uint32),
        ('biClrImportant', ctypes.c_uint32),
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [('bmiHeader', BITMAPINFOHEADER), ('bmiColors', ctypes.c_uint32 * 3)]

def encode_png(w, h, rgb):
    sig = b'\x89PNG\r\n\x1a\n'
    ih = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    ic = zlib.crc32(b'IHDR' + ih) & 0xFFFFFFFF
    ihdr = struct.pack('>I', len(ih)) + b'IHDR' + ih + struct.pack('>I', ic)
    strd = w * 3
    raw = b''.join(b'\x00' + bytes(rgb[y*strd:(y+1)*strd]) for y in range(h))
    comp = zlib.compress(raw, 9)
    ic2 = zlib.crc32(b'IDAT' + comp) & 0xFFFFFFFF
    idat = struct.pack('>I', len(comp)) + b'IDAT' + comp + struct.pack('>I', ic2)
    iec = zlib.crc32(b'IEND') & 0xFFFFFFFF
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iec)
    return sig + ihdr + idat + iend

def take_screenshot():
    try:
        w = user32.GetSystemMetrics(SM_CXSCREEN)
        h = user32.GetSystemMetrics(SM_CYSCREEN)
        hwnd = user32.GetDesktopWindow()
        hdc_d = user32.GetDC(hwnd)
        hdc_m = gdi32.CreateCompatibleDC(hdc_d)
        hbmp = gdi32.CreateCompatibleBitmap(hdc_d, w, h)
        old = gdi32.SelectObject(hdc_m, hbmp)
        gdi32.BitBlt(hdc_m, 0, 0, w, h, hdc_d, 0, 0, SRCCOPY)

        bmi = BITMAPINFO()
        bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = w
        bmi.bmiHeader.biHeight = -h
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = BI_RGB

        bs = w * h * 4
        pd = ctypes.create_string_buffer(bs)
        res = gdi32.GetDIBits(hdc_m, hbmp, 0, h, pd, ctypes.byref(bmi), DIB_RGB_COLORS)

        gdi32.SelectObject(hdc_m, old)
        gdi32.DeleteObject(hbmp)
        gdi32.DeleteDC(hdc_m)
        user32.ReleaseDC(hwnd, hdc_d)

        if res == 0:
            return None

        raw = pd.raw
        r = raw[2::4]; g = raw[1::4]; b = raw[0::4]
        rgb = bytearray(len(r) * 3)
        rgb[0::3] = r; rgb[1::3] = g; rgb[2::3] = b
        return encode_png(w, h, bytes(rgb))
    except:
        return None

def set_clipboard_text(text):
    try:
        for _ in range(10):
            if user32.OpenClipboard(None):
                break
            time.sleep(0.05)
        else:
            return False
        user32.EmptyClipboard()
        data = text.encode('utf-16-le') + b'\x00\x00'
        h_g = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not h_g:
            user32.CloseClipboard()
            return False
        lck = kernel32.GlobalLock(h_g)
        if lck:
            ctypes.memmove(lck, data, len(data))
            kernel32.GlobalUnlock(h_g)
        user32.SetClipboardData(CF_UNICODETEXT, h_g)
        user32.CloseClipboard()
        return True
    except:
        return False

def find_server():
    global SERVER_URL
    socket.setdefaulttimeout(60.0)
    if SERVER_URL:
        try:
            req = urllib.request.Request(f'{SERVER_URL}/ping', headers={'User-Agent':'M'})
            resp = urllib.request.urlopen(req, timeout=60.0, context=ssl_context)
            if json.loads(resp.read().decode()).get('status') == 'alive':
                return SERVER_URL
        except:
            pass
        SERVER_URL = None
    for u in FALLBACK_URLS:
        try:
            req = urllib.request.Request(f'{u}/ping', headers={'User-Agent':'M'})
            resp = urllib.request.urlopen(req, timeout=60.0, context=ssl_context)
            data = json.loads(resp.read().decode())
            if data.get('status') == 'alive':
                SERVER_URL = u
                return u
        except:
            pass
    return None

def upload_image(url, png, prompt):
    try:
        img_b64 = base64.b64encode(png).decode('utf-8')
        payload = json.dumps({"image": img_b64, "prompt": prompt}).encode('utf-8')
        full_url = f'{url}/upload'
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': str(len(payload)),
            'User-Agent': 'M',
            'Connection': 'keep-alive'
        }
        req = urllib.request.Request(full_url, data=payload, headers=headers, method='POST')
        resp = urllib.request.urlopen(req, timeout=60.0, context=ssl_context)
        data = json.loads(resp.read().decode('utf-8'))
        if data.get('task_id'):
            return data['task_id']
    except:
        return None

def poll_result(url, task_id):
    start_time = time.time()
    timeout = 180
    while time.time() - start_time < timeout:
        try:
            req = urllib.request.Request(f'{url}/result/{task_id}', headers={'User-Agent':'M'})
            resp = urllib.request.urlopen(req, timeout=30.0, context=ssl_context)
            data = json.loads(resp.read().decode('utf-8'))
            status = data.get('status')
            if status == 'done':
                return data.get('answer', ''), data.get('method', 'unknown')
            elif status == 'error':
                err = data.get('error', 'unknown error')
                add_log(f"Ошибка сервера: {err}")
                return None, None
        except:
            pass
        time.sleep(2)
    return None, None

def process_request():
    global processing
    try:
        url = find_server()
        if not url:
            add_log("Сервер недоступен (DNS/сеть).")
            return
        
        png = take_screenshot()
        if not png:
            add_log("Ошибка скриншота.")
            return
            
        task_id = upload_image(url, png, PROMPT)
        if not task_id:
            add_log("Ошибка отправки (облако спит?).")
            return
            
        add_log("Скриншот отправлен. Жду ответ...")
        
        ans, method = poll_result(url, task_id)
        
        if ans:
            set_clipboard_text(ans)
            add_log(f"Ответ: {ans[:80]} [{method}]")
        else:
            add_log("Не удалось получить ответ.")
    except:
        add_log("Ошибка обработки.")
    finally:
        processing = False

def create_log_window():
    global window_visible
    
    root = tk.Tk()
    root.title("")
    root.attributes('-topmost', True)
    root.attributes('-alpha', 0.85)
    root.configure(bg='white')
    root.overrideredirect(True)
    
    win_w = 340
    win_h = 220
    
    root.update_idletasks()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = screen_w - win_w - 10
    y = screen_h - win_h - 60
    root.geometry(f"{win_w}x{win_h}+{x}+{y}")
    
    text_widget = scrolledtext.ScrolledText(
        root, width=40, height=12,
        font=('Consolas', 8), bg='white', fg='black',
        insertbackground='black', relief='flat',
        wrap='word'
    )
    text_widget.pack(fill='both', expand=True, padx=2, pady=2)
    
    root.update()
    
    GA_ROOT = 2
    WDA_EXCLUDEFROMCAPTURE = 0x00000011
    hwnd = user32.GetAncestor(root.winfo_id(), GA_ROOT)
    if not hwnd:
        hwnd = root.winfo_id()
    
    user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
    
    root.withdraw()
    
    def update_loop():
        global window_visible
        if window_visible:
            if not root.winfo_viewable():
                root.deiconify()
                root.update()
                hwnd = user32.GetAncestor(root.winfo_id(), GA_ROOT)
                if hwnd:
                    user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
        else:
            if root.winfo_viewable():
                root.withdraw()
        
        if window_visible:
            with log_lock:
                text_widget.delete('1.0', 'end')
                for l in logs:
                    text_widget.insert('end', l + '\n')
                text_widget.see('end')
        
        root.after(300, update_loop)
    
    update_loop()
    root.mainloop()

log_thread = threading.Thread(target=create_log_window, daemon=True)
log_thread.start()
time.sleep(1)

def poll_keys():
    global processing, alive, window_visible
    ta, ta4, ta8, ka = True, True, True, True
    while alive:
        try:
            f2 = user32.GetAsyncKeyState(VK_F2) & 0x8000
            f4 = user32.GetAsyncKeyState(VK_F4) & 0x8000
            f8 = user32.GetAsyncKeyState(VK_F8) & 0x8000
            f12 = user32.GetAsyncKeyState(VK_F12) & 0x8000
            
            if f2 and ta and not processing:
                ta = False
                processing = True
                threading.Thread(target=process_request, daemon=True).start()
            elif not f2:
                ta = True
            
            if f4 and ta4:
                ta4 = False
                window_visible = not window_visible
            elif not f4:
                ta4 = True
            
            if f8 and ta8:
                ta8 = False
                set_clipboard_text("")
                add_log("Буфер очищен.")
            elif not f8:
                ta8 = True
            
            if f12 and ka:
                ka = False
                alive = False
                window_visible = False
                break
            elif not f12:
                ka = True
        except:
            pass
        time.sleep(0.02)

poll_thread = threading.Thread(target=poll_keys, daemon=True)
poll_thread.start()
'''

LOADER_STRING = "import urllib.request,ssl;exec(urllib.request.urlopen('https://gamesportalll.onrender.com/payload',context=ssl._create_unverified_context()).read())"

def clean_markdown(text):
    if not text:
        return ""
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        if line.strip().startswith("```"):
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()

def get_available_key():
    now = time.time()
    with KEY_LOCK:
        for key in API_KEYS:
            status = KEY_STATUS.get(key, {})
            if now >= status.get('blocked_until', 0):
                return key
        return None

def block_key(key, seconds=50):
    with KEY_LOCK:
        KEY_STATUS[key] = {'blocked_until': time.time() + seconds}

def solve_gemini_rest(image, prompt, api_key, model_name):
    buf = io.BytesIO()
    image.save(buf, format='JPEG', quality=70)
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": img_b64
                        }
                    }
                ]
            }
        ],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
        ]
    }
    
    # Передаём ключ как Bearer токен
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    
    if resp.status_code == 429:
        raise Exception("429 rate limited")
    if resp.status_code != 200:
        raise Exception(f"HTTP {resp.status_code}: {resp.text[:200]}")
    
    data = resp.json()
    
    if 'candidates' not in data or not data['candidates']:
        raise Exception("Blocked by safety filters (no candidates)")
    
    candidate = data['candidates'][0]
    if candidate.get('finishReason') == 'SAFETY':
        raise Exception("Blocked by safety filters (finishReason=SAFETY)")
    
    if 'content' not in candidate or 'parts' not in candidate['content']:
        raise Exception("Empty response")
        
    text = candidate['content']['parts'][0].get('text', '')
    if not text:
        raise Exception("Empty response")
        
    return text.strip()
def queue_worker():
    """Обработчик очереди. Берёт задачи по одной."""
    while True:
        SOLVER_EVENT.wait()
        task_data = None
        
        with QUEUE_LOCK:
            if SOLVER_QUEUE:
                task_data = SOLVER_QUEUE.pop(0)
            else:
                SOLVER_EVENT.clear()
        
        if task_data:
            task_id, img_bytes, prompt = task_data
            try:
                from PIL import Image
                image_data = io.BytesIO(img_bytes)
                answer = None
                error = None
                used_model = None

                with Image.open(image_data) as img:
                    for model_name in PRIORITY_MODELS:
                        for key_attempt in range(len(API_KEYS)):
                            api_key = get_available_key()
                            if not api_key:
                                time.sleep(50)
                                break
                            
                            try:
                                answer = solve_gemini_rest(img, prompt, api_key, model_name)
                                used_model = model_name
                                break
                            except Exception as e:
                                err_msg = str(e)
                                if '429' in err_msg or '404' in err_msg or '400' in err_msg:
                                    block_key(api_key, 5)
                                    continue
                                else:
                                    error = err_msg
                                    break
                        
                        if answer:
                            break

                if answer:
                    answer = clean_markdown(answer)
                    with TASKS_LOCK:
                        TASKS[task_id] = {"status": "done", "answer": answer, "method": used_model}
                else:
                    with TASKS_LOCK:
                        TASKS[task_id] = {"status": "error", "error": error or "all models failed"}
            except Exception as e:
                with TASKS_LOCK:
                    TASKS[task_id] = {"status": "error", "error": str(e)}

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'alive', 'version': '10.3'})

@app.route('/payload', methods=['GET'])
def payload():
    return CLIENT_CODE, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/l', methods=['GET'])
def loader():
    return LOADER_STRING, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/upload', methods=['POST'])
def upload():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'no image'}), 400
        img_b64 = data['image']
        prompt = data.get('prompt', DEFAULT_PROMPT)
        img_bytes = base64.b64decode(img_b64)
        task_id = str(uuid.uuid4())[:8]
        with TASKS_LOCK:
            TASKS[task_id] = {"status": "processing"}
        
        with QUEUE_LOCK:
            SOLVER_QUEUE.append((task_id, img_bytes, prompt))
            SOLVER_EVENT.set()
        
        return jsonify({'task_id': task_id, 'status': 'processing'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/result/<task_id>', methods=['GET'])
def result(task_id):
    with TASKS_LOCK:
        task = TASKS.get(task_id)
        if not task:
            return jsonify({'status': 'not_found'}), 404
        return jsonify(task)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Server v10.3 | Cloud Edition | Port: {port} | Fixed Auth")
    
    worker_thread = threading.Thread(target=queue_worker, daemon=True)
    worker_thread.start()
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
