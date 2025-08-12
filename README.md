# 靜態網頁託管服務

這是一個基於 FastAPI (Python) 和 Vue.js 的靜態網頁託管服務。它允許使用者上傳靜態檔案或直接貼上內容，並為其生成唯一的 URL 供外部訪問。此外，它還提供一個頁面來顯示所有已發布的靜態資源列表。

## 核心功能

*   **檔案上傳/內容貼上功能**：允許使用者上傳靜態網頁檔案（HTML, CSS, JS, 圖片等）或直接貼上 HTML/CSS/JS 代碼。
*   **生成對應網址**：上傳或貼上的內容會儲存並產生一個唯一的 URL，供外部訪問。
*   **上傳列表顯示**：提供一個頁面顯示所有已上傳或已發布的靜態資源列表，包括其 URL。

## 技術棧

*   **後端**：Python (FastAPI, Uvicorn)
*   **前端**：Vue.js

## 專案結構

```
your-static-hosting-project/
├── backend/                  # FastAPI 後端專案
│   ├── app/
│   │   ├── main.py           # FastAPI 主應用
│   │   └── static_files/     # 存放上傳靜態檔案的目錄
│   ├── venv/                 # Python 虛擬環境 (或 .venv/)
│   └── requirements.txt      # Python 依賴包
├── frontend/                 # Vue.js 前端專案
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── views/
│   │   │   └── HomeView.vue  # 主要頁面，包含上傳和列表功能
│   │   ├── App.vue
│   │   └── main.js
│   └── package.json          # Node.js 依賴包
├── start_backend.sh          # 啟動後端服務的腳本
├── start_frontend.sh         # 啟動前端服務的腳本
└── README.md
```

## 設定與安裝

### 先決條件

在開始之前，請確保您的系統已安裝以下軟體：

*   **Python 3.8+**
*   **Node.js (LTS 版本)**
*   **npm** (通常隨 Node.js 安裝)
*   **Vue CLI** (如果尚未安裝，請執行 `npm install -g @vue/cli`)

### 後端設定

1.  **進入後端目錄：**
    ```bash
    cd backend
    ```

2.  **建立並啟用虛擬環境：**
    ```bash
    python -m venv venv  # 或 python -m venv .venv
    source venv/bin/activate # macOS/Linux
    # venv\Scripts\activate # Windows
    ```

3.  **安裝 Python 依賴包：**
    ```bash
    pip install -r requirements.txt
    ```

### 前端設定

1.  **進入前端目錄：**
    ```bash
    cd frontend
    ```

2.  **安裝 Node.js 依賴包：**
    ```bash
    npm install
    ```

## 運行應用程式

在專案的根目錄下，您可以使用提供的 shell 腳本來啟動後端和前端服務。

1.  **啟動後端服務：**
    ```bash
    ./start_backend.sh
    ```
    這將在背景啟動 FastAPI 應用程式，預設運行在 `http://localhost:8000`。

2.  **啟動前端服務：**
    ```bash
    ./start_frontend.sh
    ```
    這將在背景啟動 Vue.js 開發伺服器，預設運行在 `http://localhost:8080`。

3.  **訪問應用程式：**
    在您的瀏覽器中打開 `http://localhost:8080` 即可訪問靜態網頁託管服務的前端介面。

## 使用方式

*   **上傳檔案：** 在前端介面中，選擇「上傳檔案」部分，點擊「選擇檔案」按鈕，然後選擇您想要上傳的靜態檔案（例如 HTML, CSS, JS, 圖片等）。點擊「上傳」按鈕即可。
*   **貼上內容：** 在「貼上內容」部分，您可以直接將 HTML, CSS 或 JavaScript 代碼貼入文字區域。選擇對應的檔案副檔名，然後點擊「貼上並發布」按鈕。
*   **查看已發布資源：** 頁面下方會顯示所有已上傳或已發布的資源列表，每個資源都會有一個唯一的 URL。點擊 URL 即可訪問該靜態資源。

## 重要注意事項與故障排除

*   **CORS (跨域資源共享)**：後端已配置 CORS，允許來自 `http://localhost:8080` 的請求。如果您從其他域或埠訪問前端，可能需要修改 `backend/app/main.py` 中的 `origins` 列表。
*   **資源持久化**：目前，已上傳資源的元數據（例如 URL 和檔案名）是儲存在後端應用程式運行時的記憶體字典中。這意味著當後端應用程式重啟時，這些數據將會丟失。在生產環境中，建議將此替換為資料庫（如 SQLite, PostgreSQL 等）以實現數據持久化。
*   **埠衝突**：如果啟動後端或前端時遇到「Address already in use」錯誤，表示對應的埠已被其他程序佔用。您可以使用 `lsof -i :<port>` (macOS/Linux) 或 `netstat -ano | findstr :<port>` (Windows) 來查找佔用埠的程序，然後終止它。
*   **虛擬環境**：請確保您在運行後端相關命令時，始終在 `backend` 目錄中啟用了虛擬環境。