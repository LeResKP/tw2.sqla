<%namespace name="tw" module="tw2.core.mako_util"/>
<div id="${w.attrs['id']}:wrapper">
<div ${tw.attrs(attrs=w.attrs)}>
    <ul>
    % for i, tabname in enumerate(w.items.keys()):
        <li><a href="${'#'+ w.attrs['id']+':'+str(i)}">${tabname}</a></li>
    % endfor
    </ul>
	% for i, fields in enumerate(w.items.values()):
    <div id="${w.attrs['id']}:${str(i)}">
		% for field in fields:
        	${field.display()}
		% endfor
    </div>
    % endfor
</div>
<%include file="generic_jq_ui_js.mak" />
</div>
