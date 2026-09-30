# -*- coding: utf-8 -*-
"""
محلل شيتات المكالمات (نسخة بيضاء مبسطة)
التشغيل:   streamlit run app.py

أول تبويب بيفتح هو "الأخصائيات": لكل أخصائية عدد المتابعات + حصتها من كل المتابعات،
وقدامها رفض / نفذ / وعد بالدفع / لم يتم الرد بالعدد والنسبة.
"""
import html
import re
from collections import Counter
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

# ======================================================================
# 1) الإعدادات والشكل
# ======================================================================
st.set_page_config(page_title="محلل شيتات المكالمات", page_icon="📊", layout="wide")
px.defaults.template = "plotly_white"

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

    .stApp {background:#ffffff; color:#111827;}
    .stApp, .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
    .stApp button, .stApp input, .stApp .stMarkdown, .stTabs [data-baseweb="tab"] {
        font-family:'Cairo', sans-serif;
    }
    .block-container, [data-testid="stSidebar"] {direction: rtl; text-align: right;}
    .block-container {padding-top:2rem; max-width:1250px;}
    header[data-testid="stHeader"] {background:transparent;}
    #MainMenu, footer {visibility:hidden;}
    [data-testid="stSidebar"] {background:#f8fafc; border-left:1px solid #eef0f3;}
    h1, h2, h3, h4 {color:#0f172a; font-weight:800;}

    [data-testid="stMetric"] {
        background:#fff; border:1px solid #eef0f3; border-radius:14px; padding:12px 16px; text-align:right;
    }
    .stTabs [data-baseweb="tab-list"] {gap:6px; border-bottom:1px solid #eef0f3;}
    .stTabs [data-baseweb="tab"] {font-weight:600; padding:8px 14px;}

    /* ---------- كروت الأرقام ---------- */
    .kpis {display:grid; grid-template-columns:repeat(6, 1fr); gap:12px; margin:8px 0 22px 0; direction:rtl;}
    .kpi {background:#fff; border:1px solid #eef0f3; border-radius:16px; padding:14px 16px;
          box-shadow:0 1px 2px rgba(15,23,42,.04);}
    .kpi .l {font-size:13px; color:#64748b; font-weight:600;}
    .kpi .n {font-size:30px; font-weight:800; line-height:1.2; margin-top:2px;}
    .kpi .s {font-size:12px; color:#94a3b8; margin-top:2px;}
    @media (max-width: 900px) {.kpis {grid-template-columns:repeat(2, 1fr);}}

    /* ---------- جدول الأخصائيات ---------- */
    .ag-wrap {overflow-x:auto; border:1px solid #eef0f3; border-radius:16px; direction:rtl;
              box-shadow:0 1px 2px rgba(15,23,42,.04);}
    table.ag {width:100%; border-collapse:collapse; background:#fff;}
    table.ag th {background:#f8fafc; color:#475569; font-size:13px; font-weight:700;
                 padding:12px 10px; text-align:center; border-bottom:1px solid #eef0f3; white-space:nowrap;}
    table.ag td {padding:12px 10px; text-align:center; border-bottom:1px solid #f1f5f9; vertical-align:middle;}
    table.ag tr:last-child td {border-bottom:none;}
    table.ag tbody tr:hover td {background:#fafcff;}
    table.ag th.name, table.ag td.name {text-align:right; padding-right:18px; font-weight:700; color:#0f172a; white-space:nowrap;}
    table.ag td .big {font-size:20px; font-weight:800; line-height:1.15;}
    table.ag td .sub {font-size:12px; color:#94a3b8; margin-top:2px;}
    table.ag td.zero .big {color:#cbd5e1 !important;}
    table.ag td.fu {min-width:170px; background:#f5f9ff;}
    table.ag th.fu {background:#eaf2ff; color:#1d4ed8;}
    table.ag .bar {height:6px; background:#dbe7fb; border-radius:99px; margin:6px auto 0 auto; width:80%; overflow:hidden; direction:rtl;}
    table.ag .bar span {display:block; height:100%; border-radius:99px;}
    table.ag tr.total td {background:#f8fafc; font-weight:700; border-top:2px solid #e2e8f0;}
    .tag {display:inline-block; font-size:11px; font-weight:600; color:#b45309; background:#fef3c7;
          border-radius:99px; padding:1px 8px; margin-right:6px;}
    .hint {color:#64748b; font-size:13px; margin:8px 2px 4px 2px;}
    .insight {background:#f8fafc; border:1px solid #eef0f3; border-radius:12px; padding:10px 14px;
              color:#334155; font-size:14px; margin:6px 0 16px 0;}
    table.big-table th {font-size:15px; padding:16px 10px;}
    table.big-table td {padding:16px 10px;}
    table.big-table td .big {font-size:26px;}
    table.big-table td .sub {font-size:13px;}
    table.big-table th.name, table.big-table td.name {font-size:17px; min-width:130px;}
    .stRadio label p, .stSelectbox label p {font-size:14px;}

    /* ---------- الأكثر نشاطاً ---------- */
    .hero {border:1px solid #dbe7fb; border-right:6px solid #2563eb; background:linear-gradient(270deg,#f3f8ff,#ffffff);
           border-radius:18px; padding:18px 26px; margin:8px 0 20px 0; direction:rtl;
           box-shadow:0 6px 20px rgba(37,99,235,.08);}
    .hero-badge {display:inline-block; background:#fef3c7; color:#92400e; font-weight:700; font-size:13px;
                 border-radius:99px; padding:3px 12px;}
    .hero-main {display:flex; align-items:center; gap:34px; flex-wrap:wrap; margin-top:10px;}
    .hero-name {font-size:32px; font-weight:800; color:#0f172a; line-height:1.2;}
    .hero-sub {color:#64748b; font-size:14px; margin-top:2px;}
    .hero-nums {text-align:center; padding-right:30px; border-right:1px solid #e2e8f0;}
    .hero-n {font-size:40px; font-weight:800; color:#2563eb; line-height:1.1;}
    .hero-l {font-size:13px; color:#64748b;}
    .chips {display:flex; gap:8px; flex-wrap:wrap; margin-top:14px;}
    .chip {border-radius:99px; padding:4px 13px; font-size:13px; font-weight:600;}
    table.ag tr.star td {background:#fffbeb;}
    </style>
    """,
    unsafe_allow_html=True,
)

# أعمدة بيضيفها التطبيق (بتظهر في آخر الجدول)
COL_PHONE = "الرقم (موحّد)"
COL_PHONE_ISSUE = "مشكلة الرقم"
COL_FINAL = "الحالة النهائية"
COL_FINAL_AGENT = "أخصائية الحالة النهائية"
COL_CAT = "التصنيف"
INTERNAL_COLS = {COL_PHONE, COL_PHONE_ISSUE, COL_FINAL, COL_FINAL_AGENT, COL_CAT}

# أسماء التصنيفات (ثابتة عشان تتستخدم في كذا مكان)
SUCCESS_CAT = "✅ نجاح"
PROMISE_CAT = "💰 وعد بالدفع"
REFUSE_CAT = "❌ رفض"
NOANSWER_CAT = "📵 لم يتم الرد"
FOLLOW_CAT = "🔄 متابعة"
OTHER_CAT = "❓ غير مصنف"

# ألوان التصنيفات (هادية ومتناسقة)
CAT_COLORS = {
    FOLLOW_CAT: "#2563eb",
    SUCCESS_CAT: "#16a34a",
    PROMISE_CAT: "#d97706",
    REFUSE_CAT: "#dc2626",
    NOANSWER_CAT: "#64748b",
    OTHER_CAT: "#94a3b8",
}

# تصنيف الحالات: أول تصنيف يتطابق يكسب. الكلمات بتتقارن بعد توحيد الهمزات والتاء/الهاء والياء/الألف المقصورة.
CATEGORY_RULES = [
    (SUCCESS_CAT, ["done", "نفذ", "تنفيذ"]),
    (PROMISE_CAT, ["promise"]),
    (REFUSE_CAT, ["رفض"]),
    (NOANSWER_CAT, ["لا يرد", "مشغول", "مغلق", "رقم خطا"]),
    (FOLLOW_CAT, ["متابع", "تم التواصل"]),
]

# ترتيب ظهور التصنيفات في جدول تقييم الأخصائيات (المتابعة الأول)
DISPLAY_ORDER = [FOLLOW_CAT, SUCCESS_CAT, PROMISE_CAT, REFUSE_CAT, NOANSWER_CAT, OTHER_CAT]

# الحالات زي ما هي في الشيت (بالترتيب اللي يظهر في الجدول الرئيسي)
STATUS_ORDER = ["Done", "نفذ", "لا يرد", "مغلق", "مشغول", "رقم خطأ", "متابعة", "رفض", "Promise to Pay", "متابعه واتساب"]
OTHER_STATUS = "أخرى"
# أول قاعدة تتطابق تكسب (واتساب قبل متابعة عشان ما يتخلطوش)
STATUS_RULES = [
    ("Promise to Pay", ["promise"]),
    ("متابعه واتساب", ["واتساب", "واتس", "whatsapp"]),
    ("Done", ["done"]),
    ("نفذ", ["نفذ", "تنفيذ"]),
    ("لا يرد", ["لا يرد"]),
    ("مغلق", ["مغلق"]),
    ("مشغول", ["مشغول"]),
    ("رقم خطأ", ["رقم خطا"]),
    ("متابعة", ["متابع", "تم التواصل"]),
    ("رفض", ["رفض"]),
]
STATUS_COLORS = {
    "Done": "#16a34a",
    "نفذ": "#15803d",
    "لا يرد": "#64748b",
    "مغلق": "#475569",
    "مشغول": "#94a3b8",
    "رقم خطأ": "#78716c",
    "متابعة": "#2563eb",
    "رفض": "#dc2626",
    "Promise to Pay": "#d97706",
    "متابعه واتساب": "#0d9488",
    OTHER_STATUS: "#a1a1aa",
}


_STOP_RAW = """
nan none في من علي على الي الى إلى عن مع هذا هذه ده دي دا تم عدم ان أن لا او أو ما هو هي هم كان
و ب ل لو كمان برضو يعني علشان عشان لان لأن قد كل بعد قبل ثم حتى انه انها اللي التي الذي
"""


# ======================================================================
# 2) دوال التنظيف والتجهيز
# ======================================================================
_TASHKEEL = re.compile(r"[\u064B-\u0652\u0640]")
_AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def norm_ar(s) -> str:
    """توحيد الكتابة العربية للمقارنة فقط: همزات، ى/ي، ة/ه، تشكيل، مسافات، حروف صغيرة."""
    s = _TASHKEEL.sub("", str(s).lower().strip())
    s = re.sub("[أإآ]", "ا", s).replace("ى", "ي").replace("ة", "ه")
    return re.sub(r"\s+", " ", s)


STOP_WORDS = {norm_ar(w) for w in _STOP_RAW.split()}


def categorize(status) -> str:
    if pd.isna(status):
        return OTHER_CAT
    s = norm_ar(status)
    for cat, words in CATEGORY_RULES:
        if any(norm_ar(w) in s for w in words):
            return cat
    return OTHER_CAT


def normalize_phone(v):
    """يرجّع (الرقم الموحد, المشكلة). الرقم المصري الصحيح: 11 رقم يبدأ بـ 010/011/012/015."""
    if v is None or pd.isna(v):
        return None, "فارغ"
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    s = re.sub(r"\D", "", str(v).translate(_AR_DIGITS))
    if not s:
        return None, "فارغ"
    if s.startswith("0020") and len(s) == 14:
        s = s[4:]
    elif s.startswith("20") and len(s) == 12:
        s = s[2:]
    if len(s) == 10 and s.startswith("1"):  # إكسيل شال الصفر من الأول
        s = "0" + s
    if re.fullmatch(r"01[0125]\d{8}", s):
        return s, None
    if len(s) == 22:
        return s, "رقمين ملصوقين في بعض؟"
    if len(s) < 11:
        return s, "ناقص (أقل من 11 رقم)"
    if len(s) > 11:
        return s, "فيه أرقام زيادة"
    return s, "مش بيبدأ بكود موبايل مصري"


@st.cache_data(show_spinner="جاري قراءة الملف…")
def read_file(data: bytes, name: str) -> dict:
    if name.lower().endswith(".csv"):
        try:
            return {"Main": pd.read_csv(BytesIO(data), encoding="utf-8-sig")}
        except UnicodeDecodeError:
            return {"Main": pd.read_csv(BytesIO(data), encoding="cp1256")}
    xls = pd.ExcelFile(BytesIO(data))
    return {s: pd.read_excel(xls, s) for s in xls.sheet_names}


def clean_sheet(raw: pd.DataFrame):
    """تنظيف: مسافات زيادة في العناوين والقيم، حذف الأعمدة العشوائية (Unnamed شبه فاضية)."""
    df = raw.copy()
    df.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in df.columns]
    df = df.dropna(axis=0, how="all")

    dropped = [c for c in df.columns if c.startswith("Unnamed") and df[c].notna().mean() < 0.05]
    df = df.drop(columns=dropped)

    def tidy(v):
        if isinstance(v, str):
            v = re.sub(r"\s+", " ", v).strip()
            return v or None
        return v

    for c in df.columns:
        if not pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_datetime64_any_dtype(df[c]):
            df[c] = df[c].map(tidy)
    return df.reset_index(drop=True), dropped


def detect_columns(df: pd.DataFrame) -> dict:
    def find(*keys):
        return [c for c in df.columns if any(k in norm_ar(c) for k in keys)]

    def first(*keys):
        r = find(*keys)
        return r[0] if r else None

    return {
        "phone": first("رقم", "phone", "mobile", "موبايل", "تليفون", "هاتف"),
        "date": first("تاريخ", "date"),
        "feedback": find("feedback", "فيدباك", "حاله"),
        "agent": find("اخصائ", "agent", "موظف"),
        "doctor": first("دكتور", "doctor", "طبيب"),
        "place": first("مكان", "فرع", "branch"),
        "product": first("منتج", "product"),
        "notes": first("ملاحظ", "note"),
        "reason": first("سبب"),
    }


def build_attempts(df: pd.DataFrame, cols: dict) -> pd.DataFrame:
    """كل صف في الشيت ممكن يبقى فيه أكتر من مكالمة (Feedback 1 و 2 و 3).
    هنا بنحولهم لجدول واحد: كل مكالمة في صف، مربوطة بالأخصائية اللي عملتها."""
    parts = []
    for i, fb in enumerate(cols["feedback"]):
        ag = cols["agent"][i] if i < len(cols["agent"]) else None
        part = pd.DataFrame(
            {
                "_row": df.index,
                "_stage_no": i + 1,
                "المرحلة": f"مرة {i + 1}",
                "الحالة": df[fb].values,
                "الأخصائية": df[ag].values if ag else None,
            }
        )
        parts.append(part[part["الحالة"].notna()])
    if not parts:
        return pd.DataFrame(columns=["_row", "_stage_no", "المرحلة", "الحالة", "الأخصائية", COL_CAT])
    att = pd.concat(parts, ignore_index=True)
    att[COL_CAT] = att["الحالة"].map(categorize)
    return att


def enrich(df: pd.DataFrame, cols: dict) -> pd.DataFrame:
    """يضيف: الرقم الموحد + مشكلته + الحالة النهائية (آخر مكالمة) + التصنيف."""
    df = df.copy()
    if cols["date"]:
        df[cols["date"]] = pd.to_datetime(df[cols["date"]], errors="coerce")
    if cols["phone"]:
        res = df[cols["phone"]].map(normalize_phone)
        df[COL_PHONE] = res.map(lambda t: t[0])
        df[COL_PHONE_ISSUE] = res.map(lambda t: t[1])
    att = build_attempts(df, cols)
    if not att.empty:
        last = att.sort_values("_stage_no").drop_duplicates("_row", keep="last").set_index("_row")
        df[COL_FINAL] = last["الحالة"]
        df[COL_FINAL_AGENT] = last["الأخصائية"]
        df[COL_CAT] = df[COL_FINAL].map(categorize)
    return df


def spelling_variants(df: pd.DataFrame) -> pd.DataFrame:
    """قيم متشابهة مكتوبة بطرق مختلفة (المعادي / المعادى، متابعة / متابعه...)."""
    out = []
    for c in df.columns:
        if c in INTERNAL_COLS or pd.api.types.is_numeric_dtype(df[c]) or pd.api.types.is_datetime64_any_dtype(df[c]):
            continue
        vals = df[c].dropna().astype(str)
        if vals.nunique() > 80:
            continue
        for _, grp in vals.groupby(vals.map(norm_ar)):
            forms = sorted(set(grp))
            if len(forms) > 1:
                out.append({"العمود": c, "الصيغ المختلفة": " | ".join(forms), "عدد الصفوف": len(grp)})
    return pd.DataFrame(out)


def status_key(x) -> str:
    """يوحّد كتابة الحالة (متابعة/متابعه، Done/done...) ويرجّعها بأحد الأسماء في STATUS_ORDER."""
    s = norm_ar(x)
    for name, words in STATUS_RULES:
        if any(norm_ar(w) in s for w in words):
            return name
    return OTHER_STATUS


def status_eval(a: pd.DataFrame) -> dict:
    """a فيه عمودين: الأخصائية و _st (الحالة الموحدة).

    counts : عدد كل حالة لكل أخصائية (+ صف إجمالي في الآخر)
    pct    : نسبة كل حالة من مكالمات الأخصائية نفسها
    share  : حصة الأخصائية من إجمالي الحالة (مثال: كام % من كل الرفض جه منها)
    """
    ct = pd.crosstab(a["الأخصائية"], a["_st"])
    stats = [s for s in STATUS_ORDER + [OTHER_STATUS] if s in STATUS_ORDER or s in ct.columns]
    ct = ct.reindex(columns=stats, fill_value=0)
    ct.insert(0, "الإجمالي", ct.sum(axis=1))
    total_row = ct.sum().to_frame("الإجمالي الكلي").T
    counts = pd.concat([ct, total_row]).astype(int)
    counts.index.name = "الأخصائية"

    pct = counts[stats].div(counts["الإجمالي"].where(counts["الإجمالي"] > 0), axis=0).fillna(0) * 100
    denom = counts.loc[counts.index[-1], stats].where(lambda s: s > 0)
    share = counts[stats].div(denom, axis=1).fillna(0) * 100
    return {"counts": counts, "pct": pct.round(1), "share": share.round(1), "stats": stats}



# ======================================================================
# دوال مساعدة للعرض
# ======================================================================
def for_display(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[c]):
            out[c] = out[c].dt.strftime("%Y-%m-%d")
    return out


def show_df(df: pd.DataFrame, **kw):
    d = for_display(df)
    try:
        st.dataframe(d, width="stretch", hide_index=True, **kw)
    except Exception:
        st.dataframe(d, use_container_width=True, hide_index=True, **kw)


def show_chart(fig):
    fig.update_layout(paper_bgcolor="white", plot_bgcolor="white", font_family="Cairo")
    try:
        st.plotly_chart(fig, width="stretch")
    except Exception:
        st.plotly_chart(fig, use_container_width=True)


def value_table(series: pd.Series, label: str) -> pd.DataFrame:
    vc = series.dropna().value_counts().reset_index()
    vc.columns = [label, "العدد"]
    vc["النسبة %"] = (vc["العدد"] / vc["العدد"].sum() * 100).round(1)
    return vc


def kpi_cards(items):
    """items = [(العنوان, الرقم, سطر صغير, لون)]"""
    cards = "".join(
        f"<div class='kpi'><div class='l'>{html.escape(l)}</div>"
        f"<div class='n' style='color:{c}'>{n}</div><div class='s'>{html.escape(s)}</div></div>"
        for l, n, s, c in items
    )
    st.markdown(f"<div class='kpis'>{cards}</div>", unsafe_allow_html=True)


def status_table_html(counts, pct, share, stats, people, mode, star=None) -> str:
    """جدول كبير: صف لكل أخصائية، وعمود لكل حالة. الرقم الكبير = العدد، والصغير = النسبة."""
    total = counts.index[-1]
    perc = pct if mode == "own" else share

    head = "<tr><th class='name'>الأخصائية</th><th>الإجمالي</th>"
    for s in stats:
        head += f"<th style='border-bottom:3px solid {STATUS_COLORS[s]}'>{html.escape(s)}</th>"
    head += "</tr>"

    tops = {s: int(counts.loc[people, s].max()) for s in stats}

    def row(label, is_total=False):
        name = "الإجمالي الكلي" if is_total else html.escape(str(label))
        if star is not None and label == star and not is_total:
            name = "🏆 " + name
        tr = "<tr class='total'>" if is_total else ("<tr class='star'>" if (star is not None and label == star) else "<tr>")
        tr += f"<td class='name'>{name}</td><td><div class='big'>{int(counts.loc[label, 'الإجمالي'])}</div></td>"
        for s in stats:
            n = int(counts.loc[label, s])
            col = STATUS_COLORS[s]
            p = float(perc.loc[label, s])
            if is_total and mode == "share":
                p = 100.0 if n > 0 else 0.0
            cls = " class='zero'" if n == 0 else ""
            style = f" style='background:{col}14'" if (not is_total and n > 0 and n == tops[s]) else ""
            tr += f"<td{cls}{style}><div class='big' style='color:{col}'>{n}</div><div class='sub'>{p:.1f}%</div></td>"
        return tr + "</tr>"

    body = "".join(row(p) for p in people) + row(total, is_total=True)
    return f"<div class='ag-wrap'><table class='ag big-table'><thead>{head}</thead><tbody>{body}</tbody></table></div>"



# ======================================================================
# 3) التبويبات
# ======================================================================
def tab_agents(att):
    """الصفحة الرئيسية: أداء كل أخصائية على كل حالة."""
    st.markdown("## 📊 الأداء حسب الأخصائية")
    if att.empty or att["الأخصائية"].notna().sum() == 0:
        st.warning("مفيش عمود أخصائية اتلقى. اختاره من ⚙️ تعديل الأعمدة.")
        return

    c1, c2, c3 = st.columns([3, 2, 3])
    stage = c1.radio("المرحلة", ["الكل"] + sorted(att["المرحلة"].unique()), horizontal=True, key="agent_stage")
    sort_label = c2.selectbox("رتّب حسب", ["الإجمالي"] + STATUS_ORDER, key="agent_sort")
    mode_label = c3.radio(
        "النسبة تحت كل رقم = ", ["من مكالماتها", "حصتها من إجمالي الحالة"], horizontal=True, key="agent_mode"
    )
    mode = "own" if mode_label == "من مكالماتها" else "share"
    branch_pick = "كل الفروع"
    if "الفرع" in att.columns and att["الفرع"].notna().any():
        branches = sorted(att["الفرع"].dropna().astype(str).unique())
        branch_pick = st.selectbox("الفرع", ["كل الفروع"] + branches, key="agent_branch")

    a = att if stage == "الكل" else att[att["المرحلة"] == stage]
    a = a[a["الأخصائية"].notna()].copy()
    if branch_pick != "كل الفروع":
        a = a[a["الفرع"].astype(str) == branch_pick]
    if a.empty:
        st.info("مفيش مكالمات للاختيار ده.")
        return
    a["_st"] = a["الحالة"].map(status_key)

    ev = status_eval(a)
    counts, pct, share, stats = ev["counts"], ev["pct"], ev["share"], ev["stats"]
    sort_col = "الإجمالي" if sort_label == "الإجمالي" else sort_label
    if sort_col not in counts.columns:
        sort_col = "الإجمالي"
    people = list(counts.index[:-1])
    people.sort(key=lambda p: (-int(counts.loc[p, sort_col]), -int(counts.loc[p, "الإجمالي"])))

    # ---------- الأكثر نشاطاً ----------
    total_label = counts.index[-1]
    ranked = sorted(people, key=lambda p: -int(counts.loc[p, "الإجمالي"]))
    top = ranked[0]
    n_top = int(counts.loc[top, "الإجمالي"])
    n_all = max(int(counts.loc[total_label, "الإجمالي"]), 1)
    scope = "في الفرع" if branch_pick == "كل الفروع" else f"في فرع {branch_pick}"
    if len(ranked) > 1:
        second = ranked[1]
        gap = n_top - int(counts.loc[second, "الإجمالي"])
        sub = f"متقدمة بـ {gap} مكالمة عن الثانية ({html.escape(str(second))})" if gap > 0 else f"متعادلة في العدد مع {html.escape(str(second))}"
    else:
        sub = "أخصائية واحدة في الاختيار ده"
    chips = "".join(
        f"<span class='chip' style='color:{STATUS_COLORS[s]};background:{STATUS_COLORS[s]}14'><b>{int(counts.loc[top, s])}</b> {html.escape(s)}</span>"
        for s in sorted(stats, key=lambda s: -int(counts.loc[top, s])) if int(counts.loc[top, s]) > 0
    )
    st.markdown(
        f"<div class='hero'><span class='hero-badge'>🏆 الأكثر نشاطاً {html.escape(scope)}</span>"
        f"<div class='hero-main'>"
        f"<div><div class='hero-name'>{html.escape(str(top))}</div><div class='hero-sub'>{sub}</div></div>"
        f"<div class='hero-nums'><div class='hero-n'>{n_top}</div><div class='hero-l'>مكالمة</div></div>"
        f"<div class='hero-nums'><div class='hero-n'>{n_top / n_all:.0%}</div><div class='hero-l'>من كل المكالمات</div></div>"
        f"</div><div class='chips'>{chips}</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown(status_table_html(counts, pct, share, stats, people, mode, star=top), unsafe_allow_html=True)
    hint = (
        "الرقم الكبير = عدد المكالمات بالحالة دي. النسبة الصغيرة = "
        + ("نسبتها من كل مكالمات الأخصائية." if mode == "own" else "حصة الأخصائية من كل مكالمات الحالة دي في الشيت.")
        + " الخلفية الملونة = أعلى أخصائية في الحالة."
    )
    st.markdown(f"<div class='hint'>{hint}</div>", unsafe_allow_html=True)

    long = counts.loc[people, stats].reset_index().melt(id_vars="الأخصائية", var_name="الحالة", value_name="العدد")
    fig = px.bar(
        long, y="الأخصائية", x="العدد", color="الحالة", orientation="h", barmode="stack",
        color_discrete_map=STATUS_COLORS, category_orders={"الحالة": stats, "الأخصائية": people},
        text_auto=True, title="توزيع مكالمات كل أخصائية",
    )
    fig.update_yaxes(autorange="reversed", title=None)
    fig.update_xaxes(title=None)
    fig.update_layout(height=140 + 42 * len(people), legend_title_text="", legend_orientation="h", legend_y=-0.15)
    show_chart(fig)

    with st.expander("جداول النسب والتحميل"):
        st.markdown("**العدد**")
        show_df(counts.reset_index())
        st.markdown("**نسبة كل حالة من مكالمات الأخصائية نفسها**")
        show_df(pct.assign(**{"الإجمالي": counts["الإجمالي"]}).reset_index(),
                column_config={c: st.column_config.NumberColumn(format="%.1f%%") for c in stats})
        st.markdown("**حصة كل أخصائية من إجمالي كل حالة**")
        show_df(share.reset_index(), column_config={c: st.column_config.NumberColumn(format="%.1f%%") for c in stats})
        st.markdown("**الحالات زي ما هي مكتوبة في الشيت**")
        detail = pd.crosstab(a["الأخصائية"], a["الحالة"], margins=True, margins_name="الإجمالي")
        show_df(detail.rename_axis(index="الأخصائية", columns=None).reset_index())

        buf = BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            counts.reset_index().to_excel(w, index=False, sheet_name="العدد")
            pct.reset_index().to_excel(w, index=False, sheet_name="نسبة من مكالماتها")
            share.reset_index().to_excel(w, index=False, sheet_name="حصة من الإجمالي")
        st.download_button("⬇️ تحميل التقييم Excel", buf.getvalue(), "تقييم_الأخصائيات.xlsx", key="agent_dl")


def tab_summary(df, att, cols):
    total = len(df)
    m = st.columns(5)
    m[0].metric("إجمالي السجلات", total)
    if COL_PHONE in df:
        valid = df[COL_PHONE].dropna()
        m[1].metric("أرقام فريدة", valid.nunique())
        m[2].metric("أرقام مكررة", int(valid.duplicated().sum()))
        m[3].metric("أرقام فيها مشكلة", int(df[COL_PHONE_ISSUE].notna().sum()))
    if COL_CAT in df:
        succ = int((df[COL_CAT] == SUCCESS_CAT).sum())
        m[4].metric("ناجحة (حسب الحالة النهائية)", succ, f"{succ / max(total, 1):.1%} من السجلات", delta_color="off")

        st.caption("الحالة النهائية = نتيجة آخر مكالمة اتسجلت للعميل (Feedback الأخير غير الفاضي).")
        cats = df[COL_CAT].value_counts()
        cc = st.columns(max(len(cats), 1))
        for col, (cat, n) in zip(cc, cats.items()):
            col.metric(cat, int(n))

    st.divider()
    st.subheader("توزيع الحالات")
    if att.empty:
        st.warning("مفيش عمود Feedback/حالة اتلقى تلقائياً. اختاره من ⚙️ تعديل الأعمدة في الشريط الجانبي.")
        return
    options = ["الحالة النهائية"] + sorted(att["المرحلة"].unique()) + ["كل المكالمات"]
    choice = st.radio("اعرض توزيع:", options, horizontal=True)
    if choice == "الحالة النهائية":
        series = df[COL_FINAL]
    elif choice == "كل المكالمات":
        series = att["الحالة"]
    else:
        series = att.loc[att["المرحلة"] == choice, "الحالة"]
    vt = value_table(series, "الحالة")
    left, right = st.columns([2, 1])
    with left:
        show_chart(px.pie(vt, names="الحالة", values="العدد", hole=0.4, title=f"توزيع الحالات: {choice}"))
    with right:
        show_df(vt)

    if cols["date"]:
        d = df.dropna(subset=[cols["date"]]).copy()
        if not d.empty:
            d["اليوم"] = d[cols["date"]].dt.normalize()
            daily = (
                d.groupby("اليوم")
                .agg(**{"عدد السجلات": ("اليوم", "size"), "ناجحة": (COL_CAT, lambda s: int((s == SUCCESS_CAT).sum()))})
                .reset_index()
            )
            st.subheader("التطور اليومي")
            show_chart(px.line(daily, x="اليوم", y=["عدد السجلات", "ناجحة"], markers=True))


def tab_breakdown(df, cols):
    st.subheader("تحليل حسب (دكتور / مكان / منتج / أخصائية)")
    if COL_CAT not in df:
        st.warning("محتاج عمود Feedback عشان التحليل ده.")
        return
    dims = {}
    for label, key in [("الدكتور", "doctor"), ("المكان", "place"), ("المنتج", "product")]:
        if cols[key]:
            dims[f"{label} ({cols[key]})"] = cols[key]
    dims["أخصائية الحالة النهائية"] = COL_FINAL_AGENT
    c1, c2 = st.columns([2, 1])
    dim_label = c1.selectbox("قسّم حسب:", list(dims))
    top_n = c2.slider("أعلى كام قيمة؟", 5, 40, 15)
    col = dims[dim_label]

    d = df.dropna(subset=[col, COL_CAT])
    if d.empty:
        st.info("مفيش بيانات كفاية.")
        return
    top = d[col].value_counts().head(top_n).index
    ct = pd.crosstab(d[col], d[COL_CAT]).loc[top].rename_axis(index=col, columns=None)
    cat_cols = list(ct.columns)
    ct["الإجمالي"] = ct.sum(axis=1)
    ct["نسبة النجاح %"] = (ct[SUCCESS_CAT] / ct["الإجمالي"] * 100).round(1) if SUCCESS_CAT in ct else 0.0

    long = ct[cat_cols].reset_index().melt(id_vars=col, var_name=COL_CAT, value_name="العدد")
    fig = px.bar(long, y=col, x="العدد", color=COL_CAT, orientation="h", barmode="stack", color_discrete_map=CAT_COLORS)
    fig.update_yaxes(autorange="reversed")
    show_chart(fig)
    show_df(
        ct.reset_index(),
        column_config={"نسبة النجاح %": st.column_config.NumberColumn(format="%.1f%%")},
    )


def tab_text(df, cols):
    st.subheader("تحليل الكلمات والنصوص")
    cands = [
        c
        for c in df.columns
        if c not in INTERNAL_COLS
        and not pd.api.types.is_numeric_dtype(df[c])
        and not pd.api.types.is_datetime64_any_dtype(df[c])
        and df[c].notna().any()
    ]
    if not cands:
        st.info("مفيش أعمدة نصية فيها بيانات.")
        return
    default = cols["notes"] if cols["notes"] in cands else cands[0]
    c1, c2, c3 = st.columns([2, 1, 1])
    target = c1.selectbox("العمود:", cands, index=cands.index(default))
    top_n = c2.slider("عدد الكلمات", 10, 50, 20)
    unify = c3.checkbox("توحيد الهمزات والتاء المربوطة", value=True)
    extra = st.text_input("كلمات تتجاهلها (مفصولة بمسافة):")

    series = df[target].dropna().astype(str)
    st.caption(f"عدد الخانات المكتوبة في العمود ده: {len(series)} من {len(df)}")
    stop = STOP_WORDS | {norm_ar(w) for w in extra.split()}
    tokens = []
    for text in series:
        t = norm_ar(text) if unify else text.lower()
        tokens += [w for w in re.findall(r"\w+", t) if len(w) > 1 and not w.isdigit() and w not in stop]
    if not tokens:
        st.info("مفيش كلمات كفاية للتحليل في العمود ده.")
        return
    wdf = pd.DataFrame(Counter(tokens).most_common(top_n), columns=["الكلمة", "التكرار"])
    left, right = st.columns([1, 2])
    with left:
        show_df(wdf)
    with right:
        show_chart(px.bar(wdf, x="الكلمة", y="التكرار", title=f"أكثر {top_n} كلمة في ({target})"))

    word = st.selectbox("اعرض الصفوف اللي فيها كلمة:", ["—"] + wdf["الكلمة"].tolist())
    if word != "—":
        mask = df[target].fillna("").astype(str).map(lambda x: norm_ar(x) if unify else x.lower()).str.contains(word, regex=False)
        show_df(df[mask])


def tab_quality(df, cols):
    st.subheader("الأرقام")
    if COL_PHONE in df:
        dup = df[df[COL_PHONE].notna() & df[COL_PHONE].duplicated(keep=False)].sort_values(COL_PHONE)
        st.markdown(f"**الأرقام المكررة** (بعد توحيد الصيغة: +20 / 0020 / صفر ناقص): {len(dup)} صف")
        if dup.empty:
            st.success("مفيش أرقام مكررة.")
        else:
            show_df(dup)
        bad = df[df[COL_PHONE_ISSUE].notna()]
        st.markdown(f"**أرقام فيها مشكلة:** {len(bad)}")
        if bad.empty:
            st.success("كل الأرقام سليمة.")
        else:
            show_df(bad)
    else:
        st.info("مفيش عمود رقم تليفون.")

    st.subheader("الخانات الفارغة")
    n = max(len(df), 1)
    miss = df.drop(columns=[c for c in df.columns if c in INTERNAL_COLS]).isna().sum().reset_index()
    miss.columns = ["العمود", "عدد الفاضي"]
    miss["نسبة النقص %"] = (miss["عدد الفاضي"] / n * 100).round(1)
    miss = miss.sort_values("نسبة النقص %", ascending=False)
    show_df(miss, column_config={"نسبة النقص %": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f%%")})
    empty_cols = miss.loc[miss["عدد الفاضي"] == len(df), "العمود"].tolist()
    if empty_cols:
        st.warning("أعمدة فاضية بالكامل: " + "، ".join(empty_cols))
    if cols["reason"] and df[cols["reason"]].isna().all() and COL_CAT in df:
        refused = int(df[COL_CAT].eq(REFUSE_CAT).sum())
        if refused:
            st.warning(f"عمود ({cols['reason']}) فاضي بالكامل رغم إن فيه {refused} حالة رفض، مش هتعرف أسباب الرفض من الشيت.")

    st.subheader("قيم مكتوبة بأكتر من صيغة")
    sv = spelling_variants(df)
    if sv.empty:
        st.success("مفيش تشابه إملائي مشكوك فيه.")
    else:
        st.caption("دي قيم شكلها نفس الحاجة بس مكتوبة بطرق مختلفة، ويفضل توحيدها في الشيت.")
        show_df(sv)


def tab_data(df):
    st.subheader("استعراض البيانات والبحث")
    term = st.text_input("🔎 بحث في أي عمود (اسم، رقم، دكتور، منتج...):")
    out = df
    if term.strip():
        hay = df.astype(str).agg(" ".join, axis=1).map(norm_ar)
        out = df[hay.str.contains(norm_ar(term), regex=False)]
    st.write(f"النتائج: **{len(out)}** من {len(df)}")
    show_df(out)

    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        for_display(out).to_excel(w, index=False, sheet_name="Data")
    d1, d2 = st.columns(2)
    d1.download_button("⬇️ تحميل النتائج Excel", buf.getvalue(), "results.xlsx")
    d2.download_button("⬇️ تحميل النتائج CSV", for_display(out).to_csv(index=False).encode("utf-8-sig"), "results.csv")


# ======================================================================
# 4) main
# ======================================================================
def column_mapping_ui(df, auto, sheet):
    """يسيب لك تصلح اكتشاف الأعمدة يدوي لو التلقائي غلط."""
    none = "— لا يوجد —"
    cols = dict(auto)
    with st.sidebar.expander("⚙️ تعديل الأعمدة يدوياً"):
        for key, label in [("phone", "عمود الرقم"), ("date", "عمود التاريخ")]:
            opts = [none] + list(df.columns)
            idx = opts.index(auto[key]) if auto[key] in opts else 0
            pick = st.selectbox(label, opts, index=idx, key=f"{sheet}_{key}")
            cols[key] = None if pick == none else pick
        cols["feedback"] = st.multiselect("أعمدة الحالة (بالترتيب)", list(df.columns), default=auto["feedback"], key=f"{sheet}_fb")
        cols["agent"] = st.multiselect("أعمدة الأخصائية (بنفس الترتيب)", list(df.columns), default=auto["agent"], key=f"{sheet}_ag")
        for i, fb in enumerate(cols["feedback"]):
            ag = cols["agent"][i] if i < len(cols["agent"]) else "—"
            st.caption(f"مرة {i + 1}:  {fb}  ←  {ag}")
        if len(cols["agent"]) != len(cols["feedback"]):
            st.warning("عدد أعمدة الحالة مش بيساوي عدد أعمدة الأخصائية، تأكد من الترتيب.")
    return cols


def main():
    st.markdown("#### 📊 محلل شيتات المكالمات")

    with st.sidebar:
        st.header("📂 الملف")
        up = st.file_uploader("اختر ملف (.xlsx / .xls / .csv)", type=["xlsx", "xls", "csv"])
    if not up:
        st.info("ارفع ملف من الشريط الجانبي عشان تبدأ التحليل.")
        return

    sheets = read_file(up.getvalue(), up.name)
    names = list(sheets)
    biggest = max(names, key=lambda n: sheets[n].shape[0] * sheets[n].shape[1])
    sheet = st.sidebar.selectbox("الشيت", names, index=names.index(biggest))

    df, dropped = clean_sheet(sheets[sheet])
    if df.empty:
        st.warning("الشيت ده فاضي.")
        return
    if dropped:
        st.sidebar.caption("اتجاهل عمود شبه فاضي: " + "، ".join(dropped))

    cols = column_mapping_ui(df, detect_columns(df), sheet)
    if not cols["phone"] and not cols["feedback"]:
        st.warning("الشيت ده مش شكله شيت مكالمات (مفيش عمود رقم ولا حالة). ده عرض خام له، أو حدد الأعمدة من ⚙️ تعديل الأعمدة.")
        show_df(df)
        return

    df = enrich(df, cols)

    if cols["date"] and df[cols["date"]].notna().any():
        lo, hi = df[cols["date"]].min().date(), df[cols["date"]].max().date()
        rng = st.sidebar.date_input("📅 الفترة", value=(lo, hi), min_value=lo, max_value=hi)
        if isinstance(rng, (tuple, list)) and len(rng) == 2:
            s, e = pd.Timestamp(rng[0]), pd.Timestamp(rng[1])
            df = df[df[cols["date"]].between(s, e)].reset_index(drop=True)
    att = build_attempts(df, cols)
    if cols["place"] and not att.empty:
        att["الفرع"] = df[cols["place"]].reindex(att["_row"]).values

    st.caption(f"الشيت: {sheet}  •  الصفوف: {len(df)}  •  المكالمات المسجلة: {len(att)}")

    # الأخصائيات أول تبويب، فبتظهر أول ما الملف يتفتح
    tabs = st.tabs(["📊 الأداء حسب الأخصائية", "📈 الملخص", "🧩 تحليل حسب", "🔍 الكلمات", "⚠️ الجودة", "📋 البيانات"])
    with tabs[0]:
        tab_agents(att)
    with tabs[1]:
        tab_summary(df, att, cols)
    with tabs[2]:
        tab_breakdown(df, cols)
    with tabs[3]:
        tab_text(df, cols)
    with tabs[4]:
        tab_quality(df, cols)
    with tabs[5]:
        tab_data(df)


if __name__ == "__main__":
    main()
