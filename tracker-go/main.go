package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net"
	"net/http"
	"os"
	"os/exec"
	"runtime"
	"strings"
	"time"
)

// TrackResult holds one IP geolocation result.
type TrackResult struct {
	IP        string    `json:"ip"`
	City      string    `json:"city"`
	Region    string    `json:"region"`
	Country   string    `json:"country"`
	ISP       string    `json:"isp"`
	Org       string    `json:"org"`
	AS        string    `json:"as"`
	Latitude  float64   `json:"latitude"`
	Longitude float64   `json:"longitude"`
	Timezone  string    `json:"timezone"`
	Source    string    `json:"source"`
	CheckedAt time.Time `json:"checked_at"`
}

// DeviceRecord holds a discovered local device.
type DeviceRecord struct {
	IP       string `json:"ip"`
	MAC      string `json:"mac"`
	Hostname string `json:"hostname"`
	Vendor   string `json:"vendor"`
}

const (
	outputFileIP    = "ip_track_results.json"
	outputFileScan  = "network_scan_results.json"
	outputFileTrace = "trace_results.txt"
)

func main() {
	if len(os.Args) < 2 {
		printBanner()
		printUsage()
		return
	}

	cmd := strings.ToLower(os.Args[1])
	switch cmd {
	case "track", "ip":
		runIPTrack(os.Args[2:])
	case "scan", "lan":
		runLANScan(os.Args[2:])
	case "trace":
		runTrace(os.Args[2:])
	case "all":
		runAll()
	default:
		fmt.Println("[!] Unknown command:", cmd)
		printUsage()
	}
}

func printBanner() {
	fmt.Println(`==================================================`)
	fmt.Println(`         HARD MODE IP TRACKER (GO)          `)
	fmt.Println(`    IP Geo | LAN Scan | MAC / Vendor Lookup    `)
	fmt.Println(`==================================================`)
	fmt.Println()
}

func printUsage() {
	fmt.Println("Usage:")
	fmt.Println("  tracker-go track <ip-or-domain>   - geolocate IP/domain")
	fmt.Println("  tracker-go scan <subnet>         - scan local subnet for devices")
	fmt.Println("  tracker-go trace <ip>            - simple multi-source trace hint")
	fmt.Println("  tracker-go all                   - run all trackers")
	fmt.Println()
}

// trackIP queries multiple free IP geolocation providers.
func trackIP(target string) (*TrackResult, error) {
	ip := target
	if !isIP(target) {
		resolved, err := net.LookupHost(target)
		if err != nil {
			return nil, fmt.Errorf("dns resolve failed: %v", err)
		}
		if len(resolved) == 0 {
			return nil, fmt.Errorf("no DNS results for %s", target)
		}
		ip = resolved[0]
	}

	result := &TrackResult{IP: ip}

	// Source 1: ip-api.com
	if extra, err := fetchIPAPI(ip); err == nil && extra != nil {
		result.City = extra.City
		result.Region = extra.Region
		result.Country = extra.Country
		result.ISP = extra.ISP
		result.Org = extra.Org
		result.AS = extra.AS
		result.Latitude = extra.Latitude
		result.Longitude = extra.Longitude
		result.Timezone = extra.Timezone
		result.Source = "ip-api.com"
		result.CheckedAt = time.Now()
	} else {
		// Source 2: ipwho.is
		if extra, err2 := fetchIPWho(ip); err2 == nil && extra != nil {
			result.City = extra.City
			result.Region = extra.Region
			result.Country = extra.Country
			result.ISP = extra.ISP
			result.Org = extra.Org
			result.AS = extra.AS
			result.Latitude = extra.Latitude
			result.Longitude = extra.Longitude
			result.Timezone = extra.Timezone
			result.Source = "ipwho.is"
			result.CheckedAt = time.Now()
		}
	}

	return result, nil
}

type ipAPIResult struct {
	City      string  `json:"city"`
	Region    string  `json:"regionName"`
	Country   string  `json:"country"`
	ISP       string  `json:"isp"`
	Org       string  `json:"org"`
	AS        string  `json:"as"`
	Latitude  float64 `json:"lat"`
	Longitude float64 `json:"lon"`
	Timezone  string  `json:"timezone"`
}

func fetchIPAPI(ip string) (*ipAPIResult, error) {
	url := fmt.Sprintf("http://ip-api.com/json/%s?fields=status,city,regionName,country,isp,org,as,lat,lon,timezone", ip)
	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)
	var data struct {
		Status string       `json:"status"`
		Data   *ipAPIResult `json:"-"`
	}
	if err := json.Unmarshal(body, &data); err != nil {
		return nil, err
	}
	if data.Status != "success" {
		return nil, fmt.Errorf("ip-api status: %s", data.Status)
	}
	var out ipAPIResult
	_ = json.Unmarshal(body, &out)
	return &out, nil
}

type ipWhoResult struct {
	City      string  `json:"city"`
	Region    string  `json:"region"`
	Country   string  `json:"country"`
	ISP       string  `json:"connection.isp"`
	Org       string  `json:"connection.org"`
	AS        string  `json:"connection.asn"`
	Latitude  float64 `json:"latitude"`
	Longitude float64 `json:"longitude"`
	Timezone  string  `json:"timezone.id"`
}

func fetchIPWho(ip string) (*ipWhoResult, error) {
	url := fmt.Sprintf("https://ipwho.is/%s", ip)
	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)
	var out ipWhoResult
	if err := json.Unmarshal(body, &out); err != nil {
		return nil, err
	}
	if out.City == "" && out.Country == "" {
		return nil, fmt.Errorf("ipwho: empty response")
	}
	return &out, nil
}

func isIP(s string) bool {
	return net.ParseIP(s) != nil
}

func saveJSON(path string, v interface{}) {
	b, _ := json.MarshalIndent(v, "", "  ")
	_ = os.WriteFile(path, b, 0644)
	fmt.Println("[+] Saved:", path)
}

func runIPTrack(args []string) {
	if len(args) == 0 {
		fmt.Println("Usage: tracker-go track <ip-or-domain>")
		return
	}
	target := args[0]
	fmt.Println("[>] Tracking IP/domain:", target)
	res, err := trackIP(target)
	if err != nil {
		fmt.Println("[-]", err)
		return
	}
	printTrackResult(res)
	saveJSON(outputFileIP, res)
}

func printTrackResult(r *TrackResult) {
	fmt.Println("--------------------------------------------------")
	fmt.Printf("IP       : %s\n", r.IP)
	fmt.Printf("City     : %s\n", r.City)
	fmt.Printf("Region   : %s\n", r.Region)
	fmt.Printf("Country  : %s\n", r.Country)
	fmt.Printf("ISP      : %s\n", r.ISP)
	fmt.Printf("Org      : %s\n", r.Org)
	fmt.Printf("AS       : %s\n", r.AS)
	fmt.Printf("Lat/Lon  : %.5f, %.5f\n", r.Latitude, r.Longitude)
	fmt.Printf("Timezone : %s\n", r.Timezone)
	fmt.Printf("Source   : %s\n", r.Source)
	fmt.Printf("Checked  : %s\n", r.CheckedAt.Format(time.RFC3339))
	fmt.Println("--------------------------------------------------")
	saveTraceResult(r)
}

func saveTraceResult(r *TrackResult) {
	lines := []string{
		"IP TRACE RESULT",
		strings.Repeat("=", 40),
		fmt.Sprintf("Target   : %s", r.IP),
		fmt.Sprintf("City     : %s", r.City),
		fmt.Sprintf("Region   : %s", r.Region),
		fmt.Sprintf("Country  : %s", r.Country),
		fmt.Sprintf("ISP      : %s", r.ISP),
		fmt.Sprintf("Org      : %s", r.Org),
		fmt.Sprintf("AS       : %s", r.AS),
		fmt.Sprintf("Lat/Lon  : %.5f, %.5f", r.Latitude, r.Longitude),
		fmt.Sprintf("Timezone : %s", r.Timezone),
		fmt.Sprintf("Source   : %s", r.Source),
		fmt.Sprintf("Checked  : %s", r.CheckedAt.Format(time.RFC3339)),
	}
	_ = os.WriteFile(outputFileTrace, []byte(strings.Join(lines, "\n")+"\n"), 0644)
}

// LANScan scans a /24 subnet and returns discovered devices.
func LANScan(subnet string) ([]DeviceRecord, error) {
	if subnet == "" {
		subnet = localSubnetGuess()
	}
	base := strings.TrimRight(subnet, ".")
	fmt.Println("[>] Scan subnet:", subnet)
	fmt.Println("[i] This scans /24 hosts: 1..254 via ping sweep.")
	fmt.Println("[i] Vendor lookup needs arp tables / macvendors API.")
	fmt.Println()

	var devices []DeviceRecord
	jobs := make(chan string, 254)
	results := make(chan DeviceRecord, 254)

	workers := 100
	for i := 0; i < workers; i++ {
		go func() {
			for host := range jobs {
				ip := fmt.Sprintf("%s.%s", base, host)
				if isUp(ip) {
					mac := lookupMAC(ip)
					results <- DeviceRecord{
						IP:       ip,
						MAC:      mac,
						Hostname: lookupHostname(ip),
						Vendor:   lookupVendor(mac),
					}
				}
			}
		}()
	}

	_, ipnet, err := net.ParseCIDR(subnet)
	if err != nil {
		return nil, fmt.Errorf("invalid subnet format %s: %v", subnet, err)
	}
	var hosts []string
	if ipnet != nil {
		ones, bits := ipnet.Mask.Size()
		if bits-ones > 8 {
			return nil, fmt.Errorf("only /24 or smaller supported for scan, got /%d", ones)
		}
		shift := bits - ones
		base4 := ipnet.IP.To4()
		if base4 == nil {
			base4 = net.ParseIP(subnet).To4()
		}
		if base4 == nil {
			return nil, fmt.Errorf("invalid base IP")
		}
		for i := 1; i < (1 << shift); i++ {
			if i > 254 {
				break
			}
			hosts = append(hosts, fmt.Sprintf("%d", i))
		}
	} else {
		for i := 1; i < 255; i++ {
			hosts = append(hosts, fmt.Sprintf("%d", i))
		}
	}

	for _, h := range hosts {
		jobs <- h
	}
	close(jobs)

	done := make(chan bool)
	go func() {
		for r := range results {
			devices = append(devices, r)
		}
		done <- true
	}()

	select {
	case <-done:
	case <-time.After(60 * time.Second):
		fmt.Println("[!] Scan timeout reached.")
	}
	fmt.Printf("[+] Scan complete. Found %d device(s).\n", len(devices))
	for _, d := range devices {
		fmt.Printf("  %-15s  %-17s  %-18s  %s\n", d.IP, d.MAC, d.Vendor, d.Hostname)
	}
	saveJSON(outputFileScan, devices)
	return devices, nil
}

func isUp(ip string) bool {
	var cmd *exec.Cmd
	switch runtime.GOOS {
	case "windows":
		cmd = exec.Command("ping", "-n", "1", "-w", "500", ip)
	default:
		cmd = exec.Command("ping", "-c", "1", "-W", "1", ip)
	}
	return cmd.Run() == nil
}

func lookupMAC(ip string) string {
	if runtime.GOOS == "windows" {
		out, err := exec.Command("arp", "-a", ip).Output()
		if err != nil {
			return ""
		}
		fields := strings.Fields(string(out))
		for i, f := range fields {
			if strings.Contains(f, ":") && i > 0 {
				return strings.ToUpper(f)
			}
		}
		return ""
	}
	out, err := exec.Command("arp", "-n", ip).Output()
	if err != nil {
		return ""
	}
	parts := strings.Fields(string(out))
	for _, p := range parts {
		if strings.Contains(p, ":") {
			return strings.ToUpper(p)
		}
	}
	return ""
}

func lookupHostname(ip string) string {
	names, err := net.LookupAddr(ip)
	if err != nil || len(names) == 0 {
		return ""
	}
	return strings.TrimRight(names[0], ".")
}

func lookupVendor(mac string) string {
	if len(mac) < 8 {
		return "unknown"
	}
	oui := strings.ReplaceAll(mac[:8], "-", ":")
	oui = strings.ReplaceAll(oui, ".", ":")
	oui = strings.ReplaceAll(oui, " ", ":")
	if len(oui) > 8 {
		oui = oui[:8]
	}
	// Online MAC vendor lookup from macvendors.com
	url := fmt.Sprintf("https://api.macvendors.com/%s", oui)
	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Get(url)
	if err != nil {
		return "unknown"
	}
	defer resp.Body.Close()
	b, _ := io.ReadAll(resp.Body)
	s := strings.TrimSpace(string(b))
	if s != "" {
		return s
	}
	return "unknown"
}

func localSubnetGuess() string {
	interfaces, err := net.Interfaces()
	if err != nil {
		return "192.168.1.0/24"
	}
	for _, iface := range interfaces {
		if iface.Flags&net.FlagLoopback != 0 || iface.Flags&net.FlagUp == 0 {
			continue
		}
		addrs, err := iface.Addrs()
		if err != nil {
			continue
		}
		for _, addr := range addrs {
			var ip net.IP
			switch v := addr.(type) {
			case *net.IPNet:
				ip = v.IP
			case *net.IPAddr:
				ip = v.IP
			}
			if ip == nil || ip.IsLoopback() {
				continue
			}
			ipv4 := ip.To4()
			if ipv4 != nil {
				s := ipv4.String()
				last := strings.LastIndex(s, ".")
				if last > 0 {
					return s[:last] + ".0/24"
				}
				return s + "/24"
			}
		}
	}
	return "192.168.1.0/24"
}

func runLANScan(args []string) {
	subnet := ""
	if len(args) > 0 {
		subnet = args[0]
	}
	_, err := LANScan(subnet)
	if err != nil {
		fmt.Println("[-]", err)
	}
}

func runTrace(args []string) {
	if len(args) == 0 {
		fmt.Println("Usage: tracker-go.exe trace <ip>")
		return
	}
	target := args[0]
	fmt.Println("[>] Multi-source trace for:", target)
	res, err := trackIP(target)
	if err != nil {
		fmt.Println("[-]", err)
		return
	}
	printTrackResult(res)

	// Try TCP connectivity to common ports.
	fmt.Println("[>] Connection probe:")
	ports := []string{"80", "443", "22", "53"}
	for _, port := range ports {
		addr := net.JoinHostPort(target, port)
		conn, err := net.DialTimeout("tcp", addr, 2*time.Second)
		if err == nil {
			fmt.Printf("  [OPEN] %s (%s)\n", port, conn.RemoteAddr())
			conn.Close()
		} else {
			fmt.Printf("  [CLOSED/FILTERED] %s\n", port)
		}
	}
}

func runAll() {
	printBanner()
	fmt.Println("[>] Running ALL tracker modules...")
	fmt.Println()

	fmt.Println("== 1. IP TRACK ==")
	if len(os.Args) < 3 {
		fmt.Println("[i] No target provided. Trying public IP.")
		res, err := trackIP("")
		if err != nil {
			fmt.Println("[-]", err)
		} else {
			printTrackResult(res)
		}
	} else {
		runIPTrack(os.Args[2:])
	}

	fmt.Println()
	fmt.Println("== 2. LAN SCAN ==")
	runLANScan(nil)

	fmt.Println()
	fmt.Println("== 3. TRACE ==")
	if len(os.Args) >= 3 {
		runTrace(os.Args[2:])
	} else {
		fmt.Println("[i] No target IP passed to trace.")
	}

	fmt.Println()
	fmt.Println("[OK] Done. Check JSON / TXT outputs.")
}
