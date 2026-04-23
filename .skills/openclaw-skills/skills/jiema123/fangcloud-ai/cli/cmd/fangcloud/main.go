package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strings"

	"fangcloud-ai/internal/fangcloud"
)

func main() {
	os.Exit(run(os.Args[1:]))
}

func run(args []string) int {
	if len(args) == 0 {
		printUsage()
		return 1
	}

	client := fangcloud.NewClient()
	switch args[0] {
	case "api":
		return runAPI(client, args[1:])
	case "chat":
		return runChat(client, args[1:])
	case "organize":
		return runOrganize(client, args[1:])
	case "upload":
		return runUpload(client, args[1:])
	case "-h", "--help", "help":
		printUsage()
		return 0
	default:
		fmt.Fprintf(os.Stderr, "Unknown command: %s\n", args[0])
		printUsage()
		return 1
	}
}

func printUsage() {
	fmt.Println("usage: fangcloud <api|chat|organize|upload> [args]")
}

func runAPI(client *fangcloud.Client, args []string) int {
	if len(args) < 2 {
		fmt.Fprintln(os.Stderr, "usage: fangcloud api <METHOD> <URL> [DATA_JSON]")
		return 1
	}
	method := strings.ToUpper(args[0])
	rawURL := args[1]
	var data any
	if len(args) > 2 {
		if err := json.Unmarshal([]byte(args[2]), &data); err != nil {
			fmt.Fprintln(os.Stderr, err)
			return 1
		}
	}
	resp, err := client.CallAPI(method, rawURL, data)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	return printJSON(resp)
}

func runChat(client *fangcloud.Client, args []string) int {
	fs := flag.NewFlagSet("chat", flag.ContinueOnError)
	fs.SetOutput(os.Stderr)
	agentID := fs.String("agent-id", "3776", "")
	sessionID := fs.String("session-id", "", "")
	chatType := fs.String("type", "ZSH_CHAT", "")
	libs := fs.String("libs", "", "")
	noStream := fs.Bool("no-stream", false, "")
	if err := fs.Parse(args); err != nil {
		return 1
	}
	rest := fs.Args()
	if len(rest) < 1 {
		fmt.Fprintln(os.Stderr, "usage: fangcloud chat <message> [flags]")
		return 1
	}
	var libraryIDs []string
	if *libs != "" {
		libraryIDs = strings.Split(*libs, ",")
	}
	content, err := client.Chat(fangcloud.ChatOptions{
		Message:    rest[0],
		AgentID:    *agentID,
		SessionID:  *sessionID,
		ChatType:   *chatType,
		LibraryIDs: libraryIDs,
		Stream:     !*noStream,
		Stdout:     os.Stdout,
	})
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	if *noStream {
		fmt.Println(content)
	}
	return 0
}

func runOrganize(client *fangcloud.Client, args []string) int {
	fs := flag.NewFlagSet("organize", flag.ContinueOnError)
	fs.SetOutput(os.Stderr)
	folderID := fs.Int64("folder-id", 0, "")
	folderURL := fs.String("folder-url", "", "")
	mode := fs.String("mode", "move", "")
	pageCapacity := fs.Int("page-capacity", 200, "")
	unknownCategory := fs.String("unknown-category", "其他", "")
	dryRun := fs.Bool("dry-run", false, "")
	if err := fs.Parse(args); err != nil {
		return 1
	}
	resp, err := client.OrganizeFolder(fangcloud.OrganizeOptions{
		FolderID:        *folderID,
		FolderURL:       *folderURL,
		Mode:            *mode,
		PageCapacity:    *pageCapacity,
		DryRun:          *dryRun,
		UnknownCategory: *unknownCategory,
	})
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	return printJSON(resp)
}

func runUpload(client *fangcloud.Client, args []string) int {
	fs := flag.NewFlagSet("upload", flag.ContinueOnError)
	fs.SetOutput(os.Stderr)
	remoteRoot := fs.String("remote-root", "", "")
	remoteParentID := fs.Int64("remote-parent-id", 0, "")
	conflictStrategy := fs.String("conflict-strategy", "overwrite", "")
	includeHidden := fs.Bool("include-hidden", false, "")
	dryRun := fs.Bool("dry-run", false, "")
	if err := fs.Parse(args); err != nil {
		return 1
	}
	rest := fs.Args()
	if len(rest) < 1 {
		fmt.Fprintln(os.Stderr, "usage: fangcloud upload <local_dir> [flags]")
		return 1
	}
	resp, err := client.UploadDirectory(fangcloud.UploadOptions{
		LocalDir:         rest[0],
		RemoteRoot:       *remoteRoot,
		RemoteParentID:   *remoteParentID,
		UseParentID:      *remoteParentID != 0,
		DryRun:           *dryRun,
		ConflictStrategy: *conflictStrategy,
		IncludeHidden:    *includeHidden,
	})
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	return printJSON(resp)
}

func printJSON(value any) int {
	data, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	fmt.Println(string(data))
	return 0
}
