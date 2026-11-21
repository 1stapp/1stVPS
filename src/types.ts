export interface Env {
  DB: D1Database;
  SESSION_KV: KVNamespace;
  PROVISION_QUEUE: Queue<QueueJob>;
  SUPPORT_CHAT: DurableObjectNamespace;
  ASSETS: Fetcher;

  APP_URL: string;
  AFFILIATE_RATE: string;
  EMAIL_FROM: string;

  JWT_SECRET: string;
  GOOGLE_CLIENT_ID: string;
  GOOGLE_CLIENT_SECRET: string;
  STRIPE_SECRET_KEY: string;
  STRIPE_WEBHOOK_SECRET: string;
  OVH_APP_KEY: string;
  OVH_APP_SECRET: string;
  OVH_CONSUMER_KEY: string;
  PROXMOX_API_TOKEN: string;
  VAPID_PUBLIC_KEY?: string;
  VAPID_PRIVATE_KEY?: string;
  RESEND_API_KEY?: string;

  // 站长系统消息 Webhook 与 Telegram 推送凭证
  ADMIN_WEBHOOK_URL?: string;
  ADMIN_TELEGRAM_BOT_TOKEN?: string;
  ADMIN_TELEGRAM_CHAT_ID?: string;
}

export type QueueJob =
  | { type: 'provision_vps'; orderId: string; userId: string; planId: string; datacenter: string; osTemplate: string; hostname: string }
  | { type: 'send_campaign'; campaignId: string };

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: 'customer' | 'admin';
  affiliate_code: string;
}
