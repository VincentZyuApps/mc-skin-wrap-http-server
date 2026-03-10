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

	_ "mc-skin-wrap-go/docs" // 导入自动生成的文档
)

const Version = "0.0.2-beta.7+20260311"

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
	Host          string `json:"host"`
	Port          int    `json:"port"`
	RootPath      string `json:"root_path"`
	ProxyEnabled  bool   `json:"proxy_enabled"`
	ProxyProtocol string `json:"proxy_protocol"`
	ProxyHost     string `json:"proxy_host"`
	ProxyPort     int    `json:"proxy_port"`
	LogLevel      string `json:"log_level"`
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

	// 确保 RootPath 以 / 开头且不以 / 结尾
	rootPath := config.RootPath
	if rootPath != "" && !strings.HasPrefix(rootPath, "/") {
		rootPath = "/" + rootPath
	}
	rootPath = strings.TrimSuffix(rootPath, "/")

	// 路由组处理 RootPath
	base := r.Group(rootPath)
	{
		base.GET("/mcjava/avatar/:name", getAvatar)
		base.GET("/mcjava/skin/:name", getSkin)
		base.GET("/mcjava/server_status/:addr", getServerStatus)
	}

	// Swagger 文档路由 (挂载在 rootPath 下)
	// 访问地址: http://host:port/gin_skin_wrap/docs/
	// 注意: gin-swagger 内部用 RequestURI 正则匹配文件名，
	//       访问 /docs/ 时 URI 不含文件名会 404，需手动重定向到 index.html
	swagHandler := ginSwagger.WrapHandler(swaggerFiles.Handler)
	base.GET("/docs/*any", func(c *gin.Context) {
		if c.Param("any") == "/" {
			c.Redirect(http.StatusMovedPermanently, rootPath+"/docs/index.html")
			return
		}
		swagHandler(c)
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
