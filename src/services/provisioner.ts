import { Env, QueueJob } from '../types';
import { ProxmoxClient } from './proxmox';
import { dispatchWebPush, sendInternalMessage, sendTransactionalEmail, sendAdminNotification } from './notify';

export async function runProvisionPipeline(env: Env, job: Extract<QueueJob, { type: 'provision_vps' }>) {
  const plan = await env.DB.prepare(`SELECT * FROM vps_plans WHERE id = ?`)
    .bind(job.planId)
    .first<{ id: string; name: string; vcpu: number; ram_gb: number; nvme_gb: number; price_cents: number }>();
  if (!plan) throw new Error(`Plan ${job.planId} not found`);

  // 1. Pick bare-metal node in requested datacenter with available capacity
  const node = await env.DB.prepare(
    `SELECT * FROM nodes
     WHERE datacenter = ? AND status = 'online'
       AND (total_vcpu - used_vcpu) >= ?
       AND (total_ram_gb - used_ram_gb) >= ?
       AND (total_nvme_gb - used_nvme_gb) >= ?
     ORDER BY (total_ram_gb - used_ram_gb) DESC LIMIT 1`
  )
    .bind(job.datacenter, plan.vcpu, plan.ram_gb, plan.nvme_gb)
    .first<{ id: string; pve_host: string; pve_node: string }>();
  if (!node) throw new Error(`No capacity available in ${job.datacenter}`);

  // 2. Allocate free IPv4 from node's OVH IP pool
  const ipRow = await env.DB.prepare(
    `SELECT * FROM ip_pool WHERE node_id = ? AND status = 'free' LIMIT 1`
  )
    .bind(node.id)
    .first<{ ip: string; cidr: string; gateway: string }>();
  if (!ipRow) throw new Error(`No free IPv4 on node ${node.id}`);

  const vmid = Math.floor(100 + Math.random() * 8900);
  const rootPassword = crypto.randomUUID().replace(/-/g, '').slice(0, 16);
  const instanceId = crypto.randomUUID();
  const expiresAt = new Date(Date.now() + 30 * 86400 * 1000).toISOString();

  // 3. Provision KVM VM via Proxmox VE REST API
  const pve = new ProxmoxClient(node.pve_host, env.PROXMOX_API_TOKEN);
  await pve.provisionKvmVps(node.pve_node, {
    vmid,
    name: job.hostname,
    cores: plan.vcpu,
    memoryMb: plan.ram_gb * 1024,
    diskGb: plan.nvme_gb,
    templateVmid: 9000, // Pre-built Cloud-Init template
    ipCidr: ipRow.cidr,
    gateway: ipRow.gateway,
    rootPassword,
  });

  // 4. Commit state in D1
  await env.DB.batch([
    env.DB.prepare(`UPDATE ip_pool SET status = 'assigned', assigned_vm_id = ? WHERE ip = ?`).bind(instanceId, ipRow.ip),
    env.DB.prepare(
      `UPDATE nodes SET used_vcpu = used_vcpu + ?, used_ram_gb = used_ram_gb + ?, used_nvme_gb = used_nvme_gb + ? WHERE id = ?`
    ).bind(plan.vcpu, plan.ram_gb, plan.nvme_gb, node.id),
    env.DB.prepare(
      `INSERT INTO vps_instances (id, user_id, node_id, plan_id, vmid, hostname, os_template, ipv4, status, expires_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'running', ?)`
    ).bind(instanceId, job.userId, node.id, plan.id, vmid, job.hostname, job.osTemplate, ipRow.ip, expiresAt),
    env.DB.prepare(`UPDATE orders SET status = 'provisioned' WHERE id = ?`).bind(job.orderId),
  ]);

  // 5. Notify user via Internal Message + Web Push + Email
  const user = await env.DB.prepare(`SELECT email, name FROM users WHERE id = ?`)
    .bind(job.userId)
    .first<{ email: string; name: string }>();

  await sendInternalMessage(
    env,
    job.userId,
    'system',
    `VPS ${job.hostname} 已自动开通`,
    `IP: ${ipRow.ip} | 节点: ${job.datacenter} | 系统: ${job.osTemplate}。请在控制台查看 SSH 凭据。`
  );
  await dispatchWebPush(env, job.userId, {
    title: '1stVPS 实例开通成功',
    body: `${job.hostname} (${ipRow.ip}) 已就绪并启动运行`,
  });
  if (user?.email) {
    await sendTransactionalEmail(
      env,
      user.email,
      `[1stVPS] 您的云主机 ${job.hostname} 已开通`,
      `<h2>欢迎使用 1stVPS</h2><p>主机名：<b>${job.hostname}</b></p><p>公网 IPv4：<b>${ipRow.ip}</b></p><p>系统模板：${job.osTemplate}</p>`
    );
  }

  // 6. 即时向站长发送 Webhook / Telegram 交付通知
  await sendAdminNotification(env, {
    eventType: 'order',
    title: '新实例全自动开通成功',
    content: `订单: ${job.orderId}\n客户: ${user?.email || job.userId}\n主机: ${job.hostname}\nIPv4: ${ipRow.ip}\n机房节点: ${job.datacenter}`,
  });
}
