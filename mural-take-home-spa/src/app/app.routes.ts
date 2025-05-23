import { Routes } from '@angular/router';
import { AccountsComponent } from './accounts/accounts.component';
import { OrganizationsComponent } from './organizations/organizations.component';
import { AccountDetailComponent } from './account-detail/account-detail.component';
import { OrganizationDetailComponent } from './organization-detail/organization-detail.component';

export const routes: Routes = [  
    { path: '', component: OrganizationsComponent },
    { path: 'accounts', component: AccountsComponent },
    { path: 'organizations', component: OrganizationsComponent },
    { path: 'organizations/:orgId/accounts/:accountId', component: AccountDetailComponent },
    { path: 'organizations/:id', component: OrganizationDetailComponent },
];
