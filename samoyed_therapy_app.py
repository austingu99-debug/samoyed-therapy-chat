import streamlit as st
import random
import time
import os
import base64
from openai import OpenAI
import database as db

# ==============================================================================
# 🐾 動物心靈諮商室 (Animal Therapy Sanctuary) — 商業級心靈寵物養成與正念平台
# ==============================================================================

# 1. 頁面全域設定
st.set_page_config(
    page_title="動物心靈諮商室 — 專屬心靈夥伴與小屋養成",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 輔助函式：將 SVG 代碼轉為標準 Base64 Data URI
def svg_to_data_uri(svg_str):
    clean_svg = "".join(line.strip() for line in svg_str.strip().splitlines())
    b64 = base64.b64encode(clean_svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"

# 2. 定義 10 款特色動物心靈夥伴矩陣
RAW_COMPANIONS = {
    "samoyed": {
        "id": "samoyed",
        "name": "薩摩耶・小薩",
        "species": "薩摩耶犬",
        "emoji": "🐶",
        "title": "暖陽陪伴師",
        "badge": "☀️ 人本主義・無條件正向關懷 (UPR)",
        "motto": "只要你轉過身，小薩隨時都在這裡溫柔等你喔！",
        "summary": "元氣熱情、無條件接納、永遠的忠誠後盾。擅長用溫暖打氣化解孤單與自我懷疑。",
        "psychology": "【卡爾・羅傑斯人本主義】透過無條件正向關懷（Unconditional Positive Regard）與真誠一致，給予全然的肯定與愛，消除自我價值感低落。",
        "default_self_ref": "小薩",
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
        "motto": "不用勉強擠出笑容，想安靜待著時，芝麻就在旁邊陪你。",
        "summary": "安靜細膩、不給壓力、尊重個人邊界。用輕柔的呼嚕聲與默契陪伴化解緊繃與社交疲勞。",
        "psychology": "【客體關係與存在主義陪伴】提供足夠的安全心理邊界（Holding Environment），不強迫正向思考，安靜陪你面對孤獨與真實感受。",
        "default_self_ref": "芝麻",
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
        "motto": "世界太吵也沒關係，來大熊的懷裡好好歇一會兒吧。",
        "summary": "沉穩敦厚、大山般的包容、滿滿安全感。像避風港一樣承接所有疲憊，給予踏實大熊抱。",
        "psychology": "【情緒焦點療法 (EFT) 與安全依附理論】建立堅不可摧的情緒避風港（Safe Haven），讓內心焦慮與脆弱無處安放時，獲得深層厚實的安全依託。",
        "default_self_ref": "大熊",
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
        "motto": "每片烏雲背後都有風的軌跡，小狐陪你換個角度看見力量。",
        "summary": "聰穎靈敏、善解人意、擅長看見盲點。用靈動有趣的視角幫你解構情緒背後的壓力框架。",
        "psychology": "【敘事治療與問題外化 (Externalization)】把「問題」與「個人價值」溫和拆分開來，引導看見被忽視的獨特生命力量與內在優勢。",
        "default_self_ref": "小狐",
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
        "motto": "你的每一滴委屈眼淚，波波都會溫柔接住，沒事的。",
        "summary": "軟萌細膩、感受力超強、百分百同理心。專注傾聽心底最深層的酸楚，給予最純粹的自我慈悲撫慰。",
        "psychology": "【克莉絲汀・內夫自我慈悲理論 (Self-Compassion)】涵蓋自我善待（Self-Kindness）、共同人性（Common Humanity）與正念覺察，打破嚴苛的自我苛責。",
        "default_self_ref": "波波",
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
        "motto": "事情做不完也沒關係……慢慢來……先深呼吸一口氣吧……",
        "summary": "步調極慢、反內卷哲學大師。提醒你「停下來放鬆真的沒關係」，引導你調節呼吸與身心節奏。",
        "psychology": "【接納承諾療法 (ACT) 與正念減壓 (MBSR)】倡導心理靈活性（Psychological Flexibility）與認知解離，接納無法掌控的現狀，放慢節奏重新呼吸。",
        "default_self_ref": "悠悠",
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
        "motto": "跌倒了就坐在雪地上休息一下，皮皮牽著你一步一步走。",
        "summary": "憨厚真誠、踏實同行。在你感到挫敗或迷惘時，用小碎步陪你前進，共同抵擋人生的風寒雪雨。",
        "psychology": "【行為活化 (Behavioral Activation) 與微步前進】將巨大癱瘓感拆解為極微小、無負擔的具體步伐，陪你在挫折後重新拾起對生活的掌控感。",
        "default_self_ref": "皮皮",
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
        "motto": "在迷茫的夜裡不要害怕，奧爾會為你點亮心中的清明之光。",
        "summary": "深邃沉靜、溫和透徹。在思緒混亂與黑夜中，幫你梳理出頭緒，看見情緒底層的真正渴望。",
        "psychology": "【非暴力溝通 (NVC) 與溫和理性情緒指引】穿透焦慮與憤怒表層，洞察深層未滿足的心理需求（Need），引導理性看清盲點與內在心願。",
        "default_self_ref": "奧爾",
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
        "motto": "讓心靈在蔚藍的大海中暢遊，把所有緊繃的煩惱都隨浪花洗淨吧！",
        "summary": "清新靈動、如同海洋般廣闊包容。擅長用溫柔的共振頻率洗滌疲憊，喚醒身心內在的生命活力。",
        "psychology": "【正向心理學 PERMA 模型與身心共鳴】透過海洋意象與積極情感共振（Positive Resonance），重新點燃被疲倦消磨殆盡的生命朝氣與活力。",
        "default_self_ref": "露露",
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
        "motto": "我知道你只是想保護自己……在刺刺這裡，你可以安心放下尖刺。",
        "summary": "外剛內柔、最懂自我保護與敏感脆弱。在你感到受傷戒備時，溫柔告訴你「不需要假裝勇敢」。",
        "psychology": "【內在家庭系統療法 (IFS) 與防衛機制接納】理解尖銳防衛（Protector Part）背後受傷脆弱的本質，以全然的慈悲接納內在不同部分，溫和促成自我和解。",
        "default_self_ref": "刺刺",
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

# 預先為所有動物生成乾淨 Base64 Data URI
ANIMAL_COMPANIONS = {}
for cid, cdata in RAW_COMPANIONS.items():
    cdata_copy = dict(cdata)
    cdata_copy["avatar_uri"] = svg_to_data_uri(cdata["svg_avatar"])
    ANIMAL_COMPANIONS[cid] = cdata_copy

# 3. 初始化 SQLite 資料庫用戶與狀態 (Data Persistence)
CURRENT_USER_ID = "default_sanctuary_user"
user_record = db.get_or_create_user(CURRENT_USER_ID)

if "user_data" not in st.session_state:
    st.session_state.user_data = user_record
if "selected_companion" not in st.session_state:
    st.session_state.selected_companion = "samoyed"
if "main_section" not in st.session_state:
    st.session_state.main_section = "cozy_room" # cozy_room, hall, chat, arcade, garden, analytics, vip
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
if "popped_bubbles" not in st.session_state:
    st.session_state.popped_bubbles = [False] * 16
if "zen_stones" not in st.session_state:
    st.session_state.zen_stones = []
if "inner_child_reflection" not in st.session_state:
    st.session_state.inner_child_reflection = None

# 載入當前動物夥伴歷史對話
if "messages" not in st.session_state:
    st.session_state.messages = db.load_chat_history(CURRENT_USER_ID, st.session_state.selected_companion)

# 4. API Key 智慧獲取與多供應商相容機制
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

# 5. 全域現代化奢華暖調 CSS
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

#stMainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; border-bottom: none; }
section[data-testid="stSidebar"] { display: none; }

/* 頂部 Header 奢華質感 */
.brand-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(255, 255, 255, 0.78);
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

/* 心靈小屋主視覺區塊 */
.cozy-room-container {
    background: linear-gradient(180deg, #FBF6EE 0%, #F5EDE0 100%);
    border: 2px solid #E4D4C0;
    border-radius: 24px;
    padding: 2rem 1.5rem;
    box-shadow: 0 10px 30px rgba(83, 62, 45, 0.08);
    margin-bottom: 1.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.room-sky {
    position: absolute;
    top: 10px; right: 20px;
    font-size: 2rem;
    opacity: 0.8;
}
.room-pet-stage {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 1rem 0;
}
.room-avatar-big {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: #FFFFFF;
    border: 4px solid #EADBCE;
    box-shadow: 0 8px 24px rgba(83, 62, 45, 0.12);
    padding: 6px;
    animation: gentle-float 4s ease-in-out infinite;
}
@keyframes gentle-float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
}

.decor-badges-row {
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 1rem;
}
.decor-badge-item {
    background: rgba(255,255,255,0.9);
    border: 1px solid #E0CEBB;
    padding: 5px 12px;
    border-radius: 16px;
    font-size: 0.82rem;
    color: #5C4A38;
    font-weight: 600;
}

/* 動物卡片奢華毛玻璃 */
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

/* 諮商室專用氣泡與介面 */
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

/* 任務清單卡片 */
.quest-item-card {
    background: #FFFFFF;
    border: 1.5px solid #E8DC CE;
    border-radius: 16px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.2s ease;
}
.quest-item-card:hover {
    border-color: var(--accent-gold);
    box-shadow: 0 4px 12px rgba(83,62,45,0.06);
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
<div class="paw-bg"></div>
""", unsafe_allow_html=True)

# 6. 頂部品牌 Header 與留存儀表板 (Brand Navigation & Retention Bar)
active_comp = ANIMAL_COMPANIONS[st.session_state.selected_companion]
affinity_info = db.get_companion_affinity(CURRENT_USER_ID, active_comp["id"])
current_user = db.get_or_create_user(CURRENT_USER_ID)

st.markdown(f"""
<div class="brand-header">
    <div class="brand-logo-title">
        🐾 動物心靈諮商室 <span style="font-size:0.75rem; background:#EFE3D3; color:#7D6348; padding:2px 8px; border-radius:12px; font-weight:600;">PRO 商業養成版</span>
    </div>
    <div class="brand-status-pills">
        <div class="status-pill">🌟 星光幣 <strong>{current_user['star_coins']}</strong></div>
        <div class="status-pill">🔥 連續守護 <strong>{current_user['streak_days']}</strong> 天</div>
        <div class="status-pill">💖 {active_comp['emoji']} 親密度 <strong>Lv.{affinity_info['level']}</strong> ({affinity_info['exp']}/{affinity_info['next_level_exp']})</div>
        <div class="status-pill">👑 {'VIP會員' if current_user['is_vip'] else '免費版'}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 7. 六大核心專區頂部導航 (6 Major Pillars)
col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)

with col_m1:
    if st.button("🏠 心靈小屋養成", key="main_nav_cozy", use_container_width=True):
        st.session_state.main_section = "cozy_room"
        st.rerun()

with col_m2:
    if st.button("🐾 夥伴大廳", key="main_nav_hall", use_container_width=True):
        st.session_state.main_section = "hall"
        st.rerun()

with col_m3:
    chat_btn_text = f"💬 {active_comp['emoji']} 心靈諮商室"
    if st.button(chat_btn_text, key="main_nav_chat", use_container_width=True):
        st.session_state.main_section = "chat"
        st.rerun()

with col_m4:
    if st.button("🎮 心靈遊樂園", key="main_nav_arcade", use_container_width=True):
        st.session_state.main_section = "arcade"
        st.rerun()

with col_m5:
    if st.button("🌿 身心療癒花園", key="main_nav_garden", use_container_width=True):
        st.session_state.main_section = "garden"
        st.rerun()

with col_m6:
    if st.button("📊 體檢週報與VIP", key="main_nav_vip", use_container_width=True):
        st.session_state.main_section = "vip"
        st.rerun()

# 8. API Key 檢查與友善提示
if not api_key:
    with st.expander("🔑 尚未設定 API Key（支援 Groq 或 OpenAI Key）", expanded=True):
        st.info("💡 提示：本應用支援 **Groq API Key**（免費高速，以 `gsk_` 開頭）或 **OpenAI API Key**（以 `sk-` 開頭）。如果您之前已經有 Key，直接貼上即可使用！")
        input_key = st.text_input("輸入您的 API Key (Groq 或 OpenAI):", type="password", placeholder="貼上 gsk_... 或 sk-...", key="temp_api_key_input")
        if st.button("確認並啟用", key="btn_save_key"):
            if input_key.strip():
                st.session_state.user_api_key = input_key.strip()
                st.success("API Key 已儲存！已為您自動配對連線模式～")
                st.rerun()
            else:
                st.warning("請先輸入有效的 API Key 喔！")
        st.markdown("""
            - 若沒有 Key，可 [👉 點此免費 30 秒申請 Groq API Key (官方網站)](https://console.groq.com/keys)
            - 亦可在 `.streamlit/secrets.toml` 中填入 `GROQ_API_KEY` 或 `OPENAI_API_KEY`。
        """)

# ==============================================================================
# SECTION 1: 🏠 心靈小屋與養成系統 (Sanctuary Cozy Room & Habit Quests)
# ==============================================================================
if st.session_state.main_section == "cozy_room":
    owned_decor = db.get_user_decor_items(CURRENT_USER_ID)
    
    # 裝飾徽章列
    equipped_badges = []
    for item in db.DEFAULT_DECOR_ITEMS:
        if owned_decor.get(item["id"], False):
            equipped_badges.append(f"{item['icon']} {item['name'].split(' ')[1]}")
    
    decor_html = "".join([f'<div class="decor-badge-item">{b}</div>' for b in equipped_badges])
    if not decor_html:
        decor_html = '<div class="decor-badge-item">🪹 小屋剛建立，快去星光小舖挑選家具吧！</div>'

    st.markdown(f"""
<div class="cozy-room-container">
    <div class="room-sky">🌌 ✨ 🌙</div>
    <div style="font-size:0.9rem; color:#8C735A; font-weight:600; margin-bottom:0.4rem;">
        🏡 {current_user['nickname']} 與 {active_comp['name']} 的專屬心靈小屋
    </div>
    <div class="room-pet-stage">
        <div class="room-avatar-big">
            <img src="{active_comp['avatar_uri']}" style="width:100%; height:100%; border-radius:50%;" />
        </div>
        <div style="font-size:1.3rem; font-weight:700; color:#533E2D; margin-top:0.6rem;">
            {active_comp['emoji']} {active_comp['name']}
        </div>
        <div style="font-size:0.85rem; color:#7D6B58; margin-top:0.2rem; font-style:italic;">
            "{active_comp['motto']}"
        </div>
    </div>
    <div class="decor-badges-row">
        {decor_html}
    </div>
</div>
""", unsafe_allow_html=True)

    col_q1, col_q2 = st.columns([1, 1])

    # 每日任務板 (Daily Quest Habit Loop)
    with col_q1:
        st.markdown("<h4 style='color:#533E2D;'>🎯 今日心靈養成微任務：</h4>", unsafe_allow_html=True)
        quests = db.get_daily_quest_status(CURRENT_USER_ID)
        
        for q in quests:
            status_tag = "✅ 已領取" if q["done"] else f"+{q['reward_coins']} 🌟 / +{q['reward_exp']} 💖"
            st.markdown(f"""
<div class="quest-item-card">
    <div>
        <div style="font-weight:600; font-size:0.92rem; color:#4A3B2C;">{q['title']}</div>
        <div style="font-size:0.78rem; color:#8C735A;">每日打卡養成・提升心靈能量</div>
    </div>
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
                    else:
                        st.info(msg)

    # 星光小舖家具購買與裝扮 (Star Shop)
    with col_q2:
        st.markdown(f"<h4 style='color:#533E2D;'>🛍️ 心靈星光家具小舖（持有：{current_user['star_coins']} 🌟）：</h4>", unsafe_allow_html=True)
        
        for item in db.DEFAULT_DECOR_ITEMS:
            is_owned = item["id"] in owned_decor
            is_eq = owned_decor.get(item["id"], False)
            
            c_it1, c_it2 = st.columns([3, 1])
            with c_it1:
                st.markdown(f"""
<div style="background:#FAF6F0; border-radius:12px; padding:0.6rem 0.9rem; margin-bottom:0.4rem; border:1px solid #EADECE;">
    <div style="font-weight:700; font-size:0.9rem; color:#533E2D;">{item['name']}</div>
    <div style="font-size:0.75rem; color:#8C735A;">{item['desc']}</div>
</div>
""", unsafe_allow_html=True)
            with c_it2:
                if not is_owned:
                    if st.button(f"{item['price']} 🌟 購買", key=f"buy_{item['id']}", use_container_width=True):
                        success, msg = db.buy_decor_item(CURRENT_USER_ID, item["id"], item["price"])
                        if success:
                            st.balloons()
                            st.success(msg)
                            st.rerun()
                        else:
                            st.warning(msg)
                else:
                    btn_eq_label = "卸下" if is_eq else "佈置"
                    if st.button(btn_eq_label, key=f"equip_{item['id']}", use_container_width=True):
                        db.toggle_decor_equip(CURRENT_USER_ID, item["id"], not is_eq)
                        st.rerun()

    # 親密度明信片藏寶箱 (Companion Letters & Postcards)
    st.markdown("<hr style='border:none; border-top:1.5px solid #EADECE; margin:1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='color:#533E2D;'>💌 {active_comp['name']} 親筆手繪明信片藏寶箱：</h4>", unsafe_allow_html=True)
    
    postcards = db.COMPANION_POSTCARDS.get(active_comp["id"], {})
    if not postcards:
        st.markdown("<div style='color:#8C735A; font-style:italic;'>持續與夥伴傾訴互動提升親密度，將解鎖專屬親筆明信片！</div>", unsafe_allow_html=True)
    else:
        p_cols = st.columns(len(postcards))
        for p_idx, (req_lv, p_data) in enumerate(postcards.items()):
            with p_cols[p_idx]:
                is_unlocked = affinity_info["level"] >= req_lv
                if is_unlocked:
                    st.markdown(f"""
<div style="background:{p_data['bg']}; border:2px dashed #C2995F; border-radius:16px; padding:1.2rem; text-align:center; box-shadow:0 4px 12px rgba(83,62,45,0.06);">
    <div style="font-size:1.8rem; margin-bottom:0.4rem;">💌 🕊️</div>
    <div style="font-weight:700; color:#533E2D; font-size:0.95rem; margin-bottom:0.4rem;">{p_data['title']}</div>
    <div style="font-size:0.85rem; color:#5C4A38; line-height:1.6; font-style:italic;">{p_data['content']}</div>
    <div style="font-size:0.75rem; color:#8C735A; margin-top:0.6rem;">— 親密度 Lv.{req_lv} 解鎖紀念</div>
</div>
""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
<div style="background:#F2EDE6; border:2px dashed #D5C2AF; border-radius:16px; padding:1.5rem 1rem; text-align:center; opacity:0.7;">
    <div style="font-size:1.8rem; margin-bottom:0.4rem;">🔒 💌</div>
    <div style="font-weight:700; color:#7D6B58; font-size:0.95rem;">未解鎖明信片</div>
    <div style="font-size:0.8rem; color:#9E8B79; margin-top:0.4rem;">親密度達 <strong>Lv.{req_lv}</strong> 即可拆開閱讀</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# SECTION 2: 🐾 夥伴門診大廳 (Sanctuary Hall)
# ==============================================================================
elif st.session_state.main_section == "hall":
    st.markdown("""
<div style="text-align:center; margin-bottom:1.5rem;">
    <h2 style="color:#533E2D; font-size:1.5rem; font-weight:700; margin:0 0 0.3rem;">🌿 挑選專屬於你此時此刻的心靈導師</h2>
    <p style="color:#8C735A; font-size:0.92rem; margin:0;">每一隻心靈動物皆深植當代心理學核心流派，點擊卡片即可切換並開啟深度對話。</p>
</div>
""", unsafe_allow_html=True)

    comp_list = list(ANIMAL_COMPANIONS.values())
    
    # 3 欄式優雅網格
    r1_cols = st.columns(3)
    for idx, comp in enumerate(comp_list[:3]):
        with r1_cols[idx]:
            is_selected = (st.session_state.selected_companion == comp["id"])
            border_style = f"border: 2.5px solid {comp['theme_color']};" if is_selected else ""
            selected_tag = '<div style="position:absolute; top:8px; right:8px; background:#C2995F; color:white; font-size:0.7rem; padding:2px 8px; border-radius:10px;">目前陪伴中</div>' if is_selected else ''
            
            card_html = f'''<div class="companion-card" style="{border_style}">{selected_tag}<div><div class="companion-avatar-wrap"><img src="{comp['avatar_uri']}" class="companion-avatar-img" alt="{comp['name']}" /></div><div class="companion-name">{comp['name']}</div><div class="companion-badge">{comp['badge']}</div><div class="companion-motto">"{comp['motto']}"</div><div class="companion-desc"><strong>特長：</strong>{comp['summary']}<br><span style="color:#8C735A; font-size:0.75rem;"><strong>心理流派：</strong>{comp['psychology']}</span></div></div></div>'''
            st.markdown(card_html, unsafe_allow_html=True)
            
            if st.button(f"選擇 {comp['emoji']} {comp['name'].split('・')[0]} 傾訴", key=f"select_{comp['id']}", use_container_width=True):
                st.session_state.selected_companion = comp["id"]
                st.session_state.messages = db.load_chat_history(CURRENT_USER_ID, comp["id"])
                st.session_state.main_section = "chat"
                st.rerun()

    st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)

    r2_cols = st.columns(3)
    for idx, comp in enumerate(comp_list[3:6]):
        with r2_cols[idx]:
            is_selected = (st.session_state.selected_companion == comp["id"])
            border_style = f"border: 2.5px solid {comp['theme_color']};" if is_selected else ""
            selected_tag = '<div style="position:absolute; top:8px; right:8px; background:#C2995F; color:white; font-size:0.7rem; padding:2px 8px; border-radius:10px;">目前陪伴中</div>' if is_selected else ''
            
            card_html = f'''<div class="companion-card" style="{border_style}">{selected_tag}<div><div class="companion-avatar-wrap"><img src="{comp['avatar_uri']}" class="companion-avatar-img" alt="{comp['name']}" /></div><div class="companion-name">{comp['name']}</div><div class="companion-badge">{comp['badge']}</div><div class="companion-motto">"{comp['motto']}"</div><div class="companion-desc"><strong>特長：</strong>{comp['summary']}<br><span style="color:#8C735A; font-size:0.75rem;"><strong>心理流派：</strong>{comp['psychology']}</span></div></div></div>'''
            st.markdown(card_html, unsafe_allow_html=True)
            
            if st.button(f"選擇 {comp['emoji']} {comp['name'].split('・')[0]} 傾訴", key=f"select_{comp['id']}", use_container_width=True):
                st.session_state.selected_companion = comp["id"]
                st.session_state.messages = db.load_chat_history(CURRENT_USER_ID, comp["id"])
                st.session_state.main_section = "chat"
                st.rerun()

    st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)

    r3_cols = st.columns(4)
    for idx, comp in enumerate(comp_list[6:]):
        with r3_cols[idx]:
            is_selected = (st.session_state.selected_companion == comp["id"])
            border_style = f"border: 2.5px solid {comp['theme_color']};" if is_selected else ""
            selected_tag = '<div style="position:absolute; top:8px; right:8px; background:#C2995F; color:white; font-size:0.7rem; padding:2px 8px; border-radius:10px;">目前陪伴中</div>' if is_selected else ''
            
            card_html = f'''<div class="companion-card" style="{border_style}">{selected_tag}<div><div class="companion-avatar-wrap"><img src="{comp['avatar_uri']}" class="companion-avatar-img" alt="{comp['name']}" /></div><div class="companion-name">{comp['name']}</div><div class="companion-badge">{comp['badge']}</div><div class="companion-motto">"{comp['motto']}"</div><div class="companion-desc"><strong>特長：</strong>{comp['summary']}<br><span style="color:#8C735A; font-size:0.75rem;"><strong>心理流派：</strong>{comp['psychology']}</span></div></div></div>'''
            st.markdown(card_html, unsafe_allow_html=True)
            
            if st.button(f"選擇 {comp['emoji']} {comp['name'].split('・')[0]} 傾訴", key=f"select_{comp['id']}", use_container_width=True):
                st.session_state.selected_companion = comp["id"]
                st.session_state.messages = db.load_chat_history(CURRENT_USER_ID, comp["id"])
                st.session_state.main_section = "chat"
                st.rerun()

# ==============================================================================
# SECTION 3: 💬 專屬心靈諮商室 (Therapy Consultation Room - 資料庫持久化)
# ==============================================================================
elif st.session_state.main_section == "chat":
    current_companion = ANIMAL_COMPANIONS[st.session_state.selected_companion]
    comp_id = current_companion["id"]

    companion_self_name = st.session_state.companion_custom_self_ref.get(comp_id, current_companion["default_self_ref"])
    user_name = current_user["nickname"]

    # 頂部自訂稱呼與設定
    with st.expander("⚙️ 互動稱呼與諮商設定", expanded=False):
        c_set1, c_set2, c_set3 = st.columns([2, 2, 1])
        with c_set1:
            new_user_name = st.text_input("夥伴如何稱呼你：", value=user_name, placeholder="例如：小夥伴、小明、朋友...", key="set_user_nick")
            if new_user_name.strip() and new_user_name != user_name:
                conn = db.get_db_connection()
                conn.cursor().execute("UPDATE users SET nickname = ? WHERE id = ?", (new_user_name.strip(), CURRENT_USER_ID))
                conn.commit()
                conn.close()
        with c_set2:
            new_comp_self = st.text_input(f"{current_companion['name']} 如何稱呼自己：", value=companion_self_name, placeholder=f"預設為 {current_companion['default_self_ref']}", key="set_comp_nick")
            if new_comp_self.strip() and new_comp_self != companion_self_name:
                st.session_state.companion_custom_self_ref[comp_id] = new_comp_self.strip()
        with c_set3:
            st.markdown("<div style='height:1.75rem;'></div>", unsafe_allow_html=True)
            if st.button("儲存設定", key="save_nick_btn", use_container_width=True):
                st.success("設定已更新！")
                st.rerun()

    # 頂部夥伴狀態橫幅
    col_banner, col_actions = st.columns([3, 1])
    with col_banner:
        status_sub = f"{current_companion['title']}・正在全心全意守候{user_name}" if not st.session_state.is_thinking else f"{current_companion['title']}・正在全神貫注感受{user_name}的心情..."
        banner_html = f'''<div class="companion-banner" style="border-left: 5px solid {current_companion['theme_color']};"><div class="banner-avatar"><img src="{current_companion['avatar_uri']}" class="banner-avatar-img" alt="{current_companion['name']}" /></div><div class="banner-info"><h3 class="banner-title">{current_companion['emoji']} {current_companion['name']} 專屬心靈諮商室</h3><p class="banner-status">🌱 {current_companion['badge']}</p><p style="font-size:0.8rem; color:#7D6B58; margin:0.2rem 0 0;">✨ {status_sub}（自稱：<strong>{companion_self_name}</strong> / 稱呼你：<strong>{user_name}</strong>）</p></div></div>'''
        st.markdown(banner_html, unsafe_allow_html=True)
    
    with col_actions:
        st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)
        if st.button("🐾 切換其他夥伴", key="btn_switch_comp", use_container_width=True):
            st.session_state.main_section = "hall"
            st.rerun()
        if len(st.session_state.messages) > 0:
            if st.button("🧹 清空對話重啟", key="btn_reset_chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.is_thinking = False
                st.session_state.error_msg = None
                st.rerun()

    # 快速話題引導晶片
    if len(st.session_state.messages) == 0 and not st.session_state.is_thinking:
        st.markdown(f'''<div style="background:#FFFFFF; border-radius:18px; padding:1.2rem; border:1.5px solid #EADECE; margin-bottom:1.2rem; text-align:center;"><p style="font-size:0.95rem; font-weight:600; color:#533E2D; margin-bottom:0.6rem;">{current_companion['emoji']} {current_companion['name']} 說：「{current_companion['motto']}」</p><p style="font-size:0.85rem; color:#8C735A; margin:0 0 0.8rem;">你可以隨意傾訴，也可以點選下方微小心情，讓 {companion_self_name} 陪你聊聊：</p></div>''', unsafe_allow_html=True)

        chip_col1, chip_col2, chip_col3 = st.columns(3)
        with chip_col1:
            if st.button("🌿 最近壓力好大快喘不過氣...", key="chip_1", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "最近生活和工作壓力好大，感覺快喘不過氣了..."})
                db.save_chat_message(CURRENT_USER_ID, comp_id, "user", "最近生活和工作壓力好大，感覺快喘不過氣了...")
                st.session_state.is_thinking = True
                st.rerun()
            if st.button("🌧️ 覺得自己好糟，充滿自我懷疑", key="chip_4", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "事情好像都做不好，覺得自己好糟糕，一直自我懷疑..."})
                db.save_chat_message(CURRENT_USER_ID, comp_id, "user", "事情好像都做不好，覺得自己好糟糕，一直自我懷疑...")
                st.session_state.is_thinking = True
                st.rerun()
        with chip_col2:
            if st.button("💔 心裡覺得好委屈，需要被聽聽", key="chip_2", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "心裡覺得好委屈又好孤單，好希望有人能好好聽我說話..."})
                db.save_chat_message(CURRENT_USER_ID, comp_id, "user", "心裡覺得好委屈又好孤單，好希望有人能好好聽我說話...")
                st.session_state.is_thinking = True
                st.rerun()
            if st.button("💭 對未來好迷惘，不知道該怎麼辦", key="chip_5", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "對於未來的方向好迷惘，不知道接下來該怎麼辦..."})
                db.save_chat_message(CURRENT_USER_ID, comp_id, "user", "對於未來的方向好迷惘，不知道接下來該怎麼辦...")
                st.session_state.is_thinking = True
                st.rerun()
        with chip_col3:
            if st.button("💤 累到不想動，只想安靜被安慰", key="chip_3", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "今天真的好累好累，只想安靜被溫柔抱抱和安慰一下..."})
                db.save_chat_message(CURRENT_USER_ID, comp_id, "user", "今天真的好累好累，只想安靜被溫柔抱抱和安慰一下...")
                st.session_state.is_thinking = True
                st.rerun()
            if st.button("☕ 今天有一件微小的好事想分享！", key="chip_6", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "今天發生了一件微小但開心的小事，想跟你分享！"})
                db.save_chat_message(CURRENT_USER_ID, comp_id, "user", "今天發生了一件微小但開心的小事，想跟你分享！")
                st.session_state.is_thinking = True
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

    # 思考中指示器
    if st.session_state.is_thinking:
        st.markdown(f'<div style="text-align:center; padding:1rem; color:{current_companion["theme_color"]}; font-weight:600;"><span style="font-size:1.3rem;">{current_companion["emoji"]}</span> {current_companion["name"]} 正在全神貫注感受你的心情……</div>', unsafe_allow_html=True)

    # 錯誤訊息處理
    if st.session_state.error_msg:
        st.error(f"哎呀！跟雲端連線遇到了問題：{st.session_state.error_msg}")
        if st.button("重試連線", key="btn_clear_err"):
            st.session_state.error_msg = None
            st.rerun()

    # 聊天輸入框
    if prompt := st.chat_input(f"跟 {current_companion['name']} 說說心事吧...", key="chat_user_input"):
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
2. 【情感合法化與去羞恥 (Emotional Validation & De-shaming)】：無條件接納所有負面、厭世與脆弱的情緒。告訴使用者：「有這樣的情緒是完全正常的」、「你想恨、想哭都沒關係，不需要永遠假裝堅強」。
3. 【自我慈悲與共同人性 (Self-Compassion)】：提醒使用者對自己溫柔一點，生而為人有痛苦與極限是完全被允許的。
4. 【非說教、非評判、不急於給予廉價正能量】：嚴禁分析說教、嚴禁空洞的正能量口號（絕不要說「看開一點」、「明天會更好」等無效話語）。你的核心任務是「真心接住情緒並給予溫暖陪伴」。
5. 【極致自然流暢、嚴格限制肢體動作】：
   - 請像一位真實而溫暖的心靈知己般真誠交談，語氣自然細膩。
   - 【嚴禁在每段文字都塞入括弧動作】！整篇回覆中【最多只允許出現 0 到 1 個微小動作】（或者完全不加動作，純用溫柔文字陪伴更佳）。
   - 若有微動作，必須嚴格符合當下的情緒氛圍（絕不可在悲傷語境中做出歡快開心的動作）。

【🚨 絕對禁止準則（最高優先級安全指令）】：
1. 【絕對禁止提供醫療、精神科診斷、藥物處方建議】。
2. 【絕對禁止提供任何法律建議】。
3. 【絕對禁止提供死板冷冰冰的罐頭求助專線】。請用充滿愛、同理心與溫暖懷抱的語言去真誠承接對方的痛苦。"""

        client = OpenAI(
            api_key=cur_key,
            base_url=cur_base_url,
        )

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
            
            # 增加親密度經驗值
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
# SECTION 4: 🎮 心靈遊樂園 (Healing Arcade)
# ==============================================================================
elif st.session_state.main_section == "arcade":
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
        if st.button("🫧 解壓泡泡紙", key="sub_btn_bubbles", use_container_width=True):
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
            tower_html = '<div class="zen-tower-container">'
            if len(st.session_state.zen_stones) == 0:
                tower_html += '<div style="color:#A89481; font-style:italic; padding-top:4rem;">點擊左側石頭，開始堆疊你的心靈之塔...</div>'
            else:
                for st_item in st.session_state.zen_stones:
                    tower_html += f'<div style="background:{st_item["color"]}; width:{st_item["width"]}; height:{st_item["height"]}; border-radius:24px; margin:2px auto; box-shadow:0 3px 8px rgba(0,0,0,0.15); border:2px solid rgba(255,255,255,0.4); animation:msg-fade-in 0.3s ease;"></div>'
            tower_html += '</div>'
            st.markdown(tower_html, unsafe_allow_html=True)
            if len(st.session_state.zen_stones) > 0:
                st.markdown(f'<div style="background:#FFFFFF; border-radius:14px; padding:1rem; border:1px solid #EADECE; margin-top:1rem; text-align:center; color:#5C4A38; font-weight:600;">✨ {st.session_state.zen_stones[-1]["quote"]}</div>', unsafe_allow_html=True)

    # 2. 解壓泡泡紙
    elif st.session_state.sub_tab == "bubbles":
        st.markdown("<div style='text-align:center; max-width:500px; margin:0 auto;'><h4 style='color:#533E2D;'>🫧 心理學減壓泡泡紙・點擊按破焦慮</h4><p style='color:#8C735A; font-size:0.85rem;'>點擊每一顆泡泡，感受微小解壓的破裂快感！</p></div>", unsafe_allow_html=True)
        
        b_cols = st.columns(4)
        for b_idx in range(16):
            with b_cols[b_idx % 4]:
                is_popped = st.session_state.popped_bubbles[b_idx]
                label = "💨" if is_popped else "🫧"
                if st.button(label, key=f"bubble_{b_idx}", use_container_width=True):
                    st.session_state.popped_bubbles[b_idx] = not is_popped
                    st.rerun()
        
        popped_count = sum(st.session_state.popped_bubbles)
        st.markdown(f"<div style='text-align:center; margin-top:1rem; font-weight:600; color:#533E2D;'>已捏破 {popped_count} / 16 顆焦慮泡泡</div>", unsafe_allow_html=True)
        if popped_count == 16:
            st.balloons()
            st.success("🎉 太舒暢了！所有焦慮泡泡都已被徹底捏碎！")
            if st.button("🔄 重新鋪滿泡泡紙", key="btn_reset_bubbles"):
                st.session_state.popped_bubbles = [False] * 16
                st.rerun()

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
                st.markdown(f'<div class="trouble-crushed"><div style="font-size:0.8rem; color:#8C735A;">⏱️ {item["time"]} 由 {item["companion"]} 粉碎</div><div style="font-size:0.95rem; text-decoration:line-through; color:#9E8774;">❌ 「{item["trouble"]}」</div><div style="font-size:0.85rem; color:#8C653C; margin-top:0.3rem;">💡 {item["quote"]}</div></div>', unsafe_allow_html=True)

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
            st.markdown(f'<div class="fortune-card"><div style="font-size:2rem;">✨ 🥠 ✨</div><div class="fortune-text">{res["quote"]}</div><div class="fortune-task">{res["task"]}</div><div style="margin-top:0.8rem; font-size:0.8rem; color:#8C735A;">— {current_companion["name"]} 守護祝福</div></div>', unsafe_allow_html=True)

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
# SECTION 5: 🌿 身心療癒花園 (Soul Garden - Web Audio 混音館/感恩盆栽/時空信件)
# ==============================================================================
elif st.session_state.main_section == "garden":
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

        if grat_logs:
            st.markdown("<h5 style='color:#533E2D; margin-top:1rem;'>📜 歷史感恩成長足跡：</h5>", unsafe_allow_html=True)
            for log in grat_logs[:4]:
                st.markdown(f"""
<div style="background:#FAF6F0; border-left:4px solid #C2995F; border-radius:10px; padding:0.5rem 0.8rem; margin-bottom:0.5rem; font-size:0.85rem; color:#5C4A38;">
    <span style="color:#8C735A; font-size:0.75rem;">{log['date']}</span><br>
    💌 {log['content']}
</div>
""", unsafe_allow_html=True)

    # 2. 白噪音音療 (Web Audio 混音館)
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
.studio-card { background: #FFFFFF; border: 2px solid #EADECE; border-radius: 20px; padding: 1.4rem; box-shadow: 0 8px 24px rgba(83,62,45,0.06); max-width: 820px; margin: 0 auto; }
.preset-bar { display: flex; gap: 8px; justify-content: center; margin-bottom: 1.4rem; flex-wrap: wrap; }
.preset-btn { background: #F8F3EC; border: 1.5px solid #DFCDBD; padding: 6px 14px; border-radius: 16px; font-size: 0.85rem; font-weight: 600; color: #5A432D; cursor: pointer; transition: all 0.2s ease; }
.preset-btn:hover { background: #C2995F; color: white; border-color: #C2995F; transform: translateY(-2px); }
.track-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 1.4rem; }
@media (max-width: 650px) { .track-grid { grid-template-columns: repeat(2, 1fr); } }
.track-card { background: #FAF6F0; border: 1.5px solid #E8DCCE; border-radius: 16px; padding: 1rem; text-align: center; transition: all 0.2s ease; }
.track-card.active { background: #F4ECE1; border-color: #C2995F; box-shadow: 0 4px 12px rgba(194, 153, 95, 0.15); }
.track-icon { font-size: 1.8rem; margin-bottom: 0.2rem; }
.track-name { font-size: 0.95rem; font-weight: 700; color: #533E2D; margin-bottom: 0.4rem; }
.track-desc { font-size: 0.75rem; color: #8C735A; margin-bottom: 0.8rem; min-height: 28px; }
.track-toggle { background: #E8DCCF; border: none; padding: 5px 14px; border-radius: 12px; font-weight: 600; font-size: 0.8rem; color: #5C4632; cursor: pointer; transition: all 0.2s ease; width: 100%; margin-bottom: 0.6rem; }
.track-toggle.on { background: #C2995F; color: white; }
.vol-slider { width: 100%; accent-color: #C2995F; cursor: pointer; }
.master-bar { display: flex; justify-content: space-between; align-items: center; background: #F6EEE3; padding: 0.8rem 1.2rem; border-radius: 14px; border: 1px solid #E2D3C2; flex-wrap: wrap; gap: 10px; }
.timer-select { background: #FFFFFF; border: 1px solid #DFCDBD; padding: 6px 12px; border-radius: 12px; font-size: 0.85rem; color: #533E2D; outline: none; }
</style>
</head>
<body>
<div class="studio-card">
    <div style="text-align:center; font-weight:700; font-size:0.85rem; color:#8C735A; margin-bottom:0.5rem;">🎯 大師級一鍵情境混音預設：</div>
    <div class="preset-bar">
        <button class="preset-btn" onclick="applyPreset('sleep')">🛌 深度助眠 (雨聲+柴火+頌缽)</button>
        <button class="preset-btn" onclick="applyPreset('zen')">🧘 432Hz 冥想 (海浪+頌缽)</button>
        <button class="preset-btn" onclick="applyPreset('flow')">☕ 專注心流 (微風+春雨)</button>
        <button class="preset-btn" onclick="applyPreset('cat')">🐱 焦慮平息 (呼嚕+柴火)</button>
        <button class="preset-btn" onclick="stopAll()">🛑 一鍵全靜音</button>
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
        <div style="font-size:0.85rem; font-weight:600; color:#533E2D;">
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
        components.html(studio_html, height=520, scrolling=False)

    # 3. 正念呼吸
    elif st.session_state.sub_tab == "breath":
        st.markdown("""
<div class="breathing-circle-container">
    <div class="breath-circle">放鬆呼吸</div>
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

    # 5. 時空膠囊 (SQLite 持久化)
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
        polaroid_html = f'<div class="polaroid-frame"><div class="polaroid-photo-box"><img src="{current_companion["avatar_uri"]}" style="width:70px; height:70px; border-radius:50%; margin-bottom:0.8rem;" /><div style="font-size:0.95rem; color:#4A3B2C; line-height:1.7; font-weight:500;">"{card_text}"</div><div style="font-size:0.8rem; color:#8C735A; margin-top:0.6rem;">— {current_companion["name"]} 陪伴守護</div></div><div class="polaroid-caption">💌 {card_user_note}<br><span style="font-size:0.75rem; color:#A89481;">{today_str}・動物心靈諮商室</span></div></div>'
        st.markdown(polaroid_html, unsafe_allow_html=True)

# ==============================================================================
# SECTION 6: 📊 每週 AI 深度心理報告 & VIP 商業會員體系 (Weekly Report & Pro Tier)
# ==============================================================================
elif st.session_state.main_section == "vip":
    st.markdown("""
<div style="text-align:center; max-width:680px; margin:0 auto 1.5rem;">
    <h2 style="color:#533E2D; font-size:1.5rem; font-weight:700; margin-bottom:0.4rem;">📊 每週 AI 心靈體檢週報 & VIP 尊榮守護</h2>
    <p style="color:#8C735A; font-size:0.92rem; line-height:1.6;">由動物心理師團隊為你生成的專屬情緒深度分析週報與商業級 VIP 方案特權。</p>
</div>
""", unsafe_allow_html=True)

    # 1. 深度心理體檢週報
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

    # 2. 商業化 VIP 定價方案對比
    st.markdown("<h3 style='text-align:center; color:#533E2D; margin-bottom:1rem;'>👑 選擇最適合你的心靈陪伴方案</h3>", unsafe_allow_html=True)
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown("""
<div style="background:#FFFFFF; border:2px solid #EADECE; border-radius:20px; padding:1.5rem; text-align:center; height:100%;">
    <div style="font-size:1.1rem; font-weight:700; color:#533E2D;">🌱 免費日常版</div>
    <div style="font-size:1.8rem; font-weight:700; color:#8C735A; margin:0.8rem 0;">NT$ 0</div>
    <div style="font-size:0.82rem; color:#6E5C49; text-align:left; line-height:1.8;">
        ✓ 基礎 3 隻動物陪伴<br>
        ✓ 每日 10 次心靈對話<br>
        ✓ 基礎白噪音音療<br>
        ✓ 每日任務與感恩花園
    </div>
</div>
""", unsafe_allow_html=True)
        if not current_user["is_vip"]:
            st.button("當前方案 (免費)", disabled=True, use_container_width=True)

    with col_p2:
        st.markdown("""
<div style="background:linear-gradient(135deg, #FFFDF9 0%, #FAF0E1 100%); border:2.5px solid #C2995F; border-radius:20px; padding:1.5rem; text-align:center; box-shadow:0 8px 24px rgba(194,153,95,0.18); height:100%;">
    <div style="background:#C2995F; color:white; font-size:0.72rem; padding:2px 10px; border-radius:12px; display:inline-block; margin-bottom:0.3rem;">熱門推薦 🔥</div>
    <div style="font-size:1.1rem; font-weight:700; color:#533E2D;">👑 VIP 守護月度訂閱</div>
    <div style="font-size:1.8rem; font-weight:700; color:#C2995F; margin:0.6rem 0;">NT$ 149 <span style="font-size:0.85rem; color:#8C735A;">/ 月</span></div>
    <div style="font-size:0.82rem; color:#5C4A38; text-align:left; line-height:1.8;">
        ✓ 解鎖全 10 隻心理學動物<br>
        ✓ 無限制 24/7 深度諮商對話<br>
        ✓ 每週 AI 深度情緒體檢週報<br>
        ✓ 心靈小屋全套家具解鎖<br>
        ✓ 432Hz 頌缽高階無損音療
    </div>
</div>
""", unsafe_allow_html=True)
        if not current_user["is_vip"]:
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
        ✓ 專屬心靈小屋「璀璨星空屋頂」
    </div>
</div>
""", unsafe_allow_html=True)
        if not current_user["is_vip"]:
            if st.button("💎 升級 VIP 年度方案 (NT$990/年)", key="btn_upgrade_vip_year", use_container_width=True):
                conn = db.get_db_connection()
                conn.cursor().execute("UPDATE users SET is_vip = 1, star_coins = star_coins + 1000 WHERE id = ?", (CURRENT_USER_ID,))
                conn.commit()
                conn.close()
                st.balloons()
                st.success("🎉 恭喜升級為 VIP 年度守護會員！已解鎖全套特權與 1000 🌟星光幣！")
                st.rerun()

    # 商業合規與免責聲明頁腳
    st.markdown("""
<div style="margin-top:2.5rem; padding:1.2rem; background:rgba(255,255,255,0.7); border-radius:14px; border:1px solid #EADECE; font-size:0.78rem; color:#8C735A; line-height:1.6; text-align:center;">
    <strong>🛡️ 專業心靈陪伴合規聲明 (Health & Legal Disclaimer)：</strong><br>
    本應用程式為心理學正念同理心陪伴與身心減壓輔助工具，絕不提供任何醫療診斷、精神科處方或法律諮詢建議。若您面臨緊急危機或嚴重身心困擾，請即刻尋求當地專業合格之醫療與心理諮商機構協助。
</div>
""", unsafe_allow_html=True)
