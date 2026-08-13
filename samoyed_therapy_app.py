import streamlit as st
import random
import time
import os
import json
import base64
from openai import OpenAI
import database as db

# ==============================================================================
# 🐾 動物心靈諮商室 (Animal Therapy Sanctuary) — Live 2D 心靈寵物養成手遊版
# ==============================================================================

st.set_page_config(
    page_title="動物心靈諮商室 — 你的 Live 2D 心靈陪伴神獸與小屋",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 輔助函式：將 SVG 代碼轉為標準 Base64 Data URI
def svg_to_data_uri(svg_str):
    clean_svg = "".join(line.strip() for line in svg_str.strip().splitlines())
    b64 = base64.b64encode(clean_svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"

# 2. 定義 10 款特色動物心靈夥伴矩陣 (包含神獸專屬台詞與喜愛食物)
RAW_COMPANIONS = {
    "samoyed": {
        "id": "samoyed",
        "name": "薩摩耶・小薩",
        "species": "薩摩耶犬",
        "emoji": "🐶",
        "title": "暖陽陪伴師",
        "badge": "☀️ 人本主義・無條件正向關懷 (UPR)",
        "is_free": True, # 免費領養旗艦伴侶
        "motto": "只要你轉過身，小薩隨時都在這裡溫柔等你喔！",
        "summary": "元氣熱情、無條件接納、永遠的忠誠後盾。擅長用溫暖打氣化解孤單與自我懷疑。",
        "psychology": "【卡爾・羅傑斯人本主義】透過無條件正向關懷（Unconditional Positive Regard）與真誠一致，給予全然的肯定與愛，消除自我價值感低落。",
        "default_self_ref": "小薩",
        "favorite_snack": "bone",
        "pet_quotes": [
            "（把毛茸茸的下巴靠在你掌心）小薩好喜歡你摸摸我喔！今天也辛苦了～",
            "（開心地用力搖尾巴）只要看見你，小薩整顆心都暖呼呼的！☀️",
            "（蹭蹭你的手）不管發生什麼事，小薩永遠都是你最忠誠的後盾！"
        ],
        "theme_color": "#C2995F",
        "bg_color": "#F9F4EB",
        "bubble_color": "#EFE3D3",
        "actions": ["(安靜地靠近你身邊，投以溫暖信任的目光)"],
        "svg_avatar": """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<circle cx="50" cy="50" r="46" fill="#FDFBF7" stroke="#E2D5C3" stroke-width="3"/>
<polygon points="20,40 12,18 38,26" fill="#F4EDE2"/>
<polygon points="80,40 88,18 62,26" fill="#F4EDE2"/>
<polygon points="23,38 16,22 36,28" fill="#F9D2D2"/>
<polygon points="77,38 84,22 64,28" fill="#F9D2D2"/>
<ellipse cx="36" cy="46" rx="5" ry="6" fill="#423124"/>
<ellipse cx="64" cy="46" rx="5" ry="6" fill="#423124"/>
<circle cx="38" cy="44" r="2" fill="#FFFFFF"/>
<circle cx="66" cy="44" r="2" fill="#FFFFFF"/>
<ellipse cx="50" cy="56" rx="6" ry="4" fill="#3D2B1F"/>
<path d="M 44,60 Q 50,68 56,60" fill="none" stroke="#3D2B1F" stroke-width="2.5" stroke-linecap="round"/>
<path d="M 47,63 Q 50,71 53,63" fill="#F99F9F"/>
<circle cx="28" cy="55" r="5" fill="#FCD5D5" opacity="0.6"/>
<circle cx="72" cy="55" r="5" fill="#FCD5D5" opacity="0.6"/>
</svg>"""
    },
    "cat": {
        "id": "cat",
        "name": "英短貓・芝麻",
        "species": "英國短毛貓",
        "emoji": "🐱",
        "title": "靜謐守護者",
        "badge": "🌙 邊界陪伴・客體關係與存在主義",
        "is_free": False, # VIP 解鎖
        "motto": "不用勉強擠出笑容，想安靜待著時，芝麻就在旁邊陪你。",
        "summary": "安靜細膩、不給壓力、尊重個人邊界。用輕柔的呼嚕聲與默契陪伴化解緊繃與社交疲勞。",
        "psychology": "【客體關係與存在主義陪伴】提供足夠的安全心理邊界（Holding Environment），不強迫正向思考，安靜陪你面對孤獨與真實感受。",
        "default_self_ref": "芝麻",
        "favorite_snack": "fish",
        "pet_quotes": [
            "（發出極其輕柔舒服的呼嚕嚕聲～）……別說話，就這樣安靜待著也很好。",
            "（用軟綿綿的小肉墊碰碰你的手心）累了的話，芝麻允許你隨時放空。",
            "（舒服地瞇起雙眼）這個世界上，只有在你身邊芝麻才最放鬆。"
        ],
        "theme_color": "#7C6A8D",
        "bg_color": "#F4F1F7",
        "bubble_color": "#E4DEEC",
        "actions": ["(安靜地蜷縮在手邊，發出極其輕柔舒服的呼嚕聲)"],
        "svg_avatar": """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<circle cx="50" cy="50" r="46" fill="#E8E4EC" stroke="#C8C0D4" stroke-width="3"/>
<polygon points="22,42 16,14 42,26" fill="#8F82A0"/>
<polygon points="78,42 84,14 58,26" fill="#8F82A0"/>
<polygon points="24,38 19,19 39,28" fill="#E4AFBD"/>
<polygon points="76,38 81,19 61,28" fill="#E4AFBD"/>
<ellipse cx="36" cy="46" rx="6" ry="7" fill="#F3A63B"/>
<ellipse cx="64" cy="46" rx="6" ry="7" fill="#F3A63B"/>
<ellipse cx="36" cy="46" rx="2.5" ry="6" fill="#2E2438"/>
<ellipse cx="64" cy="46" rx="2.5" ry="6" fill="#2E2438"/>
<polygon points="50,54 46,51 54,51" fill="#E4AFBD"/>
<path d="M 46,55 Q 50,59 54,55" fill="none" stroke="#5A4E68" stroke-width="2" stroke-linecap="round"/>
<line x1="22" y1="52" x2="10" y2="49" stroke="#9A8FA8" stroke-width="1.5"/>
<line x1="22" y1="56" x2="10" y2="58" stroke="#9A8FA8" stroke-width="1.5"/>
<line x1="78" y1="52" x2="90" y2="49" stroke="#9A8FA8" stroke-width="1.5"/>
<line x1="78" y1="56" x2="90" y2="58" stroke="#9A8FA8" stroke-width="1.5"/>
</svg>"""
    },
    "bear": {
        "id": "bear",
        "name": "暖心熊・大熊",
        "species": "大棕熊",
        "emoji": "🐻",
        "title": "沉穩避風港",
        "badge": "🛡️ 安全依附・情緒焦點療法 (EFT)",
        "is_free": False,
        "motto": "世界太吵也沒關係，來大熊的懷裡好好歇一會兒吧。",
        "summary": "沉穩敦厚、大山般的包容、滿滿安全感。像避風港一樣承接所有疲憊，給予踏實大熊抱。",
        "psychology": "【情緒焦點療法 (EFT) 與安全依附理論】建立堅不可摧的情緒避風港（Safe Haven），讓內心焦慮與脆弱無處安放時，獲得深層厚實的安全依託。",
        "default_self_ref": "大熊",
        "favorite_snack": "honey",
        "pet_quotes": [
            "（張開厚實的大手臂）來，大熊給你一個最踏實的大熊抱！",
            "（沉穩地笑著）放心把重量靠過來吧，大熊永遠撐得住你。",
            "（遞過熱可可）外面風雨再大，這裡永遠是你的安全屋。"
        ],
        "theme_color": "#8B6547",
        "bg_color": "#F7F2EB",
        "bubble_color": "#EADECF",
        "actions": ["(遞上一杯熱氣騰騰的香濃熱可可，沉穩溫和地注視著你)"],
        "svg_avatar": """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<circle cx="50" cy="50" r="46" fill="#B38B6D" stroke="#8E6748" stroke-width="3"/>
<circle cx="22" cy="24" r="14" fill="#B38B6D" stroke="#8E6748" stroke-width="2"/>
<circle cx="78" cy="24" r="14" fill="#B38B6D" stroke="#8E6748" stroke-width="2"/>
<circle cx="22" cy="24" r="8" fill="#E2C4A6"/>
<circle cx="78" cy="24" r="8" fill="#E2C4A6"/>
<ellipse cx="50" cy="60" rx="20" ry="15" fill="#E2C4A6"/>
<ellipse cx="36" cy="42" rx="4" ry="5" fill="#382516"/>
<ellipse cx="64" cy="42" rx="4" ry="5" fill="#382516"/>
<circle cx="38" cy="40" r="1.5" fill="#FFFFFF"/>
<circle cx="66" cy="40" r="1.5" fill="#FFFFFF"/>
<ellipse cx="50" cy="54" rx="7" ry="5" fill="#382516"/>
<path d="M 45,61 Q 50,65 55,61" fill="none" stroke="#382516" stroke-width="2.5" stroke-linecap="round"/>
</svg>"""
    },
    "fox": {
        "id": "fox",
        "name": "靈動狐・小狐",
        "species": "赤狐",
        "emoji": "🦊",
        "title": "睿智啟發者",
        "badge": "✨ 認知重塑・敘事治療 (Narrative)",
        "is_free": False,
        "motto": "每片烏雲背後都有風的軌跡，小狐陪你換個角度看見力量。",
        "summary": "聰穎靈敏、善解人意、擅長看見盲點。用靈動有趣的視角幫你解構情緒背後的壓力框架。",
        "psychology": "【敘事治療與問題外化 (Externalization)】把「問題」與「個人價值」溫和拆分開來，引導看見被忽視的獨特生命力量與內在優勢。",
        "default_self_ref": "小狐",
        "favorite_snack": "berry",
        "pet_quotes": [
            "（靈巧地晃了晃蓬鬆的大尾巴）嘻嘻，摸到小狐的幸運尾巴，今天會有好事發生喔！",
            "（眨了眨靈動的大眼睛）別困在死胡同裡，我們一起換個視角看世界！",
            "（側頭微笑）你比任何煩惱都還要強大得多！"
        ],
        "theme_color": "#C46537",
        "bg_color": "#FBF2EC",
        "bubble_color": "#F3DFD1",
        "actions": ["(側著頭專注注視著你，眼神充滿靈氣與理解)"],
        "svg_avatar": """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<circle cx="50" cy="50" r="46" fill="#F4F0EA" stroke="#E2DACF" stroke-width="3"/>
<polygon points="20,40 14,12 40,24" fill="#C95F2B"/>
<polygon points="80,40 86,12 60,24" fill="#C95F2B"/>
<polygon points="22,36 17,17 37,26" fill="#422518"/>
<polygon points="78,36 83,17 63,26" fill="#422518"/>
<path d="M 20,44 Q 50,78 50,78 Q 50,78 80,44 Z" fill="#D96E37"/>
<path d="M 22,46 Q 50,82 50,82 Q 50,82 78,46 Q 50,62 22,46 Z" fill="#FFFFFF"/>
<ellipse cx="36" cy="46" rx="4" ry="5" fill="#301A10"/>
<ellipse cx="64" cy="46" rx="4" ry="5" fill="#301A10"/>
<circle cx="37" cy="44" r="1.5" fill="#FFFFFF"/>
<circle cx="65" cy="44" r="1.5" fill="#FFFFFF"/>
<polygon points="50,68 46,64 54,64" fill="#301A10"/>
</svg>"""
    },
    "rabbit": {
        "id": "rabbit",
        "name": "垂耳兔・波波",
        "species": "垂耳兔",
        "emoji": "🐰",
        "title": "溫柔共情者",
        "badge": "🌸 自我慈悲・自我同情理論 (Self-Compassion)",
        "is_free": False,
        "motto": "你的每一滴委屈眼淚，波波都會溫柔接住，沒事的。",
        "summary": "軟萌細膩、感受力超強、百分百同理心。專注傾聽心底最深層的酸楚，給予最純粹的自我慈悲撫慰。",
        "psychology": "【克莉絲汀・內夫自我慈悲理論 (Self-Compassion)】涵蓋自我善待（Self-Kindness）、共同人性（Common Humanity）與正念覺察，打破嚴苛的自我苛責。",
        "default_self_ref": "波波",
        "favorite_snack": "carrot",
        "pet_quotes": [
            "（輕輕動了動軟軟的垂耳）波波永遠在這裡溫柔接住你的所有脆弱。",
            "（軟綿綿地貼在你手邊）別再罵自己了，你已經非常努力了喔！💖",
            "（眼裡閃爍著淚光）謝謝你對自己這麼溫柔，抱抱你～"
        ],
        "theme_color": "#B86B77",
        "bg_color": "#FAF1F3",
        "bubble_color": "#F2DDE1",
        "actions": ["(輕輕動了動長長柔軟的垂耳，溫柔凝望著你)"],
        "svg_avatar": """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<circle cx="50" cy="50" r="46" fill="#FBF8F9" stroke="#EADEE2" stroke-width="3"/>
<path d="M 28,34 C 15,35 12,65 18,74 C 22,78 28,70 26,45 Z" fill="#E6D3D8"/>
<path d="M 72,34 C 85,35 88,65 82,74 C 78,78 72,70 74,45 Z" fill="#E6D3D8"/>
<path d="M 26,38 C 18,40 16,62 20,70 C 23,73 26,67 25,48 Z" fill="#F4CAD3"/>
<path d="M 74,38 C 82,40 84,62 80,70 C 77,73 74,67 75,48 Z" fill="#F4CAD3"/>
<circle cx="50" cy="52" r="28" fill="#FBF8F9"/>
<ellipse cx="40" cy="50" rx="4" ry="5" fill="#583B43"/>
<ellipse cx="60" cy="50" rx="4" ry="5" fill="#583B43"/>
<circle cx="41" cy="48" r="1.5" fill="#FFFFFF"/>
<circle cx="61" cy="48" r="1.5" fill="#FFFFFF"/>
<polygon points="50,58 47,55 53,55" fill="#E68B9E"/>
<path d="M 47,60 Q 50,63 53,60" fill="none" stroke="#583B43" stroke-width="1.5" stroke-linecap="round"/>
<circle cx="34" cy="56" r="4" fill="#F8B6C4" opacity="0.6"/>
<circle cx="66" cy="56" r="4" fill="#F8B6C4" opacity="0.6"/>
</svg>"""
    },
    "sloth": {
        "id": "sloth",
        "name": "慢活樹懶・悠悠",
        "species": "三趾樹懶",
        "emoji": "🦥",
        "title": "正念放鬆師",
        "badge": "🍃 接納焦慮・接納承諾療法 (ACT)",
        "is_free": False,
        "motto": "事情做不完也沒關係……慢慢來……先深呼吸一口氣吧……",
        "summary": "步調極慢、反內卷哲學大師。提醒你「停下來放鬆真的沒關係」，引導你調節呼吸與身心節奏。",
        "psychology": "【接納承諾療法 (ACT) 與正念減壓 (MBSR)】倡導心理靈活性（Psychological Flexibility）與認知解離，接納無法掌控的現狀，放慢節奏重新呼吸。",
        "default_self_ref": "悠悠",
        "favorite_snack": "berry",
        "pet_quotes": ["（慢吞吞地眨了眨眼）呼……放慢腳步……今天已經做得很好了……"],
        "theme_color": "#638367",
        "bg_color": "#F3F7F4",
        "bubble_color": "#DEE9DF",
        "actions": ["(慢吞吞地眨眨眼，陪你深深吸一口氣再緩緩吐出)"],
        "svg_avatar": """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<circle cx="50" cy="50" r="46" fill="#D3C7B5" stroke="#B8AA94" stroke-width="3"/>
<ellipse cx="50" cy="52" rx="34" ry="26" fill="#F0E8DC"/>
<path d="M 26,44 C 30,42 36,45 36,54 C 36,60 28,60 24,54 Z" fill="#8C7A65"/>
<path d="M 74,44 C 70,42 64,45 64,54 C 64,60 72,60 76,54 Z" fill="#8C7A65"/>
<ellipse cx="33" cy="52" rx="3" ry="3" fill="#3D3225"/>
<ellipse cx="67" cy="52" rx="3" ry="3" fill="#3D3225"/>
<ellipse cx="50" cy="58" rx="5" ry="4" fill="#3D3225"/>
<path d="M 44,65 Q 50,69 56,65" fill="none" stroke="#3D3225" stroke-width="2" stroke-linecap="round"/>
</svg>"""
    },
    "penguin": {
        "id": "penguin",
        "name": "呆萌企鵝・皮皮",
        "species": "國王企鵝幼鳥",
        "emoji": "🐧",
        "title": "踏實同行者",
        "badge": "❄️ 微步行動・行為活化與微習慣 (Micro-steps)",
        "is_free": False,
        "motto": "跌倒了就坐在雪地上休息一下，皮皮牽著你一步一步走。",
        "summary": "憨厚真誠、踏實同行。在你感到挫敗或迷惘時，用小碎步陪你前進，共同抵擋人生的風寒雪雨。",
        "psychology": "【行為活化 (Behavioral Activation) 與微步前進】將巨大癱瘓感拆解為極微小、無負擔的具體步伐，陪你在挫折後重新拾起對生活的掌控感。",
        "default_self_ref": "皮皮",
        "favorite_snack": "fish",
        "pet_quotes": ["（用小翅膀拍拍你）就算走得再慢，每一步都是在走向更好的自己！"],
        "theme_color": "#3F718D",
        "bg_color": "#F0F5F8",
        "bubble_color": "#D8E6EE",
        "actions": ["(用毛茸茸的小翅膀輕輕碰碰你的手背)"],
        "svg_avatar": """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<circle cx="50" cy="50" r="46" fill="#384955" stroke="#25323B" stroke-width="3"/>
<ellipse cx="50" cy="56" rx="30" ry="32" fill="#FFFFFF"/>
<ellipse cx="38" cy="44" rx="4" ry="5" fill="#25323B"/>
<ellipse cx="62" cy="44" rx="4" ry="5" fill="#25323B"/>
<circle cx="39" cy="42" r="1.5" fill="#FFFFFF"/>
<circle cx="63" cy="42" r="1.5" fill="#FFFFFF"/>
<polygon points="50,54 44,48 56,48" fill="#F39C12"/>
<circle cx="30" cy="50" r="4" fill="#FAD7A0" opacity="0.6"/>
<circle cx="70" cy="50" r="4" fill="#FAD7A0" opacity="0.6"/>
</svg>"""
    },
    "owl": {
        "id": "owl",
        "name": "睿智貓頭鷹・奧爾",
        "species": "雪鴞貓頭鷹",
        "emoji": "🦉",
        "title": "沉靜引路人",
        "badge": "💡 洞察深邃・非暴力溝通 (NVC) 與理性情緒",
        "is_free": False,
        "motto": "在迷茫的夜裡不要害怕，奧爾會為你點亮心中的清明之光。",
        "summary": "深邃沉靜、溫和透徹。在思緒混亂與黑夜中，幫你梳理出頭緒，看見情緒底層的真正渴望。",
        "psychology": "【非暴力溝通 (NVC) 與溫和理性情緒指引】穿透焦慮與憤怒表層，洞察深層未滿足的心理需求（Need），引導理性看清盲點與內在心願。",
        "default_self_ref": "奧爾",
        "favorite_snack": "berry",
        "pet_quotes": ["（推了推小眼鏡）黑夜只是暫時的，你心中早已有智慧的清明之光。"],
        "theme_color": "#52627E",
        "bg_color": "#F1F4F9",
        "bubble_color": "#DAE2ED",
        "actions": ["(推了推精緻小眼鏡，投以深邃而包容的目光)"],
        "svg_avatar": """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<circle cx="50" cy="50" r="46" fill="#8492A6" stroke="#68768A" stroke-width="3"/>
<polygon points="26,30 18,12 36,22" fill="#68768A"/>
<polygon points="74,30 82,12 64,22" fill="#68768A"/>
<circle cx="36" cy="46" r="14" fill="#FBFDFF" stroke="#D3DCE6" stroke-width="2"/>
<circle cx="64" cy="46" r="14" fill="#FBFDFF" stroke="#D3DCE6" stroke-width="2"/>
<circle cx="36" cy="46" r="7" fill="#E6A23C"/>
<circle cx="64" cy="46" r="7" fill="#E6A23C"/>
<circle cx="36" cy="46" r="3.5" fill="#2C3A4B"/>
<circle cx="64" cy="46" r="3.5" fill="#2C3A4B"/>
<circle cx="38" cy="44" r="1.5" fill="#FFFFFF"/>
<circle cx="66" cy="44" r="1.5" fill="#FFFFFF"/>
<polygon points="50,56 46,50 54,50" fill="#E6A23C"/>
<path d="M 38,68 Q 50,75 62,68" fill="none" stroke="#68768A" stroke-width="2.5" stroke-linecap="round"/>
</svg>"""
    },
    "dolphin": {
        "id": "dolphin",
        "name": "療癒海豚・露露",
        "species": "寬吻海豚",
        "emoji": "🐬",
        "title": "活力洗滌者",
        "badge": "🌊 活力洗滌・正向心理學 PERMA 與生命共振",
        "is_free": False,
        "motto": "讓心靈在蔚藍的大海中暢遊，把所有緊繃的煩惱都隨浪花洗淨吧！",
        "summary": "清新靈動、如同海洋般廣闊包容。擅長用溫柔的共振頻率洗滌疲憊，喚醒身心內在的生命活力。",
        "psychology": "【正向心理學 PERMA 模型與身心共鳴】透過海洋意象與積極情感共振（Positive Resonance），重新點燃被疲倦消磨殆盡的生命朝氣與活力。",
        "default_self_ref": "露露",
        "favorite_snack": "fish",
        "pet_quotes": ["（悠揚的海豚音～）把緊繃隨海浪洗淨吧，深呼吸，感受生命的流動！"],
        "theme_color": "#2C8D8D",
        "bg_color": "#F0F8F8",
        "bubble_color": "#D3ECEC",
        "actions": ["(發出溫柔而悠揚的治癒海豚音，撫平心中的微瀾)"],
        "svg_avatar": """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<circle cx="50" cy="50" r="46" fill="#48A9A6" stroke="#318784" stroke-width="3"/>
<path d="M 22,60 C 20,40 50,30 78,45 C 86,50 88,58 76,56 C 58,54 40,68 22,60 Z" fill="#71C7C4"/>
<path d="M 30,62 C 45,60 65,65 72,57 C 60,70 40,70 30,62 Z" fill="#E8F8F7"/>
<ellipse cx="64" cy="46" rx="3.5" ry="4" fill="#1A4A49"/>
<circle cx="65" cy="45" r="1.5" fill="#FFFFFF"/>
<path d="M 68,54 Q 74,56 78,52" fill="none" stroke="#1A4A49" stroke-width="1.5" stroke-linecap="round"/>
<circle cx="58" cy="52" r="3.5" fill="#A8E4E2" opacity="0.6"/>
</svg>"""
    },
    "hedgehog": {
        "id": "hedgehog",
        "name": "小刺蝟・刺刺",
        "species": "非洲侏儒刺蝟",
        "emoji": "🦔",
        "title": "內斂知己",
        "badge": "🌰 內在家庭系統 (IFS)・防衛保護與脆弱和解",
        "is_free": False,
        "motto": "我知道你只是想保護自己……在刺刺這裡，你可以安心放下尖刺。",
        "summary": "外剛內柔、最懂自我保護與敏感脆弱。在你感到受傷戒備時，溫柔告訴你「不需要假裝勇敢」。",
        "psychology": "【內在家庭系統療法 (IFS) 與防衛機制接納】理解尖銳防衛（Protector Part）背後受傷脆弱的本質，以全然的慈悲接納內在不同部分，溫和促成自我和解。",
        "default_self_ref": "刺刺",
        "favorite_snack": "berry",
        "pet_quotes": ["（收起背上的小刺，輕輕碰你的指尖）在刺刺面前，你不需要假裝堅強。"],
        "theme_color": "#946E56",
        "bg_color": "#F7F3EF",
        "bubble_color": "#E9DFD6",
        "actions": ["(慢慢收起背上的小刺，安靜縮成一團陪著你)"],
        "svg_avatar": """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<circle cx="50" cy="50" r="46" fill="#8C674F" stroke="#6D4D38" stroke-width="3"/>
<polygon points="18,32 10,24 24,24" fill="#6D4D38"/>
<polygon points="34,22 30,10 44,14" fill="#6D4D38"/>
<polygon points="54,18 56,6 66,16" fill="#6D4D38"/>
<polygon points="74,26 84,16 78,30" fill="#6D4D38"/>
<polygon points="82,42 94,40 84,52" fill="#6D4D38"/>
<ellipse cx="50" cy="58" rx="28" ry="24" fill="#F4EAE1"/>
<ellipse cx="40" cy="54" rx="3.5" ry="4.5" fill="#3D291C"/>
<ellipse cx="60" cy="54" rx="3.5" ry="4.5" fill="#3D291C"/>
<circle cx="41" cy="52" r="1.5" fill="#FFFFFF"/>
<circle cx="61" cy="52" r="1.5" fill="#FFFFFF"/>
<ellipse cx="50" cy="62" rx="4" ry="3" fill="#3D291C"/>
<circle cx="34" cy="60" r="4" fill="#F9C6B8" opacity="0.6"/>
<circle cx="66" cy="60" r="4" fill="#F9C6B8" opacity="0.6"/>
</svg>"""
    }
}

ANIMAL_COMPANIONS = {}
for cid, cdata in RAW_COMPANIONS.items():
    cdata_copy = dict(cdata)
    cdata_copy["avatar_uri"] = svg_to_data_uri(cdata["svg_avatar"])
    ANIMAL_COMPANIONS[cid] = cdata_copy

# 3. 初始化 SQLite 資料庫用戶與狀態
CURRENT_USER_ID = "default_sanctuary_user"
user_record = db.get_or_create_user(CURRENT_USER_ID)

if "user_data" not in st.session_state:
    st.session_state.user_data = user_record
if "selected_companion" not in st.session_state:
    st.session_state.selected_companion = "samoyed"
if "main_section" not in st.session_state:
    st.session_state.main_section = "cozy_room"
if "sub_tab" not in st.session_state:
    st.session_state.sub_tab = "zen_stones"
if "is_thinking" not in st.session_state:
    st.session_state.is_thinking = False
if "error_msg" not in st.session_state:
    st.session_state.error_msg = None
if "fortune_result" not in st.session_state:
    st.session_state.fortune_result = None
if "shredded_troubles" not in st.session_state:
    st.session_state.shredded_troubles = []
if "companion_custom_self_ref" not in st.session_state:
    st.session_state.companion_custom_self_ref = {}
if "zen_stones" not in st.session_state:
    st.session_state.zen_stones = []
if "inner_child_reflection" not in st.session_state:
    st.session_state.inner_child_reflection = None
if "mobile_preview_mode" not in st.session_state:
    st.session_state.mobile_preview_mode = False
if "feeding_event" not in st.session_state:
    st.session_state.feeding_event = None

# 載入當前動物歷史對話
if "messages" not in st.session_state:
    st.session_state.messages = db.load_chat_history(CURRENT_USER_ID, st.session_state.selected_companion)

# 4. API Key 智慧獲取
def get_api_config():
    key = None
    for k in ["GROQ_API_KEY", "OPENAI_API_KEY"]:
        if k in st.secrets and str(st.secrets[k]).strip() and "在此填入" not in str(st.secrets[k]):
            key = str(st.secrets[k]).strip()
            break
    if not key:
        key = os.environ.get("GROQ_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key and "user_api_key" in st.session_state and st.session_state.user_api_key:
        key = st.session_state.user_api_key.strip()
    
    if not key:
        return None, None, None
    
    if key.startswith("gsk_"):
        return key, "https://api.groq.com/openai/v1/", "llama-3.3-70b-versatile"
    elif key.startswith("sk-"):
        return key, "https://api.openai.com/v1", "gpt-4o-mini"
    else:
        return key, "https://api.groq.com/openai/v1/", "llama-3.3-70b-versatile"

api_key, api_base_url, api_model = get_api_config()

# 5. PWA 原生 App 標籤與全域現代化奢華暖調 CSS
st.markdown("""
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="動物心靈小屋">
<meta name="mobile-web-app-capable" content="yes">
<meta name="application-name" content="動物心靈小屋">
<meta name="theme-color" content="#F8F4ED">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<link rel="manifest" href='data:application/manifest+json,{"name":"動物心靈小屋","short_name":"心靈小屋","start_url":".","display":"standalone","background_color":"#F8F4ED","theme_color":"#F8F4ED"}'>
""", unsafe_allow_html=True)

if st.session_state.mobile_preview_mode:
    st.markdown("""
<style>
.main .block-container {
    max-width: 440px !important;
    margin: 20px auto !important;
    padding: 20px 14px 40px !important;
    border-radius: 46px !important;
    border: 10px solid #2B2520 !important;
    box-shadow: 0 25px 60px rgba(0,0,0,0.35), 0 0 0 2px rgba(255,255,255,0.15) inset !important;
    background: #F8F4ED !important;
}
</style>
""", unsafe_allow_html=True)
else:
    st.markdown("""
<style>
.main .block-container {
    max-width: 960px !important;
    padding-top: 1.5rem !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700&family=Quicksand:wght@500;600;700&display=swap');

:root {
    --primary-cream: #F8F4ED;
    --card-bg: rgba(255, 255, 255, 0.88);
    --border-warm: #EADBCE;
    --accent-gold: #C2995F;
    --text-main: #4A3B2C;
    --text-muted: #8C735A;
}

.stApp {
    background-color: var(--primary-cream);
    background-image: 
        radial-gradient(circle at 10% 15%, rgba(194, 153, 95, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 90% 85%, rgba(124, 106, 141, 0.08) 0%, transparent 45%);
    font-family: 'Noto Sans TC', 'Quicksand', sans-serif;
    color: var(--text-main);
}

#stMainMenu, footer, header[data-testid="stHeader"], div[data-testid="stDecoration"], div[data-testid="stStatusWidget"], div[data-testid="stToolbar"], .viewerBadge_container__1QSob, [data-testid="manage-app-button"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
}
section[data-testid="stSidebar"] { display: none !important; }

@media (max-width: 768px) {
    .main .block-container {
        padding: 0.8rem 0.5rem 2rem !important;
    }
    .brand-header {
        padding: 0.5rem 0.8rem !important;
        border-radius: 16px !important;
    }
    .brand-logo-title {
        font-size: 1.1rem !important;
    }
    .status-pill {
        font-size: 0.72rem !important;
        padding: 2px 8px !important;
    }
}

/* 頂部 Header */
.brand-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(16px);
    border: 1.5px solid var(--border-warm);
    border-radius: 22px;
    padding: 0.7rem 1.3rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 20px rgba(83, 62, 45, 0.04);
}
.brand-logo-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #533E2D;
    display: flex;
    align-items: center;
    gap: 8px;
}
.brand-status-pills {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
}
.status-pill {
    background: #FAF5EE;
    border: 1px solid #E5D5C5;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    color: #6E5642;
    display: flex;
    align-items: center;
    gap: 5px;
}

/* 動物卡片 */
.companion-card {
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border-radius: 22px;
    padding: 1.3rem 1.1rem;
    border: 1.5px solid var(--border-warm);
    box-shadow: 0 8px 24px rgba(83, 62, 45, 0.05);
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    text-align: center;
    position: relative;
}
.companion-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 14px 32px rgba(83, 62, 45, 0.12);
    border-color: var(--accent-gold);
}
.companion-avatar-wrap {
    width: 86px;
    height: 86px;
    margin: 0 auto 0.8rem;
    border-radius: 50%;
    background: #FDFBF7;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 3px solid #EDE0CE;
    box-shadow: 0 4px 14px rgba(83, 62, 45, 0.08);
}
.companion-avatar-img {
    width: 76px;
    height: 76px;
    border-radius: 50%;
}
.companion-name {
    font-size: 1.18rem;
    font-weight: 700;
    color: #4A3B2C;
    margin-bottom: 0.3rem;
}
.companion-badge {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    color: #8C6F4F;
    background: #F6EEE3;
    padding: 0.25rem 0.65rem;
    border-radius: 12px;
    margin-bottom: 0.6rem;
    line-height: 1.3;
}
.companion-motto {
    font-size: 0.82rem;
    color: #7D6B58;
    font-style: italic;
    line-height: 1.45;
    margin-bottom: 0.7rem;
    background: #FAF6F0;
    padding: 0.5rem 0.7rem;
    border-radius: 10px;
    border-left: 3px solid var(--accent-gold);
    text-align: left;
}
.companion-desc {
    font-size: 0.8rem;
    color: #6E5C49;
    line-height: 1.55;
    margin-bottom: 0.8rem;
    text-align: left;
}

/* 諮商室專用氣泡 */
.chat-stream-box {
    max-width: 860px;
    margin: 0 auto 1.5rem;
}
.msg-row {
    display: flex;
    margin: 1rem 0;
    animation: msg-fade-in 0.35s ease-out;
}
.msg-row.bot { justify-content: flex-start; }
.msg-row.user { justify-content: flex-end; }

@keyframes msg-fade-in {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.msg-avatar {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    margin: 0 0.6rem;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #EDE0CE;
    border: 2px solid #E2D5C3;
    box-shadow: 0 3px 10px rgba(83, 62, 45, 0.08);
}
.msg-avatar-img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
}
.msg-row.user .msg-avatar { order: 1; background: #FFF9F2; border-color: #E8D8C8; }

.msg-bubble {
    max-width: 76%;
    padding: 1rem 1.3rem;
    border-radius: 22px;
    font-size: 0.98rem;
    line-height: 1.8;
    box-shadow: 0 4px 14px rgba(83, 62, 45, 0.05);
    word-break: break-word;
}
.msg-row.bot .msg-bubble {
    background: #FFFFFF;
    color: #4A3B2C;
    border-radius: 22px 22px 22px 6px;
    border: 1.5px solid #E8DCCE;
}
.msg-row.user .msg-bubble {
    background: linear-gradient(135deg, #FAF4EB 0%, #F1E5D5 100%);
    color: #4A3B2C;
    border-radius: 22px 22px 6px 22px;
    border: 1.5px solid #DFC9B4;
}

.stButton > button {
    background-color: #EDE1D1 !important;
    color: #533E2D !important;
    border: 1.5px solid #D5C2AF !important;
    border-radius: 18px !important;
    font-family: 'Noto Sans TC', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.4rem 1.1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 6px rgba(83, 62, 45, 0.06) !important;
}
.stButton > button:hover {
    background-color: #E2D2BE !important;
    border-color: var(--accent-gold) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(83, 62, 45, 0.12) !important;
}

[data-testid="stChatInput"] {
    border-color: #D5C2AF !important;
    border-radius: 26px !important;
    background-color: #FFFFFF !important;
}
[data-testid="stChatInputTextArea"] {
    font-family: 'Noto Sans TC', sans-serif !important;
    color: #4A3B2C !important;
}
[data-testid="stChatInputButton"] {
    background-color: var(--accent-gold) !important;
    color: white !important;
    border-radius: 50% !important;
}
</style>
""", unsafe_allow_html=True)

# 6. 頂部品牌 Header 與留存儀表板
active_comp = ANIMAL_COMPANIONS[st.session_state.selected_companion]
affinity_info = db.get_companion_affinity(CURRENT_USER_ID, active_comp["id"])
current_user = db.get_or_create_user(CURRENT_USER_ID)
free_quota_left = max(0, 10 - current_user.get("daily_chat_count", 0))

st.markdown(f"""
<div class="brand-header">
    <div class="brand-logo-title">
        🐾 動物心靈諮商室 <span style="font-size:0.75rem; background:#EFE3D3; color:#7D6348; padding:2px 8px; border-radius:12px; font-weight:600;">3D 擬真手遊版</span>
    </div>
    <div class="brand-status-pills">
        <div class="status-pill">🌟 星光幣 <strong>{current_user.get('star_coins', 888)}</strong></div>
        <div class="status-pill">🔥 連續守護 <strong>{current_user.get('streak_days', 1)}</strong> 天</div>
        <div class="status-pill">💖 {active_comp['emoji']} 親密度 <strong>Lv.{affinity_info.get('level', 1)}</strong> ({affinity_info.get('exp', 0)}/{affinity_info.get('next_level_exp', 100)})</div>
        <div class="status-pill">💬 今日對話：<strong>{'無限制 👑' if current_user.get('is_vip', 1) else f'{free_quota_left}/10次'}</strong></div>
        <div class="status-pill">👑 {'VIP會員 (開發解鎖)' if current_user.get('is_vip', 1) else '免費版'}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 7. 手機 App 測試安裝指南 & 手機視窗模擬控制列
col_top_app1, col_top_app2 = st.columns([3, 1])
with col_top_app1:
    with st.expander("📲 點此查看【手機 App 測試安裝指南 (iOS / Android 零下載一鍵變 App)】", expanded=False):
        st.markdown("""
<div style="background:#FAF6F0; border-radius:14px; padding:1rem; border:1px solid #EADECE; font-size:0.85rem; color:#5C4A38; line-height:1.7;">
    <h4 style="color:#533E2D; margin:0 0 0.5rem;">🍎 iPhone / iPad 使用者（Safari 原生 PWA 全螢幕）：</h4>
    <ol style="margin-bottom:0.8rem; padding-left:1.2rem;">
        <li>使用 Safari 瀏覽器打開本頁網址。</li>
        <li>點擊底部中央的「<strong>分享</strong>」按鈕（帶往上箭頭的方框圖示）。</li>
        <li>滑動找到並點擊「<strong>加入主畫面 (Add to Home Screen)</strong>」。</li>
        <li>點擊右上角「新增」—— 手機桌面上立刻生成「🐾 動物心靈小屋」App！點開即可享受 <strong>無網址列、無瀏覽器外框的 100% 全螢幕手遊沉浸體驗</strong>！</li>
    </ol>
    <h4 style="color:#533E2D; margin:0 0 0.5rem;">🤖 Android 安卓使用者（Chrome / Edge）：</h4>
    <ol style="margin:0; padding-left:1.2rem;">
        <li>使用 Chrome 瀏覽器打開本頁網址。</li>
        <li>點擊右上角「<strong>三個點選單</strong>」。</li>
        <li>點擊「<strong>安裝應用程式 (Install App)</strong>」或「<strong>加到主螢幕</strong>」。</li>
        <li>桌面生成專屬 App 圖示，即刻享受手遊般的無縫操作！</li>
    </ol>
</div>
""", unsafe_allow_html=True)

with col_top_app2:
    btn_preview_label = "🖥️ 切換電腦寬屏" if st.session_state.mobile_preview_mode else "📱 模擬手機視窗"
    if st.button(btn_preview_label, key="toggle_mobile_preview", use_container_width=True):
        st.session_state.mobile_preview_mode = not st.session_state.mobile_preview_mode
        st.rerun()

# 8. API Key 檢查
if not api_key:
    with st.expander("🔑 尚未設定 API Key（支援 Groq 或 OpenAI Key）", expanded=True):
        st.info("💡 提示：本應用支援 **Groq API Key**（免費高速，以 `gsk_` 開頭）或 **OpenAI API Key**（以 `sk-` 開頭）。如果您之前已經有 Key，直接貼上即可使用！")
        input_key = st.text_input("輸入您的 API Key (Groq 或 OpenAI):", type="password", placeholder="貼上 gsk_... 或 sk-...", key="temp_api_key_input")
        if st.button("確認並啟用", key="btn_save_key"):
            if input_key.strip():
                st.session_state.user_api_key = input_key.strip()
                st.success("API Key 已儲存！")
                st.rerun()
            else:
                st.warning("請先輸入有效的 API Key 喔！")


owned_decor = db.get_user_decor_items(CURRENT_USER_ID)

# 裝飾徽章列
equipped_badges = []
for item in db.DEFAULT_DECOR_ITEMS:
    if owned_decor.get(item["id"], False):
        equipped_badges.append(f"{item['icon']} {item['name'].split(' ')[1]}")

decor_html = "".join([f'<div style="background:rgba(255,255,255,0.9); border:1px solid #E0CEBB; padding:4px 12px; border-radius:16px; font-size:0.8rem; color:#5C4A38; font-weight:600;">{b}</div>' for b in equipped_badges])
if not decor_html:
    decor_html = '<div style="background:rgba(255,255,255,0.8); padding:4px 12px; border-radius:16px; font-size:0.8rem; color:#8C735A;">🪹 小屋剛建立，快去星光小舖挑選家具吧！</div>'

# 3D 擬真寬敞微縮心靈小屋與漫步巡邏神獸引擎 (Three.js 3D Spacious Sanctuary Roaming Engine)
pet_quotes_js = json.dumps(active_comp["pet_quotes"], ensure_ascii=False)
comp_id_val = active_comp["id"]
equipped_decor_js = json.dumps(owned_decor, ensure_ascii=False)
feeding_event_js = json.dumps(st.session_state.feeding_event, ensure_ascii=False)
st.session_state.feeding_event = None

live_pet_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@500;600;700&family=Quicksand:wght@600;700&display=swap');
* {{ box-sizing: border-box; margin: 0; padding: 0; user-select: none; }}
body {{
    background: transparent;
    font-family: 'Noto Sans TC', 'Quicksand', sans-serif;
    color: #4A3B2C;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2px;
}}
.stage-card {{
    background: linear-gradient(180deg, #F3ECE2 0%, #DFD1BE 100%);
    border: 2.5px solid #C4B097;
    border-radius: 28px;
    padding: 1.1rem 1rem 0.9rem;
    box-shadow: 0 16px 40px rgba(83,62,45,0.14), inset 0 2px 4px rgba(255,255,255,0.8);
    max-width: 880px;
    width: 100%;
    text-align: center;
    position: relative;
    overflow: hidden;
}}
.speech-bubble {{
    background: rgba(255, 255, 255, 0.96);
    border: 1.5px solid #D8C6B0;
    border-radius: 20px;
    padding: 0.75rem 1.3rem;
    font-size: 0.92rem;
    color: #4B3726;
    line-height: 1.6;
    max-width: 560px;
    margin: 0 auto 0.6rem;
    box-shadow: 0 6px 20px rgba(83,62,45,0.08);
    position: relative;
    animation: bubble-fade 0.3s ease;
}}
.speech-bubble::after {{
    content: '';
    position: absolute;
    bottom: -9px;
    left: 50%;
    transform: translateX(-50%);
    border-width: 9px 9px 0;
    border-style: solid;
    border-color: rgba(255,255,255,0.96) transparent;
    display: block;
    width: 0;
}}
#three-canvas-container {{
    width: 100%;
    height: 400px;
    margin: 0 auto;
    position: relative;
    cursor: grab;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.06);
}}
#three-canvas-container:active {{
    cursor: grabbing;
}}
.interaction-bar {{
    display: flex;
    gap: 10px;
    justify-content: center;
    align-items: center;
    margin-top: 0.6rem;
    flex-wrap: wrap;
}}
.pet-touch-btn {{
    background: #B68648;
    color: white;
    border: none;
    padding: 8px 20px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85rem;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(182,134,72,0.28);
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 4px;
}}
.pet-touch-btn:hover {{
    background: #9D7037;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(182,134,72,0.38);
}}
.hint-text {{
    font-size: 0.78rem;
    color: #725C47;
    font-weight: 600;
    margin-top: 0.4rem;
}}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
<div class="stage-card">
<div style="font-size:0.86rem; color:#6B533E; font-weight:700; margin-bottom:0.35rem; display:flex; align-items:center; justify-content:center; gap:6px;">
    <span>🏡</span> {current_user.get('nickname', '小夥伴')} 與 {active_comp['name']} 的 3D 北歐森林心靈小屋
</div>
<div class="speech-bubble" id="pet-speech">
    「{active_comp['motto']}」
</div>
<div id="three-canvas-container"></div>
<div class="interaction-bar">
    <button class="pet-touch-btn" onclick="handlePetDirect()">💖 摸摸撫慰 (瞇眼撒嬌)</button>
    <button class="pet-touch-btn" style="background:#5F8A6B;" onclick="triggerPetWalk()">🐾 走動巡邏</button>
    <button class="pet-touch-btn" style="background:#82659B;" onclick="triggerPetStretch()">🐕 伸懶腰</button>
    <button class="pet-touch-btn" style="background:#4A8B82;" onclick="triggerPetShake()">🌀 甩毛抖擻</button>
    <button class="pet-touch-btn" style="background:#8D7358;" onclick="triggerPetSit()">🧘 乖巧坐下</button>
    <button class="pet-touch-btn" style="background:#C2995F;" onclick="triggerFeedingAnimation('milk', '溫暖熱牛奶')">🥛 餵牛奶</button>
    <button class="pet-touch-btn" style="background:#A35843;" onclick="triggerFeedingAnimation('jerky', '香脆肉乾')">🥩 餵肉乾</button>
    <button class="pet-touch-btn" style="background:#8C6B53;" onclick="triggerFeedingAnimation('cookie', '心靈小餅乾')">🍪 餵餅乾</button>
</div>
<div class="hint-text">✨ 點擊地板引導小薩走過去・360° 拖曳旋轉小屋・真實光影與超萌吐舌漫步動畫</div>
</div>

<script>
const quotes = {pet_quotes_js};
const compId = "{comp_id_val}";
const equippedDecor = {equipped_decor_js};
let audioCtx = null;

function getAudioCtx() {{
    if (!audioCtx) {{
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }}
    if (audioCtx.state === 'suspended') {{
        audioCtx.resume();
    }}
    return audioCtx;
}}

function playChimeSound() {{
    try {{
        const ctx = getAudioCtx();
        const now = ctx.currentTime;
        [523.25, 659.25, 783.99, 1046.50].forEach((freq, idx) => {{
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(freq, now + idx * 0.08);
            gain.gain.setValueAtTime(0.2, now + idx * 0.08);
            gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.08 + 0.35);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(now + idx * 0.08);
            osc.stop(now + idx * 0.08 + 0.35);
        }});
    }} catch(e) {{}}
}}

function playEatingSound() {{
    try {{
        const ctx = getAudioCtx();
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(450 + Math.random()*200, now);
        osc.frequency.exponentialRampToValueAtTime(140, now + 0.07);
        gain.gain.setValueAtTime(0.35, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.07);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.07);
    }} catch(e) {{}}
}}

// ==========================================
// 🌟 1. Three.js 電影級光影場景初始化 (Three.js Soft Lighting Setup)
// ==========================================
const container = document.getElementById('three-canvas-container');
const width = container.clientWidth || 700;
const height = 400;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xEFE6D8);

const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100);
camera.position.set(4.5, 4.6, 7.8);
camera.lookAt(0, 0.7, 0);

const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
renderer.setSize(width, height);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;
container.appendChild(renderer.domElement);

// 主太陽斜射光 (Sunbeam Key Light with Soft Shadows)
const sunLight = new THREE.DirectionalLight(0xFFF4E0, 1.4);
sunLight.position.set(5.5, 9.0, 5.0);
sunLight.castShadow = true;
sunLight.shadow.mapSize.width = 1024;
sunLight.shadow.mapSize.height = 1024;
sunLight.shadow.camera.near = 0.5;
sunLight.shadow.camera.far = 25;
sunLight.shadow.camera.left = -5;
sunLight.shadow.camera.right = 5;
sunLight.shadow.camera.top = 5;
sunLight.shadow.camera.bottom = -5;
sunLight.shadow.bias = -0.001;
scene.add(sunLight);

// 半球天空環境光 (Sky / Ground Fill Light)
const hemiLight = new THREE.HemisphereLight(0xF4F9FC, 0xDAC4AE, 0.85);
hemiLight.position.set(0, 10, 0);
scene.add(hemiLight);

// 柔和前側補光 (Soft Front Fill)
const fillLight = new THREE.DirectionalLight(0xFFE8D1, 0.45);
fillLight.position.set(-4, 3, 5);
scene.add(fillLight);

const roomRoot = new THREE.Group();
scene.add(roomRoot);

// ==========================================
// 🏡 2. 精緻北歐風溫馨微縮心靈小屋 (Handcrafted Nordic Sanctuary Room)
// ==========================================
const roomSize = 7.6;
const wallHeight = 4.2;

// 胡桃木拼接木質地板
const floorGeo = new THREE.BoxGeometry(roomSize, 0.25, roomSize);
const floorMat = new THREE.MeshStandardMaterial({{
    color: 0x8C5E3B,
    roughness: 0.55,
    metalness: 0.05
}});
const roomFloor = new THREE.Mesh(floorGeo, floorMat);
roomFloor.position.y = -0.125;
roomFloor.receiveShadow = true;
roomRoot.add(roomFloor);

// 森林綠優雅背牆 (Back Wall)
const wallMat = new THREE.MeshStandardMaterial({{
    color: 0x6E8A73, // 質感鼠尾草森林綠
    roughness: 0.85,
    metalness: 0.02
}});
const backWall = new THREE.Mesh(new THREE.BoxGeometry(roomSize, wallHeight, 0.25), wallMat);
backWall.position.set(0, wallHeight / 2, -roomSize / 2 - 0.125);
backWall.receiveShadow = true;
roomRoot.add(backWall);

// 左側牆 (Left Wall)
const leftWall = new THREE.Mesh(new THREE.BoxGeometry(0.25, wallHeight, roomSize), wallMat);
leftWall.position.set(-roomSize / 2 - 0.125, wallHeight / 2, 0);
leftWall.receiveShadow = true;
roomRoot.add(leftWall);

// 踢腳線 (Wood Baseboard Trimming)
const trimMat = new THREE.MeshStandardMaterial({{ color: 0x483526, roughness: 0.6 }});
const trimBack = new THREE.Mesh(new THREE.BoxGeometry(roomSize, 0.2, 0.1), trimMat);
trimBack.position.set(0, 0.1, -roomSize / 2 + 0.05);
roomRoot.add(trimBack);
const trimLeft = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.2, roomSize), trimMat);
trimLeft.position.set(-roomSize / 2 + 0.05, 0.1, 0);
roomRoot.add(trimLeft);

// 圓形波西米亞流蘇絨毛地毯 (Fluffy Bohemian Rug)
const rugGeo = new THREE.CylinderGeometry(2.3, 2.3, 0.04, 32);
const rugMat = new THREE.MeshStandardMaterial({{
    color: 0xF7EFE5,
    roughness: 0.95
}});
const rug = new THREE.Mesh(rugGeo, rugMat);
rug.position.set(0, 0.02, 0.2);
rug.receiveShadow = true;
roomRoot.add(rug);

// 地毯內圈溫暖印花
const innerRugGeo = new THREE.CylinderGeometry(1.7, 1.7, 0.045, 32);
const innerRugMat = new THREE.MeshStandardMaterial({{ color: 0xE8D5C2, roughness: 0.9 }});
const innerRug = new THREE.Mesh(innerRugGeo, innerRugMat);
innerRug.position.set(0, 0.025, 0.2);
innerRug.receiveShadow = true;
roomRoot.add(innerRug);

// 🪟 景觀落地窗與戶外藍天青山 (Panoramic Window with Scenic View)
const windowFrameGeo = new THREE.BoxGeometry(2.6, 2.6, 0.15);
const windowFrameMat = new THREE.MeshStandardMaterial({{ color: 0xFAF6EE, roughness: 0.4 }});
const windowFrame = new THREE.Mesh(windowFrameGeo, windowFrameMat);
windowFrame.position.set(0.6, 2.4, -roomSize / 2 + 0.02);
roomRoot.add(windowFrame);

// 窗外藍天遠山
const skyCanvas = new THREE.Mesh(new THREE.PlaneGeometry(2.35, 2.35), new THREE.MeshBasicMaterial({{ color: 0x9BD0EC }}));
skyCanvas.position.set(0.6, 2.4, -roomSize / 2 + 0.08);
roomRoot.add(skyCanvas);

// 遠處山丘
const hillGeo = new THREE.CircleGeometry(1.2, 20);
const hillMat = new THREE.MeshBasicMaterial({{ color: 0x6DAA7A }});
const hill = new THREE.Mesh(hillGeo, hillMat);
hill.position.set(0.2, 1.8, -roomSize / 2 + 0.09);
roomRoot.add(hill);

// 窗框十字分隔
const crossV = new THREE.Mesh(new THREE.BoxGeometry(0.08, 2.4, 0.08), windowFrameMat);
crossV.position.set(0.6, 2.4, -roomSize / 2 + 0.1);
roomRoot.add(crossV);
const crossH = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.08, 0.08), windowFrameMat);
crossH.position.set(0.6, 2.4, -roomSize / 2 + 0.1);
roomRoot.add(crossH);

// ☀️ 窗戶傾瀉光斑
const windowLight = new THREE.SpotLight(0xFFF3D6, 0.9, 12, Math.PI / 4, 0.4);
windowLight.position.set(0.6, 3.5, -roomSize / 2 + 0.2);
windowLight.target.position.set(0.6, 0, 1.0);
scene.add(windowLight);
scene.add(windowLight.target);

// ==========================================
// 🛋️ 3. 精緻 3D 家具交互佈置 (Interactive 3D Furniture Items)
// ==========================================
let fireplaceFlame = null;
let fireplaceLight = null;
let vinylDisc = null;
let candleFlame = null;

// (1) 歐式暖冬壁爐 (Fireplace)
if (equippedDecor["fireplace"]) {{
    const fpGroup = new THREE.Group();
    fpGroup.position.set(-roomSize / 2 + 0.7, 0, -1.8);
    fpGroup.rotation.y = Math.PI / 2;

    const fpBase = new THREE.Mesh(new THREE.BoxGeometry(1.8, 1.5, 0.8), new THREE.MeshStandardMaterial({{ color: 0xD8C8B6, roughness: 0.8 }}));
    fpBase.position.y = 0.75;
    fpBase.castShadow = true;
    fpBase.receiveShadow = true;
    fpGroup.add(fpBase);

    const hearth = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.8, 0.5), new THREE.MeshStandardMaterial({{ color: 0x221B15, roughness: 0.9 }}));
    hearth.position.set(0, 0.5, 0.2);
    fpGroup.add(hearth);

    // 燃燒柴火
    for(let i=0; i<3; i++) {{
        const log = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.6, 8), new THREE.MeshStandardMaterial({{ color: 0x4A2E1B, roughness: 0.9 }}));
        log.rotation.z = Math.PI/3 * (i - 1);
        log.rotation.x = Math.PI/2;
        log.position.set((i-1)*0.12, 0.2, 0.2);
        fpGroup.add(log);
    }}

    // 跳動火焰
    const flameGeo = new THREE.ConeGeometry(0.24, 0.55, 8);
    const flameMat = new THREE.MeshBasicMaterial({{ color: 0xFF5722 }});
    fireplaceFlame = new THREE.Mesh(flameGeo, flameMat);
    fireplaceFlame.position.set(0, 0.45, 0.2);
    fpGroup.add(fireplaceFlame);

    fireplaceLight = new THREE.PointLight(0xFF8D36, 1.3, 5);
    fireplaceLight.position.set(0, 0.5, 0.3);
    fpGroup.add(fireplaceLight);

    roomRoot.add(fpGroup);
}}

// (2) 雲朵懶骨頭沙發與愛心抱枕 (Cloud Sofa & Heart Pillow)
if (equippedDecor["cushion"]) {{
    const sofaGroup = new THREE.Group();
    sofaGroup.position.set(1.9, 0, -1.9);
    sofaGroup.rotation.y = -Math.PI / 5;

    const sofaMat = new THREE.MeshStandardMaterial({{ color: 0xEAD9C8, roughness: 0.85 }});
    const seat = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.45, 0.9), sofaMat);
    seat.position.y = 0.25;
    seat.castShadow = true;
    sofaGroup.add(seat);

    const backrest = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.7, 0.35), sofaMat);
    backrest.position.set(0, 0.65, -0.32);
    backrest.castShadow = true;
    sofaGroup.add(backrest);

    // 粉紅愛心抱枕
    const pillow = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.35, 0.18), new THREE.MeshStandardMaterial({{ color: 0xE4AFBD, roughness: 0.6 }}));
    pillow.position.set(0.45, 0.55, -0.15);
    pillow.rotation.z = -0.2;
    pillow.rotation.y = 0.15;
    sofaGroup.add(pillow);

    roomRoot.add(sofaGroup);
}}

// (3) 淨化心靈龜背芋盆栽 (Monstera Plant)
if (equippedDecor["plant"]) {{
    const plantGroup = new THREE.Group();
    plantGroup.position.set(-roomSize / 2 + 0.8, 0, 1.8);

    const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.25, 0.7, 16), new THREE.MeshStandardMaterial({{ color: 0xFDFBF7, roughness: 0.3 }}));
    pot.position.y = 0.35;
    pot.castShadow = true;
    plantGroup.add(pot);

    // 綠葉
    const leafMat = new THREE.MeshStandardMaterial({{ color: 0x3E7D50, roughness: 0.5, side: THREE.DoubleSide }});
    for (let i = 0; i < 5; i++) {{
        const leaf = new THREE.Mesh(new THREE.SphereGeometry(0.35, 8, 8), leafMat);
        leaf.scale.set(1.0, 0.08, 1.6);
        const ang = (i / 5) * Math.PI * 2;
        leaf.position.set(Math.cos(ang) * 0.35, 0.8 + (i % 2) * 0.18, Math.sin(ang) * 0.35);
        leaf.rotation.x = Math.sin(ang) * 0.45;
        leaf.rotation.z = -Math.cos(ang) * 0.45;
        leaf.castShadow = true;
        plantGroup.add(leaf);
    }}
    roomRoot.add(plantGroup);
}}

// (4) 復古留聲機 (Vintage Gramophone)
if (equippedDecor["gramophone"]) {{
    const gramoGroup = new THREE.Group();
    gramoGroup.position.set(2.4, 0, 1.2);
    gramoGroup.rotation.y = -Math.PI / 1.5;

    const table = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.45, 0.65, 16), new THREE.MeshStandardMaterial({{ color: 0x543A26, roughness: 0.7 }}));
    table.position.y = 0.325;
    table.castShadow = true;
    gramoGroup.add(table);

    const box = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.14, 0.45), new THREE.MeshStandardMaterial({{ color: 0x8C5832, roughness: 0.6 }}));
    box.position.y = 0.72;
    gramoGroup.add(box);

    const discGeo = new THREE.CylinderGeometry(0.18, 0.18, 0.02, 16);
    const discMat = new THREE.MeshStandardMaterial({{ color: 0x1A1A1A, roughness: 0.2, metalness: 0.8 }});
    vinylDisc = new THREE.Mesh(discGeo, discMat);
    vinylDisc.position.set(0, 0.8, 0);
    gramoGroup.add(vinylDisc);

    const hornGeo = new THREE.ConeGeometry(0.24, 0.5, 16, 1, true);
    const hornMat = new THREE.MeshStandardMaterial({{ color: 0xD4AF37, roughness: 0.2, metalness: 0.85, side: THREE.DoubleSide }});
    const horn = new THREE.Mesh(hornGeo, hornMat);
    horn.rotation.x = Math.PI / 2.6;
    horn.position.set(0, 1.05, 0.15);
    gramoGroup.add(horn);

    roomRoot.add(gramoGroup);
}}

// (5) 香氛蠟燭 (Aromatherapy Candle)
if (equippedDecor["candle"]) {{
    const candleGroup = new THREE.Group();
    candleGroup.position.set(-1.8, 0, 2.0);

    const stool = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.32, 0.45, 16), new THREE.MeshStandardMaterial({{ color: 0x6E4D34, roughness: 0.8 }}));
    stool.position.y = 0.225;
    stool.castShadow = true;
    candleGroup.add(stool);

    const cBody = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.22, 16), new THREE.MeshStandardMaterial({{ color: 0xF7F0E6, roughness: 0.4 }}));
    cBody.position.y = 0.56;
    candleGroup.add(cBody);

    const cFlame = new THREE.Mesh(new THREE.ConeGeometry(0.04, 0.1, 8), new THREE.MeshBasicMaterial({{ color: 0xFFA726 }}));
    cFlame.position.y = 0.72;
    candleFlame = cFlame;
    candleGroup.add(cFlame);

    const candleLight = new THREE.PointLight(0xFFA726, 0.6, 2.5);
    candleLight.position.set(0, 0.75, 0);
    candleGroup.add(candleLight);

    roomRoot.add(candleGroup);
}}

// ==========================================
// 🐕 4. 超萌 3D 薩摩耶與神獸精緻建模 (High-Detail Ultra-Cute Pet Mesh)
// ==========================================
const petRoot = new THREE.Group();
roomRoot.add(petRoot);
petRoot.position.set(0, 0, 0.2);

// 主體毛色與材質 (Fluffy Cream Shaders)
let petPrimaryColor = 0xFFFFFF; // 薩摩耶雪白
let petSecondaryColor = 0xFCE8D5; // 臉頰與肚皮粉白
let isBear = (compId === 'bear');
let isFox = (compId === 'fox');
let isCat = (compId === 'cat');
let isBunny = (compId === 'bunny');

if (isBear) {{
    petPrimaryColor = 0x8B5A33;
    petSecondaryColor = 0xD9B48F;
}} else if (isFox) {{
    petPrimaryColor = 0xD35400;
    petSecondaryColor = 0xFAF0E6;
}} else if (isCat) {{
    petPrimaryColor = 0x95A5A6;
    petSecondaryColor = 0xFAFAFA;
}} else if (isBunny) {{
    petPrimaryColor = 0xFADBD8;
    petSecondaryColor = 0xFFFFFF;
}}

const petFurMat = new THREE.MeshStandardMaterial({{
    color: petPrimaryColor,
    roughness: 0.88,
    metalness: 0.02
}});

const petBellyMat = new THREE.MeshStandardMaterial({{
    color: petSecondaryColor,
    roughness: 0.9
}});

const pinkInnerMat = new THREE.MeshStandardMaterial({{
    color: 0xF4AAB9, // 粉嫩內耳與肉球
    roughness: 0.6
}});

// 身體 (Chubby Fluffy Pear Body)
const bodyGeo = new THREE.SphereGeometry(0.58, 20, 20);
bodyGeo.scale(1.0, 0.95, 1.25);
const body = new THREE.Mesh(bodyGeo, petFurMat);
body.position.y = 0.55;
body.castShadow = true;
body.receiveShadow = true;
petRoot.add(body);

// 蓬鬆胸前毛領圍脖 (Fluffy Mane Ruff)
const maneGeo = new THREE.SphereGeometry(0.48, 16, 16);
maneGeo.scale(1.2, 0.9, 0.9);
const mane = new THREE.Mesh(maneGeo, petFurMat);
mane.position.set(0, 0.72, 0.35);
mane.castShadow = true;
petRoot.add(mane);

// 圓肚皮粉嫩點綴
const bellyGeo = new THREE.SphereGeometry(0.48, 16, 16);
bellyGeo.scale(0.85, 0.75, 0.9);
const belly = new THREE.Mesh(bellyGeo, petBellyMat);
belly.position.set(0, 0.45, 0.15);
petRoot.add(belly);

// 頭部骨架群組 (Head Group with Fluffy Cheeks & Smile)
const headGroup = new THREE.Group();
headGroup.position.set(0, 0.98, 0.58);
petRoot.add(headGroup);

// 圓圓頭顱
const headGeo = new THREE.SphereGeometry(0.52, 20, 20);
headGeo.scale(1.05, 0.95, 1.0);
const head = new THREE.Mesh(headGeo, petFurMat);
head.castShadow = true;
head.receiveShadow = true;
headGroup.add(head);

// 兩側毛茸茸臉頰 (Fluffy Cheek Tufts)
const cheekL = new THREE.Mesh(new THREE.SphereGeometry(0.24, 12, 12), petFurMat);
cheekL.scale.set(1.1, 0.8, 0.8);
cheekL.position.set(-0.38, -0.08, 0.12);
headGroup.add(cheekL);

const cheekR = new THREE.Mesh(new THREE.SphereGeometry(0.24, 12, 12), petFurMat);
cheekR.scale.set(1.1, 0.8, 0.8);
cheekR.position.set(0.38, -0.08, 0.12);
headGroup.add(cheekR);

// 口鼻部 (Muzzle & Samoyed Smile)
const muzzleGeo = new THREE.SphereGeometry(0.28, 16, 16);
muzzleGeo.scale(0.95, 0.75, 1.15);
const muzzle = new THREE.Mesh(muzzleGeo, petBellyMat);
muzzle.position.set(0, -0.1, 0.36);
muzzle.castShadow = true;
headGroup.add(muzzle);

// 濕潤黑鼻頭 (Glossy Black Nose)
const noseGeo = new THREE.SphereGeometry(0.075, 12, 12);
noseGeo.scale(1.2, 0.9, 0.9);
const noseMat = new THREE.MeshStandardMaterial({{ color: 0x1A1412, roughness: 0.2, metalness: 0.3 }});
const nose = new THREE.Mesh(noseGeo, noseMat);
nose.position.set(0, 0.02, 0.65);
headGroup.add(nose);

// 招牌微笑粉紅小舌頭 (Panting Pink Tongue)
const tongueGeo = new THREE.BoxGeometry(0.12, 0.04, 0.18);
const tongueMat = new THREE.MeshStandardMaterial({{ color: 0xFF6B8B, roughness: 0.4 }});
const tongue = new THREE.Mesh(tongueGeo, tongueMat);
tongue.position.set(0, -0.18, 0.52);
tongue.rotation.x = 0.25;
headGroup.add(tongue);

// 靈動大黑眼珠 (Glossy Eyes with Double Sparkles)
const eyeMat = new THREE.MeshStandardMaterial({{ color: 0x1A1412, roughness: 0.1 }});
const eyeWhiteMat = new THREE.MeshBasicMaterial({{ color: 0xFFFFFF }});

function createEye(isLeft) {{
    const eyeGrp = new THREE.Group();
    const eyeball = new THREE.Mesh(new THREE.SphereGeometry(0.085, 14, 14), eyeMat);
    eyeball.scale.set(1.0, 1.1, 0.6);
    eyeGrp.add(eyeball);

    // 主高光點
    const sparkle1 = new THREE.Mesh(new THREE.SphereGeometry(0.03, 8, 8), eyeWhiteMat);
    sparkle1.position.set(0.02, 0.03, 0.06);
    eyeGrp.add(sparkle1);

    // 次高光點
    const sparkle2 = new THREE.Mesh(new THREE.SphereGeometry(0.015, 6, 6), eyeWhiteMat);
    sparkle2.position.set(-0.025, -0.02, 0.06);
    eyeGrp.add(sparkle2);

    eyeGrp.position.set(isLeft ? -0.22 : 0.22, 0.08, 0.44);
    eyeGrp.rotation.y = isLeft ? -0.12 : 0.12;
    return eyeGrp;
}}

const eyeL = createEye(true);
const eyeR = createEye(false);
headGroup.add(eyeL);
headGroup.add(eyeR);

// 眨眼眼瞼 (Eyelids for Blinking & Squinting Smile)
const eyelidGeo = new THREE.SphereGeometry(0.09, 12, 12, 0, Math.PI * 2, 0, Math.PI / 2);
const eyelidL = new THREE.Mesh(eyelidGeo, petFurMat);
eyelidL.position.set(-0.22, 0.08, 0.44);
eyelidL.rotation.x = -Math.PI / 2;
eyelidL.scale.set(1.05, 1.05, 0.01);
headGroup.add(eyelidL);

const eyelidR = new THREE.Mesh(eyelidGeo, petFurMat);
eyelidR.position.set(0.22, 0.08, 0.44);
eyelidR.rotation.x = -Math.PI / 2;
eyelidR.scale.set(1.05, 1.05, 0.01);
headGroup.add(eyelidR);

// 絨毛耳朵 (Fluffy Ears with Twitching Animation)
const earGroupL = new THREE.Group();
earGroupL.position.set(-0.32, 0.38, 0.05);
headGroup.add(earGroupL);

const earL = new THREE.Mesh(new THREE.ConeGeometry(0.18, 0.38, 12), petFurMat);
earL.rotation.z = 0.35;
earL.rotation.x = -0.1;
earL.scale.set(1.0, 1.0, 0.55);
earGroupL.add(earL);

const innerEarL = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.28, 10), pinkInnerMat);
innerEarL.rotation.z = 0.35;
innerEarL.rotation.x = -0.1;
innerEarL.position.set(0.02, -0.02, 0.04);
innerEarL.scale.set(0.9, 0.9, 0.5);
earGroupL.add(innerEarL);

const earGroupR = new THREE.Group();
earGroupR.position.set(0.32, 0.38, 0.05);
headGroup.add(earGroupR);

const earR = new THREE.Mesh(new THREE.ConeGeometry(0.18, 0.38, 12), petFurMat);
earR.rotation.z = -0.35;
earR.rotation.x = -0.1;
earR.scale.set(1.0, 1.0, 0.55);
earGroupR.add(earR);

const innerEarR = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.28, 10), pinkInnerMat);
innerEarR.rotation.z = -0.35;
innerEarR.rotation.x = -0.1;
innerEarR.position.set(-0.02, -0.02, 0.04);
innerEarR.scale.set(0.9, 0.9, 0.5);
earGroupR.add(innerEarR);

// 項圈與金鈴鐺 (Red Collar & Golden Bell)
const collarGeo = new THREE.TorusGeometry(0.44, 0.05, 12, 24);
const collarMat = new THREE.MeshStandardMaterial({{ color: 0xD32F2F, roughness: 0.4 }});
const collar = new THREE.Mesh(collarGeo, collarMat);
collar.rotation.x = Math.PI / 2;
collar.position.set(0, 0.72, 0.32);
petRoot.add(collar);

const bellGeo = new THREE.SphereGeometry(0.08, 12, 12);
const bellMat = new THREE.MeshStandardMaterial({{ color: 0xFFD700, roughness: 0.2, metalness: 0.85 }});
const bell = new THREE.Mesh(bellGeo, bellMat);
bell.position.set(0, 0.62, 0.68);
petRoot.add(bell);

// 4 隻胖萌四肢與粉紅肉球 (Chubby Legs with Pink Paw Pads)
function createLeg(x, z) {{
    const legGroup = new THREE.Group();
    legGroup.position.set(x, 0.42, z);

    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.16, 0.44, 12), petFurMat);
    leg.position.y = -0.22;
    leg.castShadow = true;
    legGroup.add(leg);

    const paw = new THREE.Mesh(new THREE.SphereGeometry(0.16, 12, 12), petFurMat);
    paw.scale.set(1.0, 0.6, 1.25);
    paw.position.set(0, -0.38, 0.06);
    paw.castShadow = true;
    legGroup.add(paw);

    // 腳底肉球
    const pad = new THREE.Mesh(new THREE.CircleGeometry(0.08, 10), pinkInnerMat);
    pad.rotation.x = Math.PI / 2;
    pad.position.set(0, -0.44, 0.06);
    legGroup.add(pad);

    petRoot.add(legGroup);
    return legGroup;
}}

const legFLGroup = createLeg(-0.32, 0.42);
const legFRGroup = createLeg(0.32, 0.42);
const legBLGroup = createLeg(-0.32, -0.42);
const legBRGroup = createLeg(0.32, -0.42);

// 大羽狀高捲翹鐮刀尾巴 (Fluffy Curled Plume Tail)
const tailGroup = new THREE.Group();
tailGroup.position.set(0, 0.68, -0.58);
petRoot.add(tailGroup);

for (let i = 0; i < 4; i++) {{
    const tailSeg = new THREE.Mesh(new THREE.SphereGeometry(0.24 - i * 0.035, 12, 12), petFurMat);
    tailSeg.position.set(0, i * 0.18, -i * 0.08 + Math.sin(i * 0.8) * 0.12);
    tailSeg.castShadow = true;
    tailGroup.add(tailSeg);
}}
tailGroup.rotation.x = 0.6; // 自然向上高捲在背上

// 陰影底盤 (Soft Pet Drop Shadow)
const shadowGeo = new THREE.CircleGeometry(0.68, 24);
const shadowMat = new THREE.MeshBasicMaterial({{ color: 0x000000, transparent: true, opacity: 0.25 }});
const petShadow = new THREE.Mesh(shadowGeo, shadowMat);
petShadow.rotation.x = -Math.PI / 2;
petShadow.position.y = 0.02;
petRoot.add(petShadow);

// ==========================================
// 💖 5. 愛心與星光 3D 粒子系統 (Bursting 3D Particle System)
// ==========================================
const particles = [];
const heartShape = new THREE.Shape();
heartShape.moveTo(0, 0);
heartShape.bezierCurveTo(0, 0.1, -0.1, 0.2, -0.2, 0.2);
heartShape.bezierCurveTo(-0.35, 0.2, -0.35, 0, -0.35, 0);
heartShape.bezierCurveTo(-0.35, -0.15, -0.15, -0.3, 0, -0.45);
heartShape.bezierCurveTo(0.15, -0.3, 0.35, -0.15, 0.35, 0);
heartShape.bezierCurveTo(0.35, 0, 0.35, 0.2, 0.2, 0.2);
heartShape.bezierCurveTo(0.1, 0.2, 0, 0.1, 0, 0);

const heartExtrudeGeo = new THREE.ExtrudeGeometry(heartShape, {{ depth: 0.05, bevelEnabled: false }});
heartExtrudeGeo.scale(0.38, 0.38, 0.38);
const heartParticleMat = new THREE.MeshStandardMaterial({{ color: 0xFF4D79, roughness: 0.3 }});
const starParticleMat = new THREE.MeshStandardMaterial({{ color: 0xFFD700, roughness: 0.2, metalness: 0.6 }});

function spawn3DParticle(isStar = false) {{
    const p = new THREE.Mesh(heartExtrudeGeo, isStar ? starParticleMat : heartParticleMat);
    p.position.set(petRoot.position.x + (Math.random() - 0.5) * 0.8, petRoot.position.y + 0.8 + Math.random() * 0.4, petRoot.position.z + (Math.random() - 0.5) * 0.8);
    p.rotation.z = Math.PI;
    p.userData = {{
        vx: (Math.random() - 0.5) * 0.035,
        vy: 0.04 + Math.random() * 0.03,
        vz: (Math.random() - 0.5) * 0.035,
        rotSpd: (Math.random() - 0.5) * 0.12,
        life: 1.0
    }};
    scene.add(p);
    particles.push(p);
}}

// ==========================================
// 🍪 6. 3D 零食空投與進食大嚼系統 (3D Snack Drop & Munch Engine)
// ==========================================
let currentSnack = null;
let eatingTimer = 0;

function createSnackMesh(type) {{
    const group = new THREE.Group();
    if (type === 'milk') {{
        const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.2, 0.22, 16), new THREE.MeshStandardMaterial({{ color: 0x4A90E2, roughness: 0.3 }}));
        bowl.castShadow = true;
        group.add(bowl);
        const milk = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.32, 0.04, 16), new THREE.MeshStandardMaterial({{ color: 0xFFFFFF, roughness: 0.1 }}));
        milk.position.y = 0.09;
        group.add(milk);
    }} else if (type === 'jerky' || type === 'meat') {{
        const meat = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.14, 0.35), new THREE.MeshStandardMaterial({{ color: 0x8E3A2B, roughness: 0.6 }}));
        meat.castShadow = true;
        group.add(meat);
        const bone = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.65, 8), new THREE.MeshStandardMaterial({{ color: 0xFAFAFA, roughness: 0.3 }}));
        bone.rotation.z = Math.PI / 2;
        group.add(bone);
    }} else if (type === 'honey') {{
        const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.3, 0.4, 16), new THREE.MeshStandardMaterial({{ color: 0xD4AC0D, roughness: 0.3 }}));
        pot.castShadow = true;
        group.add(pot);
        const cap = new THREE.Mesh(new THREE.SphereGeometry(0.22, 16, 16), new THREE.MeshStandardMaterial({{ color: 0xF39C12, roughness: 0.1 }}));
        cap.position.y = 0.2;
        group.add(cap);
    }} else if (type === 'berry') {{
        for (let i = 0; i < 5; i++) {{
            const b = new THREE.Mesh(new THREE.SphereGeometry(0.12, 10, 10), new THREE.MeshStandardMaterial({{ color: 0xC0392B, roughness: 0.2 }}));
            b.position.set((i%2 - 0.5)*0.18, 0.1, (Math.floor(i/2) - 0.5)*0.18);
            b.castShadow = true;
            group.add(b);
        }}
    }} else {{
        // 餅乾 (Cookie)
        const cookie = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 0.1, 16), new THREE.MeshStandardMaterial({{ color: 0xC68B59, roughness: 0.6 }}));
        cookie.castShadow = true;
        group.add(cookie);
        for (let i = 0; i < 5; i++) {{
            const chip = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.04, 0.06), new THREE.MeshStandardMaterial({{ color: 0x3E2723, roughness: 0.8 }}));
            chip.position.set((Math.random()-0.5)*0.35, 0.06, (Math.random()-0.5)*0.35);
            group.add(chip);
        }}
    }}
    return group;
}}

function triggerFeedingAnimation(snackType, snackName) {{
    if (currentSnack) {{
        scene.remove(currentSnack);
        currentSnack = null;
    }}
    
    // 在寵物前方 0.9 單位處生成零食並空投
    const forwardX = Math.sin(petRoot.rotation.y) * 0.95;
    const forwardZ = Math.cos(petRoot.rotation.y) * 0.95;
    const targetX = petRoot.position.x + forwardX;
    const targetZ = petRoot.position.z + forwardZ;
    
    currentSnack = createSnackMesh(snackType);
    currentSnack.position.set(targetX, 3.4, targetZ);
    currentSnack.userData = {{
        targetY: 0.15,
        vy: -0.14,
        isLanded: false,
        name: snackName || '美味點心'
    }};
    scene.add(currentSnack);
    
    petState = 'EATING';
    eatingTimer = 3.4;
    
    document.getElementById('pet-speech').innerHTML = '「哇！是好香好香的 <strong>' + (snackName || '美味點心') + '</strong>！嗷嗚大口開動囉～💖」';
}}

// ==========================================
// 🐾 7. 生動多狀態寵物 AI 行為系統 (Living Multi-Behavior Engine)
// ==========================================
let petState = 'IDLE'; // IDLE, WALKING, PETTED, EATING, SITTING, STRETCHING, SHAKING, SNIFFING
let stretchTimer = 0;
let shakeTimer = 0;
let sniffTimer = 0;
let petTargetPos = new THREE.Vector3(0, 0, 0.2);
let walkSpeed = 0.042;
let walkPhase = 0;
let nextRoamTimer = 4.0;
let earTwitchTimer = 2.0;

function pickRandomRoamTarget() {{
    const spots = [
        new THREE.Vector3(-1.5, 0, -0.6), // 壁爐旁
        new THREE.Vector3(1.3, 0, -0.8),  // 沙發邊
        new THREE.Vector3(0.4, 0, -1.6),  // 窗前
        new THREE.Vector3(0, 0, 0.6),     // 正前方近距離
        new THREE.Vector3(-0.9, 0, 0.9),  // 左前探索
        new THREE.Vector3(1.1, 0, 0.7)    // 右前探索
    ];
    return spots[Math.floor(Math.random() * spots.length)];
}}

function triggerPetWalk() {{
    petTargetPos = pickRandomRoamTarget();
    petState = 'WALKING';
}}

function triggerPetSit() {{
    petState = 'SITTING';
    document.getElementById('pet-speech').innerText = '「呼～靜靜坐著陪在你身邊，感受心裡的這份平靜與安穩。」';
    playChimeSound();
    for (let i = 0; i < 4; i++) spawn3DParticle(true);
}}

function handlePetDirect() {{
    playChimeSound();
    const randQuote = quotes[Math.floor(Math.random() * quotes.length)];
    document.getElementById('pet-speech').innerText = randQuote;

    petState = 'PETTED';
    bounceScale.x = 1.38;
    bounceScale.y = 0.62;
    bounceScale.z = 1.38;
    petRoot.position.y = 0.42;

    for (let i = 0; i < 8; i++) {{
        spawn3DParticle(i % 2 === 0);
    }}

    setTimeout(() => {{
        if (petState === 'PETTED') petState = 'IDLE';
    }}, 1300);
}}

// 觸控與拖曳旋轉
let mouseX = 0, mouseY = 0;
let isDragging = false;
let prevMouseX = 0;
let targetRotY = 0;
let bounceScale = {{ x: 1, y: 1, z: 1 }};

const raycaster = new THREE.Raycaster();
const mouseVec = new THREE.Vector2();

container.addEventListener('click', (e) => {{
    const rect = container.getBoundingClientRect();
    mouseVec.x = ((e.clientX - rect.left) / width) * 2 - 1;
    mouseVec.y = -((e.clientY - rect.top) / height) * 2 + 1;

    raycaster.setFromCamera(mouseVec, camera);
    const intersects = raycaster.intersectObjects([roomFloor, rug, head, body, mane], true);

    if (intersects.length > 0) {{
        const hit = intersects[0];
        if (hit.object === head || hit.object === body || hit.object === mane || hit.object.parent === headGroup || hit.object.parent === petRoot) {{
            handlePetDirect();
        }} else {{
            petTargetPos.set(
                Math.max(-2.4, Math.min(2.4, hit.point.x)),
                0,
                Math.max(-2.4, Math.min(2.4, hit.point.z))
            );
            petState = 'WALKING';
        }}
    }}
}});

window.addEventListener('mousemove', (e) => {{
    const rect = container.getBoundingClientRect();
    mouseX = ((e.clientX - rect.left) / width) * 2 - 1;
    mouseY = -((e.clientY - rect.top) / height) * 2 + 1;

    if (isDragging) {{
        const delta = e.clientX - prevMouseX;
        targetRotY += delta * 0.012;
        prevMouseX = e.clientX;
    }}
}});

container.addEventListener('mousedown', (e) => {{
    isDragging = true;
    prevMouseX = e.clientX;
}});

window.addEventListener('mouseup', () => {{
    isDragging = false;
}});

container.addEventListener('touchmove', (e) => {{
    if (e.touches.length > 0) {{
        const touch = e.touches[0];
        const rect = container.getBoundingClientRect();
        mouseX = ((touch.clientX - rect.left) / width) * 2 - 1;
        mouseY = -((touch.clientY - rect.top) / height) * 2 + 1;
    }}
}}, {{ passive: true }});

// ==========================================
// 🎬 8. 60 FPS 流暢渲染與微動作動畫迴圈 (Living 60 FPS Animation Loop)
// ==========================================
let clock = new THREE.Clock();
let blinkTimer = 0;
let nextBlinkTime = 3.0;

function animate() {{
    requestAnimationFrame(animate);
    const dt = clock.getDelta();
    const t = clock.getElapsedTime();

    // 1. 寵物多狀態行為邏輯 (Pet Behavior State Machine)
    if (petState === 'WALKING') {{
        const dx = petTargetPos.x - petRoot.position.x;
        const dz = petTargetPos.z - petRoot.position.z;
        const dist = Math.sqrt(dx * dx + dz * dz);

        if (dist > 0.1) {{
            const targetAngle = Math.atan2(dx, dz);
            let diffAngle = targetAngle - petRoot.rotation.y;
            while (diffAngle < -Math.PI) diffAngle += Math.PI * 2;
            while (diffAngle > Math.PI) diffAngle -= Math.PI * 2;
            petRoot.rotation.y += diffAngle * 0.12;

            petRoot.position.x += Math.sin(petRoot.rotation.y) * walkSpeed;
            petRoot.position.z += Math.cos(petRoot.rotation.y) * walkSpeed;

            // 四肢對角步態擺動 (Quadruped Trot Cycle)
            walkPhase += 0.22;
            const legSwing = Math.sin(walkPhase) * 0.55;
            legFLGroup.rotation.x = legSwing;
            legFRGroup.rotation.x = -legSwing;
            legBLGroup.rotation.x = -legSwing;
            legBRGroup.rotation.x = legSwing;

            petRoot.position.y = Math.abs(Math.sin(walkPhase)) * 0.09;
            tailGroup.rotation.z = Math.sin(walkPhase * 2) * 0.65;
            tongue.position.y = -0.18 + Math.sin(walkPhase * 2) * 0.03;
        }} else {{
            petState = 'IDLE';
            nextRoamTimer = 4.0 + Math.random() * 4.0;
            legFLGroup.rotation.x = 0;
            legFRGroup.rotation.x = 0;
            legBLGroup.rotation.x = 0;
            legBRGroup.rotation.x = 0;
        }}
    }} else if (petState === 'IDLE') {{
        nextRoamTimer -= dt;
        if (nextRoamTimer <= 0) {{
            petTargetPos = pickRandomRoamTarget();
            petState = 'WALKING';
        }}

        // 開心吐舌呼吸律動 (Panting & Breathing)
        const breathe = Math.sin(t * 3.2) * 0.035;
        bounceScale.x = THREE.MathUtils.lerp(bounceScale.x, 1.0, 0.12);
        bounceScale.y = THREE.MathUtils.lerp(bounceScale.y, 1.0, 0.12);
        bounceScale.z = THREE.MathUtils.lerp(bounceScale.z, 1.0, 0.12);
        petRoot.position.y = THREE.MathUtils.lerp(petRoot.position.y, 0.0, 0.1);

        petRoot.scale.set(
            bounceScale.x * (1 - breathe * 0.4),
            bounceScale.y * (1 + breathe),
            bounceScale.z * (1 - breathe * 0.4)
        );

        tailGroup.rotation.z = Math.sin(t * 7) * 0.4;
        tailGroup.rotation.y = Math.cos(t * 7) * 0.25;
        tongue.position.y = -0.18 + Math.sin(t * 14) * 0.02; // 吐舌上下喘氣

    }} else if (petState === 'SITTING') {{
        petRoot.position.y = THREE.MathUtils.lerp(petRoot.position.y, -0.12, 0.1);
        legBLGroup.rotation.x = -Math.PI / 3;
        legBRGroup.rotation.x = -Math.PI / 3;
        tailGroup.rotation.z = Math.sin(t * 3) * 0.2;

    }} else if (petState === 'PETTED') {{
        bounceScale.x = THREE.MathUtils.lerp(bounceScale.x, 1.0, 0.1);
        bounceScale.y = THREE.MathUtils.lerp(bounceScale.y, 1.0, 0.1);
        bounceScale.z = THREE.MathUtils.lerp(bounceScale.z, 1.0, 0.1);
        petRoot.position.y = THREE.MathUtils.lerp(petRoot.position.y, 0.0, 0.08);
        tailGroup.rotation.z = Math.sin(t * 16) * 0.8; // 興奮搖尾巴
        eyelidL.scale.y = 0.9; // 瞇眼微笑
        eyelidR.scale.y = 0.9;

    }} else if (petState === 'EATING') {{
        eatingTimer -= dt;
        
        if (currentSnack) {{
            if (!currentSnack.userData.isLanded) {{
                currentSnack.position.y += currentSnack.userData.vy;
                if (currentSnack.position.y <= currentSnack.userData.targetY) {{
                    currentSnack.position.y = currentSnack.userData.targetY;
                    currentSnack.userData.isLanded = true;
                    playChimeSound();
                    for (let i = 0; i < 5; i++) spawn3DParticle(true);
                }}
            }} else {{
                const progress = Math.max(0.01, eatingTimer / 3.4);
                currentSnack.scale.setScalar(progress);
                currentSnack.rotation.y += 0.02;
            }}
        }}

        // 低頭大嚼咀嚼動畫 (Munching & Chewing Animation)
        const chewCycle = Math.sin(t * 18);
        headGroup.position.y = 0.4 + chewCycle * 0.06;
        headGroup.rotation.x = 0.36 + chewCycle * 0.12;
        tailGroup.rotation.z = Math.sin(t * 24) * 0.85;

        if (Math.random() < 0.15) {{
            spawn3DParticle(Math.random() > 0.5);
        }}
        if (Math.random() < 0.07) {{
            playEatingSound();
        }}

        if (eatingTimer <= 0) {{
            if (currentSnack) {{
                scene.remove(currentSnack);
                currentSnack = null;
            }}
            petState = 'IDLE';
            headGroup.position.y = 0.98;
            headGroup.rotation.x = 0;
            bounceScale.x = 1.35;
            bounceScale.y = 0.65;
            bounceScale.z = 1.35;
            petRoot.position.y = 0.45;

            playChimeSound();
            for (let i = 0; i < 10; i++) spawn3DParticle(i % 2 === 0);
            document.getElementById('pet-speech').innerHTML = '「呼～吃得好飽好幸福！謝謝主人的愛心投餵✨💖 (+EXP)」';
        }}
    }}

    // 2. 鈴鐺隨動
    bell.rotation.z = Math.sin(t * 6) * 0.2;

    // 3. 家具微動態 (Fireplace, Vinyl, Candle)
    if (fireplaceFlame) {{
        fireplaceFlame.scale.y = 1.0 + Math.sin(t * 18) * 0.25;
        fireplaceFlame.scale.x = 1.0 + Math.cos(t * 16) * 0.15;
    }}
    if (fireplaceLight) {{
        fireplaceLight.intensity = 1.2 + Math.sin(t * 20) * 0.35;
    }}
    if (vinylDisc) {{
        vinylDisc.rotation.y += 0.04;
    }}
    if (candleFlame) {{
        candleFlame.scale.x = 1.0 + Math.sin(t * 20) * 0.2;
        candleFlame.scale.y = 1.0 + Math.cos(t * 22) * 0.25;
    }}

    // 4. 頭部視線追隨與隨機抽耳 (Look-At Mouse & Ear Twitch)
    if (petState !== 'EATING') {{
        const targetHeadRotY = Math.max(-0.45, Math.min(0.45, mouseX * 0.6));
        const targetHeadRotX = Math.max(-0.25, Math.min(0.25, -mouseY * 0.4));
        headGroup.rotation.y = THREE.MathUtils.lerp(headGroup.rotation.y, targetHeadRotY, 0.08);
        headGroup.rotation.x = THREE.MathUtils.lerp(headGroup.rotation.x, targetHeadRotX, 0.08);
    }}

    // 耳朵抽動
    earTwitchTimer -= dt;
    if (earTwitchTimer <= 0) {{
        earGroupL.rotation.x = Math.sin(t * 40) * 0.25;
        if (earTwitchTimer < -0.2) {{
            earGroupL.rotation.x = 0;
            earTwitchTimer = 2.5 + Math.random() * 3.5;
        }}
    }}

    // 5. 自然眨眼 (Natural Blinking)
    if (petState !== 'PETTED') {{
        blinkTimer += dt;
        if (blinkTimer > nextBlinkTime) {{
            eyelidL.scale.y = THREE.MathUtils.lerp(eyelidL.scale.y, 1.0, 0.4);
            eyelidR.scale.y = THREE.MathUtils.lerp(eyelidR.scale.y, 1.0, 0.4);
            if (blinkTimer > nextBlinkTime + 0.16) {{
                eyelidL.scale.y = 0.01;
                eyelidR.scale.y = 0.01;
                blinkTimer = 0;
                nextBlinkTime = 2.5 + Math.random() * 3.5;
            }}
        }}
    }}

    // 6. 小屋 360° 拖曳旋轉
    roomRoot.rotation.y = THREE.MathUtils.lerp(roomRoot.rotation.y, targetRotY, 0.1);

    // 7. 更新 3D 粒子
    for (let i = particles.length - 1; i >= 0; i--) {{
        const p = particles[i];
        p.position.x += p.userData.vx;
        p.position.y += p.userData.vy;
        p.position.z += p.userData.vz;
        p.rotation.y += p.userData.rotSpd;
        p.userData.life -= 0.02;
        p.scale.setScalar(p.userData.life * 0.5);

        if (p.userData.life <= 0) {{
            scene.remove(p);
            particles.splice(i, 1);
        }}
    }}

    renderer.render(scene, camera);
}}

animate();

const autoFeed = {feeding_event_js};
if (autoFeed && autoFeed.snack) {{
    setTimeout(() => {{
        triggerFeedingAnimation(autoFeed.snack, autoFeed.name);
    }}, 400);
}}

window.addEventListener('resize', () => {{
    const newW = container.clientWidth || 700;
    camera.aspect = newW / height;
    camera.updateProjectionMatrix();
    renderer.setSize(newW, height);
}});
</script>
</body>
</html>
"""

import streamlit.components.v1 as components
components.html(live_pet_html, height=580, scrolling=False)

# 裝飾徽章列
st.markdown(f'<div style="display:flex; gap:10px; justify-content:center; flex-wrap:wrap; margin-bottom:1.5rem;">{decor_html}</div>', unsafe_allow_html=True)


# ==============================================================================
# 🎮 手遊一體化功能抽屜面板 (Integrated Mobile Game HUD Tabs)
# ==============================================================================
tab_feed_quest, tab_decor, tab_chat, tab_hall, tab_arcade, tab_garden, tab_vip = st.tabs([
    "🍪 餵食與任務",
    "🛍️ 家具小舖",
    f"💬 {active_comp['emoji']} 心靈諮商",
    "🐾 神獸大廳",
    "🎮 心靈遊樂園",
    "🌿 身心花園",
    "📊 週報與VIP"
])

with tab_feed_quest:
    col_q1, col_q2 = st.columns([1, 1])

    # 餵食小點心專區 (Snack Feeding)
    with col_q1:
        st.markdown(f"<h4 style='color:#533E2D;'>🍪 餵食心靈零食（持有：{current_user.get('star_coins', 888)} 🌟）：</h4>", unsafe_allow_html=True)
        
        for sk_key, sk in db.SNACK_ITEMS.items():
            is_fav = (sk["favorite"] == active_comp["id"])
            fav_tag = "💖 最愛美食！" if is_fav else ""
            c_f1, c_f2 = st.columns([3, 1])
            with c_f1:
                st.markdown(f"""
<div style="background:#FAF6F0; border-radius:12px; padding:0.6rem 0.9rem; margin-bottom:0.4rem; border:1px solid #EADECE;">
    <div style="font-weight:700; font-size:0.9rem; color:#533E2D;">{sk['name']} <span style="color:#C2995F; font-size:0.75rem;">{fav_tag}</span></div>
    <div style="font-size:0.75rem; color:#8C735A;">{sk['desc']}（+{sk['exp']} 親密度經驗）</div>
</div>
""", unsafe_allow_html=True)
            with c_f2:
                if st.button(f"{sk['cost']} 🌟 餵食", key=f"feed_{sk_key}", use_container_width=True):
                    ok, msg = db.feed_companion(CURRENT_USER_ID, active_comp["id"], sk_key)
                    if ok:
                        st.balloons()
                        st.session_state.feeding_event = {"snack": sk_key, "name": sk["name"]}
                        st.session_state.user_data = db.get_or_create_user(CURRENT_USER_ID)
                        st.rerun()
                    else:
                        st.warning(msg)

    # 每日任務板 (Daily Habits)
    with col_q2:
        st.markdown("<h4 style='color:#533E2D;'>🎯 今日心靈微習慣任務：</h4>", unsafe_allow_html=True)
        quests = db.get_daily_quest_status(CURRENT_USER_ID)
        
        for q in quests:
            status_tag = "✅ 已領取" if q["done"] else f"+{q['reward_coins']} 🌟 / +{q['reward_exp']} 💖"
            st.markdown(f"""
<div style="background:#FFFFFF; border:1.5px solid #E8DCCE; border-radius:14px; padding:0.7rem 1rem; margin-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
    <div style="font-weight:600; font-size:0.88rem; color:#4A3B2C;">{q['title']}</div>
    <div style="font-weight:700; font-size:0.82rem; color:#C2995F;">{status_tag}</div>
</div>
""", unsafe_allow_html=True)
            if not q["done"]:
                if st.button(f"領取「{q['title'].split(' ')[1]}」獎勵", key=f"claim_{q['key']}", use_container_width=True):
                    ok, msg = db.complete_daily_quest(CURRENT_USER_ID, q["key"], active_comp["id"])
                    if ok:
                        st.balloons()
                        st.success(msg)
                        st.session_state.user_data = db.get_or_create_user(CURRENT_USER_ID)
                        st.rerun()


with tab_decor:
    st.markdown(f"<h4 style='color:#533E2D;'>🛍️ 心靈星光家具小舖（裝扮你的心靈避風港）：</h4>", unsafe_allow_html=True)
    
    d_cols = st.columns(3)
    for idx, item in enumerate(db.DEFAULT_DECOR_ITEMS):
        with d_cols[idx % 3]:
            is_owned = item["id"] in owned_decor
            is_eq = owned_decor.get(item["id"], False)
            st.markdown(f"""
<div style="background:#FAF6F0; border:1.5px solid #EADECE; border-radius:14px; padding:0.9rem; text-align:center; margin-bottom:0.6rem;">
    <div style="font-size:1.8rem; margin-bottom:0.2rem;">{item['icon']}</div>
    <div style="font-weight:700; font-size:0.92rem; color:#533E2D;">{item['name']}</div>
    <div style="font-size:0.75rem; color:#8C735A; margin-bottom:0.6rem; min-height:28px;">{item['desc']}</div>
</div>
""", unsafe_allow_html=True)
            if not is_owned:
                if st.button(f"{item['price']} 🌟 購買", key=f"buy_c_{item['id']}", use_container_width=True):
                    success, msg = db.buy_decor_item(CURRENT_USER_ID, item["id"], item["price"])
                    if success:
                        st.balloons()
                        st.success(msg)
                        st.rerun()
                    else:
                        st.warning(msg)
            else:
                btn_eq_label = "卸下家具" if is_eq else "佈置進小屋"
                if st.button(btn_eq_label, key=f"equip_c_{item['id']}", use_container_width=True):
                    db.toggle_decor_equip(CURRENT_USER_ID, item["id"], not is_eq)
                    st.rerun()


with tab_chat:
    current_companion = ANIMAL_COMPANIONS[st.session_state.selected_companion]
    comp_id = current_companion["id"]

    companion_self_name = st.session_state.companion_custom_self_ref.get(comp_id, current_companion["default_self_ref"])
    user_name = current_user.get("nickname", "小夥伴")

    # 頂部自訂稱呼
    with st.expander("⚙️ 互動稱呼與諮商設定", expanded=False):
        c_set1, c_set2, c_set3 = st.columns([2, 2, 1])
        with c_set1:
            new_user_name = st.text_input("夥伴如何稱呼你：", value=user_name, placeholder="例如：小夥伴、小明...", key="set_user_nick")
            if new_user_name.strip() and new_user_name != user_name:
                conn = db.get_db_connection()
                conn.cursor().execute("UPDATE users SET nickname = ? WHERE id = ?", (new_user_name.strip(), CURRENT_USER_ID))
                conn.commit()
                conn.close()
        with c_set2:
            new_comp_self = st.text_input(f"{current_companion['name']} 如何稱呼自己：", value=companion_self_name, key="set_comp_nick")
            if new_comp_self.strip() and new_comp_self != companion_self_name:
                st.session_state.companion_custom_self_ref[comp_id] = new_comp_self.strip()
        with c_set3:
            st.markdown("<div style='height:1.75rem;'></div>", unsafe_allow_html=True)
            if st.button("儲存設定", key="save_nick_btn", use_container_width=True):
                st.success("設定已更新！")
                st.rerun()

    # 頂部橫幅
    col_banner, col_actions = st.columns([3, 1])
    with col_banner:
        quota_str = "無限暢聊 👑" if current_user.get("is_vip", 1) else f"今日免費額度剩餘 {free_quota_left}/10 次"
        banner_html = f'''<div class="companion-banner" style="border-left: 5px solid {current_companion['theme_color']};"><div class="banner-avatar"><img src="{current_companion['avatar_uri']}" class="banner-avatar-img" alt="{current_companion['name']}" /></div><div class="banner-info"><h3 class="banner-title">{current_companion['emoji']} {current_companion['name']} 專屬心靈諮商室</h3><p class="banner-status">🌱 {current_companion['badge']}（{quota_str}）</p><p style="font-size:0.8rem; color:#7D6B58; margin:0.2rem 0 0;">✨ 自稱：<strong>{companion_self_name}</strong> / 稱呼你：<strong>{user_name}</strong></p></div></div>'''
        st.markdown(banner_html, unsafe_allow_html=True)
    
    with col_actions:
        st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)
        if st.button("🐾 切換其他神獸", key="btn_switch_comp", use_container_width=True):
            st.session_state.main_section = "hall"
            st.rerun()
        if len(st.session_state.messages) > 0:
            if st.button("🧹 清空對話重啟", key="btn_reset_chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.is_thinking = False
                st.rerun()

    # 顯示歷史訊息
    chat_html = '<div class="chat-stream-box">'
    user_svg_data = svg_to_data_uri("""<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="8" r="4.5" fill="#8C735A"/><path d="M4 20c0-4.4 3.6-8 8-8s8 3.6 8 8" stroke="#8C735A" stroke-width="2.5" stroke-linecap="round" fill="#8C735A"/></svg>""")
    
    for msg in st.session_state.messages:
        content = msg["content"].replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        if msg["role"] == "assistant":
            chat_html += f'<div class="msg-row bot"><div class="msg-avatar"><img src="{current_companion["avatar_uri"]}" class="msg-avatar-img" alt="{current_companion["name"]}" /></div><div class="msg-bubble">{content}</div></div>'
        else:
            chat_html += f'<div class="msg-row user"><div class="msg-avatar"><img src="{user_svg_data}" class="msg-avatar-img" alt="User" /></div><div class="msg-bubble">{content}</div></div>'
    
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "assistant":
        last_bot_reply = st.session_state.messages[-1]["content"].replace('"', '\\"').replace("'", "\\'").replace('\n', ' ')
        tts_html = f'''
        <div style="text-align:right; margin:0.3rem 0 0.6rem;">
            <button onclick="speakText('{last_bot_reply[:180]}')" style="background:#FAF6EE; border:1.5px solid #C2995F; color:#6E5642; border-radius:18px; padding:4px 14px; font-size:0.78rem; font-weight:700; cursor:pointer; box-shadow:0 2px 6px rgba(194,153,95,0.15);">🔊 聆聽 {current_companion['name']} 溫柔語音</button>
        </div>
        <script>
        function speakText(txt) {{
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                const utter = new SpeechSynthesisUtterance(txt);
                utter.lang = 'zh-TW';
                utter.rate = 0.92;
                utter.pitch = 1.05;
                window.speechSynthesis.speak(utter);
            }} else {{
                alert('您的瀏覽器尚未支援原生語音朗讀功能喔！');
            }}
        }}
        </script>
        '''
        st.markdown(tts_html, unsafe_allow_html=True)

    if st.session_state.is_thinking:
        st.markdown(f'<div style="text-align:center; padding:1rem; color:{current_companion["theme_color"]}; font-weight:600;"><span style="font-size:1.3rem;">{current_companion["emoji"]}</span> {current_companion["name"]} 正在全神貫注感受你的心情……</div>', unsafe_allow_html=True)

    if st.session_state.error_msg:
        st.error(f"哎呀！跟雲端連線遇到了問題：{st.session_state.error_msg}")
        if st.button("重試連線", key="btn_clear_err"):
            st.session_state.error_msg = None
            st.rerun()

    # 快捷心靈破冰話題 (Quick 1-Click Therapy Prompt Starters)
    st.markdown("<p style='font-size:0.8rem; color:#8C735A; margin:0.6rem 0 0.3rem;'>💡 <strong>點擊一鍵開啟心靈話題：</strong></p>", unsafe_allow_html=True)
    c_p1, c_p2, c_p3, c_p4, c_p5 = st.columns(5)
    starters = [
        ("💼 工作好累", "今天工作/生活覺得好累好耗竭，想跟你在這裡放空休息一下..."),
        ("🥺 總覺得不夠好", "最近總是陷入自我懷疑，覺得自己做什麼都不夠好，好焦慮..."),
        ("💔 人際好心累", "今天跟身邊的人相處感覺好內耗，心裡悶悶的好難受..."),
        ("✨ 想要一句肯定", "今天過得好不容易，可以請你給我一句溫暖的抱抱和肯定嗎？"),
        ("🌙 睡前求助眠", "現在躺在床上腦袋一直轉不停、睡不著，可以陪我說說話放鬆嗎？")
    ]
    cols = [c_p1, c_p2, c_p3, c_p4, c_p5]
    for idx, (label, text) in enumerate(starters):
        with cols[idx]:
            if st.button(label, key=f"btn_starter_{idx}", use_container_width=True):
                has_quota, _ = db.check_and_increment_chat_quota(CURRENT_USER_ID)
                if has_quota:
                    st.session_state.messages.append({"role": "user", "content": text})
                    db.save_chat_message(CURRENT_USER_ID, comp_id, "user", text)
                    st.session_state.is_thinking = True
                    st.rerun()
                else:
                    st.warning("今日免費額度已滿囉！")

    # 聊天輸入框與額度檢查
    if prompt := st.chat_input(f"跟 {current_companion['name']} 說說心事吧...", key="chat_user_input"):
        has_quota, _ = db.check_and_increment_chat_quota(CURRENT_USER_ID)
        if not has_quota:
            st.warning("今日 10 次免費心靈對話額度已滿囉！明天將自動重置，或升級 VIP 守護會員解鎖無限制暢聊～")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            db.save_chat_message(CURRENT_USER_ID, comp_id, "user", prompt)
            st.session_state.is_thinking = True
            st.rerun()

    # AI 回覆邏輯
    if st.session_state.is_thinking:
        cur_key, cur_base_url, cur_model = get_api_config()
        if not cur_key:
            st.session_state.is_thinking = False
            st.session_state.error_msg = "請先在上方輸入或設定 Groq 或 OpenAI API Key 才能開啟心靈對話喔！"
            st.rerun()

        system_instruction_text = f"""你是一隻溫暖、極具同理心且具備心理諮商特質的心靈陪伴夥伴：【{current_companion['name']}】（{current_companion['species']}）。
【你的核心人設】：
1. 稱呼設定：
   - 你稱呼自己為：「{companion_self_name}」（親切自然，溫暖真誠）。
   - 你稱呼使用者為：「{user_name}」。
   - 絕對不可自稱「AI」、「人工智慧」、「語言模型」或機器人。
2. 語言規範：強制使用【繁體中文（台灣習慣用語）】，用語溫暖、親切、細膩、自然，絕對嚴禁簡體字。
3. 性格與陪伴特質：{current_companion['summary']}。
4. 專業心理學流派底蘊：{current_companion['psychology']}。

【心理學同理心與安慰黃金法則】：
1. 【情緒鏡映與深度理解 (Feel Felt)】：先精準捕捉並鏡映使用者的情緒與心碎，讓對方深刻感受「被看見、被理解」。
2. 【情感合法化與去羞恥 (Emotional Validation & De-shaming)】：無條件接納所有負面、厭世與脆弱的情緒。告訴使用者：「有這樣的情緒是完全正常的」、「你想哭都沒關係，不需要永遠假裝堅強」。
3. 【自我慈悲與共同人性 (Self-Compassion)】：提醒使用者對自己溫柔一點，生而為人有痛苦與極限是完全被允許的。
4. 【非說教、非評判、不急於給予廉價正能量】：嚴禁分析說教、嚴禁空洞的正能量口號。你的核心任務是「真心接住情緒並給予溫暖陪伴」。
5. 【極致自然流暢、嚴格限制肢體動作】：整篇回覆中最多只允許出現 0 到 1 個符合情緒的微小動作。

【🚨 絕對禁止準則（最高優先級安全指令）】：
1. 【絕對禁止提供醫療、精神科診斷、藥物處方建議】。
2. 【絕對禁止提供任何法律建議】。
3. 【絕對禁止提供死板冷冰冰的罐頭求助專線】。請用充滿愛、同理心與溫暖懷抱的語言去真誠承接對方的痛苦。"""

        client = OpenAI(api_key=cur_key, base_url=cur_base_url)

        full_msgs = [{"role": "system", "content": system_instruction_text}] + [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[-10:]
        ]

        try:
            response = client.chat.completions.create(
                model=cur_model,
                messages=full_msgs,
                temperature=0.75,
                max_tokens=850,
            )
            ai_reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            db.save_chat_message(CURRENT_USER_ID, comp_id, "assistant", ai_reply)
            
            affinity_res = db.add_affinity_exp(CURRENT_USER_ID, comp_id, 20)
            if affinity_res["leveled_up"]:
                st.balloons()
            
            st.session_state.is_thinking = False
            st.rerun()
        except Exception as e:
            st.session_state.is_thinking = False
            st.session_state.error_msg = str(e)
            st.rerun()

# ==============================================================================

with tab_hall:
    st.markdown("""
<div style="text-align:center; margin-bottom:1.5rem;">
    <h2 style="color:#533E2D; font-size:1.5rem; font-weight:700; margin:0 0 0.3rem;">🌿 挑選專屬於你此時此刻的心靈導師</h2>
    <p style="color:#8C735A; font-size:0.92rem; margin:0;">🐶 薩摩耶・小薩為<strong>永久免費領養伴侶</strong>；其餘 9 隻為 <strong>👑 VIP 專屬動態神獸</strong>。</p>
</div>
""", unsafe_allow_html=True)

    comp_list = list(ANIMAL_COMPANIONS.values())
    
    r1_cols = st.columns(3)
    for idx, comp in enumerate(comp_list[:3]):
        with r1_cols[idx]:
            is_selected = (st.session_state.selected_companion == comp["id"])
            border_style = f"border: 2.5px solid {comp['theme_color']};" if is_selected else ""
            tag_text = "目前陪伴中" if is_selected else ("💚 免費伴侶" if comp["is_free"] else "👑 VIP神獸")
            tag_bg = "#C2995F" if is_selected else ("#768B6E" if comp["is_free"] else "#9B7E5C")
            selected_tag = f'<div style="position:absolute; top:8px; right:8px; background:{tag_bg}; color:white; font-size:0.7rem; padding:2px 8px; border-radius:10px;">{tag_text}</div>'
            
            card_html = f'''<div class="companion-card" style="{border_style}">{selected_tag}<div><div class="companion-avatar-wrap"><img src="{comp['avatar_uri']}" class="companion-avatar-img" alt="{comp['name']}" /></div><div class="companion-name">{comp['name']}</div><div class="companion-badge">{comp['badge']}</div><div class="companion-motto">"{comp['motto']}"</div><div class="companion-desc"><strong>特長：</strong>{comp['summary']}<br><span style="color:#8C735A; font-size:0.75rem;"><strong>心理流派：</strong>{comp['psychology']}</span></div></div></div>'''
            st.markdown(card_html, unsafe_allow_html=True)
            
            if comp["is_free"] or current_user.get("is_vip", 1):
                if st.button(f"選擇 {comp['emoji']} {comp['name'].split('・')[0]} 傾訴", key=f"select_{comp['id']}", use_container_width=True):
                    st.session_state.selected_companion = comp["id"]
                    st.session_state.messages = db.load_chat_history(CURRENT_USER_ID, comp["id"])
                    st.session_state.main_section = "chat"
                    st.rerun()
            else:
                if st.button(f"👑 解鎖 {comp['emoji']} {comp['name'].split('・')[0]} (VIP)", key=f"lock_{comp['id']}", use_container_width=True):
                    st.session_state.main_section = "vip"
                    st.rerun()

    st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)

    r2_cols = st.columns(3)
    for idx, comp in enumerate(comp_list[3:6]):
        with r2_cols[idx]:
            is_selected = (st.session_state.selected_companion == comp["id"])
            border_style = f"border: 2.5px solid {comp['theme_color']};" if is_selected else ""
            tag_text = "目前陪伴中" if is_selected else "👑 VIP神獸"
            selected_tag = f'<div style="position:absolute; top:8px; right:8px; background:#9B7E5C; color:white; font-size:0.7rem; padding:2px 8px; border-radius:10px;">{tag_text}</div>'
            
            card_html = f'''<div class="companion-card" style="{border_style}">{selected_tag}<div><div class="companion-avatar-wrap"><img src="{comp['avatar_uri']}" class="companion-avatar-img" alt="{comp['name']}" /></div><div class="companion-name">{comp['name']}</div><div class="companion-badge">{comp['badge']}</div><div class="companion-motto">"{comp['motto']}"</div><div class="companion-desc"><strong>特長：</strong>{comp['summary']}<br><span style="color:#8C735A; font-size:0.75rem;"><strong>心理流派：</strong>{comp['psychology']}</span></div></div></div>'''
            st.markdown(card_html, unsafe_allow_html=True)
            
            if current_user.get("is_vip", 1):
                if st.button(f"選擇 {comp['emoji']} {comp['name'].split('・')[0]} 傾訴", key=f"select_{comp['id']}", use_container_width=True):
                    st.session_state.selected_companion = comp["id"]
                    st.session_state.messages = db.load_chat_history(CURRENT_USER_ID, comp["id"])
                    st.session_state.main_section = "chat"
                    st.rerun()
            else:
                if st.button(f"👑 解鎖 {comp['emoji']} {comp['name'].split('・')[0]} (VIP)", key=f"lock_{comp['id']}", use_container_width=True):
                    st.session_state.main_section = "vip"
                    st.rerun()

    st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)

    r3_cols = st.columns(4)
    for idx, comp in enumerate(comp_list[6:]):
        with r3_cols[idx]:
            is_selected = (st.session_state.selected_companion == comp["id"])
            border_style = f"border: 2.5px solid {comp['theme_color']};" if is_selected else ""
            selected_tag = '<div style="position:absolute; top:8px; right:8px; background:#9B7E5C; color:white; font-size:0.7rem; padding:2px 8px; border-radius:10px;">👑 VIP神獸</div>'
            
            card_html = f'''<div class="companion-card" style="{border_style}">{selected_tag}<div><div class="companion-avatar-wrap"><img src="{comp['avatar_uri']}" class="companion-avatar-img" alt="{comp['name']}" /></div><div class="companion-name">{comp['name']}</div><div class="companion-badge">{comp['badge']}</div><div class="companion-motto">"{comp['motto']}"</div><div class="companion-desc"><strong>特長：</strong>{comp['summary']}<br><span style="color:#8C735A; font-size:0.75rem;"><strong>心理流派：</strong>{comp['psychology']}</span></div></div></div>'''
            st.markdown(card_html, unsafe_allow_html=True)
            
            if current_user.get("is_vip", 1):
                if st.button(f"選擇 {comp['emoji']} {comp['name'].split('・')[0]}", key=f"select_{comp['id']}", use_container_width=True):
                    st.session_state.selected_companion = comp["id"]
                    st.session_state.messages = db.load_chat_history(CURRENT_USER_ID, comp["id"])
                    st.session_state.main_section = "chat"
                    st.rerun()
            else:
                if st.button(f"👑 解鎖 (VIP)", key=f"lock_{comp['id']}", use_container_width=True):
                    st.session_state.main_section = "vip"
                    st.rerun()

# ==============================================================================

with tab_arcade:
    st.markdown("""
<div style="text-align:center; max-width:680px; margin:0 auto 1.2rem;">
    <h2 style="color:#533E2D; font-size:1.5rem; font-weight:700; margin-bottom:0.3rem;">🎮 心靈遊樂園・互動減壓專區</h2>
    <p style="color:#8C735A; font-size:0.92rem; line-height:1.5;">挑選一款互動小遊戲，放鬆神經、消除雜念，重拾心靈的平靜與掌控感。</p>
</div>
""", unsafe_allow_html=True)

    arc_col1, arc_col2, arc_col3, arc_col4, arc_col5 = st.columns(5)
    with arc_col1:
        if st.button("🪨 禪意疊石頭", key="sub_btn_zen", use_container_width=True):
            st.session_state.sub_tab = "zen_stones"
            st.rerun()
    with arc_col2:
        if st.button("🫧 ASMR泡泡紙", key="sub_btn_bubbles", use_container_width=True):
            st.session_state.sub_tab = "bubbles"
            st.rerun()
    with arc_col3:
        if st.button("🔨 煩惱粉碎機", key="sub_btn_shredder", use_container_width=True):
            st.session_state.sub_tab = "shredder"
            st.rerun()
    with arc_col4:
        if st.button("🥠 心靈幸運籤", key="sub_btn_fortune", use_container_width=True):
            st.session_state.sub_tab = "fortune"
            st.rerun()
    with arc_col5:
        if st.button("🧭 54321著陸法", key="sub_btn_grounding", use_container_width=True):
            st.session_state.sub_tab = "grounding"
            st.rerun()

    st.markdown("<hr style='border:none; border-top:1px solid #EADECE; margin:1rem 0;'>", unsafe_allow_html=True)

    # 1. 疊石頭
    if st.session_state.sub_tab == "zen_stones":
        stone_options = [
            {"name": "🪨 安定大地基石", "color": "#7D6B58", "width": "190px", "height": "42px", "quote": "「立足於當下，大地會穩穩托住你的每一次疲憊。」"},
            {"name": "💎 澄澈水晶靈石", "color": "#8C9EA8", "width": "160px", "height": "38px", "quote": "「如水般清澈，看清盲點，允許情緒自然流過。」"},
            {"name": "🌊 圓融河畔卵石", "color": "#A38F7A", "width": "130px", "height": "34px", "quote": "「流水磨去了尖銳，也留下了最溫潤柔軟的自己。」"},
            {"name": "🌸 慈悲粉櫻心石", "color": "#C49A9E", "width": "100px", "height": "30px", "quote": "「對自己溫柔一點，你值得世間最純粹的善待。」"},
            {"name": "🌿 復原青苔石", "color": "#768B6E", "width": "75px", "height": "26px", "quote": "「即便在石縫之中，生命依然能開出堅韌的綠意。」"}
        ]
        c_z1, c_z2 = st.columns([1, 1])
        with c_z1:
            st.markdown("<h4 style='color:#533E2D;'>🪵 挑選一塊石頭疊上心靈塔：</h4>", unsafe_allow_html=True)
            for s_idx, s in enumerate(stone_options):
                if st.button(f"{s['name']}", key=f"btn_add_stone_{s_idx}", use_container_width=True):
                    st.session_state.zen_stones.append(s)
                    st.rerun()
            if len(st.session_state.zen_stones) > 0:
                if st.button("🧹 推倒重來・清空雜念", key="btn_clear_stones", use_container_width=True):
                    st.session_state.zen_stones = []
                    st.rerun()
        with c_z2:
            st.markdown(f"<div style='text-align:center; font-weight:700; color:#533E2D;'>🌟 目前心靈塔高度：{len(st.session_state.zen_stones)} 層</div>", unsafe_allow_html=True)
            tower_html = '<div class="zen-tower-container" style="display:flex; flex-direction:column-reverse; align-items:center; min-height:260px; padding:1.5rem 0; border-bottom:4px solid #B5A290; max-width:400px; margin:0 auto;">'
            if len(st.session_state.zen_stones) == 0:
                tower_html += '<div style="color:#A89481; font-style:italic; padding-top:4rem;">點擊左側石頭，開始堆疊你的心靈之塔...</div>'
            else:
                for st_item in st.session_state.zen_stones:
                    tower_html += f'<div style="background:{st_item["color"]}; width:{st_item["width"]}; height:{st_item["height"]}; border-radius:24px; margin:2px auto; box-shadow:0 3px 8px rgba(0,0,0,0.15); border:2px solid rgba(255,255,255,0.4); animation:msg-fade-in 0.3s ease;"></div>'
            tower_html += '</div>'
            st.markdown(tower_html, unsafe_allow_html=True)
            if len(st.session_state.zen_stones) > 0:
                st.markdown(f'<div style="background:#FFFFFF; border-radius:14px; padding:1rem; border:1px solid #EADECE; margin-top:1rem; text-align:center; color:#5C4A38; font-weight:600;">✨ {st.session_state.zen_stones[-1]["quote"]}</div>', unsafe_allow_html=True)

    # 2. ASMR 3D 水晶泡泡紙
    elif st.session_state.sub_tab == "bubbles":
        st.markdown("""
<div style="text-align:center; max-width:680px; margin:0 auto 0.8rem;">
    <h3 style="color:#533E2D; font-size:1.35rem; font-weight:700; margin-bottom:0.2rem;">🫧 ASMR 心理學減壓泡泡紙・捏爆焦慮</h3>
    <p style="color:#8C735A; font-size:0.88rem; line-height:1.5;">
        擬真 3D 水晶氣泡質感與 <strong>Web Audio 原生清脆爆破音效</strong>。<br>
        隨心所欲快速點擊捏破，即時釋放掌心與大腦的緊繃壓力！
    </p>
</div>
""", unsafe_allow_html=True)

        bubble_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@500;600;700&family=Quicksand:wght@600;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
body { background: transparent; font-family: 'Noto Sans TC', 'Quicksand', sans-serif; color: #4A3B2C; display: flex; justify-content: center; align-items: center; padding: 10px; }
.bubble-sheet-container { background: #FFFFFF; border: 2px solid #EADECE; border-radius: 24px; padding: 1.5rem 1.8rem; box-shadow: 0 10px 30px rgba(83,62,45,0.06); max-width: 480px; width: 100%; text-align: center; }
.bubble-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 1.2rem auto; max-width: 360px; justify-items: center; }
.bubble-item { width: 68px; height: 68px; border-radius: 50%; position: relative; cursor: pointer; background: radial-gradient(circle at 35% 30%, #FFFFFF 0%, #E6F3EB 45%, #C2E2D0 80%, #9BC4AD 100%); box-shadow: inset 0 -4px 8px rgba(0,0,0,0.12), inset 0 3px 6px rgba(255,255,255,0.9), 0 6px 14px rgba(135,178,154,0.3); border: 1.5px solid rgba(255,255,255,0.8); transition: transform 0.12s cubic-bezier(0.175, 0.885, 0.32, 1.275); display: flex; align-items: center; justify-content: center; }
.bubble-item:hover { transform: scale(1.08); }
.bubble-item:active { transform: scale(0.92); }
.bubble-item::after { content: ''; position: absolute; top: 10px; left: 14px; width: 18px; height: 10px; border-radius: 50%; background: rgba(255,255,255,0.85); transform: rotate(-35deg); }
.bubble-item.popped { background: #EDE8E1; box-shadow: inset 0 3px 8px rgba(0,0,0,0.14); border-color: #D9CFC4; transform: scale(0.88); cursor: default; }
.bubble-item.popped::after { display: none; }
.bubble-item.popped::before { content: '💨'; font-size: 1.2rem; opacity: 0.45; }
.counter-bar { font-size: 1rem; font-weight: 700; color: #533E2D; margin-top: 0.8rem; }
.reset-btn { background: #C2995F; color: white; border: none; padding: 8px 22px; border-radius: 18px; font-weight: 700; font-size: 0.9rem; cursor: pointer; margin-top: 1rem; box-shadow: 0 4px 12px rgba(194, 153, 95, 0.25); transition: all 0.2s ease; }
.reset-btn:hover { background: #AA8249; transform: translateY(-2px); }
</style>
</head>
<body>
<div class="bubble-sheet-container">
    <div class="counter-bar" id="status-text">✨ 點擊泡泡・已捏破 <span id="popped-count" style="color:#C2995F; font-size:1.25rem;">0</span> / 16 顆</div>
    <div class="bubble-grid" id="grid"></div>
    <button class="reset-btn" onclick="resetBubbles()">🔄 重新鋪滿全新泡泡紙</button>
</div>
<script>
let audioCtx = null;
function getAudioCtx() { if (!audioCtx) { audioCtx = new (window.AudioContext || window.webkitAudioContext)(); } if (audioCtx.state === 'suspended') { audioCtx.resume(); } return audioCtx; }
function playPopSound() {
    const ctx = getAudioCtx();
    const now = ctx.currentTime;
    const baseFreq = 650 + Math.random() * 300;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(baseFreq, now);
    osc.frequency.exponentialRampToValueAtTime(120, now + 0.08);
    gain.gain.setValueAtTime(0.7, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.08);
}
function playCelebrationSound() {
    const ctx = getAudioCtx();
    const notes = [523.25, 659.25, 783.99, 1046.5];
    notes.forEach((freq, idx) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const now = ctx.currentTime + idx * 0.12;
        osc.type = 'sine';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.4, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.5);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.5);
    });
}
let poppedCount = 0;
const total = 16;
function renderGrid() {
    const grid = document.getElementById('grid');
    grid.innerHTML = '';
    poppedCount = 0;
    document.getElementById('popped-count').innerText = '0';
    document.getElementById('status-text').innerHTML = '✨ 點擊泡泡・已捏破 <span id="popped-count" style="color:#C2995F; font-size:1.25rem;">0</span> / 16 顆';
    for (let i = 0; i < total; i++) {
        const bubble = document.createElement('div');
        bubble.className = 'bubble-item';
        bubble.onclick = function() {
            if (!bubble.classList.contains('popped')) {
                playPopSound();
                bubble.classList.add('popped');
                poppedCount++;
                document.getElementById('popped-count').innerText = poppedCount;
                if (poppedCount === total) {
                    playCelebrationSound();
                    document.getElementById('status-text').innerHTML = '🎉 <strong style="color:#C2995F; font-size:1.2rem;">太棒了！焦慮已全部歸零！</strong>';
                }
            }
        };
        grid.appendChild(bubble);
    }
}
function resetBubbles() { renderGrid(); }
renderGrid();
</script>
</body>
</html>
"""
        import streamlit.components.v1 as components
        components.html(bubble_html, height=450, scrolling=False)

    # 3. 煩惱粉碎機
    elif st.session_state.sub_tab == "shredder":
        current_companion = ANIMAL_COMPANIONS[st.session_state.selected_companion]
        trouble_input = st.text_input("輸入你想粉碎的煩惱或自責字句：", placeholder="例如：拖延自責、不被理解的委屈...", key="trouble_text")
        if st.button("💥 徹底粉碎這個煩惱！", key="btn_shred"):
            if trouble_input.strip():
                st.session_state.shredded_troubles.insert(0, {
                    "trouble": trouble_input.strip(),
                    "companion": current_companion["name"],
                    "action": "施展超萌心靈魔法，將沉重壓力徹底戳破成滿天星斗！✨",
                    "quote": "「這個煩惱已經離開你了！你比自己想像的更堅強有力量。」",
                    "time": time.strftime("%H:%M")
                })
                st.balloons()
                st.rerun()
        if st.session_state.shredded_troubles:
            st.markdown("<h5 style='color:#533E2D; margin-top:1rem;'>✨ 已粉碎的心靈負擔紀錄：</h5>", unsafe_allow_html=True)
            for item in st.session_state.shredded_troubles[:4]:
                st.markdown(f'<div style="background:#F5EDE4; border-radius:15px; padding:1rem; margin:0.6rem 0; border-left:4px solid #C2995F; color:#5C4A38;"><div style="font-size:0.8rem; color:#8C735A;">⏱️ {item["time"]} 由 {item["companion"]} 粉碎</div><div style="font-size:0.95rem; text-decoration:line-through; color:#9E8774;">❌ 「{item["trouble"]}」</div><div style="font-size:0.85rem; color:#8C653C; margin-top:0.3rem;">💡 {item["quote"]}</div></div>', unsafe_allow_html=True)

    # 4. 心靈幸運籤
    elif st.session_state.sub_tab == "fortune":
        current_companion = ANIMAL_COMPANIONS[st.session_state.selected_companion]
        if st.button("🥠 敲開今日心靈幸運餅乾", key="btn_draw_fortune", use_container_width=True):
            FORTUNES = [
                {"quote": "「允許自己偶爾是一座荒蕪的花園，雨季過後，花朵自然會重新綻放。」", "task": "🌱 今日微任務：給自己泡一杯溫暖的花草茶，安靜喝完它。"},
                {"quote": "「你不需要向世界證明你有多堅強，你的存在本身就充滿價值。」", "task": "💖 今日微任務：對著鏡子裡的自己微笑一下，輕聲說一聲：『你辛苦了』。"},
                {"quote": "「焦慮常常是在為尚未發生的事情提前預支痛苦。回到此時此刻，你很安全。」", "task": "🌿 今日微任務：深呼吸 3 次，感受雙腳踏在地面上的穩穩力量。"},
                {"quote": "「設立界線不是自私，而是愛護自己心靈能量的成熟表現。」", "task": "🛡️ 今日微任務：溫柔地對一件讓你不舒服的請求說『我需要先考慮一下』。"}
            ]
            st.session_state.fortune_result = random.choice(FORTUNES)
        if st.session_state.fortune_result:
            res = st.session_state.fortune_result
            st.markdown(f'<div style="background:#FFFFFF; border:2px dashed #C2995F; border-radius:20px; padding:1.5rem; text-align:center; box-shadow:0 8px 24px rgba(83,62,45,0.06); max-width:500px; margin:1rem auto;"><div style="font-size:2rem;">✨ 🥠 ✨</div><div style="font-size:1.05rem; font-weight:600; color:#533E2D; margin:0.8rem 0; line-height:1.7;">{res["quote"]}</div><div style="background:#FAF6F0; border-radius:12px; padding:0.8rem; font-size:0.85rem; color:#8C735A; line-height:1.6;">{res["task"]}</div><div style="margin-top:0.8rem; font-size:0.8rem; color:#8C735A;">— {current_companion["name"]} 守護祝福</div></div>', unsafe_allow_html=True)

    # 5. 54321著陸法
    elif st.session_state.sub_tab == "grounding":
        current_companion = ANIMAL_COMPANIONS[st.session_state.selected_companion]
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("""
<div style="background:#FFFFFF; border-radius:16px; padding:1.2rem; border:1.5px solid #EADECE; margin-bottom:1rem;">
    <h4 style="color:#533E2D; margin:0 0 0.4rem;">👀 5 件眼睛看得到的東西</h4>
    <p style="font-size:0.85rem; color:#7D6B58; margin:0;">環顧周圍，找出 5 個不同顏色或形狀的物品（如：時鐘、桌角、植物...）</p>
</div>
<div style="background:#FFFFFF; border-radius:16px; padding:1.2rem; border:1.5px solid #EADECE; margin-bottom:1rem;">
    <h4 style="color:#533E2D; margin:0 0 0.4rem;">✋ 4 件身體摸得到的觸感</h4>
    <p style="font-size:0.85rem; color:#7D6B58; margin:0;">摸摸身上的衣服質料、光滑的桌面、手邊冰涼的杯子或椅子的靠背...</p>
</div>
<div style="background:#FFFFFF; border-radius:16px; padding:1.2rem; border:1.5px solid #EADECE;">
    <h4 style="color:#533E2D; margin:0 0 0.4rem;">👂 3 種耳朵聽到的聲音</h4>
    <p style="font-size:0.85rem; color:#7D6B58; margin:0;">靜下心聆聽：電風扇微弱的風聲、遠處的車聲、或是自己的平穩呼吸聲...</p>
</div>
""", unsafe_allow_html=True)
        with g2:
            st.markdown("""
<div style="background:#FFFFFF; border-radius:16px; padding:1.2rem; border:1.5px solid #EADECE; margin-bottom:1rem;">
    <h4 style="color:#533E2D; margin:0 0 0.4rem;">👃 2 種鼻子聞得到或喜歡的氣味</h4>
    <p style="font-size:0.85rem; color:#7D6B58; margin:0;">嗅一嗅空氣中的咖啡香、洗手乳的清香、或是回想雨後青草的芬芳...</p>
</div>
<div style="background:#FFFFFF; border-radius:16px; padding:1.2rem; border:1.5px solid #EADECE; margin-bottom:1rem;">
    <h4 style="color:#533E2D; margin:0 0 0.4rem;">👅 1 個舌尖的味覺或對自己的肯定</h4>
    <p style="font-size:0.85rem; color:#7D6B58; margin:0;">喝一小口水感受清涼，並在心中對自己說：『我現在很安全，一切都會好起來的。』</p>
</div>
""", unsafe_allow_html=True)
            if st.button("🌱 我已完成著陸練習，感覺放鬆多了", key="btn_done_grounding", use_container_width=True):
                st.success(f"{current_companion['emoji']} {current_companion['name']} 給你一個大大的掌聲！你做得非常棒！")

# ==============================================================================

with tab_garden:
    st.markdown("""
<div style="text-align:center; max-width:680px; margin:0 auto 1.2rem;">
    <h2 style="color:#533E2D; font-size:1.5rem; font-weight:700; margin-bottom:0.3rem;">🌿 身心療癒花園・深層修復專區</h2>
    <p style="color:#8C735A; font-size:0.92rem; line-height:1.5;">培養感恩心靈盆栽、聆聽大自然多軌白噪音、定格拍立得小卡、擁抱內在小孩。</p>
</div>
""", unsafe_allow_html=True)

    g_col1, g_col2, g_col3, g_col4, g_col5, g_col6 = st.columns(6)
    with g_col1:
        if st.button("🌱 感恩盆栽", key="g_tab_plant", use_container_width=True):
            st.session_state.sub_tab = "gratitude"
            st.rerun()
    with g_col2:
        if st.button("🎵 音療混音館", key="g_tab_ambient", use_container_width=True):
            st.session_state.sub_tab = "ambient"
            st.rerun()
    with g_col3:
        if st.button("🌬️ 正念呼吸", key="g_tab_breath", use_container_width=True):
            st.session_state.sub_tab = "breath"
            st.rerun()
    with g_col4:
        if st.button("🧸 內在小孩", key="g_tab_inner", use_container_width=True):
            st.session_state.sub_tab = "inner_child"
            st.rerun()
    with g_col5:
        if st.button("💌 時空膠囊", key="g_tab_capsule", use_container_width=True):
            st.session_state.sub_tab = "time_capsule"
            st.rerun()
    with g_col6:
        if st.button("🖼️ 拍立得卡", key="g_tab_polaroid", use_container_width=True):
            st.session_state.sub_tab = "polaroid"
            st.rerun()

    st.markdown("<hr style='border:none; border-top:1px solid #EADECE; margin:1rem 0;'>", unsafe_allow_html=True)

    # 1. 感恩盆栽
    if st.session_state.sub_tab == "gratitude":
        grat_logs = db.load_gratitude_logs(CURRENT_USER_ID)
        sunshine = min(200, 30 + len(grat_logs) * 25)
        stage_name = "🌸 繁花盛開的心靈之樹" if sunshine >= 140 else "🌿 繁茂舒展的翠綠小樹" if sunshine >= 90 else "🌱 破土萌芽的嫩苗"
        
        p_col1, p_col2 = st.columns([1, 1])
        with p_col1:
            st.markdown(f"""
<div style="background:#FFFFFF; border:2px solid #EADECE; border-radius:20px; padding:1.5rem; text-align:center;">
    <div style="font-size:3.5rem; margin-bottom:0.5rem;">🌱 🌳 🌸</div>
    <h3 style="color:#533E2D; margin:0 0 0.3rem;">{stage_name}</h3>
    <div style="font-weight:700; color:#C2995F; margin:0.6rem 0;">☀️ 陽光成長值：{sunshine} / 200</div>
</div>
""", unsafe_allow_html=True)
            st.progress(min(sunshine / 200.0, 1.0))
        with p_col2:
            st.markdown("<h4 style='color:#533E2D;'>💧 記錄微小心情，為盆栽澆水：</h4>", unsafe_allow_html=True)
            grat_input = st.text_input("寫下一件今天值得感謝的事或肯定自己的小細節：", placeholder="例如：今天喝了一杯好喝的咖啡...", key="grat_box_g")
            if st.button("🌱 灌溉心靈植物 (+25 陽光值)", key="btn_water_g"):
                if grat_input.strip():
                    db.save_gratitude_log(CURRENT_USER_ID, grat_input.strip())
                    db.add_star_coins(CURRENT_USER_ID, 15)
                    st.balloons()
                    st.success("紀錄已永久存入心靈成長資料庫！獲得 +15 🌟星光幣！")
                    st.rerun()

    # 2. 白噪音音療 (Web Audio 混音館 - 660px 完整無裁切版)
    elif st.session_state.sub_tab == "ambient":
        studio_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700&family=Quicksand:wght@600;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
body { background: transparent; font-family: 'Noto Sans TC', 'Quicksand', sans-serif; color: #4A3B2C; padding: 10px; }
.studio-card { background: #FFFFFF; border: 2px solid #EADECE; border-radius: 22px; padding: 1.5rem 1.6rem; box-shadow: 0 8px 24px rgba(83,62,45,0.06); max-width: 820px; margin: 0 auto; }
.preset-bar { display: flex; gap: 8px; justify-content: center; margin-bottom: 1.3rem; flex-wrap: wrap; }
.preset-btn { background: #F8F3EC; border: 1.5px solid #DFCDBD; padding: 6px 14px; border-radius: 16px; font-size: 0.82rem; font-weight: 600; color: #5A432D; cursor: pointer; transition: all 0.2s ease; }
.preset-btn:hover { background: #C2995F; color: white; border-color: #C2995F; transform: translateY(-2px); }
.preset-btn.stop { background: #FCEEEC; border-color: #E8B4B4; color: #A84242; }
.preset-btn.stop:hover { background: #E05252; color: white; border-color: #E05252; }
.track-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 1.3rem; }
@media (max-width: 650px) { .track-grid { grid-template-columns: repeat(2, 1fr); } }
.track-card { background: #FAF6F0; border: 1.5px solid #E8DCCE; border-radius: 16px; padding: 1rem 0.9rem; text-align: center; transition: all 0.2s ease; }
.track-card.active { background: #F5EDE2; border-color: #C2995F; box-shadow: 0 4px 14px rgba(194, 153, 95, 0.18); }
.track-icon { font-size: 1.9rem; margin-bottom: 0.2rem; }
.track-name { font-size: 0.95rem; font-weight: 700; color: #533E2D; margin-bottom: 0.2rem; }
.track-desc { font-size: 0.74rem; color: #8C735A; margin-bottom: 0.7rem; min-height: 24px; }
.track-toggle { background: #E8DCCF; border: none; padding: 6px 14px; border-radius: 12px; font-weight: 600; font-size: 0.82rem; color: #5C4632; cursor: pointer; transition: all 0.2s ease; width: 100%; margin-bottom: 0.6rem; }
.track-toggle.on { background: #C2995F; color: white; }
.vol-slider { width: 100%; accent-color: #C2995F; cursor: pointer; }
.master-bar { display: flex; justify-content: space-between; align-items: center; background: #F6EEE3; padding: 0.9rem 1.4rem; border-radius: 14px; border: 1px solid #E2D3C2; flex-wrap: wrap; gap: 10px; }
.timer-select { background: #FFFFFF; border: 1px solid #DFCDBD; padding: 6px 12px; border-radius: 12px; font-size: 0.85rem; color: #533E2D; outline: none; }
</style>
</head>
<body>
<div class="studio-card">
    <div style="text-align:center; font-weight:700; font-size:0.85rem; color:#8C735A; margin-bottom:0.6rem;">🎯 大師級一鍵情境混音預設：</div>
    <div class="preset-bar">
        <button class="preset-btn" onclick="applyPreset('sleep')">🛌 深度助眠 (雨聲+柴火+頌缽)</button>
        <button class="preset-btn" onclick="applyPreset('zen')">🧘 432Hz 冥想 (海浪+頌缽)</button>
        <button class="preset-btn" onclick="applyPreset('flow')">☕ 專注心流 (微風+春雨)</button>
        <button class="preset-btn" onclick="applyPreset('cat')">🐱 焦慮平息 (呼嚕+柴火)</button>
        <button class="preset-btn stop" onclick="stopAll()">🛑 一鍵全靜音</button>
    </div>
    <div class="track-grid">
        <div class="track-card" id="card-rain">
            <div class="track-icon">🌧️</div>
            <div class="track-name">溫柔春雨</div>
            <div class="track-desc">粉紅噪音濾波・隨機自然雨滴聲</div>
            <button class="track-toggle" id="btn-rain" onclick="toggleTrack('rain')">開啟</button>
            <input type="range" class="vol-slider" id="vol-rain" min="0" max="100" value="50" oninput="changeVol('rain', this.value)">
        </div>
        <div class="track-card" id="card-ocean">
            <div class="track-icon">🌊</div>
            <div class="track-name">潮汐海浪</div>
            <div class="track-desc">超低頻LFO調製・自然潮起潮落</div>
            <button class="track-toggle" id="btn-ocean" onclick="toggleTrack('ocean')">開啟</button>
            <input type="range" class="vol-slider" id="vol-ocean" min="0" max="100" value="50" oninput="changeVol('ocean', this.value)">
        </div>
        <div class="track-card" id="card-fire">
            <div class="track-icon">🔥</div>
            <div class="track-name">壁爐柴火</div>
            <div class="track-desc">劈啪木柴燃燒・安全溫暖避風港</div>
            <button class="track-toggle" id="btn-fire" onclick="toggleTrack('fire')">開啟</button>
            <input type="range" class="vol-slider" id="vol-fire" min="0" max="100" value="40" oninput="changeVol('fire', this.value)">
        </div>
        <div class="track-card" id="card-wind">
            <div class="track-icon">🌲</div>
            <div class="track-name">森林微風</div>
            <div class="track-desc">動態樹梢風聲・帶走思緒雜質</div>
            <button class="track-toggle" id="btn-wind" onclick="toggleTrack('wind')">開啟</button>
            <input type="range" class="vol-slider" id="vol-wind" min="0" max="100" value="35" oninput="changeVol('wind', this.value)">
        </div>
        <div class="track-card" id="card-bowl">
            <div class="track-icon">🔔</div>
            <div class="track-name">432Hz 頌缽</div>
            <div class="track-desc">宇宙自然療癒諧振・深度放鬆腦波</div>
            <button class="track-toggle" id="btn-bowl" onclick="toggleTrack('bowl')">開啟</button>
            <input type="range" class="vol-slider" id="vol-bowl" min="0" max="100" value="45" oninput="changeVol('bowl', this.value)">
        </div>
        <div class="track-card" id="card-purr">
            <div class="track-icon">🐱</div>
            <div class="track-name">貓咪呼嚕</div>
            <div class="track-desc">28Hz 療癒低頻・如同貓咪依偎身邊</div>
            <button class="track-toggle" id="btn-purr" onclick="toggleTrack('purr')">開啟</button>
            <input type="range" class="vol-slider" id="vol-purr" min="0" max="100" value="55" oninput="changeVol('purr', this.value)">
        </div>
    </div>
    <div class="master-bar">
        <div style="font-size:0.88rem; font-weight:600; color:#533E2D;">
            ⏱️ 舒眠倒數定時器：
            <select class="timer-select" id="timer-select" onchange="setSleepTimer(this.value)">
                <option value="0">持續播放 (無限制)</option>
                <option value="15">15 分鐘後停止</option>
                <option value="30">30 分鐘後停止</option>
                <option value="45">45 分鐘後停止</option>
                <option value="60">60 分鐘後停止</option>
            </select>
        </div>
        <div style="font-size:0.85rem; color:#8C735A;" id="timer-status">✨ 原生 Web Audio 聲學合成・零延遲</div>
    </div>
</div>
<script>
let audioCtx = null;
const tracks = { rain: { on: false, gain: null, nodes: [] }, ocean: { on: false, gain: null, nodes: [] }, fire: { on: false, gain: null, nodes: [] }, wind: { on: false, gain: null, nodes: [] }, bowl: { on: false, gain: null, nodes: [] }, purr: { on: false, gain: null, nodes: [] } };
let sleepTimerId = null;
function getAudioCtx() { if (!audioCtx) { audioCtx = new (window.AudioContext || window.webkitAudioContext)(); } if (audioCtx.state === 'suspended') { audioCtx.resume(); } return audioCtx; }
function createNoiseBuffer(ctx, duration = 4) { const bufferSize = ctx.sampleRate * duration; const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate); const data = buffer.getChannelData(0); for (let i = 0; i < bufferSize; i++) { data[i] = Math.random() * 2 - 1; } return buffer; }
function startRain(ctx, masterGain) { const src = ctx.createBufferSource(); src.buffer = createNoiseBuffer(ctx, 4); src.loop = true; const f1 = ctx.createBiquadFilter(); f1.type = 'bandpass'; f1.frequency.value = 1000; const f2 = ctx.createBiquadFilter(); f2.type = 'lowpass'; f2.frequency.value = 3500; src.connect(f1); f1.connect(f2); f2.connect(masterGain); src.start(); return [src, f1, f2]; }
function startOcean(ctx, masterGain) { const src = ctx.createBufferSource(); src.buffer = createNoiseBuffer(ctx, 5); src.loop = true; const filter = ctx.createBiquadFilter(); filter.type = 'lowpass'; filter.frequency.value = 450; const lfo = ctx.createOscillator(); lfo.frequency.value = 0.09; const lfoGain = ctx.createGain(); lfoGain.gain.value = 0.45; const waveGain = ctx.createGain(); waveGain.gain.value = 0.55; lfo.connect(lfoGain); lfoGain.connect(waveGain.gain); src.connect(filter); filter.connect(waveGain); waveGain.connect(masterGain); src.start(); lfo.start(); return [src, filter, lfo, lfoGain, waveGain]; }
function startFire(ctx, masterGain) { const src = ctx.createBufferSource(); src.buffer = createNoiseBuffer(ctx, 3); src.loop = true; const filter = ctx.createBiquadFilter(); filter.type = 'bandpass'; filter.frequency.value = 650; src.connect(filter); filter.connect(masterGain); src.start(); return [src, filter]; }
function startWind(ctx, masterGain) { const src = ctx.createBufferSource(); src.buffer = createNoiseBuffer(ctx, 4); src.loop = true; const filter = ctx.createBiquadFilter(); filter.type = 'lowpass'; filter.frequency.value = 320; const lfo = ctx.createOscillator(); lfo.frequency.value = 0.2; const lfoGain = ctx.createGain(); lfoGain.gain.value = 120; lfo.connect(lfoGain); lfoGain.connect(filter.frequency); src.connect(filter); filter.connect(masterGain); src.start(); lfo.start(); return [src, filter, lfo, lfoGain]; }
function startBowl(ctx, masterGain) { const osc1 = ctx.createOscillator(); osc1.type = 'sine'; osc1.frequency.value = 432; const osc2 = ctx.createOscillator(); osc2.type = 'sine'; osc2.frequency.value = 864; const g2 = ctx.createGain(); g2.gain.value = 0.25; osc1.connect(masterGain); osc2.connect(g2); g2.connect(masterGain); osc1.start(); osc2.start(); return [osc1, osc2, g2]; }
function startPurr(ctx, masterGain) { const osc = ctx.createOscillator(); osc.type = 'triangle'; osc.frequency.value = 28; const mod = ctx.createOscillator(); mod.frequency.value = 4.2; const modGain = ctx.createGain(); modGain.gain.value = 0.6; const purrGain = ctx.createGain(); purrGain.gain.value = 0.5; mod.connect(modGain); modGain.connect(purrGain.gain); osc.connect(purrGain); purrGain.connect(masterGain); osc.start(); mod.start(); return [osc, mod, modGain, purrGain]; }
function toggleTrack(name) { const ctx = getAudioCtx(); const t = tracks[name]; const btn = document.getElementById(`btn-${name}`); const card = document.getElementById(`card-${name}`); const slider = document.getElementById(`vol-${name}`); if (t.on) { t.nodes.forEach(n => { try { n.stop(); } catch(e){} try { n.disconnect(); } catch(e){} }); t.nodes = []; t.on = false; btn.innerText = "開啟"; btn.classList.remove("on"); card.classList.remove("active"); } else { if (!t.gain) { t.gain = ctx.createGain(); t.gain.connect(ctx.destination); } t.gain.gain.setValueAtTime(slider.value / 100, ctx.currentTime); if (name === 'rain') t.nodes = startRain(ctx, t.gain); else if (name === 'ocean') t.nodes = startOcean(ctx, t.gain); else if (name === 'fire') t.nodes = startFire(ctx, t.gain); else if (name === 'wind') t.nodes = startWind(ctx, t.gain); else if (name === 'bowl') t.nodes = startBowl(ctx, t.gain); else if (name === 'purr') t.nodes = startPurr(ctx, t.gain); t.on = true; btn.innerText = "播放中 ⏸"; btn.classList.add("on"); card.classList.add("active"); } }
function changeVol(name, val) { const ctx = getAudioCtx(); const t = tracks[name]; if (t.gain) { t.gain.gain.setValueAtTime(val / 100, ctx.currentTime); } }
function applyPreset(type) { stopAll(); setTimeout(() => { if (type === 'sleep') { document.getElementById('vol-rain').value = 60; document.getElementById('vol-fire').value = 35; document.getElementById('vol-bowl').value = 25; toggleTrack('rain'); toggleTrack('fire'); toggleTrack('bowl'); } else if (type === 'zen') { document.getElementById('vol-ocean').value = 65; document.getElementById('vol-bowl').value = 45; toggleTrack('ocean'); toggleTrack('bowl'); } else if (type === 'flow') { document.getElementById('vol-wind').value = 45; document.getElementById('vol-rain').value = 40; toggleTrack('wind'); toggleTrack('rain'); } else if (type === 'cat') { document.getElementById('vol-purr').value = 65; document.getElementById('vol-fire').value = 35; toggleTrack('purr'); toggleTrack('fire'); } }, 50); }
function stopAll() { Object.keys(tracks).forEach(name => { if (tracks[name].on) { toggleTrack(name); } }); }
function setSleepTimer(mins) { if (sleepTimerId) clearTimeout(sleepTimerId); const status = document.getElementById('timer-status'); const m = parseInt(mins); if (m === 0) { status.innerText = "✨ 原生 Web Audio 聲學合成・零延遲"; } else { status.innerText = `⏳ 倒數定時器：將在 ${m} 分鐘後自動靜音`; sleepTimerId = setTimeout(() => { stopAll(); status.innerText = "💤 舒眠定時結束，已自動靜音～祝您好夢"; }, m * 60 * 1000); } }
</script>
</body>
</html>
"""
        import streamlit.components.v1 as components
        components.html(studio_html, height=660, scrolling=False)

    # 3. 正念呼吸
    elif st.session_state.sub_tab == "breath":
        st.markdown("""
<div class="breathing-circle-container" style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:2rem 1rem;">
    <div class="breath-circle" style="width:180px; height:180px; border-radius:50%; background:radial-gradient(circle, #D8EAD9 0%, #A3C9A8 100%); box-shadow:0 0 40px rgba(163,201,168,0.6); display:flex; align-items:center; justify-content:center; color:#2F5233; font-weight:700; font-size:1.25rem;">放鬆呼吸</div>
    <div style="margin-top:1.5rem; display:flex; gap:15px; justify-content:center; font-size:0.85rem; color:#5A432D; font-weight:500;">
        <span style="background:#E2EFE3; padding:4px 12px; border-radius:12px;">🟢 吸氣 (4秒)</span>
        <span style="background:#EBF2EA; padding:4px 12px; border-radius:12px;">🟡 屏息 (4秒)</span>
        <span style="background:#F7EDE6; padding:4px 12px; border-radius:12px;">🟠 吐氣 (4秒)</span>
        <span style="background:#F2EBE5; padding:4px 12px; border-radius:12px;">⚪ 靜止 (4秒)</span>
    </div>
</div>
""", unsafe_allow_html=True)

    # 4. 內在小孩
    elif st.session_state.sub_tab == "inner_child":
        current_companion = ANIMAL_COMPANIONS[st.session_state.selected_companion]
        child_msg = st.text_input("你想對心中那個受委屈、努力長大的小自己說什麼？", placeholder="例如：辛苦你了，你不需要永遠那麼懂事，我會一直保護你...", key="inner_child_text_g")
        if st.button("💖 送出溫柔擁抱", key="btn_send_hug_g"):
            if child_msg.strip():
                st.session_state.inner_child_reflection = {
                    "user_msg": child_msg.strip(),
                    "companion_hug": f"「看見你溫柔地擁抱內在的自己，{current_companion['name']} 也好感動……你的內在小孩終於等到了這份最珍貴的愛。」"
                }
                st.balloons()
        if st.session_state.inner_child_reflection:
            ref = st.session_state.inner_child_reflection
            st.markdown(f'<div style="background:#FFFFFF; border:2px solid #EADECE; border-radius:18px; padding:1.5rem; margin-top:1rem;"><div style="color:#5C4A38; font-style:italic;">💌 你對內在小孩說：「{ref["user_msg"]}」</div><div style="font-size:1rem; color:#533E2D; margin-top:0.8rem; font-weight:600;">{current_companion["name"]} 回應：<br><span style="font-weight:400; color:#5C4A38;">{ref["companion_hug"]}</span></div></div>', unsafe_allow_html=True)

    # 5. 時空膠囊
    elif st.session_state.sub_tab == "time_capsule":
        current_companion = ANIMAL_COMPANIONS[st.session_state.selected_companion]
        col_t1, col_t2 = st.columns([1, 1])
        with col_t1:
            capsule_target = st.selectbox("這封信是寫給誰的：", ["寫給 1 個月後的自己", "寫給未來的自己", "寫給受委屈時的自己", "寫給童年的內在小孩"])
            capsule_content = st.text_area("信件內容：", placeholder="親愛的自己，當你讀到這封信的時候...", height=120)
            if st.button("🔒 封存進時空膠囊", key="btn_save_capsule_g"):
                if capsule_content.strip():
                    db.save_time_capsule(CURRENT_USER_ID, capsule_target, capsule_content.strip(), current_companion["name"])
                    st.balloons()
                    st.success("信件已安全封存進資料庫！")
                    st.rerun()
        with col_t2:
            st.markdown("<h4 style='color:#533E2D;'>📮 已封存的時空膠囊：</h4>", unsafe_allow_html=True)
            capsules = db.load_time_capsules(CURRENT_USER_ID)
            for cap in capsules[:4]:
                with st.expander(f"💌 {cap['to']}（{cap['date']} 由 {cap['guardian']} 封印）"):
                    st.markdown(f"<div style='font-size:0.9rem; color:#5C4A38; line-height:1.7;'>{cap['content']}</div>", unsafe_allow_html=True)

    # 6. 拍立得小卡
    elif st.session_state.sub_tab == "polaroid":
        current_companion = ANIMAL_COMPANIONS[st.session_state.selected_companion]
        card_text = st.text_area("編輯小卡金句：", value=current_companion["motto"], height=90)
        card_user_note = st.text_input("寫下一句備註：", value="今天也辛苦了，謝謝一直努力的自己。")
        today_str = time.strftime("%Y.%m.%d")
        polaroid_html = f'<div style="background:#FFFFFF; padding:1.3rem 1.3rem 2.2rem; border-radius:6px; box-shadow:0 12px 36px rgba(83,62,45,0.16); max-width:440px; margin:1.5rem auto; border:1px solid #EDE0CE; text-align:center;"><div style="background:#FAF6F0; border-radius:4px; padding:1.5rem; border:1px solid #EADBCE; display:flex; flex-direction:column; align-items:center; justify-content:center;"><img src="{current_companion["avatar_uri"]}" style="width:70px; height:70px; border-radius:50%; margin-bottom:0.8rem;" /><div style="font-size:0.95rem; color:#4A3B2C; line-height:1.7; font-weight:500;">"{card_text}"</div><div style="font-size:0.8rem; color:#8C735A; margin-top:0.6rem;">— {current_companion["name"]} 陪伴守護</div></div><div style="margin-top:1.2rem; font-size:0.85rem; color:#6E5C49;">💌 {card_user_note}<br><span style="font-size:0.75rem; color:#A89481;">{today_str}・動物心靈諮商室</span></div></div>'
        st.markdown(polaroid_html, unsafe_allow_html=True)

# ==============================================================================

with tab_vip:
    st.markdown("""
<div style="text-align:center; max-width:680px; margin:0 auto 1.5rem;">
    <h2 style="color:#533E2D; font-size:1.5rem; font-weight:700; margin-bottom:0.4rem;">📊 每週 AI 心靈體檢週報 & VIP 尊榮守護</h2>
    <p style="color:#8C735A; font-size:0.92rem; line-height:1.6;">由動物心理師團隊為你生成的專屬情緒深度分析週報與商業級 VIP 方案特權。</p>
</div>
""", unsafe_allow_html=True)

    with st.expander("📈 點此查看本週【AI 深度情緒健康體檢週報】", expanded=True):
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            st.markdown("""
<div style="background:#FAF6F0; border-radius:16px; padding:1.2rem; border:1px solid #EADECE;">
    <h4 style="color:#533E2D; margin-bottom:0.6rem;">🧠 核心情緒雷達分析：</h4>
    <p style="font-size:0.88rem; color:#5C4A38; line-height:1.7;">
        • <strong>自我慈悲指標：</strong> 82 分（比上週提升 +12% 🌱）<br>
        • <strong>焦慮緊繃釋放：</strong> 75 分（透過呼吸與音療有效舒緩）<br>
        • <strong>情緒被理解感：</strong> 95 分（在小薩與大熊的陪伴下建立安全基地）<br>
        • <strong>主要壓力來源：</strong> 職場完美主義與人際界線設定
    </p>
</div>
""", unsafe_allow_html=True)
        with col_r2:
            st.markdown(f"""
<div style="background:#FFFFFF; border-radius:16px; padding:1.2rem; border:1.5px solid #C2995F;">
    <h4 style="color:#C2995F; margin-bottom:0.6rem;">💌 {active_comp['name']} 給你的下週心靈處方箋：</h4>
    <p style="font-size:0.88rem; color:#5C4A38; line-height:1.7; font-style:italic;">
        「看見你這週開始願意為自己留下呼吸的空間，小薩真的很為你高興！下週讓我們試著練習『當事情做不完時，溫柔允許自己先睡個好覺』，世界不會因為你休息而崩塌的。」
    </p>
</div>
""", unsafe_allow_html=True)

    st.markdown("<hr style='border:none; border-top:1.5px solid #EADECE; margin:1.5rem 0;'>", unsafe_allow_html=True)

    # 商業定價方案
    st.markdown("<h3 style='text-align:center; color:#533E2D; margin-bottom:1rem;'>👑 選擇最適合你的心靈陪伴方案</h3>", unsafe_allow_html=True)
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown("""
<div style="background:#FFFFFF; border:2px solid #EADECE; border-radius:20px; padding:1.5rem; text-align:center; height:100%;">
    <div style="font-size:1.1rem; font-weight:700; color:#533E2D;">🌱 免費日常版</div>
    <div style="font-size:1.8rem; font-weight:700; color:#8C735A; margin:0.8rem 0;">NT$ 0</div>
    <div style="font-size:0.82rem; color:#6E5C49; text-align:left; line-height:1.8;">
        ✓ 🐶 薩摩耶・小薩 Live 2D 領養<br>
        ✓ 每日 10 次免費心靈諮商對話<br>
        ✓ 🎵 全套大自然白噪音多軌音療<br>
        ✓ 🫧 ASMR 泡泡紙與全部減壓工具<br>
        ✓ 每日打卡任務與感恩花園
    </div>
</div>
""", unsafe_allow_html=True)
        if not current_user.get("is_vip", 1):
            st.button("當前方案 (免費中)", disabled=True, use_container_width=True)

    with col_p2:
        st.markdown("""
<div style="background:linear-gradient(135deg, #FFFDF9 0%, #FAF0E1 100%); border:2.5px solid #C2995F; border-radius:20px; padding:1.5rem; text-align:center; box-shadow:0 8px 24px rgba(194,153,95,0.18); height:100%;">
    <div style="background:#C2995F; color:white; font-size:0.72rem; padding:2px 10px; border-radius:12px; display:inline-block; margin-bottom:0.3rem;">熱門推薦 🔥</div>
    <div style="font-size:1.1rem; font-weight:700; color:#533E2D;">👑 VIP 守護月度訂閱</div>
    <div style="font-size:1.8rem; font-weight:700; color:#C2995F; margin:0.6rem 0;">NT$ 149 <span style="font-size:0.85rem; color:#8C735A;">/ 月</span></div>
    <div style="font-size:0.82rem; color:#5C4A38; text-align:left; line-height:1.8;">
        ✓ 解鎖全部 10 隻 Live 2D 心理學神獸<br>
        ✓ 無限制 24/7 深度諮商對話<br>
        ✓ 每週 AI 深度情緒體檢週報<br>
        ✓ 解鎖全套奢華小屋裝扮與零食<br>
        ✓ 尊榮 VIP 專屬徽章
    </div>
</div>
""", unsafe_allow_html=True)
        if not current_user.get("is_vip", 1):
            if st.button("🌟 升級 VIP 守護會員 (NT$149/月)", key="btn_upgrade_vip_month", use_container_width=True):
                conn = db.get_db_connection()
                conn.cursor().execute("UPDATE users SET is_vip = 1, star_coins = star_coins + 300 WHERE id = ?", (CURRENT_USER_ID,))
                conn.commit()
                conn.close()
                st.balloons()
                st.success("🎉 恭喜升級為 VIP 守護會員！已解鎖全 10 隻動物夥伴與 300 🌟星光幣！")
                st.rerun()
        else:
            st.button("👑 尊榮 VIP 會員已啟用", disabled=True, use_container_width=True)

    with col_p3:
        st.markdown("""
<div style="background:#FFFFFF; border:2px solid #EADECE; border-radius:20px; padding:1.5rem; text-align:center; height:100%;">
    <div style="font-size:1.1rem; font-weight:700; color:#533E2D;">💎 VIP 年度尊榮方案</div>
    <div style="font-size:1.8rem; font-weight:700; color:#8C735A; margin:0.6rem 0;">NT$ 990 <span style="font-size:0.85rem; color:#8C735A;">/ 年</span></div>
    <div style="font-size:0.82rem; color:#6E5C49; text-align:left; line-height:1.8;">
        ✓ 享受月度方案全部特權<br>
        ✓ 相當於每月僅 NT$ 82（現省 45%）<br>
        ✓ 贈送 1000 🌟星光幣<br>
        ✓ 專屬心靈小屋「璀璨星空天窗」
    </div>
</div>
""", unsafe_allow_html=True)
        if not current_user.get("is_vip", 1):
            if st.button("💎 升級 VIP 年度方案 (NT$990/年)", key="btn_upgrade_vip_year", use_container_width=True):
                conn = db.get_db_connection()
                conn.cursor().execute("UPDATE users SET is_vip = 1, star_coins = star_coins + 1000 WHERE id = ?", (CURRENT_USER_ID,))
                conn.commit()
                conn.close()
                st.balloons()
                st.success("🎉 恭喜升級為 VIP 年度守護會員！已解鎖全套特權與 1000 🌟星光幣！")
                st.rerun()

    # 商業合規聲明
    st.markdown("""
<div style="margin-top:2.5rem; padding:1.2rem; background:rgba(255,255,255,0.7); border-radius:14px; border:1px solid #EADECE; font-size:0.78rem; color:#8C735A; line-height:1.6; text-align:center;">
    <strong>🛡️ 專業心靈陪伴合規聲明 (Health & Legal Disclaimer)：</strong><br>
    本應用程式為心理學正念同理心陪伴與身心減壓輔助工具，絕不提供任何醫療診斷、精神科處方或法律諮詢建議。若您面臨緊急危機或嚴重身心困擾，請即刻尋求當地專業合格之醫療與心理諮商機構協助。
</div>
""", unsafe_allow_html=True)
