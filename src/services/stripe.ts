import { Env } from '../types';
import { getAdminSettings } from './settings';

/**
 * Stripe Checkout & Webhook 验签 (Workers 原生 Web Crypto HMAC-SHA256)
 */
export async function createCheckoutSession(
  env: Env,
  opts: {
    orderId: string;
    userId: string;
    userEmail: string;
    planName: string;
    amountCents: number;
    datacenter: string;
    osTemplate: string;
    hostname: string;
    affiliateCode?: string;
  }
) {
  const params = new URLSearchParams({
    mode: 'payment',
    'customer_email': opts.userEmail,
    'client_reference_id': opts.orderId,
    'success_url': `${env.APP_URL}/?checkout=success&order=${opts.orderId}`,
    'cancel_url': `${env.APP_URL}/?checkout=cancelled`,
    'line_items[0][price_data][currency]': 'usd',
    'line_items[0][price_data][product_data][name]': `1stVPS ${opts.planName} (${opts.datacenter})`,
    'line_items[0][price_data][unit_amount]': String(opts.amountCents),
    'line_items[0][quantity]': '1',
    'metadata[orderId]': opts.orderId,
    'metadata[userId]': opts.userId,
    'metadata[datacenter]': opts.datacenter,
    'metadata[osTemplate]': opts.osTemplate,
    'metadata[hostname]': opts.hostname,
    'metadata[affiliateCode]': opts.affiliateCode || '',
  });

  const settings = await getAdminSettings(env);
  const res = await fetch('https://api.stripe.com/v1/checkout/sessions', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${settings.stripeSecretKey}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: params.toString(),
  });

  if (!res.ok) {
    throw new Error(`Stripe Checkout error: ${await res.text()}`);
  }
  return res.json() as Promise<{ id: string; url: string }>;
}

/** 常量时间字符串比较，防止时序侧信道 */
function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) {
    diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return diff === 0;
}

export async function verifyStripeSignature(payload: string, sigHeader: string, secret: string): Promise<boolean> {
  const parts = Object.fromEntries(sigHeader.split(',').map((p) => p.split('=')));
  const timestamp = parts['t'];
  const expectedSig = parts['v1'];
  if (!timestamp || !expectedSig) return false;

  // 时间戳容差 300 秒，过期签名一律拒绝（防重放）
  const ts = Number(timestamp);
  if (!Number.isFinite(ts)) return false;
  if (Math.abs(Math.floor(Date.now() / 1000) - ts) > 300) return false;

  const key = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const mac = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(`${timestamp}.${payload}`));
  const hex = Array.from(new Uint8Array(mac))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');

  return timingSafeEqual(hex, expectedSig);
}
