package main

import (
	"aqi-hanoi/configs"
	"aqi-hanoi/scripts"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

// TIP <p>To run your code, right-click the code and select <b>Run</b>.</p> <p>Alternatively, click
// the <icon src="AllIcons.Actions.Execute"/> icon in the gutter and select the <b>Run</b> menu item from here.</p>
func main() {
	config, err := configs.NewConfig()
	if err != nil {
		printErrorJSON(err.Error())
		os.Exit(1)
	}
	if len(os.Args) < 2 {
		printErrorJSON("thiếu tham số tên thành phố")
		os.Exit(1)
	}
	city := strings.Join(os.Args[1:], " ")
	if city == "" {
		city = "hanoi"
	}
	response, err := fetchAQI(city, config)
	if err != nil {
		printErrorJSON(err.Error())
		os.Exit(1)
	}

	aqi := response.Data.AQI
	output := scripts.OutputJSON{
		Status:            "success",
		City:              extractCityName(response.Data.City.Name),
		Location:          response.Data.City.Name,
		Geo:               response.Data.City.Geo,
		AQI:               aqi,
		Category:          aqiCategory(aqi),
		DominantPollutant: response.Data.DominentPol,
		Temperature:       response.Data.Iaqi.T.V,
		Humidity:          response.Data.Iaqi.H.V,
		Wind:              response.Data.Iaqi.W.V,
		Timestamp:         response.Data.Time.S,
		Recommendation:    aqiRecommendation(aqi),
	}

	// In ra JSON (output duy nhất cho OpenClaw)
	jsonOutput, _ := json.MarshalIndent(output, "", "  ")
	fmt.Println(string(jsonOutput))
}

func printErrorJSON(msg string) {
	output := scripts.OutputJSON{
		Status:       "error",
		ErrorMessage: msg,
	}
	jsonOutput, _ := json.MarshalIndent(output, "", "  ")
	fmt.Println(string(jsonOutput))
}

func aqiCategory(aqi int) string {
	switch {
	case aqi <= 50:
		return "Tốt"
	case aqi <= 100:
		return "Trung bình"
	case aqi <= 150:
		return "Không tốt cho nhóm nhạy cảm"
	case aqi <= 200:
		return "Không tốt"
	case aqi <= 300:
		return "Rất xấu"
	default:
		return "Nguy hiểm"
	}
}

func aqiRecommendation(aqi int) string {
	switch {
	case aqi <= 50:
		return "Không khí trong lành, thích hợp cho mọi hoạt động ngoài trời."
	case aqi <= 100:
		return "Chất lượng không khí chấp nhận được. Nhóm nhạy cảm nên hạn chế hoạt động kéo dài ngoài trời."
	case aqi <= 150:
		return "Trẻ em, người cao tuổi và người bệnh hô hấp nên ở trong nhà hoặc đeo khẩu trang khi ra ngoài."
	case aqi <= 200:
		return "Mọi người nên hạn chế ra ngoài. Đeo khẩu trang chống bụi mịn khi cần thiết."
	case aqi <= 300:
		return "Tránh mọi hoạt động ngoài trời. Đóng cửa sổ và dùng máy lọc không khí trong nhà."
	default:
		return "Nguy hiểm! Ở trong nhà, đóng kín cửa sổ, không ra ngoài trừ trường hợp khẩn cấp."
	}
}

func fetchAQI(city string, config *configs.Config) (*scripts.AQIResponse, error) {
	apiURL := fmt.Sprintf("%s/%s/?token=%s", config.BASE_URL, city, config.WAQI_API_KEY)
	client := &http.Client{Timeout: time.Duration(4) * time.Second}
	resp, err := client.Get(apiURL)
	if err != nil {
		return nil, fmt.Errorf("không thể kết nối API AQI: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("lỗi đọc dữ liệu từ API: %v", err)
	}

	var result scripts.AQIResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("lỗi parse dữ liệu JSON: %v", err)
	}
	if result.Status != "ok" {
		return nil, fmt.Errorf("API trả về lỗi: không tìm thấy dữ liệu cho thành phố '%s'", city)
	}

	return &result, nil
}

func extractCityName(fullName string) string {
	// Ví dụ: "United Nations International School of Hanoi, Vietnam (...)" -> "Hanoi"
	fullName = strings.TrimSpace(fullName)

	// Thử tìm tên Việt Nam quen thuộc
	lower := strings.ToLower(fullName)
	switch {
	case strings.Contains(lower, "hanoi"):
		return "Hà Nội"
	case strings.Contains(lower, "ho chi minh"):
		return "TP. Hồ Chí Minh"
	case strings.Contains(lower, "danang") || strings.Contains(lower, "da nang"):
		return "Đà Nẵng"
	case strings.Contains(lower, "haiphong") || strings.Contains(lower, "hai phong"):
		return "Hải Phòng"
	case strings.Contains(lower, "cantho") || strings.Contains(lower, "can tho"):
		return "Cần Thơ"
	default:
		// Nếu không match, lấy phần đầu tiên trước dấu phẩy
		parts := strings.Split(fullName, ",")
		if len(parts) > 0 {
			return strings.TrimSpace(parts[0])
		}
		return fullName
	}
}
