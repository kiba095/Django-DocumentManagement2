# Django-DocumentManagement2
 phase2 of document management (March 16-30)

 The principal is member of the commitee so he/she has two accounts
	
	user: staff1 (the uploader)
	pass: demo1234

	user: principal (the approver)
	pass: demo1234

The Members of the Commitee will have only on account (uploaders)

	user:	pass:
	staff2	demo1234
	staff3	demo1234
	staff4	demo1234
	staff5	demo1234

This users can change their own password in the dashboard(upperright corner).
This type of scheme is created base sa diagrams.


Accomplishment List

^Create a document_decision_page's where imageviewer_js for the uploaded images has a
zoom-in-out and pan functionality for better admin observation.
^Create a document_decision_page's pdfviewer to view pdf_files.
^Create filter_individual_pages for the users with their own specific content(see only their content
not others).
^Create a document_decision_page's pending,approval and rejected form for admin/principal.
^Redesign UI for responsive web pages
^Create the notification_function inside the webapp for both users/commitee and admin/principal
if the status of the document changes
^Create a filter_list of approved,rejected and pending on document_lists
^Put the logo of school(waiting), change titles brands and main color theme picked for the webapp(client choice).

*On userrole the Principal has two accounts, account for comittee_group and account member
for approving files.
*On userrole a Commitee member has only one account where they only manage their
uploaded document.

--added search_field for the document list
--added create a multiple approve, reject documents in action_button
