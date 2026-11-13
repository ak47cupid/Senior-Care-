-- Adds daily queue counters and digital queue tickets for assistance requests and appointments.
CREATE TABLE IF NOT EXISTS queue_daily_counters (
  queue_date DATE PRIMARY KEY,
  last_number INT UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS service_queue (
  queue_id INT AUTO_INCREMENT PRIMARY KEY,
  queue_date DATE NOT NULL,
  queue_number INT UNSIGNED NOT NULL,
  request_id INT NULL UNIQUE,
  appointment_id INT NULL UNIQUE,
  status ENUM('Waiting','Called','Serving','Completed','No Show') NOT NULL DEFAULT 'Waiting',
  called_at DATETIME NULL,
  completed_at DATETIME NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_service_queue_date_number (queue_date,queue_number),
  INDEX idx_service_queue_day_status (queue_date,status,queue_number),
  CONSTRAINT fk_queue_request FOREIGN KEY (request_id) REFERENCES assistance_requests(request_id) ON DELETE CASCADE,
  CONSTRAINT fk_queue_appointment FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE
) ENGINE=InnoDB;
