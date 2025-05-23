# mural_take_home
# Base Technology:
Backend: Firebase Function in Python
Frontend: Angular
Hosting: Firebase Hosting
Secret Management: Google Cloud Secret Manager

# Notes
I was unable to fix all of the bugs involving updating of the UI after an action. The following actions will require a page refresh.
Payouts: After submitting a payout request. After executing a payout request.
Organizations: After clicking TOS/KYC links and accepting

# Web Site Navigation
The landing page is a grid showing a list of all organizations. 
Actions:
a) Click the plus symbol to create a new organization
b) Click on the name of pre-existing organization to navigate to the Organization Details Page

# Organization Details Page
This will provide you more in depth details on the Organization.
At the bottom of the page you will notice an accounts section which will provide brief information on the accounts associated with the user.
Actions:
a) Click on the name of pre-existing account to navigate to the Account Details Page
b) Click the plus to create a new account
c) Click the "Back to Organizations List" button in the footer

# Accounts Page
Endpoint: /accounts
This will show a grid of all the accounts grouped by Organization Name
Actions:
a) Click on the name of pre-existing account to navigate to the Account Details Page

# Account Details Page
Endpoint example: /organizations/69307ff4-37d2-4228-bff4-935f71e3c375/accounts/d11e87c8-77ff-4994-ae4f-5e40f7dd21dd

This will provide a more in depth analysis of the account's details.
At the bottom is a section for payouts.
Actions:
a) Click on the execute button of pre-existing payout request (This only occurs if a payout request status is AWAITING_EXECUTION)
b) Click the plus to create a new payout request (I have added a "Send Sample" button if you scroll down to the bottom of the modal. I was unable to fix the bugs in this modal so the "Send Sample" button will work on creating a payout request)
c) Click the "Back to Organizations" button in the footer

# Third Party API Used
I chose IP Info's IP Geolocation API : https://ipinfo.io/products/ip-geolocation-api
The user's location will be displayed on the top right and under the header you will see a "Warning" message in red. The concept would be incorporated if dealing with business's / individuals located in countries with sanctions. I listed the US as a restricted country to demonstrate the beginning of the functionality.

# Final Thoughts
I really enjoyed working on this project from end to end. There are a few things that I would have fixed / added if I had more time:
1) Grid reloading after the actions listed in the notes
2) Grid filtering / grouping / sorting
3) The accounts page filtering out organizations that did not contain any accounts
4) Theming enhancements to the web page.
5) Additional Third Party integrations with financial / government agencies. This would get information on countries with restrictions and then can integrate that with pre-existing third party API connection.
6) Code commenting and logging.
7) Testing suite