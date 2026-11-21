# 1stVPS — 基于 OVHcloud 裸金属虚拟化与 Cloudflare 全栈的自动化云主机销售系统

面向商业化运营的下一代 VPS 自动化销售与管理平台。前端与控制面**100% 运行在 Cloudflare 边缘网络**（Workers + D1 + KV + Queues + Durable Objects + Static Assets），后端通过标准化 API 纳管 **OVHcloud 裸金属母机**与 **Proxmox VE (KVM)** 虚拟化集群，实现从客户下单、Stripe 支付、即时排队开通、网络与 IP 配置、电源控制、工单客服到推广返佣的全链路无人值守自动化。

---

## 🌟 核心业务架构与商业模型

```
                                      ┌────────────────────────────────────────────────────────┐
                                      │             Cloudflare Edge Control Plane              │
                                      │  ┌──────────────────────┐   ┌───────────────────────┐  │
                                      │  │  Hono Workers API    │   │  Cloudflare D1 (SQL)  │  │
                                      │  │  · Google OAuth 2.0  │   │  · Nodes & Subnets    │  │
                                      │  │  · Stripe Webhooks   │   │  · VPS & IP Pool      │  │
                                      │  │  · Affiliate Ledger  │   │  · Orders & Messages  │  │
                                      │  └──────────┬───────────┘   └───────────▲───────────┘  │
                                      │             │                           │              │
                                      │             ▼                           │              │
                                      │  ┌──────────────────────┐               │              │
                                      │  │  Cloudflare Queues   │───────────────┘              │
                                      │  │  (Async Provisioner) │                              │
                                      │  └──────────┬───────────┘   ┌───────────────────────┐  │
                                      │             │               │ Durable Objects (WS)  │  │
                                      │             │               │ · Live Support Chat   │  │
                                      │             │               └───────────────────────┘  │
                                      └─────────────┼──────────────────────────────────────────┘
                                                    │ Secure HTTPS / Cloudflare Tunnel
                                                    ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                            OVHcloud Bare-Metal Hypervisor Cluster                            │
│                                                                                              │
│   ┌────────────────────────────────┐                 ┌───────────────────────────────────┐   │
│   │  OVH Bare-Metal (sgp-bm-03)    │                 │  OVH vRack Private SDN Network    │   │
│   │  · AMD EPYC 9354 (32C/64T)     │                 │  · Routed Subnet: 51.79.144.16/28 │   │
│   │  · 384GB ECC DDR5 RAM          │                 │  · Gateway: 51.79.144.30          │   │
│   │  · 2x 3.84TB NVMe RAID1        │                 │  · Virtual MAC per VM             │   │
│   │  · Proxmox VE 8.3 (KVM/QEMU)   │                 └─────────────────┬─────────────────┘   │
│   └───────────────┬────────────────┘                                   │                     │
│                   │                                                    │                     │
│                   ▼                                                    ▼                     │
│   ┌──────────────────────────────────────────────────────────────────────────────────────┐   │
│   │  Sliced KVM Virtual Machines (Cloud-Init Injected)                                   │   │
│   │  ├── [VM 101] hk-proxy-edge   (4C/8G/80G)    IP: 51.79.144.18  (Debian 12)          │   │
│   │  ├── [VM 102] eu-api-worker   (8C/16G/160G)  IP: 51.79.144.19  (Ubuntu 24.04)        │   │
│   │  └── [VM 103] backup-db-01    (2C/4G/40G)    IP: 51.79.144.20  (Rocky Linux 9)       │   │
│   └──────────────────────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 单台裸金属商业模型测算 (Unit Economics)
* **母机成本**: OVHcloud Advance / Rise（如 AMD EPYC 32C/64T、256GB RAM、2x 3.84TB NVMe、1Gbps 不限流量）约 **$140/月**。
* **IPv4 成本**: OVH vRack 挂载 1 个 `/26` IP 块（64 个 IP，可分配 61 个）约 **$60/月**。
* **切分销售**: 按 1.5x - 2.0x 虚拟化合理超配，切分为 30 台 `KVM Pro (4C/8G/80G)`，客单价 **$14/月**。
* **总营收**: 30 台 × $14 = **$420/月**。
* **推广返佣**: 15% 佣金扣除约 **$63/月**。
* **单机净利润**: $420 - $140 - $60 - $63 = **$157/月**（单机毛利率超过 **60%**）。
* **控制面成本**: Cloudflare Workers Paid 基础套餐 **$5/月**，可支撑数十台母机与数千客户。

---

## 🚀 功能特性一览

### 1. 现代化企业级双主题 UI (浅色 / 深色)
* 告别低质廉价的 AI 霓虹渐变与模糊毛玻璃，采用与 **Vercel / Hetzner Cloud / Stripe / Fly.io** 对标的高密度企业级云服务视觉。
* 顶栏一键平滑切换浅色（Porcelain & Slate）与深色（Obsidian & Carbon）主题，支持 `prefers-color-scheme` 与 `localStorage` 持久化。
* 完备的 Typography 系统：UI 采用 `Inter`，IP/CIDR/端口/VMID/命令采用高可读性的 `JetBrains Mono`。

### 2. 系统拓扑与母机资源池可视化
* **物理母机监控**: 实时展示各节点的物理 CPU 核心分配率、ECC 内存水位、NVMe 存储占用与母机健康状态。
* **数据中心子网网格**: 将 OVH vRack 的 `/28` 或 `/26` 公网 IPv4 地址池以机房机架式的状态网格呈现，点击任意 IP 即可查看所属 VMID、反向解析 PTR 与虚拟 MAC。
* **交互式 Web VNC 控制台**: 客户端内置真实 Linux 终端模拟器，支持执行 `htop`、`df -h`、`ip a`、`uname -a` 等系统命令排错。

### 3. Stripe 支付与全自动开通流水线
* 支持按月、按季（9折）、按年（8折）计费，支持 Stripe Checkout 及站内账户余额即时扣缴。
* **全自动 5 步开通队列 (Cloudflare Queue)**:
  1. 接收 Webhook 并完成 HMAC-SHA256 签名校验；
  2. 匹配目标机房并根据容量算法自动选定最佳母机；
  3. 从该母机绑定的 IP 池中自动锁定空闲 IPv4；
  4. 调用 Proxmox VE REST API 克隆 Cloud-Init 模板（VMID 9000），注入 CPU/内存/IP/网关/Root 密码与自定义 SSH Key；
  5. 启动虚拟机并等待 QEMU Guest Agent 就绪，触发多通道即时交付通知。

### 4. 推广合伙人赚佣系统 (Affiliate Program)
* 专属推广链接与追踪代码（例如 `?ref=1STVIP88`），通过 Cookie 和会话双重锁定受邀客户。
* 客户首购与未来持续续费，系统通过 Worker 事务自动结算 **15% 佣金**到合伙人的 D1 账户中。
* **余额转换奖励**: 合伙人可随时一键将佣金转入 VPS 余额，并获得 **10% 额外奖励金**；或申请现金提现。
* 内置推广收益动态测算器（客户数 × 客单价实时模拟月度/年化被动收入）。

### 5. 消息中心、Web Push 与邮件营销
* **站内信 (Internal Inbox)**: 自动归档系统开通通知、Stripe 扣费电子发票、推广返佣凭据与维护广播。
* **Web Push (VAPID)**: 原生浏览器推送通道，提供实例离线告警、到期前 3 天续费预警与返佣到账弹窗。
* **在线客服 (Durable Objects)**: 基于 Cloudflare Durable Objects 实现低延迟 WebSocket 双向客服通道，支持快速连通性诊断与工单升级。
* **邮件营销后台 (Resend API)**: 支持按“全量用户”、“活跃 VPS 持有者”、“推广合伙人”一键分群，提供可视化 HTML 渲染预览与 Queue 异步排队广播。

---

## 📂 项目结构

```
1stVPS/
├── public/
│   └── index.html           # 现代化双主题客户端门户与系统可视化控制台
├── src/
│   ├── durable/
│   │   └── SupportChatRoom.ts # Cloudflare Durable Objects 实时在线客服
│   ├── services/
│   │   ├── notify.ts        # 站内信、Web Push (VAPID) 与邮件 (Resend API)
│   │   ├── ovh.ts           # OVHcloud API v1 原生签名客户端 (裸金属重装/vRack)
│   │   ├── provisioner.ts   # 全自动开通异步流水线
│   │   ├── proxmox.ts       # Proxmox VE REST API 客户端 (QEMU/Cloud-Init)
│   │   └── stripe.ts        # Stripe Checkout 会话创建与 Webhook 验签
│   ├── index.ts             # Hono REST API 入口、Queue 消费者与静态资产路由
│   └── types.ts             # TypeScript 类型定义
├── schema.sql               # Cloudflare D1 数据库架构与种子数据
├── wrangler.toml            # Cloudflare 全栈资源配置
├── tsconfig.json            # TypeScript 编译配置
└── package.json
```

---

## 🛠️ 本地启动与部署指南

### 1. 安装依赖
```bash
npm install
```

### 2. 创建 Cloudflare 资源
在 Cloudflare 仪表盘或通过 Wrangler CLI 创建所需的边缘资源：
```bash
# 创建 D1 数据库
npx wrangler d1 create 1stvps-db

# 创建 KV 命名空间
npx wrangler kv namespace create SESSION_KV

# 创建异步任务队列
npx wrangler queues create 1stvps-jobs
```

### 3. 配置 `wrangler.toml` 与初始化数据库
将上一步生成的 `database_id` 和 KV `id` 填入 `wrangler.toml`，然后执行建表与默认数据播种：
```bash
# 本地开发测试环境初始化
npm run db:local

# 生产环境 D1 初始化
npm run db:init
```

### 4. 设置密钥 (Secrets)
通过 Wrangler 加密注入生产凭证：
```bash
npx wrangler secret put JWT_SECRET
npx wrangler secret put GOOGLE_CLIENT_ID
npx wrangler secret put GOOGLE_CLIENT_SECRET
npx wrangler secret put STRIPE_SECRET_KEY
npx wrangler secret put STRIPE_WEBHOOK_SECRET
npx wrangler secret put OVH_APP_KEY
npx wrangler secret put OVH_APP_SECRET
npx wrangler secret put OVH_CONSUMER_KEY
npx wrangler secret put PROXMOX_API_TOKEN
npx wrangler secret put RESEND_API_KEY
```

### 5. 本地开发与发布
```bash
# 启动本地模拟开发服务器
npm run dev

# 编译并发布上线至 Cloudflare 全球边缘网络
npm run deploy
```

---

## 🔧 Proxmox VE 基础镜像模版制作建议

为了让自动化流水线能在 15 秒内完成交付，需在每台 OVH 裸金属母机上预置 Cloud-Init 模板：
1. 下载官方 Ubuntu / Debian Cloud 镜像（如 `ubuntu-24.04-minimal-cloudimg-amd64.img`）；
2. 执行 Proxmox CLI 创建基础模版（VMID 9000）：
   ```bash
   qm create 9000 --name "ubuntu-2404-template" --memory 2048 --net0 virtio,bridge=vmbr0
   qm importdisk 9000 ubuntu-24.04-minimal-cloudimg-amd64.img local-zfs
   qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-zfs:vm-9000-disk-0
   qm set 9000 --boot c --bootdisk scsi0
   qm set 9000 --ide2 local-zfs:cloudinit
   qm set 9000 --serial0 socket --vga serial0
   qm set 9000 --agent enabled=1
   qm template 9000
   ```
3. 后续当用户下单时，Cloudflare Worker 将直接调用 `qm clone 9000 {new_vmid}` 并通过 Cloud-Init 动态注入网络与密码，无需漫长的常规系统安装过程。
