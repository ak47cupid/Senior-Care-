<?php
require_once __DIR__ . '/../includes/functions.php';
$user = require_role(['Senior Citizen']);
$userId = (int)$user['user_id'];
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verify_csrf();
    try {
        $action = (string)($_POST['action'] ?? 'book');
        if ($action === 'book') {
            $rawDate = trim((string)($_POST['requested_at'] ?? ''));
            $purpose = trim((string)($_POST['purpose'] ?? ''));
            $date = DateTime::createFromFormat('Y-m-d\\TH:i', $rawDate);
            if (!$date || $date->format('Y-m-d\\TH:i') !== $rawDate || $date <= new DateTime()) throw new RuntimeException('Choose a valid future date and time.');
            if ($purpose === '' || mb_strlen($purpose) > 500) throw new RuntimeException('Enter the reason for your appointment (up to 500 characters).');
            $stmt = db()->prepare("INSERT INTO appointments (user_id,requested_at,purpose) VALUES (?,?,?)");
            $stmt->execute([$userId,$date->format('Y-m-d H:i:s'),$purpose]);
            $appointmentId = (int)db()->lastInsertId();
            notify_user($userId,'Appointment Request Submitted','Your appointment request #'.$appointmentId.' has been submitted for '.date('M j, Y g:i A',strtotime($date->format('Y-m-d H:i:s'))).'.');
            notify_barangay_staff('New Appointment Request',$user['full_name'].' requested an appointment for '.date('M j, Y g:i A',strtotime($date->format('Y-m-d H:i:s'))).'.',$userId);
            audit_log($userId,'Requested appointment','appointments',$appointmentId);
            flash('success','Appointment request submitted. Staff will confirm the date and time.');
        } elseif ($action === 'cancel') {
            $id = (int)($_POST['appointment_id'] ?? 0);
            $stmt = db()->prepare("UPDATE appointments SET status='Cancelled' WHERE appointment_id=? AND user_id=? AND status='Requested'");
            $stmt->execute([$id,$userId]);
            if (!$stmt->rowCount()) throw new RuntimeException('Only a pending appointment request can be cancelled.');
            audit_log($userId,'Cancelled appointment request','appointments',$id);
            flash('success','Appointment request cancelled.');
        } else throw new RuntimeException('Invalid appointment action.');
    } catch (Throwable $e) { flash('danger',$e instanceof PDOException?'Unable to save the appointment. Please try again.':$e->getMessage()); }
    redirect('/senior/appointments.php');
}
$stmt=db()->prepare('SELECT a.*,q.queue_number,q.status AS queue_status FROM appointments a LEFT JOIN service_queue q ON q.appointment_id=a.appointment_id WHERE a.user_id=? ORDER BY a.created_at DESC');
$stmt->execute([$userId]);$appointments=$stmt->fetchAll();
require_once __DIR__ . '/../includes/header.php';require_once __DIR__ . '/../includes/sidebar.php';
?>
<main class="container-fluid py-3" style="max-width:1120px">
<div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3"><div><h1 class="page-title mb-1">My Appointments</h1><p class="text-muted mb-0">Request a visit with the barangay. Staff will confirm the appointment time.</p></div><button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#book-appointment"><i class="bi bi-calendar-plus"></i> Request Appointment</button></div>
<section class="panel mb-4"><h2 class="h5">Appointment requests</h2><?php if(!$appointments): ?><p class="text-muted mb-0">You have not requested an appointment yet.</p><?php else: ?><div class="table-responsive"><table class="table align-middle mb-0"><thead><tr><th>Requested date</th><th>Purpose</th><th>Status</th><th>Confirmed time / queue</th><th>Staff notes</th><th></th></tr></thead><tbody><?php foreach($appointments as $a): ?><tr><td><?= e(date('M j, Y g:i A',strtotime($a['requested_at']))) ?></td><td><?= e($a['purpose']) ?></td><td><span class="badge text-bg-<?= $a['status']==='Confirmed'?'success':($a['status']==='Requested'?'warning':($a['status']==='Declined'?'danger':'secondary')) ?>"><?= e($a['status']) ?></span></td><td><?php if($a['scheduled_at']): ?><strong><?= e(date('M j, Y g:i A',strtotime($a['scheduled_at']))) ?></strong><?php if($a['queue_number']): ?><br><span class="badge text-bg-primary">Queue Q-<?= e(str_pad((string)$a['queue_number'],4,'0',STR_PAD_LEFT)) ?></span> <small><?= e($a['queue_status']) ?></small><?php endif; ?><?php endif; ?></td><td><?= e($a['staff_notes'] ?? '') ?></td><td><?php if($a['status']==='Requested'): ?><form method="post"><input type="hidden" name="csrf_token" value="<?= e(csrf_token()) ?>"><input type="hidden" name="action" value="cancel"><input type="hidden" name="appointment_id" value="<?= (int)$a['appointment_id'] ?>"><button class="btn btn-sm btn-outline-danger">Cancel</button></form><?php endif; ?></td></tr><?php endforeach; ?></tbody></table></div><?php endif; ?></section>
</main>
<div class="modal fade" id="book-appointment" tabindex="-1" aria-labelledby="book-appointment-title" aria-hidden="true"><div class="modal-dialog modal-dialog-centered"><form method="post" class="modal-content"><div class="modal-header"><h2 class="modal-title h5" id="book-appointment-title">Request an appointment</h2><button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button></div><div class="modal-body"><input type="hidden" name="csrf_token" value="<?= e(csrf_token()) ?>"><input type="hidden" name="action" value="book"><p class="text-muted">Choose your preferred date and time. This is a request and is not confirmed until staff approve it.</p><label class="form-label" for="requested-at">Preferred date and time</label><input class="form-control mb-3" type="datetime-local" id="requested-at" name="requested_at" min="<?= date('Y-m-d\\TH:i') ?>" required><label class="form-label" for="purpose">Reason for visit</label><textarea class="form-control" id="purpose" name="purpose" maxlength="500" rows="4" required placeholder="Briefly explain what you need help with"></textarea></div><div class="modal-footer"><button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button><button class="btn btn-primary">Submit request</button></div></form></div></div>
<?php require_once __DIR__ . '/../includes/footer.php'; ?>
