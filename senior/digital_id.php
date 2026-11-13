<?php
require_once __DIR__ . '/../includes/functions.php';
$user = require_role(['Senior Citizen']);
$q = db()->prepare('SELECT s.senior_id,s.first_name,s.middle_name,s.last_name,s.member_qr_token,u.status,u.created_at FROM senior_citizens s JOIN users u ON u.user_id=s.user_id WHERE s.user_id=?');
$q->execute([$user['user_id']]);
$member = $q->fetch();
if (!$member) { http_response_code(404); exit('Membership record not found.'); }
$isActive = $member['status'] === 'Active';
$memberNo = 'TSC-' . str_pad((string)$member['senior_id'], 6, '0', STR_PAD_LEFT);
$qrUrl = '';
if ($isActive) {
    if (empty($member['member_qr_token'])) {
        $token = bin2hex(random_bytes(32));
        $saveToken = db()->prepare('UPDATE senior_citizens SET member_qr_token=? WHERE senior_id=? AND member_qr_token IS NULL');
        $saveToken->execute([$token, $member['senior_id']]);
        $member['member_qr_token'] = $token;
    }
    $host = preg_replace('/[^a-zA-Z0-9.:[\]-]/', '', (string)($_SERVER['HTTP_HOST'] ?? 'localhost'));
    $scheme = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? 'https' : 'http';
    $qrUrl = $scheme . '://' . $host . BASE_URL . '/senior/verify_member.php?token=' . rawurlencode((string)$member['member_qr_token']);
}
$pageStyles = ['digital-id.css'];
require_once __DIR__ . '/../includes/header.php';
require_once __DIR__ . '/../includes/sidebar.php';
?>
<main class="digital-id-page">
    <a class="btn btn-outline-primary mb-3 no-print" href="<?= BASE_URL ?>/senior/dashboard.php"><i class="bi bi-arrow-left"></i> Back to dashboard</a>
    <header class="id-page-heading"><div><p class="id-eyebrow">BARANGAY TUNGKIL · SENIOR CITIZEN SERVICES</p><h1>My digital member ID</h1><p>Use this card as proof of your active membership. You can print it or save it as a PDF.</p></div>
    <?php if ($isActive): ?><button class="btn btn-primary no-print" onclick="window.print()"><i class="bi bi-printer"></i> Print / Save PDF</button><?php endif; ?></header>
    <?php if (!$isActive): ?>
        <section class="id-pending" role="status"><i class="bi bi-hourglass-split"></i><div><h2>Registration <?= e($member['status']) ?></h2><p>Your digital member ID will be available after barangay staff approve your registration. You can return here to check again.</p></div></section>
    <?php else: ?>
    <article class="member-card" aria-label="Digital senior citizen membership ID">
        <div class="card-brand"><span class="card-seal"><i class="bi bi-heart-pulse-fill"></i></span><span><strong>BARANGAY TUNGKIL</strong><small>SENIOR CITIZEN SERVICES</small></span></div>
        <div class="card-main"><div class="card-info">
            <h2 class="template-title">Digital Membership Card</h2>
            <div class="card-name"><?= e(trim($member['first_name'].' '.$member['middle_name'].' '.$member['last_name'])) ?></div><div class="template-label">Member Name</div>
            <div class="template-bottom-fields">
                <div><strong><?= e($memberNo) ?></strong><span>Member No.</span></div>
                <div><strong><?= e(date('m/d/Y',strtotime($member['created_at']))) ?></strong><span>Issue Date</span></div>
            </div>
            <div class="card-foot"><span><i class="bi bi-patch-check-fill"></i> ACTIVE MEMBER</span><span>TUNGKIL SENIOR CITIZEN</span></div>
        </div><div class="card-qr-wrap"><div id="member-qr" data-qr-url="<?= e($qrUrl) ?>" aria-label="QR code for membership verification"></div><small>SCAN TO VERIFY</small></div></div>
    </article>
    <p class="id-note"><i class="bi bi-info-circle"></i> This digital card confirms your active account in the barangay assistance system. Present the printed or on-screen card when requested.</p>
    <?php endif; ?>
</main>
<?php if ($isActive): ?><script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js" referrerpolicy="no-referrer"></script><script>
(() => { const target=document.getElementById('member-qr'); if (target && window.QRCode) new QRCode(target,{text:target.dataset.qrUrl,width:140,height:140,colorDark:'#071d2b',colorLight:'#ffffff',correctLevel:QRCode.CorrectLevel.M}); })();
</script><?php endif; ?>
<?php require_once __DIR__ . '/../includes/footer.php'; ?>
