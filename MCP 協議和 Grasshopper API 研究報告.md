# MCP 協議和 Grasshopper API 研究報告

## 1. 模型上下文協議 (MCP)

模型上下文協議 (Model Context Protocol, MCP) 是一種用於連接 AI 模型與外部應用程式的標準協議。它允許 AI 模型透過結構化的方式接收來自應用程式的上下文資訊，並發送指令以控制應用程式的行為。在 Rhino Grasshopper 的情境中，MCP 協議扮演著 AI 模型 (例如 LM Studio 上運行的 LLM) 與 Grasshopper 之間溝通的橋樑。

### 1.1 MCP 協議的核心概念

MCP 協議的核心思想是將應用程式的狀態和可操作性抽象為 AI 模型可以理解的「上下文」。這個上下文通常包含：

*   **工具函數 (Tool Functions)**：AI 模型可以調用的特定功能，例如在 Grasshopper 中創建一個圓形或連接兩個元件。這些工具函數通常會定義其輸入參數和預期的輸出。
*   **知識庫 (Knowledge Base)**：應用程式中可用元件、參數、屬性等的資訊集合。這使得 AI 模型能夠理解應用程式的「詞彙」和「語法」，從而生成有效的指令。
*   **意圖識別 (Intent Recognition)**：AI 模型能夠從自然語言指令中識別出用戶的意圖，並將其映射到相應的工具函數和操作。

### 1.2 `grasshopper-mcp` 專案分析

`grasshopper-mcp` 是一個開源專案，旨在實現 Grasshopper 與基於 MCP 協議的 AI 模型 (例如 Claude Desktop) 之間的連接。該專案由以下幾個主要部分組成：

*   **Grasshopper MCP 元件 (GH_MCP.gha)**：這是一個 Grasshopper 插件，作為 TCP 伺服器運行，負責接收來自 Python MCP Bridge Server 的指令，並在 Grasshopper 環境中執行相應的操作。它充當 Grasshopper 端點，將 Grasshopper 的內部狀態暴露給外部。
*   **Python MCP Bridge Server**：這是一個 Python 應用程式，充當 AI 模型 (例如 LM Studio) 和 Grasshopper MCP 元件之間的橋樑。它負責解析來自 AI 模型的指令，將其轉換為 Grasshopper MCP 元件可以理解的格式，並將執行結果返回給 AI 模型。它還可能包含用於管理 Grasshopper 元件知識庫的邏輯。
*   **元件知識庫 (Component Knowledge Base)**：通常以 JSON 文件的形式存在，包含 Grasshopper 元件的詳細資訊，例如元件名稱、輸入/輸出參數、參數類型、連接規則等。這個知識庫對於 AI 模型理解 Grasshopper 環境至關重要，使其能夠生成正確且有效的元件操作指令。

`grasshopper-mcp` 專案的架構清晰地展示了 MCP 協議在實際應用中的工作方式。Python Bridge Server 負責處理與 AI 模型的通訊和指令解析，而 Grasshopper MCP 元件則負責在 Grasshopper 環境中執行實際操作。元件知識庫則為 AI 模型提供了必要的領域知識。

## 2. Grasshopper API

Grasshopper 提供了豐富的 API，允許開發者以程式化的方式創建、修改和操作 Grasshopper 文件和元件。這些 API 主要通過 .NET 框架提供，因此可以使用 C# 或 VB.NET 進行開發。對於 Python 開發者，可以透過 `IronPython` 在 Grasshopper 中直接執行 Python 腳本，或者使用 `RhinoCommon` 和 `rhino3dm.py` 等庫在外部 Python 環境中與 Rhino 和 Grasshopper 進行互動。

### 2.1 Grasshopper API 核心概念

*   **GH_Document**：這是 Grasshopper API 中最核心的類別之一，代表一個 Grasshopper 文件。它包含了文件中的所有元件、參數、連接線等。通過 `GH_Document` 物件，可以程式化地添加、刪除、查找和修改文件中的任何元素。
    *   **屬性 (Properties)**：`GH_Document` 類別提供了許多屬性來訪問和控制 Grasshopper 文件的各個方面，例如 `Objects` (獲取文件中的所有頂層物件)、`FilePath` (文件路徑)、`IsModified` (文件是否被修改) 等。
    *   **方法 (Methods)**：`GH_Document` 類別提供了許多方法來執行操作，例如 `AddObject()` (添加新物件到文件)、`RemoveObject()` (從文件中移除物件)、`NewSolution()` (觸發 Grasshopper 重新計算) 等。
*   **IGH_DocumentObject**：這是 Grasshopper 中所有可以在畫布上顯示的物件的基礎介面，包括元件 (Components)、參數 (Parameters) 和組件 (Clusters) 等。通過這個介面，可以訪問物件的通用屬性，例如 `InstanceGuid` (唯一識別符)、`NickName` (顯示名稱)、`Attributes` (視覺屬性) 等。
*   **IGH_Component**：這是 Grasshopper 元件的基礎介面。開發者可以繼承這個介面來創建自定義的 Grasshopper 元件。它定義了元件的輸入和輸出參數、計算邏輯等。
*   **IGH_Param**：這是 Grasshopper 參數的基礎介面。參數用於儲存和傳遞數據。不同類型的參數 (例如數字、幾何體、文本) 會有不同的實現。
*   **GH_IO**：這個命名空間主要處理 Grasshopper 文件的序列化和反序列化，即將 Grasshopper 文件保存到磁碟和從磁碟加載。在大多數情況下，開發者可能不需要直接與 `GH_IO` 交互，因為 `GH_Document` 類別已經提供了高級別的保存和加載功能。
*   **Grasshopper.Kernel**：這個命名空間包含了 Grasshopper 插件的邏輯骨幹，包括 `GH_Document`、`IGH_Component`、`IGH_Param` 等核心類別。
*   **Grasshopper.GUI**：這個命名空間包含了 Grasshopper 用戶界面相關的類別，例如畫布 (Canvas)、菜單 (Menus) 等。通常在開發自定義元件時會與這些類別交互，以實現自定義的繪製和交互邏輯。

### 2.2 程式化生成元件與連結

要程式化地生成 Grasshopper 元件並進行連結，主要涉及以下步驟：

1.  **創建 GH_Document 物件**：首先需要一個 `GH_Document` 實例來代表當前的 Grasshopper 文件。如果是在 Grasshopper 內部運行腳本，通常可以直接訪問當前文件。如果是在外部應用程式中操作，則需要創建一個新的 `GH_Document` 或加載一個現有的文件。
2.  **實例化元件**：使用 `IGH_Component` 或其派生類的構造函數來創建元件實例。例如，要創建一個圓形元件，可能需要找到對應的元件類型並實例化它。
3.  **設置參數**：對於元件的輸入參數，需要設置其值。這可能涉及到創建 `IGH_Param` 實例並將數據賦值給它，或者直接通過元件的屬性來設置。
4.  **添加元件到文件**：使用 `GH_Document.AddObject()` 方法將創建的元件添加到 Grasshopper 文件中。
5.  **連接元件**：通過操作元件的輸入和輸出參數來建立連接。這通常涉及到獲取源參數和目標參數，然後調用相應的方法來建立連接關係。例如，`IGH_Param.AddSource()` 和 `IGH_Param.RemoveSource()` 方法可以用於管理參數的連接。
6.  **觸發解決方案**：在修改 Grasshopper 文件後，需要觸發 Grasshopper 重新計算，以更新所有元件的輸出。這可以通過調用 `GH_Document.NewSolution()` 方法來實現。

## 3. 總結

MCP 協議為 AI 模型與 Grasshopper 之間的互動提供了一個標準化的框架，而 Grasshopper API 則提供了在 Grasshopper 環境中程式化操作元件和文件的能力。結合這兩者，可以實現一個強大的系統，讓 LLM 能夠理解自然語言指令，並自動生成和操作 Grasshopper 定義。關鍵在於建立一個完善的元件知識庫，以及設計一個能夠將 LLM 輸出有效映射到 Grasshopper API 調用的中間層。

