SELECT  
pm.name,sector.name,ps.name,SUM(a.total_budget),SUM(capital_spend)
FROM 
iati_activity AS a INNER JOIN 
iati_activitypolicymarker AS apm ON (a.id = apm.activity_id)
INNER JOIN 
iati_policymarker AS pm ON (pm.code = apm.policy_marker_id)
INNER JOIN 
iati_policysignificance AS ps ON (apm.policy_significance_id = ps.code) 
INNER JOIN 
iati_activitysector AS actsector ON (a.id = actsector.activity_id)
INNER JOIN 
iati_sector AS sector  ON (actsector.sector_id = sector.code)
WHERE pm.name = 'Gender Equality'
GROUP BY pm.code,sector.code,ps.code
ORDER BY pm.code,sector.code,ps.code
