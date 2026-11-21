# -*- coding: utf-8 -*-
"""
Generates public/admin.html - Dedicated Standalone 1stVPS Operator Management System
Completely isolated from the customer portal. Contains dedicated admin login & full operator dashboard.
"""

ADMIN_HTML = r'''<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>1stVPS Operator Console - 站长管理总控中枢</title>
  <script src="https://cdn.tailwindcss.com/3.4.17"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <script src="https://unpkg.com/lucide@0.460.0/dist/umd/lucide.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />

  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
          },
          colors: {
            darkbg: {
              950: '#070A11',
              900: '#0B0F19',
              850: '#111726',
              800: '#172033',
              700: '#1F2B44',
              600: '#334155',
            }
          },
        },
      },
    };
  </script>

  <style>
    :root {
      --bg-base: #070A11;
      --bg-surface: #0B0F19;
      --bg-elevated: #111726;
      --border-subtle: #1F2B44;
      --border-strong: #334155;
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --accent: #2563EB;
      --accent-hover: #1D4ED8;
      --accent-bg: rgba(37, 99, 235, 0.12);
    }
    body {
      background-color: var(--bg-base);
      color: var(--text-main);
    }
    .ui-surface {
      background-color: var(--bg-surface);
      border: 1px solid var(--border-subtle);
    }
    .ui-elevated {
      background-color: var(--bg-elevated);
      border: 1px solid var(--border-subtle);
    }
    .admin-nav-btn.active {
      background-color: var(--accent-bg);
      color: #60A5FA;
      border-color: rgba(96, 165, 250, 0.3);
      font-weight: 600;
    }
  </style>
</head>
<body class="min-h-screen flex flex-col font-sans antialiased text-sm select-none">

  <!-- ========================================== -->
  <!-- 1. ADMIN LOGIN VIEW (未登录时显示)          -->
  <!-- ========================================== -->
  <div id="adminLoginView" class="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-darkbg-950 via-darkbg-900 to-darkbg-950">
    <div class="w-full max-w-md p-8 rounded-2xl bg-darkbg-900 border border-slate-800 shadow-2xl space-y-6">
      
      <div class="text-center space-y-2">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-blue-700 to-cyan-500 text-white flex items-center justify-center font-bold text-lg font-mono mx-auto shadow-lg shadow-blue-500/20">
          1V
        </div>
        <h1 class="text-xl font-bold tracking-tight text-white">1stVPS 站长管理总控</h1>
        <p class="text-xs text-slate-400 font-mono">Infrastructure Operator Security Gateway</p>
      </div>

      <div class="p-3 rounded-lg bg-blue-950/40 border border-blue-900/60 text-xs text-blue-300 flex items-center gap-2">
        <i data-lucide="shield-alert" class="w-4 h-4 text-blue-400 shrink-0"></i>
        <span>本页面为平台运维专用通道，所有操作均记录安全审计日志。</span>
      </div>

      <form id="adminLoginForm" class="space-y-4">
        <div>
          <label class="block text-xs font-medium text-slate-300 mb-1.5">管理员账号 (Username)</label>
          <input type="text" id="loginUsername" required value="admin" class="w-full px-3.5 py-2.5 text-xs rounded-lg border border-slate-700 bg-darkbg-950 text-white font-mono focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="admin" />
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-300 mb-1.5">安全密钥 / 管理密码 (Password)</label>
          <input type="password" id="loginPassword" required value="admin888" class="w-full px-3.5 py-2.5 text-xs rounded-lg border border-slate-700 bg-darkbg-950 text-white font-mono focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="••••••••" />
        </div>

        <button type="submit" id="loginSubmitBtn" class="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-md transition flex items-center justify-center gap-2">
          <i data-lucide="log-in" class="w-4 h-4"></i>
          <span>进入运维管理总控台</span>
        </button>
      </form>

      <div class="pt-2 text-center">
        <span class="text-[11px] text-slate-500">演示凭据已预置：账号 <code>admin</code> / 密码 <code>admin888</code></span>
      </div>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- 2. ADMIN DASHBOARD VIEW (登录后显示)        -->
  <!-- ========================================== -->
  <div id="adminDashboardView" class="hidden min-h-screen flex flex-col">
    
    <!-- Top Operator Navigation Bar -->
    <header class="px-6 py-3 bg-darkbg-900 border-b border-darkbg-700 flex items-center justify-between sticky top-0 z-40">
      <div class="flex items-center gap-3">
        <div class="w-7 h-7 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-xs font-mono">
          1V
        </div>
        <div>
          <div class="font-bold text-white text-sm flex items-center gap-2">
            <span>1stVPS 站长运营管理中枢</span>
            <span class="text-[10px] px-2 py-0.5 rounded font-mono font-semibold bg-blue-950 text-blue-400 border border-blue-800">OPERATOR ROOT</span>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 text-xs font-mono text-emerald-400 px-2.5 py-1 rounded bg-emerald-950/60 border border-emerald-900/60">
          <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>Cloudflare Edge · D1 / KV / Queue 在线</span>
        </div>

        <button id="adminLogoutBtn" class="px-3 py-1.5 rounded-lg bg-darkbg-800 hover:bg-darkbg-700 text-slate-300 text-xs font-mono transition flex items-center gap-1.5">
          <i data-lucide="log-out" class="w-3.5 h-3.5"></i>
          <span>安全退出</span>
        </button>
      </div>
    </header>

    <div class="flex-1 flex overflow-hidden">
      <!-- Admin Sidebar -->
      <aside class="w-64 bg-darkbg-900 border-r border-darkbg-700 flex flex-col p-3 space-y-1 overflow-y-auto">
        <div class="px-3 pt-2 pb-1 text-[11px] font-semibold tracking-wider text-slate-500 uppercase">平台经营与指标</div>
        <button data-tab="overview" class="admin-nav-btn active w-full flex items-center gap-2.5 px-3 py-2 rounded-lg border border-transparent text-xs text-slate-300 hover:bg-darkbg-800 transition">
          <i data-lucide="bar-chart-3" class="w-4 h-4"></i>
          <span>经营大盘与指标</span>
        </button>

        <div class="px-3 pt-3 pb-1 text-[11px] font-semibold tracking-wider text-slate-500 uppercase">底层基础设施</div>
        <button data-tab="nodes" class="admin-nav-btn w-full flex items-center gap-2.5 px-3 py-2 rounded-lg border border-transparent text-xs text-slate-300 hover:bg-darkbg-800 transition">
          <i data-lucide="server" class="w-4 h-4"></i>
          <span>裸金属母机与集群</span>
        </button>
        <button data-tab="ips" class="admin-nav-btn w-full flex items-center gap-2.5 px-3 py-2 rounded-lg border border-transparent text-xs text-slate-300 hover:bg-darkbg-800 transition">
          <i data-lucide="network" class="w-4 h-4"></i>
          <span>公网 IP 资产池</span>
        </button>
        <button data-tab="instances" class="admin-nav-btn w-full flex items-center justify-between px-3 py-2 rounded-lg border border-transparent text-xs text-slate-300 hover:bg-darkbg-800 transition">
          <span class="flex items-center gap-2.5">
            <i data-lucide="cpu" class="w-4 h-4"></i>
            <span>全量客户 VPS 穿透</span>
          </span>
          <span class="text-[10px] px-1.5 py-0.5 rounded bg-blue-950 text-blue-400 font-mono">412台</span>
        </button>

        <div class="px-3 pt-3 pb-1 text-[11px] font-semibold tracking-wider text-slate-500 uppercase">业务审核与通知自动化</div>
        <button data-tab="commissions" class="admin-nav-btn w-full flex items-center justify-between px-3 py-2 rounded-lg border border-transparent text-xs text-slate-300 hover:bg-darkbg-800 transition">
          <span class="flex items-center gap-2.5">
            <i data-lucide="check-circle-2" class="w-4 h-4"></i>
            <span>合伙人提现审核</span>
          </span>
          <span class="text-[10px] px-1.5 py-0.5 rounded bg-amber-950 text-amber-400 font-mono">2待审</span>
        </button>
        <button data-tab="webhooks" class="admin-nav-btn w-full flex items-center justify-between px-3 py-2 rounded-lg border border-transparent text-xs text-slate-300 hover:bg-darkbg-800 transition">
          <span class="flex items-center gap-2.5">
            <i data-lucide="bell-ring" class="w-4 h-4"></i>
            <span>站长消息 Webhook 推送</span>
          </span>
          <span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 font-mono">实时</span>
        </button>
        <button data-tab="marketing" class="admin-nav-btn w-full flex items-center gap-2.5 px-3 py-2 rounded-lg border border-transparent text-xs text-slate-300 hover:bg-darkbg-800 transition">
          <i data-lucide="mail" class="w-4 h-4"></i>
          <span>全员邮件营销投放</span>
        </button>
      </aside>

      <!-- Main Operational Views Container -->
      <main class="flex-1 p-6 overflow-y-auto space-y-6 bg-darkbg-950">
        
        <!-- ========================================== -->
        <!-- VIEW: OVERVIEW                             -->
        <!-- ========================================== -->
        <section id="tab-overview" class="space-y-6">
          <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
            <div class="ui-surface rounded-xl p-4 flex items-center justify-between">
              <div>
                <div class="text-[11px] font-medium text-slate-400">全站注册客户数</div>
                <div class="text-2xl font-bold font-mono text-white mt-1">1,284</div>
                <div class="text-[11px] text-emerald-400 mt-0.5">昨日净增 +14 活跃客户</div>
              </div>
              <div class="p-2.5 rounded-lg bg-indigo-950 text-indigo-400">
                <i data-lucide="users" class="w-5 h-5"></i>
              </div>
            </div>

            <div class="ui-surface rounded-xl p-4 flex items-center justify-between">
              <div>
                <div class="text-[11px] font-medium text-slate-400">全网运行 KVM 实例</div>
                <div class="text-2xl font-bold font-mono text-white mt-1">412 台</div>
                <div class="text-[11px] text-blue-400 mt-0.5">跨 3 大物理裸金属母机</div>
              </div>
              <div class="p-2.5 rounded-lg bg-blue-950 text-blue-400">
                <i data-lucide="cpu" class="w-5 h-5"></i>
              </div>
            </div>

            <div class="ui-surface rounded-xl p-4 flex items-center justify-between">
              <div>
                <div class="text-[11px] font-medium text-slate-400">本月平台总营收 (MRR)</div>
                <div class="text-2xl font-bold font-mono text-white mt-1">$14,890.00</div>
                <div class="text-[11px] text-emerald-400 mt-0.5">Stripe 信用卡 + 余额支付</div>
              </div>
              <div class="p-2.5 rounded-lg bg-emerald-950 text-emerald-400">
                <i data-lucide="dollar-sign" class="w-5 h-5"></i>
              </div>
            </div>

            <div class="ui-surface rounded-xl p-4 flex items-center justify-between">
              <div>
                <div class="text-[11px] font-medium text-slate-400">待结算合伙人返佣</div>
                <div class="text-2xl font-bold font-mono text-amber-400 mt-1">$428.00</div>
                <div class="text-[11px] text-slate-400 mt-0.5 cursor-pointer hover:underline" onclick="switchAdminTab('commissions')">2 笔待审核 →</div>
              </div>
              <div class="p-2.5 rounded-lg bg-amber-950 text-amber-400">
                <i data-lucide="clock" class="w-5 h-5"></i>
              </div>
            </div>
          </div>

          <!-- Charts -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div class="ui-surface rounded-xl p-5">
              <div class="flex items-center justify-between mb-3">
                <h3 class="text-xs font-semibold text-white">近 7 日订单总营收与推广支出 (USD)</h3>
                <span class="text-[11px] text-slate-400 font-mono">D1 SQLite 聚合</span>
              </div>
              <div class="h-60 relative">
                <canvas id="adminRevChart"></canvas>
              </div>
            </div>

            <div class="ui-surface rounded-xl p-5">
              <div class="flex items-center justify-between mb-3">
                <h3 class="text-xs font-semibold text-white">裸金属母机物理资源分配率</h3>
                <span class="text-[11px] text-slate-400 font-mono">PVE Cluster API</span>
              </div>
              <div class="h-60 relative flex items-center justify-center">
                <canvas id="adminClusterChart"></canvas>
              </div>
            </div>
          </div>
        </section>

        <!-- ========================================== -->
        <!-- VIEW: BARE METAL NODES (母机物理集群)       -->
        <!-- ========================================== -->
        <section id="tab-nodes" class="space-y-6 hidden">
          <div class="ui-surface rounded-xl p-5 space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-darkbg-700">
              <div>
                <h2 class="text-sm font-semibold text-white flex items-center gap-2">
                  <i data-lucide="server" class="w-4 h-4 text-blue-400"></i>
                  底层裸金属母机与 Proxmox VE 虚拟化集群
                </h2>
                <p class="text-xs text-slate-400 mt-0.5">监控物理 CPU、ECC 内存与 NVMe 存储虚拟化切分超配率，支持通过 OVH API 远程一键重装</p>
              </div>
              <button onclick="showToast('正在调取母机纳管向导...', 'info')" class="px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-600 hover:bg-blue-700 text-white transition flex items-center gap-1.5">
                <i data-lucide="plus" class="w-3.5 h-3.5"></i>
                纳管新母机
              </button>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4" id="adminNodesGrid">
              <!-- Rendered by JS -->
            </div>

            <div id="adminNodeDetailBox" class="mt-4 p-4 rounded-lg bg-darkbg-900 border border-darkbg-700"></div>
          </div>
        </section>

        <!-- ========================================== -->
        <!-- VIEW: IP POOL (公网 IP 资产池)              -->
        <!-- ========================================== -->
        <section id="tab-ips" class="space-y-6 hidden">
          <div class="ui-surface rounded-xl p-5 space-y-4">
            <div class="flex items-center justify-between pb-3 border-b border-darkbg-700">
              <div>
                <h2 class="text-sm font-semibold text-white flex items-center gap-2">
                  <i data-lucide="network" class="w-4 h-4 text-blue-400"></i>
                  公网 IPv4 地址池与子网网格资产库
                </h2>
                <p class="text-xs text-slate-400 mt-0.5">管理各机房绑定的独立子网网段与分配状态</p>
              </div>
              <button onclick="showToast('已打开 IP 段批量导入向导', 'info')" class="px-3 py-1.5 rounded-lg text-xs font-medium bg-darkbg-800 hover:bg-darkbg-700 text-slate-200 border border-darkbg-600 transition">
                批量导入新 IP 子网
              </button>
            </div>

            <div id="adminIpPoolContainer" class="space-y-4"></div>
          </div>
        </section>

        <!-- ========================================== -->
        <!-- VIEW: ALL INSTANCES (全量实例穿透)          -->
        <!-- ========================================== -->
        <section id="tab-instances" class="space-y-6 hidden">
          <div class="ui-surface rounded-xl p-5 space-y-4">
            <div class="flex items-center justify-between pb-3 border-b border-darkbg-700">
              <div>
                <h2 class="text-sm font-semibold text-white flex items-center gap-2">
                  <i data-lucide="cpu" class="w-4 h-4 text-blue-400"></i>
                  全平台客户 VPS 穿透总控
                </h2>
                <p class="text-xs text-slate-400 mt-0.5">跨所有注册客户穿透监管，支持强制开机/关机/重启、重设密码及处置滥用</p>
              </div>
              <input type="text" placeholder="搜索客户邮箱、IP 或主机名..." class="px-3 py-1.5 text-xs rounded-lg border border-darkbg-700 bg-darkbg-900 text-white font-mono w-64" />
            </div>

            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs font-mono">
                <thead>
                  <tr class="text-slate-400 border-b border-darkbg-700">
                    <th class="py-2.5 px-3">VMID</th>
                    <th class="py-2.5 px-3">主机名</th>
                    <th class="py-2.5 px-3">客户邮箱</th>
                    <th class="py-2.5 px-3">物理母机</th>
                    <th class="py-2.5 px-3">公网 IPv4</th>
                    <th class="py-2.5 px-3">套餐规格</th>
                    <th class="py-2.5 px-3">运行状态</th>
                    <th class="py-2.5 px-3 text-right">运维操作</th>
                  </tr>
                </thead>
                <tbody id="adminInstancesTbody" class="divide-y divide-darkbg-700"></tbody>
              </table>
            </div>
          </div>
        </section>

        <!-- ========================================== -->
        <!-- VIEW: COMMISSIONS (合伙人提现审核)          -->
        <!-- ========================================== -->
        <section id="tab-commissions" class="space-y-6 hidden">
          <div class="ui-surface rounded-xl p-5 space-y-4">
            <div class="pb-3 border-b border-darkbg-700">
              <h2 class="text-sm font-semibold text-white flex items-center gap-2">
                <i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-400"></i>
                推广合伙人佣金提现审核
              </h2>
              <p class="text-xs text-slate-400 mt-0.5">审核合伙人申请的现金打款并核销 D1 数据库余额</p>
            </div>

            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs font-mono">
                <thead>
                  <tr class="text-slate-400 border-b border-darkbg-700">
                    <th class="py-2.5 px-3">申请单号</th>
                    <th class="py-2.5 px-3">合伙人邮箱</th>
                    <th class="py-2.5 px-3">提现金额</th>
                    <th class="py-2.5 px-3">渠道</th>
                    <th class="py-2.5 px-3">收款账号/地址</th>
                    <th class="py-2.5 px-3">状态</th>
                    <th class="py-2.5 px-3 text-right">审核操作</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-darkbg-700">
                  <tr>
                    <td class="py-3 px-3">WD-9812</td>
                    <td class="py-3 px-3">vip_partner@proton.me</td>
                    <td class="py-3 px-3 font-semibold text-emerald-400">$180.00</td>
                    <td class="py-3 px-3">USDT-TRC20</td>
                    <td class="py-3 px-3 text-slate-400">TXp91K28x9...L78mQ</td>
                    <td class="py-3 px-3"><span class="px-2 py-0.5 rounded text-[10px] bg-amber-950 text-amber-400 font-semibold">待审核</span></td>
                    <td class="py-3 px-3 text-right">
                      <button class="px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-700 text-white transition" onclick="showToast('已确认打款并通过审核！', 'success')">确认打款</button>
                    </td>
                  </tr>
                  <tr>
                    <td class="py-3 px-3">WD-9804</td>
                    <td class="py-3 px-3">cloud_dev@gmail.com</td>
                    <td class="py-3 px-3 font-semibold text-emerald-400">$248.00</td>
                    <td class="py-3 px-3">PayPal</td>
                    <td class="py-3 px-3 text-slate-400">cloud_dev@gmail.com</td>
                    <td class="py-3 px-3"><span class="px-2 py-0.5 rounded text-[10px] bg-amber-950 text-amber-400 font-semibold">待审核</span></td>
                    <td class="py-3 px-3 text-right">
                      <button class="px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-700 text-white transition" onclick="showToast('已确认打款并通过审核！', 'success')">确认打款</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <!-- ========================================== -->
        <!-- VIEW: WEBHOOK PUSH (站长消息推送配置)       -->
        <!-- ========================================== -->
        <section id="tab-webhooks" class="space-y-6 hidden">
          <div class="ui-surface rounded-xl p-5 lg:p-6 space-y-6">
            <div class="pb-3 border-b border-darkbg-700">
              <h2 class="text-sm font-semibold text-white flex items-center gap-2">
                <i data-lucide="bell-ring" class="w-4 h-4 text-blue-400"></i>
                站长系统消息 Webhook 与 Telegram 实时推送配置
              </h2>
              <p class="text-xs text-slate-400 mt-0.5">当发生新订单付款、客户发起在线客服咨询、合伙人提现或实例自动交付时，第一时间通过 Webhook 或 Telegram 通知站长手机</p>
            </div>

            <!-- Configuration Inputs -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              <!-- Telegram Bot -->
              <div class="p-4 rounded-xl bg-darkbg-900 border border-darkbg-700 space-y-3.5">
                <div class="flex items-center gap-2">
                  <div class="w-6 h-6 rounded-full bg-sky-500 text-white flex items-center justify-center text-xs font-bold font-mono">TG</div>
                  <h3 class="text-xs font-semibold text-white">Telegram 机器人即时推送</h3>
                </div>
                
                <div>
                  <label class="block text-[11px] font-medium text-slate-400 mb-1">Telegram Bot Token</label>
                  <input type="password" id="webhookTgToken" class="w-full px-3 py-2 text-xs rounded-lg border border-darkbg-600 bg-darkbg-950 text-white font-mono" placeholder="7123456789:AAHk..._your_token" />
                  <span class="text-[10px] text-slate-500">在 Telegram 向 @BotFather 发送 /newbot 获取</span>
                </div>

                <div>
                  <label class="block text-[11px] font-medium text-slate-400 mb-1">Telegram Chat ID (群组或个人 ID)</label>
                  <input type="text" id="webhookTgChatId" class="w-full px-3 py-2 text-xs rounded-lg border border-darkbg-600 bg-darkbg-950 text-white font-mono" placeholder="例如: 123456789 或 -100123456789" />
                  <span class="text-[10px] text-slate-500">向 @userinfobot 发送任意消息获取您的 Chat ID</span>
                </div>
              </div>

              <!-- Custom Webhook URL -->
              <div class="p-4 rounded-xl bg-darkbg-900 border border-darkbg-700 space-y-3.5">
                <div class="flex items-center gap-2">
                  <div class="w-6 h-6 rounded-full bg-emerald-500 text-white flex items-center justify-center text-xs font-bold font-mono">WH</div>
                  <h3 class="text-xs font-semibold text-white">自定义 Webhook (飞书 / 钉钉 / 企微 / Discord)</h3>
                </div>

                <div>
                  <label class="block text-[11px] font-medium text-slate-400 mb-1">Webhook URL 回调地址</label>
                  <input type="text" id="webhookCustomUrl" class="w-full px-3 py-2 text-xs rounded-lg border border-darkbg-600 bg-darkbg-950 text-white font-mono" placeholder="https://open.feishu.cn/open-apis/bot/v2/hook/... 或 Discord Webhook" />
                  <span class="text-[10px] text-slate-500">后端自动兼容标准 HTTP POST、飞书机器人、钉钉机器人与 Discord</span>
                </div>

                <div class="pt-2 text-xs text-slate-400 space-y-1">
                  <div>· 支持群机器人静默接收全量经营报警</div>
                  <div>· 订单发生时可点击消息直达处理链路</div>
                </div>
              </div>
            </div>

            <!-- Event Toggles -->
            <div class="space-y-3 pt-3 border-t border-darkbg-700">
              <h3 class="text-xs font-semibold text-white">订阅推送的业务关键事件</h3>
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                <label class="flex items-center gap-2.5 p-3 rounded-lg border border-darkbg-700 bg-darkbg-900 text-xs cursor-pointer">
                  <input type="checkbox" id="evtOrderPaid" checked class="w-4 h-4 rounded text-blue-600" />
                  <div>
                    <div class="font-medium text-white">新订单支付成功</div>
                    <div class="text-[10px] text-slate-500">含金额、规格与客户邮箱</div>
                  </div>
                </label>

                <label class="flex items-center gap-2.5 p-3 rounded-lg border border-darkbg-700 bg-darkbg-900 text-xs cursor-pointer">
                  <input type="checkbox" id="evtSupportChat" checked class="w-4 h-4 rounded text-blue-600" />
                  <div>
                    <div class="font-medium text-white">客户发起在线咨询</div>
                    <div class="text-[10px] text-slate-500">客户提问即刻手机提醒</div>
                  </div>
                </label>

                <label class="flex items-center gap-2.5 p-3 rounded-lg border border-darkbg-700 bg-darkbg-900 text-xs cursor-pointer">
                  <input type="checkbox" id="evtAffiliateWithdraw" checked class="w-4 h-4 rounded text-blue-600" />
                  <div>
                    <div class="font-medium text-white">合伙人申请提现</div>
                    <div class="text-[10px] text-slate-500">提现金额与收款地址提醒</div>
                  </div>
                </label>

                <label class="flex items-center gap-2.5 p-3 rounded-lg border border-darkbg-700 bg-darkbg-900 text-xs cursor-pointer">
                  <input type="checkbox" id="evtProvisionResult" checked class="w-4 h-4 rounded text-blue-600" />
                  <div>
                    <div class="font-medium text-white">实例自动交付结果</div>
                    <div class="text-[10px] text-slate-500">开通成功或异常告警预警</div>
                  </div>
                </label>
              </div>
            </div>

            <!-- Actions & Live Test Status -->
            <div class="flex flex-wrap items-center justify-between gap-4 pt-3 border-t border-darkbg-700">
              <div class="flex items-center gap-2" id="webhookTestStatusBox">
                <span class="text-xs text-slate-400">点击右侧按钮可直接向您填写的配置发送测试消息验证连通性</span>
              </div>

              <div class="flex items-center gap-3">
                <button id="testWebhookBtn" class="px-4 py-2 rounded-lg bg-darkbg-800 hover:bg-darkbg-700 text-slate-200 text-xs font-medium border border-darkbg-600 transition flex items-center gap-1.5">
                  <i data-lucide="zap" class="w-3.5 h-3.5 text-amber-400"></i>
                  <span>一键发送测试推送</span>
                </button>

                <button id="saveWebhookSettingsBtn" class="px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition flex items-center gap-1.5">
                  <i data-lucide="save" class="w-3.5 h-3.5"></i>
                  <span>保存推送配置</span>
                </button>
              </div>
            </div>

          </div>
        </section>

        <!-- ========================================== -->
        <!-- VIEW: MARKETING                            -->
        <!-- ========================================== -->
        <section id="tab-marketing" class="space-y-6 hidden">
          <div class="ui-surface rounded-xl p-5 space-y-4">
            <div class="pb-3 border-b border-darkbg-700">
              <h2 class="text-sm font-semibold text-white flex items-center gap-2">
                <i data-lucide="mail" class="w-4 h-4 text-blue-400"></i>
                全员广播与邮件营销中心 (Cloudflare Queues + Resend)
              </h2>
              <p class="text-xs text-slate-400 mt-0.5">针对已注册客户群体定向发送节假日特惠、可用区扩容通知或安全维护公告</p>
            </div>

            <div class="space-y-3 max-w-2xl">
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">邮件主题 (Subject)</label>
                <input type="text" id="campaignSubject" value="[1stVPS] 新加坡节点极速 BGP 扩容完毕，全线云主机续费特惠" class="w-full px-3 py-2 text-xs rounded-lg border border-darkbg-600 bg-darkbg-900 text-white font-mono" />
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">受众用户分群</label>
                <select class="w-full px-3 py-2 text-xs rounded-lg border border-darkbg-600 bg-darkbg-900 text-white">
                  <option value="all">全站所有注册客户 (1,284 人)</option>
                  <option value="active">当前拥有运行中云主机的付费客户 (412 人)</option>
                  <option value="affiliate">合伙人分销渠道用户 (18 人)</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">HTML 邮件内容模板</label>
                <textarea rows="6" class="w-full px-3 py-2 text-xs rounded-lg border border-darkbg-600 bg-darkbg-900 text-white font-mono"><h2>尊敬的 1stVPS 用户：</h2><p>感谢您一直以来的信任。我们位于亚太新加坡的全新高速 BGP 骨干网络现已全量交付就绪！</p></textarea>
              </div>
              <button onclick="showToast('邮件任务已投递至 Cloudflare Queue 队列', 'success')" class="px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium transition flex items-center gap-1.5">
                <i data-lucide="send" class="w-3.5 h-3.5"></i>
                投递队列并发送邮件
              </button>
            </div>
          </div>
        </section>

      </main>
    </div>
  </div>

  <!-- Toast Container -->
  <div id="toastContainer" class="fixed bottom-5 right-5 z-50 flex flex-col gap-2 pointer-events-none max-w-sm"></div>

  <script>
    const ADMIN_STATE = {
      authenticated: false,
      activeTab: 'overview',
      adminUser: null,
      selectedNodeId: 'node_sgp_03',
      adminNodes: [
        {
          id: 'node_sgp_03',
          name: 'sgp-bm-03',
          dc: 'SGP · 新加坡',
          ovhId: 'ns5091231.ip-51-79-144.net',
          cpuModel: 'AMD EPYC 9354P (32C/64T)',
          totalVcpu: 128,
          usedVcpu: 36,
          totalRam: 384,
          usedRam: 96,
          subnet: '51.79.144.16/28',
          gateway: '51.79.144.30',
        },
        {
          id: 'node_rbx_01',
          name: 'rbx-bm-01',
          dc: 'FRA · 德国法兰克福',
          ovhId: 'ns3198412.ip-51-89-10.eu',
          cpuModel: 'AMD EPYC 7443P (24C/48T)',
          totalVcpu: 96,
          usedVcpu: 42,
          totalRam: 256,
          usedRam: 112,
          subnet: '51.89.10.32/28',
          gateway: '51.89.10.46',
        },
        {
          id: 'node_gra_02',
          name: 'gra-bm-02',
          dc: 'PAR · 法国巴黎',
          ovhId: 'ns3284910.ip-141-94-22.eu',
          cpuModel: 'Intel Xeon Gold 6338 (32C/64T)',
          totalVcpu: 128,
          usedVcpu: 64,
          totalRam: 512,
          usedRam: 224,
          subnet: '141.94.22.64/28',
          gateway: '141.94.22.78',
        },
      ],
      allInstances: [
        { vmid: 101, host: 'hk-proxy-edge', email: 'alex@1stvps.io', node: 'sgp-bm-03', ip: '51.79.144.18', plan: 'KVM Pro', status: 'running' },
        { vmid: 102, host: 'eu-api-worker', email: 'dev@corp.eu', node: 'rbx-bm-01', ip: '51.89.10.44', plan: 'KVM Compute', status: 'running' },
        { vmid: 103, host: 'backup-db-01', email: 'ops@cloud.io', node: 'gra-bm-02', ip: '141.94.22.91', plan: 'KVM Starter', status: 'stopped' },
        { vmid: 104, host: 'asia-relay-09', email: 'partner@vpn.net', node: 'sgp-bm-03', ip: '51.79.144.19', plan: 'KVM Extreme', status: 'running' },
      ],
    };

    // Check existing auth
    function checkAdminAuth() {
      fetch('/api/admin/auth/me')
        .then(res => res.json())
        .then(data => {
          if (data && data.authenticated) {
            ADMIN_STATE.authenticated = true;
            ADMIN_STATE.adminUser = data.user;
            showDashboard();
          } else {
            showLogin();
          }
        })
        .catch(() => showLogin());
    }

    function showLogin() {
      document.getElementById('adminLoginView').classList.remove('hidden');
      document.getElementById('adminDashboardView').classList.add('hidden');
      lucide.createIcons();
    }

    function showDashboard() {
      document.getElementById('adminLoginView').classList.add('hidden');
      document.getElementById('adminDashboardView').classList.remove('hidden');
      switchAdminTab('overview');
      lucide.createIcons();
    }

    // Login Form Submit
    document.getElementById('adminLoginForm').addEventListener('submit', (e) => {
      e.preventDefault();
      const u = document.getElementById('loginUsername').value.trim();
      const p = document.getElementById('loginPassword').value.trim();

      fetch('/api/admin/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, password: p }),
      })
        .then(res => res.json())
        .then(data => {
          if (data.ok) {
            showToast('认证成功，欢迎进入站长控制台', 'success');
            ADMIN_STATE.authenticated = true;
            ADMIN_STATE.adminUser = data.user;
            showDashboard();
          } else {
            showToast(data.error || '登录失败', 'error');
          }
        })
        .catch(err => showToast(`网络错误: ${err.message}`, 'error'));
    });

    document.getElementById('adminLogoutBtn').addEventListener('click', () => {
      fetch('/api/admin/auth/logout', { method: 'POST' }).finally(() => {
        ADMIN_STATE.authenticated = false;
        showToast('已安全登出运维中枢', 'info');
        showLogin();
      });
    });

    // Tab switching
    function switchAdminTab(tab) {
      ADMIN_STATE.activeTab = tab;
      document.querySelectorAll('section[id^="tab-"]').forEach(s => s.classList.add('hidden'));
      const target = document.getElementById(`tab-${tab}`);
      if (target) target.classList.remove('hidden');

      document.querySelectorAll('.admin-nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tab);
      });

      if (tab === 'overview') renderAdminCharts();
      if (tab === 'nodes') renderAdminNodes();
      if (tab === 'ips') renderAdminIps();
      if (tab === 'instances') renderAdminInstances();
      if (tab === 'webhooks') loadAdminWebhookSettings();
      lucide.createIcons();
    }

    document.querySelectorAll('.admin-nav-btn').forEach(btn => {
      btn.addEventListener('click', () => switchAdminTab(btn.dataset.tab));
    });

    // Charts
    let chart1 = null;
    let chart2 = null;
    function renderAdminCharts() {
      const textColor = '#94A3B8';
      const gridColor = 'rgba(51, 65, 85, 0.4)';

      const ctx1 = document.getElementById('adminRevChart');
      if (ctx1) {
        if (chart1) chart1.destroy();
        chart1 = new Chart(ctx1, {
          type: 'bar',
          data: {
            labels: ['11-16', '11-17', '11-18', '11-19', '11-20', '11-21', '今天'],
            datasets: [
              {
                label: '订单总营收 ($)',
                data: [140, 224, 168, 308, 252, 336, 196],
                backgroundColor: '#3B82F6',
                borderRadius: 4,
              },
              {
                label: '推广支出 ($)',
                data: [21, 33.6, 25.2, 46.2, 37.8, 50.4, 29.4],
                backgroundColor: '#10B981',
                borderRadius: 4,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: textColor, font: { size: 11 } } } },
            scales: {
              x: { ticks: { color: textColor }, grid: { color: gridColor } },
              y: { ticks: { color: textColor }, grid: { color: gridColor } },
            },
          },
        });
      }

      const ctx2 = document.getElementById('adminClusterChart');
      if (ctx2) {
        if (chart2) chart2.destroy();
        chart2 = new Chart(ctx2, {
          type: 'doughnut',
          data: {
            labels: ['已交付客户 VPS (42%)', '母机系统预留 (8%)', '未切分空闲 (50%)'],
            datasets: [
              {
                data: [42, 8, 50],
                backgroundColor: ['#3B82F6', '#8B5CF6', '#1E293B'],
                borderWidth: 0,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom', labels: { color: textColor, font: { size: 11 } } } },
          },
        });
      }
    }

    // Bare Metal Nodes
    function renderAdminNodes() {
      document.getElementById('adminNodesGrid').innerHTML = ADMIN_STATE.adminNodes.map(n => {
        const isSelected = n.id === ADMIN_STATE.selectedNodeId;
        const cpuPct = Math.round((n.usedVcpu / n.totalVcpu) * 100);
        const ramPct = Math.round((n.usedRam / n.totalRam) * 100);

        return `
          <div class="p-4 rounded-xl cursor-pointer border transition-all ${isSelected ? 'border-blue-500 bg-blue-950/30 ring-1 ring-blue-500' : 'ui-surface hover:border-slate-600'}" onclick="selectAdminNode('${n.id}')">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                <span class="font-mono font-semibold text-xs text-white">${n.name}</span>
              </div>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-darkbg-800 text-slate-300">${n.dc}</span>
            </div>
            <div class="text-[11px] text-slate-400 mt-2 font-mono truncate">${n.cpuModel}</div>
            <div class="text-[10px] text-slate-500 font-mono truncate">${n.ovhId}</div>

            <div class="mt-3 space-y-1.5 text-xs">
              <div class="flex justify-between text-[11px]">
                <span class="text-slate-400">vCPU 切分率:</span>
                <span class="font-mono font-medium">${n.usedVcpu} / ${n.totalVcpu} Cores (${cpuPct}%)</span>
              </div>
              <div class="w-full bg-darkbg-800 h-1.5 rounded-full overflow-hidden">
                <div class="bg-blue-600 h-full" style="width: ${cpuPct}%"></div>
              </div>

              <div class="flex justify-between text-[11px] pt-1">
                <span class="text-slate-400">ECC RAM 分配:</span>
                <span class="font-mono font-medium">${n.usedRam} / ${n.totalRam} GB (${ramPct}%)</span>
              </div>
              <div class="w-full bg-darkbg-800 h-1.5 rounded-full overflow-hidden">
                <div class="bg-emerald-500 h-full" style="width: ${ramPct}%"></div>
              </div>
            </div>
          </div>
        `;
      }).join('');

      renderAdminNodeDetail();
    }

    function selectAdminNode(id) {
      ADMIN_STATE.selectedNodeId = id;
      renderAdminNodes();
    }

    function renderAdminNodeDetail() {
      const node = ADMIN_STATE.adminNodes.find(n => n.id === ADMIN_STATE.selectedNodeId) || ADMIN_STATE.adminNodes[0];
      const panel = document.getElementById('adminNodeDetailBox');

      panel.innerHTML = `
        <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-darkbg-700 text-xs">
          <div>
            <span class="font-semibold text-white">母机切分拓扑: ${node.name}</span>
            <span class="text-slate-400 ml-2">子网: <span class="font-mono text-blue-400">${node.subnet}</span> · 网关: <span class="font-mono">${node.gateway}</span></span>
          </div>
          <button onclick="triggerOvhReinstall('${node.ovhId}')" class="px-3 py-1 rounded bg-rose-600 hover:bg-rose-700 text-white text-[11px] font-mono">
            OVH API 母机一键重装 PVE 8
          </button>
        </div>

        <div class="mt-3">
          <div class="text-[11px] text-slate-400 mb-1.5 font-medium">专用 IPv4 子网地址池网格 (点击查看绑定)</div>
          <div class="grid grid-cols-4 sm:grid-cols-8 gap-2">
            ${Array.from({ length: 16 }).map((_, idx) => {
              const lastOctet = 16 + idx;
              const isGateway = idx === 14;
              const isAssigned = idx < 6;
              const bgClass = isGateway ? 'bg-amber-950 border-amber-800 text-amber-300'
                : isAssigned ? 'bg-emerald-950 border-emerald-800 text-emerald-300 font-semibold'
                : 'bg-darkbg-950 border-darkbg-700 text-slate-500';
              const label = isGateway ? 'GW' : isAssigned ? `VM${101 + idx}` : `.${lastOctet}`;

              return `
                <div class="p-2 rounded border text-center font-mono text-[11px] ${bgClass}">
                  <div>${label}</div>
                  <div class="text-[9px] opacity-70">.${lastOctet}</div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      `;
    }

    function triggerOvhReinstall(ovhId) {
      if (!confirm(`确定要通过 OVH API 重装物理母机 ${ovhId} 为 Proxmox VE 8.3 吗？`)) return;
      showToast(`已向 OVHcloud API 提交母机 ${ovhId} 重装任务`, 'info');
      fetch('/api/admin/ovh/install-proxmox', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ serviceName: ovhId }),
      }).catch(console.error);
    }

    // IP Pool
    function renderAdminIps() {
      const container = document.getElementById('adminIpPoolContainer');
      container.innerHTML = ADMIN_STATE.adminNodes.map(node => `
        <div class="p-4 rounded-xl bg-darkbg-900 border border-darkbg-700 space-y-3">
          <div class="flex items-center justify-between text-xs">
            <div>
              <span class="font-bold text-white font-mono">${node.name}</span>
              <span class="text-slate-400 ml-2 font-mono">子网 CIDR: ${node.subnet} · 网关: ${node.gateway}</span>
            </div>
            <span class="text-emerald-400 font-mono text-[11px]">10 空闲 / 6 已分配</span>
          </div>
          <div class="grid grid-cols-4 sm:grid-cols-8 gap-1.5 text-center font-mono text-[11px]">
            ${Array.from({ length: 16 }).map((_, idx) => {
              const octet = 16 + idx;
              const isAssigned = idx < 6;
              const isGw = idx === 14;
              const cls = isGw ? 'bg-amber-950 text-amber-300 border-amber-800' : isAssigned ? 'bg-emerald-950 text-emerald-300 border-emerald-800' : 'bg-darkbg-950 text-slate-500 border-darkbg-700';
              return `<div class="p-1.5 rounded border ${cls}">.${octet}</div>`;
            }).join('')}
          </div>
        </div>
      `).join('');
    }

    // All Instances
    function renderAdminInstances() {
      document.getElementById('adminInstancesTbody').innerHTML = ADMIN_STATE.allInstances.map(inst => `
        <tr class="hover:bg-darkbg-850">
          <td class="py-2.5 px-3 text-slate-400 font-semibold">${inst.vmid}</td>
          <td class="py-2.5 px-3 font-semibold text-white">${inst.host}</td>
          <td class="py-2.5 px-3 text-slate-400">${inst.email}</td>
          <td class="py-2.5 px-3 text-slate-400">${inst.node}</td>
          <td class="py-2.5 px-3 text-blue-400">${inst.ip}</td>
          <td class="py-2.5 px-3">${inst.plan}</td>
          <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] ${inst.status === 'running' ? 'bg-emerald-950 text-emerald-400' : 'bg-darkbg-800 text-slate-400'} font-semibold">${inst.status}</span></td>
          <td class="py-2.5 px-3 text-right">
            <button onclick="showToast('已向 QEMU Agent 派发重启', 'info')" class="px-2 py-0.5 rounded bg-darkbg-800 text-slate-300 text-[11px] mr-1">重启</button>
            <button onclick="showToast('已强制停机', 'info')" class="px-2 py-0.5 rounded bg-rose-950 text-rose-400 text-[11px]">停机</button>
          </td>
        </tr>
      `).join('');
    }

    // Webhook Settings
    function loadAdminWebhookSettings() {
      fetch('/api/admin/settings')
        .then(res => res.json())
        .then(data => {
          if (data && data.settings) {
            const s = data.settings;
            if (s.telegramBotToken) document.getElementById('webhookTgToken').value = s.telegramBotToken;
            if (s.telegramChatId) document.getElementById('webhookTgChatId').value = s.telegramChatId;
            if (s.webhookUrl) document.getElementById('webhookCustomUrl').value = s.webhookUrl;
            if (s.events) {
              if (s.events.order !== undefined) document.getElementById('evtOrderPaid').checked = s.events.order;
              if (s.events.support !== undefined) document.getElementById('evtSupportChat').checked = s.events.support;
              if (s.events.affiliate !== undefined) document.getElementById('evtAffiliateWithdraw').checked = s.events.affiliate;
              if (s.events.system !== undefined) document.getElementById('evtProvisionResult').checked = s.events.system;
            }
          }
        })
        .catch(console.error);
    }

    document.getElementById('saveWebhookSettingsBtn').addEventListener('click', () => {
      const payload = {
        telegramBotToken: document.getElementById('webhookTgToken').value.trim(),
        telegramChatId: document.getElementById('webhookTgChatId').value.trim(),
        webhookUrl: document.getElementById('webhookCustomUrl').value.trim(),
        events: {
          order: document.getElementById('evtOrderPaid').checked,
          support: document.getElementById('evtSupportChat').checked,
          affiliate: document.getElementById('evtAffiliateWithdraw').checked,
          system: document.getElementById('evtProvisionResult').checked,
        },
      };

      fetch('/api/admin/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
        .then(res => res.json())
        .then(data => {
          showToast(data.message || '系统消息推送设置已保存至 Cloudflare KV', 'success');
        })
        .catch(e => showToast(`保存失败: ${e.message}`, 'error'));
    });

    document.getElementById('testWebhookBtn').addEventListener('click', () => {
      const statusBox = document.getElementById('webhookTestStatusBox');
      statusBox.innerHTML = '<span class="text-xs text-blue-400 font-mono flex items-center gap-1.5"><i data-lucide="loader" class="w-3.5 h-3.5 animate-spin"></i> 正在向 Telegram / Webhook 发送测试推送...</span>';
      lucide.createIcons();

      fetch('/api/admin/webhook/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
        .then(res => res.json())
        .then(data => {
          showToast('测试消息已派发，请查看您的 Telegram / Webhook 群', 'success');
          const tg = data.result && data.result.telegram;
          const wh = data.result && data.result.webhook;

          let html = '<div class="text-[11px] font-mono flex items-center gap-2">';
          if (tg) {
            html += tg.ok
              ? '<span class="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400">Telegram: 成功 (200)</span>'
              : `<span class="px-2 py-0.5 rounded bg-rose-950 text-rose-400">Telegram: 失败</span>`;
          } else {
            html += '<span class="text-slate-500">Telegram: 未配置</span>';
          }
          if (wh) {
            html += wh.ok
              ? '<span class="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400">Webhook: 成功 (200)</span>'
              : `<span class="px-2 py-0.5 rounded bg-rose-950 text-rose-400">Webhook: 失败</span>`;
          } else {
            html += '<span class="text-slate-500">Webhook: 未配置</span>';
          }
          html += '</div>';
          statusBox.innerHTML = html;
        })
        .catch(err => {
          statusBox.innerHTML = `<span class="text-xs text-rose-400 font-mono">测试派发异常: ${err.message}</span>`;
        });
    });

    // Toast
    function showToast(msg, type = 'info') {
      const container = document.getElementById('toastContainer');
      const colors = type === 'success'
        ? 'border-emerald-600 bg-emerald-950 text-emerald-200'
        : type === 'error'
        ? 'border-rose-600 bg-rose-950 text-rose-200'
        : 'border-blue-600 bg-darkbg-850 text-slate-100';
      const el = document.createElement('div');
      el.className = `pointer-events-auto px-4 py-2.5 rounded-lg border text-xs font-medium shadow-lg transition-all ${colors}`;
      el.textContent = msg;
      container.appendChild(el);
      setTimeout(() => el.remove(), 3200);
    }

    window.addEventListener('DOMContentLoaded', () => {
      checkAdminAuth();
      lucide.createIcons();
    });
  </script>
</body>
</html>
'''

with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(ADMIN_HTML)

print("Successfully generated public/admin.html with UTF-8 encoding!")
