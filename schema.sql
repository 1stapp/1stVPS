-- 1stVPS Cloudflare D1 Database Schema

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  avatar_url TEXT,
  google_id TEXT UNIQUE,
  role TEXT NOT NULL DEFAULT 'customer', -- 'customer' | 'admin'
  affiliate_code TEXT UNIQUE NOT NULL,
  referred_by TEXT,
  balance_cents INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS nodes (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  ovh_service_name TEXT UNIQUE NOT NULL,
  datacenter TEXT NOT NULL, -- RBX, GRA, BHS, SGP
  pve_host TEXT NOT NULL,   -- https://pve-rbx-01.1stvps.example.com:8006
  pve_node TEXT NOT NULL,
  cpu_model TEXT NOT NULL,
  total_vcpu INTEGER NOT NULL,
  used_vcpu INTEGER NOT NULL DEFAULT 0,
  total_ram_gb INTEGER NOT NULL,
  used_ram_gb INTEGER NOT NULL DEFAULT 0,
  total_nvme_gb INTEGER NOT NULL,
  used_nvme_gb INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'online',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ip_pool (
  ip TEXT PRIMARY KEY,
  cidr TEXT NOT NULL,
  gateway TEXT NOT NULL,
  node_id TEXT NOT NULL REFERENCES nodes(id),
  assigned_vm_id TEXT,
  status TEXT NOT NULL DEFAULT 'free' -- 'free' | 'assigned' | 'reserved'
);

CREATE TABLE IF NOT EXISTS vps_plans (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  vcpu INTEGER NOT NULL,
  ram_gb INTEGER NOT NULL,
  nvme_gb INTEGER NOT NULL,
  bandwidth_tb INTEGER NOT NULL,
  price_cents INTEGER NOT NULL,
  stripe_price_id TEXT
);

CREATE TABLE IF NOT EXISTS vps_instances (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id),
  node_id TEXT NOT NULL REFERENCES nodes(id),
  plan_id TEXT NOT NULL REFERENCES vps_plans(id),
  vmid INTEGER NOT NULL,
  hostname TEXT NOT NULL,
  os_template TEXT NOT NULL,
  ipv4 TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'provisioning', -- 'provisioning' | 'running' | 'stopped' | 'error'
  root_password_enc TEXT,
  expires_at TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id),
  plan_id TEXT NOT NULL REFERENCES vps_plans(id),
  stripe_session_id TEXT UNIQUE,
  amount_cents INTEGER NOT NULL,
  currency TEXT NOT NULL DEFAULT 'usd',
  affiliate_code TEXT,
  status TEXT NOT NULL DEFAULT 'pending', -- 'pending' | 'paid' | 'provisioned' | 'refunded'
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS commissions (
  id TEXT PRIMARY KEY,
  affiliate_user_id TEXT NOT NULL REFERENCES users(id),
  order_id TEXT NOT NULL REFERENCES orders(id),
  referred_user_id TEXT NOT NULL REFERENCES users(id),
  amount_cents INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'available', -- 'pending' | 'available' | 'converted' | 'paid_out'
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS messages (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id),
  category TEXT NOT NULL DEFAULT 'system', -- 'system' | 'billing' | 'affiliate'
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  is_read INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS chat_tickets (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id),
  subject TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'open', -- 'open' | 'answered' | 'closed'
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS push_subscriptions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id),
  endpoint TEXT UNIQUE NOT NULL,
  p256dh TEXT NOT NULL,
  auth TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS email_campaigns (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  subject TEXT NOT NULL,
  segment TEXT NOT NULL DEFAULT 'all', -- 'all' | 'active_vps' | 'affiliates'
  html_content TEXT NOT NULL,
  sent_count INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'draft', -- 'draft' | 'queued' | 'sent'
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ========================================================
-- 默认种子数据 (Default Seed Data)
-- ========================================================

-- 1. VPS 套餐规格 (vCPU / RAM / NVMe / Bandwidth / Price)
INSERT OR IGNORE INTO vps_plans (id, name, vcpu, ram_gb, nvme_gb, bandwidth_tb, price_cents, stripe_price_id) VALUES
  ('starter', 'KVM Starter', 2, 4, 40, 2, 600, 'price_starter_monthly'),
  ('pro', 'KVM Pro', 4, 8, 80, 5, 1400, 'price_pro_monthly'),
  ('compute', 'KVM Compute', 8, 16, 160, 10, 2800, 'price_compute_monthly'),
  ('extreme', 'KVM Extreme', 16, 32, 320, 20, 5600, 'price_extreme_monthly');

-- 2. OVHcloud 裸金属母机节点 (已重装 Proxmox VE 8)
INSERT OR IGNORE INTO nodes (id, name, ovh_service_name, datacenter, pve_host, pve_node, cpu_model, total_vcpu, used_vcpu, total_ram_gb, used_ram_gb, total_nvme_gb, used_nvme_gb, status) VALUES
  ('node_rbx_01', 'rbx-bm-01', 'ns3198412.ip-51-89-10.eu', 'RBX', 'https://pve-rbx-01.1stvps.internal:8006', 'pve-rbx-01', 'AMD EPYC 7443P (24C/48T)', 96, 42, 256, 112, 3840, 1480, 'online'),
  ('node_gra_02', 'gra-bm-02', 'ns3284910.ip-141-94-22.eu', 'GRA', 'https://pve-gra-02.1stvps.internal:8006', 'pve-gra-02', 'Intel Xeon Gold 6338 (32C/64T)', 128, 64, 512, 224, 7680, 2960, 'online'),
  ('node_sgp_03', 'sgp-bm-03', 'ns5091231.ip-51-79-144.net', 'SGP', 'https://pve-sgp-03.1stvps.internal:8006', 'pve-sgp-03', 'AMD EPYC 9354P (32C/64T)', 128, 36, 384, 96, 3840, 880, 'online'),
  ('node_bhs_04', 'bhs-bm-04', 'ns6012894.ip-198-27-80.net', 'BHS', 'https://pve-bhs-04.1stvps.internal:8006', 'pve-bhs-04', 'AMD EPYC 7763 (64C/128T)', 192, 48, 512, 128, 7680, 1920, 'online');

-- 3. OVH vRack 公网 IPv4 地址池
INSERT OR IGNORE INTO ip_pool (ip, cidr, gateway, node_id, status) VALUES
  ('51.79.144.17', '51.79.144.17/28', '51.79.144.30', 'node_sgp_03', 'assigned'),
  ('51.79.144.18', '51.79.144.18/28', '51.79.144.30', 'node_sgp_03', 'assigned'),
  ('51.79.144.19', '51.79.144.19/28', '51.79.144.30', 'node_sgp_03', 'free'),
  ('51.79.144.20', '51.79.144.20/28', '51.79.144.30', 'node_sgp_03', 'free'),
  ('51.79.144.21', '51.79.144.21/28', '51.79.144.30', 'node_sgp_03', 'free'),
  ('51.89.10.33', '51.89.10.33/28', '51.89.10.46', 'node_rbx_01', 'assigned'),
  ('51.89.10.34', '51.89.10.34/28', '51.89.10.46', 'node_rbx_01', 'free'),
  ('51.89.10.35', '51.89.10.35/28', '51.89.10.46', 'node_rbx_01', 'free'),
  ('141.94.22.65', '141.94.22.65/28', '141.94.22.78', 'node_gra_02', 'assigned'),
  ('141.94.22.66', '141.94.22.66/28', '141.94.22.78', 'node_gra_02', 'free');

-- 4. （已移除演示种子用户：生产环境不得预置任何演示/管理员账号，客户通过 Google OAuth 注册，管理员通过 ADMIN_PASSWORD 登录）

