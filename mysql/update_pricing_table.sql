CREATE TABLE IF NOT EXISTS pricing_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    subtitle VARCHAR(100) NULL,
    price VARCHAR(50) NOT NULL,
    unit VARCHAR(100) NOT NULL,
    original_price VARCHAR(50) NULL,
    is_popular BOOLEAN DEFAULT FALSE,
    features TEXT NOT NULL,
    button_text VARCHAR(50) DEFAULT '買課',
    button_link VARCHAR(255) DEFAULT '/contact',
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO system_settings (setting_key, setting_value, description) VALUES
('pricing_notice_title', '學員報名與上課須知', '課程價目表須知標題'),
('pricing_notice_content', '所有常規課程皆需提前於線上系統或向官方 LINE 預約登記。\n堂數方案為個人專屬權益，限本人上課使用，不得轉讓或轉售他人。\n方案自購買啟用起計，請於各方案指定之有效期限內使用完畢。\n若需取消或請假，請最晚於課程開始前 2 小時完成線上取消，以免扣除堂數。\n如遇天然災害或政府宣佈停班停課，本工作室常規課程將自動順延。', '課程價目表學員須知內容(每行一項)');

INSERT INTO pricing_plans (id, title, subtitle, price, unit, original_price, is_popular, features, button_text, button_link, sort_order, is_active)
SELECT 1, '單堂體驗', '適合初次體驗的學員', '$500', '/ 堂', NULL, 0, '["適合初次體驗的學員", "可任選一堂常規舞蹈課", "專業教練動作引導", "課後舞風諮詢"]', '買課', '/contact', 1, 1
WHERE NOT EXISTS (SELECT 1 FROM pricing_plans WHERE id = 1);

INSERT INTO pricing_plans (id, title, subtitle, price, unit, original_price, is_popular, features, button_text, button_link, sort_order, is_active)
SELECT 2, '小資方案', '適合規律每週練習者', '$3,200', '/ 8 堂 (平均 $400/堂)', NULL, 0, '["適合規律每週練習者", "使用期限 2 個月", "全時段常規課程皆適用", "請假彈性保留堂數"]', '買課', '/contact', 2, 1
WHERE NOT EXISTS (SELECT 1 FROM pricing_plans WHERE id = 2);

INSERT INTO pricing_plans (id, title, subtitle, price, unit, original_price, is_popular, features, button_text, button_link, sort_order, is_active)
SELECT 3, '熱血方案', '適合重度舞蹈愛好者', '$6,000', '/ 20 堂 (平均 $300/堂)', NULL, 1, '["適合重度舞蹈愛好者", "使用期限 4 個月", "全常規課程自由選修", "贈送專屬品牌運動毛巾", "享成果發表報名優先權"]', '買課', '/contact', 3, 1
WHERE NOT EXISTS (SELECT 1 FROM pricing_plans WHERE id = 3);

INSERT INTO pricing_plans (id, title, subtitle, price, unit, original_price, is_popular, features, button_text, button_link, sort_order, is_active)
SELECT 4, '尊榮月費', '當月份不限堂數暢快跳', '$8,000', '/ 月 (無限堂數)', NULL, 0, '["當月份不限堂數暢快跳", "全常規課程皆可預約", "場地個人租借 8 折特惠", "周邊服飾商品 9 折優惠"]', '買課', '/contact', 4, 1
WHERE NOT EXISTS (SELECT 1 FROM pricing_plans WHERE id = 4);

