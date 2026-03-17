import urllib.request
import json
import ssl
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import os
import html as html_module

# 서버에 존재하는 알려진 버전 목록 (사용자가 직접 입력도 가능)
VERSIONS = ["4.0", "4.0.52", "4.0.53", "4.0.54", "4.1.51"]

# 지원 언어 목록 {표시 이름: API 코드}
LANGUAGES = {
    "한국어": "ko",
    "English": "en",
    "日本語": "ja",
    "中文(简体)": "zh",
}

# 희귀도 → 성옥 보상 매핑
RARITY_TO_JADE = {
    "Low": 5,
    "Mid": 10,
    "High": 20,
}

# 성옥 아이콘 URL
JADE_ICON_URL = "https://static.nanoka.cc/assets/hsr/itemfigures/900001.webp"

# 시리즈 ID → honeyhunterworld slug 매핑 (언어에 상관없이 ID는 동일)
SERIES_SLUG_MAP = {
    "1": "i-trailblazer",
    "2": "vestige-of-luminflux",
    "3": "the-rail-unto-the-stars",
    "4": "fathom-the-unfathomable",
    "5": "the-memories-we-share",
    "6": "glory-of-the-unyielding",
    "7": "eager-for-battle",
    "8": "moment-of-joy",
    "9": "universe-in-a-nutshell",
}

def get_series_icon_url(series_id):
    """시리즈 ID로부터 아이콘 이미지 URL을 생성합니다."""
    slug = SERIES_SLUG_MAP.get(str(series_id), "")
    if slug:
        return f"https://starrail.honeyhunterworld.com/img/achievement_series/{slug}-achievement_series_icon.webp"
    return ""

def fetch_achievements(version, lang="ko"):
    """nanoka.cc에서 해당 버전의 업적 JSON을 가져옵니다."""
    url = f"https://static.nanoka.cc/hsr/{version}/{lang}/achievement/achievement.json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        response = urllib.request.urlopen(req, context=ctx)
        data = json.loads(response.read().decode('utf-8'))
        return data
    except urllib.error.URLError:
        return None
    except json.JSONDecodeError:
        return None

def extract_achievement_dict(data):
    """업적 ID를 키로, 업적 정보를 값으로 가지는 딕셔너리를 추출합니다."""
    achievements = {}
    if not data:
        return achievements

    for series_id, series_data in data.items():
        if not isinstance(series_data, dict) or 'list' not in series_data:
            continue

        series_name = series_data.get('name') or f'시리즈 {series_id}'
        for achievement in series_data['list']:
            ach_id = achievement.get('id')
            if ach_id:
                achievement['series_id'] = series_id
                achievement['series_name'] = series_name
                achievements[ach_id] = achievement

    return achievements

def generate_html_report(old_ver, new_ver, added_ids, new_achievements, old_count, new_count):
    """새로 추가된 업적 + 보상 + 시리즈 아이콘을 포함하는 HTML 리포트를 생성합니다."""

    # 시리즈별로 그룹핑 (시리즈 ID 기준으로 그룹핑하여 언어와 무관하게 아이콘 매핑)
    series_groups = {}  # {series_id: {'name': str, 'achs': list}}
    total_jade = 0
    for ach_id in added_ids:
        ach = new_achievements[ach_id]
        sid = ach.get('series_id', '0')
        series_name = ach.get('series_name') or f'Series {sid}'
        if sid not in series_groups:
            series_groups[sid] = {'name': series_name, 'achs': []}
        series_groups[sid]['achs'].append(ach)
        total_jade += RARITY_TO_JADE.get(ach.get('rarity', ''), 0)

    # 시리즈별 업적 카드 생성 (시리즈 ID 순서로 정렬)
    series_html = ""
    for sid, group in sorted(series_groups.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
        series_name = group['name']
        achs = group['achs']
        esc_name = html_module.escape(series_name)
        series_jade = sum(RARITY_TO_JADE.get(a.get('rarity', ''), 0) for a in achs)
        icon_url = get_series_icon_url(sid)
        icon_html = f'<img src="{icon_url}" alt="{esc_name}" class="series-icon"/>' if icon_url else ''

        series_html += f"""
        <div class="series-group">
            <div class="series-header">
                <div class="series-title">
                    {icon_html}
                    <h2>{esc_name} <span class="badge">{len(achs)}개</span></h2>
                </div>
                <div class="series-jade">
                    <img src="{JADE_ICON_URL}" alt="성옥" class="jade-icon-sm"/>
                    <span>{series_jade}</span>
                </div>
            </div>
        """
        for ach in achs:
            esc_ach_name = html_module.escape(ach.get('name') or '이름 없음')
            esc_desc = html_module.escape(ach.get('desc') or '설명 없음')
            rarity = ach.get('rarity') or 'Low'
            jade_amount = RARITY_TO_JADE.get(rarity, 5)
            rarity_class = rarity.lower()

            series_html += f"""
            <div class="achievement rarity-{rarity_class}">
                <div class="ach-left">
                    <div class="ach-header">
                        <span class="ach-name">{esc_ach_name}</span>
                        <span class="rarity-badge rarity-{rarity_class}">{rarity}</span>
                    </div>
                    <p class="ach-desc">{esc_desc}</p>
                </div>
                <div class="ach-reward">
                    <img src="{JADE_ICON_URL}" alt="성옥" class="jade-icon"/>
                    <span class="jade-amount">{jade_amount}</span>
                </div>
            </div>
            """
        series_html += "</div>"

    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>붕괴: 스타레일 업적 비교 ({old_ver} → {new_ver})</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
            background: linear-gradient(135deg, #0a0a1a 0%, #1a1040 40%, #0d1a2d 100%);
            color: #d8dce6;
            min-height: 100vh;
            padding: 30px 20px;
        }}
        .container {{ max-width: 960px; margin: 0 auto; }}

        /* --- Header --- */
        h1 {{
            text-align: center;
            font-size: 30px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 6px;
            text-shadow: 0 0 20px rgba(180,160,255,0.3);
        }}
        .subtitle {{
            text-align: center;
            font-size: 17px;
            color: #b0b8d0;
            margin-bottom: 30px;
            font-weight: 400;
        }}

        /* --- Summary Cards --- */
        .summary {{
            display: flex;
            justify-content: center;
            gap: 16px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }}
        .summary-card {{
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 18px 26px;
            text-align: center;
            min-width: 145px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .summary-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }}
        .summary-card .number {{
            font-size: 34px;
            font-weight: 700;
            display: block;
            line-height: 1.2;
        }}
        .summary-card .label {{
            font-size: 12px;
            color: #8890a8;
            margin-top: 5px;
            font-weight: 400;
        }}
        .num-old {{ color: #7ec8e3; }}
        .num-new {{ color: #98b8ff; }}
        .num-added {{ color: #6ee7a0; }}
        .num-jade {{ color: #ffc857; }}
        .jade-total-icon {{
            width: 30px; height: 30px;
            vertical-align: middle;
            margin-right: 2px;
        }}

        /* --- Series Group --- */
        .series-group {{
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 22px 24px;
            margin-bottom: 24px;
        }}
        .series-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 14px;
            margin-bottom: 16px;
            border-bottom: 1px solid rgba(255,255,255,0.08);
        }}
        .series-title {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .series-icon {{
            width: 48px;
            height: 48px;
            border-radius: 8px;
            border: 2px solid rgba(255,255,255,0.1);
            background: rgba(0,0,0,0.2);
            object-fit: contain;
        }}
        .series-header h2 {{
            font-size: 20px;
            color: #e0d4ff;
            font-weight: 600;
        }}
        .series-jade {{
            display: flex;
            align-items: center;
            gap: 5px;
            color: #ffc857;
            font-weight: 700;
            font-size: 16px;
        }}
        .jade-icon-sm {{ width: 24px; height: 24px; }}
        .badge {{
            display: inline-block;
            background: rgba(110,231,160,0.12);
            color: #6ee7a0;
            font-size: 13px;
            padding: 2px 10px;
            border-radius: 20px;
            font-weight: 500;
            vertical-align: middle;
            margin-left: 6px;
        }}

        /* --- Achievement Card --- */
        .achievement {{
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 14px 18px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            transition: background 0.2s, border-color 0.2s;
        }}
        .achievement:hover {{
            background: rgba(255,255,255,0.07);
            border-color: rgba(255,255,255,0.12);
        }}
        .achievement.rarity-high {{ border-left: 3px solid #ffc857; }}
        .achievement.rarity-mid {{ border-left: 3px solid #a78bfa; }}
        .achievement.rarity-low {{ border-left: 3px solid #6b7280; }}

        .ach-left {{ flex: 1; min-width: 0; }}
        .ach-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 5px;
            flex-wrap: wrap;
        }}
        .ach-name {{
            font-weight: 600;
            font-size: 15px;
            color: #ffffff;
        }}
        .rarity-badge {{
            font-size: 10px;
            padding: 2px 8px;
            border-radius: 6px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .rarity-badge.rarity-high {{ background: rgba(255,200,87,0.18); color: #ffc857; }}
        .rarity-badge.rarity-mid {{ background: rgba(167,139,250,0.18); color: #b49bff; }}
        .rarity-badge.rarity-low {{ background: rgba(107,114,128,0.18); color: #a0a8b8; }}

        .ach-desc {{
            font-size: 13px;
            color: #b0b8d0;
            line-height: 1.6;
        }}
        .ach-reward {{
            display: flex;
            align-items: center;
            gap: 4px;
            flex-shrink: 0;
            background: rgba(255,200,87,0.08);
            padding: 6px 12px;
            border-radius: 8px;
        }}
        .jade-icon {{ width: 28px; height: 28px; }}
        .jade-amount {{
            font-size: 17px;
            font-weight: 700;
            color: #ffc857;
            min-width: 24px;
            text-align: right;
        }}

        /* --- Footer --- */
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 16px;
            font-size: 12px;
            color: #555e70;
        }}
        .footer a {{ color: #7ec8e3; text-decoration: none; }}
        .footer a:hover {{ text-decoration: underline; }}

        /* --- Empty State --- */
        .empty-state {{
            text-align: center;
            color: #8890a8;
            font-size: 16px;
            padding: 60px 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⭐ 버전별 신규 업적</h1>
        <p class="subtitle">{old_ver} → {new_ver}</p>

        <div class="summary">
            <div class="summary-card">
                <span class="number num-old">{old_count}</span>
                <span class="label">{old_ver} 총 업적</span>
            </div>
            <div class="summary-card">
                <span class="number num-new">{new_count}</span>
                <span class="label">{new_ver} 총 업적</span>
            </div>
            <div class="summary-card">
                <span class="number num-added">+{len(added_ids)}</span>
                <span class="label">새로 추가됨</span>
            </div>
            <div class="summary-card">
                <span class="number num-jade">
                    <img src="{JADE_ICON_URL}" alt="성옥" class="jade-total-icon"/>{total_jade}
                </span>
                <span class="label">총 보상 성옥</span>
            </div>
        </div>

        {series_html if added_ids else '<p class="empty-state">두 버전 사이에 새롭게 추가된 업적이 없습니다.</p>'}

        <div class="footer">
            데이터 출처: <a href="https://hsr.nanoka.cc/achievement">nanoka.cc</a> ·
            아이콘 출처: <a href="https://starrail.honeyhunterworld.com">Honey Hunter World</a>
        </div>
    </div>
</body>
</html>"""

    file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"achievement_diff_{old_ver}_to_{new_ver}.html")
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(html_content)

    return file_name

def on_compare_clicked():
    old_ver = old_var.get().strip()
    new_ver = new_var.get().strip()

    if not old_ver or not new_ver:
        messagebox.showwarning("입력 오류", "이전 버전과 새 버전을 모두 입력하세요.")
        return

    if old_ver == new_ver:
        messagebox.showwarning("입력 오류", "서로 다른 버전을 선택하세요.")
        return

    btn_compare.config(state=tk.DISABLED, text="데이터 불러오는 중...")
    root.update()

    lang_code = LANGUAGES.get(lang_var.get(), "ko")

    old_data = fetch_achievements(old_ver, lang_code)
    new_data = fetch_achievements(new_ver, lang_code)

    if old_data is None:
        messagebox.showerror("에러", f"'{old_ver}' 버전의 데이터를 불러올 수 없습니다.\n해당 버전이 서버에 존재하는지 확인하세요.")
        btn_compare.config(state=tk.NORMAL, text="비교하기")
        return

    if new_data is None:
        messagebox.showerror("에러", f"'{new_ver}' 버전의 데이터를 불러올 수 없습니다.\n해당 버전이 서버에 존재하는지 확인하세요.")
        btn_compare.config(state=tk.NORMAL, text="비교하기")
        return

    old_achievements = extract_achievement_dict(old_data)
    new_achievements = extract_achievement_dict(new_data)

    old_ids = set(old_achievements.keys())
    new_ids = set(new_achievements.keys())

    added_ids = sorted(new_ids - old_ids)

    try:
        html_file = generate_html_report(
            old_ver, new_ver, added_ids, new_achievements,
            len(old_ids), len(new_ids)
        )

        total_jade = sum(RARITY_TO_JADE.get(new_achievements[aid].get('rarity', ''), 0) for aid in added_ids)

        webbrowser.open('file://' + os.path.realpath(html_file))
        messagebox.showinfo("성공",
            f"비교가 완료되었습니다!\n\n"
            f"새로 추가된 업적: {len(added_ids)}개\n"
            f"총 보상 성옥: {total_jade}개\n\n"
            f"결과 파일: {os.path.basename(html_file)}")
    except Exception as e:
        messagebox.showerror("에러", f"HTML 파일을 생성하는 중 오류가 발생했습니다:\n{e}")
    finally:
        btn_compare.config(state=tk.NORMAL, text="비교하기")


# --- GUI Setup ---
root = tk.Tk()
root.title("붕괴: 스타레일 — 업적 비교기")
root.geometry("440x340")
root.resizable(False, False)
root.configure(bg="#1e1e2e")

style = ttk.Style()
style.theme_use('clam')
style.configure('.', background="#1e1e2e", foreground="#cdd6f4")
style.configure('TFrame', background="#1e1e2e")
style.configure('TLabel', background="#1e1e2e", foreground="#cdd6f4", font=("Malgun Gothic", 10))
style.configure('Header.TLabel', background="#1e1e2e", foreground="#cba6f7", font=("Malgun Gothic", 12, "bold"))
style.configure('TButton', font=("Malgun Gothic", 11, "bold"))
style.configure('TCombobox', font=("Malgun Gothic", 10),
                fieldbackground="#313244", foreground="#cdd6f4",
                background="#313244", selectbackground="#45475a", selectforeground="#cdd6f4")
style.map('TCombobox',
          fieldbackground=[('readonly', '#313244'), ('!readonly', '#313244')],
          foreground=[('readonly', '#cdd6f4'), ('!readonly', '#cdd6f4')],
          selectbackground=[('readonly', '#45475a')],
          selectforeground=[('readonly', '#cdd6f4')])
root.option_add('*TCombobox*Listbox.background', '#313244')
root.option_add('*TCombobox*Listbox.foreground', '#cdd6f4')
root.option_add('*TCombobox*Listbox.selectBackground', '#45475a')
root.option_add('*TCombobox*Listbox.selectForeground', '#ffffff')
style.configure('Hint.TLabel', background="#1e1e2e", foreground="#6c7086", font=("Malgun Gothic", 9))

mainframe = ttk.Frame(root, padding="20")
mainframe.pack(fill=tk.BOTH, expand=True)

ttk.Label(mainframe, text="⭐ 버전별 신규 업적 비교기", style='Header.TLabel').pack(pady=(0, 15))

frame_old = ttk.Frame(mainframe)
frame_old.pack(fill=tk.X, pady=5)
ttk.Label(frame_old, text="이전 버전:", width=10).pack(side=tk.LEFT)
old_var = tk.StringVar(value=VERSIONS[0])
cb_old = ttk.Combobox(frame_old, textvariable=old_var, values=VERSIONS, width=20)
cb_old.pack(side=tk.LEFT, fill=tk.X, expand=True)

frame_new = ttk.Frame(mainframe)
frame_new.pack(fill=tk.X, pady=5)
ttk.Label(frame_new, text="새 버전:", width=10).pack(side=tk.LEFT)
new_var = tk.StringVar(value=VERSIONS[-1])
cb_new = ttk.Combobox(frame_new, textvariable=new_var, values=VERSIONS, width=20)
cb_new.pack(side=tk.LEFT, fill=tk.X, expand=True)

frame_lang = ttk.Frame(mainframe)
frame_lang.pack(fill=tk.X, pady=5)
ttk.Label(frame_lang, text="언어:", width=10).pack(side=tk.LEFT)
lang_var = tk.StringVar(value="한국어")
cb_lang = ttk.Combobox(frame_lang, textvariable=lang_var, values=list(LANGUAGES.keys()), state="readonly", width=20)
cb_lang.pack(side=tk.LEFT, fill=tk.X, expand=True)

ttk.Label(mainframe, text="💡 드롭다운에서 선택하거나, 직접 버전 번호를 입력할 수 있습니다.",
          style='Hint.TLabel').pack(pady=(5, 0), anchor=tk.W)

btn_compare = ttk.Button(mainframe, text="비교하기", command=on_compare_clicked)
btn_compare.pack(pady=18, fill=tk.X)

ttk.Label(mainframe, text="결과는 HTML 파일로 생성되어 브라우저에서 열립니다.",
          style='Hint.TLabel').pack()

root.eval('tk::PlaceWindow . center')
root.mainloop()
