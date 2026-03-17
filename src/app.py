from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import oracledb
import numpy as np

app = FastAPI(title="MES AI API")


# -----------------------------
# 1. 요청 바디 모델
# -----------------------------
class AnalyzeRequest(BaseModel):
    equip_id: int
    item_id: int
    insp_item_id: int
    op_id : int
    lot_no: str | None = None
    current_value: float
    usl: float
    lsl: float


# -----------------------------
# 2. Oracle 연결 함수
# -----------------------------
def get_connection():
    conn = oracledb.connect(
        user="APPS",
        password="infoflex",
        host="infosolution.iptime.org",
        port=1521,
        service_name="NFV_INFO"   # 실제 서비스명으로 수정
    )
    return conn


# -----------------------------
# 3. 최근 이력 조회
# -----------------------------
def get_recent_values(equip_id: int, item_id: int, insp_item_id: int,op_id:int, limit_count: int = 5):
    sql = """
        SELECT RESULT_1
        FROM (
            SELECT RESULT_1, INSPECTION_DATE
            FROM MVIEW_TOTAL_INSPECTION
            WHERE EQUIPMENT_ID = :equip_id
              AND INVENTORY_ITEM_ID = :item_id
              AND INSPECTION_ITEM_ID = :insp_item_id
              AND OPERATION_ID = :op_id
              AND RESULT_1 IS NOT NULL
            ORDER BY INSPECTION_DATE DESC
        )
        WHERE ROWNUM <= :limit_count
    """

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            sql,
            equip_id=equip_id,
            item_id=item_id,
            insp_item_id=insp_item_id,
            op_id=op_id,
            limit_count=limit_count
        )
        rows = cur.fetchall()
        values = [float(r[0]) for r in rows]
        values.reverse()
        return values
    finally:
        conn.close()


# -----------------------------
# 4. 서버 상태 확인용
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# -----------------------------
# 5. 분석 API
# -----------------------------
@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    try:
        if req.usl <= req.lsl:
            raise HTTPException(status_code=400, detail="USL must be greater than LSL")

        recent_values = get_recent_values(
            equip_id=req.equip_id,
            item_id=req.item_id,
            insp_item_id=req.insp_item_id,
            op_id=req.op_id,
            limit_count=5
        )

        center = (req.usl + req.lsl) / 2.0
        spec_range = req.usl - req.lsl

        deviation = req.current_value - center
        abs_deviation = abs(deviation)
        normalized_position = (req.current_value - req.lsl) / spec_range

        if len(recent_values) >= 1:
            rolling_mean = float(np.mean(recent_values))
        else:
            rolling_mean = None

        if len(recent_values) >= 2:
            rolling_std = float(np.std(recent_values, ddof=1))
        else:
            rolling_std = 0.0

        gap_from_mean = req.current_value - rolling_mean if rolling_mean is not None else None

        if rolling_mean is not None and rolling_std > 0:
            zscore = gap_from_mean / rolling_std
        else:
            zscore = 0.0

        out_of_spec = (req.current_value < req.lsl) or (req.current_value > req.usl)

        anomaly_score = (
            abs_deviation * 0.3
            + (abs(gap_from_mean) if gap_from_mean is not None else 0.0) * 0.4
            + abs(zscore) * 0.3
        )

        if out_of_spec:
            alarm_level = "ALARM"
        elif anomaly_score >= 2.0:
            alarm_level = "WARN"
        else:
            alarm_level = "NORMAL"

        reasons = []
        if out_of_spec:
            reasons.append("규격이탈")
        if normalized_position >= 0.9:
            reasons.append("USL근접")
        elif normalized_position <= 0.1:
            reasons.append("LSL근접")
        if abs(zscore) >= 2:
            reasons.append("최근평균대비급변")
        if not reasons:
            reasons.append("정상범위")

        return {
            "equip_id": req.equip_id,
            "item_id": req.item_id,
            "insp_item_id": req.insp_item_id,
            "op_id":req.op_id,
            "lot_no": req.lot_no,
            "recent_values": recent_values,
            "center": round(center, 4),
            "deviation": round(deviation, 4),
            "abs_deviation": round(abs_deviation, 4),
            "normalized_position": round(normalized_position, 4),
            "rolling_mean": round(rolling_mean, 4) if rolling_mean is not None else None,
            "rolling_std": round(rolling_std, 4),
            "gap_from_mean": round(gap_from_mean, 4) if gap_from_mean is not None else None,
            "zscore": round(zscore, 4),
            "out_of_spec": out_of_spec,
            "anomaly_score": round(anomaly_score, 4),
            "alarm_level": alarm_level,
            "main_reason": ",".join(reasons)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))