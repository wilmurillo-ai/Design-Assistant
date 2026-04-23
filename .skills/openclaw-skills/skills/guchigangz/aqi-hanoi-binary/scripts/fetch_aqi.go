package scripts

type AQIResponse struct {
	Status string `json:"status"`
	Data   struct {
		AQI  int `json:"aqi"`
		City struct {
			Name string    `json:"name"`
			Geo  []float64 `json:"geo"`
			URL  string    `json:"url"`
		} `json:"city"`
		DominentPol string `json:"dominentpol"`
		Time        struct {
			S   string `json:"s"`
			TZ  string `json:"tz"`
			Iso string `json:"iso"`
		} `json:"time"`
		Iaqi struct {
			Pm25 struct {
				V int `json:"v"`
			} `json:"pm25"`
			Pm10 struct {
				V int `json:"v"`
			} `json:"pm10"`
			H struct {
				V float64 `json:"v"`
			} `json:"h"`
			T struct {
				V int `json:"v"`
			} `json:"t"`
			W struct {
				V float64 `json:"v"`
			} `json:"w"`
		} `json:"iaqi"`
	} `json:"data"`
}

type OutputJSON struct {
	Status            string    `json:"status"`
	City              string    `json:"city"`
	Location          string    `json:"location"`      // Tên trạm đo cụ thể
	Geo               []float64 `json:"geo,omitempty"` // Tọa độ
	AQI               int       `json:"aqi"`
	Category          string    `json:"category"`
	DominantPollutant string    `json:"dominant_pollutant"`
	Temperature       int       `json:"temperature"` // Nhiệt độ
	Humidity          float64   `json:"humidity"`    // Độ ẩm
	Wind              float64   `json:"wind"`        // Tốc độ gió
	Timestamp         string    `json:"timestamp"`
	Recommendation    string    `json:"recommendation"`
	ErrorMessage      string    `json:"error_message,omitempty"`
}
