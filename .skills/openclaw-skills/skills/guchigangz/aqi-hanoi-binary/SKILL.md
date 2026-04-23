---
name: "aqi-hanoi-binary"
version: "1.0.0"
description: "Tra cứu chỉ số chất lượng không khí (AQI) theo thời gian thực cho các thành phố Việt Nam. Trả về AQI, nhiệt độ, độ ẩm, tốc độ gió và timestamp dưới dạng JSON."
tags: ["aqi", "air-quality", "weather", "vietnam", "hanoi", "environment", "real-time"]
homepage: "https://github.com/picoclaw-skill/aqi-hanoi"
user-invocable: true
disable-model-invocation: false
---

# AQI Vietnam Skill

Skill này cho phép tra cứu **chỉ số chất lượng không khí (AQI)** theo thời gian thực từ mạng lưới trạm đo toàn cầu [WAQI](https://waqi.info/), tập trung vào các thành phố lớn của Việt Nam.

## Khi nào dùng skill này

Sử dụng skill này khi người dùng hỏi về:
- Chất lượng không khí tại một thành phố Việt Nam
- Chỉ số AQI, mức độ ô nhiễm không khí
- Nhiệt độ, độ ẩm, tốc độ gió hiện tại
- Có nên ra ngoài không, không khí có an toàn không
- Tình trạng môi trường, bụi mịn PM2.5

Ví dụ câu hỏi kích hoạt skill:
- "Hôm nay không khí Hà Nội thế nào?"
- "AQI TP. Hồ Chí Minh bao nhiêu?"
- "Đà Nẵng có bụi không?"
- "Không khí Hải Phòng có tốt không?"

## Cách chạy

```bash
{baseDir}/aqi-hanoi <tên thành phố>
```

**Ví dụ:**
```bash
{baseDir}/aqi-hanoi hanoi
{baseDir}/aqi-hanoi "ho chi minh"
{baseDir}/aqi-hanoi danang
{baseDir}/aqi-hanoi haiphong
{baseDir}/aqi-hanoi cantho
```

> **Lưu ý:** Tên thành phố không phân biệt hoa/thường. Nếu không truyền tham số, mặc định là `hanoi`.

## Output

Skill trả về một JSON object với cấu trúc:

```json
{
  "status": "success",
  "city": "Hà Nội",
  "location": "United Nations International School of Hanoi, Vietnam",
  "geo": [21.021, 105.8412],
  "aqi": 87,
  "temperature": 28,
  "humidity": 72.5,
  "wind": 1.2,
  "timestamp": "2024-04-09 11:00:00"
}
```

| Field | Kiểu | Mô tả |
|---|---|---|
| `status` | string | `"success"` hoặc `"error"` |
| `city` | string | Tên thành phố chuẩn hóa tiếng Việt |
| `location` | string | Tên trạm đo cụ thể |
| `geo` | array | Tọa độ [lat, lon] của trạm đo |
| `aqi` | int | Chỉ số AQI (0–500+) |
| `temperature` | int | Nhiệt độ (°C) |
| `humidity` | float | Độ ẩm (%) |
| `wind` | float | Tốc độ gió (m/s) |
| `timestamp` | string | Thời điểm đo gần nhất |

## Bảng phân loại AQI

| AQI | Mức độ | Màu | Ý nghĩa |
|---|---|---|---|
| 0–50 | Tốt | 🟢 | Không khí trong lành |
| 51–100 | Trung bình | 🟡 | Chấp nhận được, nhóm nhạy cảm nên hạn chế |
| 101–150 | Không tốt cho nhóm nhạy cảm | 🟠 | Trẻ em, người già, người bệnh nên ở trong nhà |
| 151–200 | Không tốt | 🔴 | Mọi người nên hạn chế ra ngoài |
| 201–300 | Rất xấu | 🟣 | Tránh mọi hoạt động ngoài trời |
| 300+ | Nguy hiểm | 🟤 | Ở trong nhà, đóng cửa sổ |

## Cách diễn giải kết quả cho người dùng

Sau khi nhận JSON output, hãy:

1. Dùng bảng AQI ở trên để xác định mức độ và màu sắc tương ứng
2. Trình bày kết quả thân thiện, bao gồm: tên thành phố, AQI, mức độ, nhiệt độ, độ ẩm
3. Đưa ra **khuyến nghị hành động** phù hợp với mức AQI
4. Nếu `status` là `"error"`, thông báo không thể lấy dữ liệu và đề nghị thử lại

**Ví dụ phản hồi tốt:**
> 🌿 **Hà Nội** — AQI: **87** (🟡 Trung bình)
> 🌡️ Nhiệt độ: 28°C | 💧 Độ ẩm: 72% | 💨 Gió: 1.2 m/s
> ⚠️ Nhóm nhạy cảm (trẻ em, người cao tuổi, người bệnh hô hấp) nên hạn chế hoạt động ngoài trời kéo dài.

## Thành phố được hỗ trợ

- `hanoi` / `hà nội`
- `ho chi minh` / `hochiminh`
- `danang` / `da nang` / `đà nẵng`
- `haiphong` / `hai phong` / `hải phòng`
- `cantho` / `can tho` / `cần thơ`
- Bất kỳ thành phố nào có trong cơ sở dữ liệu WAQI (tên tiếng Anh)