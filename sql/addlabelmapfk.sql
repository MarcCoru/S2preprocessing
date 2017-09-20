 /*select ROW_NUMBER() OVER ()  as labelid, label from labelmap where not label='' order by labelid
*/
update labelmap c
set labelid = c2.labelid
from (select ROW_NUMBER() OVER ()  as labelid, label from labelmap where not label='' group by label order by labelid
     ) c2
     where c2.label = c.label;