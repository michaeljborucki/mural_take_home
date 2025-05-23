import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { OrganizationService } from '../services/organization.service';
import { AccountsService } from '../services/accounts.service';
import { Organization } from '../models/organization.model';
import { Account } from '../models/account.model';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { forkJoin } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';
import { CreateAccountDialogComponent } from '../dialogs/create-account-dialog.component';

@Component({
  selector: 'app-organization-detail',
  standalone: true,
  imports: [
    CommonModule,
    MatProgressSpinnerModule,
    MatCardModule,
    MatToolbarModule,
    MatTableModule,
    MatIconModule,
    RouterLink,
  ],
  templateUrl: './organization-detail.component.html',
  styleUrl: './organization-detail.component.css',
})
export class OrganizationDetailComponent implements OnInit {
  organization: Organization | null = null;
  accounts: Account[] = [];
  accountDisplayedColumns: string[] = [
    'name',
    'status',
    'apiEnabled',
    'tokenAmount',
    'tokenSymbol',
  ];

  constructor(
    private readonly route: ActivatedRoute,
    private readonly organizationService: OrganizationService,
    private readonly accountsService: AccountsService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) return;
  
    this.organizationService.getOrganizationData(id).subscribe({
      next: (organization) => {
        this.organization = organization;
        const tosAccepted = organization.tosStatus === 'ACCEPTED';
        const kycApproved = organization.kycStatus?.type === 'approved';
  
        if (tosAccepted && kycApproved) {
          this.accountsService.getAccountListData(id).subscribe({
            next: (accounts) => {
              this.accounts = accounts;
            },
            error: (err) =>
              console.error('Failed to load accounts:', err),
          });
        } else {
          console.warn('TOS not accepted or KYC not approved — skipping accounts fetch.');
          this.accounts = []; // Optional: clear or default state
        }
      },
      error: (err) =>
        console.error('Failed to load organization:', err),
    });
  }
  

  openCreateAccountDialog(): void {
    const dialogRef = this.dialog.open(CreateAccountDialogComponent);

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        // Add to accounts array or make API call
        this.accounts = [result, ...(this.accounts || [])];
      }
    });
  }
}
