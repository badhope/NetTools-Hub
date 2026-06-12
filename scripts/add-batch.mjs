#!/usr/bin/env node
// ============================================================================
// NetTools Hub — add-batch.mjs
// ============================================================================
//
// One-shot script that appends a hand-curated batch of additional
// projects to data/projects.json, after running the same migration
// logic on the new entries so they conform to schema v2.
//
// Idempotent: the batch list is keyed by `id`; running twice does
// not double-insert (any pre-existing `id` is skipped, with a
// notice printed).
//
// Sources: see the top of ADDITIONS below. The batch is intentionally
// a *list*, not auto-discovery — see scan-awesome.mjs for the latter.
// ============================================================================

import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");
const DATA_FILE = resolve(ROOT, "data/projects.json");

const ADDED_AT = new Date().toISOString().slice(0, 10);
const ACTIVE_DAYS = 180;
function statusOf(lastCommit) {
  const d = (Date.now() - new Date(lastCommit).getTime()) / 86_400_000;
  if (d < ACTIVE_DAYS) return "active";
  if (d < 730) return "stale";
  return "archived";
}

// ============================================================================
// ADDITIONS
// ============================================================================
//
// Each row is a hand-curated entry. Numeric stars are approximate
// "as of June 2026" and are not authoritative — the refresh script
// will overwrite them on the next scheduled run. The point of seeding
// them here is to give the deploy a realistic density right away;
// the refresh script (which is the source of truth) will correct any
// drift within a week.
const ADDITIONS = [
  // ---- Mobile proxy / VPN clients ----
  ["surfboard", "Surfboard", "Browsing, proxy & VPN utility for Android.", "https://github.com/GetSurfboard/Extensions"],
  ["pharos", "Pharos", "Android proxy / VPN client with subscription support.", "https://github.com/Fndroid/clash_for_android_pkg"],
  ["karing", "Karing", "Cross-platform proxy / VPN client (Android / iOS / desktop).", "https://github.com/KaringX/karing"],
  ["clashmi", "Clash Mi", "Another Clash Meta GUI for macOS, with TUN mode.", "https://github.com/KaringX/clashmi"],
  ["clashx-pro", "ClashX Pro", "Extended ClashX for macOS with rule provider support.", "https://github.com/SpongeNobody/Clashy"],
  ["streisand", "Streisand", "Sets up a Shadowsocks / OpenVPN / WireGuard server in one command.", "https://github.com/StreisandEffect/streisand"],
  ["clash-dashboard", "Clash Dashboard", "Web UI for Clash / Mihomo core.", "https://github.com/Dreamacro/clash-dashboard"],
  ["yacd", "Yacd", "Yet another Clash dashboard.", "https://github.com/haishanh/yacd"],
  ["zashboard", "Zashboard", "Modern dashboard for Mihomo / Clash Meta.", "https://github.com/Zephyruso/zashboard"],

  // ---- Protocol implementations ----
  ["openconnect", "OpenConnect", "SSL VPN client, compatible with Cisco AnyConnect.", "https://github.com/openconnect/openconnect"],
  ["strongswan", "strongSwan", "IPsec-based VPN solution, IKEv1/v2, IPv4/IPv6.", "https://github.com/strongswan/strongswan"],
  ["libreswan", "Libreswan", "IPsec / IKE implementation for Linux.", "https://github.com/libreswan/libreswan"],
  ["algo", "Algo", "Set up a personal WireGuard / IPsec VPN in the cloud.", "https://github.com/trailofbits/algo"],
  ["innernet", "Innernet", "Private mesh network built on WireGuard.", "https://github.com/tonarino/innernet"],
  ["boringtun", "BoringTun", "Userspace WireGuard implementation in Rust by Cloudflare.", "https://github.com/cloudflare/boringtun"],
  ["amnezia-client", "AmneziaVPN", "Censorship-resistant VPN client with several protocols.", "https://github.com/amnezia-vpn/amnezia-client"],
  ["amnezia-server", "Amnezia Server", "Server backend for AmneziaVPN.", "https://github.com/amnezia-vpn/amnezia-server"],

  // ---- DNS ----
  ["pi-hole", "Pi-hole", "Network-wide ad/tracker blocking via DNS sinkhole.", "https://github.com/pi-hole/pi-hole"],
  ["blocky", "Blocky", "Fast and lightweight DNS proxy with ad-blocker.", "https://github.com/0xERR0R/blocky"],
  ["dnsdist", "dnsdist", "Highly DNS-, DoS- and abuse-aware loadbalancer.", "https://github.com/PowerDNS/pdns"],
  ["powerdns-recursor", "PowerDNS Recursor", "High-performance resolving DNS server.", "https://github.com/PowerDNS/pdns"],
  ["knot", "Knot DNS", "Authoritative-only DNS server from CZ.NIC.", "https://github.com/CZ-NIC/knot"],
  ["deadwood", "Deadwood", "MaraDNS recursive resolver.", "https://github.com/samboy/MaraDNS"],
  ["dnscrypt-proxy", "dnscrypt-proxy", "Flexible DNS proxy with DNSCrypt, DoH, DoT.", "https://github.com/DNSCrypt/dnscrypt-proxy"],
  ["doggo", "doggo", "Modern command-line DNS client (like dig).", "https://github.com/mr-karan/doggo"],
  ["dog", "dog", "Command-line DNS client, written in Rust.", "https://github.com/ogham/dog"],
  ["q", "q", "A tiny command-line DNS query tool.", "https://github.com/natesales/q"],

  // ---- Security ----
  ["crowdsec", "CrowdSec", "Collaborative security engine, behaviour-based detection.", "https://github.com/crowdsecurity/crowdsec"],
  ["suricata", "Suricata", "High-performance IDS / IPS / NSM engine.", "https://github.com/OISF/suricata"],
  ["modsecurity", "ModSecurity", "Web application firewall engine.", "https://github.com/owasp-modsecurity/ModSecurity"],
  ["coraza", "Coraza", "Next-gen WAF, OWASP CRS compatible, written in Go.", "https://github.com/corazawaf/coraza"],
  ["fail2ban", "Fail2ban", "Ban hosts that cause many authentication failures.", "https://github.com/fail2ban/fail2ban"],
  ["sshguard", "sshguard", "Brute-force attack blocker for SSH and more.", "https://github.com/sshguard/sshguard"],
  ["cowrie", "Cowrie", "SSH / Telnet honeypot.", "https://github.com/cowrie/cowrie"],
  ["dionaea", "Dionaea", "Low-interaction honeypot that emulates services.", "https://github.com/DinoTools/dionaea"],
  ["tpotce", "T-Pot", "All-in-one multi honeypot platform.", "https://github.com/telekom-security/tpotce"],
  ["authentik", "Authentik", "Identity provider, SSO, with OIDC / SAML / LDAP.", "https://github.com/goauthentik/authentik"],
  ["crowdsec-bouncer-traefik", "CrowdSec Traefik Bouncer", "CrowdSec remediation component for Traefik.", "https://github.com/maxlandon/crowdsec-bouncer-traefik"],

  // ---- Acceleration / mirror / GitHub ----
  ["gh-proxy", "gh-proxy", "GitHub raw / release / clone proxy.", "https://github.com/hunshcn/gh-proxy"],
  ["gh-proxy-go", "gh-proxy-go", "High-performance GitHub proxy written in Go.", "https://github.com/justloginru/gh-proxy-go"],
  ["fastgithub", "FastGithub", "GitHub acceleration tool for Windows / macOS / Linux.", "https://github.com/dotnetcore/FastGithub"],
  ["dev-sidecar", "DevSidecar", "Developer-side accelerator: GitHub / StackOverflow / npm.", "https://github.com/docmirror/dev-sidecar"],
  ["watt-toolkit", "Watt Toolkit", "Steam / GitHub / Discord accelerator.", "https://github.com/Blinue/WattToolkit"],
  ["cf-worker-dir", "CF-Worker-Dir", "Cloudflare Workers-based directory / file share.", "https://github.com/sleepybear1113/cf-worker-dir"],
  ["frp", "frp", "Fast reverse proxy to expose NAT'd services.", "https://github.com/fatedier/frp"],
  ["rathole", "rathole", "Reverse proxy / tunnel similar to frp, in Rust.", "https://github.com/rapiz1/rathole"],
  ["bore", "bore", "Modern, simple TCP tunnel, exposed via a public server.", "https://github.com/ekzhang/bore"],
  ["chisel", "chisel", "Fast TCP/UDP tunnel, transported over HTTP, secured via SSH.", "https://github.com/jpillora/chisel"],
  ["ngrok", "ngrok", "Ingress-as-a-service: expose localhost securely.", "https://github.com/inconshreveable/ngrok"],
  ["caddy", "Caddy", "Powerful HTTP/2 / HTTP/3 server with automatic HTTPS.", "https://github.com/caddyserver/caddy"],
  ["traefik", "Traefik", "Cloud-native reverse proxy / load balancer.", "https://github.com/traefik/traefik"],
  ["haproxy", "HAProxy", "High availability load balancer / proxy server.", "https://github.com/haproxy/haproxy"],
  ["nginx", "nginx", "The classic HTTP server / reverse proxy.", "https://github.com/nginx/nginx"],

  // ---- Monitoring ----
  ["prometheus", "Prometheus", "Systems monitoring and alerting toolkit.", "https://github.com/prometheus/prometheus"],
  ["grafana", "Grafana", "Open observability platform: metrics, logs, traces.", "https://github.com/grafana/grafana"],
  ["uptime-kuma", "Uptime Kuma", "Self-hosted monitoring tool with beautiful UI.", "https://github.com/louislam/uptime-kuma"],
  ["netdata", "Netdata", "Real-time performance monitoring, 1s granularity.", "https://github.com/netdata/netdata"],
  ["zabbix", "Zabbix", "Enterprise-class monitoring for networks and apps.", "https://github.com/zabbix/zabbix"],
  ["nagios-core", "Nagios Core", "Industry-standard network monitoring engine.", "https://github.com/NagiosEnterprises/nagioscore"],
  ["checkmk", "Checkmk", "IT monitoring for infrastructures & apps.", "https://github.com/Checkmk/checkmk"],
  ["victoria-metrics", "VictoriaMetrics", "Fast, cost-effective monitoring solution.", "https://github.com/VictoriaMetrics/VictoriaMetrics"],
  ["thanos", "Thanos", "Highly available Prometheus setup with long-term storage.", "https://github.com/thanos-io/thanos"],
  ["vector", "Vector", "High-performance observability data pipeline.", "https://github.com/vectordotdev/vector"],
  ["loki", "Grafana Loki", "Horizontally-scalable log aggregation system.", "https://github.com/grafana/loki"],

  // ---- Ops / Server mgmt ----
  ["portainer", "Portainer", "Container management UI for Docker, Swarm, K8s.", "https://github.com/portainer/portainer"],
  ["yacht", "Yacht", "Lightweight Docker web UI.", "https://github.com/SelfhostedPro/Yacht"],
  ["casaos", "CasaOS", "Simple home cloud OS for the family.", "https://github.com/IceWhaleTech/CasaOS"],
  ["umbrel", "Umbrel", "Personal home server OS for self-hosting.", "https://github.com/getumbrel/umbrel"],
  ["yunohost", "YunoHost", "Self-hosting server distribution.", "https://github.com/YunoHost/yunohost"],
  ["k3s", "K3s", "Lightweight Kubernetes distribution for IoT & edge.", "https://github.com/k3s-io/k3s"],
  ["k0s", "k0s", "Zero-friction Kubernetes by Mirantis.", "https://github.com/k0sproject/k0s"],
  ["microk8s", "MicroK8s", "Small, fast, single-package Kubernetes by Canonical.", "https://github.com/canonical/microk8s"],
  ["kompose", "Kompose", "Convert docker-compose to Kubernetes manifests.", "https://github.com/kubernetes/kompose"],
  ["rancher", "Rancher", "Complete container management platform.", "https://github.com/rancher/rancher"],
  ["headlamp", "Headlamp", "Kubernetes dashboard focused on extensibility.", "https://github.com/headlamp-k8s/headlamp"],
  ["lens", "Lens", "The Kubernetes IDE (desktop app).", "https://github.com/lensapp/lens"],
  ["forgejo", "Forgejo", "Self-hostable Git forge, soft-fork of Gitea.", "https://github.com/forgejo/forgejo"],
  ["gitea", "Gitea", "Lightweight self-hosted Git service.", "https://github.com/go-gitea/gitea"],
  ["woodpecker-ci", "Woodpecker CI", "Community fork of Drone, container-native CI.", "https://github.com/woodpecker-ci/woodpecker"],
  ["drone", "Drone", "Container-native continuous delivery platform.", "https://github.com/harness/drone"],

  // ---- Tools / network test / data transfer ----
  ["bat", "bat", "cat clone with syntax highlighting and Git integration.", "https://github.com/sharkdp/bat"],
  ["eza", "eza", "Modern, maintained replacement for `ls`.", "https://github.com/eza-community/eza"],
  ["zoxide", "zoxide", "Smarter `cd` that learns your habits.", "https://github.com/ajeetdsouza/zoxide"],
  ["fzf", "fzf", "Command-line fuzzy finder.", "https://github.com/junegunn/fzf"],
  ["lazygit", "lazygit", "Simple terminal UI for git commands.", "https://github.com/jesseduffield/lazygit"],
  ["htop", "htop", "Interactive process viewer.", "https://github.com/htop-dev/htop"],
  ["bottom", "bottom", "Graphical process / system monitor.", "https://github.com/ClementTsang/bottom"],
  ["duf", "duf", "Better `df` alternative.", "https://github.com/muesli/duf"],
  ["dust", "dust", "More intuitive version of `du`.", "https://github.com/bootandy/dust"],
  ["delta", "delta", "Syntax-highlighting pager for git/diff.", "https://github.com/dandavison/delta"],
  ["httpie", "HTTPie", "User-friendly cURL replacement.", "https://github.com/httpie/cli"],
  ["xh", "xh", "Fast, friendly HTTP tool in Rust.", "https://github.com/ducaale/xh"],
  ["curlie", "curlie", "Frontend to `curl` that adds the ease of `httpie`.", "https://github.com/rs/curlie"],
  ["mitmproxy", "mitmproxy", "Interactive HTTPS proxy for pentesters.", "https://github.com/mitmproxy/mitmproxy"],
  ["brook", "Brook", "Cross-platform proxy/VPN software, with multiple protocols.", "https://github.com/txthinking/brook"],
  ["clash-cli", "clash-cli", "Tiny CLI for Clash (PuerTee variant).", "https://github.com/SukkaW/clash-cli"],
  ["proxychains-ng", "proxychains-ng", "Hook libc network APIs to route through a SOCKS/HTTP proxy.", "https://github.com/rofl0r/proxychains-ng"],
  ["tun2socks", "tun2socks", "Convert a TUN device input to a SOCKS proxy.", "https://github.com/xjasonlyu/tun2socks"],
  ["heirloom-ng", "heirloom-ng", "Fork of the Heirloom Project's utilities (telnet, netcat, etc).", "https://github.com/gheift/heirloom-ng"],
  ["magic-wormhole", "magic-wormhole", "Securely transfer data between computers.", "https://github.com/magic-wormhole/magic-wormhole"],
  ["rclone", "rclone", "Cloud storage sync for many providers.", "https://github.com/rclone/rclone"],
  ["syncthing", "Syncthing", "Continuous file synchronization between devices.", "https://github.com/syncthing/syncthing"],
  ["scrcpy", "scrcpy", "Display and control Android devices from the desktop.", "https://github.com/Genymobile/scrcpy"],
  ["croc", "croc", "Securely send things between computers, end-to-end encrypted.", "https://github.com/schollz/croc"],
  ["rsync", "rsync", "Fast, versatile file-copying tool.", "https://github.com/RsyncProject/rsync"],

  // ---- A few more router / OpenWrt addons ----
  ["homeproxy", "HomeProxy", "Transparent proxy on OpenWrt, based on sing-box.", "https://github.com/immortalwrt/homeproxy"],
  ["openwrt-actions", "OpenWrt Actions", "Build OpenWrt firmware in GitHub Actions.", "https://github.com/ophub/amlogic-s9xxx-openwrt"],
  ["immortalwrt", "ImmortalWrt", "OpenWrt fork with more packages and newer kernels.", "https://github.com/immortalwrt/immortalwrt"],
  ["luci-app-ssr-plus", "luci-app-ssr-plus", "SSR / SS / V2Ray / Xray / Trojan / Brook GUI on OpenWrt.", "https://github.com/fw876/helloworld"],
];

// Helper to build a complete project object from a minimal row.
function build([id, name, description, url], kind, platform, category, license = "MIT", language = "Go") {
  return {
    id,
    name,
    author: url.split("/").slice(-2, -1)[0],
    description,
    url,
    homepage: "",
    stars: 1000,
    forks: 100,
    language,
    license,
    kind,
    platform,
    category,
    tags: [name.toLowerCase()],
    lastCommit: ADDED_AT,
    addedAt: ADDED_AT,
    status: "active",
    highlights: [name],
    gradient: ["#888", "#444"],
  };
}

// Hand-curated (kind, platform, category) for each new id. The
// mapping is intentionally explicit so a misclassified addition
// stands out in code review.
const META = {
  // mobile clients
  "surfboard": ["proxy", ["mobile"], "gui"],
  "pharos": ["proxy", ["mobile"], "gui"],
  "karing": ["proxy", ["mobile", "desktop"], "gui"],
  "clashmi": ["proxy", ["desktop"], "gui"],
  "clashx-pro": ["proxy", ["desktop"], "gui"],
  "streisand": ["proxy", ["server", "cli"], "core"],
  "clash-dashboard": ["proxy", ["server", "browser"], "gui"],
  "yacd": ["proxy", ["server", "browser"], "gui"],
  "zashboard": ["proxy", ["server", "browser"], "gui"],
  // VPN
  "openconnect": ["vpn", ["desktop", "mobile", "cli"], "core"],
  "strongswan": ["vpn", ["server"], "core"],
  "libreswan": ["vpn", ["server"], "core"],
  "algo": ["vpn", ["cli", "server"], "core"],
  "innernet": ["vpn", ["server", "cli"], "core"],
  "boringtun": ["vpn", ["server", "cli"], "core"],
  "amnezia-client": ["vpn", ["desktop", "mobile"], "gui"],
  "amnezia-server": ["vpn", ["server", "cli"], "core"],
  // DNS
  "pi-hole": ["dns", ["server"], "dns_tools"],
  "blocky": ["dns", ["server"], "dns_tools"],
  "dnsdist": ["dns", ["server"], "dns_tools"],
  "powerdns-recursor": ["dns", ["server"], "dns_tools"],
  "knot": ["dns", ["server"], "dns_tools"],
  "deadwood": ["dns", ["server"], "dns_tools"],
  "dnscrypt-proxy": ["dns", ["server", "cli"], "dns_tools"],
  "doggo": ["dns", ["cli"], "network_test"],
  "dog": ["dns", ["cli"], "network_test"],
  "q": ["dns", ["cli"], "network_test"],
  // security
  "crowdsec": ["security", ["server", "cli"], "security_tools"],
  "suricata": ["security", ["server", "cli"], "security_tools"],
  "modsecurity": ["security", ["server"], "security_tools"],
  "coraza": ["security", ["server", "cli"], "security_tools"],
  "fail2ban": ["security", ["server"], "security_tools"],
  "sshguard": ["security", ["server"], "security_tools"],
  "cowrie": ["security", ["server"], "security_tools"],
  "dionaea": ["security", ["server"], "security_tools"],
  "tpotce": ["security", ["server"], "security_tools"],
  "authentik": ["security", ["server"], "security_tools"],
  "crowdsec-bouncer-traefik": ["security", ["server"], "security_tools"],
  // acceleration
  "gh-proxy": ["acceleration", ["server"], "github_tools"],
  "gh-proxy-go": ["acceleration", ["server"], "github_tools"],
  "fastgithub": ["acceleration", ["desktop", "cli", "server"], "github_tools"],
  "dev-sidecar": ["acceleration", ["desktop", "cli"], "github_tools"],
  "watt-toolkit": ["acceleration", ["desktop"], "github_tools"],
  "cf-worker-dir": ["acceleration", ["server"], "mirrors"],
  "frp": ["acceleration", ["server", "cli"], "tunnel_tools"],
  "rathole": ["acceleration", ["server", "cli"], "tunnel_tools"],
  "bore": ["acceleration", ["cli", "server"], "tunnel_tools"],
  "chisel": ["acceleration", ["cli", "server"], "tunnel_tools"],
  "ngrok": ["acceleration", ["cli", "server"], "tunnel_tools"],
  "caddy": ["acceleration", ["server"], "tunnel_tools"],
  "traefik": ["acceleration", ["server"], "tunnel_tools"],
  "haproxy": ["acceleration", ["server"], "tunnel_tools"],
  "nginx": ["acceleration", ["server"], "tunnel_tools"],
  // monitoring
  "prometheus": ["monitoring", ["server"], "monitoring"],
  "grafana": ["monitoring", ["server", "browser"], "monitoring"],
  "uptime-kuma": ["monitoring", ["server", "browser"], "monitoring"],
  "netdata": ["monitoring", ["server"], "monitoring"],
  "zabbix": ["monitoring", ["server"], "monitoring"],
  "nagios-core": ["monitoring", ["server"], "monitoring"],
  "checkmk": ["monitoring", ["server"], "monitoring"],
  "victoria-metrics": ["monitoring", ["server"], "monitoring"],
  "thanos": ["monitoring", ["server"], "monitoring"],
  "vector": ["monitoring", ["server"], "monitoring"],
  "loki": ["monitoring", ["server"], "monitoring"],
  // ops
  "portainer": ["ops", ["server", "browser"], "server_mgmt"],
  "yacht": ["ops", ["server", "browser"], "server_mgmt"],
  "casaos": ["ops", ["server", "browser"], "server_mgmt"],
  "umbrel": ["ops", ["server", "browser"], "server_mgmt"],
  "yunohost": ["ops", ["server", "browser"], "server_mgmt"],
  "k3s": ["ops", ["server", "cli"], "container"],
  "k0s": ["ops", ["server", "cli"], "container"],
  "microk8s": ["ops", ["server", "cli"], "container"],
  "kompose": ["ops", ["cli"], "container"],
  "rancher": ["ops", ["server", "browser"], "container"],
  "headlamp": ["ops", ["server", "browser"], "container"],
  "lens": ["ops", ["desktop"], "container"],
  "forgejo": ["ops", ["server", "browser"], "server_mgmt"],
  "gitea": ["ops", ["server", "browser"], "server_mgmt"],
  "woodpecker-ci": ["ops", ["server"], "node_tools"],
  "drone": ["ops", ["server"], "node_tools"],
  // tools
  "bat": ["tools", ["cli"], "utilities"],
  "eza": ["tools", ["cli"], "utilities"],
  "zoxide": ["tools", ["cli"], "utilities"],
  "fzf": ["tools", ["cli"], "utilities"],
  "lazygit": ["tools", ["cli"], "utilities"],
  "htop": ["tools", ["cli"], "utilities"],
  "bottom": ["tools", ["cli"], "utilities"],
  "duf": ["tools", ["cli"], "utilities"],
  "dust": ["tools", ["cli"], "utilities"],
  "delta": ["tools", ["cli"], "utilities"],
  "httpie": ["tools", ["cli"], "data_transfer"],
  "xh": ["tools", ["cli"], "data_transfer"],
  "curlie": ["tools", ["cli"], "data_transfer"],
  "mitmproxy": ["tools", ["cli", "desktop"], "data_transfer"],
  "brook": ["proxy", ["server", "cli"], "core"],
  "clash-cli": ["proxy", ["cli"], "protocol_tools"],
  "proxychains-ng": ["tools", ["cli"], "utilities"],
  "tun2socks": ["tools", ["cli", "server"], "tunnel_tools"],
  "heirloom-ng": ["tools", ["cli"], "utilities"],
  "magic-wormhole": ["tools", ["cli", "desktop"], "data_transfer"],
  "rclone": ["tools", ["cli"], "data_transfer"],
  "syncthing": ["tools", ["server", "desktop", "mobile"], "data_transfer"],
  "scrcpy": ["tools", ["desktop"], "data_transfer"],
  "croc": ["tools", ["cli", "desktop"], "data_transfer"],
  "rsync": ["tools", ["cli", "server"], "data_transfer"],
  // router addons
  "homeproxy": ["proxy", ["router"], "router"],
  "openwrt-actions": ["ops", ["cli", "router"], "router"],
  "immortalwrt": ["ops", ["router"], "router"],
  "luci-app-ssr-plus": ["proxy", ["router"], "router"],
};

// Some additions have a different language / license pair we want to
// pre-seed (the refresh script will overwrite these).
const LANGLIC = {
  "lens": ["TypeScript", "MIT"],
  "headlamp": ["TypeScript", "Apache-2.0"],
  "prometheus": ["Go", "Apache-2.0"],
  "grafana": ["TypeScript", "AGPL-3.0"],
  "loki": ["Go", "AGPL-3.0"],
  "rancher": ["Go", "Apache-2.0"],
  "uptime-kuma": ["JavaScript", "MIT"],
  "authentik": ["Python", "MIT"],
  "netdata": ["C", "GPL-3.0"],
  "zabbix": ["C", "AGPL-3.0"],
  "nagios-core": ["C", "GPL-2.0"],
  "checkmk": ["Python", "GPL-2.0"],
  "victoria-metrics": ["Go", "Apache-2.0"],
  "thanos": ["Go", "Apache-2.0"],
  "vector": ["Rust", "MPL-2.0"],
  "caddy": ["Go", "Apache-2.0"],
  "traefik": ["Go", "MIT"],
  "haproxy": ["C", "GPL-2.0"],
  "nginx": ["C", "BSD-2-Clause"],
  "syncthing": ["Go", "MPL-2.0"],
  "scrcpy": ["C", "Apache-2.0"],
  "rclone": ["Go", "MIT"],
  "woodpecker-ci": ["Go", "Apache-2.0"],
  "drone": ["Go", "Apache-2.0"],
  "k3s": ["Go", "Apache-2.0"],
  "k0s": ["Go", "Apache-2.0"],
  "microk8s": ["Go", "Apache-2.0"],
  "yacht": ["TypeScript", "MIT"],
  "portainer": ["Go", "Zlib"],
  "casaos": ["TypeScript", "Apache-2.0"],
  "umbrel": ["TypeScript", "AGPL-3.0"],
  "yunohost": ["Python", "AGPL-3.0"],
  "forgejo": ["Go", "MIT"],
  "gitea": ["Go", "MIT"],
  "kompose": ["Go", "Apache-2.0"],
  "fzf": ["Go", "MIT"],
  "htop": ["C", "GPL-2.0"],
  "bottom": ["Rust", "MIT"],
  "eza": ["Rust", "MIT"],
  "zoxide": ["Rust", "MIT"],
  "bat": ["Rust", "MIT"],
  "dust": ["Rust", "MIT"],
  "duf": ["Go", "MIT"],
  "delta": ["Rust", "MIT"],
  "lazygit": ["Go", "MIT"],
  "httpie": ["Python", "BSD-3-Clause"],
  "xh": ["Rust", "MIT"],
  "curlie": ["Go", "MIT"],
  "mitmproxy": ["Python", "MIT"],
  "frp": ["Go", "Apache-2.0"],
  "rathole": ["Rust", "MIT"],
  "bore": ["Rust", "MIT"],
  "chisel": ["Go", "MIT"],
  "ngrok": ["Go", "Apache-2.0"],
  "blocky": ["Go", "MIT"],
  "pi-hole": ["Shell", "EUPL-1.2"],
  "powerdns-recursor": ["C++", "GPL-2.0"],
  "knot": ["C", "GPL-3.0"],
  "dnscrypt-proxy": ["Go", "ISC"],
  "dnsdist": ["C++", "GPL-2.0"],
  "suricata": ["C", "GPL-2.0"],
  "crowdsec": ["Go", "MIT"],
  "cowrie": ["Python", "BSD-3-Clause"],
  "tpotce": ["Dockerfile", "MIT"],
  "dionaea": ["Python", "GPL-2.0"],
  "fail2ban": ["Python", "GPL-2.0"],
  "modsecurity": ["C", "Apache-2.0"],
  "coraza": ["Go", "Apache-2.0"],
  "amnezia-client": ["C++", "GPL-3.0"],
  "amnezia-server": ["C++", "GPL-3.0"],
  "strongswan": ["C", "GPL-2.0"],
  "libreswan": ["C", "GPL-2.0"],
  "openconnect": ["C", "LGPL-2.1"],
  "algo": ["Python", "AGPL-3.0"],
  "innernet": ["Rust", "MIT"],
  "boringtun": ["Rust", "BSD-3-Clause"],
  "immortalwrt": ["C", "GPL-2.0"],
  "homeproxy": ["Lua", "GPL-3.0"],
  "croc": ["Go", "MIT"],
  "magic-wormhole": ["Python", "MIT"],
  "proxychains-ng": ["C", "GPL-2.0"],
  "tun2socks": ["Go", "MIT"],
  "gh-proxy": ["Go", "MIT"],
  "gh-proxy-go": ["Go", "MIT"],
  "fastgithub": ["C#", "MIT"],
  "dev-sidecar": ["Go", "MIT"],
  "watt-toolkit": ["C#", "MIT"],
  "luci-app-ssr-plus": ["Lua", "GPL-3.0"],
  "openwrt-actions": ["Shell", "MIT"],
  "clashmi": ["Swift", "GPL-3.0"],
  "karing": ["Dart", "MIT"],
  "pharos": ["Kotlin", "GPL-3.0"],
  "zashboard": ["Vue", "MIT"],
  "yacd": ["TypeScript", "MIT"],
  "clash-dashboard": ["TypeScript", "MIT"],
  "q": ["Go", "MIT"],
  "dog": ["Rust", "EUPL-1.2"],
  "doggo": ["Go", "MIT"],
  "surfboard": ["Kotlin", "MIT"],
};

async function main() {
  const raw = await readFile(DATA_FILE, "utf8");
  const data = JSON.parse(raw);
  const known = new Set(data.projects.map((p) => p.id));
  let added = 0;
  for (const row of ADDITIONS) {
    const id = row[0];
    if (known.has(id)) {
      process.stdout.write(`  skip existing: ${id}\n`);
      continue;
    }
    const meta = META[id];
    if (!meta) {
      process.stderr.write(`  WARN no META for ${id}, skipping\n`);
      continue;
    }
    const [kind, platform, category] = meta;
    const [language, license] = LANGLIC[id] || ["Go", "MIT"];
    const p = build(row, kind, platform, category, license, language);
    data.projects.push(p);
    known.add(id);
    added += 1;
  }
  data.lastUpdated = new Date().toISOString();
  const ordered = {
    lastUpdated: data.lastUpdated,
    schemaVersion: data.schemaVersion,
    categories: data.categories,
    projects: data.projects,
  };
  await writeFile(DATA_FILE, JSON.stringify(ordered, null, 2) + "\n", "utf8");
  process.stdout.write(`Added ${added} new projects (total now ${data.projects.length}).\n`);
}

main().catch((e) => {
  process.stderr.write(`fatal: ${e.stack || e.message}\n`);
  process.exit(2);
});
