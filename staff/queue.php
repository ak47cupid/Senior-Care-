<?php
require_once __DIR__ . '/../includes/functions.php';
require_once __DIR__ . '/../sms/sms_gateway.php';
$staff=require_role(['Barangay Staff']);
$date=(string)($_GET['date']??date('Y-m-d'));
$parsed=DateTime::createFromFormat('!Y-m-d',$date);
if(!$parsed||$parsed->format('Y-m-d')!==$date){http_response_code(422);exit('Choose a valid queue date.');}
if($_SERVER['REQUEST_METHOD']==='POST'){
    verify_csrf();$action=(string)($_POST['action']??'');$postDate=(string)($_POST['date']??date('Y-m-d'));
    try{
        $pdo=db();$pdo->beginTransaction();$ticket=null;
        if($action==='call_next'){
            $q=$pdo->prepare("SELECT q.*,u.user_id,u.full_name,u.phone_number FROM service_queue q LEFT JOIN assistance_requests ar ON ar.request_id=q.request_id LEFT JOIN senior_citizens s ON s.senior_id=ar.senior_id LEFT JOIN appointments a ON a.appointment_id=q.appointment_id JOIN users u ON u.user_id=COALESCE(s.user_id,a.user_id) WHERE q.queue_date=? AND q.status='Waiting' ORDER BY q.queue_number LIMIT 1 FOR UPDATE");
            $q->execute([$postDate]);$ticket=$q->fetch();
            if(!$ticket)throw new RuntimeException('There are no waiting tickets for this date.');
            $pdo->prepare("UPDATE service_queue SET status='Called',called_at=NOW() WHERE queue_id=?")->execute([$ticket['queue_id']]);
            $msg='Your queue ticket Q-'.str_pad((string)$ticket['queue_number'],4,'0',STR_PAD_LEFT).' is being called. Please proceed to the service counter.';
            notify_user((int)$ticket['user_id'],'Queue Ticket Called',$msg);
            audit_log((int)$staff['user_id'],'Called queue ticket','service_queue',(int)$ticket['queue_id']);
        }elseif(in_array($action,['start','complete','no_show'],true)){
            $queueId=(int)($_POST['queue_id']??0);$q=$pdo->prepare('SELECT q.*,u.user_id,u.phone_number FROM service_queue q LEFT JOIN assistance_requests ar ON ar.request_id=q.request_id LEFT JOIN senior_citizens s ON s.senior_id=ar.senior_id LEFT JOIN appointments a ON a.appointment_id=q.appointment_id JOIN users u ON u.user_id=COALESCE(s.user_id,a.user_id) WHERE q.queue_id=? AND q.queue_date=? FOR UPDATE');$q->execute([$queueId,$postDate]);$ticket=$q->fetch();
            if(!$ticket)throw new RuntimeException('Queue ticket not found.');
            $next=match($action){'start'=>'Serving','complete'=>'Completed',default=>'No Show'};
            $allowed=match($action){'start'=>$ticket['status']==='Called','complete'=>in_array($ticket['status'],['Called','Serving'],true),default=>in_array($ticket['status'],['Waiting','Called'],true)};
            if(!$allowed)throw new RuntimeException('This queue ticket cannot be updated from its current status.');
            $pdo->prepare('UPDATE service_queue SET status=?,completed_at=? WHERE queue_id=?')->execute([$next,in_array($next,['Completed','No Show'],true)?date('Y-m-d H:i:s'):null,$queueId]);
            audit_log((int)$staff['user_id'],ucfirst(str_replace('_',' ',$action)).' queue ticket','service_queue',$queueId);
            if($next==='Completed')notify_user((int)$ticket['user_id'],'Queue Service Completed','Your queue visit has been marked completed. Thank you.');
        }else throw new RuntimeException('Invalid queue action.');
        $pdo->commit();
        if($action==='call_next'){$sms=send_sms_with_status((int)$ticket['user_id'],(string)$ticket['phone_number'],$msg);flash($sms['ok']?'success':'warning',$sms['ok']?'Next ticket called and SMS sent.':'Next ticket called. SMS could not be sent; account notification is available.');}
        else flash('success','Queue ticket updated.');
    }catch(Throwable $e){if(isset($pdo)&&$pdo->inTransaction())$pdo->rollBack();flash('danger',$e instanceof PDOException?'Unable to update the queue. Please try again.':$e->getMessage());}
    redirect('/staff/queue.php?date='.rawurlencode($postDate));
}
$q=db()->prepare("SELECT q.*,u.full_name,COALESCE(a.purpose,ar.request_type) AS service,CASE WHEN q.appointment_id IS NOT NULL THEN 'Appointment' ELSE 'Assistance request' END AS queue_type FROM service_queue q LEFT JOIN assistance_requests ar ON ar.request_id=q.request_id LEFT JOIN senior_citizens s ON s.senior_id=ar.senior_id LEFT JOIN appointments a ON a.appointment_id=q.appointment_id JOIN users u ON u.user_id=COALESCE(s.user_id,a.user_id) WHERE q.queue_date=? ORDER BY q.queue_number");$q->execute([$date]);$tickets=$q->fetchAll();
$current=0;foreach($tickets as $t)if(in_array($t['status'],['Called','Serving'],true))$current++;
require_once __DIR__ . '/../includes/header.php';require_once __DIR__ . '/../includes/sidebar.php';
?>
<main class="container-fluid py-3" style="max-width:1200px"><header class="d-flex flex-wrap justify-content-between align-items-end gap-3 mb-3"><div><h1 class="page-title mb-1">Digital Queue</h1><p class="text-muted mb-0">Call queue tickets for assistance requests and confirmed appointments.</p></div><form class="d-flex gap-2 align-items-end"><label>Queue date<input class="form-control" type="date" name="date" value="<?= e($date) ?>"></label><button class="btn btn-outline-primary">View</button></form></header>
<section class="panel mb-3 d-flex flex-wrap justify-content-between align-items-center gap-3"><div><strong><?= count($tickets) ?></strong> tickets · <strong><?= $current ?></strong> called / serving</div><form method="post"><input type="hidden" name="csrf_token" value="<?= e(csrf_token()) ?>"><input type="hidden" name="date" value="<?= e($date) ?>"><button class="btn btn-primary btn-lg" name="action" value="call_next"><i class="bi bi-megaphone"></i> Call Next Ticket</button></form></section>
<section class="panel table-responsive"><table class="table align-middle"><thead><tr><th>Queue</th><th>Member</th><th>Service</th><th>Type</th><th>Status</th><th>Action</th></tr></thead><tbody><?php if(!$tickets): ?><tr><td colspan="6" class="text-muted">No queue tickets for this date.</td></tr><?php endif; ?><?php foreach($tickets as $t): ?><tr><td><strong class="fs-5">Q-<?= e(str_pad((string)$t['queue_number'],4,'0',STR_PAD_LEFT)) ?></strong></td><td><?= e($t['full_name']) ?></td><td><?= e($t['service']) ?></td><td><?= e($t['queue_type']) ?></td><td><span class="badge text-bg-<?= $t['status']==='Completed'?'success':($t['status']==='Called'?'primary':($t['status']==='Serving'?'info':($t['status']==='Waiting'?'warning':'secondary'))) ?>"><?= e($t['status']) ?></span></td><td><form method="post" class="d-flex flex-wrap gap-1"><input type="hidden" name="csrf_token" value="<?= e(csrf_token()) ?>"><input type="hidden" name="date" value="<?= e($date) ?>"><input type="hidden" name="queue_id" value="<?= (int)$t['queue_id'] ?>"><?php if($t['status']==='Called'): ?><button class="btn btn-sm btn-outline-primary" name="action" value="start">Start service</button><?php endif; ?><?php if(in_array($t['status'],['Called','Serving'],true)): ?><button class="btn btn-sm btn-success" name="action" value="complete">Complete</button><?php endif; ?><?php if(in_array($t['status'],['Waiting','Called'],true)): ?><button class="btn btn-sm btn-outline-danger" name="action" value="no_show">No show</button><?php endif; ?></form></td></tr><?php endforeach; ?></tbody></table></section></main>
<?php require_once __DIR__ . '/../includes/footer.php'; ?>
