"""
AI-CARE Lung Pro - 資料管理模組
================================

處理病人回報資料的讀取與儲存
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import uuid

DATA_FILE = "data/patient_records.json"

def ensure_data_file():
    """確保資料檔案存在"""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        initial_data = {
            "patients": {},
            "reports": [],
            "alerts": [],
            "interventions": []
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=2)

def load_data() -> Dict:
    """載入所有資料"""
    ensure_data_file()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"patients": {}, "reports": [], "alerts": [], "interventions": []}

def save_data(data: Dict):
    """儲存資料"""
    ensure_data_file()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def get_or_create_patient(patient_id: str, patient_info: Dict = None) -> Dict:
    """取得或建立病人資料"""
    data = load_data()
    
    if patient_id not in data["patients"]:
        # 建立新病人
        data["patients"][patient_id] = {
            "id": patient_id,
            "name": patient_info.get("name", f"病人{patient_id[-4:]}") if patient_info else f"病人{patient_id[-4:]}",
            "age": patient_info.get("age", 65) if patient_info else 65,
            "surgery": patient_info.get("surgery", "肺葉切除術") if patient_info else "肺葉切除術",
            "surgery_date": patient_info.get("surgery_date", datetime.now().strftime("%Y-%m-%d")) if patient_info else datetime.now().strftime("%Y-%m-%d"),
            "diagnosis": patient_info.get("diagnosis", "肺癌") if patient_info else "肺癌",
            "phone": patient_info.get("phone", "") if patient_info else "",
            "created_at": datetime.now().isoformat(),
            "last_report": None,
            "total_reports": 0,
            "compliance_rate": 0
        }
        save_data(data)
    
    return data["patients"][patient_id]

def save_report(patient_id: str, report: Dict):
    """儲存症狀回報"""
    data = load_data()
    
    # 建立回報記錄
    report_record = {
        "id": str(uuid.uuid4())[:8],
        "patient_id": patient_id,
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "symptoms": report.get("symptoms", []),
        "scores": report.get("scores", {}),
        "overall_score": report.get("overall_score", 0),
        "conversation": report.get("conversation", []),
        "status": "completed"
    }
    
    data["reports"].append(report_record)
    
    # 更新病人資料
    if patient_id in data["patients"]:
        data["patients"][patient_id]["last_report"] = datetime.now().isoformat()
        data["patients"][patient_id]["total_reports"] = len([r for r in data["reports"] if r["patient_id"] == patient_id])
    
    # 檢查是否需要產生警示
    overall_score = report.get("overall_score", 0)
    if overall_score >= 7:
        alert = create_alert(patient_id, "red", report)
        data["alerts"].append(alert)
    elif overall_score >= 4:
        alert = create_alert(patient_id, "yellow", report)
        data["alerts"].append(alert)
    
    save_data(data)
    return report_record

def create_alert(patient_id: str, level: str, report: Dict) -> Dict:
    """建立警示"""
    data = load_data()
    patient = data["patients"].get(patient_id, {})
    
    return {
        "id": str(uuid.uuid4())[:8],
        "patient_id": patient_id,
        "patient_name": patient.get("name", "未知"),
        "level": level,
        "score": report.get("overall_score", 0),
        "symptoms": report.get("symptoms", []),
        "timestamp": datetime.now().isoformat(),
        "time_display": datetime.now().strftime("%H:%M"),
        "status": "pending",  # pending, contacted, resolved
        "handled_by": None,
        "handled_at": None,
        "notes": ""
    }

def get_patient_reports(patient_id: str, limit: int = 10) -> List[Dict]:
    """取得病人的回報記錄"""
    data = load_data()
    reports = [r for r in data["reports"] if r["patient_id"] == patient_id]
    reports.sort(key=lambda x: x["timestamp"], reverse=True)
    return reports[:limit]

def get_all_patients() -> List[Dict]:
    """取得所有病人"""
    data = load_data()
    patients = list(data["patients"].values())
    
    # 計算每個病人的狀態
    for patient in patients:
        patient_reports = [r for r in data["reports"] if r["patient_id"] == patient["id"]]
        if patient_reports:
            latest = max(patient_reports, key=lambda x: x["timestamp"])
            patient["last_score"] = latest.get("overall_score", 0)
            patient["last_symptoms"] = latest.get("symptoms", [])
            patient["last_report_time"] = latest.get("time", "")
            
            # 判斷狀態
            if latest["overall_score"] >= 7:
                patient["status"] = "alert"
            elif latest["overall_score"] >= 4:
                patient["status"] = "warning"
            else:
                patient["status"] = "normal"
        else:
            patient["status"] = "no_report"
            patient["last_score"] = None
    
    return patients

def get_pending_alerts() -> List[Dict]:
    """取得待處理的警示"""
    data = load_data()
    alerts = [a for a in data["alerts"] if a["status"] == "pending"]
    alerts.sort(key=lambda x: (x["level"] == "red", x["timestamp"]), reverse=True)
    return alerts

def get_all_alerts(limit: int = 50) -> List[Dict]:
    """取得所有警示"""
    data = load_data()
    alerts = data["alerts"]
    alerts.sort(key=lambda x: x["timestamp"], reverse=True)
    return alerts[:limit]

def update_alert_status(alert_id: str, status: str, handled_by: str = None, notes: str = ""):
    """更新警示狀態"""
    data = load_data()
    for alert in data["alerts"]:
        if alert["id"] == alert_id:
            alert["status"] = status
            alert["handled_by"] = handled_by
            alert["handled_at"] = datetime.now().isoformat()
            alert["notes"] = notes
            break
    save_data(data)

def save_intervention(patient_id: str, intervention: Dict):
    """儲存介入紀錄"""
    data = load_data()
    
    record = {
        "id": str(uuid.uuid4())[:8],
        "patient_id": patient_id,
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "type": intervention.get("type", "電話"),
        "content": intervention.get("content", ""),
        "duration": intervention.get("duration", ""),
        "referral": intervention.get("referral"),
        "nurse": intervention.get("nurse", "")
    }
    
    data["interventions"].append(record)
    save_data(data)
    return record

def get_interventions(patient_id: str = None, limit: int = 20) -> List[Dict]:
    """取得介入紀錄"""
    data = load_data()
    
    if patient_id:
        interventions = [i for i in data["interventions"] if i["patient_id"] == patient_id]
    else:
        interventions = data["interventions"]
    
    interventions.sort(key=lambda x: x["timestamp"], reverse=True)
    return interventions[:limit]

def get_statistics() -> Dict:
    """取得統計資料"""
    data = load_data()
    
    total_patients = len(data["patients"])
    total_reports = len(data["reports"])
    
    # 今日統計
    today = datetime.now().strftime("%Y-%m-%d")
    today_reports = [r for r in data["reports"] if r["date"] == today]
    today_alerts = [a for a in data["alerts"] if a["timestamp"].startswith(today)]
    
    # 警示統計
    pending_alerts = len([a for a in data["alerts"] if a["status"] == "pending"])
    red_alerts = len([a for a in data["alerts"] if a["status"] == "pending" and a["level"] == "red"])
    yellow_alerts = len([a for a in data["alerts"] if a["status"] == "pending" and a["level"] == "yellow"])
    
    return {
        "total_patients": total_patients,
        "total_reports": total_reports,
        "today_reports": len(today_reports),
        "today_alerts": len(today_alerts),
        "pending_alerts": pending_alerts,
        "red_alerts": red_alerts,
        "yellow_alerts": yellow_alerts
    }
