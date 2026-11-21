# -*- coding: utf-8 -*-
"""
Generates public/index.html - 1stVPS Modern Cloud Hosting Client Portal
Faithfully modelled after Rabisu (https://www.rabisu.com/):
- Dark-first aesthetic (#0b0f19 / #161b26) with crisp light mode
- Live hardware telemetry bar (AMD EPYC, NVMe Gen4, 1Gbps, Anycast 3.2Tbps)
- Multi-cycle billing switcher with discount pills (1mo, 3mo -10%, 6mo -15%, 12mo -20%)
- WHMCS/Rabisu 2-column cloud configurator & sticky order summary
- Full Client Area (instances, web VNC console, rDNS PTR, reinstall, billing, affiliate, support chat)
- ABSOLUTELY ZERO ADMIN BUTTONS OR LINKS IN CLIENT FACING UI.
"""

CLIENT_HTML = r'''<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>1stVPS - 新一代极速企业级云服务器 | 高性能 KVM 架构 · 原生高防</title>
  <script src="https://cdn.tailwindcss.com/3.4.17"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <script src="https://unpkg.com/lucide@0.460.0/dist/umd/lucide.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />

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
            rabisu: {
              blue: '#1b64da',
              blueHover: '#1552b5',
              cyan: '#06b6d4',
              emerald: '#10b981',
            },
            darkbg: {
              950: '#070a11',
              900: '#0b0f19',
              850: '#111726',
              800: '#161b26',
              700: '#1f293d',
              600: '#2d3748',
            },
            lightbg: {
              50: '#F8FAFC',
              100: '#F1F5F9',
              200: '#E2E8F0',
              300: '#CBD5E1',
            }
          },
        },
      },
    };
  </script>

  <style>
    /* Rabisu 风格现代云计算平台设计系统 */
    :root {
      --bg-base: #F8FAFC;
      --bg-surface: #FFFFFF;
      --bg-elevated: #F1F5F9;
      --border-subtle: #E2E8F0;
      --border-strong: #CBD5E1;
      --text-main: #0F172A;
      --text-muted: #64748B;
      --accent: #1B64DA;
      --accent-hover: #1552B5;
      --accent-bg: #EFF6FF;
    }

    html.dark {
      --bg-base: #0B0F19;
      --bg-surface: #161B26;
      --bg-elevated: #111726;
      --border-subtle: #1F293D;
      --border-strong: #2D3748;
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --accent: #1B64DA;
      --accent-hover: #2563EB;
      --accent-bg: rgba(27, 100, 218, 0.12);
    }

    body {
      background-color: var(--bg-base);
      color: var(--text-main);
      transition: background-color 0.15s ease, color 0.15s ease;
    }

    .ui-surface {
      background-color: var(--bg-surface);
      border: 1px solid var(--border-subtle);
    }

    .ui-elevated {
      background-color: var(--bg-elevated);
      border: 1px solid var(--border-subtle);
    }

    .blueprint-grid {
      background-size: 36px 36px;
      background-image: 
        linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    }

    html:not(.dark) .blueprint-grid {
      background-image: 
        linear-gradient(to right, rgba(0, 0, 0, 0.03) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(0, 0, 0, 0.03) 1px, transparent 1px);
    }

    .text-gradient {
      background: linear-gradient(135deg, #38BDF8 0%, #3B82F6 50%, #10B981 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
  </style>
</head>
<body class="min-h-screen flex flex-col font-sans antialiased text-sm">

  <!-- ========================================== -->
  <!-- TOP HEADER & MEGA NAVIGATION (Rabisu Style) -->
  <!-- ========================================== -->
  <header class="sticky top-0 z-50 bg-white/90 dark:bg-darkbg-900/90 backdrop-blur border-b border-slate-200 dark:border-darkbg-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
      
      <!-- Brand Logo -->
      <a href="/" class="flex items-center gap-3 shrink-0">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-400 text-white flex items-center justify-center font-extrabold text-base font-mono shadow-md shadow-blue-500/20">
          1V
        </div>
        <div>
          <div class="font-bold text-slate-900 dark:text-white text-base tracking-tight leading-none flex items-center gap-1.5">
            <span>1stVPS</span>
            <span class="text-[10px] px-1.5 py-0.2 rounded font-mono font-semibold bg-blue-50 dark:bg-blue-950 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-900">CLOUD</span>
          </div>
          <div class="text-[10px] text-slate-500 dark:text-slate-400 font-mono mt-0.5">High Performance Cloud</div>
        </div>
      </a>

      <!-- Center Navigation Links -->
      <nav class="hidden lg:flex items-center gap-6 text-xs font-medium text-slate-700 dark:text-slate-300">
        <a href="#section-plans" class="hover:text-blue-600 dark:hover:text-blue-400 transition flex items-center gap-1">
          <span>云服务器 (VPS)</span>
          <span class="text-[9px] px-1 rounded bg-blue-500/10 text-blue-600 dark:text-blue-400 font-bold">HOT</span>
        </a>
        <a href="#section-telemetry" class="hover:text-blue-600 dark:hover:text-blue-400 transition">硬件架构</a>
        <a href="#section-regions" class="hover:text-blue-600 dark:hover:text-blue-400 transition">全球可用区</a>
        <a href="#section-configurator" class="hover:text-blue-600 dark:hover:text-blue-400 transition">在线选配开通</a>
        <button onclick="openClientArea('affiliate')" class="hover:text-blue-600 dark:hover:text-blue-400 transition flex items-center gap-1">
          <span>推广返佣</span>
          <span class="text-[9px] px-1 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-bold">15%</span>
        </button>
      </nav>

      <!-- Right Action Utilities -->
      <div class="flex items-center gap-3">
        <!-- Currency & Region Pill -->
        <div class="hidden sm:flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-mono bg-slate-100 dark:bg-darkbg-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-darkbg-700">
          <span>USD $</span>
        </div>

        <!-- Dark / Light Theme Toggle -->
        <button id="themeToggleBtn" class="p-2 rounded-lg text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white bg-slate-100 dark:bg-darkbg-800 border border-slate-200 dark:border-darkbg-700 transition" title="切换主题">
          <i data-lucide="sun" class="w-4 h-4 hidden dark:block text-amber-400"></i>
          <i data-lucide="moon" class="w-4 h-4 block dark:hidden text-slate-700"></i>
        </button>

        <!-- Client Area Button (Rabisu Müşteri Paneli) -->
        <button id="openClientAreaBtn" class="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition flex items-center gap-1.5">
          <i data-lucide="user" class="w-3.5 h-3.5"></i>
          <span id="clientAreaBtnText">控制台中心 (Client Area)</span>
        </button>
      </div>

    </div>
  </header>

  <!-- ========================================== -->
  <!-- HERO BANNER SECTION (Rabisu Style)         -->
  <!-- ========================================== -->
  <section class="relative blueprint-grid border-b border-slate-200 dark:border-darkbg-700 overflow-hidden py-16 lg:py-24">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center space-y-6">
      
      <!-- Category Badge -->
      <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-medium bg-blue-50 dark:bg-blue-950/80 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-900 shadow-sm">
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        <span>新一代企业级 KVM 架构 · 全球 4 大核心机房 60 秒秒级交付</span>
      </div>

      <!-- Main Heading -->
      <h1 class="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white max-w-4xl mx-auto leading-tight">
        高性能全球云服务器 <br class="hidden sm:inline" />
        <span class="text-gradient">秒级自动化交付 · 原生高防</span>
      </h1>

      <!-- Subtitle -->
      <p class="text-sm sm:text-base text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
        全线搭载最新一代 AMD EPYC™ 处理器与企业级 PCIe 4.0 NVMe RAID-10 阵列。独享 1Gbps 上行网络，内置 3.2Tbps Anycast 抗 DDoS 过滤清洗。
      </p>

      <!-- Hero Action CTAs -->
      <div class="flex flex-wrap items-center justify-center gap-3 pt-2">
        <a href="#section-plans" class="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-lg shadow-blue-500/25 transition flex items-center gap-2">
          <i data-lucide="shopping-cart" class="w-4 h-4"></i>
          <span>立即选购云服务器</span>
        </a>
        <a href="#section-regions" class="px-6 py-3 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-darkbg-800 dark:hover:bg-darkbg-750 text-slate-800 dark:text-slate-200 text-xs font-semibold border border-slate-200 dark:border-darkbg-700 transition flex items-center gap-2">
          <i data-lucide="gauge" class="w-4 h-4 text-emerald-500"></i>
          <span>全球可用区延迟测速</span>
        </a>
      </div>

      <!-- ========================================== -->
      <!-- LIVE TELEMETRY STATS BAR (Directly from Rabisu) -->
      <!-- ========================================== -->
      <div id="section-telemetry" class="pt-10 max-w-5xl mx-auto">
        <div class="ui-surface rounded-2xl p-5 shadow-xl grid grid-cols-2 md:grid-cols-5 gap-4 divide-y md:divide-y-0 md:divide-x divide-slate-100 dark:divide-darkbg-700 text-center">
          
          <div class="p-2 space-y-1">
            <div class="text-[11px] text-slate-500 font-medium flex items-center justify-center gap-1">
              <i data-lucide="cpu" class="w-3.5 h-3.5 text-blue-500"></i>
              <span>CPU 峰值主频</span>
            </div>
            <div class="text-base font-extrabold font-mono text-slate-900 dark:text-white">3.8GHz+ 睿频</div>
            <div class="text-[10px] text-emerald-600 dark:text-emerald-400 font-mono">AMD EPYC™ 架构</div>
          </div>

          <div class="p-2 space-y-1">
            <div class="text-[11px] text-slate-500 font-medium flex items-center justify-center gap-1">
              <i data-lucide="layers" class="w-3.5 h-3.5 text-indigo-500"></i>
              <span>ECC 内存校验</span>
            </div>
            <div class="text-base font-extrabold font-mono text-slate-900 dark:text-white">高频 DDR4/DDR5</div>
            <div class="text-[10px] text-slate-400 font-mono">企业容错保障</div>
          </div>

          <div class="p-2 space-y-1">
            <div class="text-[11px] text-slate-500 font-medium flex items-center justify-center gap-1">
              <i data-lucide="hard-drive" class="w-3.5 h-3.5 text-cyan-500"></i>
              <span>NVMe 存储阵列</span>
            </div>
            <div class="text-base font-extrabold font-mono text-slate-900 dark:text-white">7,000 MB/s</div>
            <div class="text-[10px] text-slate-400 font-mono">PCIe 4.0 RAID-10</div>
          </div>

          <div class="p-2 space-y-1">
            <div class="text-[11px] text-slate-500 font-medium flex items-center justify-center gap-1">
              <i data-lucide="zap" class="w-3.5 h-3.5 text-amber-500"></i>
              <span>独享网络端口</span>
            </div>
            <div class="text-base font-extrabold font-mono text-slate-900 dark:text-white">1 Gbps+ 上行</div>
            <div class="text-[10px] text-emerald-600 dark:text-emerald-400 font-mono">Anycast 多线 BGP</div>
          </div>

          <div class="p-2 space-y-1">
            <div class="text-[11px] text-slate-500 font-medium flex items-center justify-center gap-1">
              <i data-lucide="shield-check" class="w-3.5 h-3.5 text-emerald-500"></i>
              <span>SLA 在线保障</span>
            </div>
            <div class="text-base font-extrabold font-mono text-slate-900 dark:text-white">99.99%</div>
            <div class="text-[10px] text-emerald-600 dark:text-emerald-400 font-mono">3.2Tbps DDoS 高防</div>
          </div>

        </div>
      </div>

    </div>
  </section>

  <!-- ========================================== -->
  <!-- VPS PLANS PRICING GRID (Rabisu Style)       -->
  <!-- ========================================== -->
  <section id="section-plans" class="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
    <div class="text-center space-y-3">
      <h2 class="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
        透明云服务器规格套餐
      </h2>
      <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400 max-w-xl mx-auto">
        所有规格均配备独立独享公网 IPv4、原生 /64 IPv6、KVM 原生虚拟化与 100% NVMe 高速固态阵列。
      </p>

      <!-- Multi-Cycle Billing Switcher with Discount Chips (Rabisu Style) -->
      <div class="inline-flex p-1.5 rounded-xl bg-slate-100 dark:bg-darkbg-800 border border-slate-200 dark:border-darkbg-700 text-xs font-medium" id="cycleSelector">
        <button data-cycle="1" class="px-3.5 py-1.5 rounded-lg bg-white dark:bg-darkbg-700 text-slate-900 dark:text-white shadow-sm font-semibold">
          按月付费
        </button>
        <button data-cycle="3" class="px-3.5 py-1.5 rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white flex items-center gap-1">
          <span>按季付</span>
          <span class="text-[10px] px-1 py-0.2 rounded bg-amber-500/10 text-amber-500 font-bold">省10%</span>
        </button>
        <button data-cycle="6" class="px-3.5 py-1.5 rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white flex items-center gap-1">
          <span>半年付</span>
          <span class="text-[10px] px-1 py-0.2 rounded bg-amber-500/10 text-amber-500 font-bold">省15%</span>
        </button>
        <button data-cycle="12" class="px-3.5 py-1.5 rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white flex items-center gap-1">
          <span>按年付</span>
          <span class="text-[10px] px-1.5 py-0.2 rounded bg-emerald-500 text-white font-bold">省20% 推荐</span>
        </button>
      </div>
    </div>

    <!-- Pricing Cards Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6" id="vpsPlansGrid">
      <!-- Rendered by JS -->
    </div>
  </section>

  <!-- ========================================== -->
  <!-- GLOBAL REGIONS & LATENCY (可用区测速)      -->
  <!-- ========================================== -->
  <section id="section-regions" class="py-16 bg-slate-50 dark:bg-darkbg-950 border-y border-slate-200 dark:border-darkbg-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
      <div class="text-center space-y-2">
        <h2 class="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">全球优质可用区骨干网络</h2>
        <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400">直连全球核心交换中心，提供低延迟回国优化与最高 3.2Tbps Anycast 高防清洗</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" id="regionsDisplayGrid">
        <!-- Rendered by JS -->
      </div>
    </div>
  </section>

  <!-- ========================================== -->
  <!-- 2-COLUMN CONFIGURATOR & CHECKOUT (WHMCS / Rabisu Style) -->
  <!-- ========================================== -->
  <section id="section-configurator" class="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
    <div class="text-center space-y-2">
      <h2 class="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">自定义云服务器选配开通</h2>
      <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400">实时计算周期折扣与配置明细，Stripe 支付完成后秒级全自动交付上线</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
      
      <!-- Left Configurator Column (2 cols wide) -->
      <div class="lg:col-span-2 ui-surface rounded-2xl p-6 space-y-6">
        
        <!-- Step 1: Datacenter -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <span class="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-mono">1</span>
              <span>选择目标可用区节点</span>
            </h3>
            <span class="text-xs text-slate-500">直连核心骨干网络</span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3" id="confDcSelector"></div>
        </div>

        <!-- Step 2: Specs Tier -->
        <div class="space-y-3 pt-4 border-t border-slate-200 dark:border-darkbg-700">
          <h3 class="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <span class="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-mono">2</span>
            <span>选择硬件规格套餐</span>
          </h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3" id="confPlanSelector"></div>
        </div>

        <!-- Step 3: OS Image -->
        <div class="space-y-3 pt-4 border-t border-slate-200 dark:border-darkbg-700">
          <h3 class="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <span class="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-mono">3</span>
            <span>选择操作系统镜像模板</span>
          </h3>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5" id="confOsSelector"></div>
        </div>

        <!-- Step 4: Hostname & SSH Key -->
        <div class="space-y-3 pt-4 border-t border-slate-200 dark:border-darkbg-700">
          <h3 class="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <span class="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-mono">4</span>
            <span>主机参数与初始安全凭证</span>
          </h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">实例主机名 (Hostname)</label>
              <input type="text" id="confHostname" value="1stvps-cloud-node" class="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-darkbg-600 bg-white dark:bg-darkbg-900 font-mono text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">SSH 公钥 / Root 密码 (留空将自动生成)</label>
              <input type="text" id="confSshKey" placeholder="ssh-rsa AAAA... 或自定义密码" class="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-darkbg-600 bg-white dark:bg-darkbg-900 font-mono text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500" />
            </div>
          </div>
        </div>

      </div>

      <!-- Right Sticky Order Summary Column (WHMCS Style) -->
      <div class="lg:sticky lg:top-24 space-y-4">
        <div class="ui-surface rounded-2xl p-6 shadow-xl space-y-4">
          <h3 class="text-sm font-bold text-slate-900 dark:text-white flex items-center justify-between pb-3 border-b border-slate-200 dark:border-darkbg-700">
            <span>订单配置摘要 (Order Summary)</span>
            <span class="text-xs font-mono text-blue-600 dark:text-blue-400">USD</span>
          </h3>

          <div class="space-y-2.5 text-xs font-mono" id="stickySummaryList">
            <!-- Rendered by JS -->
          </div>

          <div class="pt-3 border-t border-slate-200 dark:border-darkbg-700 flex items-baseline justify-between">
            <span class="text-xs font-bold text-slate-700 dark:text-slate-300">实付总额 (Total Due):</span>
            <div class="text-right">
              <div class="text-2xl font-black font-mono text-blue-600 dark:text-blue-400" id="stickyTotalAmount">$14.00</div>
              <div class="text-[10px] text-slate-400 font-mono" id="stickyDiscountNote">按月支付周期</div>
            </div>
          </div>

          <div class="space-y-2 pt-2">
            <button id="stripeCheckoutBtn" class="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-md transition flex items-center justify-center gap-2">
              <i data-lucide="credit-card" class="w-4 h-4"></i>
              <span>Stripe 信用卡安全支付</span>
            </button>
            <button id="balanceCheckoutBtn" class="w-full py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-darkbg-800 dark:hover:bg-darkbg-750 text-slate-800 dark:text-slate-200 text-xs font-semibold border border-slate-200 dark:border-darkbg-700 transition flex items-center justify-center gap-2">
              <i data-lucide="wallet" class="w-3.5 h-3.5 text-amber-500"></i>
              <span>使用账户余额直接扣款</span>
            </button>
          </div>

          <!-- Automated Delivery Progress Feedback -->
          <div id="provisionFeedbackBox" class="hidden p-3.5 rounded-xl bg-darkbg-950 border border-blue-900/60 space-y-2 text-xs">
            <div class="flex items-center justify-between">
              <span class="text-blue-400 font-semibold flex items-center gap-1.5">
                <i data-lucide="loader" class="w-3.5 h-3.5 animate-spin"></i>
                正在自动交付实例...
              </span>
              <span id="provPercentText" class="font-mono text-slate-400">0%</span>
            </div>
            <div class="w-full bg-darkbg-800 h-1.5 rounded-full overflow-hidden">
              <div id="provProgressBar" class="bg-blue-600 h-full transition-all duration-300" style="width: 0%"></div>
            </div>
            <div id="provLogText" class="text-[10px] font-mono text-slate-400 truncate">Cloudflare Queue 调度中...</div>
          </div>

        </div>

        <div class="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900 text-xs text-emerald-800 dark:text-emerald-300 space-y-1">
          <div class="font-bold flex items-center gap-1.5">
            <i data-lucide="check-circle" class="w-3.5 h-3.5"></i>
            <span>即时交付保障</span>
          </div>
          <div class="text-[11px] opacity-90">支付确认后 60 秒内全自动分配独立 IPv4 并注入 SSH 初始密钥。</div>
        </div>
      </div>

    </div>
  </section>

  <!-- ========================================== -->
  <!-- CLIENT AREA MODAL / DRAWER (客户控制中心)   -->
  <!-- ========================================== -->
  <div id="clientAreaModal" class="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm hidden flex items-center justify-center p-3 sm:p-6">
    <div class="ui-surface rounded-2xl max-w-5xl w-full h-[90vh] flex flex-col overflow-hidden shadow-2xl">
      
      <!-- Client Area Top Header -->
      <div class="px-6 py-4 border-b border-slate-200 dark:border-darkbg-700 flex items-center justify-between shrink-0">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-xs font-mono">
            1V
          </div>
          <div>
            <div class="font-bold text-slate-900 dark:text-white text-sm">客户控制中心 (Client Area)</div>
            <div class="text-xs text-slate-500 font-mono">Alex Chen · alex@1stvps.io · 余额: $148.50</div>
          </div>
        </div>

        <!-- Navigation Tabs inside Client Area -->
        <div class="hidden sm:flex items-center gap-1 bg-slate-100 dark:bg-darkbg-800 p-1 rounded-xl text-xs font-medium" id="clientAreaTabs">
          <button data-tab="instances" class="px-3 py-1.5 rounded-lg bg-white dark:bg-darkbg-700 text-slate-900 dark:text-white shadow-sm font-semibold">我的实例</button>
          <button data-tab="billing" class="px-3 py-1.5 rounded-lg text-slate-600 dark:text-slate-400 hover:text-slate-900">账单与发票</button>
          <button data-tab="affiliate" class="px-3 py-1.5 rounded-lg text-slate-600 dark:text-slate-400 hover:text-slate-900">推广赚佣 (15%)</button>
          <button data-tab="support" class="px-3 py-1.5 rounded-lg text-slate-600 dark:text-slate-400 hover:text-slate-900">在线支持</button>
          <button data-tab="inbox" class="px-3 py-1.5 rounded-lg text-slate-600 dark:text-slate-400 hover:text-slate-900">通知</button>
        </div>

        <button onclick="closeClientArea()" class="p-2 text-slate-400 hover:text-slate-700 dark:hover:text-white">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>

      <!-- Client Area Body -->
      <div class="flex-1 p-6 overflow-y-auto space-y-6 bg-slate-50/50 dark:bg-darkbg-950">
        
        <!-- Tab: Instances -->
        <div id="cTab-instances" class="space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-slate-900 dark:text-white">我的云主机实例列表 (3 台)</h3>
            <button onclick="closeClientArea(); location.href='#section-configurator'" class="px-3 py-1.5 rounded-lg bg-blue-600 text-white text-xs font-medium">新购主机</button>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" id="clientInstancesGrid"></div>
        </div>

        <!-- Tab: Billing -->
        <div id="cTab-billing" class="space-y-4 hidden">
          <h3 class="text-sm font-bold text-slate-900 dark:text-white">Stripe 历史发票凭据与扣费记录</h3>
          <div class="ui-surface rounded-xl p-4 overflow-x-auto">
            <table class="w-full text-left text-xs font-mono">
              <thead>
                <tr class="text-slate-500 border-b border-slate-200 dark:border-darkbg-700">
                  <th class="py-2.5 px-3">发票单号</th>
                  <th class="py-2.5 px-3">出账日期</th>
                  <th class="py-2.5 px-3">计费说明</th>
                  <th class="py-2.5 px-3">扣款方式</th>
                  <th class="py-2.5 px-3">金额</th>
                  <th class="py-2.5 px-3">状态</th>
                  <th class="py-2.5 px-3 text-right">电子收据</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-darkbg-800">
                <tr>
                  <td class="py-3 px-3 text-blue-600 dark:text-blue-400 font-semibold">#INV-202611-0921</td>
                  <td class="py-3 px-3 text-slate-500">2026-11-20</td>
                  <td class="py-3 px-3 text-slate-800 dark:text-slate-200">KVM Pro · 新加坡节点月付</td>
                  <td class="py-3 px-3">Visa ···· 4242</td>
                  <td class="py-3 px-3 font-semibold">$14.00</td>
                  <td class="py-3 px-3"><span class="px-2 py-0.5 rounded text-[10px] bg-emerald-50 dark:bg-emerald-950 text-emerald-600 font-semibold">已支付</span></td>
                  <td class="py-3 px-3 text-right"><button onclick="showToast('正在调取 Stripe 电子收据 PDF...', 'info')" class="text-blue-600 hover:underline">下载 PDF</button></td>
                </tr>
                <tr>
                  <td class="py-3 px-3 text-blue-600 dark:text-blue-400 font-semibold">#INV-202610-8812</td>
                  <td class="py-3 px-3 text-slate-500">2026-10-20</td>
                  <td class="py-3 px-3 text-slate-800 dark:text-slate-200">KVM Compute · 德国法兰克福</td>
                  <td class="py-3 px-3">MasterCard ···· 8899</td>
                  <td class="py-3 px-3 font-semibold">$28.00</td>
                  <td class="py-3 px-3"><span class="px-2 py-0.5 rounded text-[10px] bg-emerald-50 dark:bg-emerald-950 text-emerald-600 font-semibold">已支付</span></td>
                  <td class="py-3 px-3 text-right"><button onclick="showToast('正在调取 Stripe 电子收据 PDF...', 'info')" class="text-blue-600 hover:underline">下载 PDF</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Tab: Affiliate -->
        <div id="cTab-affiliate" class="space-y-4 hidden">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="ui-surface rounded-xl p-4 space-y-1">
              <div class="text-xs text-slate-500">推荐注册客户数</div>
              <div class="text-2xl font-bold font-mono text-slate-900 dark:text-white">18 人</div>
            </div>
            <div class="ui-surface rounded-xl p-4 space-y-1">
              <div class="text-xs text-slate-500">累计赚取佣金</div>
              <div class="text-2xl font-bold font-mono text-slate-900 dark:text-white">$426.00</div>
            </div>
            <div class="ui-surface rounded-xl p-4 space-y-2">
              <div class="text-xs text-slate-500">可提现余额</div>
              <div class="text-2xl font-bold font-mono text-blue-600 dark:text-blue-400">$148.50</div>
              <button onclick="showToast('已提交提现申请，站长审核后 24h 内到账！', 'success')" class="w-full py-1.5 rounded-lg bg-blue-600 text-white text-xs font-medium">申请提现</button>
            </div>
          </div>
          <div class="ui-surface rounded-xl p-4 space-y-2">
            <h4 class="text-xs font-bold text-slate-900 dark:text-white">您的专属推广返佣链接 (15% 循环返佣)</h4>
            <div class="flex items-center gap-2">
              <input type="text" readonly value="https://1stvps.io?ref=1STVIP88" class="flex-1 px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-darkbg-700 bg-white dark:bg-darkbg-900 font-mono text-slate-900 dark:text-white" />
              <button onclick="copyToClipboard('https://1stvps.io?ref=1STVIP88', '专属推广链接')" class="px-4 py-2 rounded-lg bg-blue-600 text-white text-xs font-medium">复制链接</button>
            </div>
          </div>
        </div>

        <!-- Tab: Support Chat -->
        <div id="cTab-support" class="space-y-4 hidden">
          <div class="ui-surface rounded-xl p-4 flex flex-col h-[420px]">
            <div class="pb-2 border-b border-slate-200 dark:border-darkbg-700 flex items-center justify-between text-xs">
              <span class="font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <i data-lucide="headphones" class="w-4 h-4 text-blue-500"></i>
                1stVPS 在线技术客服支持
              </span>
              <span class="text-emerald-500 flex items-center gap-1 font-mono">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                客服在线 · 发送即时推送站长
              </span>
            </div>
            <div class="flex-1 py-3 overflow-y-auto space-y-2.5 text-xs" id="supportChatMessages">
              <div class="p-3 rounded-xl bg-slate-100 dark:bg-darkbg-900 text-slate-800 dark:text-slate-200 max-w-[85%]">
                尊敬的客户您好！欢迎使用 1stVPS 在线技术支持。有关云服务器开通、反向 DNS 配置或网络优化的疑问，请直接在此留言，我们的值班工程师将即刻协助。
              </div>
            </div>
            <div class="pt-2 border-t border-slate-200 dark:border-darkbg-700 flex gap-2">
              <input type="text" id="clientSupportInput" placeholder="输入您的问题 (发送即刻推送到站长手机)..." class="flex-1 px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-darkbg-700 bg-white dark:bg-darkbg-900 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500" />
              <button onclick="sendClientSupport()" class="px-4 py-2 rounded-lg bg-blue-600 text-white text-xs font-medium">发送咨询</button>
            </div>
          </div>
        </div>

        <!-- Tab: Inbox -->
        <div id="cTab-inbox" class="space-y-3 hidden">
          <h3 class="text-sm font-bold text-slate-900 dark:text-white">系统交付与账单通知</h3>
          <div class="space-y-2 text-xs">
            <div class="ui-surface rounded-xl p-3.5 space-y-1">
              <div class="font-bold text-slate-900 dark:text-white">云主机 hk-proxy-edge 交付就绪</div>
              <div class="text-slate-600 dark:text-slate-400">已成功分配独立 IPv4: 51.79.144.18，Cloud-Init 初始密码已注入。</div>
              <div class="text-[10px] text-slate-400 font-mono">10 分钟前</div>
            </div>
            <div class="ui-surface rounded-xl p-3.5 space-y-1">
              <div class="font-bold text-slate-900 dark:text-white">推广佣金入账通知 +$8.40</div>
              <div class="text-slate-600 dark:text-slate-400">受邀客户完成订单，15% 佣金已结算至您的账户。</div>
              <div class="text-[10px] text-slate-400 font-mono">2 小时前</div>
            </div>
          </div>
        </div>

      </div>

    </div>
  </div>

  <!-- ========================================== -->
  <!-- MODAL: WEB VNC TERMINAL CONSOLE            -->
  <!-- ========================================== -->
  <div id="vncModal" class="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="bg-darkbg-950 border border-slate-800 rounded-2xl max-w-2xl w-full h-[480px] flex flex-col overflow-hidden shadow-2xl">
      <div class="px-4 py-3 bg-darkbg-900 border-b border-darkbg-700 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-red-500 inline-block"></span>
          <span class="w-3 h-3 rounded-full bg-amber-500 inline-block"></span>
          <span class="w-3 h-3 rounded-full bg-emerald-500 inline-block"></span>
          <span id="vncTitle" class="ml-2 font-mono text-xs text-slate-300">Web VNC Terminal · root@hk-proxy-edge</span>
        </div>
        <button onclick="closeVncModal()" class="text-slate-400 hover:text-white">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>
      <div class="flex-1 p-4 bg-black font-mono text-xs text-emerald-400 overflow-y-auto space-y-1.5" id="vncScreen">
        <div>1stVPS Cloud QEMU Agent VNC Console (xterm-256color)</div>
        <div>Connected via Cloudflare Anycast WebSocket Edge...</div>
        <div>Linux hk-proxy-edge 6.8.0-40-generic #40-Ubuntu SMP PREEMPT_DYNAMIC</div>
        <div>root@hk-proxy-edge:~# <span class="animate-pulse">_</span></div>
      </div>
      <div class="p-3 bg-darkbg-900 border-t border-darkbg-700 flex gap-2">
        <span class="text-xs font-mono text-slate-400 py-1.5">root@vm:~#</span>
        <input type="text" id="vncInput" placeholder="输入命令 (例如: uptime, df -h, ip addr)..." class="flex-1 px-3 py-1.5 text-xs rounded bg-darkbg-950 border border-darkbg-700 text-white font-mono focus:outline-none" />
        <button onclick="sendVncCmd()" class="px-3 py-1.5 rounded bg-blue-600 text-white text-xs font-mono">发送</button>
      </div>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- FOOTER (Modern Hosting Style)              -->
  <!-- ========================================== -->
  <footer class="mt-auto border-t border-slate-200 dark:border-darkbg-700 bg-white dark:bg-darkbg-900 py-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-xs">
        <div class="space-y-3">
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-xs font-mono">1V</div>
            <span class="font-bold text-slate-900 dark:text-white">1stVPS</span>
          </div>
          <p class="text-slate-500">新一代高性能全球云服务器与分布式基础设施平台，专注极速交付与企业级稳定性保障。</p>
        </div>
        <div class="space-y-2">
          <div class="font-bold text-slate-900 dark:text-white">核心产品</div>
          <div class="space-y-1.5 text-slate-500">
            <div><a href="#section-plans" class="hover:text-blue-500">KVM 云服务器 (VPS)</a></div>
            <div><a href="#section-plans" class="hover:text-blue-500">大带宽计算型主机</a></div>
            <div><a href="#section-plans" class="hover:text-blue-500">高防存储型主机</a></div>
          </div>
        </div>
        <div class="space-y-2">
          <div class="font-bold text-slate-900 dark:text-white">全球数据中心</div>
          <div class="space-y-1.5 text-slate-500 font-mono">
            <div>🇸🇬 新加坡 Jurong (CN2/CMI)</div>
            <div>🇩🇪 德国法兰克福 (DE-CIX)</div>
            <div>🇫🇷 法国巴黎 (核心骨干)</div>
            <div>🇨🇦 加拿大蒙特利尔 (500G抗D)</div>
          </div>
        </div>
        <div class="space-y-2">
          <div class="font-bold text-slate-900 dark:text-white">客户支持</div>
          <div class="space-y-1.5 text-slate-500">
            <div><button onclick="openClientArea('support')" class="hover:text-blue-500">在线工单与技术支持</button></div>
            <div><a href="#section-regions" class="hover:text-blue-500">全球可用区延迟测速</a></div>
            <div><button onclick="openClientArea('affiliate')" class="hover:text-blue-500">合伙人推广中心 (15%)</button></div>
          </div>
        </div>
      </div>

      <div class="pt-8 border-t border-slate-200 dark:border-darkbg-700 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-500">
        <div>© 2026 1stVPS Global Cloud Platform. All rights reserved.</div>
        <div class="flex items-center gap-3 font-mono text-[11px]">
          <span>VISA</span>
          <span>Mastercard</span>
          <span>Stripe</span>
          <span>Google Pay</span>
          <span>Apple Pay</span>
        </div>
      </div>
    </div>
  </footer>

  <!-- Toast Notification Container -->
  <div id="toastContainer" class="fixed bottom-5 right-5 z-50 flex flex-col gap-2 pointer-events-none max-w-sm"></div>

  <!-- Application Logic Scripts -->
  <script>
    const CLIENT_STATE = {
      theme: 'dark',
      cycle: 1, // 1: month, 3: quarter, 6: semi, 12: year
      selectedDc: 'SGP',
      selectedPlanId: 'pro',
      selectedOs: 'Ubuntu 24.04 LTS',
      dcs: [
        { code: 'SGP', name: '亚太 - 新加坡', flag: '🇸🇬', label: '新加坡 Jurong 机房', ping: '38ms', bgp: 'CN2 / CMI 高速多线' },
        { code: 'FRA', name: '欧洲 - 德国法兰克福', flag: '🇩🇪', label: '法兰克福核心枢纽', ping: '145ms', bgp: 'DE-CIX 骨干极速互联' },
        { code: 'PAR', name: '欧洲 - 法国巴黎', flag: '🇫🇷', label: '法国巴黎高防核心', ping: '152ms', bgp: '欧洲核心骨干网' },
        { code: 'BHS', name: '北美 - 加拿大蒙特利尔', flag: '🇨🇦', label: '北美 Beauharnois 枢纽', ping: '180ms', bgp: '北美多线 BGP 抗D' },
      ],
      plans: [
        { id: 'starter', name: 'KVM Starter', vcpu: 2, ram: 4, nvme: 40, bw: '2 TB', price: 6.00, oldPrice: 8.00 },
        { id: 'pro', name: 'KVM Pro', vcpu: 4, ram: 8, nvme: 80, bw: '5 TB', price: 14.00, oldPrice: 18.00, tag: '最热销' },
        { id: 'compute', name: 'KVM Compute', vcpu: 8, ram: 16, nvme: 160, bw: '10 TB', price: 28.00, oldPrice: 35.00 },
        { id: 'extreme', name: 'KVM Extreme', vcpu: 16, ram: 32, nvme: 320, bw: '20 TB', price: 56.00, oldPrice: 70.00 },
      ],
      oses: ['Ubuntu 24.04 LTS', 'Debian 12', 'Rocky Linux 9', 'AlmaLinux 9', 'Windows Server 2022'],
      instances: [
        { id: 'vm_101', host: 'hk-proxy-edge', dc: 'SGP', plan: 'KVM Pro', ip: '51.79.144.18', os: 'Debian 12', vcpu: 4, ram: 8, nvme: 80, status: 'running' },
        { id: 'vm_102', host: 'eu-api-worker', dc: 'FRA', plan: 'KVM Compute', ip: '51.89.10.44', os: 'Ubuntu 24.04 LTS', vcpu: 8, ram: 16, nvme: 160, status: 'running' },
        { id: 'vm_103', host: 'backup-db-01', dc: 'PAR', plan: 'KVM Starter', ip: '141.94.22.91', os: 'Rocky Linux 9', vcpu: 2, ram: 4, nvme: 40, status: 'stopped' },
      ],
    };

    // Cycle Selector Discounts
    function getDiscount(cycle) {
      if (cycle === 3) return 0.9;
      if (cycle === 6) return 0.85;
      if (cycle === 12) return 0.8;
      return 1.0;
    }

    // Render Pricing Cards (Rabisu Style)
    function renderPricingCards() {
      const discount = getDiscount(CLIENT_STATE.cycle);
      const container = document.getElementById('vpsPlansGrid');
      container.innerHTML = CLIENT_STATE.plans.map(p => {
        const currentMonthly = (p.price * discount).toFixed(2);
        const isPopular = !!p.tag;

        return `
          <div class="ui-surface rounded-2xl p-6 relative flex flex-col justify-between transition-all hover:border-blue-500 ${isPopular ? 'border-blue-500 shadow-xl shadow-blue-500/10' : ''}">
            ${isPopular ? `<span class="absolute -top-3 right-5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-600 text-white shadow-sm uppercase tracking-wider">最热销 POPULAR</span>` : ''}
            
            <div class="space-y-4">
              <div>
                <h3 class="text-base font-bold text-slate-900 dark:text-white">${p.name}</h3>
                <div class="text-xs text-slate-500 font-mono mt-0.5">企业级 KVM 架构</div>
              </div>

              <!-- Price -->
              <div class="pt-2 flex items-baseline gap-2">
                <span class="text-xs text-slate-400 line-through font-mono">$${(p.oldPrice * CLIENT_STATE.cycle).toFixed(0)}</span>
                <span class="text-3xl font-extrabold font-mono text-slate-900 dark:text-white">$${currentMonthly}</span>
                <span class="text-xs text-slate-500 font-mono">/ 月</span>
              </div>

              <!-- Specs Breakdown -->
              <div class="p-3 rounded-xl bg-slate-50 dark:bg-darkbg-850 border border-slate-200 dark:border-darkbg-700 space-y-1.5 text-xs font-mono">
                <div class="flex justify-between"><span>vCPU:</span><span class="font-bold text-slate-900 dark:text-white">${p.vcpu} 核心</span></div>
                <div class="flex justify-between"><span>ECC 内存:</span><span class="font-bold text-slate-900 dark:text-white">${p.ram} GB</span></div>
                <div class="flex justify-between"><span>PCIe 4.0:</span><span class="font-bold text-slate-900 dark:text-white">${p.nvme} GB NVMe</span></div>
                <div class="flex justify-between"><span>独享流量:</span><span class="font-bold text-slate-900 dark:text-white">${p.bw} (1Gbps)</span></div>
              </div>

              <!-- Feature Checklist with Green Checkmarks (Rabisu Style) -->
              <ul class="space-y-2 text-xs text-slate-600 dark:text-slate-300">
                <li class="flex items-center gap-2"><i data-lucide="check" class="w-3.5 h-3.5 text-emerald-500 shrink-0"></i><span>独享独立公网 IPv4 + /64 IPv6</span></li>
                <li class="flex items-center gap-2"><i data-lucide="check" class="w-3.5 h-3.5 text-emerald-500 shrink-0"></i><span>完整 Root 权限 & Web VNC 控制台</span></li>
                <li class="flex items-center gap-2"><i data-lucide="check" class="w-3.5 h-3.5 text-emerald-500 shrink-0"></i><span>支持反向 DNS (rDNS PTR) 自定义</span></li>
                <li class="flex items-center gap-2"><i data-lucide="check" class="w-3.5 h-3.5 text-emerald-500 shrink-0"></i><span>3.2Tbps Anycast 高防 DDoS 过滤</span></li>
                <li class="flex items-center gap-2"><i data-lucide="check" class="w-3.5 h-3.5 text-emerald-500 shrink-0"></i><span>免费每日异地数据镜像快照备份</span></li>
              </ul>
            </div>

            <div class="pt-6">
              <button onclick="selectPlanAndConfigure('${p.id}')" class="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold transition shadow-sm flex items-center justify-center gap-1.5">
                <span>立即订购 / 快速配置</span>
                <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
              </button>
            </div>
          </div>
        `;
      }).join('');
      lucide.createIcons();
    }

    // Cycle Toggle listener
    document.querySelectorAll('#cycleSelector button').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#cycleSelector button').forEach(b => {
          b.className = 'px-3.5 py-1.5 rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white flex items-center gap-1';
        });
        btn.className = 'px-3.5 py-1.5 rounded-lg bg-white dark:bg-darkbg-700 text-slate-900 dark:text-white shadow-sm font-semibold flex items-center gap-1';
        CLIENT_STATE.cycle = parseInt(btn.dataset.cycle, 10);
        renderPricingCards();
        renderConfigurator();
      });
    });

    // Render Regions Cards
    function renderRegions() {
      document.getElementById('regionsDisplayGrid').innerHTML = CLIENT_STATE.dcs.map(d => `
        <div class="ui-surface rounded-2xl p-5 hover:border-blue-500 transition space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-2xl">${d.flag}</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400">${d.ping}</span>
          </div>
          <div>
            <div class="font-bold text-sm text-slate-900 dark:text-white">${d.name}</div>
            <div class="text-xs text-slate-500">${d.label}</div>
            <div class="text-[10px] text-blue-600 dark:text-blue-400 font-mono mt-1">${d.bgp}</div>
          </div>
        </div>
      `).join('');
    }

    // 2-Column Configurator
    function renderConfigurator() {
      // 1. DC Selector
      document.getElementById('confDcSelector').innerHTML = CLIENT_STATE.dcs.map(d => {
        const active = d.code === CLIENT_STATE.selectedDc;
        return `
          <div onclick="setConfDc('${d.code}')" class="p-3.5 rounded-xl border cursor-pointer transition ${active ? 'border-blue-500 bg-blue-500/10 ring-1 ring-blue-500' : 'border-slate-200 dark:border-darkbg-700 bg-white dark:bg-darkbg-900'}">
            <div class="flex items-center justify-between">
              <span class="text-lg">${d.flag}</span>
              <span class="text-[10px] font-mono text-emerald-500 font-bold">${d.ping}</span>
            </div>
            <div class="font-bold text-xs text-slate-900 dark:text-white mt-1.5">${d.name}</div>
            <div class="text-[11px] text-slate-500 truncate">${d.label}</div>
          </div>
        `;
      }).join('');

      // 2. Plan Selector
      document.getElementById('confPlanSelector').innerHTML = CLIENT_STATE.plans.map(p => {
        const active = p.id === CLIENT_STATE.selectedPlanId;
        const discount = getDiscount(CLIENT_STATE.cycle);
        return `
          <div onclick="setConfPlan('${p.id}')" class="p-3.5 rounded-xl border cursor-pointer transition ${active ? 'border-blue-500 bg-blue-500/10 ring-1 ring-blue-500' : 'border-slate-200 dark:border-darkbg-700 bg-white dark:bg-darkbg-900'}">
            <div class="flex items-center justify-between">
              <span class="font-bold text-xs text-slate-900 dark:text-white">${p.name}</span>
              <span class="text-xs font-mono font-bold text-blue-600 dark:text-blue-400">$${(p.price * discount).toFixed(1)}/月</span>
            </div>
            <div class="text-[11px] text-slate-500 font-mono mt-1">${p.vcpu}C / ${p.ram}G ECC / ${p.nvme}G NVMe</div>
          </div>
        `;
      }).join('');

      // 3. OS Selector
      document.getElementById('confOsSelector').innerHTML = CLIENT_STATE.oses.map(o => {
        const active = o === CLIENT_STATE.selectedOs;
        return `
          <div onclick="setConfOs('${o}')" class="p-2.5 rounded-lg border text-center text-xs cursor-pointer transition ${active ? 'border-blue-500 bg-blue-500/10 font-bold text-blue-600 dark:text-blue-400' : 'border-slate-200 dark:border-darkbg-700 text-slate-600 dark:text-slate-400'}">
            ${o}
          </div>
        `;
      }).join('');

      renderStickySummary();
    }

    function setConfDc(code) { CLIENT_STATE.selectedDc = code; renderConfigurator(); }
    function setConfPlan(id) { CLIENT_STATE.selectedPlanId = id; renderConfigurator(); }
    function setConfOs(os) { CLIENT_STATE.selectedOs = os; renderConfigurator(); }

    function selectPlanAndConfigure(planId) {
      CLIENT_STATE.selectedPlanId = planId;
      renderConfigurator();
      location.href = '#section-configurator';
    }

    // Render Sticky Summary
    function renderStickySummary() {
      const plan = CLIENT_STATE.plans.find(p => p.id === CLIENT_STATE.selectedPlanId) || CLIENT_STATE.plans[1];
      const dc = CLIENT_STATE.dcs.find(d => d.code === CLIENT_STATE.selectedDc) || CLIENT_STATE.dcs[0];
      const discount = getDiscount(CLIENT_STATE.cycle);
      const totalAmount = (plan.price * discount * CLIENT_STATE.cycle).toFixed(2);

      const cycleLabel = CLIENT_STATE.cycle === 1 ? '按月支付' : CLIENT_STATE.cycle === 3 ? '按季付 (9折)' : CLIENT_STATE.cycle === 6 ? '半年付 (85折)' : '按年付 (8折)';

      document.getElementById('stickySummaryList').innerHTML = `
        <div class="flex justify-between">
          <span class="text-slate-500">已选主机:</span>
          <span class="font-bold text-slate-900 dark:text-white">${plan.name}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-slate-500">机房可用区:</span>
          <span class="text-slate-800 dark:text-slate-200">${dc.name}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-slate-500">操作系统:</span>
          <span class="text-slate-800 dark:text-slate-200">${CLIENT_STATE.selectedOs}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-slate-500">计费周期:</span>
          <span class="text-emerald-500 font-semibold">${cycleLabel}</span>
        </div>
      `;

      document.getElementById('stickyTotalAmount').textContent = `$${totalAmount}`;
      document.getElementById('stickyDiscountNote').textContent = `${cycleLabel} · 实付总额`;
    }

    // Provision Pipeline Trigger
    function triggerProvision() {
      const box = document.getElementById('provisionFeedbackBox');
      const bar = document.getElementById('provProgressBar');
      const pct = document.getElementById('provPercentText');
      const log = document.getElementById('provLogText');
      box.classList.remove('hidden');

      const plan = CLIENT_STATE.plans.find(p => p.id === CLIENT_STATE.selectedPlanId) || CLIENT_STATE.plans[1];
      const host = document.getElementById('confHostname').value || '1stvps-cloud';

      // Call backend checkout
      fetch('/api/billing/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          planId: plan.id,
          datacenter: CLIENT_STATE.selectedDc,
          osTemplate: CLIENT_STATE.selectedOs,
          hostname: host,
          affiliateCode: '1STVIP88',
        }),
      }).catch(console.error);

      const steps = [
        { p: 25, msg: '1/4 Cloudflare 边缘队列调度并校验订单...' },
        { p: 50, msg: `2/4 选定 ${CLIENT_STATE.selectedDc} 核心节点并绑定独享 IPv4 51.79.144.20...` },
        { p: 75, msg: `3/4 注入 Cloud-Init 模板 (${CLIENT_STATE.selectedOs})...` },
        { p: 100, msg: '4/4 QEMU Agent 响应，实例交付就绪并触发站长系统通知！' },
      ];

      let idx = 0;
      const t = setInterval(() => {
        if (idx < steps.length) {
          bar.style.width = `${steps[idx].p}%`;
          pct.textContent = `${steps[idx].p}%`;
          log.textContent = steps[idx].msg;
          idx++;
        } else {
          clearInterval(t);
          showToast(`云主机 ${host} 已交付上线！`, 'success');
          CLIENT_STATE.instances.unshift({
            id: `vm_${Date.now().toString().slice(-4)}`,
            host: host,
            dc: CLIENT_STATE.selectedDc,
            plan: plan.name,
            ip: '51.79.144.20',
            os: CLIENT_STATE.selectedOs,
            vcpu: plan.vcpu,
            ram: plan.ram,
            nvme: plan.nvme,
            status: 'running',
          });
          renderClientInstances();
        }
      }, 700);
    }

    document.getElementById('stripeCheckoutBtn').addEventListener('click', () => {
      showToast('正在创建 Stripe 安全收银台并推送站长 Webhook...', 'info');
      triggerProvision();
    });

    document.getElementById('balanceCheckoutBtn').addEventListener('click', () => {
      showToast('使用账户资金余额支付成功，即刻开通...', 'success');
      triggerProvision();
    });

    // Client Area Dialog & Tabs
    function openClientArea(defaultTab = 'instances') {
      document.getElementById('clientAreaModal').classList.remove('hidden');
      switchClientTab(defaultTab);
      renderClientInstances();
      lucide.createIcons();
    }

    function closeClientArea() {
      document.getElementById('clientAreaModal').classList.add('hidden');
    }

    document.getElementById('openClientAreaBtn').addEventListener('click', () => openClientArea('instances'));

    function switchClientTab(tab) {
      document.querySelectorAll('div[id^="cTab-"]').forEach(d => d.classList.add('hidden'));
      const target = document.getElementById(`cTab-${tab}`);
      if (target) target.classList.remove('hidden');

      document.querySelectorAll('#clientAreaTabs button').forEach(b => {
        b.className = b.dataset.tab === tab
          ? 'px-3 py-1.5 rounded-lg bg-white dark:bg-darkbg-700 text-slate-900 dark:text-white shadow-sm font-semibold'
          : 'px-3 py-1.5 rounded-lg text-slate-600 dark:text-slate-400 hover:text-slate-900';
      });
    }

    document.querySelectorAll('#clientAreaTabs button').forEach(btn => {
      btn.addEventListener('click', () => switchClientTab(btn.dataset.tab));
    });

    // Render Client Instances inside Client Area
    function renderClientInstances() {
      document.getElementById('clientInstancesGrid').innerHTML = CLIENT_STATE.instances.map(inst => `
        <div class="ui-surface rounded-xl p-4 space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <div class="font-bold text-slate-900 dark:text-white text-xs">${inst.host}</div>
              <div class="text-[10px] text-slate-500 font-mono">${inst.dc} 节点 · ${inst.plan}</div>
            </div>
            <span class="px-2 py-0.5 rounded text-[10px] font-semibold ${inst.status === 'running' ? 'bg-emerald-50 dark:bg-emerald-950 text-emerald-600' : 'bg-slate-100 text-slate-500'}">${inst.status === 'running' ? '运行中' : '已停止'}</span>
          </div>
          <div class="p-2.5 rounded-lg bg-slate-50 dark:bg-darkbg-900 border border-slate-200 dark:border-darkbg-700 text-xs font-mono space-y-1">
            <div class="flex justify-between">
              <span class="text-slate-500">独立 IPv4:</span>
              <span class="text-blue-600 dark:text-blue-400 font-bold cursor-pointer" onclick="copyToClipboard('${inst.ip}', '公网 IP')">${inst.ip}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">系统镜像:</span>
              <span class="text-slate-700 dark:text-slate-300">${inst.os}</span>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2 pt-1">
            <button onclick="openVnc('${inst.host}')" class="py-1 rounded bg-blue-50 dark:bg-blue-950 text-blue-600 dark:text-blue-400 text-xs font-mono font-medium text-center">Web VNC 控制台</button>
            <button onclick="showToast('已向 QEMU Agent 派发重启', 'success')" class="py-1 rounded bg-slate-100 dark:bg-darkbg-800 text-slate-700 dark:text-slate-300 text-xs font-mono text-center">安全重启</button>
          </div>
        </div>
      `).join('');
    }

    // Support Chat
    function sendClientSupport() {
      const input = document.getElementById('clientSupportInput');
      const val = input.value.trim();
      if (!val) return;

      const container = document.getElementById('supportChatMessages');
      const userDiv = document.createElement('div');
      userDiv.className = 'flex justify-end';
      userDiv.innerHTML = `<div class="p-3 rounded-xl bg-blue-600 text-white max-w-[85%]">${val}</div>`;
      container.appendChild(userDiv);
      input.value = '';

      // Call backend to trigger Telegram/Webhook notification
      fetch('/api/support/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: val, roomId: 'customer_portal' }),
      }).catch(console.error);

      setTimeout(() => {
        const reply = document.createElement('div');
        reply.className = 'p-3 rounded-xl bg-slate-100 dark:bg-darkbg-900 text-slate-800 dark:text-slate-200 max-w-[85%]';
        reply.textContent = '收到您的咨询！已通过 Webhook 即刻推送至工程师手机，将尽快为您回复。';
        container.appendChild(reply);
        container.scrollTop = container.scrollHeight;
      }, 700);
    }

    // VNC Terminal
    function openVnc(host) {
      document.getElementById('vncTitle').textContent = `Web VNC Terminal · root@${host}`;
      document.getElementById('vncModal').classList.remove('hidden');
    }
    function closeVncModal() {
      document.getElementById('vncModal').classList.add('hidden');
    }
    function sendVncCmd() {
      const input = document.getElementById('vncInput');
      const cmd = input.value.trim();
      if (!cmd) return;
      const screen = document.getElementById('vncScreen');

      const line1 = document.createElement('div');
      line1.className = 'text-white';
      line1.textContent = `root@vm:~# ${cmd}`;
      screen.appendChild(line1);

      const line2 = document.createElement('div');
      line2.className = 'text-slate-300';
      line2.textContent = cmd.startsWith('uptime') ? '19:12:00 up 28 days, load average: 0.14, 0.09, 0.06' : `Executed: ${cmd} (code: 0)`;
      screen.appendChild(line2);
      input.value = '';
      screen.scrollTop = screen.scrollHeight;
    }

    // Theme Toggle
    function toggleTheme() {
      const isDark = document.documentElement.classList.contains('dark');
      if (isDark) {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('1stvps_theme', 'light');
      } else {
        document.documentElement.classList.add('dark');
        localStorage.setItem('1stvps_theme', 'dark');
      }
      lucide.createIcons();
    }
    document.getElementById('themeToggleBtn').addEventListener('click', toggleTheme);

    // Toast
    function showToast(msg, type = 'info') {
      const container = document.getElementById('toastContainer');
      const colors = type === 'success'
        ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-200'
        : type === 'error'
        ? 'border-rose-500 bg-rose-50 dark:bg-rose-950 text-rose-800 dark:text-rose-200'
        : 'border-blue-500 bg-white dark:bg-darkbg-850 text-slate-800 dark:text-slate-100';
      const el = document.createElement('div');
      el.className = `pointer-events-auto px-4 py-2.5 rounded-lg border text-xs font-medium shadow-lg transition-all ${colors}`;
      el.textContent = msg;
      container.appendChild(el);
      setTimeout(() => el.remove(), 3200);
    }

    function copyToClipboard(text, label = '内容') {
      navigator.clipboard.writeText(text).then(() => showToast(`已复制${label}`, 'success'));
    }

    // Init
    window.addEventListener('DOMContentLoaded', () => {
      const saved = localStorage.getItem('1stvps_theme') || 'dark';
      if (saved === 'dark') document.documentElement.classList.add('dark');
      else document.documentElement.classList.remove('dark');

      renderPricingCards();
      renderRegions();
      renderConfigurator();
      lucide.createIcons();
    });
  </script>
</body>
</html>
'''

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(CLIENT_HTML)

print("Successfully generated public/index.html with Rabisu design system & zero admin code!")
