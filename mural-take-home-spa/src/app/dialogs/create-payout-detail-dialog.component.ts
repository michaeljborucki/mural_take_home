import { Component, Inject } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatOptionModule } from '@angular/material/core';
import { MatButtonModule } from '@angular/material/button';
import { PayoutService } from '../services/payout.service';
import { MatDialogModule, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-create-payout-detail-dialog',
  standalone: true,
  templateUrl: './create-payout-detail-dialog.component.html',
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatOptionModule,
    MatButtonModule,
    MatDialogModule
  ],
  styleUrls: ['./create-payout-detail-dialog.component.css'],
})
export class CreatePayoutDetailDialogComponent {
  formData = {
    memo: '',
    amount: 0,
  
    bankName: '',
    bankAccountOwner: '',
    bankAccountNumber: '',
    phoneNumber: '',
    documentNumber: '',
    documentType: '',
    fiatRailType: '',
    fiatSymbol: '',
    accountType: '',
  
    firstName: '',
    lastName: '',
    email: '',
    dateOfBirth: '',
  
    address1: '',
    country: '',
    state: '',
    city: '',
    zip: ''
  };
  
  sample_payload = {
    "sourceAccountId": "",
    "memo": "December contract",
    "payouts": [
      {
        "amount": {
          "tokenSymbol": "USDC",
          "tokenAmount": 5
        },
        "payoutDetails": {
          "type": "fiat",
          "bankName": "Bancamia S.A.",
          "bankAccountOwner": "test",
          "fiatAndRailDetails": {
              "type": "cop",
              "symbol": "COP",
              "accountType": "CHECKING",
              "phoneNumber": "+57 601 555 5555",
              "bankAccountNumber": "1234567890123456",
              "documentNumber": "1234563",
              "documentType": "NATIONAL_ID"
            }
        },
        "recipientInfo": {
          "type": "individual",
          "firstName": "Javier",
          "lastName": "Gomez",
          "email": "jgomez@gmail.com",
          "dateOfBirth": "1980-02-22",
          "physicalAddress": {
            "address1": "Cra. 37 #10A 29",
            "country": "CO",
            "state": "Antioquia",
            "city": "Medellin",
            "zip": "050015"
          }
        }
      }
    ]
  }


  errorMessage = '';

  isSubmitting = false;
  constructor(
    public dialogRef: MatDialogRef<CreatePayoutDetailDialogComponent>,
    private payoutService: PayoutService
  ) {}

  onSubmit(): void {
    if (this.isSubmitting) return;
    this.isSubmitting = true;
    this.dialogRef.close(this.formData);
  }

  onCancel(): void {
    this.dialogRef.close(null);
  }

  sendSample(): void{
    if (this.isSubmitting) return;
    this.isSubmitting = true;
    this.dialogRef.close(this.sample_payload);
  }
}
