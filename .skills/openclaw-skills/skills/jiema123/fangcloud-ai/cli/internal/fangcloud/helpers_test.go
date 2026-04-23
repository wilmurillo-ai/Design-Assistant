package fangcloud

import "testing"

func TestNormalizeURL(t *testing.T) {
	tests := []struct {
		name string
		in   string
		want string
	}{
		{"full url", "https://open.fangcloud.com/api/v2/user/info", "https://open.fangcloud.com/api/v2/user/info"},
		{"relative path with slash", "/v2/user/info", "https://open.fangcloud.com/api/v2/user/info"},
		{"relative path without slash", "v2/user/info", "https://open.fangcloud.com/api/v2/user/info"},
		{"recent items adds limit", "/v2/file/recent_items", "https://open.fangcloud.com/api/v2/file/recent_items?limit=20"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := NormalizeURL(tt.in)
			if err != nil {
				t.Fatalf("NormalizeURL returned error: %v", err)
			}
			if got != tt.want {
				t.Fatalf("NormalizeURL(%q) = %q, want %q", tt.in, got, tt.want)
			}
		})
	}
}

func TestExtractFolderID(t *testing.T) {
	tests := []struct {
		name string
		url  string
		want int64
	}{
		{"folder path", "https://v2.fangcloud.com/desktop/files/folder/12345", 12345},
		{"preview query", "https://v2.fangcloud.com/desktop/files/recent?preview=67890", 67890},
		{"folder_id query", "https://x.test/path?folder_id=24680", 24680},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := ExtractFolderID(0, tt.url)
			if err != nil {
				t.Fatalf("ExtractFolderID returned error: %v", err)
			}
			if got != tt.want {
				t.Fatalf("ExtractFolderID(%q) = %d, want %d", tt.url, got, tt.want)
			}
		})
	}
}

func TestClassifyFilename(t *testing.T) {
	if got := ClassifyFilename("report.PDF", "其他"); got != "文档" {
		t.Fatalf("ClassifyFilename PDF = %q, want 文档", got)
	}
	if got := ClassifyFilename("archive.unknown", "其他"); got != "其他" {
		t.Fatalf("ClassifyFilename unknown = %q, want 其他", got)
	}
}

func TestBuildOutputName(t *testing.T) {
	tests := []struct {
		goos   string
		goarch string
		want   string
	}{
		{"windows", "amd64", "fangcloud-windows-amd64.exe"},
		{"windows", "arm64", "fangcloud-windows-arm64.exe"},
		{"darwin", "amd64", "fangcloud-macos-amd64"},
		{"darwin", "arm64", "fangcloud-macos-arm64"},
		{"linux", "amd64", "fangcloud-linux-amd64"},
		{"linux", "arm64", "fangcloud-linux-arm64"},
	}

	for _, tt := range tests {
		t.Run(tt.goos+"-"+tt.goarch, func(t *testing.T) {
			got := BuildOutputName(tt.goos, tt.goarch)
			if got != tt.want {
				t.Fatalf("BuildOutputName(%q, %q) = %q, want %q", tt.goos, tt.goarch, got, tt.want)
			}
		})
	}
}

func TestDefaultBuildTargets(t *testing.T) {
	targets := DefaultBuildTargets()
	if len(targets) != 6 {
		t.Fatalf("DefaultBuildTargets() len = %d, want 6", len(targets))
	}
}
