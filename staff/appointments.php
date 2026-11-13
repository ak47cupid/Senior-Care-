<?php
require_once __DIR__ . '/../includes/functions.php';
require_once __DIR__ . '/../sms/sms_gateway.php';
$staff=require_role(['Barangay Staff']);
if ($_SERVER['REQUEST_METHOD']==='POST') {
    verify_csrf();
    try {
        $id=(int)($_POST['appointment_id']??0);$action=(string)($_POST['action']??'');$notes=trim((string)($_POST['staff_notes']??''));
        if (!in_array($action,['confirm','decline','complete'],true) || mb_strlen($notes)>500) throw new RuntimeException('Invalid appointment update.');
        $pdo=db();$pdo->beginTransaction();
        try {
            $q=$pdo->prepare('SELECT a.*,u.full_name,u.phone_number FROM appointments a JOIN users u ON u.user_id=a.user_id WHERE a.appointment_id=? FOR UPDATE');$q->execute([$id]);$a=$q->fetch();
            if (!$a || $a['status']!=='Requested' && !($action==='complete' && $a['status']==='Confirmed')) throw new RuntimeException('This appointment has already been reviewed.');
            if ($action==='confirm') {
                $raw=trim((string)($_POST['scheduled_at']??''));$date=DateTime::createFromFormat('Y-m-d\\TH:i',$raw);
                if (!$date || $date->format('Y-m-d\\TH:i')!==$raw || $date<=new DateTime()) throw new RuntimeException('Choose a valid future appointment time.');
                $slot=$date->format('Y-m-d H:i:s');
                $busy=$pdo->prepare("SELECT COUNT(*) FROM appointments WHERE status='Confirmed' AND scheduled_at=? AND appointment_id<>?");$busy->execute([$slot,$id]);
                if ((int)$busy->fetchColumn()>0) throw new RuntimeException('That exact time is already booked. Choose another appointment time.');
                $pdo->prepare("UPDATE appointments SET status='Confirmed',scheduled_at=?,staff_notes=?,reviewed_by=? WHERE appointment_id=?")->execute([$slot,$notes?:null,$staff['user_id'],$id]);
                $queueNumber=issue_service_queue_ticket($pdo,date('Y-m-d',strtotime($slot)),null,$id);
                $status='Confirmed';$message='Your appointment is confirmed for '.date('M j, Y g:i A',strtotime($slot)).'. Your queue ticket is Q-'.str_pad((string)$queueNumber,4,'0',STR_PAD_LEFT).'.'.($notes!==''?' '.$notes:'');
            } elseif ($action==='decline') {
                if ($notes==='') throw new RuntimeException('Please provide a reason when declining an appointment.');
                $pdo->prepare("UPDATE appointments SET status='Declined',staff_notes=?,reviewed_by=? WHERE appointment_id=?")->execute([$notes,$staff['user_id'],$id]);
                $status='Declined';$message='Your appointment request was declined. '.$notes;
            } else {
                $pdo->prepare("UPDATE appointments SET status='Completed',staff_notes=?,reviewed_by=? WHERE appointment_id=?")->execute([$notes?:$a['staff_notes'],$staff['user_id'],$id]);
                $status='Completed';$message='Your appointment has been marked completed.'.($notes!==''?' '.$notes:'');
            }
            notify_user((int)$a['user_id'],'Appointment '.$status,$message);
            audit_log((int)$staff['user_id'],$action.' appointment','appointments',$id);
            $pdo->commit();
        } catch(Throwable $e) {if($pdo->inTransaction())$pdo->rollBack();throw $e;}
        $sms=send_sms_with_status((int)$a['user_id'],(string)$a['phone_number'],$message);
        flash($sms['ok']?'success':'warning',$sms['ok']?'Appointment updated and SMS sent.':'Appointment updated. SMS could not be sent; the account notification is available.');
    } catch(Throwable $e) {flash('danger',$e instanceof PDOException?'Could not update the appointment.':$e->getMessage());}
    redirect('/staff/appointments.php');
}
$rows=db()->query("SELECT a.*,u.full_name,u.phone_number,q.queue_number,q.status AS queue_status FROM appointments a JOIN users u ON u.user_id=a.user_id LEFT JOIN service_queue q ON q.appointment_id=a.appointment_id ORDER BY FIELD(a.status,'Requested','Confirmed','Declined','Cancelled','Completed'),a.requested_at")->fetchAll();
require_once __DIR__ . '/../includes/header.php';require_once __DIR__ . '/../includes/sidebar.php';
?>
<main class="container-fluid py-3" style="max-width:1200px"><h1 class="page-title">Appointment Requests</h1><p class="text-muted">Review preferred dates, confirm a time, or decline with a reason. Seniors receive an account notification and SMS when their request is updated.</p>
<?php if(!$rows): ?><section class="panel">No appointment requests yet.</section><?php endif; ?>
<?php foreach($rows as $a): ?><article class="panel mb-3"><div class="d-flex flex-wrap justify-content-between gap-2"><h2 class="h5 mb-1"><?= e($a['full_name']) ?> · Appointment #<?= (int)$a['appointment_id'] ?></h2><span class="badge text-bg-<?= $a['status']==='Confirmed'?'success':($a['status']==='Requested'?'warning':($a['status']==='Declined'?'danger':'secondary')) ?>"><?= e($a['status']) ?></span></div><p class="mb-1"><strong>Preferred:</strong> <?= e(date('M j, Y g:i A',strtotime($a['requested_at']))) ?></p><p><strong>Reason:</strong> <?= e($a['purpose']) ?></p><?php if($a['scheduled_at']): ?><p><strong>Confirmed time:</strong> <?= e(date('M j, Y g:i A',strtotime($a['scheduled_at']))) ?><?php if($a['queue_number']): ?> · <strong>Queue Q-<?= e(str_pad((string)$a['queue_number'],4,'0',STR_PAD_LEFT)) ?></strong> (<?= e($a['queue_status']) ?>)<?php endif; ?></p><?php endif; ?><?php if($a['staff_notes']): ?><p><strong>Staff notes:</strong> <?= e($a['staff_notes']) ?></p><?php endif; ?>
<?php if($a['status']==='Requested'): ?><form method="post" class="row g-2"><input type="hidden" name="csrf_token" value="<?= e(csrf_token()) ?>"><input type="hidden" name="appointment_id" value="<?= (int)$a['appointment_id'] ?>"><label class="col-md-4">Confirm date and time<input class="form-control" type="datetime-local" name="scheduled_at" min="<?= date('Y-m-d\\TH:i') ?>" value="<?= e(date('Y-m-d\\TH:i',strtotime($a['requested_at']))) ?>" required></label><label class="col-md-5">Notes / location<input class="form-control" name="staff_notes" maxlength="500" placeholder="e.g. Barangay Hall, bring your ID"></label><div class="col-md-3 d-flex gap-2 align-items-end"><button class="btn btn-success" name="action" value="confirm">Confirm</button><button class="btn btn-outline-danger" name="action" value="decline">Decline</button></div></form><form method="post" class="d-none" id="decline-<?= (int)$a['appointment_id'] ?>"><input type="hidden" name="csrf_token" value="<?= e(csrf_token()) ?>"></form><?php elseif($a['status']==='Confirmed'): ?><form method="post" class="row g-2"><input type="hidden" name="csrf_token" value="<?= e(csrf_token()) ?>"><input type="hidden" name="appointment_id" value="<?= (int)$a['appointment_id'] ?>"><label class="col-md-8">Completion notes<input class="form-control" name="staff_notes" maxlength="500" placeholder="Optional"></label><div class="col-md-4 d-flex align-items-end"><button class="btn btn-primary" name="action" value="complete">Mark completed</button></div></form><?php endif; ?></article><?php endforeach; ?></main>
<script>document.querySelectorAll('button[value="decline"]').forEach(button=>button.addEventListener('click',()=>{const form=button.closest('form');form.querySelector('[name="scheduled_at"]').required=false;const notes=form.querySelector('[name="staff_notes"]');notes.required=true;notes.placeholder='Required: enter reason for declining';}));</script>
<?php require_once __DIR__ . '/../includes/footer.php'; ?>

