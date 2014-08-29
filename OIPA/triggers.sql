DROP TRIGGER  IF EXISTS  oipav6.copy_iati_description_trigger;
CREATE TRIGGER copy_iati_description_trigger
  AFTER INSERT ON iati_description
  FOR EACH ROW 
    UPDATE iati_activity SET search_description = concat(ifnull(search_description,""), concat(' ', NEW.description))
    WHERE iati_activity.id = NEW.activity_id;
    
DROP TRIGGER  IF EXISTS  oipav6.copy_iati_title_trigger;
CREATE TRIGGER copy_iati_title_trigger
  AFTER UPDATE ON iati_title
  FOR EACH ROW 
    UPDATE iati_activity SET search_title = concat(ifnull(search_title,""), concat(' ',NEW.title))
    WHERE iati_activity.id = NEW.activity_id;
