"""
AI-CARE Lung Pro - 設定檔
=========================

🔑 在這裡設定您的 API Key 和管理員帳號密碼
"""

# ============================================
# OpenAI API 設定
# ============================================
OPENAI_API_KEY = ""  # ← 填入您的 OpenAI API Key，例如 "sk-proj-xxxxx"
DEFAULT_MODEL = "gpt-4o-mini"  # 可選：gpt-4o-mini, gpt-4o, gpt-3.5-turbo

# ============================================
# 管理後台登入帳號（可設定多組）
# ============================================
ADMIN_CREDENTIALS = {
    # "帳號": "密碼"
    "admin": "aicare2024",      # 管理員
    "nurse01": "nurse2024",     # 個管師 1
    "nurse02": "nurse2024",     # 個管師 2
}

# ============================================
# 系統設定
# ============================================
SYSTEM_NAME = "AI-CARE Lung"
HOSPITAL_NAME = "三軍總醫院"
DEPARTMENT_NAME = "數位醫學中心"

# 警示閾值
ALERT_THRESHOLD_RED = 7      # 紅色警示（≥7分）
ALERT_THRESHOLD_YELLOW = 4   # 黃色警示（≥4分）

# 資料檔案路徑
DATA_FILE = "data/patient_records.json"
