# Grasshopper MCP Server 使用者手冊

## 目錄

1. [簡介](#簡介)
2. [快速開始](#快速開始)
3. [基本概念](#基本概念)
4. [使用介面](#使用介面)
5. [支援的元件](#支援的元件)
6. [實用範例](#實用範例)
7. [進階功能](#進階功能)
8. [常見問題](#常見問題)
9. [技術支援](#技術支援)

## 簡介

Grasshopper MCP Server 是一個革命性的工具，它將人工智慧的力量帶入參數化設計領域。透過自然語言指令，您可以直接與 Grasshopper 進行對話，讓 AI 幫助您創建複雜的參數化模型，而無需手動拖拉元件和連接線。

### 主要特色

- **自然語言控制**: 使用日常語言描述您的設計意圖
- **智能元件生成**: AI 自動選擇和配置適當的 Grasshopper 元件
- **即時回饋**: 立即看到您的指令在 Grasshopper 中的執行結果
- **學習能力**: 系統會從您的使用模式中學習，提供更精確的建議
- **擴展性**: 支援自定義元件和工作流程

### 適用對象

- **建築師**: 快速探索設計概念和形式生成
- **工程師**: 自動化重複性的參數化建模任務
- **設計師**: 專注於創意而非技術細節
- **學生**: 學習參數化設計的概念和實踐
- **研究人員**: 探索 AI 輔助設計的可能性

## 快速開始

### 第一次使用

1. **確認系統已正確安裝**
   - Rhino 和 Grasshopper 已安裝並可正常運行
   - LM Studio 已安裝並載入 gtp-oss 模型
   - MCP Server 已啟動並運行

2. **開啟 Grasshopper**
   - 啟動 Rhino
   - 開啟 Grasshopper
   - 在畫布上放置 "MCP Bridge" 元件
   - 將 Enable 輸入設為 True

3. **啟動 LM Studio 客戶端**
   ```bash
   python lm_studio_client.py
   ```

4. **開始您的第一個設計**
   ```
   User: Create a circle with radius 10
   ```

### 5 分鐘教學

讓我們透過一個簡單的範例來了解系統的基本使用方式：

**步驟 1: 創建基本幾何**
```
User: Create a circle with radius 5
Assistant: I'll create a circle with radius 5 for you.
[系統在 Grasshopper 中創建圓形元件]
```

**步驟 2: 添加更多元件**
```
User: Create a point at the center of the circle
Assistant: I'll create a point at the origin (0,0,0) which will be at the center of your circle.
[系統創建點元件]
```

**步驟 3: 進行變換**
```
User: Extrude the circle upward by 10 units
Assistant: I'll extrude your circle vertically by 10 units to create a cylinder.
[系統創建擠出元件並連接到圓形]
```

**步驟 4: 清理畫布**
```
User: Clear the canvas
Assistant: I'll clear all components from the Grasshopper canvas.
[系統清除所有元件]
```

## 基本概念

### 自然語言指令

系統支援多種自然語言表達方式：

**創建指令**:
- "Create a circle with radius 10"
- "Make a point at coordinates (5, 5, 0)"
- "Generate a line from origin to (10, 0, 0)"

**修改指令**:
- "Change the radius to 15"
- "Move the point to (10, 10, 0)"
- "Rotate the geometry by 45 degrees"

**連接指令**:
- "Connect the circle to an extrude component"
- "Use the point as the center for the circle"
- "Link the output to the next component"

**查詢指令**:
- "What components are available?"
- "Show me the current parameters"
- "List all created components"

### 元件類型

系統支援多種 Grasshopper 元件類型：

**幾何元件**:
- 點 (Point)
- 向量 (Vector)
- 平面 (Plane)

**曲線元件**:
- 圓形 (Circle)
- 直線 (Line)
- 矩形 (Rectangle)
- 多段線 (Polyline)

**曲面元件**:
- 擠出 (Extrude)
- 放樣 (Loft)
- 旋轉 (Revolve)

**變換元件**:
- 移動 (Move)
- 旋轉 (Rotate)
- 縮放 (Scale)

**數學元件**:
- 加法 (Addition)
- 乘法 (Multiplication)
- 數值滑桿 (Number Slider)

### 參數系統

每個元件都有特定的輸入和輸出參數：

**輸入參數**:
- 必要參數：創建元件時必須提供
- 可選參數：有預設值，可以省略
- 數據類型：數值、點、向量、幾何等

**輸出參數**:
- 結果幾何：元件生成的幾何物件
- 變換數據：變換操作的相關信息
- 計算結果：數學運算的結果

## 使用介面

### LM Studio 客戶端介面

這是主要的使用介面，提供自然語言交互：

```
Grasshopper LLM Interface ready. Type 'quit' to exit.

User: [在此輸入您的指令]
Assistant: [AI 的回應和執行結果]
```

**介面特色**:
- 支援多輪對話
- 保持上下文記憶
- 提供詳細的執行回饋
- 錯誤處理和建議

### Web API 介面

對於程式化使用，系統提供 REST API：

**健康檢查**:
```bash
GET /health
```

**列出元件**:
```bash
GET /components
```

**創建元件**:
```bash
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

**連接元件**:
```bash
POST /connect_components
Content-Type: application/json

{
  "source_component": "circle",
  "source_param": "Circle",
  "target_component": "extrude",
  "target_param": "Base"
}
```

### Grasshopper 介面

在 Grasshopper 中，MCP Bridge 元件提供：

**輸入**:
- Enable: 啟用/停用 MCP 橋接
- Port: TCP 通訊端口 (預設 8888)

**輸出**:
- Status: 目前連接狀態
- Log: 操作日誌和錯誤信息

## 支援的元件

### 幾何元件

#### 點 (Point)
**用途**: 創建三維空間中的點
**參數**:
- X: X 座標 (必要)
- Y: Y 座標 (必要)
- Z: Z 座標 (必要)

**範例**:
```
"Create a point at coordinates (10, 5, 0)"
"Make a point at the origin"
```

#### 向量 (Vector)
**用途**: 創建方向向量
**參數**:
- X: X 分量 (必要)
- Y: Y 分量 (必要)
- Z: Z 分量 (必要)

**範例**:
```
"Create a vector pointing upward"
"Make a vector from (0,0,0) to (1,1,1)"
```

#### 平面 (Plane)
**用途**: 定義工作平面
**參數**:
- Origin: 平面原點 (必要)
- Normal: 平面法向量 (可選，預設 Z 軸)

**範例**:
```
"Create a plane at the origin"
"Make a plane with normal vector pointing up"
```

### 曲線元件

#### 圓形 (Circle)
**用途**: 創建圓形曲線
**參數**:
- Plane: 基準平面 (可選，預設 XY 平面)
- Radius: 半徑 (必要，必須 > 0)

**範例**:
```
"Create a circle with radius 10"
"Make a circle on the XY plane with radius 5"
```

#### 直線 (Line)
**用途**: 創建兩點間的直線
**參數**:
- Start: 起點 (必要)
- End: 終點 (必要)

**範例**:
```
"Create a line from origin to (10,0,0)"
"Draw a line between two points"
```

#### 矩形 (Rectangle)
**用途**: 創建矩形曲線
**參數**:
- Plane: 基準平面 (可選，預設 XY 平面)
- X Size: X 方向尺寸 (必要，必須 > 0)
- Y Size: Y 方向尺寸 (必要，必須 > 0)

**範例**:
```
"Create a rectangle 10 by 5"
"Make a square with side length 8"
```

### 曲面元件

#### 擠出 (Extrude)
**用途**: 沿向量擠出幾何
**參數**:
- Base: 基礎幾何 (必要)
- Direction: 擠出方向向量 (必要)

**範例**:
```
"Extrude the circle upward by 10 units"
"Extrude the rectangle in the Z direction"
```

#### 放樣 (Loft)
**用途**: 通過多條曲線創建曲面
**參數**:
- Curves: 放樣曲線 (必要)
- Closed: 是否封閉 (可選，預設 false)

**範例**:
```
"Loft through the circles"
"Create a lofted surface"
```

### 變換元件

#### 移動 (Move)
**用途**: 平移幾何物件
**參數**:
- Geometry: 要移動的幾何 (必要)
- Motion: 移動向量 (必要)

**範例**:
```
"Move the circle 5 units to the right"
"Translate the geometry upward"
```

#### 旋轉 (Rotate)
**用途**: 旋轉幾何物件
**參數**:
- Geometry: 要旋轉的幾何 (必要)
- Angle: 旋轉角度 (弧度) (必要)
- Axis: 旋轉軸 (可選，預設 Z 軸)
- Center: 旋轉中心 (可選，預設原點)

**範例**:
```
"Rotate the geometry 45 degrees"
"Rotate around the Z axis"
```

## 實用範例

### 範例 1: 創建簡單的塔樓

```
User: Create a circle with radius 5
Assistant: I'll create a circle with radius 5 for you.

User: Extrude the circle upward by 20 units
Assistant: I'll extrude your circle vertically by 20 units to create a cylinder.

User: Create another circle with radius 3 at height 20
Assistant: I'll create a smaller circle with radius 3 positioned at height 20.

User: Extrude this circle upward by 15 units
Assistant: I'll extrude the smaller circle to create the upper part of your tower.
```

### 範例 2: 創建螺旋樓梯

```
User: Create a circle with radius 8
Assistant: I'll create a circle with radius 8.

User: Create a point at the center
Assistant: I'll create a point at the origin.

User: Create a helix around the circle with 3 turns and height 30
Assistant: I'll create a helical curve for your spiral staircase.

User: Create rectangular steps along the helix
Assistant: I'll create rectangular steps positioned along the helical path.
```

### 範例 3: 參數化立面

```
User: Create a rectangle 20 by 30
Assistant: I'll create a rectangle with dimensions 20 by 30.

User: Divide the rectangle into a 5 by 6 grid
Assistant: I'll divide your rectangle into a grid of 30 cells.

User: Create circles in each grid cell with varying radii
Assistant: I'll create circles in each cell with different sizes for your facade pattern.

User: Extrude each circle by different amounts
Assistant: I'll extrude the circles with varying depths to create a dynamic facade.
```

### 範例 4: 有機形式生成

```
User: Create 5 random points in space
Assistant: I'll create 5 points at random locations.

User: Create a smooth curve through these points
Assistant: I'll create a smooth interpolated curve through your points.

User: Create circles perpendicular to the curve at regular intervals
Assistant: I'll create circles oriented perpendicular to the curve.

User: Loft through all the circles
Assistant: I'll create a lofted surface through the circles for an organic form.
```

## 進階功能

### 批次操作

您可以在單一指令中執行多個操作：

```
User: Create a circle with radius 10, then extrude it by 5 units, and finally move it 10 units to the right
Assistant: I'll perform all three operations in sequence:
1. Creating circle with radius 10
2. Extruding by 5 units
3. Moving 10 units to the right
```

### 參數化設計

系統支援參數化思維：

```
User: Create a parametric tower where the base radius is 10, height is 50, and the top radius is 5
Assistant: I'll create a parametric tower with tapering from base to top.

User: Now change the base radius to 15
Assistant: I'll update the base radius while maintaining the parametric relationships.
```

### 條件邏輯

使用條件語句創建複雜邏輯：

```
User: If the radius is greater than 5, create a cylinder, otherwise create a cone
Assistant: I'll set up conditional logic based on the radius value.
```

### 迴圈和陣列

創建重複元素：

```
User: Create 10 circles in a row, each with radius increasing by 1
Assistant: I'll create an array of circles with progressively increasing radii.
```

### 數據管理

處理複雜的數據結構：

```
User: Import the point coordinates from a CSV file
Assistant: I'll help you import and process the coordinate data.

User: Create geometry based on the imported data
Assistant: I'll generate geometry using your imported coordinates.
```

## 常見問題

### Q1: 系統無法理解我的指令怎麼辦？

**A**: 嘗試以下方法：
- 使用更簡單、更直接的語言
- 將複雜指令分解為多個簡單步驟
- 參考本手冊中的範例語法
- 檢查元件名稱和參數是否正確

**範例**:
```
❌ "Make some kind of curved thing that goes up"
✅ "Create a circle and extrude it upward by 10 units"
```

### Q2: 如何撤銷上一個操作？

**A**: 目前系統不支援自動撤銷，但您可以：
- 使用 "Clear the canvas" 清除所有元件
- 在 Grasshopper 中手動刪除不需要的元件
- 重新開始您的設計流程

### Q3: 系統支援哪些單位？

**A**: 系統使用 Rhino 的當前單位設定。確保在開始設計前設定正確的單位：
- 公制：公釐、公分、公尺
- 英制：英吋、英尺

### Q4: 如何創建自定義元件？

**A**: 您可以：
1. 修改 `component_factory.py` 添加新元件定義
2. 在 Grasshopper 中創建自定義元件並註冊到系統
3. 聯繫技術支援獲取詳細指導

### Q5: 系統運行緩慢怎麼辦？

**A**: 檢查以下項目：
- 確保您的電腦符合系統需求
- 關閉不必要的應用程式釋放記憶體
- 使用較小的 LLM 模型 (如 gtp-oss 20B 而非 120B)
- 避免創建過於複雜的幾何

### Q6: 如何保存我的設計？

**A**: 
- 在 Grasshopper 中正常保存 .gh 檔案
- 在 Rhino 中保存 3D 模型
- 系統會保持對話歷史，但建議定期保存重要設計

### Q7: 可以與其他 Grasshopper 插件一起使用嗎？

**A**: 是的，MCP Server 與大多數 Grasshopper 插件相容。但請注意：
- 某些插件可能會影響系統性能
- 自定義元件可能需要額外配置
- 建議在穩定環境中測試相容性

### Q8: 如何獲得更好的 AI 回應？

**A**: 提供更詳細和具體的指令：
- 包含具體的數值和參數
- 描述您的設計意圖
- 使用專業術語
- 提供上下文信息

**範例**:
```
❌ "Make it bigger"
✅ "Increase the circle radius from 5 to 10"
```

## 技術支援

### 獲取幫助

如果您遇到問題或需要協助：

1. **查閱文檔**
   - 使用者手冊 (本文檔)
   - 部署指南
   - API 文檔

2. **檢查日誌**
   - MCP Server 日誌檔案
   - Grasshopper 錯誤訊息
   - LM Studio 狀態

3. **社群支援**
   - GitHub Issues
   - 使用者論壇
   - 技術討論群組

4. **專業支援**
   - 技術支援信箱
   - 線上諮詢服務
   - 培訓課程

### 回報問題

回報問題時請提供：

- 詳細的問題描述
- 重現步驟
- 錯誤訊息截圖
- 系統環境信息
- 相關日誌檔案

### 功能建議

我們歡迎您的功能建議：

- 新的元件類型
- 改進的自然語言理解
- 使用者介面優化
- 性能改進建議

---

感謝您使用 Grasshopper MCP Server！我們希望這個工具能夠幫助您更高效地進行參數化設計，並探索 AI 輔助設計的無限可能。

