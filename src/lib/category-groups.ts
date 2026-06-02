export interface CategoryGroup {
  id: string;
  labelKey: string;
  icon: string;
  slugs: string[];
}

export const CATEGORY_GROUPS: CategoryGroup[] = [
  {
    id: "proxy",
    labelKey: "group.proxy",
    icon: "🔌",
    slugs: ["core", "gui", "subscription", "protocol_tools"],
  },
  {
    id: "accel",
    labelKey: "group.accel",
    icon: "🚀",
    slugs: ["github_tools", "router", "mirrors", "tunnel_tools"],
  },
  {
    id: "ops",
    labelKey: "group.ops",
    icon: "🐳",
    slugs: ["docker", "container", "server_mgmt", "node_tools", "monitoring"],
  },
  {
    id: "config",
    labelKey: "group.config",
    icon: "⚙️",
    slugs: ["rules", "dns_tools", "cert_tools"],
  },
  {
    id: "tools",
    labelKey: "group.tools",
    icon: "🧰",
    slugs: ["utilities", "network_test", "data_transfer"],
  },
  {
    id: "security",
    labelKey: "group.security",
    icon: "🛡️",
    slugs: ["security_tools", "collection"],
  },
];

export function getGroupOfSlug(slug: string): CategoryGroup | undefined {
  return CATEGORY_GROUPS.find((g) => g.slugs.includes(slug));
}
