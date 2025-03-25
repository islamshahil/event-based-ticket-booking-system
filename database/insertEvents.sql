
INSERT INTO events (name, date, location, total_seats)
VALUES 
    ('Tech Conference 2025', '2025-05-15 10:00:00', 'Dubai Convention Center', 10),
    ('Cybersecurity Summit', '2025-06-20 09:30:00', 'Singapore Expo Hall', 15),
    ('AI & Machine Learning Expo', '2025-07-10 11:00:00', 'San Francisco Tech Hub', 8),
    ('Blockchain Innovations', '2025-08-05 14:00:00', 'Berlin Tech Park', 10),
    ('Cloud Computing Forum', '2025-09-12 15:30:00', 'London Business Center', 20)
RETURNING id;

