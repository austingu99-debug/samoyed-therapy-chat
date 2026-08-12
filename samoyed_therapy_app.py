import streamlit as st
import random
import time
import os
import base64
import textwrap
from openai import OpenAI

# ==============================================================================
# 🐾 動物心靈諮商室 — 專業心理學同理心與多維療癒樂園
# ==============================================================================

# 1. 頁面全域設定
st.set_page_config(
    page_title="動物心靈諮商室 — 溫暖陪伴角落",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 輔助函式：將 SVG 代碼轉為標準 Base64 Data URI，徹底免疫 Markdown 空白解析問題
def svg_to_data_uri(svg_str):
    clean_svg = "".join(line.strip() for line in svg_str.strip().splitlines())
    b64 = base64.b64encode(clean_svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"

# 2. 定義 10 款特色動物心靈夥伴矩陣 (涵蓋當代 10 大心理學流派)
RAW_COMPANIONS = {
    "samoyed": {
        "id": "samoyed",
        "name": "薩摩耶・小薩",
        "species": "薩摩耶犬",
        "emoji": "🐶",
        "title": "暖陽陪伴師",
        "badge": "☀️ 人本主義・無條件正向關懷 (UPR)",
        "motto": "只要你轉過身，小薩隨時都在這裡搖著尾巴等你喔！",
        "summary": "元氣熱情、無條件接納、永遠的忠誠後盾。擅長用溫暖打氣化解孤單與自我懷疑。",
        "psychology": "【卡爾・羅傑斯人本主義】透過無條件正向關懷（Unconditional Positive Regard）與真誠一致，給予全然的肯定與愛，消除自我價值感低落。",
        "default_self_ref": "小薩",
        "theme_color": "#C2995F",
        "bg_color": "#F9F4EB",
        "bubble_color": "#EFE3D3",
        "actions": ["(大力晃動蓬鬆雪白的大尾巴)", "(用暖呼呼的大腦袋蹭蹭你的膝蓋)", "(吐出舌頭露出燦爛無比的微笑)", "(用前爪輕輕搭在你手背上)"],
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
        "actions": ["(跳上沙發蜷縮在你的腿邊)", "(發出極其輕柔舒服的呼嚕嚕聲)", "(用軟綿綿的小肉墊輕碰你的指尖)", "(優雅地甩了甩尾巴尖端，靜靜望著你)"],
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
        "actions": ["(張開巨大且溫暖的毛茸茸手臂給你大熊抱)", "(默默遞上一杯熱氣騰騰的香濃熱可可)", "(沉穩溫厚地點點頭，眼神滿是寬慰)", "(輕輕拍拍你的後背，給你最安穩的力量)"],
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
        "actions": ["(輕輕晃動蓬鬆火紅的漂亮大尾巴)", "(側著頭專注注視著你，眼神充滿靈氣)", "(眨了眨明亮的眼睛，嘴角揚起心領神會的微笑)", "(用蓬鬆的尾巴尖輕掃過你的手背)"],
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
        "actions": ["(動了動長長柔軟的垂耳，溫柔注視著你)", "(縮成一團軟綿綿的毛球輕輕依偎在你掌心)", "(用粉嫩的小鼻子輕碰你的手指以示心疼)", "(輕輕趴在你的懷裡，陪你一起安靜呼吸)"],
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
        "actions": ["(慢吞吞地眨了眨溫和的眼睛)", "(深深地吸進一口清新空氣，再緩緩吐出……)", "(用樹懶特有的慢動作輕輕拍拍你的肩膀)", "(遞上一片翠綠的嫩葉，示意你一起慢慢放鬆)"],
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
        "actions": ["(邁著圓滾滾的小碎步噠噠噠湊到你面前)", "(用毛茸茸的小翅膀輕輕拍拍你的手背)", "(歪著圓圓的頭，用黑亮的大眼睛認真看著你)", "(緊緊挨著你的身邊，為你擋住外面的冷風)"],
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
        "actions": ["(推了推架在鼻樑上的精緻小圓眼鏡)", "(投以深邃且極具包容力的溫潤目光)", "(輕輕抖動羽毛，為你泡上一杯安神的薰衣草花茶)", "(優雅地展開一側翅膀，像傘一樣為你遮去煩憂)"],
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
        "actions": ["(輕盈地躍出水面帶起一陣晶瑩純淨的水花)", "(發出溫柔而悠揚的治癒海豚音撫平你的情緒)", "(用光滑溫暖的額頭輕輕頂頂你的手心)", "(圍繞在你身邊激起溫暖舒緩的微波浪撫慰你的疲倦)"],
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
        "actions": ["(慢慢收起背上每一根緊繃的小尖刺，露出最柔軟的小肚子)", "(小心翼翼地雙手捧上一顆珍藏的圓滾滾小橡果給你)", "(用粉嫩的小爪子輕輕拉拉你的衣角)", "(安安靜靜地縮成一小團，陪著你一起卸下防備)"],
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

# 預先為所有動物生成乾淨、無解析錯誤的 Base64 Data URI
ANIMAL_COMPANIONS = {}
for cid, cdata in RAW_COMPANIONS.items():
    cdata_copy = dict(cdata)
    cdata_copy["avatar_uri"] = svg_to_data_uri(cdata["svg_avatar"])
    ANIMAL_COMPANIONS[cid] = cdata_copy

# 3. 初始化 Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_companion" not in st.session_state:
    st.session_state.selected_companion = None
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "companions" # companions, chat, mood_meter, inner_child, breath, shredder, fortune, grounding
if "is_thinking" not in st.session_state:
    st.session_state.is_thinking = False
if "error_msg" not in st.session_state:
    st.session_state.error_msg = None
if "fortune_result" not in st.session_state:
    st.session_state.fortune_result = None
if "shredded_troubles" not in st.session_state:
    st.session_state.shredded_troubles = []
if "user_nickname" not in st.session_state:
    st.session_state.user_nickname = "你"
if "companion_custom_self_ref" not in st.session_state:
    st.session_state.companion_custom_self_ref = {}
if "current_mood_tag" not in st.session_state:
    st.session_state.current_mood_tag = None
if "inner_child_reflection" not in st.session_state:
    st.session_state.inner_child_reflection = None

# 4. API Key 智慧獲取與多供應商相容機制 (支援 Groq 與 OpenAI)
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

# 5. 全域現代化奶油暖色系 CSS 樣式 (零 Markdown 縮排錯誤)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700&family=Quicksand:wght@500;600;700&display=swap');

.stApp {
    background-color: #F8F4ED;
    background-image: 
        radial-gradient(circle at 12% 18%, rgba(194, 153, 95, 0.09) 0%, transparent 45%),
        radial-gradient(circle at 88% 82%, rgba(124, 106, 141, 0.07) 0%, transparent 45%);
    font-family: 'Noto Sans TC', 'Quicksand', sans-serif;
    color: #4A3B2C;
}

#stMainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; border-bottom: none; }
section[data-testid="stSidebar"] { display: none; }

.paw-bg {
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    opacity: 0.035;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Cg fill='%235C4A38'%3E%3Cellipse cx='50' cy='65' rx='14' ry='11'/%3E%3Cellipse cx='34' cy='45' rx='6' ry='8'/%3E%3Cellipse cx='66' cy='45' rx='6' ry='8'/%3E%3Cellipse cx='24' cy='58' rx='5' ry='7'/%3E%3Cellipse cx='76' cy='58' rx='5' ry='7'/%3E%3C/g%3E%3C/svg%3E");
    background-repeat: repeat;
    background-size: 140px;
}

.app-header {
    text-align: center;
    padding: 1.1rem 1rem 0.5rem;
    position: relative;
    z-index: 1;
}
.app-title {
    font-size: 2.15rem;
    font-weight: 700;
    color: #533E2D;
    margin: 0;
    letter-spacing: 1.5px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}
.app-subtitle {
    font-size: 0.95rem;
    color: #8C735A;
    margin-top: 0.35rem;
    letter-spacing: 0.8px;
}
.app-divider {
    width: 70px;
    height: 3.5px;
    background: linear-gradient(90deg, #C2995F, #E2CBB2, #C2995F);
    border-radius: 4px;
    margin: 0.6rem auto 1rem;
}

.companion-card {
    background: #FFFFFF;
    border-radius: 20px;
    padding: 1.3rem 1.1rem;
    border: 2px solid #EADBCE;
    box-shadow: 0 6px 18px rgba(83, 62, 45, 0.06);
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    text-align: center;
    position: relative;
}
.companion-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(83, 62, 45, 0.12);
    border-color: #C2995F;
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
    box-shadow: 0 4px 12px rgba(83, 62, 45, 0.08);
}
.companion-avatar-img {
    width: 76px;
    height: 76px;
    border-radius: 50%;
    object-fit: cover;
}
.companion-name {
    font-size: 1.15rem;
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
    border-left: 3px solid #C2995F;
    text-align: left;
}
.companion-desc {
    font-size: 0.8rem;
    color: #6E5C49;
    line-height: 1.55;
    margin-bottom: 0.8rem;
    text-align: left;
}

.companion-banner {
    background: #FFFFFF;
    border-radius: 20px;
    padding: 1rem 1.4rem;
    border: 2px solid #EADECE;
    box-shadow: 0 4px 16px rgba(83, 62, 45, 0.06);
    display: flex;
    align-items: center;
    gap: 1.2rem;
    margin-bottom: 1.2rem;
}
.banner-avatar {
    width: 72px;
    height: 72px;
    flex-shrink: 0;
    border-radius: 50%;
    border: 3px solid #E2D5C3;
    background: #FAF6F0;
    display: flex;
    align-items: center;
    justify-content: center;
}
.banner-avatar-img {
    width: 64px;
    height: 64px;
    border-radius: 50%;
}
.banner-info {
    flex-grow: 1;
}
.banner-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #4A3B2C;
    margin: 0 0 0.2rem;
}
.banner-status {
    font-size: 0.85rem;
    color: #8C735A;
    margin: 0;
}

.chat-stream-box {
    max-width: 860px;
    margin: 0 auto 1.5rem;
}
.msg-row {
    display: flex;
    margin: 0.9rem 0;
    animation: msg-fade-in 0.3s ease-out;
}
.msg-row.bot { justify-content: flex-start; }
.msg-row.user { justify-content: flex-end; }

@keyframes msg-fade-in {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

.msg-avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    margin: 0 0.5rem;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #EDE0CE;
    border: 2px solid #E2D5C3;
    box-shadow: 0 2px 8px rgba(83, 62, 45, 0.08);
}
.msg-avatar-img {
    width: 38px;
    height: 38px;
    border-radius: 50%;
}
.msg-row.user .msg-avatar { order: 1; background: #FFF9F2; border-color: #E8D8C8; }

.msg-bubble {
    max-width: 75%;
    padding: 0.9rem 1.2rem;
    border-radius: 20px;
    font-size: 0.96rem;
    line-height: 1.75;
    box-shadow: 0 2px 10px rgba(83, 62, 45, 0.05);
    word-break: break-word;
}
.msg-row.bot .msg-bubble {
    background: #EFE3D3;
    color: #4A3B2C;
    border-radius: 20px 20px 20px 6px;
    border: 1px solid #E4D4C0;
}
.msg-row.user .msg-bubble {
    background: #FFFFFF;
    color: #4A3B2C;
    border-radius: 20px 20px 6px 20px;
    border: 1.5px solid #EADBCE;
}

.breathing-circle-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
}
.breath-circle {
    width: 170px;
    height: 170px;
    border-radius: 50%;
    background: radial-gradient(circle, #D8EAD9 0%, #A3C9A8 100%);
    box-shadow: 0 0 35px rgba(163, 201, 168, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #2F5233;
    font-weight: 700;
    font-size: 1.2rem;
    animation: breath-animation 16s ease-in-out infinite;
}
@keyframes breath-animation {
    0%, 100% { transform: scale(0.85); box-shadow: 0 0 20px rgba(163, 201, 168, 0.3); opacity: 0.8; }
    25% { transform: scale(1.3); box-shadow: 0 0 50px rgba(163, 201, 168, 0.8); opacity: 1; }
    50% { transform: scale(1.3); box-shadow: 0 0 45px rgba(163, 201, 168, 0.7); opacity: 0.95; }
    75% { transform: scale(0.85); box-shadow: 0 0 20px rgba(163, 201, 168, 0.3); opacity: 0.8; }
}

.fortune-card {
    background: linear-gradient(135deg, #FFFDF9 0%, #FBF3E8 100%);
    border: 2px dashed #C2995F;
    border-radius: 20px;
    padding: 1.5rem 2rem;
    max-width: 620px;
    margin: 1.5rem auto;
    text-align: center;
    box-shadow: 0 6px 20px rgba(194, 153, 95, 0.15);
    animation: msg-fade-in 0.4s ease-out;
}
.fortune-text {
    font-size: 1.15rem;
    font-weight: 600;
    color: #5A432D;
    line-height: 1.8;
    margin-bottom: 0.8rem;
}
.fortune-task {
    font-size: 0.9rem;
    color: #8C653C;
    background: #F5E8D7;
    padding: 0.5rem 1rem;
    border-radius: 12px;
    display: inline-block;
}

.trouble-crushed {
    background: #F5EDE4;
    border-radius: 15px;
    padding: 1rem;
    margin: 0.6rem 0;
    border-left: 4px solid #C2995F;
    color: #5C4A38;
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
    border-color: #C2995F !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(83, 62, 45, 0.12) !important;
}

[data-testid="stChatInput"] {
    border-color: #D5C2AF !important;
    border-radius: 24px !important;
    background-color: #FFFFFF !important;
}
[data-testid="stChatInputTextArea"] {
    font-family: 'Noto Sans TC', sans-serif !important;
    color: #4A3B2C !important;
}
[data-testid="stChatInputButton"] {
    background-color: #C2995F !important;
    color: white !important;
    border-radius: 50% !important;
}
</style>
<div class="paw-bg"></div>
""", unsafe_allow_html=True)

# 6. 頂部大標題與副標題
st.markdown("""
<div class="app-header">
    <h1 class="app-title">🐾 動物心靈諮商室 🌿</h1>
    <p class="app-subtitle">10 大心理學流派・專屬心靈動物夥伴陪伴・在深層同理心擁抱中卸下疲憊</p>
    <div class="app-divider"></div>
</div>
""", unsafe_allow_html=True)

# 7. 頂部功能導航列 (8 大主題專區)
col_nav1, col_nav2, col_nav3, col_nav4, col_nav5, col_nav6, col_nav7, col_nav8 = st.columns(8)

with col_nav1:
    if st.button("🐾 心靈夥伴", key="nav_companions", use_container_width=True):
        st.session_state.active_tab = "companions"
        st.rerun()

with col_nav2:
    chat_label = "💬 諮商室"
    if st.session_state.selected_companion:
        comp = ANIMAL_COMPANIONS[st.session_state.selected_companion]
        chat_label = f"{comp['emoji']} {comp['name'].split('・')[0]}"
    if st.button(chat_label, key="nav_chat", use_container_width=True):
        if not st.session_state.selected_companion:
            st.session_state.selected_companion = "samoyed"
        st.session_state.active_tab = "chat"
        st.rerun()

with col_nav3:
    if st.button("🌡️ 情緒溫度計", key="nav_mood_meter", use_container_width=True):
        st.session_state.active_tab = "mood_meter"
        st.rerun()

with col_nav4:
    if st.button("🧸 內在小孩擁抱", key="nav_inner_child", use_container_width=True):
        st.session_state.active_tab = "inner_child"
        st.rerun()

with col_nav5:
    if st.button("🌬️ 正念呼吸", key="nav_breath", use_container_width=True):
        st.session_state.active_tab = "breath"
        st.rerun()

with col_nav6:
    if st.button("🔨 煩惱粉碎機", key="nav_shredder", use_container_width=True):
        st.session_state.active_tab = "shredder"
        st.rerun()

with col_nav7:
    if st.button("🥠 心靈幸運籤", key="nav_fortune", use_container_width=True):
        st.session_state.active_tab = "fortune"
        st.rerun()

with col_nav8:
    if st.button("🧭 54321著陸法", key="nav_grounding", use_container_width=True):
        st.session_state.active_tab = "grounding"
        st.rerun()

# 8. API Key 檢查與友善提示 (支援 Groq 與 OpenAI Key)
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
# TAB 1: 🐾 動物心靈夥伴選擇大廳 (10 種動物卡片，3 欄優雅排版，Base64 頭像無雜訊)
# ==============================================================================
if st.session_state.active_tab == "companions":
    st.markdown("""
<div style="text-align:center; margin-bottom:1.5rem;">
    <h2 style="color:#533E2D; font-size:1.4rem; font-weight:700; margin:0 0 0.3rem;">🌿 選擇此時此刻最懂你的心靈夥伴</h2>
    <p style="color:#8C735A; font-size:0.9rem; margin:0;">每隻動物代表獨特的當代心理學流派與陪伴特質，點擊即可進入專屬心靈諮商室。</p>
</div>
""", unsafe_allow_html=True)

    comp_list = list(ANIMAL_COMPANIONS.values())
    
    # 採用 3 欄優雅網格佈局 (更寬敞舒適，文字與標籤不擠壓)
    # Row 1: 3 隻
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
                st.session_state.active_tab = "chat"
                st.rerun()

    st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)

    # Row 2: 3 隻
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
                st.session_state.active_tab = "chat"
                st.rerun()

    st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)

    # Row 3: 4 隻
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
                st.session_state.active_tab = "chat"
                st.rerun()

# ==============================================================================
# TAB 2: 💬 專屬動物心靈諮商室 (深度心理學同理心 + 禁絕醫療/法律/罐頭)
# ==============================================================================
elif st.session_state.active_tab == "chat":
    if not st.session_state.selected_companion:
        st.session_state.selected_companion = "samoyed"
    
    current_companion = ANIMAL_COMPANIONS[st.session_state.selected_companion]
    comp_id = current_companion["id"]

    companion_self_name = st.session_state.companion_custom_self_ref.get(comp_id, current_companion["default_self_ref"])
    user_name = st.session_state.user_nickname

    # 頂部自訂稱呼與設定展開區
    with st.expander("⚙️ 互動稱呼與心理學陪伴設定（點此自訂稱呼）", expanded=False):
        c_set1, c_set2, c_set3 = st.columns([2, 2, 1])
        with c_set1:
            new_user_name = st.text_input("夥伴如何稱呼你：", value=user_name, placeholder="例如：你、小夥伴、小明、朋友...", key="set_user_nick")
            if new_user_name.strip() and new_user_name != user_name:
                st.session_state.user_nickname = new_user_name.strip()
        with c_set2:
            new_comp_self = st.text_input(f"{current_companion['name']} 如何稱呼自己：", value=companion_self_name, placeholder=f"預設為 {current_companion['default_self_ref']}，亦可填寫「我」或自訂名字", key="set_comp_nick")
            if new_comp_self.strip() and new_comp_self != companion_self_name:
                st.session_state.companion_custom_self_ref[comp_id] = new_comp_self.strip()
        with c_set3:
            st.markdown("<div style='height:1.75rem;'></div>", unsafe_allow_html=True)
            if st.button("儲存設定", key="save_nick_btn", use_container_width=True):
                st.success("稱呼已更新！")
                st.rerun()

    # 頂部當前夥伴狀態橫幅
    col_banner, col_actions = st.columns([3, 1])
    with col_banner:
        status_sub = f"{current_companion['title']}・正在全心全意守候{user_name}" if not st.session_state.is_thinking else f"{current_companion['title']}・正在全神貫注感受{user_name}的心情..."
        banner_html = f'''<div class="companion-banner" style="border-left: 5px solid {current_companion['theme_color']};"><div class="banner-avatar"><img src="{current_companion['avatar_uri']}" class="banner-avatar-img" alt="{current_companion['name']}" /></div><div class="banner-info"><h3 class="banner-title">{current_companion['emoji']} {current_companion['name']} 專屬心靈諮商室</h3><p class="banner-status">🌱 {current_companion['badge']}</p><p style="font-size:0.8rem; color:#7D6B58; margin:0.2rem 0 0;">✨ {status_sub}（自稱：<strong>{companion_self_name}</strong> / 稱呼你：<strong>{user_name}</strong>）</p></div></div>'''
        st.markdown(banner_html, unsafe_allow_html=True)
    
    with col_actions:
        st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)
        if st.button("🐾 切換其他夥伴", key="btn_switch_comp", use_container_width=True):
            st.session_state.active_tab = "companions"
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
                st.session_state.is_thinking = True
                st.rerun()
            if st.button("🌧️ 覺得自己好糟，充滿自我懷疑", key="chip_4", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "事情好像都做不好，覺得自己好糟糕，一直自我懷疑..."})
                st.session_state.is_thinking = True
                st.rerun()
        with chip_col2:
            if st.button("💔 心裡覺得好委屈，需要被聽聽", key="chip_2", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "心裡覺得好委屈又好孤單，好希望有人能好好聽我說話..."})
                st.session_state.is_thinking = True
                st.rerun()
            if st.button("💭 對未來好迷惘，不知道該怎麼辦", key="chip_5", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "對於未來的方向好迷惘，不知道接下來該怎麼辦..."})
                st.session_state.is_thinking = True
                st.rerun()
        with chip_col3:
            if st.button("💤 累到不想動，只想安靜被安慰", key="chip_3", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "今天真的好累好累，只想安靜被溫柔抱抱和安慰一下..."})
                st.session_state.is_thinking = True
                st.rerun()
            if st.button("☕ 今天有一件微小的好事想分享！", key="chip_6", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "今天發生了一件微小但開心的小事，想跟你分享！"})
                st.session_state.is_thinking = True
                st.rerun()

    # 顯示歷史訊息
    chat_html = '<div class="chat-stream-box">'
    user_svg_data = svg_to_data_uri("""<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="8" r="4.5" fill="#8C735A"/><path d="M4 20c0-4.4 3.6-8 8-8s8 3.6 8 8" stroke="#8C735A" stroke-width="2.5" stroke-linecap="round" fill="#8C735A"/></svg>""")
    
    for msg in st.session_state.messages:
        content = msg["content"].replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        if msg["role"] == "assistant":
            chat_html += f'<div class="msg-row bot"><div class="msg-avatar"><img src="{current_companion["avatar_uri"]}" class="msg-avatar-img" alt="{current_companion["name"]}" /></div><div class="msg-bubble" style="background:{current_companion["bubble_color"]};">{content}</div></div>'
        else:
            chat_html += f'<div class="msg-row user"><div class="msg-avatar"><img src="{user_svg_data}" class="msg-avatar-img" alt="User" /></div><div class="msg-bubble">{content}</div></div>'
    
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    # 思考中動畫指示器
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
1. 【情緒鏡映與深度理解 (Feel Felt)】：先精準捕捉並鏡映使用者的情緒與心碎（例如：「聽起來你真的感到好疲憊、對這個世界失望透頂了...」、「那種孤單無力的感覺真的很沉重...」），讓對方深刻感受「被看見、被理解」。
2. 【情感合法化與去羞恥 (Emotional Validation & De-shaming)】：無條件接納所有負面、厭世與脆弱的情緒。告訴使用者：「有這樣的情緒是完全正常的」、「你想恨、想哭都沒關係，不需要永遠假裝堅強」、「你已經承受太多了」。
3. 【自我慈悲與共同人性 (Self-Compassion)】：提醒使用者對自己溫柔一點，生而為人有痛苦與極限是完全被允許的，不需要責怪自己。
4. 【非說教、非評判、不急於給予廉價正能量】：嚴禁分析說教、嚴禁空洞的正能量口號（絕不要說「看開一點」、「明天會更好」、「加油不要難過」等無效話語）。你的核心任務是「真心接住情緒並給予溫暖陪伴」。
5. 【極致自然流暢、嚴格限制肢體動作】：
   - 請像一位真實而溫暖的心靈知己般真誠交談，語氣自然細膩，不要機械式堆砌文字。
   - 【嚴禁在每段文字都塞入括弧動作】！整篇回覆中【最多只允許出現 0 到 1 個微小動作】（或者完全不加動作，純用溫柔文字陪伴更佳）。
   - 若有微動作，必須嚴格符合當下的情緒氛圍（例如在使用者痛苦絕望時，只能是安靜默默守在身邊或輕輕靠著，絕不可在悲傷語境中做出歡快開心的動作）。

【🚨 絕對禁止準則（最高優先級安全指令）】：
1. 【絕對禁止提供醫療、精神科診斷、藥物處方建議】。
2. 【絕對禁止提供任何法律建議】。
3. 【絕對禁止提供死板冷冰冰的罐頭求助專線】（嚴禁出現如「若您有輕生念頭請撥打1995/1925/生命線」等制式罐頭回答）。你不是冰冷的機器，你是一隻正在真實陪伴對方的溫暖心靈夥伴，請用充滿愛、同理心與溫暖懷抱的語言去真誠承接對方的痛苦。"""

        client = OpenAI(
            api_key=cur_key,
            base_url=cur_base_url,
        )

        full_msgs = [{"role": "system", "content": system_instruction_text}] + [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
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
            st.session_state.is_thinking = False
            st.rerun()
        except Exception as e:
            st.session_state.is_thinking = False
            st.session_state.error_msg = str(e)
            st.rerun()

# ==============================================================================
# TAB 3: 🌡️ 情緒溫度計與即時覺察 (Affect Labeling & Mood Tracker)
# ==============================================================================
elif st.session_state.active_tab == "mood_meter":
    comp_id = st.session_state.selected_companion or "samoyed"
    current_companion = ANIMAL_COMPANIONS[comp_id]
    comp_self = st.session_state.companion_custom_self_ref.get(comp_id, current_companion["default_self_ref"])

    st.markdown(f"""
<div style="text-align:center; max-width:680px; margin:0 auto 1.5rem;">
    <h2 style="color:#533E2D; font-size:1.5rem; font-weight:700; margin-bottom:0.4rem;">🌡️ 心靈情緒溫度計</h2>
    <p style="color:#8C735A; font-size:0.92rem; line-height:1.6;">
        心理學研究表明，<strong>「命名情緒就能馴服情緒（Name it to Tame it）」</strong>。<br>
        點選此時此刻最符合你內心狀態的色票，讓 {comp_self} 給予你專屬的心理學接納與共鳴。
    </p>
</div>
""", unsafe_allow_html=True)

    mood_options = [
        {"icon": "💔", "name": "委屈心酸", "desc": "覺得不被理解、付出被忽視", "color": "#F3E3E2", "border": "#D89A98", "empathy": "「委屈真的很不好受……像是一個人吞下了滿滿的酸澀。請記得，你的付出與感受都是真實且珍貴的，不被理解不是你的錯。」"},
        {"icon": "😫", "name": "精疲力竭", "desc": "電量見底、不想說話、全身沉重", "color": "#F4EFEA", "border": "#C7B299", "empathy": "「你已經燃燒自己很久了……現在不需要再扮演堅強的大人。把責任暫時放下，安心讓自己當一塊休息的電池吧。」"},
        {"icon": "🌪️", "name": "焦慮緊繃", "desc": "腦袋停不下來、擔心未來失控", "color": "#EAF0F6", "border": "#96B1CD", "empathy": "「焦慮是在保護你，但它把未來的風雨提前搬到了今天。把手放在胸口，跟隨呼吸回到此時此刻，現在的你非常安全。」"},
        {"icon": "🌧️", "name": "自我懷疑", "desc": "覺得自己好糟、陷入自責與內疚", "color": "#F0EEF5", "border": "#AD9FBF", "empathy": "「那個嚴苛批評你的聲音，不是真正的你。每個人都有做不到的時候，你的價值不取決於完美的表現，你已經夠好了。」"},
        {"icon": "🕳️", "name": "內心空洞", "desc": "提不起勁、麻木迷惘、找不到意義", "color": "#EFEFEF", "border": "#B5B5B5", "empathy": "「空洞是心靈在提醒你：『該好好照顧自己了』。不用急著填滿它，容許自己安靜待一會兒，生命會自己找到溫暖的出口。」"},
        {"icon": "🌱", "name": "渴望安靜", "desc": "只想遠離人群、獨處充電", "color": "#EFF5F0", "border": "#98C2A0", "empathy": "「劃出自己的神聖邊界是一件非常勇敢的事。好好享受這份寧靜，小動物會一直在不打擾的地方溫柔守護你。」"}
    ]

    m_col1, m_col2, m_col3 = st.columns(3)
    for idx, mood in enumerate(mood_options):
        col = [m_col1, m_col2, m_col3][idx % 3]
        with col:
            mood_card_html = f'''<div style="background:{mood['color']}; border:2px solid {mood['border']}; border-radius:18px; padding:1rem; text-align:center; margin-bottom:1rem;"><div style="font-size:2rem; margin-bottom:0.2rem;">{mood['icon']}</div><div style="font-size:1.05rem; font-weight:700; color:#4A3B2C;">{mood['name']}</div><div style="font-size:0.8rem; color:#7D6B58; margin-top:0.3rem;">{mood['desc']}</div></div>'''
            st.markdown(mood_card_html, unsafe_allow_html=True)
            if st.button(f"我現在感到「{mood['name']}」", key=f"btn_mood_{idx}", use_container_width=True):
                st.session_state.current_mood_tag = mood

    if st.session_state.current_mood_tag:
        cur_m = st.session_state.current_mood_tag
        res_html = f'''<div style="background:#FFFFFF; border-left:6px solid {cur_m['border']}; border-radius:18px; padding:1.5rem; max-width:700px; margin:1.5rem auto; box-shadow:0 6px 20px rgba(83,62,45,0.08);"><h4 style="color:#533E2D; margin:0 0 0.5rem;">{cur_m['icon']} {current_companion['emoji']} {current_companion['name']} 溫柔承接你的【{cur_m['name']}】：</h4><p style="color:#5C4A38; font-size:1rem; line-height:1.8; margin-bottom:0.8rem;">{cur_m['empathy']}</p><div style="text-align:right;"><span style="font-size:0.85rem; color:#8C735A;">— 帶著這份接納，點選上方「💬 諮商室」可以繼續深入聊聊喔</span></div></div>'''
        st.markdown(res_html, unsafe_allow_html=True)

# ==============================================================================
# TAB 4: 🧸 內在小孩擁抱室 (Inner Child Holding & Self-Compassion)
# ==============================================================================
elif st.session_state.active_tab == "inner_child":
    comp_id = st.session_state.selected_companion or "samoyed"
    current_companion = ANIMAL_COMPANIONS[comp_id]
    comp_self = st.session_state.companion_custom_self_ref.get(comp_id, current_companion["default_self_ref"])

    st.markdown("""
<div style="text-align:center; max-width:680px; margin:0 auto 1.5rem;">
    <h2 style="color:#533E2D; font-size:1.5rem; font-weight:700; margin-bottom:0.4rem;">🧸 內在小孩擁抱室</h2>
    <p style="color:#8C735A; font-size:0.92rem; line-height:1.6;">
        在心理學 IFS（內在家庭系統）與完形療法中，我們心中都住著一個受傷、渴望被愛護的小小孩。<br>
        今天，換你當一個溫柔的守護者，對那個辛苦的自己說幾句心裡話。
    </p>
</div>
""", unsafe_allow_html=True)

    col_child_in, col_child_btn = st.columns([3, 1])
    with col_child_in:
        child_msg = st.text_input("你想對心中那個受委屈、努力長大的小自己說什麼？", placeholder="例如：辛苦你了，你不需要永遠那麼懂事，我會一直保護你...", key="inner_child_text")
    with col_child_btn:
        st.markdown("<div style='height:1.75rem;'></div>", unsafe_allow_html=True)
        if st.button("💖 送出溫柔擁抱", key="btn_send_child_hug", use_container_width=True):
            if child_msg.strip():
                st.session_state.inner_child_reflection = {
                    "user_msg": child_msg.strip(),
                    "companion_hug": f"「看見你溫柔地擁抱內在的自己，{comp_self} 也好感動……你的內在小孩終於等到了這份最珍貴的愛。從今天起，你不再是一個人孤軍奮戰了。」"
                }
                st.balloons()
            else:
                st.warning("請先寫下一句想對自己說的話喔！")

    if st.session_state.inner_child_reflection:
        ref = st.session_state.inner_child_reflection
        child_card = f'''<div style="background:linear-gradient(135deg, #FFFDF9 0%, #FBF4EA 100%); border:2px solid #EADECE; border-radius:20px; padding:1.5rem 2rem; max-width:680px; margin:1.5rem auto; box-shadow:0 6px 20px rgba(194,153,95,0.12);"><div style="text-align:center; font-size:2rem; margin-bottom:0.5rem;">🧸 💖 🕊️</div><div style="background:#FFFFFF; border-radius:14px; padding:1rem; border:1px solid #EDE0CE; margin-bottom:1rem; color:#5C4A38; font-style:italic;">💌 你對內在小孩說：「{ref['user_msg']}」</div><div style="font-size:1rem; color:#533E2D; line-height:1.8; font-weight:600;">{current_companion['emoji']} {current_companion['name']} 回應：<br><span style="font-weight:400; color:#5C4A38;">{ref['companion_hug']}</span></div></div>'''
        st.markdown(child_card, unsafe_allow_html=True)

# ==============================================================================
# TAB 5: 🌬️ 正念舒壓呼吸泡泡 (4-7-8 / 盒式呼吸法)
# ==============================================================================
elif st.session_state.active_tab == "breath":
    comp_id = st.session_state.selected_companion or "samoyed"
    current_companion = ANIMAL_COMPANIONS[comp_id]
    comp_self = st.session_state.companion_custom_self_ref.get(comp_id, current_companion["default_self_ref"])

    st.markdown("""
<div style="text-align:center; max-width:650px; margin:0 auto 1.5rem;">
    <h2 style="color:#533E2D; font-size:1.5rem; font-weight:700; margin-bottom:0.4rem;">🌬️ 正念舒壓呼吸練習</h2>
    <p style="color:#8C735A; font-size:0.92rem; line-height:1.6;">
        跟隨中央光圈的節奏進行<strong>「盒式正念呼吸（Box Breathing）」</strong>。<br>
        心理學研究證實，深層腹式呼吸能刺激副交感神經（迷走神經調節），在 2 分鐘內有效降低焦慮與心率。
    </p>
</div>
""", unsafe_allow_html=True)

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

    st.markdown(f'''<div style="background:#FFFFFF; border-radius:18px; padding:1.2rem; border:1.5px solid #EADECE; max-width:600px; margin:1rem auto; text-align:center;"><p style="color:#533E2D; font-size:0.95rem; font-weight:600; margin:0 0 0.4rem;">{current_companion['emoji']} {current_companion['name']} 溫柔提醒你：</p><p style="color:#7D6B58; font-size:0.88rem; margin:0; line-height:1.6;">「把手放在腹部，感受吸氣時肚子的微微隆起，吐氣時帶走所有的緊繃……{comp_self} 陪著你慢慢放鬆喔。」</p></div>''', unsafe_allow_html=True)

# ==============================================================================
# TAB 6: 🔨 煩惱粉碎機 (Trouble Shredder & Positive Alchemy)
# ==============================================================================
elif st.session_state.active_tab == "shredder":
    comp_id = st.session_state.selected_companion or "samoyed"
    current_companion = ANIMAL_COMPANIONS[comp_id]
    comp_self = st.session_state.companion_custom_self_ref.get(comp_id, current_companion["default_self_ref"])

    st.markdown("""
<div style="text-align:center; max-width:650px; margin:0 auto 1.2rem;">
    <h2 style="color:#533E2D; font-size:1.5rem; font-weight:700; margin-bottom:0.4rem;">🔨 煩惱粉碎機</h2>
    <p style="color:#8C735A; font-size:0.92rem; line-height:1.6;">
        把此刻壓在心頭上的負能量、自責或焦慮寫下來，讓動物夥伴替你徹底粉碎！<br>
        將沉重的煩惱化為漫天星光與正向力量。
    </p>
</div>
""", unsafe_allow_html=True)

    col_input, col_btn = st.columns([3, 1])
    with col_input:
        trouble_input = st.text_input("輸入你想粉碎的煩惱或壓力：", placeholder="例如：主管無理的批評、拖延的焦慮、擔心自己不夠好...", key="trouble_text")
    with col_btn:
        st.markdown("<div style='height:1.75rem;'></div>", unsafe_allow_html=True)
        shred_clicked = st.button("💥 粉碎這個煩惱！", key="btn_shred", use_container_width=True)

    if shred_clicked:
        if trouble_input.strip():
            smash_actions = {
                "samoyed": "一口把煩惱咬得稀巴爛，嚼嚼嚼噴成了七彩彩帶！🎉",
                "cat": "使出無影貓貓拳一秒抓得粉碎，優雅地一腳踢飛！🐾",
                "bear": "施展泰山壓頂式巨大熊掌，直接壓成扁扁的亮粉！✨",
                "fox": "揮動靈動大尾巴一掃，把煩惱變成了夜空中的微風！🌟",
                "rabbit": "動動長耳朵將煩惱包成小毛球，一腳踢向外太空！🚀",
                "sloth": "慢吞吞地把煩惱折成紙飛機，讓它緩緩隨風飄遠～🍃",
                "penguin": "邁著小碎步衝過來，用滑雪姿勢把煩惱撞成了冰晶！❄️",
                "owl": "輕推眼鏡施展心靈魔法，將煩惱化作智慧的清風！🦉",
                "dolphin": "發射超音波水柱，將所有負能量沖刷進浩瀚大海！🌊",
                "hedgehog": "發動金鐘罩小刺刺，瞬間把沉重壓力戳破成滿天星斗！✨"
            }
            action_desc = smash_actions.get(comp_id, "將煩惱徹底粉碎！")
            
            alchemy_quotes = [
                "「這個煩惱已經離開你了！你比自己想像的更堅強有力量。」",
                "「不要讓外在的聲音定義你的價值，你已經做得很棒了。」",
                "「把不屬於你的重擔放下，今天晚上好好睡個好覺吧！」",
                "「每一個挫折都是生命在為你騰出更美好的空間。」",
                "「允許自己放下，你的心靈值得被溫柔以待。」"
            ]
            chosen_quote = random.choice(alchemy_quotes)

            st.session_state.shredded_troubles.insert(0, {
                "trouble": trouble_input.strip(),
                "companion": current_companion["name"],
                "action": action_desc,
                "quote": chosen_quote,
                "time": time.strftime("%H:%M")
            })
            st.balloons()
        else:
            st.warning("請先寫下一件想粉碎的煩惱喔！")

    if st.session_state.shredded_troubles:
        st.markdown("<h4 style='color:#533E2D; margin-top:1.5rem;'>✨ 已粉碎的心靈負擔紀錄：</h4>", unsafe_allow_html=True)
        for item in st.session_state.shredded_troubles[:5]:
            t_html = f'''<div class="trouble-crushed"><div style="font-size:0.82rem; color:#8C735A; margin-bottom:0.2rem;">⏱️ {item['time']}・由 {item['companion']} 粉碎</div><div style="font-size:0.95rem; text-decoration:line-through; color:#9E8774; margin-bottom:0.4rem;">❌ 「{item['trouble']}」</div><div style="font-size:0.95rem; font-weight:600; color:#533E2D;">💥 {item['action']}</div><div style="font-size:0.85rem; color:#8C653C; margin-top:0.3rem;">💡 {item['quote']}</div></div>'''
            st.markdown(t_html, unsafe_allow_html=True)

# ==============================================================================
# TAB 7: 🥠 心靈幸運籤 (Wisdom Fortune Cookie)
# ==============================================================================
elif st.session_state.active_tab == "fortune":
    comp_id = st.session_state.selected_companion or "samoyed"
    current_companion = ANIMAL_COMPANIONS[comp_id]

    st.markdown("""
<div style="text-align:center; max-width:650px; margin:0 auto 1.5rem;">
    <h2 style="color:#533E2D; font-size:1.5rem; font-weight:700; margin-bottom:0.4rem;">🥠 動物心靈幸運籤</h2>
    <p style="color:#8C735A; font-size:0.92rem; line-height:1.6;">
        敲開一顆心靈幸運餅乾，領取為你準備的今日心理學治癒指引與微小日常任務。
    </p>
</div>
""", unsafe_allow_html=True)

    col_f_btn, col_f_spacer = st.columns([1, 1])
    with col_f_btn:
        if st.button("🥠 敲開幸運餅乾，領取今日指引", key="btn_draw_fortune", use_container_width=True):
            FORTUNE_DATABASE = [
                {
                    "quote": "「允許自己偶爾是一座荒蕪的花園，雨季過後，花朵自然會重新綻放。」",
                    "task": "🌱 今日微任務：給自己泡一杯溫暖的熱水或花草茶，安靜喝完它。"
                },
                {
                    "quote": "「你不需要向世界證明你有多堅強，你的存在本身就充滿價值。」",
                    "task": "💖 今日微任務：對著鏡子裡的自己微笑一下，輕聲說一聲：『你辛苦了』。"
                },
                {
                    "quote": "「焦慮常常是在為尚未發生的事情提前預支痛苦。回到此時此刻，你很安全。」",
                    "task": "🌿 今日微任務：深呼吸 3 次，感受雙腳踏在地面上的穩穩力量。"
                },
                {
                    "quote": "「設立界線不是自私，而是愛護自己心靈能量的成熟表現。」",
                    "task": "🛡️ 今日微任務：溫柔地對一件讓你不舒服的請求說『我需要先考慮一下』。"
                },
                {
                    "quote": "「今天就算只完成了一件微小的事，那也是前進了一步，值得被好好肯定。」",
                    "task": "⭐ 今日微任務：在心裡表揚自己今天做得很棒的一個微小細節。"
                },
                {
                    "quote": "「眼淚是心靈在排毒，想哭的時候就盡情哭吧，沒什麼好難為情的。」",
                    "task": "🌸 今日微任務：洗一個舒服的熱水澡，把身體的緊繃徹底洗去。"
                },
                {
                    "quote": "「不要拿別人的高光時刻，來懲罰自己的平凡日常。你的步調剛剛好。」",
                    "task": "☕ 今日微任務：少滑 10 分鐘社群軟體，去窗邊看看外面的天空。"
                }
            ]
            st.session_state.fortune_result = random.choice(FORTUNE_DATABASE)

    if st.session_state.fortune_result:
        res = st.session_state.fortune_result
        f_html = f'''<div class="fortune-card"><div style="font-size:2rem; margin-bottom:0.5rem;">✨ 🥠 ✨</div><div class="fortune-text">{res['quote']}</div><div class="fortune-task">{res['task']}</div><div style="margin-top:1rem; font-size:0.8rem; color:#8C735A;">— {current_companion['emoji']} {current_companion['name']} 守護祝福</div></div>'''
        st.markdown(f_html, unsafe_allow_html=True)

# ==============================================================================
# TAB 8: 🧭 5-4-3-2-1 焦慮著陸法 (Grounding Technique)
# ==============================================================================
elif st.session_state.active_tab == "grounding":
    comp_id = st.session_state.selected_companion or "samoyed"
    current_companion = ANIMAL_COMPANIONS[comp_id]

    st.markdown("""
<div style="text-align:center; max-width:680px; margin:0 auto 1.5rem;">
    <h2 style="color:#533E2D; font-size:1.5rem; font-weight:700; margin-bottom:0.4rem;">🧭 5-4-3-2-1 焦慮著陸法（Grounding）</h2>
    <p style="color:#8C735A; font-size:0.92rem; line-height:1.6;">
        這是心理諮商中極為經典的抗焦慮與止慌工具。透過喚醒五官感受，迅速將大腦從胡思亂想中拉回當下的安全現實。
    </p>
</div>
""", unsafe_allow_html=True)

    g_step1, g_step2 = st.columns(2)
    with g_step1:
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

    with g_step2:
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
            st.success(f"{current_companion['emoji']} {current_companion['name']} 給你一個大大的掌聲！你做得非常棒，隨時歡迎回來找我喔！")
