import sqlite3
import json
import time
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "therapy_sanctuary.db")

# 預設心靈小屋可購買家具清單 (Decors & Furnishings)
DEFAULT_DECOR_ITEMS = [
    {
        "id": "decor_fireplace",
        "name": "🔥 溫暖暖陽壁爐",
        "desc": "劈啪作響的微光柴火，為小屋帶來無限安全感",
        "price": 60,
        "icon": "🔥",
        "slot": "heater"
    },
    {
        "id": "decor_beanbag",
        "name": "🛋️ 雲朵羊毛懶骨頭",
        "desc": "整個人陷進去的極致柔軟，卸下所有身體緊繃",
        "price": 80,
        "icon": "🛋️",
        "slot": "seat"
    },
    {
        "id": "decor_plant",
        "name": "🪴 療癒龜背芋盆栽",
        "desc": "欣欣向榮的綠意，散發靜謐舒緩的生命力",
        "price": 40,
        "icon": "🪴",
        "slot": "plant"
    },
    {
        "id": "decor_skylight",
        "name": "🌌 璀璨星空觀景天窗",
        "desc": "抬頭就能看見浩瀚銀河，提醒你宇宙正溫柔包容著你",
        "price": 120,
        "icon": "🌌",
        "slot": "window"
    },
    {
        "id": "decor_gramophone",
        "name": "📻 復古心靈留聲機",
        "desc": "播放著黑膠唱片的柔和旋律，濾除外在世界所有喧囂",
        "price": 100,
        "icon": "📻",
        "slot": "music"
    },
    {
        "id": "decor_candle",
        "name": "🕯️ 薰衣草舒緩香氛蠟燭",
        "desc": "淡淡的薰衣草與洋甘菊香氣，安撫每一根緊繃的神經",
        "price": 30,
        "icon": "🕯️",
        "slot": "table"
    }
]

# 動物親密度升級明信片庫 (Postcards from Companions)
COMPANION_POSTCARDS = {
    "samoyed": {
        2: {"title": "☀️ 小薩的晨曦明信片", "content": "「只要你願意轉過身，小薩隨時都在這裡等你！今天也要對自己溫柔一點喔！」", "bg": "#FFF9EE"},
        3: {"title": "🐾 靈魂摯友紀念信", "content": "「遇見你之後，小薩的生活變得好溫暖。謝謝你願意把心事跟我分享，你真的很珍貴！」", "bg": "#FDF3E3"}
    },
    "cat": {
        2: {"title": "🌙 芝麻的呼嚕信件", "content": "「(把毛茸茸的小肉墊放在你手心) 累了就放空吧，不說話的時候，我也一直都在。」", "bg": "#F5F2F9"},
        3: {"title": "🐈 靜謐守護者的誓言", "content": "「這個世界雖然很吵，但在芝麻的小角落裡，你可以永遠做最真實的自己。」", "bg": "#EFEAF6"}
    },
    "bear": {
        2: {"title": "☕ 大熊的熱可可明信片", "content": "「無論今天外面下了多大的雨，大熊隨時為你準備好熱可可和大熊抱。」", "bg": "#F9F3EC"},
        3: {"title": "🛡️ 堅固避風港的約定", "content": "「辛苦了。你在大熊這裡永遠不需要逞強，安心把重量靠過來吧。」", "bg": "#F3E8DB"}
    },
    "rabbit": {
        2: {"title": "🌸 波波的溫柔小紙條", "content": "「你的每一滴委屈眼淚，波波都好好接住了。你已經做得很棒了，抱抱你！」", "bg": "#FAF1F3"},
        3: {"title": "🐰 自我慈悲同盟誓言", "content": "「別再責怪自己了，生而為人本來就會累。從今天起，我們一起溫柔善待自己。」", "bg": "#F6E4E8"}
    }
}

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. 用戶表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        nickname TEXT DEFAULT '小夥伴',
        streak_days INTEGER DEFAULT 1,
        last_active_date TEXT,
        soul_energy INTEGER DEFAULT 80,
        star_coins INTEGER DEFAULT 150,
        is_vip INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)

    # 2. 動物親密度表 (Affinity)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companion_affinity (
        user_id TEXT,
        companion_id TEXT,
        level INTEGER DEFAULT 1,
        exp INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, companion_id)
    )
    """)

    # 3. 心靈小屋裝飾表 (Sanctuary Decor)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sanctuary_decor (
        user_id TEXT,
        item_id TEXT,
        is_equipped INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, item_id)
    )
    """)

    # 4. 歷史對話表 (Chat History)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        companion_id TEXT,
        role TEXT,
        content TEXT,
        created_at TEXT
    )
    """)

    # 5. 感恩日記表 (Gratitude Logs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gratitude_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        content TEXT,
        created_at TEXT
    )
    """)

    # 6. 時空膠囊表 (Time Capsules)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS time_capsules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        target_person TEXT,
        content TEXT,
        guardian_companion TEXT,
        created_at TEXT
    )
    """)

    # 7. 每日任務完成紀錄表 (Daily Quests)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_quests (
        user_id TEXT,
        quest_date TEXT,
        quest_key TEXT,
        is_completed INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, quest_date, quest_key)
    )
    """)

    conn.commit()
    conn.close()

# 取得或建立單一用戶資料
def get_or_create_user(user_id="default_user"):
    init_database()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today_str = time.strftime("%Y-%m-%d")
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        cursor.execute("""
        INSERT INTO users (id, nickname, streak_days, last_active_date, soul_energy, star_coins, is_vip, created_at)
        VALUES (?, '小夥伴', 1, ?, 85, 150, 0, ?)
        """, (user_id, today_str, now_str))
        
        # 贈送一件初始壁爐家具
        cursor.execute("INSERT OR REPLACE INTO sanctuary_decor (user_id, item_id, is_equipped) VALUES (?, 'decor_fireplace', 1)", (user_id,))
        cursor.execute("INSERT OR REPLACE INTO sanctuary_decor (user_id, item_id, is_equipped) VALUES (?, 'decor_plant', 1)", (user_id,))
        
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
    else:
        # 檢查連續登入天數
        last_date = row["last_active_date"]
        if last_date != today_str:
            # 昨天或更早登入
            streak = row["streak_days"] + 1
            cursor.execute("UPDATE users SET streak_days = ?, last_active_date = ?, soul_energy = MIN(100, soul_energy + 10) WHERE id = ?", (streak, today_str, user_id))
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
    user_dict = dict(row)
    conn.close()
    return user_dict

# 增加星光幣
def add_star_coins(user_id, amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET star_coins = star_coins + ? WHERE id = ?", (amount, user_id))
    conn.commit()
    conn.close()

# 取得夥伴親密度與等級
def get_companion_affinity(user_id, companion_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companion_affinity WHERE user_id = ? AND companion_id = ?", (user_id, companion_id))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO companion_affinity (user_id, companion_id, level, exp) VALUES (?, ?, 1, 0)", (user_id, companion_id))
        conn.commit()
        conn.close()
        return {"level": 1, "exp": 0, "next_level_exp": 100}
    
    level = row["level"]
    exp = row["exp"]
    conn.close()
    return {"level": level, "exp": exp, "next_level_exp": level * 100}

# 增加親密度經驗值 (並自動升級)
def add_affinity_exp(user_id, companion_id, exp_amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companion_affinity WHERE user_id = ? AND companion_id = ?", (user_id, companion_id))
    row = cursor.fetchone()
    
    cur_level = row["level"] if row else 1
    cur_exp = (row["exp"] if row else 0) + exp_amount
    needed_exp = cur_level * 100
    leveled_up = False
    
    while cur_exp >= needed_exp and cur_level < 5:
        cur_exp -= needed_exp
        cur_level += 1
        needed_exp = cur_level * 100
        leveled_up = True
        
    cursor.execute("INSERT OR REPLACE INTO companion_affinity (user_id, companion_id, level, exp) VALUES (?, ?, ?, ?)",
                   (user_id, companion_id, cur_level, cur_exp))
    conn.commit()
    conn.close()
    return {"level": cur_level, "exp": cur_exp, "leveled_up": leveled_up}

# 取得已購買與裝備之家具
def get_user_decor_items(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sanctuary_decor WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    owned_map = {r["item_id"]: bool(r["is_equipped"]) for r in rows}
    return owned_map

# 購買家具
def buy_decor_item(user_id, item_id, price):
    user = get_or_create_user(user_id)
    if user["star_coins"] < price:
        return False, "星光幣不足喔！快去完成每日心靈任務賺取吧～"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET star_coins = star_coins - ? WHERE id = ?", (price, user_id))
    cursor.execute("INSERT OR REPLACE INTO sanctuary_decor (user_id, item_id, is_equipped) VALUES (?, ?, 1)", (user_id, item_id))
    conn.commit()
    conn.close()
    return True, "購買成功！已為你佈置進心靈小屋囉！✨"

# 切換家具裝備狀態
def toggle_decor_equip(user_id, item_id, new_state):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE sanctuary_decor SET is_equipped = ? WHERE user_id = ? AND item_id = ?", (1 if new_state else 0, user_id, item_id))
    conn.commit()
    conn.close()

# 儲存對話紀錄
def save_chat_message(user_id, companion_id, role, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (user_id, companion_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                   (user_id, companion_id, role, content, time.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# 載入歷史對話
def load_chat_history(user_id, companion_id, limit=20):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM chat_history WHERE user_id = ? AND companion_id = ? ORDER BY id DESC LIMIT ?", (user_id, companion_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

# 每日任務狀態管理
def get_daily_quest_status(user_id):
    today_str = time.strftime("%Y-%m-%d")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quest_key, is_completed FROM daily_quests WHERE user_id = ? AND quest_date = ?", (user_id, today_str))
    rows = cursor.fetchall()
    conn.close()
    
    status_map = {r["quest_key"]: bool(r["is_completed"]) for r in rows}
    
    quests = [
        {"key": "chat_companion", "title": "🌅 向動物夥伴傾訴一次心事", "reward_coins": 20, "reward_exp": 25, "done": status_map.get("chat_companion", False)},
        {"key": "do_breathing", "title": "🌬️ 進行 2 分鐘正念盒式呼吸", "reward_coins": 20, "reward_exp": 20, "done": status_map.get("do_breathing", False)},
        {"key": "log_gratitude", "title": "🌱 記錄 1 條感恩花園日記", "reward_coins": 25, "reward_exp": 30, "done": status_map.get("log_gratitude", False)},
        {"key": "pop_bubbles", "title": "🫧 捏破 10 顆以上焦慮泡泡", "reward_coins": 15, "reward_exp": 15, "done": status_map.get("pop_bubbles", False)}
    ]
    return quests

# 完成任務領取獎勵
def complete_daily_quest(user_id, quest_key, companion_id="samoyed"):
    today_str = time.strftime("%Y-%m-%d")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT is_completed FROM daily_quests WHERE user_id = ? AND quest_date = ? AND quest_key = ?", (user_id, today_str, quest_key))
    row = cursor.fetchone()
    
    if row and row["is_completed"]:
        conn.close()
        return False, "今天已經領取過這項任務的獎勵囉！"
    
    # 標記完成
    cursor.execute("INSERT OR REPLACE INTO daily_quests (user_id, quest_date, quest_key, is_completed) VALUES (?, ?, ?, 1)", (user_id, today_str, quest_key))
    conn.commit()
    conn.close()
    
    rewards = {
        "chat_companion": (20, 25),
        "do_breathing": (20, 20),
        "log_gratitude": (25, 30),
        "pop_bubbles": (15, 15)
    }
    coins, exp = rewards.get(quest_key, (10, 10))
    
    add_star_coins(user_id, coins)
    add_affinity_exp(user_id, companion_id, exp)
    return True, f"任務完成！獲得 +{coins} 🌟星光幣 與 +{exp} 💖親密度經驗值！"

# 感恩日記與時空膠囊持久化
def save_gratitude_log(user_id, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = time.strftime("%Y-%m-%d %H:%M")
    cursor.execute("INSERT INTO gratitude_logs (user_id, content, created_at) VALUES (?, ?, ?)", (user_id, content, now_str))
    conn.commit()
    conn.close()

def load_gratitude_logs(user_id, limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT content, created_at FROM gratitude_logs WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [{"content": r["content"], "date": r["created_at"]} for r in rows]

def save_time_capsule(user_id, target, content, guardian):
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = time.strftime("%Y-%m-%d %H:%M")
    cursor.execute("INSERT INTO time_capsules (user_id, target_person, content, guardian_companion, created_at) VALUES (?, ?, ?, ?, ?)",
                   (user_id, target, content, guardian, now_str))
    conn.commit()
    conn.close()

def load_time_capsules(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT target_person, content, guardian_companion, created_at FROM time_capsules WHERE user_id = ? ORDER BY id DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"to": r["target_person"], "content": r["content"], "guardian": r["guardian_companion"], "date": r["created_at"]} for r in rows]
