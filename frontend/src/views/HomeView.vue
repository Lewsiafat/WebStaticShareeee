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