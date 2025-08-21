# Grasshopper MCP Server 開發者文檔

## 目錄

1. [架構概述](#架構概述)
2. [開發環境設置](#開發環境設置)
3. [核心模組](#核心模組)
4. [API 參考](#api-參考)
5. [擴展開發](#擴展開發)
6. [測試指南](#測試指南)
7. [部署和維護](#部署和維護)
8. [貢獻指南](#貢獻指南)

## 架構概述

### 系統架構

Grasshopper MCP Server 採用模組化架構，主要由以下組件組成：

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LM Studio     │    │   MCP Server    │    │  Grasshopper    │
│   (gtp-oss)     │◄──►│   (Python)      │◄──►│  MCP Component  │
│                 │    │                 │    │   (C#/.NET)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    OpenAI API              Flask REST API          TCP Socket
   (HTTP/JSON)              (HTTP/JSON)            (TCP/JSON)
```

### 技術棧

**後端 (MCP Server)**:
- Python 3.8+
- Flask (Web 框架)
- Flask-CORS (跨域支援)
- Requests (HTTP 客戶端)
- Socket (TCP 通訊)

**前端 (Grasshopper Component)**:
- C# (.NET Framework 4.8)
- Grasshopper SDK
- Rhino SDK
- Newtonsoft.Json (JSON 處理)

**AI 整合**:
- LM Studio (本地 LLM 伺服器)
- OpenAI 相容 API
- gtp-oss 20B/120B 模型

### 數據流

1. **用戶輸入** → LM Studio (自然語言處理)
2. **LM Studio** → MCP Server (函數調用請求)
3. **MCP Server** → Component Factory (元件驗證)
4. **MCP Server** → Grasshopper Component (TCP 命令)
5. **Grasshopper Component** → Grasshopper API (元件創建)
6. **結果回饋** ← 反向流程

## 開發環境設置

### 必要軟體

```bash
# Python 環境
Python 3.8+
pip (套件管理器)

# .NET 開發環境
Visual Studio 2019+ 或 Visual Studio Code
.NET Framework 4.8

# Rhino 開發環境
Rhino 7+
Grasshopper SDK
RhinoCommon SDK
```

### 開發環境安裝

#### 1. Python 環境

```bash
# 克隆專案
git clone <repository-url>
cd grasshopper_mcp_server

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安裝開發依賴
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 開發專用依賴
```

#### 2. C# 開發環境

```bash
# 安裝 Grasshopper SDK
# 通常隨 Rhino 安裝自動提供

# 設置專案參考
# RhinoCommon.dll
# Grasshopper.dll
# GH_IO.dll
```

#### 3. 開發工具

```bash
# 程式碼格式化
pip install black flake8 isort

# 測試工具
pip install pytest pytest-cov

# 文檔生成
pip install sphinx sphinx-rtd-theme
```

### IDE 配置

#### Visual Studio Code

```json
// .vscode/settings.json
{
    "python.defaultInterpreter": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true
}
```

#### Visual Studio

```xml
<!-- 專案檔案配置 -->
<PropertyGroup>
    <TargetFramework>net48</TargetFramework>
    <RhinoVersion>7.0</RhinoVersion>
    <GrasshopperVersion>1.0</RhinoVersion>
</PropertyGroup>
```

## 核心模組

### 1. MCP Server (mcp_server.py)

主要的 Flask 應用程式，負責 HTTP API 和 TCP 通訊。

#### 關鍵類別

```python
class MCPServer:
    """主要的 MCP 伺服器類別"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.grasshopper_client = GrasshopperTCPClient()
        self.knowledge_base = ComponentKnowledgeBase()
        self.created_components = {}
    
    def run(self, host="0.0.0.0", port=5000, debug=False):
        """啟動伺服器"""
        pass
```

#### 主要端點

```python
@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    pass

@app.route('/create_component', methods=['POST'])
def create_component():
    """創建 Grasshopper 元件"""
    pass

@app.route('/connect_components', methods=['POST'])
def connect_components():
    """連接 Grasshopper 元件"""
    pass
```

### 2. Component Factory (component_factory.py)

元件定義和管理系統。

#### 核心類別

```python
class ComponentDefinition:
    """元件定義數據類別"""
    name: str
    internal_name: str
    category: str
    description: str
    input_params: List[Parameter]
    output_params: List[Parameter]

class ComponentFactory:
    """元件工廠類別"""
    
    def __init__(self):
        self.components = {}
        self._load_default_components()
    
    def validate_component_parameters(self, name, params):
        """驗證元件參數"""
        pass
```

#### 添加新元件

```python
def add_custom_component(self):
    """添加自定義元件範例"""
    custom_comp = ComponentDefinition(
        name="Custom Sphere",
        internal_name="GH_CustomSphere",
        category="Custom",
        subcategory="Geometry",
        description="Create a custom sphere",
        input_params=[
            Parameter("Radius", "R", ParameterType.NUMBER, "Sphere radius", True, 1.0, 0.0),
            Parameter("Center", "C", ParameterType.POINT, "Sphere center", False, "Origin")
        ],
        output_params=[
            Parameter("Sphere", "S", ParameterType.BREP, "Resulting sphere")
        ]
    )
    self.components["custom_sphere"] = custom_comp
```

### 3. LM Studio Client (lm_studio_client.py)

LM Studio API 整合和對話管理。

#### 核心功能

```python
class LMStudioClient:
    """LM Studio API 客戶端"""
    
    def __init__(self, base_url="http://localhost:1234"):
        self.base_url = base_url
        self.tools = self._define_tools()
    
    def chat_completion(self, messages, model="gtp-oss-20b"):
        """發送聊天完成請求"""
        pass
    
    def _define_tools(self):
        """定義可用工具函數"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_grasshopper_component",
                    "description": "Create a component in Grasshopper",
                    "parameters": {...}
                }
            }
        ]
```

### 4. Grasshopper Component (grasshopper_component.cs)

Grasshopper 插件，處理 TCP 通訊和元件操作。

#### 核心類別

```csharp
public class GH_MCPComponent : GH_Component
{
    private TcpListener _tcpListener;
    private Dictionary<string, IGH_DocumentObject> _createdComponents;
    
    protected override void SolveInstance(IGH_DataAccess DA)
    {
        // 主要邏輯處理
    }
    
    private string ProcessCommand(string jsonCommand)
    {
        // 處理來自 MCP Server 的命令
    }
    
    private string CreateComponent(JObject command)
    {
        // 創建 Grasshopper 元件
    }
}
```

## API 參考

### REST API

#### 健康檢查

```http
GET /health
```

**回應**:
```json
{
    "status": "healthy",
    "grasshopper_connected": true,
    "components_loaded": 16
}
```

#### 列出元件

```http
GET /components
```

**回應**:
```json
{
    "components": ["circle", "point", "line", ...],
    "info": "詳細的元件信息..."
}
```

#### 創建元件

```http
POST /create_component
Content-Type: application/json

{
    "component_name": "circle",
    "parameters": {
        "Radius": 10.0,
        "Plane": "XY"
    }
}
```

**回應**:
```json
{
    "success": true,
    "component_guid": "12345678-1234-5678-9012-123456789012",
    "message": "Component created successfully"
}
```

#### 連接元件

```http
POST /connect_components
Content-Type: application/json

{
    "source_component": "circle",
    "source_param": "Circle",
    "target_component": "extrude",
    "target_param": "Base"
}
```

### TCP Protocol

MCP Server 與 Grasshopper Component 之間的 TCP 通訊協議。

#### 命令格式

所有命令都是 JSON 格式，以換行符結尾：

```json
{
    "command": "create_component",
    "component_name": "GH_Circle",
    "parameters": {
        "Radius": 10.0,
        "Plane": "XY"
    }
}
```

#### 回應格式

```json
{
    "success": true,
    "component_guid": "12345678-1234-5678-9012-123456789012",
    "message": "Component created successfully"
}
```

#### 支援的命令

1. **create_component**: 創建元件
2. **connect_parameters**: 連接參數
3. **clear_canvas**: 清除畫布
4. **get_status**: 獲取狀態
5. **list_components**: 列出已創建的元件

## 擴展開發

### 添加新的 Grasshopper 元件

#### 1. 在 Component Factory 中定義

```python
def _add_custom_components(self):
    """添加自定義元件"""
    
    # 定義新元件
    custom_comp = ComponentDefinition(
        name="Custom Component",
        internal_name="GH_Custom",
        category="Custom",
        subcategory="User",
        description="User-defined custom component",
        input_params=[
            Parameter("Input1", "I1", ParameterType.NUMBER, "First input", True),
            Parameter("Input2", "I2", ParameterType.POINT, "Second input", False)
        ],
        output_params=[
            Parameter("Output", "O", ParameterType.GEOMETRY, "Result output")
        ]
    )
    
    self.components["custom"] = custom_comp
```

#### 2. 在 Grasshopper Component 中實現

```csharp
private string CreateCustomComponent(JObject parameters)
{
    try
    {
        // 提取參數
        double input1 = parameters["Input1"]?.ToObject<double>() ?? 0.0;
        // ... 其他參數處理
        
        // 創建實際的 Grasshopper 元件
        var customComponent = new CustomGrasshopperComponent();
        customComponent.CreateAttributes();
        customComponent.Attributes.Pivot = new PointF(100, 100);
        
        // 設置參數
        // ...
        
        // 添加到文檔
        OnPingDocument().AddObject(customComponent, false);
        
        return JsonConvert.SerializeObject(new 
        { 
            success = true, 
            component_guid = customComponent.InstanceGuid.ToString()
        });
    }
    catch (Exception ex)
    {
        return JsonConvert.SerializeObject(new { success = false, error = ex.Message });
    }
}
```

### 添加新的 LLM 工具函數

#### 1. 定義工具函數

```python
def _define_custom_tools(self):
    """定義自定義工具函數"""
    return [
        {
            "type": "function",
            "function": {
                "name": "create_custom_pattern",
                "description": "Create a custom geometric pattern",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern_type": {
                            "type": "string",
                            "enum": ["grid", "radial", "spiral"],
                            "description": "Type of pattern to create"
                        },
                        "count": {
                            "type": "integer",
                            "description": "Number of elements in pattern"
                        }
                    },
                    "required": ["pattern_type", "count"]
                }
            }
        }
    ]
```

#### 2. 實現工具函數處理

```python
def _execute_custom_tool(self, tool_call):
    """執行自定義工具函數"""
    function_name = tool_call["function"]["name"]
    arguments = json.loads(tool_call["function"]["arguments"])
    
    if function_name == "create_custom_pattern":
        return self._create_pattern(arguments)
    
    return {"success": False, "error": f"Unknown function: {function_name}"}

def _create_pattern(self, arguments):
    """創建自定義圖案"""
    pattern_type = arguments.get("pattern_type")
    count = arguments.get("count", 10)
    
    # 實現圖案創建邏輯
    # ...
    
    return {"success": True, "message": f"Created {pattern_type} pattern with {count} elements"}
```

### 自定義參數類型

#### 1. 定義新的參數類型

```python
class ParameterType(Enum):
    """擴展參數類型"""
    # 現有類型...
    CUSTOM_TYPE = "CustomType"
    MATERIAL = "Material"
    TEXTURE = "Texture"
```

#### 2. 實現參數驗證

```python
def _validate_custom_parameter(self, param_type, value):
    """驗證自定義參數"""
    if param_type == ParameterType.CUSTOM_TYPE:
        # 自定義驗證邏輯
        if not self._is_valid_custom_value(value):
            raise ValueError("Invalid custom parameter value")
    
    return value
```

## 測試指南

### 單元測試

#### 測試 Component Factory

```python
import pytest
from component_factory import ComponentFactory, ParameterType

class TestComponentFactory:
    
    def setup_method(self):
        self.factory = ComponentFactory()
    
    def test_component_loading(self):
        """測試元件載入"""
        assert len(self.factory.components) > 0
        assert "circle" in self.factory.components
    
    def test_parameter_validation(self):
        """測試參數驗證"""
        result = self.factory.validate_component_parameters(
            "circle", {"Radius": 10.0}
        )
        assert "error" not in result
        assert result["Radius"] == 10.0
    
    def test_invalid_parameters(self):
        """測試無效參數"""
        result = self.factory.validate_component_parameters(
            "circle", {"Radius": -5.0}
        )
        assert "error" in result
```

#### 測試 MCP Server

```python
import pytest
from mcp_server import MCPServer

class TestMCPServer:
    
    def setup_method(self):
        self.server = MCPServer()
        self.client = self.server.app.test_client()
    
    def test_health_endpoint(self):
        """測試健康檢查端點"""
        response = self.client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
    
    def test_create_component_endpoint(self):
        """測試元件創建端點"""
        payload = {
            "component_name": "circle",
            "parameters": {"Radius": 10.0}
        }
        response = self.client.post('/create_component', json=payload)
        assert response.status_code == 200
```

### 整合測試

#### 測試完整工作流程

```python
def test_complete_workflow():
    """測試完整的工作流程"""
    # 1. 啟動 MCP Server
    server = MCPServer()
    
    # 2. 創建元件
    result = server.create_component("circle", {"Radius": 10.0})
    assert result["success"]
    
    # 3. 創建另一個元件
    result = server.create_component("extrude", {"Direction": [0, 0, 10]})
    assert result["success"]
    
    # 4. 連接元件
    result = server.connect_components("circle", "Circle", "extrude", "Base")
    assert result["success"]
```

### 效能測試

```python
import time
import concurrent.futures

def test_concurrent_requests():
    """測試並發請求"""
    server = MCPServer()
    client = server.app.test_client()
    
    def make_request():
        return client.get('/health')
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(100)]
        results = [future.result() for future in futures]
    
    end_time = time.time()
    
    # 檢查所有請求都成功
    assert all(r.status_code == 200 for r in results)
    
    # 檢查效能
    total_time = end_time - start_time
    assert total_time < 5.0  # 100 個請求應在 5 秒內完成
```

### 測試執行

```bash
# 執行所有測試
pytest

# 執行特定測試檔案
pytest tests/test_component_factory.py

# 執行測試並生成覆蓋率報告
pytest --cov=. --cov-report=html

# 執行效能測試
pytest tests/test_performance.py -v
```

## 部署和維護

### Docker 部署

#### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "mcp_server.py"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - mcp-server
    restart: unless-stopped
```

### 監控和日誌

#### 日誌配置

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    """設置日誌"""
    if not app.debug:
        file_handler = RotatingFileHandler(
            'logs/mcp_server.log', 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('MCP Server startup')
```

#### 健康檢查腳本

```bash
#!/bin/bash
# health_check.sh

HEALTH_URL="http://localhost:5000/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "MCP Server is healthy"
    exit 0
else
    echo "MCP Server is unhealthy (HTTP $RESPONSE)"
    exit 1
fi
```

### 效能優化

#### 連接池

```python
import threading
from queue import Queue

class ConnectionPool:
    """TCP 連接池"""
    
    def __init__(self, max_connections=10):
        self.max_connections = max_connections
        self.pool = Queue(maxsize=max_connections)
        self.lock = threading.Lock()
    
    def get_connection(self):
        """獲取連接"""
        try:
            return self.pool.get_nowait()
        except:
            return self._create_connection()
    
    def return_connection(self, conn):
        """歸還連接"""
        try:
            self.pool.put_nowait(conn)
        except:
            conn.close()
```

#### 快取機制

```python
from functools import lru_cache
import time

class ComponentCache:
    """元件快取"""
    
    def __init__(self, ttl=300):  # 5 分鐘 TTL
        self.cache = {}
        self.ttl = ttl
    
    @lru_cache(maxsize=128)
    def get_component_info(self, component_name):
        """獲取元件信息（帶快取）"""
        return self._load_component_info(component_name)
    
    def _load_component_info(self, component_name):
        """載入元件信息"""
        # 實際載入邏輯
        pass
```

## 貢獻指南

### 程式碼風格

#### Python 程式碼風格

```python
# 使用 Black 格式化
black --line-length 88 .

# 使用 isort 排序 import
isort .

# 使用 flake8 檢查
flake8 --max-line-length 88 .
```

#### C# 程式碼風格

```csharp
// 遵循 Microsoft C# 編碼慣例
// https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/inside-a-program/coding-conventions

public class ExampleClass
{
    private readonly string _privateField;
    
    public string PublicProperty { get; set; }
    
    public void PublicMethod()
    {
        // 方法實現
    }
}
```

### 提交流程

#### 1. Fork 和 Clone

```bash
# Fork 專案到您的 GitHub 帳號
# 然後 clone 到本地

git clone https://github.com/yourusername/grasshopper-mcp-server.git
cd grasshopper-mcp-server
```

#### 2. 建立功能分支

```bash
git checkout -b feature/new-component-support
```

#### 3. 開發和測試

```bash
# 進行開發
# ...

# 執行測試
pytest

# 檢查程式碼風格
black .
flake8 .
```

#### 4. 提交變更

```bash
git add .
git commit -m "Add support for new component type

- Implement CustomComponent class
- Add parameter validation
- Update documentation
- Add unit tests"
```

#### 5. 推送和建立 Pull Request

```bash
git push origin feature/new-component-support
```

然後在 GitHub 上建立 Pull Request。

### Pull Request 檢查清單

- [ ] 程式碼遵循專案風格指南
- [ ] 所有測試通過
- [ ] 添加了適當的測試覆蓋
- [ ] 更新了相關文檔
- [ ] 提交訊息清晰且描述性強
- [ ] 沒有合併衝突

### 發布流程

#### 版本號規則

使用語義化版本 (Semantic Versioning):
- MAJOR.MINOR.PATCH (例如: 1.2.3)
- MAJOR: 不相容的 API 變更
- MINOR: 向後相容的功能新增
- PATCH: 向後相容的錯誤修復

#### 發布步驟

```bash
# 1. 更新版本號
echo "1.2.3" > VERSION

# 2. 更新 CHANGELOG
# 編輯 CHANGELOG.md

# 3. 提交版本變更
git add VERSION CHANGELOG.md
git commit -m "Bump version to 1.2.3"

# 4. 建立標籤
git tag -a v1.2.3 -m "Release version 1.2.3"

# 5. 推送
git push origin main --tags
```

---

這份開發者文檔提供了 Grasshopper MCP Server 的完整開發指南。如果您有任何問題或建議，請隨時聯繫開發團隊或在 GitHub 上建立 Issue。

