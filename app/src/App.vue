<script setup>
import { ref } from "vue";

const GITHUB = "https://github.com/ronitjadhav/geoservercloud-mcp";
const PYPI = "https://pypi.org/project/geoservercloud-mcp/";
const REGISTRY =
  "https://registry.modelcontextprotocol.io/?q=geoservercloud-mcp";

const features = [
  {
    icon: "🗂️",
    title: "Workspaces",
    text: "Create, list, and manage workspaces.",
  },
  {
    icon: "🗄️",
    title: "Datastores",
    text: "PostGIS, JNDI, PMTiles, and generic stores.",
  },
  {
    icon: "🧬",
    title: "Layers & Feature Types",
    text: "Publish and manage vector layers.",
  },
  {
    icon: "🛰️",
    title: "Coverage & Raster",
    text: "Coverage stores and ImageMosaic granules.",
  },
  {
    icon: "🎨",
    title: "Styles",
    text: "Upload and assign SLD & MBStyle styles.",
  },
  {
    icon: "🔗",
    title: "WMS / WMTS Cascading",
    text: "Proxy external OGC services as layers.",
  },
  {
    icon: "🧩",
    title: "Layer Groups",
    text: "Compose and manage grouped layers.",
  },
  {
    icon: "🔒",
    title: "Security & ACL",
    text: "Users, roles, and access-control rules.",
  },
  { icon: "⚡", title: "GeoWebCache", text: "Manage tile caching for layers." },
];

const tabs = [
  {
    key: "claude-code",
    label: "Claude Code",
    code: `claude mcp add geoserver \\\n  --env GEOSERVER_URL=http://localhost:8080/geoserver \\\n  --env GEOSERVER_USER=admin \\\n  --env GEOSERVER_PASSWORD=geoserver \\\n  -- uvx geoservercloud-mcp`,
  },
  {
    key: "desktop",
    label: "Claude Desktop / VS Code",
    code: `{
  "mcpServers": {
    "geoserver": {
      "command": "uvx",
      "args": ["geoservercloud-mcp"],
      "env": {
        "GEOSERVER_URL": "http://localhost:8080/geoserver",
        "GEOSERVER_USER": "admin",
        "GEOSERVER_PASSWORD": "geoserver"
      }
    }
  }
}`,
  },
  {
    key: "uvx",
    label: "uvx",
    code: `# run without installing (needs uv)\nuvx geoservercloud-mcp`,
  },
  {
    key: "pip",
    label: "pip",
    code: `pip install geoservercloud-mcp\ngeoservercloud-mcp`,
  },
];
const active = ref("claude-code");

const prompts = [
  "List all workspaces in GeoServer",
  "Create a new workspace called 'test_data'",
  "What layers are available in the 'topp' workspace?",
  "Create a PostGIS datastore connection",
  "Upload this SLD and set it as the default style for the roads layer",
  "Cascade the WMS service at example.com into a new layer",
];

const installCmd = "claude mcp add geoserver -- uvx geoservercloud-mcp";
const copied = ref(false);
function copyInstall() {
  navigator.clipboard?.writeText(installCmd).then(() => {
    copied.value = true;
    setTimeout(() => (copied.value = false), 1500);
  });
}
</script>

<template>
  <header class="nav" id="top">
    <div class="nav-inner">
      <a class="brand" href="#top">
        <img
          class="brand-logo"
          src="/geoservercloud-mcp.png"
          alt="GeoServer MCP"
        />
      </a>
      <nav class="nav-links">
        <a :href="GITHUB" target="_blank" rel="noopener">GitHub</a>
        <a :href="PYPI" target="_blank" rel="noopener">PyPI</a>
        <a :href="REGISTRY" target="_blank" rel="noopener">MCP Registry</a>
      </nav>
    </div>
  </header>

  <main class="wrap">
    <!-- HERO -->
    <section class="hero">
      <div class="hero-copy">
        <span class="eyebrow rise" style="--d: 0s">
          <span class="pulse"></span> GeoServer × Model Context Protocol
        </span>
        <h1 class="rise" style="--d: 0.05s">
          Talk to <span class="hl">GeoServer</span>.
        </h1>
        <p class="lead rise" style="--d: 0.1s">
          An MCP server that lets AI assistants like Claude manage GeoServer
          workspaces, datastores, layers, and styles — 70+ REST operations
          exposed as natural-language tools.
        </p>

        <div class="cmd rise" style="--d: 0.15s">
          <code>{{ installCmd }}</code>
          <button @click="copyInstall">
            {{ copied ? "✓ copied" : "copy" }}
          </button>
        </div>

        <div class="cta-row rise" style="--d: 0.2s">
          <a class="neo-btn" :href="GITHUB" target="_blank" rel="noopener"
            >★ Star on GitHub</a
          >
          <a class="neo-btn alt" :href="PYPI" target="_blank" rel="noopener"
            >Install from PyPI</a
          >
        </div>

        <div class="tags rise" style="--d: 0.25s">
          <span class="t">Python</span>
          <span class="t">FastMCP</span>
          <span class="t">GeoServer</span>
          <span class="t">REST API</span>
          <span class="t">Docker</span>
        </div>
      </div>

      <div class="hero-visual rise" style="--d: 0.15s">
        <div class="chatwin">
          <div class="chat-head">
            <span class="dot r"></span>
            <span class="dot y"></span>
            <span class="dot g"></span>
            <img
              class="chat-logo"
              src="/geoservercloud-mcp.png"
              alt="GeoServer MCP"
            />
          </div>
          <div class="chat-body">
            <div class="msg user">
              Create a workspace called <b>demo</b> and connect our PostGIS
              database.
            </div>
            <div class="msg bot">
              <span class="who">GeoServer MCP</span>
              On it — ran two tools:
              <div class="tool">✓ create_workspace <span>demo</span></div>
              <div class="tool">
                ✓ create_pg_datastore <span>demo · main</span>
              </div>
            </div>
            <div class="msg user">Now publish the <b>roads</b> table.</div>
            <div class="msg bot">
              <span class="who">GeoServer MCP</span>
              <div class="tool">
                ✓ create_feature_type <span>demo:roads</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- PROMPTS -->
    <section>
      <h2>Just ask</h2>
      <div class="prompts">
        <div v-for="p in prompts" :key="p" class="neo-card prompt">
          {{ p }}
        </div>
      </div>
    </section>

    <!-- QUICK START -->
    <section>
      <h2>Quick start</h2>
      <div class="tabbar">
        <button
          v-for="t in tabs"
          :key="t.key"
          :class="{ on: active === t.key }"
          @click="active = t.key"
        >
          {{ t.label }}
        </button>
      </div>
      <pre
        class="code"
      ><code>{{ tabs.find((t) => t.key === active).code }}</code></pre>
    </section>

    <!-- FEATURES -->
    <section>
      <h2>Everything GeoServer, as tools</h2>
      <div class="grid">
        <div v-for="f in features" :key="f.title" class="neo-card feature">
          <div
            class="ico"
            :style="{
              background: [
                'var(--yellow)',
                'var(--cyan)',
                'var(--pink)',
                'var(--lime)',
                'var(--orange)',
                'var(--purple)',
              ][features.indexOf(f) % 6],
            }"
          >
            {{ f.icon }}
          </div>
          <h3>{{ f.title }}</h3>
          <p>{{ f.text }}</p>
        </div>
      </div>
    </section>
  </main>

  <footer>
    <div class="wrap foot-inner">
      <span>Built on the python-geoservercloud library · BSD-2-Clause</span>
      <span>
        <a :href="GITHUB" target="_blank" rel="noopener">GitHub</a> ·
        <a :href="PYPI" target="_blank" rel="noopener">PyPI</a> ·
        <a :href="REGISTRY" target="_blank" rel="noopener">MCP Registry</a>
      </span>
    </div>
  </footer>
</template>
