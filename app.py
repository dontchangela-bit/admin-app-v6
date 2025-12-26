"""
AI-CARE Lung Pro - 管理後台（完整臨床版）
==========================================

🔵 個管師與資料中心（需登入）
包含完整的肺癌術後照護臨床資料結構
"""

import streamlit as st
from datetime import datetime, timedelta, date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# 載入設定
try:
    from config import (
        ADMIN_CREDENTIALS, SYSTEM_NAME, HOSPITAL_NAME, DEPARTMENT_NAME,
        ALERT_THRESHOLD_RED, ALERT_THRESHOLD_YELLOW
    )
except:
    ADMIN_CREDENTIALS = {"admin": "aicare2024", "nurse01": "nurse2024"}
    SYSTEM_NAME = "AI-CARE Lung"
    HOSPITAL_NAME = "三軍總醫院"
    DEPARTMENT_NAME = "數位醫學中心"
    ALERT_THRESHOLD_RED = 7
    ALERT_THRESHOLD_YELLOW = 4

# 載入資料管理
try:
    from data_manager import (
        get_all_patients, get_pending_alerts, get_all_alerts,
        update_alert_status, get_interventions, save_intervention,
        get_patient_reports, get_statistics, load_data, save_data
    )
    DATA_MANAGER_AVAILABLE = True
except:
    DATA_MANAGER_AVAILABLE = False

# ============================================
# 臨床資料選項定義
# ============================================
CLINICAL_OPTIONS = {
    # 基本資料
    "gender": ["男", "女"],
    "smoking_status": ["從未吸菸", "已戒菸", "目前吸菸"],
    "asa_class": ["I", "II", "III", "IV"],
    "ecog": ["0", "1", "2", "3", "4"],
    
    # 共病
    "comorbidities": [
        "COPD", "ILD", "高血壓", "冠心病", "心房顫動", "心衰竭",
        "糖尿病", "慢性腎臟病", "肝硬化", "腦中風", "其他惡性腫瘤"
    ],
    
    # 腫瘤位置
    "tumor_location": ["周邊型", "中央型"],
    "lobe": ["RUL", "RML", "RLL", "LUL", "LLL", "Lingula"],
    
    # 手術方式
    "surgery_type": [
        "Wedge resection",
        "Segmentectomy", 
        "Lobectomy",
        "Bilobectomy",
        "Pneumonectomy",
        "Sleeve resection"
    ],
    "surgery_approach": [
        "VATS (多孔)",
        "Uniportal VATS",
        "RATS",
        "開胸手術",
        "轉換開胸"
    ],
    "ln_dissection": ["系統性淋巴結廓清", "淋巴結取樣", "未執行"],
    
    # 病理
    "pathology_type": [
        "AIS (原位腺癌)",
        "MIA (微浸潤腺癌)",
        "Invasive adenocarcinoma",
        "Squamous cell carcinoma",
        "Large cell carcinoma",
        "Small cell carcinoma",
        "Carcinoid",
        "其他"
    ],
    "adenocarcinoma_subtype": [
        "Lepidic", "Acinar", "Papillary", "Micropapillary", "Solid",
        "Invasive mucinous", "Colloid", "Fetal", "Enteric"
    ],
    "margin_status": ["R0 (完全切除)", "R1 (顯微殘留)", "R2 (肉眼殘留)"],
    "lvi": ["無", "有"],
    "vpi": ["PL0", "PL1", "PL2", "PL3"],
    "stas": ["無", "有", "未檢測"],
    
    # 分子檢測
    "egfr_status": ["Wild type", "Exon 19 del", "L858R", "T790M", "Exon 20 ins", "其他突變", "未檢測"],
    "alk_status": ["陰性", "陽性", "未檢測"],
    "pdl1_status": ["<1%", "1-49%", "≥50%", "未檢測"],
    
    # 術後併發症
    "complications": [
        "延遲性氣漏 (>5天)",
        "肺炎",
        "心房顫動",
        "ARDS",
        "乳糜胸",
        "術後出血",
        "再手術",
        "呼吸衰竭插管",
        "其他"
    ],
    
    # 術後輔助治療
    "adjuvant_therapy": [
        "無需輔助治療",
        "輔助化療",
        "輔助標靶治療 (TKI)",
        "輔助免疫治療",
        "輔助放射治療",
        "化療 + 免疫",
        "待 MDT 討論"
    ],
    
    # 疼痛控制
    "pain_control": [
        "PCA",
        "Intercostal nerve block",
        "ESP block",
        "Paravertebral block",
        "口服止痛藥",
        "其他"
    ]
}

# T 分期
T_STAGE = ["Tis", "T1mi", "T1a", "T1b", "T1c", "T2a", "T2b", "T3", "T4"]
N_STAGE = ["N0", "N1", "N2", "N3"]
M_STAGE = ["M0", "M1a", "M1b", "M1c"]

# ============================================
# 頁面設定
# ============================================
st.set_page_config(
    page_title=f"{SYSTEM_NAME} - 管理後台",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS 樣式
# ============================================
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border-left: 5px solid;
        height: 100%;
    }
    
    .section-header {
        background: linear-gradient(135deg, #1e40af, #3b82f6);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 20px 0 15px 0;
        font-weight: 600;
    }
    
    .info-box {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 8px 0;
    }
    
    .alert-card-red {
        background: linear-gradient(135deg, #fef2f2, #fee2e2);
        border-left: 4px solid #ef4444;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .alert-card-yellow {
        background: linear-gradient(135deg, #fffbeb, #fef3c7);
        border-left: 4px solid #f59e0b;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .patient-card {
        background: white;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        border-left: 4px solid;
    }
    
    .intervention-card {
        background: #f8fafc;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
        border-left: 3px solid #3b82f6;
    }
    
    .header-banner {
        background: linear-gradient(135deg, #1e40af, #3b82f6);
        border-radius: 16px;
        padding: 24px 32px;
        color: white;
        margin-bottom: 24px;
    }
    
    .clinical-section {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# Session State
# ============================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'admin_page' not in st.session_state:
    st.session_state.admin_page = "dashboard"
if 'selected_patient' not in st.session_state:
    st.session_state.selected_patient = None

# ============================================
# 模擬數據
# ============================================
MOCK_PATIENTS = [
    {"id": "P001", "name": "王大明", "age": 68, "gender": "男", "surgery": "Lobectomy", "status": "normal", "post_op_day": 14, "phone": "0912-345-678"},
    {"id": "P002", "name": "李小華", "age": 55, "gender": "女", "surgery": "Segmentectomy", "status": "warning", "post_op_day": 7, "phone": "0923-456-789"},
]

MOCK_ALERTS = [
    {"id": "A001", "patient_id": "P001", "patient_name": "王大明", "level": "yellow", "score": 5, "symptoms": ["疲勞"], "time_display": "10:30", "status": "pending", "phone": "0912-345-678"},
]

# ============================================
# 資料取得函數
# ============================================
def get_patients_data():
    if DATA_MANAGER_AVAILABLE:
        try:
            patients = get_all_patients()
            if patients:
                return patients
        except:
            pass
    return MOCK_PATIENTS

def get_alerts_data():
    if DATA_MANAGER_AVAILABLE:
        try:
            alerts = get_all_alerts()
            if alerts:
                return alerts
        except:
            pass
    return MOCK_ALERTS

def get_pending_alerts_data():
    alerts = get_alerts_data()
    return [a for a in alerts if a.get("status") == "pending"]

def get_stats_data():
    patients = get_patients_data()
    alerts = get_alerts_data()
    pending = [a for a in alerts if a.get("status") == "pending"]
    return {
        "total_patients": len(patients),
        "today_reports": len([p for p in patients if ":" in str(p.get("last_report_time", ""))]),
        "red_alerts": len([a for a in pending if a.get("level") == "red"]),
        "yellow_alerts": len([a for a in pending if a.get("level") == "yellow"]),
        "pending_alerts": len(pending)
    }

def save_patient_clinical_data(patient_id, clinical_data):
    """儲存病人臨床資料"""
    if DATA_MANAGER_AVAILABLE:
        try:
            data = load_data()
            if patient_id in data.get("patients", {}):
                data["patients"][patient_id]["clinical"] = clinical_data
                data["patients"][patient_id]["clinical_updated_at"] = datetime.now().isoformat()
                data["patients"][patient_id]["clinical_updated_by"] = st.session_state.username
                save_data(data)
                return True
        except Exception as e:
            st.error(f"儲存失敗: {e}")
    return False

# ============================================
# 登入功能
# ============================================
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 40px 0;">
            <div style="font-size: 72px; margin-bottom: 16px;">🏥</div>
            <h1 style="color: #1e293b; margin-bottom: 4px; font-size: 32px;">AI-CARE Lung</h1>
            <p style="color: #64748b; font-size: 16px; margin-bottom: 40px;">管理後台</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("帳號", placeholder="輸入帳號")
            password = st.text_input("密碼", type="password", placeholder="輸入密碼")
            submit = st.form_submit_button("登入", use_container_width=True, type="primary")
            
            if submit:
                if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ 帳號或密碼錯誤")
        
        with st.expander("📋 測試帳號"):
            st.markdown("管理員：admin / aicare2024")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# ============================================
# 側邊欄
# ============================================
def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 16px 0 24px 0;">
            <div style="font-size: 36px;">🏥</div>
            <div style="font-size: 16px; font-weight: 700; color: #1e293b; margin-top: 6px;">{SYSTEM_NAME}</div>
            <div style="font-size: 11px; color: #64748b;">管理後台</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"👤 **{st.session_state.username}**")
        st.markdown("---")
        
        menu_items = [
            ("dashboard", "📊", "儀表板"),
            ("alerts", "⚠️", "警示處理"),
            ("patients", "👥", "病人管理"),
            ("clinical", "📋", "臨床資料"),
            ("education", "📚", "衛教推送"),
            ("interventions", "📝", "介入紀錄"),
            ("reports", "📈", "報表統計"),
        ]
        
        for page_id, icon, label in menu_items:
            btn_type = "primary" if st.session_state.admin_page == page_id else "secondary"
            if st.button(f"{icon} {label}", key=f"nav_{page_id}", use_container_width=True, type=btn_type):
                st.session_state.admin_page = page_id
                st.rerun()
        
        st.markdown("---")
        stats = get_stats_data()
        col1, col2 = st.columns(2)
        col1.metric("🔴", stats.get('red_alerts', 0))
        col2.metric("🟡", stats.get('yellow_alerts', 0))
        
        st.markdown("---")
        if st.button("🚪 登出", use_container_width=True):
            logout()

# ============================================
# 儀表板
# ============================================
def render_dashboard():
    st.markdown(f"""
    <div class="header-banner">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 14px; opacity: 0.9;">{HOSPITAL_NAME} {DEPARTMENT_NAME}</div>
                <div style="font-size: 28px; font-weight: 700; margin-top: 4px;">📊 工作儀表板</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 14px; opacity: 0.9;">{datetime.now().strftime('%Y年%m月%d日')}</div>
                <div style="font-size: 20px; font-weight: 600;">{datetime.now().strftime('%H:%M')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    stats = get_stats_data()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'<div class="stat-card" style="border-color: #3b82f6;"><div style="font-size: 36px; font-weight: 700; color: #3b82f6;">{stats["total_patients"]}</div><div style="color: #64748b;">📋 總收案</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card" style="border-color: #10b981;"><div style="font-size: 36px; font-weight: 700; color: #10b981;">{stats["today_reports"]}</div><div style="color: #64748b;">✅ 今日回報</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card" style="border-color: #ef4444;"><div style="font-size: 36px; font-weight: 700; color: #ef4444;">{stats["red_alerts"]}</div><div style="color: #64748b;">🔴 紅色警示</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-card" style="border-color: #f59e0b;"><div style="font-size: 36px; font-weight: 700; color: #f59e0b;">{stats["yellow_alerts"]}</div><div style="color: #64748b;">🟡 黃色警示</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("### ⚠️ 待處理警示")
        alerts = get_pending_alerts_data()
        if alerts:
            for alert in alerts[:5]:
                level = alert.get("level", "yellow")
                st.markdown(f"""
                <div class="alert-card-{level}">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <strong>{alert.get('patient_name', '未知')}</strong> - {', '.join(alert.get('symptoms', []))}
                            <br><small>📱 {alert.get('phone', '')}</small>
                        </div>
                        <div style="font-size: 24px; font-weight: 700;">{alert.get('score', 0)}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ 目前沒有待處理警示")
    
    with col2:
        st.markdown("### 📅 今日排程")
        schedule = [("08:00-10:00", "晨間巡視", "✅"), ("10:00-12:00", "警示處理", "▶️"), ("13:00-15:00", "個案追蹤", "⏳")]
        for time, task, icon in schedule:
            st.markdown(f"**{icon} {time}** {task}")

# ============================================
# 警示處理
# ============================================
def render_alerts():
    st.markdown("## ⚠️ 警示處理")
    all_alerts = get_alerts_data()
    
    pending = [a for a in all_alerts if a.get("status") == "pending"]
    contacted = [a for a in all_alerts if a.get("status") == "contacted"]
    resolved = [a for a in all_alerts if a.get("status") == "resolved"]
    
    tab1, tab2, tab3 = st.tabs([f"⏳ 待處理 ({len(pending)})", f"📞 聯繫中 ({len(contacted)})", f"✅ 已完成 ({len(resolved)})"])
    
    with tab1:
        if pending:
            for alert in pending:
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        level = alert.get("level", "yellow")
                        st.markdown(f"""
                        <div class="alert-card-{level}">
                            <strong>{alert.get('patient_name', '未知')}</strong> | 評分: {alert.get('score', 0)}
                            <br>症狀: {', '.join(alert.get('symptoms', []))}
                            <br><small>📱 {alert.get('phone', '')}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        if st.button("📞 已聯繫", key=f"contact_{alert['id']}"):
                            if DATA_MANAGER_AVAILABLE:
                                update_alert_status(alert['id'], 'contacted', st.session_state.username)
                            st.rerun()
        else:
            st.success("🎉 沒有待處理的警示")
    
    with tab2:
        if contacted:
            for alert in contacted:
                st.info(f"📞 {alert.get('patient_name')} - 聯繫中")
        else:
            st.info("目前沒有聯繫中的警示")
    
    with tab3:
        if resolved:
            for alert in resolved[:10]:
                st.success(f"✅ {alert.get('patient_name')} - 已完成")
        else:
            st.info("目前沒有已完成的警示")

# ============================================
# 病人管理
# ============================================
def render_patients():
    st.markdown("## 👥 病人管理")
    
    patients = get_patients_data()
    pending_setup = [p for p in patients if p.get("status") == "pending_setup" or p.get("surgery", "") == "待設定"]
    active_patients = [p for p in patients if p not in pending_setup]
    
    if pending_setup:
        st.warning(f"🆕 有 {len(pending_setup)} 位新病人待完成設定")
        for patient in pending_setup:
            with st.expander(f"⚙️ {patient.get('name', '未知')} ({patient.get('phone', '')})"):
                st.info("請至「📋 臨床資料」頁面完成設定")
    
    st.markdown("### 📋 病人列表")
    search = st.text_input("🔍 搜尋", placeholder="姓名或電話...")
    
    filtered = active_patients
    if search:
        filtered = [p for p in filtered if search in p.get("name", "") or search in p.get("phone", "")]
    
    st.markdown(f"**共 {len(filtered)} 位病人**")
    
    for patient in filtered:
        status = patient.get("status", "normal")
        icon = "🔴" if status == "alert" else "🟡" if status == "warning" else "✅"
        
        with st.expander(f"{icon} **{patient.get('name', '未知')}** | D+{patient.get('post_op_day', 0)}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                - 年齡: {patient.get('age', '')} 歲
                - 性別: {patient.get('gender', '未填')}
                - 電話: {patient.get('phone', '')}
                """)
            with col2:
                st.markdown(f"""
                - 手術: {patient.get('surgery', '')}
                - 術後天數: D+{patient.get('post_op_day', 0)}
                """)
            
            if st.button("📋 查看/編輯臨床資料", key=f"clinical_{patient.get('id')}"):
                st.session_state.selected_patient = patient.get('id')
                st.session_state.admin_page = "clinical"
                st.rerun()

# ============================================
# 臨床資料管理（核心功能）
# ============================================
def render_clinical():
    st.markdown("## 📋 臨床資料管理")
    
    patients = get_patients_data()
    
    # 選擇病人
    patient_options = {f"{p.get('name', '未知')} ({p.get('id', '')})": p.get('id') for p in patients}
    
    selected_name = st.selectbox(
        "選擇病人",
        options=["-- 請選擇 --"] + list(patient_options.keys())
    )
    
    if selected_name == "-- 請選擇 --":
        st.info("👆 請選擇病人以查看或編輯臨床資料")
        return
    
    patient_id = patient_options[selected_name]
    patient = next((p for p in patients if p.get('id') == patient_id), None)
    
    if not patient:
        st.error("找不到病人資料")
        return
    
    # 取得現有臨床資料
    clinical = patient.get("clinical", {})
    
    st.markdown(f"### 📋 {patient.get('name', '')} 的臨床資料")
    
    # 使用 tabs 分類
    tabs = st.tabs([
        "一、基本資料",
        "二、腫瘤特徵",
        "三、手術資訊",
        "四、病理結果",
        "五、併發症",
        "六、康復追蹤",
        "七、後續治療",
        "八、ePRO/衛教"
    ])
    
    # === 一、基本資料與共病 ===
    with tabs[0]:
        st.markdown('<div class="section-header">一、病患基本資料與共病</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("年齡", value=clinical.get("age", patient.get("age", 65)), min_value=18, max_value=120)
            gender = st.selectbox("性別", CLINICAL_OPTIONS["gender"], index=CLINICAL_OPTIONS["gender"].index(clinical.get("gender", "男")) if clinical.get("gender") in CLINICAL_OPTIONS["gender"] else 0)
            height = st.number_input("身高 (cm)", value=clinical.get("height", 165), min_value=100, max_value=220)
            weight = st.number_input("體重 (kg)", value=clinical.get("weight", 60.0), min_value=30.0, max_value=200.0, step=0.1)
        
        with col2:
            bmi = weight / ((height/100) ** 2) if height > 0 else 0
            st.metric("BMI", f"{bmi:.1f}")
            smoking_status = st.selectbox("吸菸狀態", CLINICAL_OPTIONS["smoking_status"], index=CLINICAL_OPTIONS["smoking_status"].index(clinical.get("smoking_status", "從未吸菸")) if clinical.get("smoking_status") in CLINICAL_OPTIONS["smoking_status"] else 0)
            pack_year = st.number_input("Pack-year", value=clinical.get("pack_year", 0), min_value=0, max_value=200)
        
        with col3:
            asa_class = st.selectbox("ASA Class", CLINICAL_OPTIONS["asa_class"], index=CLINICAL_OPTIONS["asa_class"].index(clinical.get("asa_class", "II")) if clinical.get("asa_class") in CLINICAL_OPTIONS["asa_class"] else 1)
            ecog = st.selectbox("ECOG Performance Status", CLINICAL_OPTIONS["ecog"], index=CLINICAL_OPTIONS["ecog"].index(clinical.get("ecog", "0")) if clinical.get("ecog") in CLINICAL_OPTIONS["ecog"] else 0)
        
        st.markdown("**肺功能**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            fev1 = st.number_input("FEV1 (%)", value=clinical.get("fev1", 80), min_value=0, max_value=150)
        with col2:
            dlco = st.number_input("DLCO (%)", value=clinical.get("dlco", 80), min_value=0, max_value=150)
        with col3:
            ppo_fev1 = st.number_input("ppoFEV1 (%)", value=clinical.get("ppo_fev1", 0), min_value=0, max_value=150)
        with col4:
            ppo_dlco = st.number_input("ppoDLCO (%)", value=clinical.get("ppo_dlco", 0), min_value=0, max_value=150)
        
        st.markdown("**共病**")
        comorbidities = st.multiselect("選擇共病", CLINICAL_OPTIONS["comorbidities"], default=clinical.get("comorbidities", []))
        
        prior_thoracic = st.checkbox("既往胸腔手術史", value=clinical.get("prior_thoracic", False))
        prior_radiation = st.checkbox("既往胸腔放射治療史", value=clinical.get("prior_radiation", False))
    
    # === 二、腫瘤特徵 ===
    with tabs[1]:
        st.markdown('<div class="section-header">二、影像與腫瘤特徵</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            tumor_size = st.number_input("腫瘤最大徑 (cm)", value=clinical.get("tumor_size", 2.0), min_value=0.1, max_value=20.0, step=0.1)
            tumor_location = st.selectbox("腫瘤位置", CLINICAL_OPTIONS["tumor_location"], index=CLINICAL_OPTIONS["tumor_location"].index(clinical.get("tumor_location", "周邊型")) if clinical.get("tumor_location") in CLINICAL_OPTIONS["tumor_location"] else 0)
            lobe = st.selectbox("分葉位置", CLINICAL_OPTIONS["lobe"], index=CLINICAL_OPTIONS["lobe"].index(clinical.get("lobe", "RUL")) if clinical.get("lobe") in CLINICAL_OPTIONS["lobe"] else 0)
        
        with col2:
            ggo_ratio = st.slider("GGO Ratio (%)", 0, 100, clinical.get("ggo_ratio", 50))
            ctr = st.slider("CTR - Consolidation Tumor Ratio (%)", 0, 100, clinical.get("ctr", 50))
            suv_max = st.number_input("SUVmax (PET-CT)", value=clinical.get("suv_max", 0.0), min_value=0.0, max_value=50.0, step=0.1)
        
        st.markdown("**影像學分期 (cTNM)**")
        col1, col2, col3 = st.columns(3)
        with col1:
            c_t = st.selectbox("cT", T_STAGE, index=T_STAGE.index(clinical.get("c_t", "T1a")) if clinical.get("c_t") in T_STAGE else 2)
        with col2:
            c_n = st.selectbox("cN", N_STAGE, index=N_STAGE.index(clinical.get("c_n", "N0")) if clinical.get("c_n") in N_STAGE else 0)
        with col3:
            c_m = st.selectbox("cM", M_STAGE, index=M_STAGE.index(clinical.get("c_m", "M0")) if clinical.get("c_m") in M_STAGE else 0)
        
        multiple_lesions = st.checkbox("多發病灶", value=clinical.get("multiple_lesions", False))
        pleural_invasion_image = st.checkbox("影像學疑似胸膜侵犯", value=clinical.get("pleural_invasion_image", False))
    
    # === 三、手術資訊 ===
    with tabs[2]:
        st.markdown('<div class="section-header">三、術式與手術特徵</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            surgery_date = st.date_input("手術日期", value=datetime.strptime(clinical.get("surgery_date", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d").date() if clinical.get("surgery_date") else datetime.now().date())
            surgery_type = st.selectbox("手術方式", CLINICAL_OPTIONS["surgery_type"], index=CLINICAL_OPTIONS["surgery_type"].index(clinical.get("surgery_type", "Lobectomy")) if clinical.get("surgery_type") in CLINICAL_OPTIONS["surgery_type"] else 2)
            surgery_approach = st.selectbox("手術途徑", CLINICAL_OPTIONS["surgery_approach"], index=CLINICAL_OPTIONS["surgery_approach"].index(clinical.get("surgery_approach", "VATS (多孔)")) if clinical.get("surgery_approach") in CLINICAL_OPTIONS["surgery_approach"] else 0)
        
        with col2:
            op_time = st.number_input("手術時間 (分鐘)", value=clinical.get("op_time", 180), min_value=0, max_value=1000)
            ebl = st.number_input("出血量 (ml)", value=clinical.get("ebl", 100), min_value=0, max_value=5000)
            conversion = st.checkbox("轉換開胸", value=clinical.get("conversion", False))
        
        st.markdown("**淋巴結處理**")
        col1, col2, col3 = st.columns(3)
        with col1:
            ln_dissection = st.selectbox("淋巴結處理", CLINICAL_OPTIONS["ln_dissection"], index=CLINICAL_OPTIONS["ln_dissection"].index(clinical.get("ln_dissection", "系統性淋巴結廓清")) if clinical.get("ln_dissection") in CLINICAL_OPTIONS["ln_dissection"] else 0)
        with col2:
            ln_stations = st.number_input("採檢站數", value=clinical.get("ln_stations", 5), min_value=0, max_value=20)
        with col3:
            ln_total = st.number_input("採檢顆數", value=clinical.get("ln_total", 15), min_value=0, max_value=100)
        
        combined_procedure = st.text_input("合併手術", value=clinical.get("combined_procedure", ""), placeholder="例如：pleurectomy, decortication")
    
    # === 四、病理結果 ===
    with tabs[3]:
        st.markdown('<div class="section-header">四、病理結果</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            pathology_type = st.selectbox("病理診斷", CLINICAL_OPTIONS["pathology_type"], index=CLINICAL_OPTIONS["pathology_type"].index(clinical.get("pathology_type", "Invasive adenocarcinoma")) if clinical.get("pathology_type") in CLINICAL_OPTIONS["pathology_type"] else 2)
            
            if "adenocarcinoma" in pathology_type.lower():
                adeno_subtype = st.selectbox("腺癌亞型", CLINICAL_OPTIONS["adenocarcinoma_subtype"], index=CLINICAL_OPTIONS["adenocarcinoma_subtype"].index(clinical.get("adeno_subtype", "Acinar")) if clinical.get("adeno_subtype") in CLINICAL_OPTIONS["adenocarcinoma_subtype"] else 1)
            
            margin_status = st.selectbox("Margin 狀態", CLINICAL_OPTIONS["margin_status"], index=CLINICAL_OPTIONS["margin_status"].index(clinical.get("margin_status", "R0 (完全切除)")) if clinical.get("margin_status") in CLINICAL_OPTIONS["margin_status"] else 0)
        
        with col2:
            lvi = st.selectbox("Lymphovascular Invasion", CLINICAL_OPTIONS["lvi"], index=CLINICAL_OPTIONS["lvi"].index(clinical.get("lvi", "無")) if clinical.get("lvi") in CLINICAL_OPTIONS["lvi"] else 0)
            vpi = st.selectbox("Visceral Pleural Invasion", CLINICAL_OPTIONS["vpi"], index=CLINICAL_OPTIONS["vpi"].index(clinical.get("vpi", "PL0")) if clinical.get("vpi") in CLINICAL_OPTIONS["vpi"] else 0)
            stas = st.selectbox("STAS", CLINICAL_OPTIONS["stas"], index=CLINICAL_OPTIONS["stas"].index(clinical.get("stas", "無")) if clinical.get("stas") in CLINICAL_OPTIONS["stas"] else 0)
        
        st.markdown("**病理分期 (pTNM)**")
        col1, col2, col3 = st.columns(3)
        with col1:
            p_t = st.selectbox("pT", T_STAGE, index=T_STAGE.index(clinical.get("p_t", "T1a")) if clinical.get("p_t") in T_STAGE else 2, key="p_t")
        with col2:
            p_n = st.selectbox("pN", N_STAGE, index=N_STAGE.index(clinical.get("p_n", "N0")) if clinical.get("p_n") in N_STAGE else 0, key="p_n")
        with col3:
            p_m = st.selectbox("pM", M_STAGE, index=M_STAGE.index(clinical.get("p_m", "M0")) if clinical.get("p_m") in M_STAGE else 0, key="p_m")
        
        st.markdown("**分子檢測**")
        col1, col2, col3 = st.columns(3)
        with col1:
            egfr = st.selectbox("EGFR", CLINICAL_OPTIONS["egfr_status"], index=CLINICAL_OPTIONS["egfr_status"].index(clinical.get("egfr", "未檢測")) if clinical.get("egfr") in CLINICAL_OPTIONS["egfr_status"] else 6)
        with col2:
            alk = st.selectbox("ALK", CLINICAL_OPTIONS["alk_status"], index=CLINICAL_OPTIONS["alk_status"].index(clinical.get("alk", "未檢測")) if clinical.get("alk") in CLINICAL_OPTIONS["alk_status"] else 2)
        with col3:
            pdl1 = st.selectbox("PD-L1", CLINICAL_OPTIONS["pdl1_status"], index=CLINICAL_OPTIONS["pdl1_status"].index(clinical.get("pdl1", "未檢測")) if clinical.get("pdl1") in CLINICAL_OPTIONS["pdl1_status"] else 3)
    
    # === 五、併發症 ===
    with tabs[4]:
        st.markdown('<div class="section-header">五、圍手術期照護與併發症</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            complications = st.multiselect("術後併發症", CLINICAL_OPTIONS["complications"], default=clinical.get("complications", []))
            icu_days = st.number_input("ICU 天數", value=clinical.get("icu_days", 0), min_value=0, max_value=100)
        
        with col2:
            chest_tube_count = st.number_input("胸管支數", value=clinical.get("chest_tube_count", 1), min_value=0, max_value=5)
            chest_tube_days = st.number_input("胸管留置天數", value=clinical.get("chest_tube_days", 3), min_value=0, max_value=60)
            air_leak_grade = st.selectbox("氣漏程度", ["無", "Grade 1", "Grade 2", "Grade 3", "Grade 4"], index=["無", "Grade 1", "Grade 2", "Grade 3", "Grade 4"].index(clinical.get("air_leak_grade", "無")) if clinical.get("air_leak_grade") in ["無", "Grade 1", "Grade 2", "Grade 3", "Grade 4"] else 0)
        
        st.markdown("**住院相關**")
        col1, col2, col3 = st.columns(3)
        with col1:
            los = st.number_input("住院天數", value=clinical.get("los", 5), min_value=0, max_value=365)
        with col2:
            readmit_30 = st.checkbox("30天內再入院", value=clinical.get("readmit_30", False))
        with col3:
            readmit_90 = st.checkbox("90天內再入院", value=clinical.get("readmit_90", False))
    
    # === 六、康復追蹤 ===
    with tabs[5]:
        st.markdown('<div class="section-header">六、功能回復與康復</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            preop_rehab = st.checkbox("術前肺復健", value=clinical.get("preop_rehab", False))
            early_ambulation = st.checkbox("術後早期下床 (POD1)", value=clinical.get("early_ambulation", True))
            incentive_spirometer = st.selectbox("呼吸訓練依從性", ["優良", "普通", "差", "未執行"], index=["優良", "普通", "差", "未執行"].index(clinical.get("incentive_spirometer", "優良")) if clinical.get("incentive_spirometer") in ["優良", "普通", "差", "未執行"] else 0)
        
        with col2:
            pain_control = st.multiselect("疼痛控制方式", CLINICAL_OPTIONS["pain_control"], default=clinical.get("pain_control", []))
            adl_recovery = st.selectbox("ADL 回復程度", ["完全獨立", "輕度依賴", "中度依賴", "重度依賴"], index=["完全獨立", "輕度依賴", "中度依賴", "重度依賴"].index(clinical.get("adl_recovery", "完全獨立")) if clinical.get("adl_recovery") in ["完全獨立", "輕度依賴", "中度依賴", "重度依賴"] else 0)
        
        follow_up_compliance = st.slider("回診依從性 (%)", 0, 100, clinical.get("follow_up_compliance", 100))
    
    # === 七、後續治療 ===
    with tabs[6]:
        st.markdown('<div class="section-header">七、腫瘤治療後續追蹤</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            adjuvant = st.selectbox("輔助治療", CLINICAL_OPTIONS["adjuvant_therapy"], index=CLINICAL_OPTIONS["adjuvant_therapy"].index(clinical.get("adjuvant", "無需輔助治療")) if clinical.get("adjuvant") in CLINICAL_OPTIONS["adjuvant_therapy"] else 0)
            mdt_date = st.date_input("MDT 討論日期", value=datetime.strptime(clinical.get("mdt_date", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d").date() if clinical.get("mdt_date") else None)
        
        with col2:
            mdt_decision = st.text_area("MDT 決議內容", value=clinical.get("mdt_decision", ""), height=100)
        
        st.markdown("**追蹤影像排程**")
        col1, col2, col3 = st.columns(3)
        with col1:
            fu_3m = st.date_input("3個月 CT", value=datetime.strptime(clinical.get("fu_3m", ""), "%Y-%m-%d").date() if clinical.get("fu_3m") else None, key="fu_3m")
        with col2:
            fu_6m = st.date_input("6個月 CT", value=datetime.strptime(clinical.get("fu_6m", ""), "%Y-%m-%d").date() if clinical.get("fu_6m") else None, key="fu_6m")
        with col3:
            fu_12m = st.date_input("12個月 CT", value=datetime.strptime(clinical.get("fu_12m", ""), "%Y-%m-%d").date() if clinical.get("fu_12m") else None, key="fu_12m")
        
        recurrence = st.checkbox("復發", value=clinical.get("recurrence", False))
        if recurrence:
            recurrence_type = st.selectbox("復發類型", ["局部復發", "遠端轉移", "局部+遠端"], index=["局部復發", "遠端轉移", "局部+遠端"].index(clinical.get("recurrence_type", "局部復發")) if clinical.get("recurrence_type") in ["局部復發", "遠端轉移", "局部+遠端"] else 0)
            recurrence_date = st.date_input("復發日期")
    
    # === 八、ePRO/衛教 ===
    with tabs[7]:
        st.markdown('<div class="section-header">八、病人教育與 ePRO 追蹤</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**術前衛教**")
            preop_education = st.checkbox("已完成術前衛教", value=clinical.get("preop_education", False))
            education_comprehension = st.selectbox("衛教理解程度", ["優", "良", "可", "差"], index=["優", "良", "可", "差"].index(clinical.get("education_comprehension", "良")) if clinical.get("education_comprehension") in ["優", "良", "可", "差"] else 1)
            sdm_completed = st.checkbox("已完成 SDM 共享決策", value=clinical.get("sdm_completed", False))
        
        with col2:
            st.markdown("**ePRO 追蹤狀態**")
            epro_enrolled = st.checkbox("已加入 ePRO 追蹤", value=clinical.get("epro_enrolled", True))
            epro_compliance = st.slider("ePRO 填答率 (%)", 0, 100, clinical.get("epro_compliance", 80))
            chatbot_usage = st.number_input("AI 對話次數", value=clinical.get("chatbot_usage", 0), min_value=0)
        
        st.markdown("**最近症狀監測摘要**")
        symptom_summary = st.text_area("症狀摘要 (由系統自動更新)", value=clinical.get("symptom_summary", ""), height=100, disabled=True)
        nurse_notes = st.text_area("個管師備註", value=clinical.get("nurse_notes", ""), height=100)
    
    # === 儲存按鈕 ===
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 儲存所有臨床資料", use_container_width=True, type="primary"):
            # 收集所有資料
            new_clinical = {
                # 基本資料
                "age": age, "gender": gender, "height": height, "weight": weight,
                "smoking_status": smoking_status, "pack_year": pack_year,
                "asa_class": asa_class, "ecog": ecog,
                "fev1": fev1, "dlco": dlco, "ppo_fev1": ppo_fev1, "ppo_dlco": ppo_dlco,
                "comorbidities": comorbidities,
                "prior_thoracic": prior_thoracic, "prior_radiation": prior_radiation,
                
                # 腫瘤特徵
                "tumor_size": tumor_size, "tumor_location": tumor_location, "lobe": lobe,
                "ggo_ratio": ggo_ratio, "ctr": ctr, "suv_max": suv_max,
                "c_t": c_t, "c_n": c_n, "c_m": c_m,
                "multiple_lesions": multiple_lesions, "pleural_invasion_image": pleural_invasion_image,
                
                # 手術資訊
                "surgery_date": surgery_date.strftime("%Y-%m-%d"),
                "surgery_type": surgery_type, "surgery_approach": surgery_approach,
                "op_time": op_time, "ebl": ebl, "conversion": conversion,
                "ln_dissection": ln_dissection, "ln_stations": ln_stations, "ln_total": ln_total,
                "combined_procedure": combined_procedure,
                
                # 病理
                "pathology_type": pathology_type, "margin_status": margin_status,
                "lvi": lvi, "vpi": vpi, "stas": stas,
                "p_t": p_t, "p_n": p_n, "p_m": p_m,
                "egfr": egfr, "alk": alk, "pdl1": pdl1,
                
                # 併發症
                "complications": complications, "icu_days": icu_days,
                "chest_tube_count": chest_tube_count, "chest_tube_days": chest_tube_days,
                "air_leak_grade": air_leak_grade, "los": los,
                "readmit_30": readmit_30, "readmit_90": readmit_90,
                
                # 康復
                "preop_rehab": preop_rehab, "early_ambulation": early_ambulation,
                "incentive_spirometer": incentive_spirometer, "pain_control": pain_control,
                "adl_recovery": adl_recovery, "follow_up_compliance": follow_up_compliance,
                
                # 後續治療
                "adjuvant": adjuvant, "mdt_decision": mdt_decision,
                "fu_3m": fu_3m.strftime("%Y-%m-%d") if fu_3m else "",
                "fu_6m": fu_6m.strftime("%Y-%m-%d") if fu_6m else "",
                "fu_12m": fu_12m.strftime("%Y-%m-%d") if fu_12m else "",
                "recurrence": recurrence,
                
                # ePRO
                "preop_education": preop_education, "education_comprehension": education_comprehension,
                "sdm_completed": sdm_completed, "epro_enrolled": epro_enrolled,
                "epro_compliance": epro_compliance, "chatbot_usage": chatbot_usage,
                "nurse_notes": nurse_notes,
            }
            
            if save_patient_clinical_data(patient_id, new_clinical):
                st.success("✅ 臨床資料已儲存！")
                st.balloons()
            else:
                st.warning("⚠️ Demo 模式：資料已暫存（重整頁面後會消失）")

# ============================================
# 介入紀錄
# ============================================
def render_interventions():
    st.markdown("## 📝 介入紀錄")
    
    tab1, tab2 = st.tabs(["📋 紀錄列表", "➕ 新增紀錄"])
    
    with tab1:
        interventions = []
        if DATA_MANAGER_AVAILABLE:
            try:
                interventions = get_interventions()
            except:
                pass
        
        if interventions:
            for record in interventions:
                st.markdown(f"""
                <div class="intervention-card">
                    <strong>{record.get('patient_name', record.get('patient_id', ''))}</strong>
                    <span style="background:#dbeafe;color:#1e40af;padding:2px 8px;border-radius:4px;font-size:11px;margin-left:6px;">{record.get('type', '')}</span>
                    <br><small>{record.get('time', '')}</small>
                    <p style="margin: 8px 0 0 0;">{record.get('content', '')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("目前沒有介入紀錄")
    
    with tab2:
        with st.form("new_intervention"):
            patients = get_patients_data()
            patient_names = ["選擇病人..."] + [f"{p.get('name', '未知')} ({p.get('id', '')})" for p in patients]
            
            patient = st.selectbox("病人", patient_names)
            method = st.selectbox("聯繫方式", ["電話", "LINE", "簡訊", "門診", "視訊"])
            duration = st.text_input("通話時間", placeholder="例如：5分鐘")
            content = st.text_area("紀錄內容", height=150)
            referral = st.selectbox("轉介", ["無", "緩和醫療", "營養諮詢", "復健科", "心理諮商", "社工"])
            
            if st.form_submit_button("💾 儲存紀錄", use_container_width=True, type="primary"):
                if patient != "選擇病人..." and content:
                    st.success("✅ 紀錄已儲存！")
                else:
                    st.error("請選擇病人並填寫紀錄內容")

# ============================================
# 衛教推送系統
# ============================================
# 載入衛教系統
try:
    from education_system import (
        EDUCATION_MATERIALS, AUTO_PUSH_RULES, education_manager,
        get_materials_by_category, get_material_by_id
    )
    EDUCATION_AVAILABLE = True
except:
    EDUCATION_AVAILABLE = False
    EDUCATION_MATERIALS = {}
    AUTO_PUSH_RULES = []

def render_education():
    st.markdown("## 📚 衛教推送系統")
    
    if not EDUCATION_AVAILABLE:
        st.warning("衛教系統模組載入中...")
    
    tabs = st.tabs(["📤 手動推送", "⚙️ 自動規則", "📋 推送紀錄", "📖 衛教單張庫"])
    
    # === 手動推送 ===
    with tabs[0]:
        st.markdown("### 📤 手動推送衛教單張")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**1️⃣ 選擇病人**")
            patients = get_patients_data()
            patient_options = {f"{p.get('name', '未知')} ({p.get('id', '')}) - D+{p.get('post_op_day', 0)}": p for p in patients}
            
            selected_patient_name = st.selectbox(
                "選擇病人",
                options=["-- 請選擇 --"] + list(patient_options.keys()),
                key="edu_patient"
            )
            
            if selected_patient_name != "-- 請選擇 --":
                patient = patient_options[selected_patient_name]
                st.info(f"📋 術後第 {patient.get('post_op_day', 0)} 天 | {patient.get('surgery', '未知手術')}")
        
        with col2:
            st.markdown("**2️⃣ 選擇衛教單張**")
            
            # 依類別分組
            categories = {}
            for key, material in EDUCATION_MATERIALS.items():
                cat = material.get("category", "其他")
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append({"key": key, **material})
            
            selected_category = st.selectbox(
                "類別",
                options=list(categories.keys()) if categories else ["無資料"],
                key="edu_category"
            )
            
            if selected_category and selected_category in categories:
                materials_in_cat = categories[selected_category]
                material_options = {f"{m['icon']} {m['title']}": m['key'] for m in materials_in_cat}
                
                selected_material_name = st.selectbox(
                    "衛教單張",
                    options=list(material_options.keys()),
                    key="edu_material"
                )
                
                if selected_material_name:
                    material_key = material_options[selected_material_name]
                    material = EDUCATION_MATERIALS.get(material_key, {})
                    st.caption(material.get("description", ""))
        
        st.markdown("---")
        
        # 個人化訊息
        custom_message = st.text_area(
            "📝 附加個人化訊息（選填）",
            placeholder="例如：王先生您好，根據您今天回報的呼吸狀況，特別提供這份呼吸運動指南...",
            height=100
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📤 推送給病人", use_container_width=True, type="primary"):
                if selected_patient_name == "-- 請選擇 --":
                    st.error("請選擇病人")
                elif not EDUCATION_AVAILABLE:
                    st.warning("衛教系統載入中，請稍後再試")
                else:
                    patient = patient_options[selected_patient_name]
                    material_key = material_options.get(selected_material_name, "")
                    
                    if material_key:
                        record = education_manager.push_material(
                            patient_id=patient.get("id"),
                            patient_name=patient.get("name"),
                            material_id=material_key,
                            push_type="manual",
                            pushed_by=st.session_state.username
                        )
                        
                        if record:
                            st.success(f"✅ 已推送「{selected_material_name}」給 {patient.get('name')}！")
                            st.balloons()
                        else:
                            st.error("推送失敗")
        
        # 快速推送建議
        st.markdown("---")
        st.markdown("### 💡 智慧推送建議")
        
        if selected_patient_name != "-- 請選擇 --":
            patient = patient_options[selected_patient_name]
            post_op_day = patient.get("post_op_day", 0)
            
            recommendations = []
            
            if post_op_day <= 3:
                recommendations = [
                    ("BREATHING_EXERCISE", "呼吸運動訓練", "術後早期必備"),
                    ("PAIN_MANAGEMENT", "疼痛控制指南", "術後疼痛管理"),
                    ("EARLY_AMBULATION", "早期下床活動", "促進恢復"),
                ]
            elif post_op_day <= 7:
                recommendations = [
                    ("HOME_CARE", "居家照護指南", "即將出院"),
                    ("WARNING_SIGNS", "警示徵象", "出院前必讀"),
                    ("WOUND_CARE", "傷口照護", "居家換藥"),
                ]
            elif post_op_day <= 14:
                recommendations = [
                    ("FOLLOW_UP", "術後追蹤檢查", "回診準備"),
                    ("PHYSICAL_ACTIVITY", "術後運動指南", "漸進式恢復"),
                    ("NUTRITION", "營養指南", "促進癒合"),
                ]
            else:
                recommendations = [
                    ("EMOTIONAL_SUPPORT", "心理調適指南", "長期照護"),
                    ("SMOKING_CESSATION", "戒菸指南", "預防復發"),
                ]
            
            st.markdown(f"**根據 D+{post_op_day} 建議推送：**")
            
            cols = st.columns(len(recommendations))
            for i, (key, title, reason) in enumerate(recommendations):
                with cols[i]:
                    material = EDUCATION_MATERIALS.get(key, {})
                    st.markdown(f"""
                    <div style="background: #f0f9ff; border-radius: 10px; padding: 12px; text-align: center; height: 120px;">
                        <div style="font-size: 24px;">{material.get('icon', '📄')}</div>
                        <div style="font-size: 13px; font-weight: 600; margin-top: 4px;">{title}</div>
                        <div style="font-size: 11px; color: #64748b;">{reason}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("推送", key=f"quick_{key}", use_container_width=True):
                        if EDUCATION_AVAILABLE:
                            record = education_manager.push_material(
                                patient_id=patient.get("id"),
                                patient_name=patient.get("name"),
                                material_id=key,
                                push_type="manual",
                                pushed_by=st.session_state.username
                            )
                            if record:
                                st.success(f"✅ 已推送！")
    
    # === 自動規則 ===
    with tabs[1]:
        st.markdown("### ⚙️ 自動推送規則")
        st.caption("系統會依據以下規則自動推送衛教單張給病人")
        
        # 依術後天數
        st.markdown("#### 📅 依術後天數自動推送")
        
        day_rules = [r for r in AUTO_PUSH_RULES if r.get("trigger_type") == "post_op_day"]
        
        for rule in sorted(day_rules, key=lambda x: x.get("trigger_value", 0)):
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.markdown(f"**D+{rule.get('trigger_value')}**")
            
            with col2:
                materials = rule.get("materials", [])
                material_names = [EDUCATION_MATERIALS.get(m, {}).get("title", m) for m in materials]
                st.markdown(", ".join(material_names))
            
            with col3:
                enabled = st.checkbox("啟用", value=rule.get("enabled", True), key=f"rule_{rule['id']}")
        
        st.markdown("---")
        
        # 依症狀觸發
        st.markdown("#### 🩺 依症狀自動推送")
        
        symptom_rules = [r for r in AUTO_PUSH_RULES if r.get("trigger_type") == "symptom"]
        
        for rule in symptom_rules:
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.markdown(f"**{rule.get('trigger_value')}**")
            
            with col2:
                materials = rule.get("materials", [])
                material_names = [EDUCATION_MATERIALS.get(m, {}).get("title", m) for m in materials]
                st.markdown(", ".join(material_names))
            
            with col3:
                enabled = st.checkbox("啟用", value=rule.get("enabled", True), key=f"rule_{rule['id']}")
        
        st.markdown("---")
        
        # 依治療計畫
        st.markdown("#### 💊 依治療計畫自動推送")
        
        treatment_rules = [r for r in AUTO_PUSH_RULES if r.get("trigger_type") == "treatment"]
        
        for rule in treatment_rules:
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.markdown(f"**{rule.get('name')}**")
            
            with col2:
                materials = rule.get("materials", [])
                material_names = [EDUCATION_MATERIALS.get(m, {}).get("title", m) for m in materials]
                st.markdown(", ".join(material_names))
            
            with col3:
                enabled = st.checkbox("啟用", value=rule.get("enabled", True), key=f"rule_{rule['id']}")
    
    # === 推送紀錄 ===
    with tabs[2]:
        st.markdown("### 📋 推送紀錄")
        
        # 篩選
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_patient = st.selectbox("病人", ["全部"] + [p.get("name", "") for p in get_patients_data()], key="filter_patient")
        with col2:
            filter_type = st.selectbox("推送類型", ["全部", "手動推送", "自動推送"], key="filter_type")
        with col3:
            filter_status = st.selectbox("狀態", ["全部", "已送出", "已讀取"], key="filter_status")
        
        st.markdown("---")
        
        # 取得紀錄
        if EDUCATION_AVAILABLE:
            history = education_manager.get_all_history()
        else:
            # 模擬資料
            history = [
                {
                    "id": "PUSH001",
                    "patient_name": "王大明",
                    "material_title": "呼吸運動訓練指南",
                    "category": "呼吸訓練",
                    "push_type": "auto",
                    "pushed_by": "system",
                    "pushed_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                    "status": "read"
                },
                {
                    "id": "PUSH002",
                    "patient_name": "王大明",
                    "material_title": "術後疼痛控制指南",
                    "category": "疼痛控制",
                    "push_type": "manual",
                    "pushed_by": "nurse01",
                    "pushed_at": (datetime.now() - timedelta(hours=5)).isoformat(),
                    "status": "sent"
                },
                {
                    "id": "PUSH003",
                    "patient_name": "李小華",
                    "material_title": "居家照護指南",
                    "category": "居家照護",
                    "push_type": "auto",
                    "pushed_by": "system",
                    "pushed_at": (datetime.now() - timedelta(days=1)).isoformat(),
                    "status": "read"
                },
            ]
        
        # 顯示紀錄
        if history:
            for record in history[:20]:
                push_type_badge = "🤖 自動" if record.get("push_type") == "auto" else "👤 手動"
                status_badge = "✅ 已讀" if record.get("status") == "read" else "📤 已送出"
                
                # 格式化時間
                try:
                    pushed_time = datetime.fromisoformat(record.get("pushed_at", ""))
                    time_display = pushed_time.strftime("%m/%d %H:%M")
                except:
                    time_display = record.get("pushed_at", "")[:16]
                
                st.markdown(f"""
                <div style="background: #f8fafc; border-radius: 10px; padding: 14px; margin-bottom: 10px; border-left: 3px solid {'#22c55e' if record.get('status') == 'read' else '#3b82f6'};">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span style="font-weight: 600;">{record.get('patient_name', '')}</span>
                            <span style="background: #e0e7ff; color: #3730a3; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 8px;">{record.get('category', '')}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 12px; color: #64748b;">{time_display}</span>
                            <br>
                            <span style="font-size: 11px;">{push_type_badge} | {status_badge}</span>
                        </div>
                    </div>
                    <div style="margin-top: 6px; font-size: 14px;">{record.get('material_title', '')}</div>
                    <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">推送者：{record.get('pushed_by', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("目前沒有推送紀錄")
        
        # 統計
        st.markdown("---")
        st.markdown("### 📊 推送統計")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("今日推送", len([r for r in history if r.get("pushed_at", "")[:10] == datetime.now().strftime("%Y-%m-%d")]))
        col2.metric("本週推送", len(history))
        col3.metric("已讀率", f"{len([r for r in history if r.get('status') == 'read']) / max(len(history), 1) * 100:.0f}%")
        col4.metric("自動推送", len([r for r in history if r.get("push_type") == "auto"]))
    
    # === 衛教單張庫 ===
    with tabs[3]:
        st.markdown("### 📖 衛教單張庫")
        
        # 類別篩選
        all_categories = list(set(m.get("category", "其他") for m in EDUCATION_MATERIALS.values()))
        selected_cat = st.selectbox("篩選類別", ["全部"] + all_categories, key="lib_category")
        
        # 顯示單張
        for key, material in EDUCATION_MATERIALS.items():
            if selected_cat != "全部" and material.get("category") != selected_cat:
                continue
            
            with st.expander(f"{material.get('icon', '📄')} {material.get('title', key)}"):
                st.markdown(f"**類別：** {material.get('category', '')}")
                st.markdown(f"**說明：** {material.get('description', '')}")
                st.markdown("---")
                st.markdown(material.get("content", ""))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.button("✏️ 編輯", key=f"edit_{key}", use_container_width=True)
                with col2:
                    st.button("📤 快速推送", key=f"push_{key}", use_container_width=True)

# ============================================
# 報表統計
# ============================================
def render_reports():
    st.markdown("## 📈 報表統計")
    
    tab1, tab2 = st.tabs(["📊 總覽", "💾 匯出"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 收案狀態")
            fig = px.pie(
                values=[35, 5, 2],
                names=["正常追蹤", "黃色警示", "紅色警示"],
                color_discrete_sequence=["#22c55e", "#f59e0b", "#ef4444"]
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 症狀分布")
            fig = px.bar(
                x=[45, 38, 25, 22, 18],
                y=["疲勞", "疼痛", "呼吸困難", "咳嗽", "睡眠問題"],
                orientation='h',
                color_discrete_sequence=["#3b82f6"]
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 數據匯出")
        format_option = st.selectbox("匯出格式", ["Excel (.xlsx)", "CSV (.csv)", "JSON"])
        st.checkbox("去識別化處理", value=True)
        
        if st.button("📥 產生匯出檔案", use_container_width=True, type="primary"):
            st.info("💡 匯出功能開發中...")

# ============================================
# 主程式
# ============================================
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        render_sidebar()
        
        if st.session_state.admin_page == "dashboard":
            render_dashboard()
        elif st.session_state.admin_page == "alerts":
            render_alerts()
        elif st.session_state.admin_page == "patients":
            render_patients()
        elif st.session_state.admin_page == "clinical":
            render_clinical()
        elif st.session_state.admin_page == "education":
            render_education()
        elif st.session_state.admin_page == "interventions":
            render_interventions()
        elif st.session_state.admin_page == "reports":
            render_reports()
        else:
            render_dashboard()

if __name__ == "__main__":
    main()
