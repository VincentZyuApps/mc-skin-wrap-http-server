package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/spf13/pflag"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"

	docs "mc-skin-wrap-go/docs"
)

const Version = "0.0.3-beta.4+20260311"

const banner = `
    __  _________    _____ __ __ _____   __    _       ______  ___    ____ 
   /  |/  / ____/   / ___// //_//  _/ | / /   | |     / / __ \/   |  / __ \
  / /|_/ / /  ______\__ \/ ,<   / //  |/ /____| | /| / / /_/ / /| | / /_/ /
 / /  / / /__/_____/__/ / /| |_/ // /|  /_____/ |/ |/ / _, _/ ___ |/ ____/ 
/_/  /_/\____/    /____/_/ |_/___/_/ |_/      |__/|__/_/ |_/_/  |_/_/      

   __________        ___________   __
  / ____/ __ \      / ____/  _/ | / /
 / / __/ / / /_____/ / __ / //  |/ / 
/ /_/ / /_/ /_____/ /_/ // // /|  /  
\____/\____/      \____/___/_/ |_/   
`

type Config struct {
	Host             string   `json:"host"`
	Port             int      `json:"port"`
	RootPath         string   `json:"root_path"`
	CORSAllowOrigins []string `json:"cors_allow_origins"`
	ProxyEnabled     bool     `json:"proxy_enabled"`
	ProxyProtocol    string   `json:"proxy_protocol"`
	ProxyHost        string   `json:"proxy_host"`
	ProxyPort        int      `json:"proxy_port"`
	LogLevel         string   `json:"log_level"`
}

var config Config
var httpClient *http.Client

func loadConfig(path string) {
	// 如果不是绝对路径，转为绝对路径（相对于运行目录或可执行文件目录）
	if !filepath.IsAbs(path) {
		abs, _ := filepath.Abs(path)
		path = abs
	}

	file, err := os.Open(path)
	if err != nil {
		log.Fatalf("[ERROR] 无法打开配置文件 %s: %v", path, err)
	}
	defer file.Close()

	decoder := json.NewDecoder(file)
	if err := decoder.Decode(&config); err != nil {
		log.Fatalf("[ERROR] 无法解析配置文件: %v", err)
	}
	fmt.Printf("[INFO] 已加载配置文件: %s\n", path)
}

func initHTTPClient() {
	transport := &http.Transport{}

	if config.ProxyEnabled {
		protocol := strings.ToLower(config.ProxyProtocol)
		// 如果是 socks5h，Go 的 http.ProxyURL 可能需要特殊处理（通常通过代理 URL 的 scheme 识别）
		proxyURLStr := fmt.Sprintf("%s://%s:%d", protocol, config.ProxyHost, config.ProxyPort)
		proxyURL, err := url.Parse(proxyURLStr)
		if err != nil {
			log.Fatalf("[ERROR] 代理 URL 解析失败: %v", err)
		}
		transport.Proxy = http.ProxyURL(proxyURL)
		fmt.Printf("[INFO] 代理已启用: %s\n", proxyURLStr)
	} else {
		fmt.Println("[INFO] 代理未启用")
	}

	httpClient = &http.Client{
		Transport: transport,
		Timeout:   10 * time.Second,
	}
}

func normalizePathPrefix(value string) string {
	value = strings.TrimSpace(value)
	if value == "" || value == "/" {
		return ""
	}
	if !strings.HasPrefix(value, "/") {
		value = "/" + value
	}
	return strings.TrimRight(value, "/")
}

func joinPathPrefixes(parts ...string) string {
	var builder strings.Builder
	for _, part := range parts {
		if part == "" {
			continue
		}
		// Ensure leading slash for the component if it's not empty/root
		if builder.Len() > 0 && !strings.HasSuffix(builder.String(), "/") && !strings.HasPrefix(part, "/") {
			builder.WriteString("/")
		}
		builder.WriteString(part)
	}

	result := builder.String()
	// Ensure the result starts with / if it's not empty
	if result != "" && !strings.HasPrefix(result, "/") {
		result = "/" + result
	}
	// Clean up double slashes, but be careful with *any which is valid
	// We can use a simple replace for common double slashes arising from joins
	result = strings.ReplaceAll(result, "//", "/")

	if result == "" {
		return "/"
	}
	return result
}

func firstForwardedValue(value string) string {
	if value == "" {
		return ""
	}
	return strings.TrimSpace(strings.Split(value, ",")[0])
}

func requestHost(c *gin.Context) string {
	if host := firstForwardedValue(c.GetHeader("X-Forwarded-Host")); host != "" {
		return host
	}
	if c.Request.Host != "" {
		return c.Request.Host
	}
	return fmt.Sprintf("127.0.0.1:%d", config.Port)
}

func requestScheme(c *gin.Context) string {
	if scheme := firstForwardedValue(c.GetHeader("X-Forwarded-Proto")); scheme != "" {
		return scheme
	}
	if c.Request.TLS != nil {
		return "https"
	}
	return "http"
}

func requestProxyPrefix(c *gin.Context) string {
	return normalizePathPrefix(firstForwardedValue(c.GetHeader("X-Forwarded-Prefix")))
}

func buildSwaggerDoc(c *gin.Context, rootPath string) string {
	spec := *docs.SwaggerInfo
	spec.Host = requestHost(c)
	spec.BasePath = joinPathPrefixes(requestProxyPrefix(c), rootPath)
	spec.Schemes = []string{requestScheme(c)}
	return spec.ReadDoc()
}

func applyCORS(r *gin.Engine) {
	allowedOrigins := make([]string, 0, len(config.CORSAllowOrigins))
	for _, origin := range config.CORSAllowOrigins {
		origin = strings.TrimSpace(origin)
		if origin != "" {
			allowedOrigins = append(allowedOrigins, origin)
		}
	}
	if len(allowedOrigins) == 0 {
		allowedOrigins = []string{"*"}
	}

	r.Use(func(c *gin.Context) {
		origin := c.GetHeader("Origin")
		allowAll := len(allowedOrigins) == 1 && allowedOrigins[0] == "*"

		if allowAll {
			c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		} else if origin != "" {
			for _, allowedOrigin := range allowedOrigins {
				if strings.EqualFold(allowedOrigin, origin) {
					c.Writer.Header().Set("Access-Control-Allow-Origin", origin)
					c.Writer.Header().Add("Vary", "Origin")
					break
				}
			}
		}

		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, OPTIONS")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization, Accept, Origin")
		c.Writer.Header().Set("Access-Control-Expose-Headers", "Content-Type, Content-Length")

		if c.Request.Method == http.MethodOptions {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}

		c.Next()
	})
}

// @title			MC Skin Wrap API
// @version		0.0.1
// @description	Minecraft 皮肤/头像/服务器状态反向代理服务
// @contact.name	VincentZyu
// @license.name	MIT
// @host			127.0.0.1:60311
// @BasePath		/gin_skin_wrap
func main() {
	fmt.Print(banner)
	fmt.Printf("                                                    v%s\n\n", Version)

	configPath := pflag.StringP("config", "c", "config.json", "path to config file")
	pflag.Parse()

	loadConfig(*configPath)
	initHTTPClient()

	if strings.ToLower(config.LogLevel) == "silent" {
		gin.SetMode(gin.ReleaseMode)
		gin.DefaultWriter = io.Discard
	} else if strings.ToLower(config.LogLevel) == "debug" || strings.ToLower(config.LogLevel) == "trace" {
		gin.SetMode(gin.DebugMode)
	} else {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.Default()
	applyCORS(r)
	if err := r.SetTrustedProxies([]string{"127.0.0.1", "::1"}); err != nil {
		log.Fatalf("[ERROR] 设置可信代理失败: %v", err)
	}

	// 确保 RootPath 以 / 开头且不以 / 结尾
	rootPath := normalizePathPrefix(config.RootPath)

	// 路由组处理 RootPath
	base := r.Group(rootPath)
	{
		base.GET("/mcjava/avatar/:name", getAvatar)
		base.GET("/mcjava/skin/:name", getSkin)
		base.GET("/mcjava/server_status/:addr", getServerStatus)
	}

	// Swagger 文档路由 (挂载在 rootPath 下)
	// 访问地址: http://host:port/gin_skin_wrap/docs/
	// 反向代理场景会根据 X-Forwarded-* 头动态修正 host/basePath。

	// 为了避免路由冲突 (*any vs doc.json)，将 doc.json 放在 docs 目录外层
	// 例如: /gin_skin_wrap/swagger_doc.json

	// Ensure paths are constructed correctly using path.Join for cleanliness
	// but manually handle the rootPath logic to be safe
	docJsonPath := rootPath + "/swagger_doc.json"
	docJsonPath = strings.ReplaceAll(docJsonPath, "//", "/")

	r.GET(docJsonPath, func(c *gin.Context) {
		doc := buildSwaggerDoc(c, rootPath)
		c.Data(http.StatusOK, "application/json", []byte(doc))
	})

	// Serve swagger UI, pointing it to our dynamic doc.json endpoint
	// 使用相对路径，使其同时在直接访问和反代访问下工作
	// 浏览器地址: .../docs/index.html -> 相对路径 ../swagger_doc.json -> .../swagger_doc.json

	docsPath := rootPath + "/docs/*any"
	docsPath = strings.ReplaceAll(docsPath, "//", "/")

	rawSwaggerHandler := ginSwagger.WrapHandler(swaggerFiles.Handler,
		ginSwagger.URL("../swagger_doc.json"),
	)

	r.GET(docsPath, func(c *gin.Context) {
		// Fix 404 on trailing slash access (e.g. /docs/)
		// swaggo handler might not default to index.html for root path in all versions/setups
		if c.Param("any") == "/" || c.Param("any") == "" {
			c.Redirect(http.StatusMovedPermanently, "index.html")
			return
		}
		rawSwaggerHandler(c)
	})

	// Redirect root /docs (without slash) to /docs/index.html
	docsRoot := rootPath + "/docs"
	docsRoot = strings.ReplaceAll(docsRoot, "//", "/")
	// Only register if it doesn't conflict.
	// In gin, /path and /path/*any can coexist if handled carefully,
	// but usually *any at /path/*any matches /path/something, not /path itself.
	r.GET(docsRoot, func(c *gin.Context) {
		c.Redirect(http.StatusMovedPermanently, docsRoot+"/index.html")
	})
	r.GET(joinPathPrefixes(rootPath, "/health"), func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "healthy"})
	})

	addr := fmt.Sprintf("%s:%d", config.Host, config.Port)
	fmt.Printf("[INFO] 服务运行在 http://%s%s\n", addr, rootPath)
	if err := r.Run(addr); err != nil {
		log.Fatalf("[ERROR] 启动服务失败: %v", err)
	}
}

// getAvatar godoc
// @Summary		获取玩家头像
// @Description	代理访问 https://minotar.net/avatar/{name}
// @Tags			Minecraft
// @Produce		image/png
// @Param			name	path	string	true	"玩家名称"
// @Success		200		{file}	file	"头像图片"
// @Router			/mcjava/avatar/{name} [get]
func getAvatar(c *gin.Context) {
	name := c.Param("name")
	targetURL := fmt.Sprintf("https://minotar.net/avatar/%s", name)
	proxyRequest(c, targetURL)
}

// getSkin godoc
// @Summary		获取玩家皮肤
// @Description	代理访问 https://minotar.net/skin/{name}
// @Tags			Minecraft
// @Produce		image/png
// @Param			name	path	string	true	"玩家名称"
// @Success		200		{file}	file	"皮肤图片"
// @Router			/mcjava/skin/{name} [get]
func getSkin(c *gin.Context) {
	name := c.Param("name")
	targetURL := fmt.Sprintf("https://minotar.net/skin/%s", name)
	proxyRequest(c, targetURL)
}

// getServerStatus godoc
// @Summary		获取服务器状态
// @Description	代理访问 https://api.mcstatus.io/v2/status/java/{addr}
// @Tags			Minecraft
// @Produce		json
// @Param			addr	path		string					true	"服务器地址"
// @Success		200		{object}	map[string]interface{}	"服务器状态 JSON"
// @Router			/mcjava/server_status/{addr} [get]
func getServerStatus(c *gin.Context) {
	addr := c.Param("addr")
	targetURL := fmt.Sprintf("https://api.mcstatus.io/v2/status/java/%s", addr)
	proxyRequest(c, targetURL)
}

func proxyRequest(c *gin.Context, targetURL string) {
	resp, err := httpClient.Get(targetURL)
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"detail": fmt.Sprintf("请求外部 API 失败: %v", err)})
		return
	}
	defer resp.Body.Close()

	// 透传 Content-Type 和内容
	contentType := resp.Header.Get("Content-Type")
	c.DataFromReader(resp.StatusCode, resp.ContentLength, contentType, resp.Body, nil)
}
