"""
AI-CARE Lung - 衛教推送系統
============================

包含：
1. 衛教單張庫
2. 自動推送規則
3. 手動推送介面
4. 推送紀錄追蹤
"""

from datetime import datetime, timedelta
import json

# ============================================
# 衛教單張庫
# ============================================
EDUCATION_MATERIALS = {
    # === 術後基礎照護 ===
    "POST_OP_CARE": {
        "id": "EDU001",
        "category": "術後照護",
        "title": "肺癌術後基礎照護指南",
        "description": "傷口照護、活動注意事項、飲食建議",
        "content": """
## 🏥 肺癌術後基礎照護指南

### 傷口照護
- 保持傷口乾燥清潔
- 觀察傷口有無紅腫、滲液、異味
- 依醫囑時間回診拆線

### 活動建議
- 術後早期下床活動，促進恢復
- 避免提重物（< 5公斤）至少 4-6 週
- 循序漸進增加活動量

### 飲食建議
- 均衡飲食，高蛋白質促進癒合
- 多攝取蔬果，預防便秘
- 少量多餐，避免脹氣

### ⚠️ 警示徵象
如有以下情況，請立即就醫：
- 發燒 > 38°C
- 傷口紅腫化膿
- 呼吸困難加劇
- 胸痛劇烈
        """,
        "icon": "🏥",
        "priority": 1
    },
    
    "BREATHING_EXERCISE": {
        "id": "EDU002",
        "category": "呼吸訓練",
        "title": "呼吸運動訓練指南",
        "description": "深呼吸、噘嘴式呼吸、腹式呼吸練習",
        "content": """
## 🌬️ 呼吸運動訓練指南

### 為什麼要做呼吸運動？
- 預防肺部塌陷
- 促進痰液排出
- 加速肺功能恢復

### 深呼吸練習
1. 坐直或半躺姿勢
2. 用鼻子慢慢吸氣 4 秒
3. 憋氣 2 秒
4. 用嘴巴慢慢吐氣 6 秒
5. 每小時練習 10 次

### 噘嘴式呼吸
1. 用鼻子吸氣
2. 嘴唇噘起像吹蠟燭
3. 慢慢吐氣，時間是吸氣的 2 倍
4. 感覺呼吸困難時使用

### 誘發性肺量計 (Triflow)
1. 坐直，正常呼氣
2. 含住吸嘴，慢慢深吸氣
3. 盡量讓球升高並維持
4. 每小時練習 10 次

### 📅 建議頻率
- 每小時至少練習一次
- 每次 5-10 分鐘
        """,
        "icon": "🌬️",
        "priority": 1
    },
    
    "PAIN_MANAGEMENT": {
        "id": "EDU003",
        "category": "疼痛控制",
        "title": "術後疼痛控制指南",
        "description": "疼痛評估、用藥指導、非藥物緩解",
        "content": """
## 💊 術後疼痛控制指南

### 疼痛評估
請用 0-10 分評估您的疼痛：
- 0 分：完全不痛
- 1-3 分：輕微疼痛
- 4-6 分：中度疼痛
- 7-10 分：嚴重疼痛

### 用藥原則
- 按時服藥，不要等痛了才吃
- 依醫囑使用止痛藥
- 記錄用藥時間和效果

### 非藥物緩解
- 冰敷（術後 48 小時內）
- 姿勢調整（側躺時用枕頭支撐）
- 放鬆技巧（深呼吸、冥想）
- 分散注意力（聽音樂、看書）

### 咳嗽時減痛技巧
1. 雙手或枕頭輕壓傷口
2. 先深吸一口氣
3. 用力咳出
4. 這樣可以減少咳嗽時的疼痛

### ⚠️ 何時該告知醫護人員
- 疼痛分數持續 > 6 分
- 止痛藥效果不佳
- 出現新的疼痛部位
        """,
        "icon": "💊",
        "priority": 2
    },
    
    "EARLY_AMBULATION": {
        "id": "EDU004",
        "category": "活動指導",
        "title": "術後早期下床活動指南",
        "description": "下床步驟、活動量建議、注意事項",
        "content": """
## 🚶 術後早期下床活動指南

### 為什麼要早期下床？
- 預防肺栓塞
- 促進腸胃蠕動
- 加速整體恢復
- 預防肌肉萎縮

### 下床步驟
1. 先在床上坐起，停留 1-2 分鐘
2. 雙腳放到床邊，再停留 1-2 分鐘
3. 確認無頭暈後，扶著站起
4. 站穩後，慢慢行走

### 活動量建議
| 術後天數 | 建議活動 |
|---------|---------|
| D+1 | 床邊坐起、站立 |
| D+2 | 病房內行走 |
| D+3 | 走廊行走 2-3 次 |
| D+4起 | 逐漸增加距離 |

### ⚠️ 注意事項
- 有人陪伴
- 穿防滑鞋
- 攜帶引流管時小心
- 感覺頭暈立即坐下
        """,
        "icon": "🚶",
        "priority": 1
    },
    
    "WOUND_CARE": {
        "id": "EDU005",
        "category": "傷口照護",
        "title": "傷口照護指南",
        "description": "傷口觀察、換藥、沐浴注意事項",
        "content": """
## 🩹 傷口照護指南

### 傷口觀察重點
每天觀察傷口，注意：
- ✅ 正常：輕微發紅、輕微腫脹
- ⚠️ 異常：明顯紅腫、滲液、異味、裂開

### 換藥原則
- 依醫囑時間換藥
- 換藥前洗手
- 使用無菌敷料
- 由內向外清潔

### 沐浴注意
- 傷口未癒合前避免泡澡
- 可使用防水敷料淋浴
- 沐浴後保持傷口乾燥
- 拆線後 3 天可正常沐浴

### 胸管傷口
- 拔管後傷口較小
- 保持乾燥 3-5 天
- 觀察有無滲液或氣腫

### ⚠️ 立即就醫情況
- 傷口裂開
- 大量滲液或出血
- 傷口周圍紅腫熱痛擴大
- 發燒 > 38°C
        """,
        "icon": "🩹",
        "priority": 2
    },
    
    "HOME_CARE": {
        "id": "EDU006",
        "category": "居家照護",
        "title": "出院居家照護指南",
        "description": "居家注意事項、生活調整、回診提醒",
        "content": """
## 🏠 出院居家照護指南

### 居家環境準備
- 床鋪高度適中，方便起身
- 浴室加裝防滑墊、扶手
- 常用物品放在容易取得處
- 保持室內空氣流通

### 日常生活
| 活動 | 建議 |
|-----|-----|
| 睡眠 | 側躺或半坐臥較舒適 |
| 進食 | 少量多餐、細嚼慢嚥 |
| 沐浴 | 淋浴為主、避免過熱 |
| 穿衣 | 選擇前開式衣物 |

### 活動限制（4-6週內）
- ❌ 提重物 > 5 公斤
- ❌ 劇烈運動
- ❌ 開車（視恢復狀況）
- ✅ 散步、輕度家務

### 營養建議
- 高蛋白：魚、肉、蛋、豆類
- 維生素 C：促進傷口癒合
- 足夠水分：每日 1500-2000ml
- 高纖維：預防便秘

### 📅 回診時間
- 術後 1-2 週：拆線、看病理報告
- 術後 1 個月：恢復評估
- 術後 3 個月：追蹤 CT
        """,
        "icon": "🏠",
        "priority": 1
    },
    
    "WARNING_SIGNS": {
        "id": "EDU007",
        "category": "警示徵象",
        "title": "術後警示徵象",
        "description": "需要立即就醫的危險徵象",
        "content": """
## 🚨 術後警示徵象

### 🔴 立即急診（撥打 119）
- 突然嚴重呼吸困難
- 胸痛劇烈、冒冷汗
- 意識改變、昏倒
- 咳血（鮮紅色、量多）
- 嘴唇發紫

### 🟡 盡快回診（24小時內）
- 發燒 > 38°C
- 傷口紅腫、滲液增加
- 呼吸困難加重
- 持續胸痛不緩解
- 痰液變黃綠色

### 🟢 下次回診時告知
- 輕微咳嗽
- 傷口輕微不適
- 疲倦感
- 食慾稍差

### 📞 緊急聯繫方式
- 醫院急診：(02) XXXX-XXXX
- 個管師專線：(02) XXXX-XXXX
- 值班時間：週一至週五 08:00-17:00
        """,
        "icon": "🚨",
        "priority": 1
    },
    
    "NUTRITION": {
        "id": "EDU008",
        "category": "營養指導",
        "title": "術後營養指南",
        "description": "促進恢復的飲食建議",
        "content": """
## 🍎 術後營養指南

### 營養目標
- 促進傷口癒合
- 維持免疫力
- 恢復體力

### 蛋白質攝取
每日需要量：體重 x 1.2-1.5 g
- 魚類：鮭魚、鱈魚
- 肉類：雞胸肉、瘦肉
- 蛋類：每日 1-2 顆
- 豆類：豆腐、豆漿

### 促進癒合的營養素
| 營養素 | 食物來源 |
|-------|---------|
| 維生素 C | 芭樂、柑橘、奇異果 |
| 維生素 A | 紅蘿蔔、地瓜、南瓜 |
| 鋅 | 牡蠣、堅果、全穀 |
| 鐵 | 紅肉、深綠蔬菜 |

### 飲食原則
- 少量多餐（每日 5-6 餐）
- 細嚼慢嚥
- 避免脹氣食物
- 足夠水分

### ⚠️ 術後避免
- 過於油膩食物
- 辛辣刺激
- 酒精
- 未經醫囑的保健食品
        """,
        "icon": "🍎",
        "priority": 2
    },
    
    "SMOKING_CESSATION": {
        "id": "EDU009",
        "category": "戒菸衛教",
        "title": "戒菸指南",
        "description": "戒菸的重要性與方法",
        "content": """
## 🚭 戒菸指南

### 為什麼術後要戒菸？
- 促進傷口癒合
- 降低併發症風險
- 改善肺功能恢復
- 降低癌症復發風險

### 戒菸的好處（時間軸）
| 時間 | 身體變化 |
|-----|---------|
| 20 分鐘 | 心跳血壓恢復正常 |
| 24 小時 | 血液含氧量增加 |
| 2 週 | 肺功能開始改善 |
| 1 個月 | 咳嗽減少、體力改善 |
| 1 年 | 心臟病風險降低一半 |

### 戒菸方法
1. **藥物輔助**
   - 尼古丁替代療法（貼片、口香糖）
   - 戒菸藥物（需醫師處方）

2. **行為改變**
   - 找出吸菸誘因並避免
   - 用其他活動取代吸菸
   - 告知親友尋求支持

3. **專業協助**
   - 戒菸門診
   - 戒菸專線：0800-636363

### 戒斷症狀處理
- 焦慮：深呼吸、運動
- 想吸菸：喝水、嚼口香糖
- 失眠：減少咖啡因、規律作息
        """,
        "icon": "🚭",
        "priority": 2
    },
    
    "FOLLOW_UP": {
        "id": "EDU010",
        "category": "追蹤檢查",
        "title": "術後追蹤檢查指南",
        "description": "追蹤時程與檢查項目說明",
        "content": """
## 📋 術後追蹤檢查指南

### 追蹤時程
| 時間 | 檢查項目 |
|-----|---------|
| 術後 1-2 週 | 回診、拆線、病理報告 |
| 術後 1 個月 | 恢復評估、胸部 X 光 |
| 術後 3 個月 | 胸部 CT |
| 術後 6 個月 | 胸部 CT |
| 術後 1 年 | 胸部 CT、抽血 |
| 之後每年 | 低劑量 CT |

### 病理報告說明
術後約 1-2 週可得知：
- 腫瘤類型
- 分期（pTNM）
- 切緣狀態
- 是否需要輔助治療

### 追蹤檢查的目的
- 確認恢復狀況
- 早期發現復發
- 評估治療效果
- 處理術後問題

### 📅 回診準備
- 攜帶健保卡、病歷
- 記錄要詢問的問題
- 攜帶用藥清單
- 有症狀變化請告知
        """,
        "icon": "📋",
        "priority": 2
    },
    
    "ADJUVANT_CHEMO": {
        "id": "EDU011",
        "category": "輔助治療",
        "title": "術後輔助化學治療說明",
        "description": "化療目的、流程、副作用處理",
        "content": """
## 💉 術後輔助化學治療說明

### 什麼情況需要化療？
- 病理分期 II 期以上
- 有淋巴結轉移
- 高風險因子（LVI、VPI等）

### 化療時程
- 通常術後 4-8 週開始
- 每 3 週一次
- 共 4 次療程

### 常見副作用與處理
| 副作用 | 處理方式 |
|-------|---------|
| 噁心嘔吐 | 止吐藥、少量多餐 |
| 疲倦 | 適度休息、輕度活動 |
| 白血球下降 | 避免感染、監測體溫 |
| 掉髮 | 暫時性、會恢復 |
| 手腳麻 | 告知醫師調整 |

### ⚠️ 化療期間注意
- 避免生食
- 勤洗手
- 避免人多擁擠處
- 發燒立即就醫
        """,
        "icon": "💉",
        "priority": 3
    },
    
    "TARGETED_THERAPY": {
        "id": "EDU012",
        "category": "輔助治療",
        "title": "標靶治療說明",
        "description": "EGFR-TKI 標靶藥物使用指南",
        "content": """
## 🎯 標靶治療說明

### 什麼是標靶治療？
針對癌細胞特定基因突變的藥物治療
- EGFR 突變：可用 EGFR-TKI
- ALK 重組：可用 ALK 抑制劑

### 術後標靶治療
- 適用於 EGFR 突變陽性
- 通常服用 3 年
- 每日口服

### 常見副作用
| 副作用 | 發生率 | 處理 |
|-------|-------|-----|
| 皮疹 | 常見 | 保濕、防曬 |
| 腹瀉 | 常見 | 止瀉藥、補水 |
| 肝功能異常 | 需監測 | 定期抽血 |
| 間質性肺炎 | 少見但嚴重 | 立即就醫 |

### 服藥注意
- 固定時間服用
- 不可自行停藥
- 定期回診追蹤
- 記錄副作用
        """,
        "icon": "🎯",
        "priority": 3
    },
    
    "EMOTIONAL_SUPPORT": {
        "id": "EDU013",
        "category": "心理支持",
        "title": "術後心理調適指南",
        "description": "情緒處理、心理支持資源",
        "content": """
## 💚 術後心理調適指南

### 常見情緒反應
術後有這些感受是正常的：
- 焦慮、擔心復發
- 情緒低落、悲傷
- 疲倦、缺乏動力
- 對未來感到不確定

### 調適方法
1. **接受情緒**
   - 允許自己有負面情緒
   - 不要壓抑感受

2. **表達分享**
   - 與家人朋友傾訴
   - 加入病友團體
   - 尋求專業諮商

3. **自我照顧**
   - 維持規律作息
   - 適度運動
   - 做喜歡的事情

4. **正念練習**
   - 專注當下
   - 深呼吸放鬆
   - 冥想

### 🆘 需要幫助的訊號
- 持續 2 週以上情緒低落
- 失眠或嗜睡
- 食慾明顯改變
- 對事物失去興趣
- 有自我傷害念頭

### 📞 心理支持資源
- 社工師諮詢
- 心理諮商門診
- 癌症關懷專線：0800-123-456
        """,
        "icon": "💚",
        "priority": 2
    },
    
    "PHYSICAL_ACTIVITY": {
        "id": "EDU014",
        "category": "復健運動",
        "title": "術後運動指南",
        "description": "漸進式運動建議",
        "content": """
## 🏃 術後運動指南

### 運動的好處
- 加速體力恢復
- 改善肺功能
- 減少疲倦感
- 改善心情

### 漸進式運動計畫
| 階段 | 時間 | 運動類型 |
|-----|-----|---------|
| 第 1-2 週 | 住院期 | 床邊活動、走廊行走 |
| 第 3-4 週 | 出院後 | 室內走動、輕度伸展 |
| 第 5-8 週 | 恢復期 | 戶外散步 15-30 分鐘 |
| 第 9-12 週 | 進階期 | 快走、輕度有氧 |
| 3 個月後 | 維持期 | 規律運動 30 分鐘/天 |

### 上肢運動（預防肩膀僵硬）
1. 手臂前舉、側舉
2. 肩膀繞圈
3. 爬牆運動
4. 每日 2-3 次，每次 10 分鐘

### ⚠️ 運動注意事項
- 循序漸進，不要勉強
- 感覺不適就休息
- 避免憋氣用力
- 避免劇烈碰撞運動
        """,
        "icon": "🏃",
        "priority": 2
    },
    
    "SLEEP_GUIDE": {
        "id": "EDU015",
        "category": "生活照護",
        "title": "術後睡眠指南",
        "description": "改善睡眠品質的方法",
        "content": """
## 😴 術後睡眠指南

### 術後睡眠困難的原因
- 傷口疼痛
- 姿勢不適
- 焦慮擔憂
- 環境改變

### 舒適睡姿
- **側躺**：患側朝上，用枕頭支撐
- **半坐臥**：床頭抬高 30-45 度
- **仰躺**：膝下墊枕頭

### 改善睡眠的方法
1. **睡前準備**
   - 固定就寢時間
   - 睡前 1 小時避免螢幕
   - 放鬆活動（閱讀、音樂）

2. **環境調整**
   - 保持安靜、黑暗
   - 適宜溫度（24-26°C）
   - 舒適的床鋪

3. **白天習慣**
   - 避免午睡過長（< 30分鐘）
   - 適度活動
   - 減少咖啡因

### 疼痛影響睡眠時
- 睡前服用止痛藥
- 使用冰敷或熱敷
- 調整睡姿
        """,
        "icon": "😴",
        "priority": 3
    }
}

# ============================================
# 自動推送規則
# ============================================
AUTO_PUSH_RULES = [
    # 依術後天數推送
    {
        "id": "RULE001",
        "name": "術後第 1 天",
        "trigger_type": "post_op_day",
        "trigger_value": 1,
        "materials": ["BREATHING_EXERCISE", "EARLY_AMBULATION", "PAIN_MANAGEMENT"],
        "enabled": True
    },
    {
        "id": "RULE002",
        "name": "術後第 2 天",
        "trigger_type": "post_op_day",
        "trigger_value": 2,
        "materials": ["WOUND_CARE", "NUTRITION"],
        "enabled": True
    },
    {
        "id": "RULE003",
        "name": "術後第 3 天",
        "trigger_type": "post_op_day",
        "trigger_value": 3,
        "materials": ["POST_OP_CARE"],
        "enabled": True
    },
    {
        "id": "RULE004",
        "name": "出院前（術後第 5 天）",
        "trigger_type": "post_op_day",
        "trigger_value": 5,
        "materials": ["HOME_CARE", "WARNING_SIGNS"],
        "enabled": True
    },
    {
        "id": "RULE005",
        "name": "術後第 7 天",
        "trigger_type": "post_op_day",
        "trigger_value": 7,
        "materials": ["PHYSICAL_ACTIVITY", "EMOTIONAL_SUPPORT"],
        "enabled": True
    },
    {
        "id": "RULE006",
        "name": "術後第 14 天",
        "trigger_type": "post_op_day",
        "trigger_value": 14,
        "materials": ["FOLLOW_UP"],
        "enabled": True
    },
    {
        "id": "RULE007",
        "name": "術後第 30 天",
        "trigger_type": "post_op_day",
        "trigger_value": 30,
        "materials": ["SMOKING_CESSATION"],
        "enabled": True
    },
    
    # 依症狀觸發
    {
        "id": "RULE101",
        "name": "呼吸困難症狀",
        "trigger_type": "symptom",
        "trigger_value": "呼吸困難",
        "materials": ["BREATHING_EXERCISE", "WARNING_SIGNS"],
        "enabled": True
    },
    {
        "id": "RULE102",
        "name": "疼痛症狀",
        "trigger_type": "symptom",
        "trigger_value": "疼痛",
        "materials": ["PAIN_MANAGEMENT"],
        "enabled": True
    },
    {
        "id": "RULE103",
        "name": "睡眠問題",
        "trigger_type": "symptom",
        "trigger_value": "睡眠",
        "materials": ["SLEEP_GUIDE"],
        "enabled": True
    },
    {
        "id": "RULE104",
        "name": "情緒困擾",
        "trigger_type": "symptom",
        "trigger_value": "焦慮",
        "materials": ["EMOTIONAL_SUPPORT"],
        "enabled": True
    },
    {
        "id": "RULE105",
        "name": "傷口問題",
        "trigger_type": "symptom",
        "trigger_value": "傷口",
        "materials": ["WOUND_CARE", "WARNING_SIGNS"],
        "enabled": True
    },
    
    # 依治療計畫觸發
    {
        "id": "RULE201",
        "name": "開始化療",
        "trigger_type": "treatment",
        "trigger_value": "chemotherapy",
        "materials": ["ADJUVANT_CHEMO"],
        "enabled": True
    },
    {
        "id": "RULE202",
        "name": "開始標靶治療",
        "trigger_type": "treatment",
        "trigger_value": "targeted",
        "materials": ["TARGETED_THERAPY"],
        "enabled": True
    }
]

# ============================================
# 推送紀錄管理
# ============================================
class EducationPushManager:
    def __init__(self):
        self.push_history = []
    
    def push_material(self, patient_id, patient_name, material_id, push_type="manual", pushed_by="system"):
        """推送衛教單張"""
        material = EDUCATION_MATERIALS.get(material_id)
        if not material:
            return None
        
        record = {
            "id": f"PUSH{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "patient_id": patient_id,
            "patient_name": patient_name,
            "material_id": material_id,
            "material_title": material["title"],
            "category": material["category"],
            "push_type": push_type,  # manual, auto
            "pushed_by": pushed_by,
            "pushed_at": datetime.now().isoformat(),
            "read_at": None,
            "status": "sent"  # sent, read
        }
        
        self.push_history.append(record)
        return record
    
    def get_patient_history(self, patient_id):
        """取得病人的推送紀錄"""
        return [r for r in self.push_history if r["patient_id"] == patient_id]
    
    def get_all_history(self):
        """取得所有推送紀錄"""
        return sorted(self.push_history, key=lambda x: x["pushed_at"], reverse=True)
    
    def mark_as_read(self, push_id):
        """標記為已讀"""
        for record in self.push_history:
            if record["id"] == push_id:
                record["read_at"] = datetime.now().isoformat()
                record["status"] = "read"
                return True
        return False
    
    def check_auto_push(self, patient_id, patient_name, post_op_day, symptoms=None, treatment=None):
        """檢查並執行自動推送"""
        pushed = []
        
        for rule in AUTO_PUSH_RULES:
            if not rule["enabled"]:
                continue
            
            should_push = False
            
            # 術後天數觸發
            if rule["trigger_type"] == "post_op_day":
                if post_op_day == rule["trigger_value"]:
                    should_push = True
            
            # 症狀觸發
            elif rule["trigger_type"] == "symptom" and symptoms:
                for symptom in symptoms:
                    if rule["trigger_value"] in symptom:
                        should_push = True
                        break
            
            # 治療觸發
            elif rule["trigger_type"] == "treatment" and treatment:
                if rule["trigger_value"] in treatment.lower():
                    should_push = True
            
            if should_push:
                for material_id in rule["materials"]:
                    # 檢查是否已推送過
                    already_pushed = any(
                        r["patient_id"] == patient_id and 
                        r["material_id"] == material_id and
                        r["push_type"] == "auto"
                        for r in self.push_history
                    )
                    
                    if not already_pushed:
                        record = self.push_material(
                            patient_id, patient_name, material_id,
                            push_type="auto", pushed_by="system"
                        )
                        if record:
                            pushed.append(record)
        
        return pushed

# 全域實例
education_manager = EducationPushManager()

# ============================================
# 輔助函數
# ============================================
def get_materials_by_category():
    """依類別分組衛教單張"""
    categories = {}
    for key, material in EDUCATION_MATERIALS.items():
        cat = material["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({"key": key, **material})
    return categories

def get_material_by_id(material_id):
    """根據 ID 取得衛教單張"""
    return EDUCATION_MATERIALS.get(material_id)
