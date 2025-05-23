import { Component, OnInit } from '@angular/core';
import { AccountsService } from '../services/accounts.service';
import { OrganizationService } from '../services/organization.service';
import { getOrgIdsWithCaching } from '../../utility_functions';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-accounts',
  templateUrl: './accounts.component.html',
  styleUrls: ['./accounts.component.css'],
  standalone: true,
  imports: [CommonModule, MatCardModule, MatTableModule, RouterLink]
})
export class AccountsComponent implements OnInit {
  groupedAccounts: { [orgId: string]: any[] } = {};
  accountColumns: string[] = ['name', 'status', 'balance', 'bankName', 'wallet'];

  loading = false;
  orgIds: string[] = [];
  orgs: any[] = [];

  constructor(
    private accountsService: AccountsService,
    private organizationService: OrganizationService
  ) {}

  async ngOnInit(): Promise<void> {
    this.loading = true;

    try {
      const orgs = await getOrgIdsWithCaching(this.organizationService);
      const orgIds = orgs.map((org: { id: string }) => org.id);
      this.orgIds = orgIds;
      this.orgs = orgs;

      const calls = orgIds.map((orgId) =>
        this.accountsService.getAccountListData(orgId).pipe(
          catchError((err) => {
            console.error(`Failed to fetch accounts for ${orgId}`, err);
            return of([]);
          })
        )
      );

      forkJoin(calls).subscribe({
        next: (results) => {
          results.forEach((accounts, i) => {
            const orgName = orgs[i].name;
            const orgId = orgIds[i];
            this.groupedAccounts[orgId] = accounts;
          });
          this.loading = false;
        },
        error: (err) => {
          console.error('Unexpected error loading accounts:', err);
          this.loading = false;
        },
      });
    } catch (err) {
      console.error('Could not load org IDs:', err);
      this.loading = false;
    }
  }
}
