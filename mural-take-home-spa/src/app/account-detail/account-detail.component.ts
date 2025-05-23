import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatToolbarModule } from '@angular/material/toolbar';
import { RouterLink } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';

import { AccountsService } from '../services/accounts.service';
import { PayoutService } from '../services/payout.service';

import { Account } from '../models/account.model';
import { Payout } from '../models/payout.model';
import { PayoutStatus } from '../models/payoutstatus.enum';
import { MatDialog } from '@angular/material/dialog';
import { CreatePayoutDetailDialogComponent } from '../dialogs/create-payout-detail-dialog.component';
import { Overlay } from '@angular/cdk/overlay';

@Component({
  selector: 'app-account-detail',
  templateUrl: './account-detail.component.html',
  standalone: true,
  styleUrl: './account-detail.component.css',
  imports: [
    MatProgressSpinnerModule,
    CommonModule,
    MatCardModule,
    MatToolbarModule,
    RouterLink,
    MatTableModule,
    MatIconModule
  ]
})
export class AccountDetailComponent implements OnInit {
  orgId!: string;
  accountId!: string;
  account?: Account;
  payouts: Payout[] = [];
  executingPayoutIds = new Set<string>();
  payoutDisplayedColumns = ['id', 'status', 'amount', 'fiat', 'fiatStatus', 'createdAt'];

  constructor(
    private route: ActivatedRoute,
    private accountsService: AccountsService,
    private payoutService: PayoutService,
    private dialog: MatDialog,
    private overlay: Overlay
  ) {}

  ngOnInit(): void {
    this.orgId = this.route.snapshot.paramMap.get('orgId')!;
    this.accountId = this.route.snapshot.paramMap.get('accountId')!;

    this.loadAccountDetails();
    this.loadPayouts();
  }

  private loadAccountDetails(): void {
    this.accountsService.getAccountData(this.orgId, this.accountId).subscribe({
      next: (data) => (this.account = data),
      error: (err) => console.error('Failed to fetch account:', err)
    });
  }

  private loadPayouts(): void {
    const basePayload = {
      filter: {
        type: 'payoutStatus',
        statuses: Object.values(PayoutStatus) // ['AWAITING_EXECUTION', ...]
      }
    };

    this.payoutService.getPayoutData(this.orgId, this.accountId, basePayload).subscribe({
      next: (data: Payout[]) => (this.payouts = data),
      error: (err) => console.error('Failed to fetch payouts:', err)
    });
  }

  onExecute(payout: Payout): void {
    const id = payout.id;
    this.executingPayoutIds.add(id);
  
    this.payoutService.executePayoutRequest(this.orgId, this.accountId, id).subscribe({
      next: (updatedPayout: Payout) => {
        const index = this.payouts.findIndex(p => p.id === id);
        if (index !== -1) {
          this.payouts[index] = updatedPayout;
        }
        this.executingPayoutIds.delete(id);
      },
      error: (err) => {
        console.error('Failed to execute payout:', err);
        this.executingPayoutIds.delete(id);
      }
    });
  }

  openCreatePayoutDialog(): void {
      const dialogRef = this.dialog.open(CreatePayoutDetailDialogComponent, {
        width: '600px',
        autoFocus: false,
        scrollStrategy: this.overlay.scrollStrategies.reposition()
      });
    
      dialogRef.afterClosed().subscribe((result) => {
        if (result) {
          if (result.sourceAccountId === ''){
            result.sourceAccountId = this.accountId
          }
          this.payoutService.createPayout(this.orgId, result).subscribe({
          });
        }
      });
    }
}
