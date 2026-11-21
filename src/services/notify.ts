import { Env } from '../types';
import { getAdminSettings } from './settings';

export async function sendInternalMessage(
  env: Env,
  userId: string,
  category: 'system' | 'billing' | 'affiliate',
  title: string,
  body: string
) {
  await env.DB.prepare(
    `INSERT INTO messages (id, user_id, category, title, body) VALUES (?, ?, ?, ?, ?)`
  )
    .bind(crypto.randomUUID(), userId, category, title, body)
    .run();
}

export async function sendTransactionalEmail(env: Env, to: string, subject: string, html: string) {
  const settings = await getAdminSettings(env);
  if (!settings.resendApiKey) return { skipped: true };
  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${settings.resendApiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ from: settings.emailFrom, to, subject, html }),
  });
  return res.json();
}

export async function dispatchWebPush(env: Env, userId: string, payload: { title: string; body: string; url?: string }) {
  const subs = await env.DB.prepare(`SELECT endpoint FROM push_subscriptions WHERE user_id = ?`)
    .bind(userId)
    .all<{ endpoint: string }>();

  return { delivered: subs.results.length, payload };
}

/**
 * 站长系统消息 Webhook 与 Telegram 实时推送
 * 用于新订单、支付到账、客户在线工单咨询、提现申请等关键业务事件即时通知站长
 */
export async function sendAdminNotification(
  env: Env,
  opts: {
    eventType: 'order' | 'support' | 'affiliate' | 'system';
    title: string;
    content: string;
  }
) {
  // 推送配置统一从站长后台设置读取 (KV 优先，env 回退)
  const settings = await getAdminSettings(env);
  const botToken = settings.telegramBotToken;
  const chatId = settings.telegramChatId;
  const webhookUrl = settings.webhookUrl;
  const eventToggles = settings.events;

  // Check if this event type is enabled
  if (eventToggles[opts.eventType] === false) {
    return { skipped: true, reason: `Event ${opts.eventType} disabled in admin settings` };
  }

  const results: {
    telegram?: { ok: boolean; status?: number; error?: string };
    webhook?: { ok: boolean; status?: number; error?: string };
  } = {};

  // 1. Telegram Bot 推送
  if (botToken && chatId) {
    const text = `🔔 *[1stVPS 站长通知] ${opts.title}*\n\n${opts.content}\n\n⏰ 时间: ${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}`;
    try {
      const res = await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          text,
          parse_mode: 'Markdown',
        }),
      });
      results.telegram = { ok: res.ok, status: res.status };
      if (!res.ok) {
        const errText = await res.text();
        results.telegram.error = errText;
      }
    } catch (e: any) {
      results.telegram = { ok: false, error: e?.message || String(e) };
    }
  }

  // 2. 自定义 Webhook 推送 (兼容 飞书 / 钉钉 / 企微 / Discord / 通用 HTTP POST)
  if (webhookUrl) {
    const formattedText = `[1stVPS 站长通知] ${opts.title}\n${opts.content}\n时间: ${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}`;
    try {
      const res = await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          // 通用格式
          event: opts.eventType,
          title: opts.title,
          content: opts.content,
          timestamp: new Date().toISOString(),
          // Discord 兼容
          content_discord: formattedText,
          // 飞书自定义机器人兼容
          msg_type: 'text',
          content_feishu: { text: formattedText },
          // 钉钉自定义机器人兼容
          text: { content: formattedText },
        }),
      });
      results.webhook = { ok: res.ok, status: res.status };
      if (!res.ok) {
        const errText = await res.text();
        results.webhook.error = errText;
      }
    } catch (e: any) {
      results.webhook = { ok: false, error: e?.message || String(e) };
    }
  }

  return results;
}
