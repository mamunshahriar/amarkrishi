-- =========================================================
-- Amar Krishi (আমার কৃষি) - Digital Farming Assistance Platform
-- Database Schema
-- =========================================================



-- ---------------------------------------------------------
-- Users
-- ---------------------------------------------------------

CREATE DATABASE IF NOT EXISTS railway;
USE railway;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,            -- hashed (werkzeug)
    phone VARCHAR(20),
    address VARCHAR(255),
    district VARCHAR(100),
    land_size DECIMAL(6,2) DEFAULT 0,           -- in acres
    preferred_crops VARCHAR(255),
    profile_image VARCHAR(255) DEFAULT 'default-farmer.png',
    language_pref ENUM('en','bn') DEFAULT 'bn',
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Crops
-- ---------------------------------------------------------
CREATE TABLE crops (
    crop_id INT AUTO_INCREMENT PRIMARY KEY,
    crop_name VARCHAR(100) NOT NULL,
    crop_name_bn VARCHAR(100),
    season ENUM('Kharif','Rabi','Summer','All Season') NOT NULL,
    soil_type VARCHAR(100),
    description TEXT,
    expected_yield VARCHAR(100),
    growing_time_days INT,
    profit_level ENUM('Low','Medium','High') DEFAULT 'Medium',
    market_demand ENUM('Low','Medium','High') DEFAULT 'Medium',
    water_requirement ENUM('Low','Medium','High') DEFAULT 'Medium',
    image VARCHAR(255)
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Diseases
-- ---------------------------------------------------------
CREATE TABLE diseases (
    disease_id INT AUTO_INCREMENT PRIMARY KEY,
    disease_name VARCHAR(150) NOT NULL,
    disease_name_bn VARCHAR(150),
    crop_id INT,
    symptoms TEXT,
    possible_cause TEXT,
    treatment TEXT,
    prevention TEXT,
    medicine VARCHAR(255),
    FOREIGN KEY (crop_id) REFERENCES crops(crop_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Disease Reports (AI Detection History)
-- ---------------------------------------------------------
CREATE TABLE disease_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    disease_id INT,
    image_path VARCHAR(255) NOT NULL,
    result VARCHAR(150),
    confidence DECIMAL(5,2),
    detection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (disease_id) REFERENCES diseases(disease_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Crop Recommendations (history of suggestions given to user)
-- ---------------------------------------------------------
CREATE TABLE crop_recommendations (
    recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    crop_id INT NOT NULL,
    district VARCHAR(100),
    soil_type VARCHAR(100),
    water_availability VARCHAR(50),
    season VARCHAR(50),
    recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (crop_id) REFERENCES crops(crop_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Market Prices
-- ---------------------------------------------------------
CREATE TABLE market_prices (
    price_id INT AUTO_INCREMENT PRIMARY KEY,
    crop_id INT NOT NULL,
    market_name VARCHAR(150) NOT NULL,
    district VARCHAR(100),
    price_per_kg DECIMAL(8,2) NOT NULL,
    previous_price DECIMAL(8,2),
    update_date DATE DEFAULT (CURRENT_DATE()),
    FOREIGN KEY (crop_id) REFERENCES crops(crop_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Weather
-- ---------------------------------------------------------
CREATE TABLE weather (
    weather_id INT AUTO_INCREMENT PRIMARY KEY,
    district VARCHAR(100) NOT NULL,
    temperature DECIMAL(4,1),
    humidity INT,
    wind_speed DECIMAL(4,1),
    rain_probability INT,
    alert_type ENUM('None','Heat Wave','Flood','Storm','Frost') DEFAULT 'None',
    alert_severity ENUM('Low','Medium','High') DEFAULT 'Low',
    best_irrigation_time VARCHAR(100),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Expenses / Income (Expense Tracker module)
-- ---------------------------------------------------------
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type ENUM('Income','Expense') NOT NULL,
    category VARCHAR(100),
    amount DECIMAL(10,2) NOT NULL,
    note VARCHAR(255),
    transaction_date DATE DEFAULT (CURRENT_DATE()),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Notifications
-- ---------------------------------------------------------
CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT,
    status ENUM('Unread','Read') DEFAULT 'Unread',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =========================================================
-- SAMPLE DATA
-- =========================================================

INSERT INTO crops (crop_name, crop_name_bn, season, soil_type, description, expected_yield, growing_time_days, profit_level, market_demand, water_requirement, image) VALUES
('Rice', 'ধান', 'Kharif', 'Clay/Loamy', 'Staple cereal crop of Bangladesh, grown widely across all districts.', '4.5 ton/hectare', 120, 'Medium', 'High', 'High', 'rice.jpg'),
('Potato', 'আলু', 'Rabi', 'Sandy Loam', 'High value winter crop, popular in Rangpur and Munshiganj.', '20 ton/hectare', 90, 'High', 'High', 'Medium', 'potato.jpg'),
('Wheat', 'গম', 'Rabi', 'Loamy', 'Major winter cereal, suited to northern districts.', '3 ton/hectare', 110, 'Medium', 'Medium', 'Low', 'wheat.jpg'),
('Jute', 'পাট', 'Kharif', 'Loamy/Clay', 'Cash crop, Bangladesh is a top global producer.', '2.5 ton/hectare', 120, 'Medium', 'Medium', 'High', 'jute.jpg'),
('Mustard', 'সরিষা', 'Rabi', 'Loamy', 'Oilseed crop grown after Aman rice harvest.', '1.2 ton/hectare', 85, 'Medium', 'Medium', 'Low', 'mustard.jpg'),
('Maize', 'ভুট্টা', 'Rabi', 'Sandy Loam', 'Increasingly popular as poultry feed crop.', '7 ton/hectare', 100, 'High', 'High', 'Medium', 'maize.jpg'),
('Onion', 'পেঁয়াজ', 'Rabi', 'Loamy', 'High demand vegetable, prices fluctuate seasonally.', '10 ton/hectare', 100, 'High', 'High', 'Medium', 'onion.jpg'),
('Garlic', 'রসুন', 'Rabi', 'Sandy Loam', 'Grown widely in Rajshahi and Pabna.', '6 ton/hectare', 130, 'High', 'Medium', 'Low', 'garlic.jpg'),
('Tomato', 'টমেটো', 'Rabi', 'Loamy', 'Popular vegetable with high market demand in winter.', '25 ton/hectare', 75, 'High', 'High', 'Medium', 'tomato.jpg'),
('Brinjal', 'বেগুন', 'All Season', 'Loamy', 'Versatile vegetable grown year-round.', '18 ton/hectare', 80, 'Medium', 'High', 'Medium', 'brinjal.jpg');

INSERT INTO diseases (disease_name, disease_name_bn, crop_id, symptoms, possible_cause, treatment, prevention, medicine) VALUES
('Rice Blast', 'ধানের ব্লাস্ট রোগ', 1, 'Diamond-shaped lesions on leaves, white to gray centers with brown margins.', 'Fungus Magnaporthe oryzae, favored by high humidity and excess nitrogen.', 'Apply Tricyclazole-based fungicide; remove infected plants.', 'Use resistant varieties, avoid excess nitrogen fertilizer, proper spacing.', 'Tricyclazole 75% WP'),
('Late Blight', 'লেট ব্লাইট রোগ', 2, 'Dark water-soaked spots on leaves, white fungal growth on undersides.', 'Fungus Phytophthora infestans, spreads in cool wet weather.', 'Apply Mancozeb or Metalaxyl based fungicide immediately.', 'Avoid overhead irrigation, ensure good drainage, crop rotation.', 'Mancozeb 80% WP'),
('Wheat Rust', 'গমের মরিচা রোগ', 3, 'Orange-brown pustules on leaves and stems.', 'Fungus Puccinia species, spread by wind-borne spores.', 'Apply Propiconazole fungicide at early stage.', 'Plant resistant varieties, timely sowing.', 'Propiconazole 25% EC'),
('Tomato Leaf Curl', 'টমেটো পাতা কোঁকড়ানো রোগ', 9, 'Upward curling and yellowing of leaves, stunted growth.', 'Whitefly-transmitted virus (ToLCV).', 'Remove infected plants, control whitefly population with neem oil or insecticide.', 'Use virus-free seedlings, insect-proof nursery nets.', 'Imidacloprid 17.8% SL');

INSERT INTO market_prices (crop_id, market_name, district, price_per_kg, previous_price, update_date) VALUES
(1, 'Barishal Krishi Bazar', 'Barisal', 18.50, 18.05, CURDATE()),
(3, 'Naogaon Bazar', 'Naogaon', 21.25, 21.00, CURDATE()),
(6, 'Mymensingh Bazar', 'Mymensingh', 16.80, 16.20, CURDATE()),
(2, 'Hili Bazar', 'Dinajpur', 12.00, 12.50, CURDATE()),
(7, 'Faridpur Bazar', 'Faridpur', 17.50, 17.20, CURDATE());

INSERT INTO weather (district, temperature, humidity, wind_speed, rain_probability, alert_type, alert_severity, best_irrigation_time) VALUES
('Dhaka', 28.0, 65, 12, 30, 'None', 'Low', 'Early Morning (6-8 AM)'),
('Rajshahi', 32.5, 48, 9, 10, 'Heat Wave', 'Medium', 'Late Evening (6-8 PM)'),
('Sylhet', 26.0, 80, 18, 75, 'Flood', 'High', 'Avoid Irrigation Today'),
('Rangpur', 24.5, 70, 14, 40, 'Frost', 'Low', 'Mid Morning (9-10 AM)');

INSERT INTO users (name, email, password, phone, address, district, land_size, preferred_crops, language_pref) VALUES
('Abdul Karim', 'karim@example.com', 'pbkdf2:sha256:dummyhashvalue', '01711000000', 'Village Char Para', 'Barisal', 2.50, 'Rice, Potato', 'bn');

INSERT INTO notifications (user_id, title, message, status) VALUES
(1, 'Heavy Rain Alert', 'Heavy rainfall expected in your area within 24 hours.', 'Unread'),
(1, 'Market Price Update', 'Rice price increased by 2.5% today.', 'Unread');
