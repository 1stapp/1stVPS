import { Env } from '../types';

/**
 * 站长后台系统配置 (Cloudflare KV: admin:settings)
 * 后台可配置的凭据与业务参数统一在此读取：KV 值优先，KV 为空时回退到环境变量 / Wrangler Secret。
 * 引导级密钥 (JWT_SECRET / ADMIN_PASSWORD) 不属于后台配置，仍只存于 Wrangler Secret。
 */
export interface AdminSettings {
  // 非密钥项 (GET /api/admin/settings 可完整返回)
  telegramChatId: string;
  webhookUrl: string;
  emailFrom: string;
  affiliateRate: string;
  events: { order: boolean; support: boolean; affiliate: boolean; system: boolean };
  // 密钥项 (GET 接口只返回掩码与是否已配置，绝不回显明文)
  telegramBotToken: string;
  stripeSecretKey: string;
  stripeWebhookSecret: string;
  googleClientId: string;
  googleClientSecret: string;
  resendApiKey: string;
  ovhAppKey: string;
  ovhAppSecret: string;
  ovhConsumerKey: string;
  proxmoxApiToken: string;
  vapidPublicKey: string;
  vapidPrivateKey: string;
}

/** 密钥字段在 GET 接口中的掩码占位；POST 回传掩码或空字符串表示保持原值 */
export const SECRET_MASK = '••••••';

export const SECRET_SETTING_FIELDS = [
  'telegramBotToken',
  'stripeSecretKey',
  'stripeWebhookSecret',
  'googleClientId',
  'googleClientSecret',
  'resendApiKey',
  'ovhAppKey',
  'ovhAppSecret',
  'ovhConsumerKey',
  'proxmoxApiToken',
  'vapidPublicKey',
  'vapidPrivateKey',
] as const satisfies readonly (keyof AdminSettings)[];

export const PLAIN_SETTING_FIELDS = ['telegramChatId', 'webhookUrl', 'emailFrom', 'affiliateRate'] as const satisfies readonly (keyof AdminSettings)[];

const DEFAULT_EVENTS = { order: true, support: true, affiliate: true, system: true };

type RawAdminSettings = Partial<Omit<AdminSettings, 'events'>> & { events?: Partial<AdminSettings['events']> };

// 请求内缓存：同一请求多次读取配置时只查一次 KV；保存配置后需调用 invalidateAdminSettingsCache 失效
const cache = new WeakMap<Env, Promise<AdminSettings>>();

export function getAdminSettings(env: Env): Promise<AdminSettings> {
  let pending = cache.get(env);
  if (!pending) {
    pending = loadAdminSettings(env);
    cache.set(env, pending);
  }
  return pending;
}

export function invalidateAdminSettingsCache(env: Env) {
  cache.delete(env);
}

async function loadAdminSettings(env: Env): Promise<AdminSettings> {
  let kv: RawAdminSettings = {};
  if (env.SESSION_KV) {
    try {
      const raw = await env.SESSION_KV.get('admin:settings');
      if (raw) kv = JSON.parse(raw) as RawAdminSettings;
    } catch (e) {
      console.warn('Failed to load admin settings from KV:', e);
    }
  }

  // KV 值非空时优先，否则回退 env
  const pick = (kvValue: string | undefined, envValue: string | undefined): string =>
    kvValue && kvValue.trim() !== '' ? kvValue : envValue || '';

  return {
    telegramChatId: pick(kv.telegramChatId, env.ADMIN_TELEGRAM_CHAT_ID),
    webhookUrl: pick(kv.webhookUrl, env.ADMIN_WEBHOOK_URL),
    emailFrom: pick(kv.emailFrom, env.EMAIL_FROM),
    affiliateRate: pick(kv.affiliateRate, env.AFFILIATE_RATE),
    events: { ...DEFAULT_EVENTS, ...(kv.events || {}) },
    telegramBotToken: pick(kv.telegramBotToken, env.ADMIN_TELEGRAM_BOT_TOKEN),
    stripeSecretKey: pick(kv.stripeSecretKey, env.STRIPE_SECRET_KEY),
    stripeWebhookSecret: pick(kv.stripeWebhookSecret, env.STRIPE_WEBHOOK_SECRET),
    googleClientId: pick(kv.googleClientId, env.GOOGLE_CLIENT_ID),
    googleClientSecret: pick(kv.googleClientSecret, env.GOOGLE_CLIENT_SECRET),
    resendApiKey: pick(kv.resendApiKey, env.RESEND_API_KEY),
    ovhAppKey: pick(kv.ovhAppKey, env.OVH_APP_KEY),
    ovhAppSecret: pick(kv.ovhAppSecret, env.OVH_APP_SECRET),
    ovhConsumerKey: pick(kv.ovhConsumerKey, env.OVH_CONSUMER_KEY),
    proxmoxApiToken: pick(kv.proxmoxApiToken, env.PROXMOX_API_TOKEN),
    vapidPublicKey: pick(kv.vapidPublicKey, env.VAPID_PUBLIC_KEY),
    vapidPrivateKey: pick(kv.vapidPrivateKey, env.VAPID_PRIVATE_KEY),
  };
}
