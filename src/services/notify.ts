import { Env } from '../types';

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
  if (!env.RESEND_API_KEY) return { skipped: true };
  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ from: env.EMAIL_FROM, to, subject, html }),
  });
  return res.json();
}

export async function dispatchWebPush(env: Env, userId: string, payload: { title: string; body: string; url?: string }) {
  const subs = await env.DB.prepare(`SELECT endpoint FROM push_subscriptions WHERE user_id = ?`)
    .bind(userId)
    .all<{ endpoint: string }>();

  // In production, sign VAPID JWT with env.VAPID_PRIVATE_KEY via crypto.subtle
  // and POST encrypted payload to each Web Push endpoint.
  return { delivered: subs.results.length, payload };
}
