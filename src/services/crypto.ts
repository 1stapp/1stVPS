/**
 * 对称加密小工具 (AES-GCM)
 * 密钥由 JWT_SECRET 经 SHA-256 摘要派生，存储格式为 base64(iv ‖ ciphertext)
 */

async function deriveKey(secret: string): Promise<CryptoKey> {
  if (!secret) {
    throw new Error('JWT_SECRET is not configured');
  }
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(secret));
  return crypto.subtle.importKey('raw', digest, { name: 'AES-GCM' }, false, ['encrypt', 'decrypt']);
}

function toBase64(bytes: Uint8Array): string {
  let bin = '';
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin);
}

function fromBase64(b64: string): Uint8Array {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

/** 加密明文，返回 base64(iv ‖ ciphertext) */
export async function encryptSecret(plaintext: string, secret: string): Promise<string> {
  const key = await deriveKey(secret);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const cipher = new Uint8Array(
    await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, new TextEncoder().encode(plaintext))
  );
  const combined = new Uint8Array(iv.length + cipher.length);
  combined.set(iv, 0);
  combined.set(cipher, iv.length);
  return toBase64(combined);
}

/** 解密 encryptSecret 产出的 base64(iv ‖ ciphertext) */
export async function decryptSecret(encoded: string, secret: string): Promise<string> {
  const key = await deriveKey(secret);
  const combined = fromBase64(encoded);
  const iv = combined.slice(0, 12);
  const cipher = combined.slice(12);
  const plain = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key, cipher);
  return new TextDecoder().decode(plain);
}
