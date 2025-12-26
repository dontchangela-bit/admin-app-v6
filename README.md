# AI-CARE Lung - 管理後台

## 部署步驟

1. 在 GitHub 建立新 Repo（例如：aicare-admin）
2. 上傳這個資料夾內的所有檔案
3. 到 Streamlit Cloud 部署
4. Main file 選擇 `app.py`

## 登入帳號

| 角色 | 帳號 | 密碼 |
|------|------|------|
| 管理員 | admin | aicare2024 |
| 個管師1 | nurse01 | nurse2024 |
| 個管師2 | nurse02 | nurse2024 |

## 檔案清單
- app.py（主程式）
- config.py（設定，可修改帳號密碼）
- data_manager.py（資料管理）
- requirements.txt（套件）
- data/patient_records.json（資料儲存）
- .streamlit/config.toml（樣式設定）

## 修改帳號密碼
編輯 config.py 中的 ADMIN_CREDENTIALS
