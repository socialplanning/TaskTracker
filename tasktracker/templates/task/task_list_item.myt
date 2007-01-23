<%args>
atask
</%args>
<& task_item.myt, atask=atask &>

% for atask in atask.liveChildren():
<& task_list_item.myt, atask=atask &>
%