import { Env } from '../types';

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

  const res = await fetch('https://api.stripe.com/v1/checkout/sessions', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.STRIPE_SECRET_KEY}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: params.toString(),
  });

  if (!res.ok) {
    throw new Error(`Stripe Checkout error: ${await res.text()}`);
  }
  return res.json() as Promise<{ id: string; url: string }>;
}

export async function verifyStripeSignature(payload: string, sigHeader: string, secret: string): Promise<boolean> {
  const parts = Object.fromEntries(sigHeader.split(',').map((p) => p.split('=')));
  const timestamp = parts['t'];
  const expectedSig = parts['v1'];
  if (!timestamp || !expectedSig) return false;

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

  return hex === expectedSig;
}
