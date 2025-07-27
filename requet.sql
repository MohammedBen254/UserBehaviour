SELECT 
    -- User data
    u.user_id,
    u.created_at AS user_created_at,
    s.session_id,
    s.start_time AS session_start_time,
    e.event_id,
    e.timestamp AS event_timestamp,
    et.event_type_id,
    
    -- PageView data
    pv.url AS page_url,
    pv.title AS page_title,
    pv.referrer AS page_referrer,
    pv.viewport_width,
    pv.viewport_height,
     
    -- Click data
    c.tag AS click_tag,
    c.element_id AS click_element_id,
    c.class_list AS click_class_list,
    c.text AS click_text,
    c.href AS click_href,
    c.x AS click_x,
    c.y AS click_y,
    c.scroll_position AS click_scroll_position,
    c.time_on_page AS click_time_on_page

FROM "User" u
JOIN "Session" s ON s.user_id = u.user_id
JOIN Event e ON e.session_id = s.session_id
JOIN EventType et ON et.event_type_id = e.event_type_id

LEFT JOIN PageView pv ON pv.event_id = e.event_id
LEFT JOIN Click c ON c.event_id = e.event_id

ORDER BY e.timestamp;
