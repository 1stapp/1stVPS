import { Env, QueueJob } from '../types';
import { ProxmoxClient } from './proxmox';
import { encryptSecret } from './crypto';
import { getAdminSettings } from './settings';
import { dispatchWebPush, sendInternalMessage, sendTransactionalEmail, sendAdminNotification } from './notify';

export async function runProvisionPipeline(env: Env, job: Extract<QueueJob, { type: 'provision_vps' }>) {
  // 0. 幂等保护：队列消息可能被重投递，订单已开通时直接返回，避免重复开通
  const order = await env.DB.prepare(`SELECT status FROM orders WHERE id = ?`)
    .bind(job.orderId)
    .first<{ status: string }>();
  if (order?.status === 'provisioned') {
    return;
  }

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

  const instanceId = crypto.randomUUID();

  // 3. 原子抢占 IP：仅当 IP 仍为 free 时才更新成功，防止并发任务重复分配同一 IP
  const claim = await env.DB.prepare(
    `UPDATE ip_pool SET status = 'assigned', assigned_vm_id = ? WHERE ip = ? AND status = 'free'`
  )
    .bind(instanceId, ipRow.ip)
    .run();
  if (claim.meta.changes !== 1) {
    throw new Error(`Failed to claim IP ${ipRow.ip}: already taken`);
  }

  try {
    // 4. vmid 按节点内现有最大值 +1 分配，避免随机冲突
    const vmidRow = await env.DB.prepare(
      `SELECT COALESCE(MAX(vmid), 100) + 1 AS next_vmid FROM vps_instances WHERE node_id = ?`
    )
      .bind(node.id)
      .first<{ next_vmid: number }>();
    const vmid = vmidRow?.next_vmid ?? 101;

    const rootPassword = crypto.randomUUID().replace(/-/g, '').slice(0, 16);
    // 初始 root 密码加密后入库（密钥由 JWT_SECRET 派生，缺失时直接抛错）
    const rootPasswordEnc = await encryptSecret(rootPassword, env.JWT_SECRET);
    const expiresAt = new Date(Date.now() + 30 * 86400 * 1000).toISOString();

    // 5. Provision KVM VM via Proxmox VE REST API (Token 取自站长后台设置，KV 优先、Secret 回退)
    const settings = await getAdminSettings(env);
    const pve = new ProxmoxClient(node.pve_host, settings.proxmoxApiToken);
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

    // 6. Commit state in D1 (IP 已在步骤 3 抢占，无需重复更新)
    await env.DB.batch([
      env.DB.prepare(
        `UPDATE nodes SET used_vcpu = used_vcpu + ?, used_ram_gb = used_ram_gb + ?, used_nvme_gb = used_nvme_gb + ? WHERE id = ?`
      ).bind(plan.vcpu, plan.ram_gb, plan.nvme_gb, node.id),
      env.DB.prepare(
        `INSERT INTO vps_instances (id, user_id, node_id, plan_id, vmid, hostname, os_template, ipv4, status, root_password_enc, expires_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'running', ?, ?)`
      ).bind(instanceId, job.userId, node.id, plan.id, vmid, job.hostname, job.osTemplate, ipRow.ip, rootPasswordEnc, expiresAt),
      env.DB.prepare(`UPDATE orders SET status = 'provisioned' WHERE id = ?`).bind(job.orderId),
    ]);
  } catch (err) {
    // 任一步骤失败：释放已抢占的 IP 回地址池，随后向上抛出触发队列重试
    await env.DB.prepare(
      `UPDATE ip_pool SET status = 'free', assigned_vm_id = NULL WHERE ip = ? AND assigned_vm_id = ?`
    )
      .bind(ipRow.ip, instanceId)
      .run();
    throw err;
  }

  // 7. Notify user via Internal Message + Web Push + Email
  const user = await env.DB.prepare(`SELECT email, name FROM users WHERE id = ?`)
    .bind(job.userId)
    .first<{ email: string; name: string }>();

  await sendInternalMessage(
    env,
    job.userId,
    'system',
    `VPS ${job.hostname} 已自动开通`,
    `IP: ${ipRow.ip} | 节点: ${job.datacenter} | 系统: ${job.osTemplate}。可通过控制台凭据接口 (GET /api/vps/${instanceId}/credentials) 查看 SSH 登录凭据。`
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

  // 8. 即时向站长发送 Webhook / Telegram 交付通知
  await sendAdminNotification(env, {
    eventType: 'order',
    title: '新实例全自动开通成功',
    content: `订单: ${job.orderId}\n客户: ${user?.email || job.userId}\n主机: ${job.hostname}\nIPv4: ${ipRow.ip}\n机房节点: ${job.datacenter}`,
  });
}
