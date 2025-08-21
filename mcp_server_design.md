# MCP Server 架構和 Grasshopper 元件生成邏輯設計

## 1. 系統總體架構

本專案旨在開發一個 Rhino Grasshopper 的 MCP (Model Context Protocol) Server，使其能夠從 LM Studio 上運行的 gtp-oss LLM 模型接收指令，並自動地依照 LLM 的指示生成 Grasshopper 的元件與連結方式。整個系統將由以下幾個主要部分組成：

1.  **LM Studio (LLM Provider)**：負責運行 gtp-oss 20B 或 120B 等大型語言模型，並提供標準的 OpenAI 相容 API 接口供外部應用程式調用。LLM 將接收用戶的自然語言指令，並根據其理解和預設的工具函數定義，生成 Grasshopper 操作的結構化指令。
2.  **MCP Server (Python)**：這是本專案的核心部分，作為 LM Studio 和 Grasshopper 之間的橋樑。它將監聽來自 LM Studio 的 API 請求，解析 LLM 生成的指令，並將這些指令轉換為 Grasshopper 可以理解和執行的操作。同時，它也負責維護 Grasshopper 元件的知識庫，並將 Grasshopper 的執行結果或狀態回饋給 LLM (如果需要)。
3.  **Grasshopper MCP Component (GH_MCP.gha)**：這是一個運行在 Grasshopper 環境中的插件，負責與 MCP Server 進行通訊，接收來自 Server 的 Grasshopper 操作指令，並在 Grasshopper 畫布上執行實際的元件創建、參數設置和連接操作。它還可能負責將 Grasshopper 的狀態信息 (例如元件列表、參數值等) 發送回 MCP Server。
4.  **Grasshopper (Rhino)**：Grasshopper 是實際執行參數化設計的環境，它將根據 GH_MCP Component 接收到的指令來動態生成和修改設計。
5.  **元件知識庫 (Component Knowledge Base)**：這是一個獨立的數據源，包含 Grasshopper 中所有可用元件的詳細信息，例如元件名稱、輸入/輸出參數、數據類型、預期值範圍、連接規則以及可能的預設值。這個知識庫將被 MCP Server 和 LLM 用於理解 Grasshopper 環境，並生成正確的指令。

以下是系統的總體架構圖：

```mermaid
graph TD
    User[用戶] -->|自然語言指令| LMStudio(LM Studio - LLM Provider)
    LMStudio -->|結構化指令 (Function Call)| MCPServer(MCP Server - Python)
    MCPServer -->|Grasshopper 操作指令| GHComponent(Grasshopper MCP Component - GH_MCP.gha)
    GHComponent -->|執行操作| Grasshopper(Grasshopper - Rhino)
    Grasshopper -->|狀態/結果回饋| GHComponent
    GHComponent -->|狀態/結果回饋| MCPServer
    MCPServer -->|查詢/更新| ComponentKB[元件知識庫 - JSON/DB]
    MCPServer -->|結果/錯誤信息| LMStudio
    LMStudio -->|回應/澄清| User
```

## 2. 通訊流程設計

### 2.1 LM Studio 與 MCP Server 的通訊

LM Studio 將作為一個本地的 OpenAI 相容 API 伺服器運行。MCP Server 將作為一個客戶端，向 LM Studio 發送請求。通訊流程如下：

1.  **用戶輸入**：用戶在與 LM Studio 交互時，輸入自然語言指令，例如「創建一個半徑為 10 的圓形」。
2.  **LLM 處理**：LM Studio 內部運行的 gtp-oss LLM 接收到指令後，會根據其訓練和我們提供的工具函數定義，判斷用戶的意圖。如果判斷需要執行 Grasshopper 操作，LLM 將生成一個 `function_call` 請求。
3.  **MCP Server 監聽**：MCP Server 將作為一個 HTTP 伺服器運行，監聽來自 LM Studio 的 `function_call` 請求。LM Studio 可以配置為將其生成的 `function_call` 請求發送到 MCP Server 的特定端點。
4.  **指令解析**：MCP Server 接收到 `function_call` 請求後，將解析其中的工具函數名稱和參數。例如，它可能會解析出 `create_circle` 函數和 `radius=10`、`center_point=(0,0,0)` 等參數。
5.  **Grasshopper 操作轉換**：MCP Server 將解析後的指令轉換為 Grasshopper MCP Component 可以理解和執行的具體操作指令。這可能涉及到查找元件知識庫以獲取元件的唯一 ID、參數的內部名稱等。
6.  **結果回饋**：Grasshopper 執行操作後，GH_MCP Component 會將執行結果 (成功/失敗、錯誤信息、新創建元件的 ID 等) 返回給 MCP Server。MCP Server 再將這些結果格式化後，作為 LLM 的工具調用結果返回給 LM Studio。LM Studio 可以將這些結果呈現給用戶，或者根據結果生成後續的對話。

### 2.2 MCP Server 與 Grasshopper MCP Component 的通訊

MCP Server (Python) 與 Grasshopper MCP Component (GH_MCP.gha) 之間的通訊將基於 TCP 協議。這是一個輕量級且高效的通訊方式，適合在本地環境中進行實時交互。

1.  **GH_MCP Component 作為 TCP 伺服器**：GH_MCP Component 將在 Grasshopper 內部啟動一個 TCP 伺服器，監聽來自 MCP Server 的連接請求。
2.  **MCP Server 作為 TCP 客戶端**：MCP Server 將作為 TCP 客戶端，連接到 GH_MCP Component 啟動的 TCP 伺服器。
3.  **指令發送**：MCP Server 將 Grasshopper 操作指令 (例如 JSON 格式的命令) 通過 TCP 連接發送給 GH_MCP Component。
4.  **指令執行**：GH_MCP Component 接收到指令後，將使用 Grasshopper API 在 Grasshopper 畫布上執行相應的操作，例如創建元件、設置參數、連接線等。
5.  **結果返回**：GH_MCP Component 將操作的執行結果 (成功/失敗、錯誤信息、新創建元件的 GUID 等) 通過 TCP 連接返回給 MCP Server。

## 3. Grasshopper 元件生成和連結邏輯

### 3.1 元件知識庫的設計

元件知識庫是整個系統的關鍵組成部分，它為 LLM 和 MCP Server 提供了 Grasshopper 元件的「詞彙表」和「語法規則」。建議使用 JSON 格式來儲存元件知識庫，每個元件一個 JSON 文件，或者一個大的 JSON 文件包含所有元件的信息。每個元件的條目應包含以下信息：

*   **元件名稱 (Display Name)**：用戶在 Grasshopper 界面中看到的元件名稱，例如「Circle」、「Extrude」。
*   **內部名稱/GUID (Internal Name/GUID)**：Grasshopper 內部用於識別元件的唯一標識符。這對於程式化操作至關重要。
*   **描述 (Description)**：元件的功能簡要描述，用於幫助 LLM 理解元件的用途。
*   **輸入參數 (Input Parameters)**：
    *   **參數名稱 (Parameter Name)**：例如「Radius」、「Base Plane」。
    *   **內部名稱 (Internal Name)**：參數的內部標識符。
    *   **數據類型 (Data Type)**：例如「Number」、「Plane」、「Geometry」。
    *   **是否必須 (Is Required)**：該參數是否為元件的必要輸入。
    *   **預設值 (Default Value)**：如果參數有預設值。
    *   **值範圍/約束 (Value Range/Constraints)**：例如，半徑必須為正數。
    *   **描述 (Description)**：參數的用途描述。
*   **輸出參數 (Output Parameters)**：
    *   **參數名稱 (Parameter Name)**：例如「Circle」、「Extruded Geometry」。
    *   **內部名稱 (Internal Name)**：參數的內部標識符。
    *   **數據類型 (Data Type)**：例如「Curve」、「Brep」。
    *   **描述 (Description)**：輸出參數的用途描述。
*   **範例用法 (Example Usage)**：提供一些自然語言的範例，說明如何使用該元件，這對於 LLM 的訓練和提示工程非常有幫助。

### 3.2 元件生成邏輯

當 MCP Server 接收到 LLM 關於創建元件的指令時，它將執行以下步驟：

1.  **解析指令**：從 LLM 的 `function_call` 中提取要創建的元件名稱和其參數。
2.  **查詢知識庫**：根據元件名稱在元件知識庫中查找對應的元件信息，獲取其內部名稱、參數列表等。
3.  **構建 Grasshopper 操作命令**：根據知識庫中的信息和 LLM 提供的參數，構建一個 Grasshopper MCP Component 可以理解的命令。這個命令將包含元件的內部名稱以及每個輸入參數的值。例如：
    ```json
    {
        "command": "create_component",
        "component_name": "GH_Circle",
        "parameters": {
            "Radius": 10.0,
            "Plane": [0.0, 0.0, 0.0] // 或者更複雜的平面表示
        }
    }
    ```
4.  **發送命令**：通過 TCP 連接將命令發送給 GH_MCP Component。
5.  **接收結果**：GH_MCP Component 執行命令後，將返回新創建元件的 GUID 和其他相關信息。MCP Server 將儲存這些信息，以便後續的連結操作。

### 3.3 元件連結邏輯

當 MCP Server 接收到 LLM 關於連結元件的指令時，它將執行以下步驟：

1.  **解析指令**：從 LLM 的 `function_call` 中提取要連結的源元件、源參數、目標元件和目標參數。
2.  **查找元件 GUID**：根據元件名稱或之前儲存的 GUID，找到源元件和目標元件的唯一標識符。
3.  **查詢知識庫**：驗證源參數和目標參數的數據類型是否相容，並獲取其內部名稱。
4.  **構建 Grasshopper 操作命令**：構建一個 Grasshopper MCP Component 可以理解的連結命令。例如：
    ```json
    {
        "command": "connect_parameters",
        "source_component_guid": "<source_guid>",
        "source_parameter_name": "<source_param_internal_name>",
        "target_component_guid": "<target_guid>",
        "target_parameter_name": "<target_param_internal_name>"
    }
    ```
5.  **發送命令**：通過 TCP 連接將命令發送給 GH_MCP Component。
6.  **接收結果**：GH_MCP Component 執行命令後，將返回連結操作的成功或失敗狀態。

## 4. 錯誤處理和回饋機制

為了提高系統的穩定性和智能性，需要建立完善的錯誤處理和回饋機制：

*   **MCP Server 錯誤處理**：MCP Server 應捕獲在指令解析、知識庫查詢和與 GH_MCP Component 通訊過程中可能發生的錯誤。這些錯誤應被記錄，並以友好的格式返回給 LM Studio。
*   **Grasshopper 錯誤回饋**：GH_MCP Component 應捕獲在 Grasshopper 內部執行操作時可能發生的錯誤 (例如無效的參數值、不相容的連接)。這些錯誤信息應通過 TCP 返回給 MCP Server，再由 MCP Server 傳遞給 LM Studio。
*   **LLM 錯誤學習**：LM Studio 接收到錯誤信息後，可以將其作為上下文的一部分，用於指導 LLM 在後續的對話中避免重複錯誤，或者向用戶請求澄清。
*   **狀態同步**：MCP Server 應盡可能地維護 Grasshopper 畫布的當前狀態 (例如已創建的元件及其 GUID)，以便 LLM 能夠基於最新的狀態生成指令。當 Grasshopper 畫布發生外部變化時，GH_MCP Component 應能將這些變化通知給 MCP Server。

## 5. 開發考量

*   **語言選擇**：MCP Server 將使用 Python 實現，利用其豐富的庫生態系統和易用性。GH_MCP Component 將使用 C# 實現，因為它是 Grasshopper 插件開發的原生語言。
*   **依賴管理**：對於 Python 部分，將使用 `pip` 管理依賴。對於 C# 部分，將使用 NuGet 或手動管理 Grasshopper SDK 依賴。
*   **測試**：需要為 MCP Server 和 GH_MCP Component 編寫單元測試和整合測試，以確保其功能正確性和穩定性。
*   **部署**：考慮將 MCP Server 打包為可執行文件或 Docker 容器，以便於部署。GH_MCP Component 將作為 Grasshopper 插件進行部署。

這個設計將為開發一個功能強大且智能的 Rhino Grasshopper MCP Server 奠定基礎，使其能夠有效地利用 LLM 的能力來自動化參數化設計過程。

