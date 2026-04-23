package fangcloud

import (
	"bufio"
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"
)

const defaultBaseURL = "https://open.fangcloud.com/api"

var defaultCategoryMap = map[string]map[string]struct{}{
	"图片":  {".jpg": {}, ".jpeg": {}, ".png": {}, ".gif": {}, ".bmp": {}, ".webp": {}, ".svg": {}, ".heic": {}},
	"表格":  {".xls": {}, ".xlsx": {}, ".csv": {}},
	"演示":  {".ppt": {}, ".pptx": {}, ".key": {}},
	"文档":  {".md": {}, ".txt": {}, ".doc": {}, ".docx": {}, ".pdf": {}, ".rtf": {}, ".xmds": {}},
	"代码":  {".py": {}, ".js": {}, ".ts": {}, ".tsx": {}, ".jsx": {}, ".java": {}, ".go": {}, ".sh": {}, ".yaml": {}, ".yml": {}, ".json": {}, ".xml": {}, ".sql": {}},
	"压缩包": {".zip": {}, ".rar": {}, ".7z": {}, ".tar": {}, ".gz": {}},
}

type Client struct {
	HTTPClient *http.Client
}

type ChatOptions struct {
	Message    string
	AgentID    string
	SessionID  string
	ChatType   string
	LibraryIDs []string
	Stream     bool
	Stdout     io.Writer
}

type OrganizeOptions struct {
	FolderID        int64
	FolderURL       string
	Mode            string
	PageCapacity    int
	DryRun          bool
	UnknownCategory string
}

type UploadOptions struct {
	LocalDir         string
	RemoteRoot       string
	RemoteParentID   int64
	UseParentID      bool
	DryRun           bool
	ConflictStrategy string
	IncludeHidden    bool
}

type BuildTarget struct {
	GOOS   string
	GOARCH string
}

func NewClient() *Client {
	return &Client{
		HTTPClient: &http.Client{Timeout: 120 * time.Second},
	}
}

func NormalizeURL(input string) (string, error) {
	trimmed := strings.TrimSpace(input)
	if trimmed == "" {
		return "", errors.New("URL is required")
	}
	parsed, err := url.Parse(trimmed)
	if err == nil && parsed.Scheme != "" && parsed.Host != "" {
		trimmed = parsed.String()
	} else {
		if strings.HasPrefix(trimmed, "/") {
			trimmed = defaultBaseURL + trimmed
		} else {
			trimmed = defaultBaseURL + "/" + trimmed
		}
	}
	if strings.Contains(trimmed, "recent_items") && !strings.Contains(trimmed, "limit=") {
		if strings.Contains(trimmed, "?") {
			trimmed += "&limit=20"
		} else {
			trimmed += "?limit=20"
		}
	}
	return trimmed, nil
}

func getToken(rawURL string) (string, error) {
	if strings.Contains(rawURL, "admin") {
		token := os.Getenv("FANGCLOUD_ADMIN_TOKEN")
		if token == "" {
			return "", fmt.Errorf("token not found for admin URL %s", rawURL)
		}
		return token, nil
	}
	token := os.Getenv("FANGCLOUD_USER_TOKEN")
	if token == "" {
		return "", fmt.Errorf("FANGCLOUD_USER_TOKEN not found in environment")
	}
	return token, nil
}

func (c *Client) CallAPI(method, rawURL string, data any) (map[string]any, error) {
	finalURL, err := NormalizeURL(rawURL)
	if err != nil {
		return nil, err
	}
	token, err := getToken(finalURL)
	if err != nil {
		return nil, err
	}
	return c.doJSON(method, finalURL, token, data)
}

func (c *Client) doJSON(method, rawURL, token string, data any) (map[string]any, error) {
	var body io.Reader
	if data != nil {
		payload, err := json.Marshal(data)
		if err != nil {
			return nil, err
		}
		body = bytes.NewReader(payload)
	}

	req, err := http.NewRequest(method, rawURL, body)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	payload, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("HTTP %d %s: %s", resp.StatusCode, resp.Status, string(payload))
	}

	if len(bytes.TrimSpace(payload)) == 0 {
		return map[string]any{}, nil
	}

	var result map[string]any
	if err := json.Unmarshal(payload, &result); err != nil {
		return nil, err
	}
	return result, nil
}

func (c *Client) Chat(opts ChatOptions) (string, error) {
	token := os.Getenv("FANGCLOUD_USER_TOKEN")
	if token == "" {
		return "", errors.New("FANGCLOUD_USER_TOKEN not found in environment")
	}

	if opts.SessionID == "" {
		opts.SessionID = strconv.FormatInt(time.Now().Unix(), 10)
	}
	if opts.ChatType == "" {
		opts.ChatType = "ZSH_CHAT"
	}
	if opts.Stdout == nil {
		opts.Stdout = os.Stdout
	}

	payload := map[string]any{
		"messages":  []map[string]string{{"role": "user", "content": opts.Message}},
		"sessionId": opts.SessionID,
		"chatType":  opts.ChatType,
	}
	if opts.AgentID != "" && opts.ChatType == "ZSH_CHAT" {
		payload["knowledgeGptId"] = opts.AgentID
	}
	if opts.ChatType == "AI_LIBRARY" && len(opts.LibraryIDs) > 0 {
		payload["libraryIds"] = opts.LibraryIDs
		payload["search"] = "true"
		payload["gptType"] = "deepseek"
	}

	body, err := json.Marshal(payload)
	if err != nil {
		return "", err
	}
	req, err := http.NewRequest(http.MethodPost, defaultBaseURL+"/v2/knowledge/chatStream", bytes.NewReader(body))
	if err != nil {
		return "", err
	}
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		payload, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("HTTP %d %s: %s", resp.StatusCode, resp.Status, string(payload))
	}

	scanner := bufio.NewScanner(resp.Body)
	scanner.Buffer(make([]byte, 0, 4096), 1024*1024)
	var content strings.Builder
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if !strings.HasPrefix(line, "data:") {
			continue
		}
		line = strings.TrimSpace(strings.TrimPrefix(line, "data:"))
		if line == "" || line == "[DONE]" {
			continue
		}

		var chunk map[string]any
		if err := json.Unmarshal([]byte(line), &chunk); err != nil {
			continue
		}
		choices, ok := chunk["choices"].([]any)
		if !ok || len(choices) == 0 {
			continue
		}
		first, ok := choices[0].(map[string]any)
		if !ok {
			continue
		}
		delta, ok := first["delta"].(map[string]any)
		if !ok {
			continue
		}
		piece, _ := delta["content"].(string)
		if piece == "" {
			continue
		}
		content.WriteString(piece)
		if opts.Stream {
			if _, err := io.WriteString(opts.Stdout, piece); err != nil {
				return "", err
			}
		}
	}
	if err := scanner.Err(); err != nil {
		return "", err
	}
	if opts.Stream {
		_, _ = io.WriteString(opts.Stdout, "\n")
	}
	return content.String(), nil
}

func ExtractFolderID(folderID int64, folderURL string) (int64, error) {
	if folderID != 0 {
		return folderID, nil
	}
	if strings.TrimSpace(folderURL) == "" {
		return 0, errors.New("either --folder-id or --folder-url is required")
	}
	decoded, err := url.QueryUnescape(folderURL)
	if err != nil {
		decoded = folderURL
	}
	patterns := []*regexp.Regexp{
		regexp.MustCompile(`/folder/(\d+)`),
		regexp.MustCompile(`preview=(\d+)`),
		regexp.MustCompile(`folder_id=(\d+)`),
	}
	for _, pattern := range patterns {
		match := pattern.FindStringSubmatch(decoded)
		if len(match) == 2 {
			id, err := strconv.ParseInt(match[1], 10, 64)
			if err != nil {
				return 0, err
			}
			return id, nil
		}
	}
	return 0, fmt.Errorf("cannot extract folder id from URL: %s", folderURL)
}

func ClassifyFilename(filename, unknownCategory string) string {
	lower := strings.ToLower(filename)
	ext := filepath.Ext(lower)
	for category, extensions := range defaultCategoryMap {
		if _, ok := extensions[ext]; ok {
			return category
		}
	}
	return unknownCategory
}

func (c *Client) OrganizeFolder(opts OrganizeOptions) (map[string]any, error) {
	token := os.Getenv("FANGCLOUD_USER_TOKEN")
	if token == "" {
		return nil, errors.New("FANGCLOUD_USER_TOKEN not found in environment")
	}
	if opts.Mode == "" {
		opts.Mode = "move"
	}
	if opts.PageCapacity == 0 {
		opts.PageCapacity = 200
	}
	if opts.UnknownCategory == "" {
		opts.UnknownCategory = "其他"
	}
	folderID, err := ExtractFolderID(opts.FolderID, opts.FolderURL)
	if err != nil {
		return nil, err
	}

	files, folders, err := c.listChildren(folderID, token, opts.PageCapacity)
	if err != nil {
		return nil, err
	}
	if len(files) == 0 {
		return map[string]any{
			"root_folder_id":          folderID,
			"mode":                    opts.Mode,
			"initial_file_count":      0,
			"created_folders":         []any{},
			"processed_count":         0,
			"processed_by_category":   map[string]int{},
			"failed_count":            0,
			"failed_samples":          []any{},
			"remaining_files_in_root": 0,
			"dry_run":                 opts.DryRun,
		}, nil
	}

	filePlan := make([]map[string]any, 0, len(files))
	categoriesSet := map[string]struct{}{}
	for _, item := range files {
		name, _ := item["name"].(string)
		category := ClassifyFilename(name, opts.UnknownCategory)
		categoriesSet[category] = struct{}{}
		filePlan = append(filePlan, map[string]any{
			"id":       item["id"],
			"name":     name,
			"category": category,
		})
	}
	categories := make([]string, 0, len(categoriesSet))
	for category := range categoriesSet {
		categories = append(categories, category)
	}
	sort.Strings(categories)

	categoryMap, created, err := c.ensureCategories(folderID, folders, categories, token, opts.DryRun)
	if err != nil {
		return nil, err
	}

	processedByCategory := map[string]int{}
	failed := make([]map[string]any, 0)
	processed := 0
	for _, item := range filePlan {
		fileID := toInt64(item["id"])
		category, _ := item["category"].(string)
		targetID := categoryMap[category]
		if fileID == 0 || targetID == 0 {
			failed = append(failed, map[string]any{
				"id":     fileID,
				"name":   item["name"],
				"reason": "missing_target",
			})
			continue
		}
		if opts.DryRun {
			processed++
			processedByCategory[category]++
			continue
		}
		_, err := c.doJSON(http.MethodPost, fmt.Sprintf("%s/v2/file/%d/%s", defaultBaseURL, fileID, opts.Mode), token, map[string]any{
			"target_folder_id": targetID,
		})
		if err != nil {
			failed = append(failed, map[string]any{
				"id":       fileID,
				"name":     item["name"],
				"category": category,
				"error":    err.Error(),
			})
			continue
		}
		processed++
		processedByCategory[category]++
	}

	verifyFiles, _, err := c.listChildren(folderID, token, opts.PageCapacity)
	if err != nil {
		return nil, err
	}

	return map[string]any{
		"root_folder_id":          folderID,
		"mode":                    opts.Mode,
		"initial_file_count":      len(files),
		"categories":              categories,
		"created_folders":         created,
		"processed_count":         processed,
		"processed_by_category":   processedByCategory,
		"failed_count":            len(failed),
		"failed_samples":          limitMapSlice(failed, 10),
		"remaining_files_in_root": len(verifyFiles),
		"dry_run":                 opts.DryRun,
	}, nil
}

func (c *Client) listChildren(folderID int64, token string, pageCapacity int) ([]map[string]any, []map[string]any, error) {
	var lastErr error
	for _, startPage := range []int{0, 1} {
		allFiles := []map[string]any{}
		allFolders := []map[string]any{}
		pageID := startPage
		pageCount := -1
		for {
			path := fmt.Sprintf("%s/v2/folder/%d/children?folder_id=%d&type=all&page_capacity=%d&page_id=%d", defaultBaseURL, folderID, folderID, pageCapacity, pageID)
			data, err := c.doJSON(http.MethodGet, path, token, nil)
			if err != nil {
				lastErr = err
				break
			}
			files := toMapSlice(data["files"])
			folders := toMapSlice(data["folders"])
			allFiles = append(allFiles, files...)
			allFolders = append(allFolders, folders...)
			if pageCount < 0 {
				pageCount = int(toInt64(data["page_count"]))
			}
			if len(files) == 0 && len(folders) == 0 {
				return allFiles, allFolders, nil
			}
			if pageCount > 0 {
				if pageID >= pageCount-1 {
					return allFiles, allFolders, nil
				}
			} else if len(files)+len(folders) < pageCapacity {
				return allFiles, allFolders, nil
			}
			pageID++
		}
	}
	if lastErr == nil {
		lastErr = errors.New("unknown error")
	}
	return nil, nil, fmt.Errorf("failed to list folder children: %w", lastErr)
}

func (c *Client) ensureCategories(folderID int64, existingFolders []map[string]any, categories []string, token string, dryRun bool) (map[string]int64, []map[string]any, error) {
	result := map[string]int64{}
	for _, folder := range existingFolders {
		name, _ := folder["name"].(string)
		id := toInt64(folder["id"])
		if name != "" && id != 0 {
			result[name] = id
		}
	}
	created := []map[string]any{}
	for _, category := range categories {
		if result[category] != 0 {
			continue
		}
		if dryRun {
			created = append(created, map[string]any{"name": category, "id": nil, "dry_run": true})
			result[category] = -1
			continue
		}
		resp, err := c.doJSON(http.MethodPost, defaultBaseURL+"/v2/folder/create", token, map[string]any{
			"name":      category,
			"parent_id": folderID,
		})
		if err != nil {
			return nil, nil, err
		}
		id := toInt64(resp["id"])
		if id == 0 {
			return nil, nil, fmt.Errorf("failed to create category folder: %s", category)
		}
		result[category] = id
		created = append(created, map[string]any{"name": category, "id": id})
	}
	return result, created, nil
}

func (c *Client) UploadDirectory(opts UploadOptions) (map[string]any, error) {
	token := os.Getenv("FANGCLOUD_USER_TOKEN")
	if token == "" {
		return nil, errors.New("FANGCLOUD_USER_TOKEN not found in environment")
	}
	if opts.RemoteRoot != "" && opts.UseParentID {
		return nil, errors.New("--remote-root and --remote-parent-id cannot be used together")
	}

	resolvedLocal, originalMissing, err := resolveLocalDir(opts.LocalDir)
	if err != nil {
		return nil, err
	}
	localName := filepath.Base(resolvedLocal)
	remoteBase := localName
	if opts.RemoteRoot != "" {
		remoteBase = strings.Trim(opts.RemoteRoot, "/") + "/" + localName
	}

	allFiles, err := collectFiles(resolvedLocal, opts.IncludeHidden)
	if err != nil {
		return nil, err
	}

	ensuredFolders := map[string]struct{}{}
	ensuredFolderIDs := map[string]int64{}
	var remoteBaseFolderID int64
	dryRunNextFolderID := int64(-1)
	if opts.UseParentID {
		if opts.DryRun {
			remoteBaseFolderID = dryRunNextFolderID
			dryRunNextFolderID--
		} else {
			remoteBaseFolderID, err = c.ensureChildFolder(token, opts.RemoteParentID, localName)
			if err != nil {
				return nil, err
			}
		}
	}

	uploaded := []map[string]any{}
	failed := []map[string]any{}

	for _, file := range allFiles {
		relFolder := strings.ReplaceAll(filepath.Dir(file.RelPath), string(os.PathSeparator), "/")
		targetFolder := ""
		var targetFolderID int64

		if opts.UseParentID {
			relParts := []string{}
			if relFolder != "" && relFolder != "." {
				relParts = strings.Split(relFolder, "/")
			}
			currentID := remoteBaseFolderID
			currentPath := localName
			for _, part := range relParts {
				key := fmt.Sprintf("%d:%s", currentID, part)
				if ensuredFolderIDs[key] == 0 {
					if opts.DryRun {
						ensuredFolderIDs[key] = dryRunNextFolderID
						dryRunNextFolderID--
					} else {
						childID, err := c.ensureChildFolder(token, currentID, part)
						if err != nil {
							return nil, err
						}
						ensuredFolderIDs[key] = childID
					}
				}
				currentID = ensuredFolderIDs[key]
				currentPath += "/" + part
			}
			targetFolderID = currentID
			targetFolder = currentPath
		} else {
			if relFolder == "" || relFolder == "." {
				targetFolder = remoteBase
			} else {
				targetFolder = strings.Trim(remoteBase+"/"+relFolder, "/")
			}
			if _, ok := ensuredFolders[targetFolder]; !ok {
				if !opts.DryRun {
					_, err := c.doJSON(http.MethodPost, defaultBaseURL+"/v2/folder/create_by_path", token, map[string]any{
						"target_folder_path": targetFolder,
					})
					if err != nil {
						return nil, err
					}
				}
				ensuredFolders[targetFolder] = struct{}{}
			}
		}

		name := sanitizeName(filepath.Base(file.AbsPath))
		uploadName := name
		overwrite := opts.ConflictStrategy != "rename"
		renamedOnConflict := false

		tryUpload := func(overwriteFlag bool) error {
			if opts.DryRun {
				return nil
			}
			var initResp map[string]any
			var err error
			if opts.UseParentID {
				payload := map[string]any{"parent_id": targetFolderID, "name": uploadName, "upload_type": "api"}
				if overwriteFlag {
					payload["is_covered"] = true
				}
				initResp, err = c.doJSON(http.MethodPost, defaultBaseURL+"/v2/file/upload_v2", token, payload)
			} else {
				payload := map[string]any{"target_folder_path": targetFolder, "name": uploadName, "upload_type": "api"}
				if overwriteFlag {
					payload["is_covered"] = true
				}
				initResp, err = c.doJSON(http.MethodPost, defaultBaseURL+"/v2/file/upload_by_path", token, payload)
			}
			if err != nil {
				return err
			}
			uploadURL := findUploadURL(initResp)
			if uploadURL == "" {
				return fmt.Errorf("upload URL not found in init response for %s", file.RelPath)
			}
			return uploadFile(uploadURL, file.AbsPath)
		}

		err := tryUpload(overwrite)
		if err != nil && !overwrite {
			uploadName = buildRename(name)
			renamedOnConflict = true
			err = tryUpload(false)
		}
		if err != nil {
			failed = append(failed, map[string]any{
				"local":               file.RelPath,
				"remote_folder":       targetFolder,
				"remote_folder_id":    nullableInt64(targetFolderID),
				"error":               err.Error(),
				"retried_with_rename": renamedOnConflict,
			})
			continue
		}
		uploaded = append(uploaded, map[string]any{
			"local":               file.RelPath,
			"remote_folder":       targetFolder,
			"remote_folder_id":    nullableInt64(targetFolderID),
			"remote_name":         uploadName,
			"renamed_on_conflict": renamedOnConflict,
		})
	}

	return map[string]any{
		"local_input":           opts.LocalDir,
		"resolved_local":        resolvedLocal,
		"path_autocorrected":    originalMissing != "",
		"original_missing_path": nullableString(originalMissing),
		"remote_mode":           ternary(opts.UseParentID, "parent_id", "path"),
		"remote_parent_id":      nullableInt64(opts.RemoteParentID),
		"remote_base_folder_id": nullableInt64(remoteBaseFolderID),
		"remote_base_folder":    remoteBase,
		"conflict_strategy":     opts.ConflictStrategy,
		"include_hidden":        opts.IncludeHidden,
		"dry_run":               opts.DryRun,
		"total_files":           len(allFiles),
		"uploaded_count":        len(uploaded),
		"failed_count":          len(failed),
		"rename_retry_count":    countRenamed(uploaded),
		"failed_samples":        limitMapSlice(failed, 10),
		"uploaded_samples":      limitMapSlice(uploaded, 20),
	}, nil
}

type localFile struct {
	AbsPath string
	RelPath string
}

func collectFiles(root string, includeHidden bool) ([]localFile, error) {
	files := []localFile{}
	err := filepath.WalkDir(root, func(path string, d os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		name := d.Name()
		if !includeHidden && strings.HasPrefix(name, ".") {
			if d.IsDir() && path != root {
				return filepath.SkipDir
			}
			if path != root {
				return nil
			}
		}
		if d.IsDir() {
			return nil
		}
		relPath, err := filepath.Rel(root, path)
		if err != nil {
			return err
		}
		files = append(files, localFile{AbsPath: path, RelPath: relPath})
		return nil
	})
	if err != nil {
		return nil, err
	}
	sort.Slice(files, func(i, j int) bool { return files[i].RelPath < files[j].RelPath })
	return files, nil
}

func resolveLocalDir(localDir string) (string, string, error) {
	expanded, err := expandHome(localDir)
	if err != nil {
		return "", "", err
	}
	if stat, err := os.Stat(expanded); err == nil && stat.IsDir() {
		abs, err := filepath.Abs(expanded)
		return abs, "", err
	}
	parent := filepath.Dir(expanded)
	target := filepath.Base(expanded)
	stat, err := os.Stat(parent)
	if err != nil || !stat.IsDir() {
		return "", "", fmt.Errorf("local directory not found: %s", expanded)
	}
	entries, err := os.ReadDir(parent)
	if err != nil {
		return "", "", err
	}
	bestName := ""
	bestDistance := 1000
	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}
		name := entry.Name()
		distance := levenshtein(strings.ToLower(target), strings.ToLower(name))
		if distance < bestDistance {
			bestDistance = distance
			bestName = name
		}
	}
	if bestName != "" && bestDistance <= 3 {
		guessed := filepath.Join(parent, bestName)
		abs, err := filepath.Abs(guessed)
		return abs, expanded, err
	}
	return "", "", fmt.Errorf("local directory not found: %s", expanded)
}

func expandHome(path string) (string, error) {
	if path == "~" || strings.HasPrefix(path, "~/") {
		home, err := os.UserHomeDir()
		if err != nil {
			return "", err
		}
		return filepath.Join(home, strings.TrimPrefix(path, "~/")), nil
	}
	return path, nil
}

func sanitizeName(name string) string {
	illegal := `/?:*"<>|`
	var builder strings.Builder
	for _, ch := range name {
		if strings.ContainsRune(illegal, ch) {
			builder.WriteRune('_')
			continue
		}
		builder.WriteRune(ch)
	}
	out := strings.TrimRight(builder.String(), ".")
	if len(out) > 222 {
		return out[:222]
	}
	return out
}

func buildRename(name string) string {
	ext := filepath.Ext(name)
	base := strings.TrimSuffix(name, ext)
	return sanitizeName(fmt.Sprintf("%s__reupload_%s%s", base, time.Now().Format("20060102150405"), ext))
}

func uploadFile(uploadURL, filePath string) error {
	file, err := os.Open(filePath)
	if err != nil {
		return err
	}
	defer file.Close()

	var body bytes.Buffer
	writer := multipart.NewWriter(&body)
	part, err := writer.CreateFormFile("file", filepath.Base(filePath))
	if err != nil {
		return err
	}
	if _, err := io.Copy(part, file); err != nil {
		return err
	}
	if err := writer.Close(); err != nil {
		return err
	}

	req, err := http.NewRequest(http.MethodPost, uploadURL, &body)
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", writer.FormDataContentType())
	client := &http.Client{Timeout: 10 * time.Minute}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 400 {
		payload, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("upload failed with status %d: %s", resp.StatusCode, string(payload))
	}
	return nil
}

func findUploadURL(value any) string {
	switch v := value.(type) {
	case string:
		if strings.HasPrefix(v, "http") && strings.Contains(v, "upload") {
			return v
		}
	case map[string]any:
		for _, child := range v {
			if found := findUploadURL(child); found != "" {
				return found
			}
		}
	case []any:
		for _, child := range v {
			if found := findUploadURL(child); found != "" {
				return found
			}
		}
	}
	return ""
}

func (c *Client) ensureChildFolder(token string, parentID int64, name string) (int64, error) {
	items, err := c.listFolderChildren(token, parentID)
	if err != nil {
		return 0, err
	}
	for _, item := range items {
		if itemType, _ := item["type"].(string); itemType != "folder" {
			continue
		}
		if itemName, _ := item["name"].(string); itemName != name {
			continue
		}
		if inTrash, _ := item["in_trash"].(bool); inTrash {
			continue
		}
		if id := toInt64(item["id"]); id != 0 {
			return id, nil
		}
	}
	resp, err := c.doJSON(http.MethodPost, defaultBaseURL+"/v2/folder/create", token, map[string]any{
		"name":      name,
		"parent_id": parentID,
	})
	if err != nil {
		return 0, err
	}
	id := toInt64(resp["id"])
	if id == 0 {
		return 0, fmt.Errorf("create folder response missing id for %s under parent %d", name, parentID)
	}
	return id, nil
}

func (c *Client) listFolderChildren(token string, folderID int64) ([]map[string]any, error) {
	pageID := 0
	pageCapacity := 100
	items := []map[string]any{}
	for {
		query := url.Values{}
		query.Set("page_id", strconv.Itoa(pageID))
		query.Set("page_capacity", strconv.Itoa(pageCapacity))
		resp, err := c.doJSON(http.MethodGet, fmt.Sprintf("%s/v2/folder/%d/children?%s", defaultBaseURL, folderID, query.Encode()), token, nil)
		if err != nil {
			return nil, err
		}
		items = append(items, toMapSlice(resp["files"])...)
		items = append(items, toMapSlice(resp["folders"])...)
		pageCount := int(toInt64(resp["page_count"]))
		if pageCount <= 1 || pageID+1 >= pageCount {
			return items, nil
		}
		pageID++
	}
}

func toMapSlice(value any) []map[string]any {
	items, ok := value.([]any)
	if !ok {
		if maps, ok := value.([]map[string]any); ok {
			return maps
		}
		return nil
	}
	result := make([]map[string]any, 0, len(items))
	for _, item := range items {
		if m, ok := item.(map[string]any); ok {
			result = append(result, m)
		}
	}
	return result
}

func toInt64(value any) int64 {
	switch v := value.(type) {
	case int:
		return int64(v)
	case int64:
		return v
	case float64:
		return int64(v)
	case json.Number:
		id, _ := v.Int64()
		return id
	case string:
		id, _ := strconv.ParseInt(v, 10, 64)
		return id
	default:
		return 0
	}
}

func limitMapSlice(items []map[string]any, limit int) []map[string]any {
	if len(items) <= limit {
		return items
	}
	return items[:limit]
}

func countRenamed(items []map[string]any) int {
	total := 0
	for _, item := range items {
		if renamed, _ := item["renamed_on_conflict"].(bool); renamed {
			total++
		}
	}
	return total
}

func DefaultBuildTargets() []BuildTarget {
	return []BuildTarget{
		{GOOS: "darwin", GOARCH: "amd64"},
		{GOOS: "darwin", GOARCH: "arm64"},
		{GOOS: "linux", GOARCH: "amd64"},
		{GOOS: "linux", GOARCH: "arm64"},
		{GOOS: "windows", GOARCH: "amd64"},
		{GOOS: "windows", GOARCH: "arm64"},
	}
}

func BuildOutputName(goos, goarch string) string {
	switch goos {
	case "windows":
		return fmt.Sprintf("fangcloud-windows-%s.exe", goarch)
	case "darwin":
		return fmt.Sprintf("fangcloud-macos-%s", goarch)
	default:
		return fmt.Sprintf("fangcloud-linux-%s", goarch)
	}
}

func nullableInt64(value int64) any {
	if value == 0 {
		return nil
	}
	return value
}

func nullableString(value string) any {
	if value == "" {
		return nil
	}
	return value
}

func ternary[T any](condition bool, a, b T) T {
	if condition {
		return a
	}
	return b
}

func levenshtein(a, b string) int {
	if a == b {
		return 0
	}
	if len(a) == 0 {
		return len(b)
	}
	if len(b) == 0 {
		return len(a)
	}
	prev := make([]int, len(b)+1)
	for j := range prev {
		prev[j] = j
	}
	for i := 1; i <= len(a); i++ {
		current := make([]int, len(b)+1)
		current[0] = i
		for j := 1; j <= len(b); j++ {
			cost := 0
			if a[i-1] != b[j-1] {
				cost = 1
			}
			current[j] = min3(
				current[j-1]+1,
				prev[j]+1,
				prev[j-1]+cost,
			)
		}
		prev = current
	}
	return prev[len(b)]
}

func min3(a, b, c int) int {
	if a < b && a < c {
		return a
	}
	if b < c {
		return b
	}
	return c
}
