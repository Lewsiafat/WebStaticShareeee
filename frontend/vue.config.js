const { defineConfig } = require("@vue/cli-service");
module.exports = defineConfig({
  transpileDependencies: true,
  publicPath: '/webShareee/',
  devServer: {
    port: 8080,
  }
});
