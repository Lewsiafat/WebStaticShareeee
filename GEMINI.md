好的，很高興為您提供關於建立靜態網頁服務的指導，該服務將使用 FastAPI 作為後端，Vue.js 作為前端，並利用 Uvicorn 運行 FastAPI 應用。

這個專案將包含以下核心功能：

1.  **檔案上傳/內容貼上功能**：允許使用者上傳靜態網頁檔案（HTML, CSS, JS, 圖片等）或直接貼上 HTML/CSS/JS 代碼。
2.  **生成對應網址**：上傳或貼上的內容會儲存並產生一個唯一的 URL，供外部訪問。
3.  **上傳列表顯示**：提供一個頁面顯示所有已上傳或已發布的靜態資源列表，包括其 URL。
4.  **技術棧**：
    *   **後端**：Python (FastAPI, Uvicorn)
    *   **前端**：Vue.js

### 專案架構概述

我們將建立兩個獨立的專案：一個是 FastAPI 後端，另一個是 Vue.js 前端。前端將透過 API 呼叫與後端進行通訊。

```
your-static-hosting-project/
├── backend/                  # FastAPI 後端專案
│   ├── app/
│   │   ├── main.py           # FastAPI 主應用
│   │   ├── api/
│   │   │   ├── endpoints.py  # API 端點定義 (上傳、列表等)
│   │   │   └── models.py     # 資料模型 (例如：上傳項目資訊)
│   │   ├── static_files/     # 存放上傳靜態檔案的目錄
│   │   └── __init__.py
│   ├── .env                  # 環境變數 (可選)
│   ├── requirements.txt      # Python 依賴包
│   └── uvicorn_run.sh        # 啟動 Uvicorn 的腳本 (可選)
└── frontend/                 # Vue.js 前端專案
    ├── public/
    ├── src/
    │   ├── assets/
    │   ├── components/       # Vue 組件 (上傳表單、列表項目等)
    │   ├── views/            # Vue 視圖 (上傳頁面、列表頁面)
    │   ├── App.vue
    │   └── main.js
    ├── package.json          # Node.js 依賴包
    └── vue.config.js         # Vue CLI 配置 (可選)
```

### 後端：FastAPI & Uvicorn

#### 1. 建立 FastAPI 專案

首先，建立一個 Python 虛擬環境並安裝必要的套件：

```bash
# 在專案根目錄
mkdir backend
cd backend
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

pip install fastapi uvicorn python-multipart aiofiles
```

*   `fastapi`: Web 框架。
*   `uvicorn`: ASGI 伺服器，用於運行 FastAPI 應用。
*   `python-multipart`: 處理檔案上傳的依賴。
*   `aiofiles`: 異步檔案操作，用於高效地儲存上傳的檔案。

#### 2. FastAPI 應用程式 (`backend/app/main.py`)

```python
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import uuid
import aiofiles

app = FastAPI()

# 儲存上傳檔案的目錄
UPLOAD_DIR = "static_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 儲存已上傳資源的元數據 (簡單起見，這裡使用字典，實際生產環境建議使用資料庫)
# 格式: { "id": {"filename": "xxx.html", "url": "/static/xxx.html", "type": "file/paste"} }
uploaded_resources = {}

# 掛載靜態檔案目錄，讓 FastAPI 可以直接提供這些檔案
# /resources/{resource_id} 會對應到 UPLOAD_DIR/{resource_id}
app.mount("/resources", StaticFiles(directory=UPLOAD_DIR), name="resources")

class PasteContent(BaseModel):
    content: str
    file_extension: str = "html" # 預設為 HTML

# --- API 端點 ---

@app.get("/")
async def read_root():
    return {"message": "歡迎來到靜態網頁服務後端！"}

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    """上傳單一檔案。"""
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    save_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_extension}")

    try:
        async with aiofiles.open(save_path, "wb") as out_file:
            while content := await file.read(1024):  # 分塊讀取寫入
                await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上傳檔案失敗: {e}")

    resource_url = f"/resources/{file_id}{file_extension}"
    uploaded_resources[file_id] = {
        "filename": file.filename,
        "id": file_id,
        "url": resource_url,
        "type": "file",
        "original_name": file.filename,
        "extension": file_extension
    }
    return {"message": "檔案上傳成功", "url": resource_url, "id": file_id}

@app.post("/pastecontent/")
async def paste_content(item: PasteContent):
    """貼上內容並儲存為檔案。"""
    file_id = str(uuid.uuid4())
    file_extension = item.file_extension if item.file_extension.startswith('.') else f".{item.file_extension}"
    save_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_extension}")

    try:
        async with aiofiles.open(save_path, "w", encoding="utf-8") as out_file:
            await out_file.write(item.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"儲存內容失敗: {e}")

    resource_url = f"/resources/{file_id}{file_extension}"
    uploaded_resources[file_id] = {
        "filename": f"pasted_content{file_extension}",
        "id": file_id,
        "url": resource_url,
        "type": "paste",
        "extension": file_extension
    }
    return {"message": "內容儲存成功", "url": resource_url, "id": file_id}

@app.get("/list/")
async def list_resources():
    """獲取所有已上傳資源的列表。"""
    # 這裡返回的資料結構可以根據前端需求進行調整
    return {"resources": list(uploaded_resources.values())}

# 可選: 直接重定向到上傳的資源
@app.get("/go/{resource_id}")
async def go_to_resource(resource_id: str):
    """根據 ID 重定向到對應的資源 URL。"""
    if resource_id in uploaded_resources:
        return RedirectResponse(url=uploaded_resources[resource_id]["url"])
    raise HTTPException(status_code=404, detail="資源未找到")

```

**重要提示：**

*   **`UPLOAD_DIR`**：這是您的靜態檔案會被儲存的地方。
*   **`uploaded_resources` 字典**：在生產環境中，這個應該替換為一個資料庫（如 SQLite, PostgreSQL, MongoDB 等）來持久化儲存資源的元數據，因為當應用程式重啟時，字典中的數據會丟失。
*   **安全考慮**：這個範例沒有包含任何認證或授權。在真實應用中，您需要考慮誰可以上傳、誰可以查看列表等。同時，對上傳的檔案進行病毒掃描或內容驗證也是很重要的。

#### 3. 運行 FastAPI 應用

在 `backend` 目錄下，您可以直接使用 Uvicorn 運行應用：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

*   `app.main`: 指向 `app` 目錄下的 `main.py` 模組。
*   `:app`: 指向 `main.py` 模組中的 `FastAPI` 實例變數 `app`。
*   `--reload`: 開啟熱重載，程式碼變更時會自動重啟（開發用）。
*   `--host 0.0.0.0`: 允許從任何 IP 訪問（開發用）。
*   `--port 8000`: 應用程式將在 8000 端口運行。

### 前端：Vue.js

#### 1. 建立 Vue.js 專案

使用 Vue CLI 建立一個新的 Vue 專案。如果您還沒有安裝 Vue CLI，請先安裝：

```bash
npm install -g @vue/cli
# 或者 yarn global add @vue/cli
```

然後在專案根目錄（與 `backend` 同級）建立前端專案：

```bash
cd .. # 回到根目錄
vue create frontend
# 選擇 "Manually select features"，然後選擇 Babel, Router (如果需要多頁面), Linter/Formatter
# 其他選項可以根據提示選擇
cd frontend
npm install # 或者 yarn install
```

#### 2. Vue.js 組件與頁面

**a. `frontend/src/views/HomeView.vue` (或類似的頁面用於上傳和列表)**

```vue
<template>
  <div class="home">
    <h1>靜態資源託管服務</h1>

    <div class="upload-section">
      <h2>上傳檔案</h2>
      <input type="file" @change="handleFileUpload" ref="fileInput" />
      <button @click="uploadFile">上傳</button>
      <p v-if="uploadMessage">{{ uploadMessage }}</p>
    </div>

    <div class="paste-section">
      <h2>貼上內容</h2>
      <textarea v-model="pasteContent" rows="10" cols="50" placeholder="貼上您的 HTML, CSS 或 JS 代碼"></textarea>
      <select v-model="pasteExtension">
        <option value="html">.html (HTML)</option>
        <option value="css">.css (CSS)</option>
        <option value="js">.js (JavaScript)</option>
        <option value="txt">.txt (純文本)</option>
      </select>
      <button @click="pasteText">貼上並發布</button>
      <p v-if="pasteMessage">{{ pasteMessage }}</p>
    </div>

    <div class="list-section">
      <h2>已發布資源列表</h2>
      <button @click="fetchResources">刷新列表</button>
      <ul v-if="resources.length">
        <li v-for="resource in resources" :key="resource.id">
          <strong>{{ resource.original_name || resource.filename }}</strong> ({{ resource.type }})<br />
          <a :href="backendBaseUrl + resource.url" target="_blank">{{ backendBaseUrl + resource.url }}</a>
          <br>
          <small>ID: {{ resource.id }}</small>
        </li>
      </ul>
      <p v-else>目前沒有已發布的資源。</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'HomeView',
  data() {
    return {
      selectedFile: null,
      uploadMessage: '',
      pasteContent: '',
      pasteExtension: 'html',
      pasteMessage: '',
      resources: [],
      backendBaseUrl: 'http://localhost:8000', // FastAPI 後端地址
    };
  },
  mounted() {
    this.fetchResources(); // 組件載入時獲取列表
  },
  methods: {
    handleFileUpload(event) {
      this.selectedFile = event.target.files[0];
    },
    async uploadFile() {
      if (!this.selectedFile) {
        this.uploadMessage = '請選擇一個檔案。';
        return;
      }

      const formData = new FormData();
      formData.append('file', this.selectedFile);

      try {
        const response = await axios.post(`${this.backendBaseUrl}/uploadfile/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        this.uploadMessage = `上傳成功！URL: ${this.backendBaseUrl}${response.data.url}`;
        this.selectedFile = null;
        this.$refs.fileInput.value = ''; // 清空檔案選擇
        this.fetchResources(); // 刷新列表
      } catch (error) {
        console.error('檔案上傳失敗:', error);
        this.uploadMessage = '檔案上傳失敗。';
      }
    },
    async pasteText() {
      if (!this.pasteContent.trim()) {
        this.pasteMessage = '請貼上一些內容。';
        return;
      }

      try {
        const response = await axios.post(`${this.backendBaseUrl}/pastecontent/`, {
          content: this.pasteContent,
          file_extension: this.pasteExtension,
        });
        this.pasteMessage = `內容發布成功！URL: ${this.backendBaseUrl}${response.data.url}`;
        this.pasteContent = ''; // 清空內容
        this.fetchResources(); // 刷新列表
      } catch (error) {
        console.error('內容貼上失敗:', error);
        this.pasteMessage = '內容貼上失敗。';
      }
    },
    async fetchResources() {
      try {
        const response = await axios.get(`${this.backendBaseUrl}/list/`);
        this.resources = response.data.resources;
      } catch (error) {
        console.error('獲取資源列表失敗:', error);
      }
    },
  },
};
</script>

<style scoped>
.home {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

div {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background-color: #f9f9f9;
}

h1, h2 {
  color: #333;
}

button {
  padding: 8px 15px;
  margin-left: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}

input[type="file"], textarea, select {
  display: block;
  margin-top: 10px;
  margin-bottom: 10px;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  width: calc(100% - 20px);
}

textarea {
  resize: vertical;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  background-color: #e9e9e9;
  margin-bottom: 8px;
  padding: 10px;
  border-radius: 4px;
}

li a {
  word-break: break-all; /* 防止 URL 過長溢出 */
}
</style>
```

**b. `frontend/src/main.js`**

確保 Vue 應用程式可以載入 `HomeView`。如果使用 Vue CLI，這通常會自動設置。

```javascript
import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // 如果您使用了 Vue Router

createApp(App).use(router).mount('#app');
```

**c. 安裝 Axios**

在 `frontend` 目錄下安裝 `axios` 用於 HTTP 請求：

```bash
npm install axios
# 或者 yarn add axios
```

#### 3. 運行 Vue.js 前端

在 `frontend` 目錄下運行開發伺服器：

```bash
npm run serve
# 或者 yarn serve
```

這通常會在 `http://localhost:8080` 啟動前端服務。

### 運行與測試

1.  **啟動後端**：
    在 `backend` 目錄下，運行：
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    確保它在 8000 端口運行。

2.  **啟動前端**：
    在 `frontend` 目錄下，運行：
    ```bash
    npm run serve
    ```
    確保它在 8080 端口運行。

3.  **訪問應用**：
    打開瀏覽器訪問 `http://localhost:8080`。您應該能看到上傳和貼上內容的選項，以及已發布的資源列表。

### 後續改進與考慮

*   **持久化儲存**：將 `uploaded_resources` 字典替換為真正的資料庫（如 SQLite 或 PostgreSQL）來儲存資源元數據。
*   **檔案清理**：當資源不再需要時，考慮如何刪除它們及其對應的檔案。
*   **安全**：
    *   **CORS (跨域資源共享)**：如果前端和後端不在同一域或端口，您需要在 FastAPI 中配置 CORS。
    ```python
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI()

    origins = [
        "http://localhost:8080", # 允許前端域
        # "http://your-frontend-domain.com",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    ```    *   **檔案類型驗證**：限制可上傳的檔案類型，防止惡意文件上傳。
    *   **檔案大小限制**：限制上傳檔案的大小。
    *   **防止目錄遍歷**：確保檔案儲存路徑不會被惡意利用。
*   **使用者介面/使用者體驗**：改進前端介面，提供更好的使用者體驗，例如上傳進度條、錯誤提示等。
*   **部署**：將 FastAPI 應用部署到生產環境（例如使用 Gunicorn + Uvicorn，或 Docker）。Vue.js 應用則需要被構建為靜態文件，然後通過 Nginx 或其他服務器提供。
*   **性能**：對於大量檔案，考慮使用雲儲存服務（如 AWS S3, Google Cloud Storage）而不是直接在伺服器本地儲存。
*   **Uvicorn for project management**：您的原始提示中提到 "uvicorn for project management"。需要澄清的是，Uvicorn 是用來運行 ASGI 應用的伺服器。對於 Python 專案管理（依賴管理、虛擬環境等），更推薦使用 `pipenv` 或 `poetry`。
    *   **`pipenv`**：
        ```bash
        pip install pipenv
        cd backend
        pipenv install fastapi uvicorn python-multipart aiofiles
        pipenv shell # 進入虛擬環境
        pipenv run uvicorn app.main:app --reload
        ```
    *   **`poetry`**：
        ```bash
        pip install poetry
        cd backend
        poetry init # 互動式建立 pyproject.toml
        poetry add fastapi uvicorn python-multipart aiofiles
        poetry run uvicorn app.main:app --reload
        ```

這個專案基礎已經涵蓋了您的所有要求，您可以基於此進行進一步的開發和功能擴展。
