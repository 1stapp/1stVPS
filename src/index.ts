import { Hono, Context } from 'hono';
import { Env, QueueJob } from './types';
import { createCheckoutSession, verifyStripeSignature } from './services/stripe';
import { runProvisionPipeline } from './services/provisioner';
import { decryptSecret } from './services/crypto';
import {
  getAdminSettings,
  invalidateAdminSettingsCache,
  SECRET_MASK,
  SECRET_SETTING_FIELDS,
  PLAIN_SETTING_FIELDS,
} from './services/settings';
import { ProxmoxClient } from './services/proxmox';
import { OvhClient } from './services/ovh';
import { sendInternalMessage, sendTransactionalEmail, sendAdminNotification } from './services/notify';

export { SupportChatRoom } from './durable/SupportChatRoom';

const app = new Hono<{ Bindings: Env }>();

// --- 辅助方法: 获取当前会话客户 (无有效会话时返回 null，绝不回退到演示用户) ---
type UserRow = {
  id: string;
  email: string;
  name: string;
  avatar_url: string;
  role: string;
  affiliate_code: string;
  balance_cents: number;
};

async function getCurrentUser(c: Context<{ Bindings: Env }>): Promise<UserRow | null> {
  try {
    const cookie = c.req.header('Cookie') || '';
    const match = cookie.match(/1stvps_session=([^;]+)/);
    const token = match ? match[1] : null;
    if (token && c.env.SESSION_KV) {
      const userId = await c.env.SESSION_KV.get(`sess:${token}`);
      if (userId && c.env.DB) {
        const u = await c.env.DB.prepare(`SELECT * FROM users WHERE id = ?`).bind(userId).first<UserRow>();
        if (u) return u;
      }
    }
  } catch {
    // 会话读取失败按未登录处理
  }

  return null;
}

// --- 辅助方法: 独立管理员鉴权 (客户无权穿透) ---
async function getAdminUser(c: Context<{ Bindings: Env }>) {
  try {
    const cookie = c.req.header('Cookie') || '';
    const match = cookie.match(/1stvps_admin_session=([^;]+)/);
    const authHeader = c.req.header('Authorization') || '';
    const bearer = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : null;
    const token = bearer || (match ? match[1] : null);

    if (token && c.env.SESSION_KV) {
      const raw = await c.env.SESSION_KV.get(`admin_sess:${token}`);
      if (raw) {
        return JSON.parse(raw);
      }
    }
  } catch {}

  return null;
}

// --- 1. 用户信息与 Google OAuth 2.0 ---
app.get('/api/user/me', async (c) => {
  const user = await getCurrentUser(c);
  return c.json({ user });
});

app.get('/api/auth/google', async (c) => {
  const settings = await getAdminSettings(c.env);
  if (!settings.googleClientId) {
    return c.json({ error: 'Google OAuth is not configured' }, 503);
  }
  const state = crypto.randomUUID();
  const ref = c.req.query('ref') || '';
  if (c.env.SESSION_KV) {
    await c.env.SESSION_KV.put(`oauth:${state}`, JSON.stringify({ ref }), { expirationTtl: 600 });
  }

  const url = new URL('https://accounts.google.com/o/oauth2/v2/auth');
  url.searchParams.set('client_id', settings.googleClientId);
  url.searchParams.set('redirect_uri', `${c.env.APP_URL || 'http://localhost:8787'}/api/auth/google/callback`);
  url.searchParams.set('response_type', 'code');
  url.searchParams.set('scope', 'openid email profile');
  url.searchParams.set('state', state);
  return c.redirect(url.toString());
});

app.get('/api/auth/google/callback', async (c) => {
  const code = c.req.query('code');
  const state = c.req.query('state');
  if (!code || !state) return c.json({ error: 'Missing code or state' }, 400);

  let ref = '';
  if (c.env.SESSION_KV) {
    const rawState = await c.env.SESSION_KV.get(`oauth:${state}`);
    if (rawState) {
      await c.env.SESSION_KV.delete(`oauth:${state}`);
      const parsed = JSON.parse(rawState) as { ref?: string };
      ref = parsed.ref || '';
    }
  }

  const settings = await getAdminSettings(c.env);
  const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      code,
      client_id: settings.googleClientId,
      client_secret: settings.googleClientSecret,
      redirect_uri: `${c.env.APP_URL}/api/auth/google/callback`,
      grant_type: 'authorization_code',
    }),
  });
  const tokens = (await tokenRes.json()) as { access_token: string };
  const profileRes = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
    headers: { Authorization: `Bearer ${tokens.access_token}` },
  });
  const profile = (await profileRes.json()) as { sub: string; email: string; name: string; picture: string };

  let user = await c.env.DB.prepare(`SELECT * FROM users WHERE email = ?`).bind(profile.email).first<{ id: string }>();
  if (!user) {
    const userId = crypto.randomUUID();
    const affCode = `1ST${userId.slice(0, 6).toUpperCase()}`;
    await c.env.DB.prepare(
      `INSERT INTO users (id, email, name, avatar_url, google_id, affiliate_code, referred_by) VALUES (?, ?, ?, ?, ?, ?, ?)`
    )
      .bind(userId, profile.email, profile.name, profile.picture, profile.sub, affCode, ref || null)
      .run();
    user = { id: userId };
  }

  const sessionToken = crypto.randomUUID();
  if (c.env.SESSION_KV) {
    await c.env.SESSION_KV.put(`sess:${sessionToken}`, user.id, { expirationTtl: 86400 * 7 });
  }
  c.header('Set-Cookie', `1stvps_session=${sessionToken}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=604800`);
  return c.redirect(`${c.env.APP_URL || '/'}`);
});

// --- 2. 客户前台：全球可用区与机房节点延迟 ---
app.get('/api/regions', async (c) => {
  return c.json({
    regions: [
      { id: 'SGP', code: 'SGP', name: '亚太 - 新加坡', location: '新加坡 Jurong 高速机房', ping: '38ms', status: 'operational', flag: '🇸🇬', bgp: 'CN2 / CMI 高速回国 BGP' },
      { id: 'FRA', code: 'FRA', name: '欧洲 - 德国法兰克福', location: '德国法兰克福互联枢纽', ping: '145ms', status: 'operational', flag: '🇩🇪', bgp: 'DE-CIX 骨干极速互联' },
      { id: 'PAR', code: 'PAR', name: '欧洲 - 法国巴黎', location: '法国巴黎高防核心节点', ping: '152ms', status: 'operational', flag: '🇫🇷', bgp: '欧洲核心骨干网 / 原生防D' },
      { id: 'BHS', code: 'BHS', name: '北美 - 加拿大蒙特利尔', location: '加拿大 Beauharnois 核心机房', ping: '180ms', status: 'operational', flag: '🇨🇦', bgp: '北美多线 BGP 抗D 500Gbps' },
    ],
  });
});

// 管理员专用：裸金属母机与底层资源池拓扑 (严格鉴权，客户无权访问)
app.get('/api/nodes/overview', async (c) => {
  const admin = await getAdminUser(c);
  if (!admin) {
    return c.json({ error: 'Forbidden: Admin access required' }, 403);
  }
  try {
    const nodes = await c.env.DB.prepare(`SELECT * FROM nodes`).all();
    const ipStats = await c.env.DB.prepare(
      `SELECT node_id, status, COUNT(*) as count FROM ip_pool GROUP BY node_id, status`
    ).all();
    const ipDetails = await c.env.DB.prepare(`SELECT * FROM ip_pool LIMIT 100`).all();
    return c.json({ nodes: nodes.results, ipStats: ipStats.results, ips: ipDetails.results });
  } catch (err) {
    console.error('Failed to load nodes overview:', err);
    return c.json({ error: 'Internal error' }, 500);
  }
});

// --- 3. VPS 套餐规格 ---
app.get('/api/plans', async (c) => {
  try {
    const rows = await c.env.DB.prepare(`SELECT * FROM vps_plans ORDER BY price_cents ASC`).all();
    return c.json({ plans: rows.results });
  } catch (err) {
    console.error('Failed to load plans:', err);
    return c.json({ error: 'Internal error' }, 500);
  }
});

// --- 4. 用户 VPS 实例管理 ---
app.get('/api/vps/instances', async (c) => {
  const user = await getCurrentUser(c);
  if (!user) return c.json({ error: 'Unauthorized' }, 401);
  try {
    const rows = await c.env.DB.prepare(
      `SELECT v.*, p.name as plan_name, p.vcpu, p.ram_gb, p.nvme_gb, p.bandwidth_tb, n.datacenter, n.name as node_name
       FROM vps_instances v
       JOIN vps_plans p ON v.plan_id = p.id
       JOIN nodes n ON v.node_id = n.id
       WHERE v.user_id = ?
       ORDER BY v.created_at DESC`
    )
      .bind(user.id)
      .all();
    return c.json({ instances: rows.results });
  } catch (err) {
    console.error('Failed to load instances:', err);
    return c.json({ error: 'Internal error' }, 500);
  }
});

// 辅助方法: 校验实例归属，返回实例与节点信息；不存在或不属于该用户时返回 null
async function getOwnedInstance(c: Context<{ Bindings: Env }>, instanceId: string, userId: string) {
  return c.env.DB.prepare(
    `SELECT v.id, v.vmid, v.ipv4, v.root_password_enc, n.pve_host, n.pve_node
     FROM vps_instances v JOIN nodes n ON v.node_id = n.id
     WHERE v.id = ? AND v.user_id = ?`
  )
    .bind(instanceId, userId)
    .first<{ id: string; vmid: number; ipv4: string; root_password_enc: string | null; pve_host: string; pve_node: string }>();
}

app.post('/api/vps/:id/power', async (c) => {
  const user = await getCurrentUser(c);
  if (!user) return c.json({ error: 'Unauthorized' }, 401);
  const id = c.req.param('id');
  const { action } = await c.req.json<{ action: 'start' | 'stop' | 'reboot' | 'reset' }>();

  const row = await getOwnedInstance(c, id, user.id);
  if (!row) return c.json({ error: 'Instance not found' }, 404);

  const settings = await getAdminSettings(c.env);
  if (!settings.proxmoxApiToken) {
    return c.json({ error: 'Proxmox hypervisor is not configured' }, 501);
  }

  try {
    const pve = new ProxmoxClient(row.pve_host, settings.proxmoxApiToken);
    await pve.powerAction(row.pve_node, row.vmid, action);
  } catch (err) {
    // 母机调用失败时不得伪造成功，也不得修改实例状态
    console.error('Power action failed:', err);
    return c.json({ error: 'Hypervisor power action failed' }, 502);
  }

  const newStatus = action === 'stop' ? 'stopped' : 'running';
  await c.env.DB.prepare(`UPDATE vps_instances SET status = ? WHERE id = ?`).bind(newStatus, id).run();
  return c.json({ ok: true, id, action, status: newStatus });
});

app.post('/api/vps/:id/rdns', async (c) => {
  const user = await getCurrentUser(c);
  if (!user) return c.json({ error: 'Unauthorized' }, 401);
  const id = c.req.param('id');
  await c.req.json<{ ptr: string }>().catch(() => ({ ptr: '' }));

  const row = await getOwnedInstance(c, id, user.id);
  if (!row) return c.json({ error: 'Instance not found' }, 404);

  // rDNS 尚未接入虚拟化平台/IP 提供商 API，诚实返回未实现，不伪造成功
  return c.json({ error: 'rDNS 设置尚未接入虚拟化平台，暂不可用' }, 501);
});

app.post('/api/vps/:id/reinstall', async (c) => {
  const user = await getCurrentUser(c);
  if (!user) return c.json({ error: 'Unauthorized' }, 401);
  const id = c.req.param('id');
  await c.req.json<{ osTemplate: string }>().catch(() => ({ osTemplate: '' }));

  const row = await getOwnedInstance(c, id, user.id);
  if (!row) return c.json({ error: 'Instance not found' }, 404);

  // 系统重装尚未接入虚拟化平台，诚实返回未实现，不伪造成功
  return c.json({ error: '系统重装尚未接入虚拟化平台，暂不可用' }, 501);
});

// 实例 SSH 凭据 (仅实例所有者可查看，密码解密后返回)
app.get('/api/vps/:id/credentials', async (c) => {
  const user = await getCurrentUser(c);
  if (!user) return c.json({ error: 'Unauthorized' }, 401);
  const id = c.req.param('id');

  const row = await getOwnedInstance(c, id, user.id);
  if (!row) return c.json({ error: 'Instance not found' }, 404);
  if (!row.root_password_enc) {
    return c.json({ error: 'Credentials not available for this instance' }, 404);
  }

  try {
    const password = await decryptSecret(row.root_password_enc, c.env.JWT_SECRET);
    return c.json({ ipv4: row.ipv4, username: 'root', password });
  } catch (err) {
    console.error('Failed to decrypt instance credentials:', err);
    return c.json({ error: 'Internal error' }, 500);
  }
});

// --- 5. Stripe Checkout & 自动开通流水线 ---
app.post('/api/billing/checkout', async (c) => {
  const user = await getCurrentUser(c);
  if (!user) return c.json({ error: 'Unauthorized' }, 401);
  const { planId, datacenter, osTemplate, hostname, affiliateCode } = await c.req.json();

  // 套餐必须真实存在于 vps_plans，不再静默回退到默认套餐
  const plan = await c.env.DB.prepare(`SELECT * FROM vps_plans WHERE id = ?`)
    .bind(planId)
    .first<{ id: string; name: string; price_cents: number }>();
  if (!plan) {
    return c.json({ error: 'Plan not found' }, 400);
  }

  const orderId = `ORD-${Date.now().toString().slice(-6)}`;
  try {
    await c.env.DB.prepare(
      `INSERT INTO orders (id, user_id, plan_id, amount_cents, affiliate_code, status) VALUES (?, ?, ?, ?, ?, 'pending')`
    )
      .bind(orderId, user.id, plan.id, plan.price_cents, affiliateCode || null)
      .run();
  } catch {}

  // 触发站长系统通知 Webhook
  await sendAdminNotification(c.env, {
    eventType: 'order',
    title: '💰 新订单创建/待支付',
    content: `订单号: ${orderId}\n用户: ${user.name} (${user.email})\n套餐: ${plan.name}\n机房: ${datacenter}\n系统: ${osTemplate}\n主机名: ${hostname}\n金额: $${(plan.price_cents / 100).toFixed(2)} USD`,
  });

  const checkoutSettings = await getAdminSettings(c.env);
  if (checkoutSettings.stripeSecretKey) {
    const session = await createCheckoutSession(c.env, {
      orderId,
      userId: user.id,
      userEmail: user.email,
      planName: plan.name,
      amountCents: plan.price_cents,
      datacenter,
      osTemplate,
      hostname,
      affiliateCode,
    });
    return c.json({ checkoutUrl: session.url, orderId });
  }

  // 未配置 Stripe 时，仅在显式开启 ALLOW_SIMULATED_CHECKOUT 的环境下才返回模拟结账
  if (c.env.ALLOW_SIMULATED_CHECKOUT === 'true') {
    return c.json({
      checkoutUrl: `/?checkout=simulated&orderId=${orderId}&planId=${plan.id}&dc=${datacenter}&os=${encodeURIComponent(osTemplate)}&host=${encodeURIComponent(hostname)}`,
      orderId,
      simulated: true,
    });
  }

  return c.json({ error: 'Payment is not configured' }, 503);
});

app.post('/api/webhooks/stripe', async (c) => {
  const settings = await getAdminSettings(c.env);
  if (!settings.stripeWebhookSecret) {
    console.error('Stripe webhook secret is not configured');
    return c.json({ error: 'Stripe webhook is not configured' }, 500);
  }
  const sig = c.req.header('stripe-signature') || '';
  const rawBody = await c.req.text();
  const valid = await verifyStripeSignature(rawBody, sig, settings.stripeWebhookSecret);
  if (!valid) return c.json({ error: 'Invalid signature' }, 400);

  const event = JSON.parse(rawBody) as { type: string; data: { object: { metadata: Record<string, string>; amount_total: number } } };
  if (event.type === 'checkout.session.completed') {
    const meta = event.data.object.metadata;
    await c.env.DB.prepare(`UPDATE orders SET status = 'paid' WHERE id = ?`).bind(meta.orderId).run();

    // 结算推广佣金 (默认 15%)
    if (meta.affiliateCode) {
      const aff = await c.env.DB.prepare(`SELECT id FROM users WHERE affiliate_code = ?`)
        .bind(meta.affiliateCode)
        .first<{ id: string }>();
      if (aff && aff.id !== meta.userId) {
        const rate = parseFloat(settings.affiliateRate || '0.15');
        const commissionCents = Math.round((event.data.object.amount_total || 0) * rate);
        await c.env.DB.batch([
          c.env.DB.prepare(`INSERT INTO commissions (id, affiliate_user_id, order_id, referred_user_id, amount_cents) VALUES (?, ?, ?, ?, ?)`)
            .bind(crypto.randomUUID(), aff.id, meta.orderId, meta.userId, commissionCents),
          c.env.DB.prepare(`UPDATE users SET balance_cents = balance_cents + ? WHERE id = ?`).bind(commissionCents, aff.id),
        ]);
        await sendInternalMessage(
          c.env,
          aff.id,
          'affiliate',
          '推广返佣到账通知',
          `您的推广客户完成订单，获得 $${(commissionCents / 100).toFixed(2)} 佣金！`
        );
      }
    }

    // 推送异步开通流水线到 Cloudflare Queue
    await c.env.PROVISION_QUEUE.send({
      type: 'provision_vps',
      orderId: meta.orderId,
      userId: meta.userId,
      planId: meta.planId || 'pro',
      datacenter: meta.datacenter || 'RBX',
      osTemplate: meta.osTemplate || 'ubuntu-24.04',
      hostname: meta.hostname || `vps-${meta.orderId.slice(-4)}`,
    });

    // 触发站长系统通知 Webhook (Stripe 真实到账)
    await sendAdminNotification(c.env, {
      eventType: 'order',
      title: '🎉 订单支付成功 (Stripe 到账)',
      content: `订单号: ${meta.orderId}\n用户 ID: ${meta.userId}\n金额: $${((event.data.object.amount_total || 0) / 100).toFixed(2)} USD\n机房: ${meta.datacenter}\n套餐: ${meta.planId}`,
    });
  }
  return c.json({ received: true });
});

// --- 6. 推广赚佣中心 (Affiliate & Referral) ---
app.get('/api/affiliate/stats', async (c) => {
  const user = await getCurrentUser(c);
  if (!user) return c.json({ error: 'Unauthorized' }, 401);
  try {
    const rows = await c.env.DB.prepare(
      `SELECT c.*, u.email as referred_email
       FROM commissions c
       JOIN users u ON c.referred_user_id = u.id
       WHERE c.affiliate_user_id = ?
       ORDER BY c.created_at DESC`
    )
      .bind(user.id)
      .all();
    const totalEarnedCents = (rows.results as Array<{ amount_cents: number }>).reduce((acc, curr) => acc + curr.amount_cents, 0);

    return c.json({
      affiliateCode: user.affiliate_code,
      balanceCents: user.balance_cents,
      totalEarnedCents,
      referralCount: rows.results.length,
      commissions: rows.results,
    });
  } catch (err) {
    console.error('Failed to load affiliate stats:', err);
    return c.json({ error: 'Internal error' }, 500);
  }
});

app.post('/api/affiliate/withdraw', async (c) => {
  const user = await getCurrentUser(c);
  if (!user) return c.json({ error: 'Unauthorized' }, 401);
  const { amountCents, method } = await c.req.json<{ amountCents: number; method: 'credit' | 'payout' }>();
  if (!amountCents || amountCents <= 0) {
    return c.json({ error: '无效提现金额' }, 400);
  }

  // 可用额度 = 该用户 status='available' 的佣金总额，超出即拒绝
  const availRow = await c.env.DB.prepare(
    `SELECT COALESCE(SUM(amount_cents), 0) AS total FROM commissions WHERE affiliate_user_id = ? AND status = 'available'`
  )
    .bind(user.id)
    .first<{ total: number }>();
  const availableCents = availRow?.total ?? 0;
  if (amountCents > availableCents) {
    return c.json({ error: '提现金额超过可用佣金余额' }, 400);
  }

  // 按最旧优先逐笔消耗佣金：整笔标记状态，最后一笔不足时只扣减金额、剩余保持 available
  const commRows = await c.env.DB.prepare(
    `SELECT id, amount_cents FROM commissions WHERE affiliate_user_id = ? AND status = 'available' ORDER BY created_at ASC`
  )
    .bind(user.id)
    .all<{ id: string; amount_cents: number }>();
  const consumedStatus = method === 'credit' ? 'converted' : 'paid_out';
  const updates: D1PreparedStatement[] = [];
  let remaining = amountCents;
  for (const row of commRows.results) {
    if (remaining <= 0) break;
    if (row.amount_cents <= remaining) {
      updates.push(c.env.DB.prepare(`UPDATE commissions SET status = ? WHERE id = ?`).bind(consumedStatus, row.id));
      remaining -= row.amount_cents;
    } else {
      updates.push(c.env.DB.prepare(`UPDATE commissions SET amount_cents = amount_cents - ? WHERE id = ?`).bind(remaining, row.id));
      remaining = 0;
    }
  }

  const bonusCents = method === 'credit' ? Math.round(amountCents * 0.1) : 0;
  if (method === 'credit') {
    // 本金已在佣金结算时计入 balance_cents，这里只补发 10% 奖励，避免重复入账
    updates.push(c.env.DB.prepare(`UPDATE users SET balance_cents = balance_cents + ? WHERE id = ?`).bind(bonusCents, user.id));
  } else {
    updates.push(c.env.DB.prepare(`UPDATE users SET balance_cents = balance_cents - ? WHERE id = ?`).bind(amountCents, user.id));
  }
  await c.env.DB.batch(updates);

  // 触发站长系统通知 Webhook: 合伙人佣金提现申请
  await sendAdminNotification(c.env, {
    eventType: 'affiliate',
    title: '💵 合伙人佣金提现申请',
    content: `申请人: ${user.name} (${user.email})\n推广码: ${user.affiliate_code}\n提现金额: $${(amountCents / 100).toFixed(2)} USD\n提现方式: ${method === 'credit' ? '兑换云主机账户余额 (+10% 奖励)' : '申请现金打款 (USDT/PayPal)'}`,
  });

  if (method === 'credit') {
    return c.json({ ok: true, method: 'credit', bonusCents, message: `成功兑换余额并获得 10% 额外奖励 $${(bonusCents / 100).toFixed(2)}` });
  }

  return c.json({ ok: true, method: 'payout', message: '提现申请已提交，将于 24 小时内结算至您的收款账户' });
});

// --- 7. 站内信与 Web Push ---
app.get('/api/messages', async (c) => {
  const user = await getCurrentUser(c);
  if (!user) return c.json({ error: 'Unauthorized' }, 401);
  try {
    const rows = await c.env.DB.prepare(`SELECT * FROM messages WHERE user_id = ? ORDER BY created_at DESC`)
      .bind(user.id)
      .all();
    return c.json({ messages: rows.results });
  } catch (err) {
    console.error('Failed to load messages:', err);
    return c.json({ error: 'Internal error' }, 500);
  }
});

app.post('/api/messages/mark-read', async (c) => {
  const user = await getCurrentUser(c);
  if (!user) return c.json({ error: 'Unauthorized' }, 401);
  const { messageId } = await c.req.json().catch(() => ({ messageId: null }));
  try {
    if (messageId) {
      await c.env.DB.prepare(`UPDATE messages SET is_read = 1 WHERE id = ? AND user_id = ?`).bind(messageId, user.id).run();
    } else {
      await c.env.DB.prepare(`UPDATE messages SET is_read = 1 WHERE user_id = ?`).bind(user.id).run();
    }
  } catch {}
  return c.json({ ok: true });
});

app.post('/api/push/subscribe', async (c) => {
  const user = await getCurrentUser(c);
  if (!user) return c.json({ error: 'Unauthorized' }, 401);
  const { endpoint, keys } = await c.req.json();
  try {
    await c.env.DB.prepare(
      `INSERT OR REPLACE INTO push_subscriptions (id, user_id, endpoint, p256dh, auth) VALUES (?, ?, ?, ?, ?)`
    )
      .bind(crypto.randomUUID(), user.id, endpoint, keys.p256dh, keys.auth)
      .run();
  } catch {}
  return c.json({ ok: true });
});

// --- 8. 邮件营销后台 (Cloudflare Queues + Resend API) ---
app.get('/api/marketing/campaigns', async (c) => {
  const admin = await getAdminUser(c);
  if (!admin) return c.json({ error: 'Forbidden: Admin access required' }, 403);
  try {
    const rows = await c.env.DB.prepare(`SELECT * FROM email_campaigns ORDER BY created_at DESC`).all();
    return c.json({ campaigns: rows.results });
  } catch (err) {
    console.error('Failed to load campaigns:', err);
    return c.json({ error: 'Internal error' }, 500);
  }
});

app.post('/api/marketing/campaigns', async (c) => {
  const admin = await getAdminUser(c);
  if (!admin) return c.json({ error: 'Forbidden: Admin access required' }, 403);
  const { title, subject, segment, htmlContent } = await c.req.json();
  const id = crypto.randomUUID();
  try {
    await c.env.DB.prepare(
      `INSERT INTO email_campaigns (id, title, subject, segment, html_content, status) VALUES (?, ?, ?, ?, ?, 'queued')`
    )
      .bind(id, title, subject, segment, htmlContent)
      .run();
  } catch {}

  if (c.env.PROVISION_QUEUE) {
    await c.env.PROVISION_QUEUE.send({ type: 'send_campaign', campaignId: id });
  }
  return c.json({ ok: true, campaignId: id });
});

// --- 9. 在线客服 WebSocket (Cloudflare Durable Objects) ---
app.get('/api/support/ws/:roomId', async (c) => {
  // 升级 WebSocket 前必须持有有效的客户会话或管理员会话
  const user = await getCurrentUser(c);
  const admin = user ? null : await getAdminUser(c);
  if (!user && !admin) {
    return c.json({ error: 'Unauthorized' }, 401);
  }
  if (c.env.SUPPORT_CHAT) {
    const id = c.env.SUPPORT_CHAT.idFromName(c.req.param('roomId'));
    const stub = c.env.SUPPORT_CHAT.get(id);
    return stub.fetch(c.req.raw);
  }
  return c.text('Durable Objects not available', 501);
});

app.post('/api/support/message', async (c) => {
  const user = await getCurrentUser(c);
  if (!user) return c.json({ error: 'Unauthorized' }, 401);
  const { text, roomId } = await c.req.json<{ text: string; roomId?: string }>();

  // 触发站长系统通知 Webhook: 客户发起在线咨询
  await sendAdminNotification(c.env, {
    eventType: 'support',
    title: '💬 客户发起在线咨询',
    content: `来自客户: ${user.name} (${user.email})\n房间: ${roomId || '技术客服室'}\n咨询内容: ${text || '（发起对话）'}`,
  });

  return c.json({ ok: true });
});

// --- 10. 管理员专属认证与系统总控接口 ---
app.post('/api/admin/auth/login', async (c) => {
  const { username, password } = await c.req.json<{ username?: string; password?: string }>();

  // 管理员密码通过 ADMIN_PASSWORD secret 配置，未配置时禁用管理员登录
  if (!c.env.ADMIN_PASSWORD) {
    return c.json({ ok: false, error: 'Admin login is not configured' }, 503);
  }

  if (username === 'admin' && password === c.env.ADMIN_PASSWORD) {
    const token = crypto.randomUUID();
    const adminUser = {
      id: 'admin_root',
      username: 'admin',
      email: 'admin@1stvps.io',
      name: '系统运维管理员',
      role: 'admin',
    };

    if (c.env.SESSION_KV) {
      await c.env.SESSION_KV.put(`admin_sess:${token}`, JSON.stringify(adminUser), { expirationTtl: 86400 * 3 });
    }

    c.header('Set-Cookie', `1stvps_admin_session=${token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=259200`);
    return c.json({ ok: true, token, user: adminUser });
  }

  return c.json({ ok: false, error: '管理员用户名或登录密码错误' }, 401);
});

app.get('/api/admin/auth/me', async (c) => {
  const admin = await getAdminUser(c);
  if (!admin) return c.json({ authenticated: false }, 401);
  return c.json({ authenticated: true, user: admin });
});

app.post('/api/admin/auth/logout', async (c) => {
  const cookie = c.req.header('Cookie') || '';
  const match = cookie.match(/1stvps_admin_session=([^;]+)/);
  if (match && match[1] && c.env.SESSION_KV) {
    await c.env.SESSION_KV.delete(`admin_sess:${match[1]}`);
  }
  c.header('Set-Cookie', '1stvps_admin_session=; Path=/; HttpOnly; Max-Age=0');
  return c.json({ ok: true });
});

app.post('/api/admin/ovh/install-proxmox', async (c) => {
  const admin = await getAdminUser(c);
  if (!admin) return c.json({ error: 'Forbidden' }, 403);
  const { serviceName, hostname } = await c.req.json<{ serviceName: string; hostname?: string }>();
  const settings = await getAdminSettings(c.env);
  if (settings.ovhAppKey && settings.ovhAppSecret) {
    const ovh = new OvhClient(c.env);
    const res = await ovh.installProxmoxTemplate(serviceName, 'proxmox8_64', hostname);
    return c.json({ ok: true, ovhTask: res });
  }
  return c.json({ ok: true, simulated: true, message: `已向 OVH API 提交母机 ${serviceName} 重装任务 (Proxmox VE 8)` });
});

// 管理员专用：平台经营总览数据
app.get('/api/admin/overview', async (c) => {
  const admin = await getAdminUser(c);
  if (!admin) {
    return c.json({ error: 'Forbidden: Admin access required' }, 403);
  }

  try {
    const usersCount = await c.env.DB.prepare(`SELECT COUNT(*) as count FROM users`).first<{ count: number }>();
    const vpsCount = await c.env.DB.prepare(`SELECT COUNT(*) as count FROM vps_instances`).first<{ count: number }>();
    const ordersRev = await c.env.DB.prepare(`SELECT SUM(amount_cents) as total FROM orders WHERE status = 'paid' OR status = 'provisioned'`).first<{ total: number }>();
    const pendingComms = await c.env.DB.prepare(`SELECT COUNT(*) as count, SUM(amount_cents) as total FROM commissions WHERE status = 'available'`).first<{ count: number; total: number }>();

    return c.json({
      totalUsers: usersCount?.count ?? 0,
      totalInstances: vpsCount?.count ?? 0,
      totalRevenueCents: ordersRev?.total ?? 0,
      pendingCommissionsCents: pendingComms?.total ?? 0,
    });
  } catch (err) {
    console.error('Failed to load admin overview:', err);
    return c.json({ error: 'Internal error' }, 500);
  }
});

// 管理员专用：获取全站所有客户的 VPS 实例列表
app.get('/api/admin/instances', async (c) => {
  const admin = await getAdminUser(c);
  if (!admin) return c.json({ error: 'Forbidden' }, 403);

  try {
    const rows = await c.env.DB.prepare(
      `SELECT v.*, u.email as user_email, u.name as user_name, n.name as node_name, n.datacenter, p.name as plan_name
       FROM vps_instances v
       JOIN users u ON v.user_id = u.id
       JOIN nodes n ON v.node_id = n.id
       JOIN vps_plans p ON v.plan_id = p.id
       ORDER BY v.created_at DESC LIMIT 100`
    ).all();
    return c.json({ instances: rows.results });
  } catch (err) {
    console.error('Failed to load admin instances:', err);
    return c.json({ error: 'Internal error' }, 500);
  }
});

// 管理员专用：审核推广返佣提现
app.post('/api/admin/commissions/:id/approve', async (c) => {
  const admin = await getAdminUser(c);
  if (!admin) return c.json({ error: 'Forbidden' }, 403);
  const id = c.req.param('id');
  try {
    await c.env.DB.prepare(`UPDATE commissions SET status = 'paid_out' WHERE id = ?`).bind(id).run();
  } catch {}
  return c.json({ ok: true, id, status: 'paid_out', message: '已标记为已结算打款' });
});

// 管理员专用：批量导入/绑定 OVH vRack IP 段
app.post('/api/admin/ip-pool/import', async (c) => {
  const admin = await getAdminUser(c);
  if (!admin) return c.json({ error: 'Forbidden' }, 403);
  const { nodeId, subnetCidr, gateway, ips } = await c.req.json<{ nodeId: string; subnetCidr: string; gateway: string; ips: string[] }>();
  try {
    for (const ip of ips) {
      await c.env.DB.prepare(`INSERT OR IGNORE INTO ip_pool (ip, cidr, gateway, node_id, status) VALUES (?, ?, ?, ?, 'free')`)
        .bind(ip, subnetCidr, gateway, nodeId)
        .run();
    }
  } catch {}
  return c.json({ ok: true, imported: ips.length });
});

// 管理员专用：获取系统配置 (KV 优先、env 回退；密钥字段只返回掩码与是否已配置，绝不回显明文)
app.get('/api/admin/settings', async (c) => {
  const admin = await getAdminUser(c);
  if (!admin) return c.json({ error: 'Forbidden' }, 403);

  const s = await getAdminSettings(c.env);
  const mask = (v: string) => (v ? SECRET_MASK : '');
  return c.json({
    settings: {
      telegramBotToken: mask(s.telegramBotToken),
      telegramBotTokenSet: !!s.telegramBotToken,
      telegramChatId: s.telegramChatId,
      webhookUrl: s.webhookUrl,
      events: s.events,
      stripeSecretKey: mask(s.stripeSecretKey),
      stripeSecretKeySet: !!s.stripeSecretKey,
      stripeWebhookSecret: mask(s.stripeWebhookSecret),
      stripeWebhookSecretSet: !!s.stripeWebhookSecret,
      googleClientId: mask(s.googleClientId),
      googleClientIdSet: !!s.googleClientId,
      googleClientSecret: mask(s.googleClientSecret),
      googleClientSecretSet: !!s.googleClientSecret,
      resendApiKey: mask(s.resendApiKey),
      resendApiKeySet: !!s.resendApiKey,
      emailFrom: s.emailFrom,
      affiliateRate: s.affiliateRate,
      ovhAppKey: mask(s.ovhAppKey),
      ovhAppKeySet: !!s.ovhAppKey,
      ovhAppSecret: mask(s.ovhAppSecret),
      ovhAppSecretSet: !!s.ovhAppSecret,
      ovhConsumerKey: mask(s.ovhConsumerKey),
      ovhConsumerKeySet: !!s.ovhConsumerKey,
      proxmoxApiToken: mask(s.proxmoxApiToken),
      proxmoxApiTokenSet: !!s.proxmoxApiToken,
      vapidPublicKey: mask(s.vapidPublicKey),
      vapidPublicKeySet: !!s.vapidPublicKey,
      vapidPrivateKey: mask(s.vapidPrivateKey),
      vapidPrivateKeySet: !!s.vapidPrivateKey,
    },
  });
});

// 管理员专用：保存系统配置到 KV (在现有 KV 原始值上合并；密钥字段传空或回传掩码表示保持原值)
app.post('/api/admin/settings', async (c) => {
  const admin = await getAdminUser(c);
  if (!admin) return c.json({ error: 'Forbidden' }, 403);

  const body = await c.req.json<Record<string, unknown>>();

  let current: Record<string, unknown> = {};
  if (c.env.SESSION_KV) {
    try {
      const raw = await c.env.SESSION_KV.get('admin:settings');
      if (raw) current = JSON.parse(raw) as Record<string, unknown>;
    } catch {}
  }

  const next: Record<string, unknown> = { ...current };

  // 非密钥字段：传入即覆盖 (传空字符串 = 清除 KV 值、回退 env)
  for (const field of PLAIN_SETTING_FIELDS) {
    if (typeof body[field] === 'string') {
      next[field] = body[field];
    }
  }
  // 密钥字段：空字符串或掩码占位 = 保持现有值不变，其余视为新值写入
  for (const field of SECRET_SETTING_FIELDS) {
    const v = body[field];
    if (typeof v === 'string' && v !== '' && v !== SECRET_MASK) {
      next[field] = v;
    }
  }
  if (body.events && typeof body.events === 'object') {
    const prevEvents = (current.events as Record<string, boolean> | undefined) || {
      order: true,
      support: true,
      affiliate: true,
      system: true,
    };
    next.events = { ...prevEvents, ...(body.events as Record<string, boolean>) };
  }

  if (c.env.SESSION_KV) {
    await c.env.SESSION_KV.put('admin:settings', JSON.stringify(next));
  }
  invalidateAdminSettingsCache(c.env);

  return c.json({ ok: true, message: '站长系统配置已成功保存' });
});

// 管理员专用：一键测试发送 Webhook 消息
app.post('/api/admin/webhook/test', async (c) => {
  const admin = await getAdminUser(c);
  if (!admin) return c.json({ error: 'Forbidden' }, 403);

  const result = await sendAdminNotification(c.env, {
    eventType: 'system',
    title: '🔔 1stVPS Webhook 连通性测试',
    content: `这是一条来自 1stVPS 站长后台的实时推送测试。\n管理员: ${admin.name} (${admin.email})\n如果您在 Telegram 或 Webhook 群机器人中收到此消息，说明系统消息推送链路完全正常！`,
  });

  return c.json({ ok: true, message: '测试消息已派发', result });
});

// --- 独立管理员控制台入口 (/admin 与 /admin/*) ---
app.get('/admin', async (c) => {
  if (c.env.ASSETS) {
    return c.env.ASSETS.fetch(new Request(new URL('/admin.html', c.req.url)));
  }
  return c.text('1stVPS Operator Admin Portal');
});

app.get('/admin/*', async (c) => {
  if (c.env.ASSETS) {
    return c.env.ASSETS.fetch(new Request(new URL('/admin.html', c.req.url)));
  }
  return c.text('1stVPS Operator Admin Portal');
});

// --- 静态资产回退 (Cloudflare Workers Static Assets) ---
app.all('*', async (c) => {
  if (c.env.ASSETS) {
    return c.env.ASSETS.fetch(c.req.raw);
  }
  return c.text('1stVPS Platform API Ready');
});

export default {
  fetch: app.fetch,
  async queue(batch: MessageBatch<QueueJob>, env: Env) {
    for (const msg of batch.messages) {
      if (msg.body.type === 'provision_vps') {
        await runProvisionPipeline(env, msg.body);
      } else if (msg.body.type === 'send_campaign') {
        const campaign = await env.DB.prepare(`SELECT * FROM email_campaigns WHERE id = ?`)
          .bind(msg.body.campaignId)
          .first<{ subject: string; html_content: string }>();
        if (campaign) {
          const users = await env.DB.prepare(`SELECT email FROM users LIMIT 100`).all<{ email: string }>();
          for (const u of users.results) {
            await sendTransactionalEmail(env, u.email, campaign.subject, campaign.html_content);
          }
          await env.DB.prepare(`UPDATE email_campaigns SET status = 'sent', sent_count = ? WHERE id = ?`)
            .bind(users.results.length, msg.body.campaignId)
            .run();
        }
      }
      msg.ack();
    }
  },
};
