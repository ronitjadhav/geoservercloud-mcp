import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// Project GitHub Pages site is served from /geoservercloud-mcp/
export default defineConfig({
  base: "/geoservercloud-mcp/",
  plugins: [vue()],
});
