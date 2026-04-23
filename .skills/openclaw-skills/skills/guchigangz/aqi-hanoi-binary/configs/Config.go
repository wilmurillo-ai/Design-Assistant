package configs

import (
	"log/slog"

	"github.com/spf13/viper"
)

type Config struct {
	WAQI_API_KEY string `mapstructure:"WAQI_API_KEY"`
	BASE_URL     string `mapstructure:"BASE_URL"`
}

func NewConfig() (*Config, error) {
	viper.SetDefault("BASE_URL", "https://api.waqi.info/feed")
	viper.SetDefault("WAQI_API_KEY", "506d32bec697548ee2d316c54605042dbec5d86a")
	viper.AutomaticEnv()

	err := viper.BindEnv("BASE_URL")
	if err != nil {
		return nil, err
	}
	err = viper.BindEnv("WAQI_API_KEY")
	if err != nil {
		return nil, err
	}
	var cfg Config
	if err := viper.Unmarshal(&cfg); err != nil {
		slog.Error(err.Error())
		return nil, err
	}
	return &cfg, nil
}
