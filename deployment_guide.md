# Grasshopper MCP Server 部署指南

## 概述

本指南提供了 Grasshopper MCP Server 的完整部署步驟，包括系統需求、安裝過程、配置設定以及故障排除。

## 系統需求

### 硬體需求

**最低需求**:
- CPU: 4 核心 2.0GHz
- RAM: 8GB
- 儲存空間: 10GB 可用空間
- 網路: 穩定的網路連接

**建議需求**:
- CPU: 8 核心 3.0GHz 或更高
- RAM: 16GB 或更高 (用於運行大型 LLM 模型)
- 儲存空間: 50GB 可用空間 (用於模型儲存)
- GPU: NVIDIA RTX 4090 或同等級 (用於 gtp-oss 120B 模型)

### 軟體需求

**必要軟體**:
- Windows 10/11 或 macOS 10.15+ 或 Ubuntu 20.04+
- Python 3.8 或更高版本
- Rhino 7+ 與 Grasshopper
- LM Studio (最新版本)

**可選軟體**:
- Docker (用於容器化部署)
- Git (用於版本控制)

## 安裝步驟

### 1. 準備環境

#### 1.1 安裝 Python 依賴

```bash
# 克隆專案 (如果使用 Git)
git clone <repository-url>
cd grasshopper_mcp_server

# 建立虛擬環境 (建議)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements.txt
```

#### 1.2 安裝 LM Studio

1. 前往 [LM Studio 官網](https://lmstudio.ai/) 下載最新版本
2. 安裝並啟動 LM Studio
3. 下載 gtp-oss 20B 或 120B 模型
4. 啟動本地伺服器 (預設端口: 1234)

#### 1.3 安裝 Grasshopper MCP Component

1. 編譯 `grasshopper_component.cs` 為 `.gha` 檔案
2. 將 `.gha` 檔案複製到 Grasshopper 插件目錄
3. 重新啟動 Rhino 和 Grasshopper
4. 在 Grasshopper 畫布上放置 MCP Bridge 元件

### 2. 配置設定

#### 2.1 MCP Server 配置

建立配置檔案 `config.json`:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false
  },
  "grasshopper": {
    "tcp_host": "localhost",
    "tcp_port": 8888,
    "connection_timeout": 10
  },
  "lm_studio": {
    "base_url": "http://localhost:1234",
    "api_key": "lm-studio",
    "model": "gtp-oss-20b",
    "timeout": 30
  },
  "logging": {
    "level": "INFO",
    "file": "mcp_server.log"
  }
}
```

#### 2.2 LM Studio 配置

1. 開啟 LM Studio
2. 載入 gtp-oss 模型
3. 前往 "Local Server" 頁面
4. 啟用 "OpenAI Compatibility"
5. 設定端口為 1234 (預設)
6. 點擊 "Start Server"

#### 2.3 Grasshopper 配置

1. 開啟 Rhino 和 Grasshopper
2. 在畫布上放置 "MCP Bridge" 元件
3. 設定 Enable 輸入為 True
4. 設定 Port 輸入為 8888 (預設)
5. 確認元件狀態顯示 "MCP Bridge Started"

## 啟動系統

### 1. 啟動順序

按照以下順序啟動各個組件：

1. **啟動 LM Studio**
   ```bash
   # LM Studio 應該已經在背景運行
   # 確認模型已載入且伺服器已啟動
   ```

2. **啟動 Grasshopper**
   ```bash
   # 開啟 Rhino 和 Grasshopper
   # 確認 MCP Bridge 元件已啟用
   ```

3. **啟動 MCP Server**
   ```bash
   cd grasshopper_mcp_server
   python mcp_server.py
   ```

### 2. 驗證安裝

#### 2.1 檢查 MCP Server

```bash
curl http://localhost:5000/health
```

預期回應:
```json
{
  "status": "healthy",
  "grasshopper_connected": true,
  "components_loaded": 16
}
```

#### 2.2 檢查 LM Studio

```bash
curl http://localhost:1234/v1/models
```

預期回應應包含已載入的模型列表。

#### 2.3 測試整合

使用 LM Studio 客戶端進行測試:

```bash
python lm_studio_client.py
```

輸入測試指令:
```
User: Create a circle with radius 10
```

## 使用方式

### 1. 基本操作

#### 1.1 透過 LM Studio 客戶端

```bash
python lm_studio_client.py
```

支援的自然語言指令範例:
- "Create a circle with radius 10"
- "Create a point at coordinates (5, 5, 0)"
- "Extrude the circle upward by 20 units"
- "Connect the point to the circle"
- "Clear the canvas"

#### 1.2 直接 API 調用

```bash
# 創建圓形
curl -X POST http://localhost:5000/create_component \
  -H "Content-Type: application/json" \
  -d '{
    "component_name": "circle",
    "parameters": {
      "Radius": 10.0,
      "Plane": "XY"
    }
  }'

# 列出可用元件
curl http://localhost:5000/components
```

### 2. 進階功能

#### 2.1 批次操作

可以透過腳本進行批次操作:

```python
import requests

base_url = "http://localhost:5000"

# 創建多個元件
components = [
    {"component_name": "point", "parameters": {"X": 0, "Y": 0, "Z": 0}},
    {"component_name": "circle", "parameters": {"Radius": 5.0}},
    {"component_name": "extrude", "parameters": {"Direction": [0, 0, 10]}}
]

for comp in components:
    response = requests.post(f"{base_url}/create_component", json=comp)
    print(response.json())
```

#### 2.2 自定義元件

可以透過修改 `component_factory.py` 添加自定義元件:

```python
# 在 ComponentFactory 類別中添加新元件
custom_comp = ComponentDefinition(
    name="Custom Component",
    internal_name="GH_Custom",
    category="Custom",
    subcategory="User",
    description="User-defined custom component",
    input_params=[...],
    output_params=[...]
)
self.components["custom"] = custom_comp
```

## 故障排除

### 1. 常見問題

#### 1.1 MCP Server 無法啟動

**症狀**: 伺服器啟動失敗或端口被佔用

**解決方案**:
```bash
# 檢查端口使用情況
netstat -tulpn | grep 5000

# 終止佔用端口的程序
sudo kill -9 <PID>

# 或使用不同端口
python mcp_server.py --port 5001
```

#### 1.2 無法連接到 Grasshopper

**症狀**: "Connection refused" 錯誤

**解決方案**:
1. 確認 Grasshopper 已開啟且 MCP Bridge 元件已啟用
2. 檢查防火牆設定
3. 確認端口 8888 未被其他程序佔用
4. 重新啟動 Grasshopper 和 MCP Bridge 元件

#### 1.3 LM Studio 連接失敗

**症狀**: "Connection refused" 或 "Timeout" 錯誤

**解決方案**:
1. 確認 LM Studio 伺服器已啟動
2. 檢查模型是否已正確載入
3. 驗證 OpenAI 相容模式已啟用
4. 確認端口 1234 可訪問

#### 1.4 元件創建失敗

**症狀**: 元件創建請求返回錯誤

**解決方案**:
1. 檢查參數格式和數值範圍
2. 確認元件名稱正確
3. 查看 MCP Server 日誌獲取詳細錯誤信息
4. 驗證 Grasshopper 畫布狀態

### 2. 日誌分析

#### 2.1 MCP Server 日誌

```bash
# 查看即時日誌
tail -f mcp_server.log

# 搜尋錯誤
grep ERROR mcp_server.log
```

#### 2.2 Grasshopper 日誌

Grasshopper 錯誤通常顯示在 Rhino 命令列或 MCP Bridge 元件的輸出中。

### 3. 效能調優

#### 3.1 記憶體優化

```python
# 在 mcp_server.py 中調整
import gc

# 定期清理記憶體
gc.collect()
```

#### 3.2 連接池優化

```python
# 調整 TCP 連接設定
socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```

## 安全考量

### 1. 網路安全

- 在生產環境中，考慮使用 HTTPS
- 限制 API 訪問來源
- 實施 API 金鑰認證

### 2. 系統安全

- 定期更新依賴套件
- 使用最小權限原則
- 監控系統資源使用

## 維護和更新

### 1. 定期維護

- 檢查日誌檔案大小
- 清理暫存檔案
- 更新模型和依賴

### 2. 版本更新

```bash
# 備份現有配置
cp config.json config.json.backup

# 更新程式碼
git pull origin main

# 更新依賴
pip install -r requirements.txt --upgrade

# 重新啟動服務
```

## 支援和社群

- **文件**: 查看專案 README 和 API 文件
- **問題回報**: 使用 GitHub Issues
- **社群討論**: 參與相關論壇和討論群組

---

本部署指南涵蓋了 Grasshopper MCP Server 的完整部署流程。如有任何問題，請參考故障排除章節或聯繫技術支援。

