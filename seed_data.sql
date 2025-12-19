USE py_data_app;
CREATE TABLE IF NOT EXISTS records (
 id INT AUTO_INCREMENT PRIMARY KEY,
 category VARCHAR(100) NOT NULL,
 subcategory VARCHAR(100),
 value FLOAT NOT NULL,
 recorded_at DATETIME NOT NULL
);
-- Insert some sample rows (you can extend this)
INSERT INTO records (category, subcategory, value, recorded_at) VALUES
('Sales','Online',120.50,'2025-01-01 10:00:00'),
('Sales','Offline',200.00,'2025-01-02 11:00:00'),
('Sales','Online',90.25,'2025-01-03 09:30:00'),
('Support','Email',50.00,'2025-01-01 12:00:00'),
('Support','Phone',70.00,'2025-01-04 14:00:00');