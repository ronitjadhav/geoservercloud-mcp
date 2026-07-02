# Docs site

Vue 3 + Vite info site for GeoServer MCP, deployed to GitHub Pages by
`.github/workflows/pages.yaml`. Neobrutalist styling is hand-rolled CSS in
`src/style.css` (design inspired by [neobrutalism.dev](https://www.neobrutalism.dev/)).

```bash
cd app
npm install
npm run dev      # local dev server
npm run build    # production build -> app/dist
```

The site is served under `/geoservercloud-mcp/` (see `base` in `vite.config.js`).
