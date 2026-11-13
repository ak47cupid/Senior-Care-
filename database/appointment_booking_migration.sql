-- Enables senior citizen appointment requests and staff confirmation.
CREATE TABLE IF NOT EXISTS appointments (
  appointment_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  requested_at DATETIME NOT NULL,
  purpose VARCHAR(500) NOT NULL,
  status ENUM('Requested','Confirmed','Declined','Cancelled','Completed') NOT NULL DEFAULT 'Requested',
  scheduled_at DATETIME NULL,
  staff_notes VARCHAR(500) NULL,
  reviewed_by INT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_appointments_user_status_date (user_id,status,requested_at),
  INDEX idx_appointments_schedule (status,scheduled_at),
  CONSTRAINT fk_appointments_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  CONSTRAINT fk_appointments_reviewer FOREIGN KEY (reviewed_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;
